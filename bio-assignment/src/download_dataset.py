# download_dataset.py
# Downloads reviewed Swiss-Prot sequences from UniProt for 4 protein families

import os
import re
import time
import requests
import pandas as pd

FAMILIES = {
    'GPCR': {
        'query': 'reviewed:true AND family:"g-protein coupled receptor 1 family" AND length:[250 TO 700]',
        'description': 'G-protein coupled receptor 1 family'
    },
    'Nuclear_Receptor': {
        'query': 'reviewed:true AND family:"nuclear hormone receptor family" AND length:[200 TO 800]',
        'description': 'Nuclear hormone receptor family'
    },
    'Ion_Channel': {
        'query': 'reviewed:true AND family:"potassium channel family" AND length:[200 TO 800]',
        'description': 'Potassium channel family'
    },
    'Protein_Kinase': {
        'query': 'reviewed:true AND family:"protein kinase superfamily" AND length:[250 TO 800]',
        'description': 'Protein kinase superfamily'
    }
}

VALID_AA_REGEX = re.compile(r'^[ACDEFGHIKLMNPQRSTVWY]+$')

def fetch_family_sequences(family_name, query, target_count=150):
    print(f"Fetching sequences for {family_name}...")
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        'query': query,
        'format': 'tsv',
        'fields': 'accession,id,gene_names,protein_name,organism_name,length,sequence',
        'size': target_count + 50
    }
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Python script)'}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {family_name}: {e}")
        return []

    lines = response.text.strip().split('\n')
    if len(lines) <= 1:
        print(f"Warning: No records found for {family_name}")
        return []

    header = lines[0].split('\t')
    records = []
    seen_seqs = set()

    for line in lines[1:]:
        parts = line.split('\t')
        if len(parts) < len(header):
            continue
        
        acc = parts[0].strip()
        entry_name = parts[1].strip()
        gene = parts[2].strip() if len(parts) > 2 else ""
        protein = parts[3].strip() if len(parts) > 3 else ""
        organism = parts[4].strip() if len(parts) > 4 else ""
        length_val = int(parts[5].strip()) if parts[5].strip().isdigit() else 0
        seq = parts[6].strip().upper() if len(parts) > 6 else ""

        # Filter: only 20 standard amino acids
        if not VALID_AA_REGEX.match(seq):
            continue
        if seq in seen_seqs:
            continue
        seen_seqs.add(seq)

        records.append({
            'Accession': acc,
            'EntryName': entry_name,
            'Family': family_name,
            'Gene': gene,
            'ProteinName': protein,
            'Organism': organism,
            'Length': length_val,
            'Sequence': seq
        })

        if len(records) >= target_count:
            break

    print(f"Got {len(records)} sequences for {family_name}.")
    return records

def download_all_data(output_dir="data/raw", target_per_family=150):
    os.makedirs(output_dir, exist_ok=True)
    all_records = []

    for fam_key, info in FAMILIES.items():
        recs = fetch_family_sequences(fam_key, info['query'], target_count=target_per_family)
        all_records.extend(recs)
        time.sleep(0.5)

    df = pd.DataFrame(all_records)
    csv_path = os.path.join(output_dir, "uniprot_protein_families.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(df)} total sequences to {csv_path}")

    # Save as fasta as well
    fasta_path = os.path.join(output_dir, "uniprot_protein_families.fasta")
    with open(fasta_path, "w") as f:
        for _, row in df.iterrows():
            f.write(f">{row['Accession']}|{row['EntryName']}|{row['Family']}|Len={row['Length']}\n")
            seq = row['Sequence']
            for i in range(0, len(seq), 60):
                f.write(seq[i:i+60] + "\n")

    print("\nDataset Summary:")
    summary = df.groupby('Family').agg(
        Count=('Accession', 'count'),
        Mean_Length=('Length', 'mean'),
        Min_Length=('Length', 'min'),
        Max_Length=('Length', 'max')
    ).reset_index()
    print(summary.to_string(index=False))

    return df

if __name__ == "__main__":
    download_all_data()
