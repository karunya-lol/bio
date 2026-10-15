# feature_extraction.py
# Extracts AAC, CTD physicochemical properties, sequence length/charge, and DPC from sequences.

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

STANDARD_AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")

# Physicochemical groupings based on Chothia / Kyte-Doolittle / Levitt classifications
HYDROPHOBICITY = {
    'Hydrophilic': set("RKEDQN"),
    'Neutral': set("GASTPHY"),
    'Hydrophobic': set("CVLIMFW")
}

VDW_VOLUME = {
    'Small': set("GASCTPD"),
    'Medium': set("NVEQIL"),
    'Large': set("MHKFRYW")
}

POLARITY = {
    'Low_Polarity': set("LIFWCMVY"),
    'Neutral_Polarity': set("PATGS"),
    'High_Polarity': set("HQRKNED")
}

CHARGE = {
    'Positive': set("KRH"),
    'Negative': set("DE"),
    'Neutral_Charge': set("ACFGILMNPQSTVWY")
}

SECONDARY_STRUCTURE_PROPENSITY = {
    'Helix': set("EALMQKRH"),
    'Strand': set("VIYCWFT"),
    'Coil': set("GNPSD")
}

def compute_aac(seq):
    """Compute Amino Acid Composition (20 features)"""
    length = len(seq)
    counts = {aa: 0 for aa in STANDARD_AMINO_ACIDS}
    for aa in seq:
        if aa in counts:
            counts[aa] += 1
    return {f"AAC_{aa}": counts[aa] / length for aa in STANDARD_AMINO_ACIDS}

def compute_ctd_composition(seq):
    """Compute CTD composition features across 5 physicochemical attributes"""
    length = len(seq)
    feats = {}
    
    # 1. Hydrophobicity
    for group_name, aa_set in HYDROPHOBICITY.items():
        cnt = sum(1 for aa in seq if aa in aa_set)
        feats[f"CTD_Hydro_{group_name}"] = cnt / length
        
    # 2. Van der Waals Volume
    for group_name, aa_set in VDW_VOLUME.items():
        cnt = sum(1 for aa in seq if aa in aa_set)
        feats[f"CTD_VDW_{group_name}"] = cnt / length

    # 3. Polarity
    for group_name, aa_set in POLARITY.items():
        cnt = sum(1 for aa in seq if aa in aa_set)
        feats[f"CTD_Polar_{group_name}"] = cnt / length

    # 4. Charge
    for group_name, aa_set in CHARGE.items():
        cnt = sum(1 for aa in seq if aa in aa_set)
        feats[f"CTD_Charge_{group_name}"] = cnt / length

    # 5. Secondary Structure Propensity
    for group_name, aa_set in SECONDARY_STRUCTURE_PROPENSITY.items():
        cnt = sum(1 for aa in seq if aa in aa_set)
        feats[f"CTD_SecStruct_{group_name}"] = cnt / length

    return feats

def compute_macro_properties(seq):
    """Compute macro sequence statistics"""
    length = len(seq)
    # Aromaticity: F + W + Y
    aromatic_count = sum(1 for aa in seq if aa in "FWY")
    # Aliphatic: A + V + I + L
    aliphatic_count = sum(1 for aa in seq if aa in "AVIL")
    # Tiny: G + A + S
    tiny_count = sum(1 for aa in seq if aa in "GAS")
    # Net charge proxy at neutral pH: (K + R + 0.1*H) - (D + E)
    pos_charge = seq.count("K") + seq.count("R") + 0.1 * seq.count("H")
    neg_charge = seq.count("D") + seq.count("E")
    net_charge = (pos_charge - neg_charge) / length

    return {
        'Seq_Length': length,
        'Prop_Aromatic': aromatic_count / length,
        'Prop_Aliphatic': aliphatic_count / length,
        'Prop_Tiny': tiny_count / length,
        'Estimated_NetCharge': net_charge
    }

def compute_dipeptide_composition(seq, top_dipeptides=None):
    """Compute Dipeptide Composition (DPC)"""
    length = len(seq)
    dpc = {}
    if length < 2:
        return dpc
    
    total_pairs = length - 1
    # Count all adjacent pairs
    pair_counts = {}
    for i in range(total_pairs):
        pair = seq[i:i+2]
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
        
    if top_dipeptides is not None:
        for pair in top_dipeptides:
            dpc[f"DPC_{pair}"] = pair_counts.get(pair, 0) / total_pairs
    else:
        for a1 in STANDARD_AMINO_ACIDS:
            for a2 in STANDARD_AMINO_ACIDS:
                pair = a1 + a2
                dpc[f"DPC_{pair}"] = pair_counts.get(pair, 0) / total_pairs
    return dpc

def extract_all_features(raw_csv_path="data/raw/uniprot_protein_families.csv", 
                         output_dir="data/processed",
                         random_state=42):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(raw_csv_path)
    print(f"Loaded {len(df)} sequences from {raw_csv_path}")

    feature_rows = []
    for idx, row in df.iterrows():
        seq = row['Sequence']
        f_dict = {
            'Accession': row['Accession'],
            'EntryName': row['EntryName'],
            'Family': row['Family']
        }
        f_dict.update(compute_aac(seq))
        f_dict.update(compute_ctd_composition(seq))
        f_dict.update(compute_macro_properties(seq))
        f_dict.update(compute_dipeptide_composition(seq)) # all 400 dipeptides
        
        feature_rows.append(f_dict)

    feat_df = pd.DataFrame(feature_rows)
    all_features_path = os.path.join(output_dir, "features.csv")
    feat_df.to_csv(all_features_path, index=False)
    print(f"Extracted {feat_df.shape[1] - 3} features for {len(feat_df)} proteins.")
    print(f"Saved full feature matrix to {all_features_path}")

    # Train / Test split (80% train, 20% unseen test, stratified by family)
    train_df, test_df = train_test_split(
        feat_df, 
        test_size=0.20, 
        random_state=random_state, 
        stratify=feat_df['Family']
    )

    train_path = os.path.join(output_dir, "train_features.csv")
    test_path = os.path.join(output_dir, "test_features.csv")
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"\nTrain set: {len(train_df)} samples saved to {train_path}")
    print(f"Test set:  {len(test_df)} samples saved to {test_path}")

    print("\nClass distribution:")
    dist = pd.DataFrame({
        'Train': train_df['Family'].value_counts(),
        'Test': test_df['Family'].value_counts(),
        'Total': feat_df['Family'].value_counts()
    })
    print(dist.to_string())

    return feat_df, train_df, test_df

if __name__ == "__main__":
    extract_all_features()
