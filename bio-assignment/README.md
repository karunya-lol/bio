# ISC 211: Introduction to Bioinformatics — Individual Assignment

**Student Name:** Karunya  
**Roll Number:** `2025bcd0025`  
**Course:** ISC 211 - Introduction to Bioinformatics  
**Institute:** IIIT Kottayam  

---

## 1. Topic and Algorithm Allocation

From the assignment formula:
- **Roll number last 3 digits ($R$):** $R = 25$
- **Topic:** $((25 - 1) \bmod 11) + 1 = 3 \implies$ **Topic 3: Protein Family Classification Using Machine Learning**
- **Algorithm:** Since Topic $3 \le 10$, $M = ((25 - 1) \bmod 13) + 1 = 12 \implies$ **M12: Hierarchical Clustering**
- **Reference Review Paper:** T. Idhaya, A. Suruliandi, S. P. Raja, *"A Comprehensive Review on Machine Learning Techniques for Protein Family Prediction"*, *The Protein Journal*, 43, 171–186 (2024).

---

## 2. Biological Problem

Experimental determination of protein 3D structures and functions cannot keep pace with high-throughput sequencing. Classifying proteins into families based on evolutionary and biochemical relationships helps annotate uncharacterized sequences and identify drug targets.

In this project, we classify protein sequences into four representative families:
1. **G-Protein Coupled Receptors (GPCRs):** 7-transmembrane receptors that mediate cellular signaling.
2. **Nuclear Hormone Receptors (NRs):** Transcription factors with zinc-finger DNA-binding domains.
3. **Ion Channels (ICs, Potassium Channels):** Membrane channels regulating potassium ion transport.
4. **Protein Kinases (PKs):** Catalytic enzymes that transfer phosphate groups from ATP to target proteins.

---

## 3. Dataset

Sequences were downloaded directly from **UniProtKB/Swiss-Prot** (reviewed: true) via the UniProt REST API:
- Filtered to lengths between 200 and 800 residues.
- Removed sequences with ambiguous amino acids (B, Z, X, U, O) and duplicates.
- **Total Sequences:** 582 non-redundant proteins
  - GPCR: 150
  - Ion Channel: 132
  - Nuclear Receptor: 150
  - Protein Kinase: 150
- **Split:** 80% train (465 sequences) and 20% stratified test (117 sequences).
- Files: `data/raw/uniprot_protein_families.csv` and `data/raw/uniprot_protein_families.fasta`.

---

## 4. Feature Extraction and Selection

From primary sequences, 440 features were extracted:
1. **Amino Acid Composition (AAC, 20 features):** Relative frequency of the 20 canonical amino acids.
2. **Physicochemical Properties / CTD (15 features):** Group composition for Hydrophobicity, Volume, Polarity, Charge, and Secondary Structure Propensity.
3. **Sequence Length & Charge (5 features):** Length, aromaticity, aliphatic index, tiny residues, and net charge proxy.
4. **Dipeptide Composition (DPC, 400 features):** Frequencies of all adjacent amino acid pairs.

**ANOVA Feature Selection:** Using an ANOVA F-score filter, the top 60 features were selected. Top features included hydrophobic composition ($F=396.1$), low polarity ($F=383.5$), neutral charge ($F=374.1$), and cysteine composition ($F=114.6$).

---

## 5. Model: Hierarchical Agglomerative Clustering (M12)

- Evaluated four linkage methods: Ward, Complete, Average (UPGMA), and Single linkage.
- Training set dendrogram cut at $k = 4$ clusters.
- Clusters mapped to majority protein family to derive cluster centroids.
- Test sequences assigned to nearest cluster centroid.

### Summary of Results:
- **Ward's Linkage (Best):**
  - Cophenetic Correlation (CPCC): 0.6952
  - Training Cluster Purity: 93.12%
  - Adjusted Rand Index (ARI): 0.8347
  - **Unseen Test Accuracy:** **91.45%** (107 / 117 correct)
  - **Test Macro F1-Score:** **91.29%**
  - **GPCR Recall:** **100.00%** (30 / 30 correct)

---

## 6. Project Structure

```
bio-assignment/
├── data/
│   ├── raw/
│   │   ├── uniprot_protein_families.csv      # Downloaded Swiss-Prot dataset
│   │   └── uniprot_protein_families.fasta    # FASTA file
│   └── processed/
│       ├── features.csv                      # Extracted feature matrix
│       ├── train_features.csv                # 80% train split
│       └── test_features.csv                 # 20% test split
├── figures/
│   ├── dendrogram_ward.png                   # Dendrogram with k=4 cutoff
│   ├── pca_clusters_vs_families.png          # 2D PCA comparison
│   ├── confusion_matrix.png                  # Test set confusion matrix
│   ├── feature_importance.png                # Top 15 features by ANOVA
│   └── linkage_comparison.png                # Linkage comparison bar chart
├── results/
│   ├── evaluation_summary.json               # Detailed metrics
│   └── linkage_comparison.csv                # Linkage comparison table
├── src/
│   ├── download_dataset.py                   # UniProt downloader
│   ├── feature_extraction.py                 # Feature extractor
│   ├── hierarchical_clustering.py            # Model implementation & inference
│   ├── evaluate.py                           # Evaluation script
│   └── visualize.py                          # Plotting script
├── main.py                                   # Runs the full pipeline
├── generate_report.py                        # Generates the 5-page PDF report
├── report.pdf                                # Final 5-page report
├── requirements.txt                          # Python dependencies
├── README.md                                 # Project documentation
└── submission_2025bcd0025.zip                # LMS submission archive
```

---

## 7. How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the pipeline:**
   ```bash
   python main.py
   ```

3. **Rebuild the PDF report:**
   ```bash
   python generate_report.py
   ```
