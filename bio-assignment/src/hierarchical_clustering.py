# hierarchical_clustering.py
# Hierarchical clustering (Ward, complete, average, single) and test evaluation.

import os
import json
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, cophenet, fcluster
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score,
    normalized_mutual_info_score,
    homogeneity_completeness_v_measure,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

def compute_cluster_purity(y_true, cluster_labels):
    """Compute clustering purity with respect to ground-truth labels."""
    contingency = pd.crosstab(pd.Series(cluster_labels, name='Cluster'), pd.Series(y_true, name='True'))
    purity = contingency.max(axis=1).sum() / len(y_true)
    return purity, contingency

class HierarchicalProteinClassifier:
    def __init__(self, n_clusters=4, linkage_method='ward', select_k_features=60):
        self.n_clusters = n_clusters
        self.linkage_method = linkage_method
        self.select_k_features = select_k_features
        
        self.feature_selector = SelectKBest(f_classif, k=select_k_features) if select_k_features else None
        self.scaler = StandardScaler()
        self.selected_feature_names = None
        self.Z = None
        self.train_cluster_labels = None
        self.cluster_to_family_map = {}
        self.cluster_centroids = {}
        self.classes_ = None
        self.X_train_transformed = None
        self.y_train_true = None

    def fit(self, train_df):
        """Fit the hierarchical clustering model on training sequences."""
        meta_cols = ['Accession', 'EntryName', 'Family']
        raw_feat_cols = [c for c in train_df.columns if c not in meta_cols]
        
        X_raw = train_df[raw_feat_cols].values
        y_true = train_df['Family'].values
        self.classes_ = sorted(list(set(y_true)))
        self.y_train_true = y_true

        # Step 1: Feature Selection via ANOVA F-test (Filter method)
        if self.feature_selector:
            X_sel = self.feature_selector.fit_transform(X_raw, y_true)
            selected_indices = self.feature_selector.get_support(indices=True)
            self.selected_feature_names = [raw_feat_cols[i] for i in selected_indices]
            self.feature_scores = {
                raw_feat_cols[i]: float(self.feature_selector.scores_[i]) 
                for i in selected_indices
            }
        else:
            X_sel = X_raw
            self.selected_feature_names = raw_feat_cols
            self.feature_scores = {}

        # Step 2: Standardization
        X_scaled = self.scaler.fit_transform(X_sel)
        self.X_train_transformed = X_scaled

        # Step 3: Hierarchical Agglomerative Clustering
        self.Z = linkage(X_scaled, method=self.linkage_method)
        
        # Form flat clusters for k = n_clusters
        self.train_cluster_labels = fcluster(self.Z, t=self.n_clusters, criterion='maxclust')

        # Step 4: Map clusters to biological families & calculate cluster prototypes
        contingency = pd.crosstab(
            pd.Series(self.train_cluster_labels, name='Cluster'), 
            pd.Series(y_true, name='Family')
        )
        self.contingency_matrix = contingency

        for c in range(1, self.n_clusters + 1):
            mask = (self.train_cluster_labels == c)
            if np.sum(mask) > 0 and c in contingency.index:
                majority_family = contingency.loc[c].idxmax()
                self.cluster_to_family_map[c] = majority_family
                self.cluster_centroids[c] = np.mean(X_scaled[mask], axis=0)
            else:
                self.cluster_to_family_map[c] = self.classes_[0]
                self.cluster_centroids[c] = np.zeros(X_scaled.shape[1])

        # Step 5: Calculate training metrics
        return self._evaluate_train(X_scaled, y_true, self.train_cluster_labels)

    def _evaluate_train(self, X_scaled, y_true, cluster_labels):
        purity, _ = compute_cluster_purity(y_true, cluster_labels)
        sil = silhouette_score(X_scaled, cluster_labels)
        db = davies_bouldin_score(X_scaled, cluster_labels)
        ch = calinski_harabasz_score(X_scaled, cluster_labels)
        ari = adjusted_rand_score(y_true, cluster_labels)
        nmi = normalized_mutual_info_score(y_true, cluster_labels)
        h, c_score, v = homogeneity_completeness_v_measure(y_true, cluster_labels)

        dists = pdist(X_scaled)
        coph_corr, _ = cophenet(self.Z, dists)

        y_train_pred = [self.cluster_to_family_map[c] for c in cluster_labels]
        acc = accuracy_score(y_true, y_train_pred)

        metrics = {
            'linkage': self.linkage_method,
            'cophenetic_correlation': float(coph_corr),
            'silhouette_score': float(sil),
            'davies_bouldin_index': float(db),
            'calinski_harabasz_index': float(ch),
            'adjusted_rand_index': float(ari),
            'normalized_mutual_info': float(nmi),
            'homogeneity': float(h),
            'completeness': float(c_score),
            'v_measure': float(v),
            'cluster_purity': float(purity),
            'train_accuracy': float(acc)
        }
        return metrics

    def transform_features(self, df):
        """Transform raw test dataframe to scaled feature space."""
        meta_cols = ['Accession', 'EntryName', 'Family']
        raw_feat_cols = [c for c in df.columns if c not in meta_cols]
        X_raw = df[raw_feat_cols].values
        if self.feature_selector:
            X_sel = self.feature_selector.transform(X_raw)
        else:
            X_sel = X_raw
        return self.scaler.transform(X_sel)

    def predict(self, test_df):
        """Predict biological protein family for unseen test sequences."""
        X_scaled = self.transform_features(test_df)

        assigned_clusters = []
        for x in X_scaled:
            best_c = min(
                self.cluster_centroids.keys(), 
                key=lambda c: np.linalg.norm(x - self.cluster_centroids[c])
            )
            assigned_clusters.append(best_c)

        y_pred = [self.cluster_to_family_map[c] for c in assigned_clusters]
        return np.array(y_pred), np.array(assigned_clusters)

    def evaluate_test(self, test_df):
        """Comprehensive evaluation on unseen test data."""
        y_true = test_df['Family'].values
        y_pred, test_clusters = self.predict(test_df)

        acc = accuracy_score(y_true, y_pred)
        prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
        prec_wt, rec_wt, f1_wt, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=self.classes_)
        clf_rep = classification_report(y_true, y_pred, labels=self.classes_, output_dict=True, zero_division=0)

        results = {
            'test_accuracy': float(acc),
            'precision_macro': float(prec_macro),
            'recall_macro': float(rec_macro),
            'f1_macro': float(f1_macro),
            'precision_weighted': float(prec_wt),
            'recall_weighted': float(rec_wt),
            'f1_weighted': float(f1_wt),
            'confusion_matrix': cm.tolist(),
            'classification_report': clf_rep,
            'classes': self.classes_
        }
        return results, y_pred

