# evaluate.py
# Evaluation functions for linkage comparison and test set metrics.

import os
import json
import numpy as np
import pandas as pd
from hierarchical_clustering import HierarchicalProteinClassifier, run_linkage_comparison

def full_evaluation(k_features=60, output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    
    train_df = pd.read_csv("data/processed/train_features.csv")
    test_df = pd.read_csv("data/processed/test_features.csv")

    print("\n--- Evaluating Linkage Methods ---")

    # 1. Linkage comparison
    print("\n--- LINKAGE COMPARISON ACROSS 4 CRITERIA ---")
    comp_df = run_linkage_comparison(train_df, test_df, k_features=k_features)
    print(comp_df.to_string(index=False))
    comp_df.to_csv(os.path.join(output_dir, "linkage_comparison.csv"), index=False)

    # 2. Detailed Evaluation of Best Model (Ward's Linkage)
    print("\n--- DETAILED EVALUATION OF WARD'S HIERARCHICAL CLUSTERING MODEL ---")
    model = HierarchicalProteinClassifier(linkage_method='ward', select_k_features=k_features)
    train_metrics = model.fit(train_df)
    
    print("\n[TRAINING CLUSTERING VALIDATION]")
    print(f"Cophenetic Correlation Coefficient (CPCC): {train_metrics['cophenetic_correlation']:.4f}")
    print(f"Silhouette Coefficient:                   {train_metrics['silhouette_score']:.4f}")
    print(f"Davies-Bouldin Index:                     {train_metrics['davies_bouldin_index']:.4f}")
    print(f"Calinski-Harabasz Index:                  {train_metrics['calinski_harabasz_index']:.2f}")
    print(f"Adjusted Rand Index (ARI):                {train_metrics['adjusted_rand_index']:.4f}")
    print(f"Normalized Mutual Information (NMI):      {train_metrics['normalized_mutual_info']:.4f}")
    print(f"Homogeneity:                              {train_metrics['homogeneity']:.4f}")
    print(f"Completeness:                             {train_metrics['completeness']:.4f}")
    print(f"V-Measure:                                {train_metrics['v_measure']:.4f}")
    print(f"Cluster Purity:                           {train_metrics['cluster_purity']:.4f}")

    print("\n[CLUSTER CONTINGENCY MATRIX (TRAINING SET)]")
    print(model.contingency_matrix)

    print("\n[CLUSTER TO BIOLOGICAL FAMILY MAPPING]")
    for c, fam in model.cluster_to_family_map.items():
        print(f"  Cluster {c} -> {fam}")

    # 3. Unseen Test Set Evaluation
    test_results, y_pred = model.evaluate_test(test_df)
    print("\n[UNSEEN TEST SET EVALUATION]")
    print(f"Test Accuracy:         {test_results['test_accuracy'] * 100:.2f}%")
    print(f"Macro Precision:       {test_results['precision_macro'] * 100:.2f}%")
    print(f"Macro Recall:          {test_results['recall_macro'] * 100:.2f}%")
    print(f"Macro F1-Score:        {test_results['f1_macro'] * 100:.2f}%")
    print(f"Weighted F1-Score:     {test_results['f1_weighted'] * 100:.2f}%")

    print("\n[TEST CONFUSION MATRIX]")
    cm_df = pd.DataFrame(
        test_results['confusion_matrix'],
        index=model.classes_,
        columns=model.classes_
    )
    print(cm_df)

    print("\n[PER-CLASS CLASSIFICATION REPORT]")
    clf_rep_df = pd.DataFrame(test_results['classification_report']).transpose()
    print(clf_rep_df.to_string())

    # Save metrics JSON
    all_summary = {
        'student_name': 'Karunya',
        'roll_number': '2025bcd0025',
        'assigned_topic': 'Topic 3: Protein Family Classification Using Machine Learning',
        'assigned_algorithm': 'M12: Hierarchical Clustering',
        'train_metrics': train_metrics,
        'test_results': test_results
    }
    with open(os.path.join(output_dir, "evaluation_summary.json"), "w") as f:
        json.dump(all_summary, f, indent=4)
        
    print(f"\nSaved detailed results to {output_dir}/")
    return all_summary

if __name__ == "__main__":
    full_evaluation()
