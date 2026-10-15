"""
generate_report.py
Script to generate the 5-page PDF report for ISC 211 Assignment.
Author: Karunya (2025bcd0025)
"""

import os
import sys
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas for adding running headers and page numbers (Page X of Y)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Running header (on pages > 1)
        if self._pageNumber > 1:
            self.drawString(50, 11 * inch - 34, "ISC 211: Introduction to Bioinformatics | Assignment Report")
            self.drawRightString(8.5 * inch - 50, 11 * inch - 34, "Karunya (2025bcd0025)")
            self.setStrokeColor(colors.HexColor("#cccccc"))
            self.setLineWidth(0.5)
            self.line(50, 11 * inch - 38, 8.5 * inch - 50, 11 * inch - 38)

        # Running footer
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(50, 42, 8.5 * inch - 50, 42)
        self.drawString(50, 30, "IIIT Kottayam — ISC 211 Assignment")
        self.drawRightString(8.5 * inch - 50, 30, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf_report(output_filename="report.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=colors.HexColor('#0f2b48'),
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1a365d'),
        alignment=1
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=colors.HexColor('#1a365d'),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11.5,
        textColor=colors.HexColor('#2b5c8f'),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.4,
        textColor=colors.HexColor('#222222'),
        spaceAfter=3.5,
        alignment=4 # Justified
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=9.8,
        textColor=colors.HexColor('#222222'),
        leftIndent=10,
        firstLineIndent=-7,
        spaceAfter=2
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=8.5,
        alignment=1
    )
    
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        alignment=1
    )

    caption_style = ParagraphStyle(
        'CaptionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.2,
        leading=9,
        textColor=colors.HexColor('#444444'),
        alignment=1,
        spaceAfter=4
    )

    story = []

    # ==========================================
    # PAGE 1: TITLE, ABSTRACT, SEC 1 & 2
    # ==========================================
    story.append(Paragraph("ISC 211: Introduction to Bioinformatics — Individual Assignment", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Protein Family Classification Using Hierarchical Agglomerative Clustering", subtitle_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Student:</b> Karunya &nbsp;|&nbsp; <b>Roll Number:</b> 2025bcd0025 &nbsp;|&nbsp; <b>Allocation:</b> R = 25 &rarr; Topic 3, Algorithm M12<br/>"
                           "<b>Topic:</b> Protein Family Classification Using Machine Learning &nbsp;|&nbsp; <b>Algorithm:</b> Hierarchical Clustering<br/>"
                           "<b>Reference Paper:</b> T. Idhaya, A. Suruliandi, S. P. Raja, <i>The Protein Journal</i> 43, 171–186 (2024)", meta_style))
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a365d"), spaceAfter=5, spaceBefore=1))

    # Abstract Box
    abstract_text = (
        "<b>Abstract—</b> In this assignment, hierarchical agglomerative clustering (M12) was implemented to classify protein sequences into "
        "functional families (Topic 3). Following the literature survey by Idhaya et al. (2024), we selected four benchmark protein families: "
        "G-protein coupled receptors (GPCRs), potassium ion channels, nuclear hormone receptors, and protein kinases. A curated dataset of 582 "
        "reviewed Swiss-Prot sequences was obtained from UniProt. We extracted 440 sequence-derived features, covering amino acid composition "
        "(AAC), CTD physicochemical descriptors, macroscopic sequence properties, and dipeptide composition (DPC). To reduce dimensionality, "
        "an ANOVA F-statistic filter was used to select the top 60 features. We evaluated four linkage methods: Ward, complete, average (UPGMA), "
        "and single linkage. Ward's method gave the best clustering quality, achieving a cophenetic correlation of 0.6952, training cluster purity "
        "of 93.12%, and an Adjusted Rand Index (ARI) of 0.8347. On an unseen test set of 117 sequences, the model achieved 91.45% accuracy and "
        "a macro F1-score of 91.29%, with 100% recall on GPCRs. The results demonstrate that primary sequence and physicochemical composition "
        "provide strong discriminatory signals for protein family classification."
    )
    
    abs_table = Table([[Paragraph(abstract_text, body_style)]], colWidths=[512])
    abs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f4f7fb")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#b0c4de")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(abs_table)
    story.append(Spacer(1, 4))

    # Section 1: Biological Problem Formulation
    story.append(Paragraph("1. Biological Problem Formulation", h1_style))
    p1_text = (
        "Proteins perform diverse biochemical roles in living cells, including catalytic activity, structural support, and signal transduction. "
        "High-throughput sequencing projects have yielded millions of primary protein sequences, but experimental determination of their three-dimensional "
        "structures and biochemical functions remains slow and labor-intensive. A protein family consists of proteins that share common evolutionary ancestry, "
        "similar sequences, conserved structural domains, and related functions. Grouping proteins into families is valuable for functional annotation of newly "
        "sequenced genomes, understanding molecular evolution, and identifying potential drug targets (Idhaya et al., 2024).<br/>"
        "Based on the assignment formula using roll number 2025bcd0025 (last three digits R = 025): "
        "Topic = ((25 - 1) mod 11) + 1 = Topic 3 (Protein Family Classification), and Algorithm = ((25 - 1) mod 13) + 1 = M12 (Hierarchical Clustering). "
        "We focus on four representative families reviewed in the literature:"
    )
    story.append(Paragraph(p1_text, body_style))
    
    story.append(Paragraph("• <b>G-Protein Coupled Receptors (GPCRs):</b> 7-transmembrane &alpha;-helical receptors that sense extracellular signals and activate internal signaling pathways. They are common targets for pharmaceutical drugs.", bullet_style))
    story.append(Paragraph("• <b>Nuclear Hormone Receptors (NRs):</b> Transcription factors with conserved zinc-finger DNA-binding domains and ligand-binding domains that control gene expression in response to steroids and hormones.", bullet_style))
    story.append(Paragraph("• <b>Ion Channels (ICs, Potassium Channels):</b> Pore-forming membrane proteins with conserved selectivity filters that regulate potassium ion flow across cell membranes.", bullet_style))
    story.append(Paragraph("• <b>Protein Kinases (PKs):</b> Catalytic enzymes that transfer phosphate groups from ATP to specific substrate proteins, regulating major signaling cascades.", bullet_style))
    story.append(Spacer(1, 3))

    # Section 2: Dataset Acquisition & Preprocessing
    story.append(Paragraph("2. Dataset Acquisition & Curation", h1_style))
    p2_text = (
        "We retrieved protein sequences from the curated <b>UniProt Swiss-Prot</b> database (reviewed: true) using the UniProt REST API. "
        "To ensure data quality, we applied three filtering criteria: (1) keeping sequences with lengths between 200 and 800 amino acids; "
        "(2) removing sequences containing ambiguous residues such as B, Z, X, U, or O; and (3) removing duplicate sequences. "
        "A total of 582 non-redundant sequences were retained. The dataset was split into an 80% training set (465 proteins) for cluster "
        "analysis and prototype estimation, and a 20% stratified test set (117 proteins) for evaluating performance on unseen data."
    )
    story.append(Paragraph(p2_text, body_style))
    story.append(Spacer(1, 3))

    # Table 1: Dataset Summary
    t1_data = [
        [Paragraph("<b>Protein Family</b>", table_cell_bold), Paragraph("<b>UniProt Family Annotation</b>", table_cell_bold), Paragraph("<b>Count</b>", table_cell_bold), Paragraph("<b>Mean Len &plusmn; SD</b>", table_cell_bold), Paragraph("<b>Train (80%)</b>", table_cell_bold), Paragraph("<b>Test (20%)</b>", table_cell_bold)],
        [Paragraph("GPCR", table_cell), Paragraph("G-protein coupled receptor 1 family", table_cell), Paragraph("150", table_cell), Paragraph("379.5 &plusmn; 58.2", table_cell), Paragraph("120", table_cell), Paragraph("30", table_cell)],
        [Paragraph("Ion Channel (IC)", table_cell), Paragraph("Potassium channel family", table_cell), Paragraph("132", table_cell), Paragraph("556.2 &plusmn; 131.4", table_cell), Paragraph("105", table_cell), Paragraph("27", table_cell)],
        [Paragraph("Nuclear Receptor (NR)", table_cell), Paragraph("Nuclear hormone receptor family", table_cell), Paragraph("150", table_cell), Paragraph("496.9 &plusmn; 89.7", table_cell), Paragraph("120", table_cell), Paragraph("30", table_cell)],
        [Paragraph("Protein Kinase (PK)", table_cell), Paragraph("Protein kinase superfamily", table_cell), Paragraph("150", table_cell), Paragraph("533.0 &plusmn; 114.6", table_cell), Paragraph("120", table_cell), Paragraph("30", table_cell)],
        [Paragraph("<b>Total</b>", table_cell_bold), Paragraph("<b>Swiss-Prot Curated Dataset</b>", table_cell_bold), Paragraph("<b>582</b>", table_cell_bold), Paragraph("<b>489.1 &plusmn; 121.8</b>", table_cell_bold), Paragraph("<b>465</b>", table_cell_bold), Paragraph("<b>117</b>", table_cell_bold)]
    ]
    t1 = Table(t1_data, colWidths=[80, 160, 45, 87, 70, 70])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a365d")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#f8f9fa")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#e9ecef")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t1)
    story.append(Paragraph("<b>Table 1:</b> Summary of curated Swiss-Prot benchmark sequences across target protein families.", caption_style))

    # ==========================================
    # PAGE 2: SEC 3 FEATURE ENGINEERING & FIG 1
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("3. Feature Extraction & Selection", h1_style))
    p3_text = (
        "Because protein sequences have varying lengths, numerical descriptors must be extracted to represent each protein. "
        "Following common feature extraction practices reviewed in Idhaya et al. (2024), we extracted 440 features:<br/>"
        "<b>1. Amino Acid Composition (AAC, 20 features):</b> The relative frequency of each amino acid, "
        "<i>f(i) = N<sub>i</sub> / L</i>, representing overall residue usage.<br/>"
        "<b>2. Physicochemical Properties / CTD (15 features):</b> Amino acids were grouped into three bins for each of five physicochemical "
        "attributes (Chothia and Kyte-Doolittle classifications): <i>Hydrophobicity</i> (Hydrophilic, Neutral, Hydrophobic), <i>van der Waals Volume</i> "
        "(Small, Medium, Large), <i>Polarity</i> (Low, Neutral, High), <i>Charge</i> (Positive, Negative, Neutral), and <i>Secondary Structure Propensity</i> "
        "(Helix, Strand, Coil). The fraction of residues falling in each bin was computed.<br/>"
        "<b>3. Macroscopic Descriptors (5 features):</b> Sequence length, aromatic fraction (F+W+Y), aliphatic fraction (A+V+I+L), "
        "tiny residue fraction (G+A+S), and net charge proxy at pH 7.<br/>"
        "<b>4. Dipeptide Composition (DPC, 400 features):</b> The frequency of all adjacent pairs <i>f(i, j) = N<sub>ij</sub> / (L - 1)</i>, "
        "which preserves local sequence context."
    )
    story.append(Paragraph(p3_text, body_style))
    story.append(Spacer(1, 2))

    story.append(Paragraph("3.1 Feature Selection via ANOVA F-Score", h2_style))
    p31_text = (
        "Using all 400 dipeptides directly creates a high-dimensional feature space with sparse counts and noise. As discussed in Section 8.4 "
        "of the review paper, filter methods such as ANOVA F-tests effectively identify the most informative descriptors. We used an ANOVA F-test "
        "to score each feature and selected the top 60 features. This improved cluster purity from 56.8% to <b>93.12%</b> and test accuracy from "
        "58.1% to <b>91.45%</b>. All selected features were standardized (mean = 0, std = 1) before clustering."
    )
    story.append(Paragraph(p31_text, body_style))
    story.append(Spacer(1, 2))

    if os.path.exists("figures/feature_importance.png"):
        story.append(Image("figures/feature_importance.png", width=6.6*inch, height=3.1*inch))
        story.append(Paragraph("<b>Figure 1:</b> Top 15 features ranked by ANOVA F-statistic. Hydrophobicity, polarity, and charge distributions show the strongest differences across families.", caption_style))

    story.append(Paragraph("<b>Biological Explanation:</b> Hydrophobic composition (F = 396.1) and low polarity (F = 383.5) scored highest because GPCRs have seven lipid-spanning transmembrane helices. Nuclear receptors showed higher cysteine composition (AAC_C, F = 114.6) due to the cysteine-rich zinc fingers that coordinate zinc ions. Kinases had higher negative charge proportions (F = 320.4), consistent with the acidic residues involved in ATP binding and coordination of divalent cations.", body_style))

    # ==========================================
    # PAGE 3: SEC 4 HIERARCHICAL CLUSTERING METHODOLOGY & DENDROGRAM
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("4. Methodology: Hierarchical Agglomerative Clustering", h1_style))
    p4_text = (
        "Hierarchical Agglomerative Clustering (HAC) is an unsupervised bottom-up method commonly used in bioinformatics and phylogenetic studies. "
        "It starts by treating every sequence as its own cluster and iteratively merges the closest pair of clusters according to a chosen linkage "
        "criterion until all samples form a single tree (dendrogram).<br/>"
        "We tested four standard linkage methods with Euclidean distance:"
    )
    story.append(Paragraph(p4_text, body_style))

    story.append(Paragraph("• <b>Ward's Linkage:</b> Minimizes the increase in total within-cluster sum of squares: "
                           "<i>&Delta;ESS(A, B) = (|A|&middot;|B|) / (|A| + |B|) &middot; ||&mu;<sub>A</sub> - &mu;<sub>B</sub>||<sup>2</sup></i>. Tends to produce clusters of similar size and spherical shapes.", bullet_style))
    story.append(Paragraph("• <b>Complete Linkage:</b> Uses the maximum distance between points in each cluster: <i>D(A, B) = max { d(x, y) : x &isin; A, y &isin; B }</i>. Produces compact clusters.", bullet_style))
    story.append(Paragraph("• <b>Average Linkage (UPGMA):</b> Uses the average distance between all pairs of points: <i>D(A, B) = (1 / (|A||B|)) &sum; &sum; d(x, y)</i>. Standard method for biological trees.", bullet_style))
    story.append(Paragraph("• <b>Single Linkage:</b> Uses the minimum distance between points: <i>D(A, B) = min { d(x, y) : x &isin; A, y &isin; B }</i>. Can cause chaining artifacts.", bullet_style))
    story.append(Spacer(1, 2))

    story.append(Paragraph("4.1 Cophenetic Correlation and Test Inference", h2_style))
    p41_text = (
        "To check how well the dendrogram preserves original pairwise distances, we computed the <b>Cophenetic Correlation Coefficient (CPCC)</b>: "
        "<i>CPCC = &sum; (d<sub>ij</sub> - d_avg)(c<sub>ij</sub> - c_avg) / [ &radic;&sum;(d<sub>ij</sub> - d_avg)<sup>2</sup> &middot; &radic;&sum;(c<sub>ij</sub> - c_avg)<sup>2</sup> ]</i>, "
        "where <i>d<sub>ij</sub></i> is the original Euclidean distance and <i>c<sub>ij</sub></i> is the dendrogram height where objects <i>i</i> and <i>j</i> merge.<br/>"
        "To evaluate on unseen test data, the training dendrogram was cut at <i>k = 4</i> clusters. Each cluster was labeled by its majority family, "
        "and its centroid was computed. Unseen test samples were assigned to the nearest cluster centroid: "
        "<i>y_pred = Label(arg min<sub>k</sub> ||x<sub>test</sub> - &mu;<sub>k</sub>||)</i>."
    )
    story.append(Paragraph(p41_text, body_style))
    story.append(Spacer(1, 2))

    if os.path.exists("figures/dendrogram_ward.png"):
        story.append(Image("figures/dendrogram_ward.png", width=6.6*inch, height=3.0*inch))
        story.append(Paragraph("<b>Figure 2:</b> Hierarchical clustering dendrogram using Ward's linkage (truncated to top 40 branches). The horizontal dashed line marks the cut-off height separating the sequences into four primary clusters corresponding to GPCR, Ion Channel, Kinase, and Nuclear Receptor families.", caption_style))

    # ==========================================
    # PAGE 4: EXPERIMENTAL RESULTS, TABLES & PCA
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("5. Experimental Results", h1_style))
    p5_text = (
        "We compared the four linkage criteria using both unsupervised metrics (CPCC, Silhouette score, Davies-Bouldin index) and ground-truth "
        "alignment metrics (Adjusted Rand Index, cluster purity, unseen test accuracy). As shown in Table 2, Ward's linkage performed best for "
        "recovering biological families, yielding an Adjusted Rand Index (ARI) of 0.8347, cluster purity of 93.12%, and test accuracy of 91.45%."
    )
    story.append(Paragraph(p5_text, body_style))
    story.append(Spacer(1, 2))

    # Table 2: Linkage Comparison
    t2_data = [
        [Paragraph("<b>Linkage Method</b>", table_cell_bold), Paragraph("<b>CPCC</b>", table_cell_bold), Paragraph("<b>Silhouette</b>", table_cell_bold), Paragraph("<b>Davies-Bouldin</b>", table_cell_bold), Paragraph("<b>ARI</b>", table_cell_bold), Paragraph("<b>NMI</b>", table_cell_bold), Paragraph("<b>Cluster Purity</b>", table_cell_bold), Paragraph("<b>Test Accuracy</b>", table_cell_bold), Paragraph("<b>Test Macro F1</b>", table_cell_bold)],
        [Paragraph("<b>Ward (Variance)</b>", table_cell_bold), Paragraph("0.6952", table_cell), Paragraph("0.1409", table_cell), Paragraph("2.1476", table_cell), Paragraph("<b>0.8347</b>", table_cell_bold), Paragraph("<b>0.8341</b>", table_cell_bold), Paragraph("<b>93.12%</b>", table_cell_bold), Paragraph("<b>91.45%</b>", table_cell_bold), Paragraph("<b>91.29%</b>", table_cell_bold)],
        [Paragraph("Complete (Max Dist)", table_cell), Paragraph("0.6672", table_cell), Paragraph("0.1108", table_cell), Paragraph("2.1450", table_cell), Paragraph("0.3899", table_cell), Paragraph("0.4809", table_cell), Paragraph("59.57%", table_cell), Paragraph("67.52%", table_cell), Paragraph("59.55%", table_cell)],
        [Paragraph("Average (UPGMA)", table_cell), Paragraph("<b>0.7578</b>", table_cell_bold), Paragraph("<b>0.2236</b>", table_cell_bold), Paragraph("<b>1.0996</b>", table_cell_bold), Paragraph("0.3109", table_cell), Paragraph("0.4988", table_cell), Paragraph("50.97%", table_cell), Paragraph("51.28%", table_cell), Paragraph("36.97%", table_cell)],
        [Paragraph("Single (Min Dist)", table_cell), Paragraph("0.5505", table_cell), Paragraph("0.1444", table_cell), Paragraph("0.6520", table_cell), Paragraph("0.0001", table_cell), Paragraph("0.0127", table_cell), Paragraph("26.45%", table_cell), Paragraph("29.91%", table_cell), Paragraph("17.71%", table_cell)]
    ]
    t2 = Table(t2_data, colWidths=[92, 46, 50, 60, 48, 48, 62, 53, 53])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a365d")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#e8f4fd")),
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t2)
    story.append(Paragraph("<b>Table 2:</b> Comparison of hierarchical clustering linkage criteria on the dataset.", caption_style))
    story.append(Spacer(1, 2))

    if os.path.exists("figures/pca_clusters_vs_families.png"):
        story.append(Image("figures/pca_clusters_vs_families.png", width=6.6*inch, height=2.6*inch))
        story.append(Paragraph("<b>Figure 3:</b> 2D PCA projection of the dataset: (A) True biological family labels; (B) Clusters found by Ward's hierarchical clustering (k=4) with cluster centroids shown as black 'X' marks.", caption_style))

    story.append(Paragraph("<b>Training Set Clustering Breakdown:</b> The 465 training sequences grouped into four clusters as follows: <i>Cluster 1</i> (117 GPCRs, 4 ICs &rarr; GPCR); <i>Cluster 2</i> (101 ICs, 3 GPCRs, 1 NR, 21 PK &rarr; Ion Channel); <i>Cluster 3</i> (99 PKs, 3 NRs &rarr; Protein Kinase); <i>Cluster 4</i> (116 NRs &rarr; Nuclear Receptor). GPCRs and Nuclear Receptors separated with almost no mixing.", body_style))

    # ==========================================
    # PAGE 5: TEST SET METRICS, DISCUSSION, CONCLUSION & REFS
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("5.1 Performance on Unseen Test Sequences", h2_style))
    
    if os.path.exists("figures/confusion_matrix.png"):
        cm_img = Image("figures/confusion_matrix.png", width=3.1*inch, height=2.5*inch)
    else:
        cm_img = Paragraph("Confusion matrix image missing", body_style)

    # Table 3: Per Class Report
    t3_data = [
        [Paragraph("<b>Protein Family</b>", table_cell_bold), Paragraph("<b>Precision</b>", table_cell_bold), Paragraph("<b>Recall</b>", table_cell_bold), Paragraph("<b>F1-Score</b>", table_cell_bold), Paragraph("<b>Support</b>", table_cell_bold)],
        [Paragraph("GPCR", table_cell), Paragraph("93.75%", table_cell), Paragraph("<b>100.00%</b>", table_cell_bold), Paragraph("<b>96.77%</b>", table_cell_bold), Paragraph("30", table_cell)],
        [Paragraph("Ion Channel (IC)", table_cell), Paragraph("80.65%", table_cell), Paragraph("92.59%", table_cell), Paragraph("86.21%", table_cell), Paragraph("27", table_cell)],
        [Paragraph("Nuclear Receptor (NR)", table_cell), Paragraph("<b>96.55%</b>", table_cell_bold), Paragraph("93.33%", table_cell), Paragraph("94.92%", table_cell), Paragraph("30", table_cell)],
        [Paragraph("Protein Kinase (PK)", table_cell), Paragraph("96.00%", table_cell), Paragraph("80.00%", table_cell), Paragraph("87.27%", table_cell), Paragraph("30", table_cell)],
        [Paragraph("<b>Macro Average</b>", table_cell_bold), Paragraph("<b>91.74%</b>", table_cell_bold), Paragraph("<b>91.48%</b>", table_cell_bold), Paragraph("<b>91.29%</b>", table_cell_bold), Paragraph("<b>117</b>", table_cell_bold)],
        [Paragraph("<b>Overall Accuracy</b>", table_cell_bold), Paragraph("—", table_cell), Paragraph("—", table_cell), Paragraph("<b>91.45%</b>", table_cell_bold), Paragraph("<b>117</b>", table_cell_bold)]
    ]
    t3 = Table(t3_data, colWidths=[90, 48, 48, 48, 44])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a365d")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0,1), (-1,-3), [colors.white, colors.HexColor("#f8f9fa")]),
        ('BACKGROUND', (0,-2), (-1,-1), colors.HexColor("#e9ecef")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))

    combo_table = Table([[cm_img, t3]], colWidths=[235, 277])
    combo_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(combo_table)
    story.append(Paragraph("<b>Figure 4 & Table 3:</b> Confusion matrix and classification report for the 117 unseen test sequences.", caption_style))
    story.append(Spacer(1, 2))

    # Section 6: Biological Discussion
    story.append(Paragraph("6. Discussion", h1_style))
    p6_text = (
        "The experimental results correspond well with known biochemical characteristics of each family:<br/>"
        "<b>1. GPCR Classification:</b> GPCRs achieved 100% recall on the test set. Their high proportion of hydrophobic residues "
        "(leucine, valine, isoleucine) across seven membrane-spanning segments clearly distinguishes them from soluble globular proteins.<br/>"
        "<b>2. Nuclear Receptors:</b> NRs formed a distinct cluster with high precision (96.55%) and recall (93.33%). The abundance of cysteines "
        "forming zinc finger modules in their DNA-binding domain gives them a unique composition compared to other families.<br/>"
        "<b>3. Ion Channels and Kinases:</b> A small number of kinases (5 out of 30) were assigned to the ion channel cluster. Both protein types "
        "contain large cytoplasmic regions with mixed &alpha;/&beta; secondary structures, resulting in minor feature overlap.<br/>"
        "<b>4. Comparison of Linkages:</b> Average linkage preserved the original distance matrix best (CPCC = 0.7578), but Ward's linkage achieved "
        "substantially higher test accuracy (91.45% vs 51.28%) because it minimizes within-cluster variance, preventing chaining effects."
    )
    story.append(Paragraph(p6_text, body_style))
    story.append(Spacer(1, 2))

    # Section 7: Conclusion & References
    story.append(Paragraph("7. Conclusion", h1_style))
    p7_text = (
        "In this work, hierarchical clustering was used to classify protein sequences into four functional families. Using 582 Swiss-Prot "
        "sequences, sequence-based feature extraction combined with ANOVA feature selection produced a representation that achieved 93.12% "
        "training cluster purity and 91.45% accuracy on an unseen test set. This confirms that simple sequence composition and physicochemical "
        "descriptors can reliably group proteins into their correct biological families without requiring 3D structural data."
    )
    story.append(Paragraph(p7_text, body_style))
    story.append(Spacer(1, 2))

    story.append(Paragraph("References", h2_style))
    refs = [
        "1. T. Idhaya, A. Suruliandi, S. P. Raja. <i>A Comprehensive Review on Machine Learning Techniques for Protein Family Prediction</i>, The Protein Journal, 43:171–186, 2024.",
        "2. M. Bhasin, G. P. S. Raghava. <i>GPCRpred: An SVM-Based Method for Prediction of Families and Subfamilies of G-Protein Coupled Receptors</i>, Nucleic Acids Res., 32:W383–W389, 2004.",
        "3. K. C. Chou, D. W. Elrod. <i>Prediction of Enzyme Family Classes</i>, J. Proteome Res., 2(2):183–190, 2003.",
        "4. K. Han, M. Wang, L. Zhang, et al. <i>Predicting Ion Channels Genes and Their Types with Machine Learning Techniques</i>, Front. Genet., 10:399, 2019.",
        "5. UniProt Consortium. <i>UniProt: The Universal Protein Knowledgebase in 2023</i>, Nucleic Acids Res., 51(D1):D523–D531, 2023."
    ]
    for r in refs:
        story.append(Paragraph(r, bullet_style))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"\nPDF Report successfully re-compiled: {output_filename}")

if __name__ == "__main__":
    build_pdf_report("report.pdf")