def run_linkage_comparison(train_df, test_df, k_features=60):
    """Run comparison of all 4 linkage methods and return DataFrame."""
    linkages = ['ward', 'complete', 'average', 'single']
    records = []

    for method in linkages:
        model = HierarchicalProteinClassifier(n_clusters=4, linkage_method=method, select_k_features=k_features)
        train_m = model.fit(train_df)
        test_m, _ = model.evaluate_test(test_df)

        records.append({
            'Linkage': method.capitalize(),
            'Cophenetic Correlation (CPCC)': train_m['cophenetic_correlation'],
            'Silhouette Score': train_m['silhouette_score'],
            'Davies-Bouldin Index': train_m['davies_bouldin_index'],
            'Adjusted Rand Index (ARI)': train_m['adjusted_rand_index'],
            'Normalized Mutual Info (NMI)': train_m['normalized_mutual_info'],
            'Cluster Purity': train_m['cluster_purity'],
            'Test Accuracy': test_m['test_accuracy'],
            'Test Macro F1': test_m['f1_macro']
        })

    return pd.DataFrame(records)

if __name__ == "__main__":
    train_df = pd.read_csv("data/processed/train_features.csv")
    test_df = pd.read_csv("data/processed/test_features.csv")
    
    comp_df = run_linkage_comparison(train_df, test_df, k_features=60)
    print("--- Linkage Comparison Table ---")
    print(comp_df.to_string(index=False))
