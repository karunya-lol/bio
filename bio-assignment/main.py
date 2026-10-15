# ISC 211: Introduction to Bioinformatics
# Assignment: Topic 3 (Protein Family Classification) using M12 (Hierarchical Clustering)
# Student: Karunya (2025bcd0025)

import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'

from download_dataset import download_all_data
from feature_extraction import extract_all_features
from hierarchical_clustering import HierarchicalProteinClassifier, run_linkage_comparison
from evaluate import full_evaluation
from visualize import generate_all_visualizations

def run_pipeline(force_download=False):
    print("Running protein family classification pipeline (Hierarchical Clustering)...")

    # Step 1: Download dataset if not already present
    raw_data_path = "data/raw/uniprot_protein_families.csv"
    if force_download or not os.path.exists(raw_data_path):
        print("\nStep 1: Downloading Swiss-Prot sequences from UniProt...")
        download_all_data()
    else:
        print(f"\nStep 1: Found existing dataset at {raw_data_path}.")

    # Step 2: Extract features
    features_path = "data/processed/train_features.csv"
    if not os.path.exists(features_path):
        print("\nStep 2: Extracting sequence and physicochemical features...")
        extract_all_features()
    else:
        print(f"\nStep 2: Found processed features at {features_path}.")

    # Step 3: Run model evaluation
    print("\nStep 3: Training hierarchical clustering models and evaluating on test set...")
    summary = full_evaluation(k_features=60, output_dir="results")

    # Step 4: Generate plots
    print("\nStep 4: Generating plots...")
    generate_all_visualizations()

    print("\nPipeline finished successfully. Output files saved in results/ and figures/.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run assignment pipeline")
    parser.add_argument("--force-download", action="store_true", help="Re-download dataset from UniProt")
    args = parser.parse_args()

    run_pipeline(force_download=args.force_download)
