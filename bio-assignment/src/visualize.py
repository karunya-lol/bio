# visualize.py
# Generates plots: dendrogram, PCA projection, confusion matrix, feature importance, and linkage comparison.

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix
from hierarchical_clustering import HierarchicalProteinClassifier, run_linkage_comparison

# Style settings for academic publication
plt.rcParams['font.sans-serif'] = 'Helvetica', 'Arial', 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

FAMILY_COLORS = {
    'GPCR': '#1f77b4',           # Steel Blue
    'Ion_Channel': '#ff7f0e',    # Safety Orange
    'Nuclear_Receptor': '#2ca02c',# Forest Green
    'Protein_Kinase': '#d62728'   # Crimson Red
}

def plot_dendrogram(model, output_path="figures/dendrogram_ward.png"):
    """Plot hierarchical clustering dendrogram with cluster cut threshold."""
    plt.figure(figsize=(10, 5), dpi=300)
    
    # Calculate cutoff height between 3rd and 4th last merges
    cut_height = (model.Z[-4, 2] + model.Z[-3, 2]) / 2.0

    dendrogram(
        model.Z,
        truncate_mode='lastp',
        p=40,
        leaf_rotation=90.,
        leaf_font_size=9.,
        show_contracted=True,
        color_threshold=cut_height,
        above_threshold_color='#7f7f7f'
    )
    plt.axhline(y=cut_height, color='#d62728', linestyle='--', linewidth=1.5, 
                label=f'Cut-off Height = {cut_height:.1f} (k=4 clusters)')
    plt.title("Hierarchical Agglomerative Clustering Dendrogram (Ward Linkage)\nProtein Sequences Clustered by Primary & Physicochemical Descriptors", fontsize=11, fontweight='bold', pad=10)
    plt.xlabel("Clustered Sequence Groups (Truncated to Top 40 Sub-branches)", fontsize=9, labelpad=8)
    plt.ylabel("Ward Minimum Variance Distance", fontsize=9)
    plt.legend(loc='upper right', frameon=True, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved dendrogram to {output_path}")

def plot_pca_comparison(model, train_df, output_path="figures/pca_clusters_vs_families.png"):
    """Plot 2D PCA comparing true biological families vs discovered clusters."""
    pca_2d = PCA(n_components=2, random_state=42)
    X_2d = pca_2d.fit_transform(model.X_train_transformed)
    var_exp = pca_2d.explained_variance_ratio_ * 100

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    # Panel A: Ground-Truth Biological Families
    for fam in sorted(list(FAMILY_COLORS.keys())):
        mask = (model.y_train_true == fam)
        axes[0].scatter(
            X_2d[mask, 0], X_2d[mask, 1],
            c=FAMILY_COLORS[fam], label=fam.replace('_', ' '),
            alpha=0.75, edgecolors='none', s=35
        )
    axes[0].set_title("(A) Ground-Truth Biological Protein Families", fontsize=10, fontweight='bold')
    axes[0].set_xlabel(f"Principal Component 1 ({var_exp[0]:.1f}% var)", fontsize=9)
    axes[0].set_ylabel(f"Principal Component 2 ({var_exp[1]:.1f}% var)", fontsize=9)
    axes[0].legend(loc='best', frameon=True, fontsize=8)
    axes[0].grid(True, linestyle=':', alpha=0.5)

    # Panel B: Hierarchical Clustering Clusters
    cluster_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    for c in range(1, 5):
        mask = (model.train_cluster_labels == c)
        mapped_fam = model.cluster_to_family_map.get(c, f"C{c}")
        axes[1].scatter(
            X_2d[mask, 0], X_2d[mask, 1],
            c=cluster_palette[c-1], label=f"Cluster {c} (-> {mapped_fam})",
            alpha=0.75, edgecolors='none', s=35
        )
        
        # Plot cluster centroid projected into 2D PCA
        centroid_2d = pca_2d.transform(model.cluster_centroids[c].reshape(1, -1))
        axes[1].scatter(
            centroid_2d[0, 0], centroid_2d[0, 1],
            c='black', marker='X', s=90, edgecolors='white', linewidth=1.2
        )

    axes[1].set_title("(B) Discovered Hierarchical Clusters (k=4, Ward)", fontsize=10, fontweight='bold')
    axes[1].set_xlabel(f"Principal Component 1 ({var_exp[0]:.1f}% var)", fontsize=9)
    axes[1].set_ylabel(f"Principal Component 2 ({var_exp[1]:.1f}% var)", fontsize=9)
    axes[1].legend(loc='best', frameon=True, fontsize=8)
    axes[1].grid(True, linestyle=':', alpha=0.5)

    plt.suptitle("Principal Component Projection: Biological Families vs. Hierarchical Clusters", fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved PCA projection to {output_path}")

def plot_confusion_matrix(test_results, output_path="figures/confusion_matrix.png"):
    """Plot annotated confusion matrix heatmap for unseen test set."""
    cm = np.array(test_results['confusion_matrix'])
    classes = [c.replace('_', '\n') for c in test_results['classes']]

    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    cax = ax.matshow(cm, cmap='Blues', alpha=0.85)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > cm.max() / 2 else "black"
            ax.text(j, i, str(val), va='center', ha='center', fontsize=11, fontweight='bold', color=color)

    fig.colorbar(cax, fraction=0.046, pad=0.04)
    ax.set_xticks(range(len(classes)))
    ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes, fontsize=8)
    ax.set_yticklabels(classes, fontsize=8)
    ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)
    
    plt.title(f"Confusion Matrix on Unseen Biological Test Set\n(Accuracy: {test_results['test_accuracy']*100:.1f}%, Macro F1: {test_results['f1_macro']*100:.1f}%)", 
              fontsize=10, fontweight='bold', pad=12)
    plt.xlabel("Predicted Protein Family", fontsize=9, labelpad=8)
    plt.ylabel("True Protein Family", fontsize=9, labelpad=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved confusion matrix to {output_path}")

def plot_linkage_comparison(comp_df, output_path="figures/linkage_comparison.png"):
    """Plot comparative performance bar chart across the 4 linkage methods."""
    methods = comp_df['Linkage'].tolist()
    cpcc = comp_df['Cophenetic Correlation (CPCC)'].tolist()
    purity = comp_df['Cluster Purity'].tolist()
    ari = comp_df['Adjusted Rand Index (ARI)'].tolist()
    test_acc = comp_df['Test Accuracy'].tolist()

    x = np.arange(len(methods))
    width = 0.18

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    ax.bar(x - 1.5*width, cpcc, width, label='CPCC (Preservation)', color='#4c72b0')
    ax.bar(x - 0.5*width, purity, width, label='Cluster Purity', color='#55a868')
    ax.bar(x + 0.5*width, ari, width, label='Adjusted Rand Index', color='#c44e52')
    ax.bar(x + 1.5*width, test_acc, width, label='Test Accuracy', color='#8172b3')

    ax.set_title("Performance Benchmark Across Hierarchical Linkage Criteria", fontsize=11, fontweight='bold', pad=10)
    ax.set_ylabel("Score (0.0 to 1.0)", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=9, fontweight='semibold')
    ax.set_ylim(0, 1.08)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', frameon=True, fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved linkage comparison to {output_path}")

def plot_feature_importance(model, output_path="figures/feature_importance.png", top_n=15):
    """Plot top biological features based on ANOVA F-statistic."""
    scores = model.feature_scores
    sorted_feats = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_n]
    
    feats = [item[0] for item in sorted_feats][::-1]
    f_vals = [item[1] for item in sorted_feats][::-1]

    # Clean feature names for biological presentation
    clean_labels = []
    for f in feats:
        lbl = f.replace("CTD_Hydro_", "Hydrophobicity: ")
        lbl = lbl.replace("CTD_Polar_", "Polarity: ")
        lbl = lbl.replace("CTD_Charge_", "Charge: ")
        lbl = lbl.replace("CTD_SecStruct_", "Sec. Struct: ")
        lbl = lbl.replace("Prop_", "Macro: ")
        lbl = lbl.replace("AAC_", "Amino Acid: ")
        lbl = lbl.replace("DPC_", "Dipeptide: ")
        lbl = lbl.replace("_", " ")
        clean_labels.append(lbl)

    plt.figure(figsize=(8, 5), dpi=300)
    bars = plt.barh(clean_labels, f_vals, color='#2b5c8f', height=0.65)
    plt.title(f"Top {top_n} Discriminative Biological Features (ANOVA F-statistic)", fontsize=11, fontweight='bold', pad=10)
    plt.xlabel("ANOVA F-Score (Significance in Family Discrimination)", fontsize=9)
    plt.ylabel("Biological Sequence / Physicochemical Feature", fontsize=9)
    plt.grid(axis='x', linestyle=':', alpha=0.6)
    
    # Value annotations on bars
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 5, bar.get_y() + bar.get_height()/2, f"{width:.1f}", 
                 va='center', ha='left', fontsize=7.5, color='#333333')

    plt.xlim(0, max(f_vals) * 1.15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved feature importance to {output_path}")

def generate_all_visualizations():
    os.makedirs("figures", exist_ok=True)
    train_df = pd.read_csv("data/processed/train_features.csv")
    test_df = pd.read_csv("data/processed/test_features.csv")

    # Fit best model
    model = HierarchicalProteinClassifier(linkage_method='ward', select_k_features=60)
    train_m = model.fit(train_df)
    test_res, _ = model.evaluate_test(test_df)

    # Plot all figures
    plot_dendrogram(model)
    plot_pca_comparison(model, train_df)
    plot_confusion_matrix(test_res)
    plot_feature_importance(model)

    # Linkage comparison
    comp_df = run_linkage_comparison(train_df, test_df, k_features=60)
    plot_linkage_comparison(comp_df)

    print("\nAll publication-grade figures successfully generated in figures/")

if __name__ == "__main__":
    generate_all_visualizations()
