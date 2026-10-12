# Generate Native 16:9 PowerPoint Presentation for MST vs K-Means
$ErrorActionPreference = "Stop"

$repoRoot = (Get-Location).Path
$outputPptx = Join-Path $repoRoot "docs\presentation\MST_vs_KMeans_Final_Presentation.pptx"
$figDir = Join-Path $repoRoot "results\figures"

$msoTrue = -1
$msoFalse = 0

Write-Host "Initializing Microsoft PowerPoint COM Object..."
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = $msoTrue

try {
    $presentation = $ppt.Presentations.Add($msoTrue)
    
    # Set 16:9 Widescreen dimensions (13.333 x 7.5 inches = 960 x 540 points)
    $presentation.PageSetup.SlideWidth = 960
    $presentation.PageSetup.SlideHeight = 540

    # Color Constants (RGB as integers: R + G*256 + B*65536)
    $cBg = 0x160d09        # #090d16
    $cCardBg = 0x1f1811    # #11181f
    $cWhite = 0xffffff     # #ffffff
    $cCyan = 0xd4b606      # #06b6d4
    $cBlue = 0xf6823b      # #3b82f6
    $cTextMuted = 0xa39480 # #8094a3
    $cCardBorder = 0x37291f# #1f2937

    function Set-SlideTheme($slide) {
        $slide.FollowMasterBackground = $msoFalse
        $slide.Background.Fill.Solid()
        $slide.Background.Fill.ForeColor.RGB = $cBg
    }

    function Add-Header($slide, $cat, $title, $sub) {
        $hBox = $slide.Shapes.AddTextbox(1, 40, 20, 880, 70) # msoTextOrientationHorizontal = 1
        $tf = $hBox.TextFrame
        $tf.MarginTop = 0; $tf.MarginLeft = 0; $tf.MarginRight = 0; $tf.MarginBottom = 0
        $tr = $tf.TextRange
        
        $tr.Text = "$cat`r`n$title"
        $tr.Paragraphs(1).Font.Size = 10
        $tr.Paragraphs(1).Font.Bold = $msoTrue
        $tr.Paragraphs(1).Font.Color.RGB = $cBlue
        
        $tr.Paragraphs(2).Font.Size = 22
        $tr.Paragraphs(2).Font.Bold = $msoTrue
        $tr.Paragraphs(2).Font.Color.RGB = $cWhite
    }

    function Set-Notes($slide, $speaker, $notes) {
        $np = $slide.NotesPage.Shapes(2).TextFrame.TextRange
        $np.Text = "SPEAKER: $speaker`r`n`r`n$notes"
    }

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    Write-Host "Creating Slide 1..."
    $s1 = $presentation.Slides.Add(1, 12) # ppLayoutBlank = 12
    Set-SlideTheme $s1
    
    $tBox = $s1.Shapes.AddTextbox(1, 60, 100, 840, 260)
    $tf = $tBox.TextFrame
    $tr = $tf.TextRange
    $tr.Text = "Pattern Matching Lab (BCS-DS-777) &bull; Final Defense Deck`r`nMST vs K-Means Robustness Analysis`r`nA Comparative Quantitative Investigation of Graph-Theoretic Spanning Forest Clustering and Centroid Voronoi Partitioning Under Controlled Topological and Stochastic Perturbations"
    $tr.Paragraphs(1).Font.Size = 12
    $tr.Paragraphs(1).Font.Color.RGB = $cCyan
    $tr.Paragraphs(1).Font.Bold = $msoTrue
    
    $tr.Paragraphs(2).Font.Size = 32
    $tr.Paragraphs(2).Font.Color.RGB = $cWhite
    $tr.Paragraphs(2).Font.Bold = $msoTrue
    
    $tr.Paragraphs(3).Font.Size = 13
    $tr.Paragraphs(3).Font.Color.RGB = $cTextMuted

    $mBox = $s1.Shapes.AddTextbox(1, 60, 380, 840, 100)
    $mTr = $mBox.TextFrame.TextRange
    $mTr.Text = "Student Investigators: Himanshu Gupta (Alloc. No. 19) & Parth Yadav`r`nInstitution: Manav Rachna International Institute of Research and Studies (MRIIRS), Faridabad`r`nRepository: github.com/Himanshu102931/MST-KMeans-Robustness-Analysis (Checkpoint 1baf1c9)"
    $mTr.Font.Size = 11
    $mTr.Font.Color.RGB = 0xcccccc
    Set-Notes $s1 "Himanshu Gupta" "Respected external examiner, course coordinator, and faculty mentors. Good morning. I am Himanshu Gupta, Allocation Number 19, and alongside my project partner, Parth Yadav, we are presenting our final academic project in Pattern Matching Lab: MST vs K-Means Robustness Analysis."

    # ==========================================
    # SLIDE 2: Introduction
    # ==========================================
    Write-Host "Creating Slide 2..."
    $s2 = $presentation.Slides.Add(2, 12)
    Set-SlideTheme $s2
    Add-Header $s2 "MOTIVATION & CONTEXT" "The Challenge of Unsupervised Clustering" ""
    
    $b2_1 = $s2.Shapes.AddTextbox(1, 40, 100, 420, 380)
    $b2_1.TextFrame.TextRange.Text = "The Algorithmic Dilemma`r`n`r`n&bull; Inductive Bias: Every clustering algorithm imposes geometric assumptions on data.`r`n&bull; Centroid Models (K-Means): Assume compact, spherical, linearly separable clusters.`r`n&bull; Graph Models (MST): Assume continuous topological manifolds discovered via local proximity.`r`n&bull; The Conflict: Centroid models fail structurally when clusters curve or interlock."
    $b2_1.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b2_1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b2_1.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b2_1.TextFrame.TextRange.Font.Size = 12; $b2_1.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b2_2 = $s2.Shapes.AddTextbox(1, 480, 100, 440, 380)
    $b2_2.TextFrame.TextRange.Text = "Real-World Robustness Challenges`r`n`r`n&bull; Physical Sensors: Produce isotropic Gaussian coordinate noise (&sigma;).`r`n&bull; Ambient Outliers: Anomalies and background noise produce spurious data points (&eta;).`r`n&bull; Non-Linear Structures: Real biological, GIS, and sensor manifolds curve in feature space.`r`n&bull; Research Objective: Quantitatively measure robustness degradation under isolated stress."
    $b2_2.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b2_2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b2_2.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b2_2.TextFrame.TextRange.Font.Size = 12; $b2_2.TextFrame.TextRange.Font.Color.RGB = $cWhite
    Set-Notes $s2 "Parth Yadav" "In unsupervised pattern recognition, clustering algorithms make strong mathematical assumptions. K-Means assumes spherical Voronoi cells, while MST traces topological connectivity. Real data contains noise, outliers, and non-convex manifolds."

    # ==========================================
    # SLIDE 3: Problem Statement
    # ==========================================
    Write-Host "Creating Slide 3..."
    $s3 = $presentation.Slides.Add(3, 12)
    Set-SlideTheme $s3
    Add-Header $s3 "PROBLEM DEFINITION" "Research Problem & Core Questions" ""
    
    $b3_1 = $s3.Shapes.AddTextbox(1, 40, 100, 440, 380)
    $b3_1.TextFrame.TextRange.Text = "Official Allocated Objective (Allocation 19)`r`n`r`n'Compare MST-based clustering and K-Means under noise, outliers, and non-linear data distributions using quantitative robustness measures.'`r`n`r`nMethodological Gaps Addressed:`r`n&bull; Confounding noise and outliers together in unisolated sweeps.`r`n&bull; Artificial outlier inclusion distorting partition quality metrics.`r`n&bull; Black-box Python libraries obscuring algorithmic mechanics."
    $b3_1.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b3_1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b3_1.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b3_1.TextFrame.TextRange.Font.Size = 12; $b3_1.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b3_2 = $s3.Shapes.AddTextbox(1, 500, 100, 420, 380)
    $b3_2.TextFrame.TextRange.Text = "Core Research Questions`r`n`r`n&bull; RQ1 (Manifolds): Can single-linkage MST recover non-convex shapes where K-Means fails?`r`n&bull; RQ2 (Noise): At what exact threshold does Gaussian noise bridge inter-cluster margins?`r`n&bull; RQ3 (Outliers): Does single-linkage MST suffer from catastrophic cut misallocation?`r`n&bull; RQ4 (Scaling): How do practical execution runtimes scale for dense Prim vs. Lloyd?"
    $b3_2.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b3_2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b3_2.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b3_2.TextFrame.TextRange.Font.Size = 12; $b3_2.TextFrame.TextRange.Font.Color.RGB = $cWhite
    Set-Notes $s3 "Himanshu Gupta" "Our allocated objective compares MST and K-Means under noise, outliers, and non-linear distributions. We formulated four core research questions to investigate manifold discovery, noise thresholds, outlier vulnerability, and computational scalability."

    # ==========================================
    # SLIDE 4: Objectives & Scope
    # ==========================================
    Write-Host "Creating Slide 4..."
    $s4 = $presentation.Slides.Add(4, 12)
    Set-SlideTheme $s4
    Add-Header $s4 "PROJECT FOUNDATION" "Measurable Objectives & Experimental Scope" ""
    
    $b4_1 = $s4.Shapes.AddTextbox(1, 40, 100, 460, 380)
    $b4_1.TextFrame.TextRange.Text = "5 Measurable Learning Objectives`r`n`r`n&bull; LO-1: Native JS K-Means++ and dense Prim's MST verified by 64 unit tests.`r`n&bull; LO-2: Deterministic synthetic data engine with reproducible seeds (11, 22, 33).`r`n&bull; LO-3: 144 paired trials measuring Inlier Adjusted Rand Index (ARI) & degradation.`r`n&bull; LO-4: High-resolution monotonic runtime profiling across N in [100, 600].`r`n&bull; LO-5: Open-source interactive dashboard with live sweeps & CSV exports."
    $b4_1.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b4_1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b4_1.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b4_1.TextFrame.TextRange.Font.Size = 11.5; $b4_1.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b4_2 = $s4.Shapes.AddTextbox(1, 520, 100, 400, 380)
    $b4_2.TextFrame.TextRange.Text = "Experimental Scope & Boundaries`r`n`r`n&bull; Feature Space: 2D Euclidean plane (D = 2) for direct visual auditability.`r`n&bull; Sample Size: N = 300 inliers for robustness; N in [100, 600] for benchmarks.`r`n&bull; Architecture: 100% browser-native client-side JavaScript. Zero backend servers.`r`n&bull; Evaluation Metric: Chance-adjusted Inlier ARI (Hubert & Arabie, 1985)."
    $b4_2.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b4_2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b4_2.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b4_2.TextFrame.TextRange.Font.Size = 11.5; $b4_2.TextFrame.TextRange.Font.Color.RGB = $cWhite
    Set-Notes $s4 "Parth Yadav" "We defined five measurable objectives covering native algorithm implementation, reproducible synthetic generation, 144 paired trials, monotonic benchmarking, and an interactive dashboard. The scope evaluates 2D Euclidean manifolds with sample sizes up to 600."

    # ==========================================
    # SLIDE 5: K-Means Algorithm
    # ==========================================
    Write-Host "Creating Slide 5..."
    $s5 = $presentation.Slides.Add(5, 12)
    Set-SlideTheme $s5
    Add-Header $s5 "CENTROID PARADIGM" "Lloyd's K-Means & K-Means++ Seeding" ""
    
    $b5_1 = $s5.Shapes.AddTextbox(1, 40, 100, 440, 380)
    $b5_1.TextFrame.TextRange.Text = "Mathematical Formulation`r`n`r`nObjective: Minimize Inertia (WCSS):`r`nJ = &Sigma; &Sigma; || x_i - &mu;_k ||^2`r`n`r`n&bull; K-Means++ Seeding: Sample centroids with P(x) proportional to D(x)^2 (O(log K) bound).`r`n&bull; Assignment Step: Assign x_i to nearest centroid (Voronoi cell).`r`n&bull; Update Step: Recompute &mu;_k = (1 / |C_k|) &Sigma; x_i (Arithmetic mean).`r`n&bull; Convergence: Terminate when centroid shift < 10^-5 or I >= 100."
    $b5_1.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b5_1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b5_1.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b5_1.TextFrame.TextRange.Font.Size = 11.5; $b5_1.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b5_2 = $s5.Shapes.AddTextbox(1, 500, 100, 420, 380)
    $b5_2.TextFrame.TextRange.Text = "Inductive Bias & Structural Limits`r`n`r`n&bull; Noise Averaging Advantage: Centroid update is an arithmetic mean. Centroid variance is &sigma;^2 / N_k, naturally dampening zero-mean Gaussian noise.`r`n`r`n&bull; Linear Hyperplane Constraint: Decision boundaries are linear Voronoi bisectors {x : ||x - &mu;_A|| = ||x - &mu;_B||}.`r`n`r`n&bull; Geometric Blindness: Cannot bend around curved arcs or separate nested concentric shells."
    $b5_2.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b5_2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b5_2.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b5_2.TextFrame.TextRange.Font.Size = 11.5; $b5_2.TextFrame.TextRange.Font.Color.RGB = $cWhite
    Set-Notes $s5 "Himanshu Gupta" "K-Means minimizes Within-Cluster Sum of Squares using Lloyd iteration with K-Means++ initialization. Centroid averaging dampens Gaussian noise by 1/N_k. However, because boundaries are linear Voronoi hyperplanes, K-Means is structurally incapable of non-convex separation."

    # ==========================================
    # SLIDE 6: MST Clustering
    # ==========================================
    Write-Host "Creating Slide 6..."
    $s6 = $presentation.Slides.Add(6, 12)
    Set-SlideTheme $s6
    Add-Header $s6 "GRAPH PARADIGM" "Prim's MST & Graph-Theoretic Cuts" ""
    
    $b6_1 = $s6.Shapes.AddTextbox(1, 40, 100, 440, 380)
    $b6_1.TextFrame.TextRange.Text = "Graph-Theoretic Formulation`r`n`r`nComplete Graph G = (V, E), edge weights w(u, v) = ||u - v||`r`n`r`n&bull; Prim's Dense MST: Greedily adds min-weight cut edge using priority array &kappa;[v]. Time complexity: &Theta;(N^2).`r`n&bull; Zahn's Partitioning: Sort all N - 1 tree edges; delete the (K - 1) longest edges.`r`n&bull; Component Extraction: Disjoint Set Union (Union-Find) labels the K connected subtrees."
    $b6_1.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b6_1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b6_1.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b6_1.TextFrame.TextRange.Font.Size = 11.5; $b6_1.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b6_2 = $s6.Shapes.AddTextbox(1, 500, 100, 420, 380)
    $b6_2.TextFrame.TextRange.Text = "Manifold Transitivity & Fragility`r`n`r`n&bull; Single-Linkage Chaining: Points connect through sequences of short pairwise edges, discovering arbitrary continuous non-linear manifolds.`r`n`r`n&bull; The Outlier Fragility: Cluster distance is defined by the nearest neighbor pair. Intermediate noise points bridge clusters, while isolated outliers hijack tree cuts."
    $b6_2.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b6_2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b6_2.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b6_2.TextFrame.TextRange.Font.Size = 11.5; $b6_2.TextFrame.TextRange.Font.Color.RGB = $cWhite
    Set-Notes $s6 "Parth Yadav" "MST clustering constructs a Euclidean Minimum Spanning Tree via Prim's algorithm, then removes the K-1 longest edges. Single-linkage connectivity allows arbitrary manifold discovery, but creates extreme vulnerability to outlier bridging and pendant edge hijacking."

    # ==========================================
    # SLIDE 7: System Architecture
    # ==========================================
    Write-Host "Creating Slide 7..."
    $s7 = $presentation.Slides.Add(7, 12)
    Set-SlideTheme $s7
    Add-Header $s7 "SOFTWARE ENGINEERING" "Proposed Architecture: 100% Browser-Native" ""
    
    $b7_1 = $s7.Shapes.AddTextbox(1, 40, 100, 270, 380)
    $b7_1.TextFrame.TextRange.Text = "Data & PRNG Layer`r`n`r`n&bull; `js/data/prng.js`: Linear Congruential Generator (2^32 modulus) for bit-for-bit seed reproducibility.`r`n&bull; `js/data/datasets.js`: Parametric generators for Blobs, Moons, and Circles with Box-Muller transforms."
    $b7_1.TextFrame.TextRange.Paragraphs(1).Font.Size = 13; $b7_1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b7_1.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b7_1.TextFrame.TextRange.Font.Size = 11; $b7_1.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b7_2 = $s7.Shapes.AddTextbox(1, 340, 100, 280, 380)
    $b7_2.TextFrame.TextRange.Text = "Algorithm & Evaluation`r`n`r`n&bull; `js/algorithms/`: Native Lloyd K-Means++ and Prim MST with Union-Find.`r`n&bull; `js/metrics/`: Contingency tables and Hubert & Arabie Adjusted Rand Index.`r`n&bull; `js/experiments/`: Automated robustness sweeps and benchmark harness."
    $b7_2.TextFrame.TextRange.Paragraphs(1).Font.Size = 13; $b7_2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b7_2.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b7_2.TextFrame.TextRange.Font.Size = 11; $b7_2.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b7_3 = $s7.Shapes.AddTextbox(1, 650, 100, 270, 380)
    $b7_3.TextFrame.TextRange.Text = "Visualization & Verification`r`n`r`n&bull; Canvas API: High-DPI 2D coordinate scatters and tree overlays.`r`n&bull; Step-by-Step Explorer: Centroid migration and Prim frontier animation.`r`n&bull; Unit Tests: 64 automated tests passing in under 50 ms."
    $b7_3.TextFrame.TextRange.Paragraphs(1).Font.Size = 13; $b7_3.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b7_3.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b7_3.TextFrame.TextRange.Font.Size = 11; $b7_3.TextFrame.TextRange.Font.Color.RGB = $cWhite
    Set-Notes $s7 "Himanshu Gupta" "The entire research application runs natively inside the web browser with zero external dependencies. It includes an internal LCG PRNG for reproducibility, pure algorithmic modules, an ARI evaluator, interactive step-by-step visualizers, and passes 64 unit tests."

    # ==========================================
    # SLIDE 8: Dataset Families
    # ==========================================
    Write-Host "Creating Slide 8..."
    $s8 = $presentation.Slides.Add(8, 12)
    Set-SlideTheme $s8
    Add-Header $s8 "EXPERIMENTAL SETUP" "Synthetic Dataset Geometries (N = 300 Inliers)" ""
    
    $blobsImg = Join-Path $figDir "blobs_comparison.png"
    if (Test-Path $blobsImg) {
        $s8.Shapes.AddPicture($blobsImg, 0, 1, 40, 120, 270, 220)
    }
    $moonsImg = Join-Path $figDir "moons_comparison.png"
    if (Test-Path $moonsImg) {
        $s8.Shapes.AddPicture($moonsImg, 0, 1, 345, 120, 270, 220)
    }
    $circlesImg = Join-Path $figDir "circles_comparison.png"
    if (Test-Path $circlesImg) {
        $s8.Shapes.AddPicture($circlesImg, 0, 1, 650, 120, 270, 220)
    }
    
    $dDesc = $s8.Shapes.AddTextbox(1, 40, 360, 880, 120)
    $dDesc.TextFrame.TextRange.Text = "1. Gaussian Blobs (K = 3): Convex, isotropic spherical normal clusters (100 pts/cluster). Linearly separable.`r`n2. Two Moons (K = 2): Non-linear interlocking semicircular crescents (150 pts/cluster). Requires manifold transitivity.`r`n3. Concentric Circles (K = 2): Non-linear nested rings (150 pts/cluster). Centers coincide at (0, 0), defeating centroid models."
    $dDesc.TextFrame.TextRange.Font.Size = 11; $dDesc.TextFrame.TextRange.Font.Color.RGB = $cWhite
    Set-Notes $s8 "Parth Yadav" "We evaluated both algorithms on three canonical 2D dataset families with 300 inliers each: Gaussian Blobs (convex), Two Moons (interlocking non-linear manifolds), and Concentric Circles (nested rings with identical centroids at the origin)."

    # ==========================================
    # SLIDE 9: Methodology
    # ==========================================
    Write-Host "Creating Slide 9..."
    $s9 = $presentation.Slides.Add(9, 12)
    Set-SlideTheme $s9
    Add-Header $s9 "RIGOROUS EVALUATION" "Controlled Methodology & Inlier Metric Protocol" ""
    
    $b9_1 = $s9.Shapes.AddTextbox(1, 40, 100, 440, 380)
    $b9_1.TextFrame.TextRange.Text = "Controlled Perturbation Design`r`n`r`n&bull; Experiment A (Noise Sweep): Gaussian noise &sigma; in [0.00, 0.20]; outliers fixed at 0%.`r`n&bull; Experiment B (Outlier Sweep): Ambient outliers &eta; in [0%, 20%] (0, 15, 30, 60 pts); noise fixed at 0.00.`r`n&bull; Experiment C (Baseline): Clean matched baseline (&sigma;=0.00, &eta;=0%).`r`n&bull; Paired Trials: Seeds {11, 22, 33} &rarr; identical coordinates fed to both algorithms &rarr; 144 evaluations."
    $b9_1.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b9_1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b9_1.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b9_1.TextFrame.TextRange.Font.Size = 11.5; $b9_1.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b9_2 = $s9.Shapes.AddTextbox(1, 500, 100, 420, 380)
    $b9_2.TextFrame.TextRange.Text = "Evaluation Metrics & Inlier Rule`r`n`r`n&bull; Adjusted Rand Index (ARI): Chance-corrected partition concordance (Hubert & Arabie, 1985) in [-1.0, 1.0]. Expected value is 0.0 for random chance; 1.0 for perfect partition.`r`n&bull; Inlier Evaluation Protocol: ARI computed strictly over the 300 ground-truth inliers to prevent artificial outlier cluster inflation.`r`n&bull; Baseline Degradation: &Delta;ARI = max(0.0, ARI_base - ARI_pert) measuring non-negative loss."
    $b9_2.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b9_2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b9_2.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b9_2.TextFrame.TextRange.Font.Size = 11.5; $b9_2.TextFrame.TextRange.Font.Color.RGB = $cWhite
    Set-Notes $s9 "Himanshu Gupta" "We strictly separated our tests into independent noise sweeps and outlier sweeps across seeds 11, 22, and 33, producing 144 paired trials. We evaluate ARI strictly across the 300 ground-truth inliers to avoid artificial score inflation from uniform outliers."

    # ==========================================
    # SLIDE 10: Clean Dataset Results
    # ==========================================
    Write-Host "Creating Slide 10..."
    $s10 = $presentation.Slides.Add(10, 12)
    Set-SlideTheme $s10
    Add-Header $s10 "EMPIRICAL RESULTS" "Clean Geometry Results: The Topological Contrast" ""
    
    $b10 = $s10.Shapes.AddTextbox(1, 40, 95, 460, 380)
    $b10.TextFrame.TextRange.Text = "Measured Baseline Concordance (&sigma;=0.00, &eta;=0%)`r`n`r`n&bull; Gaussian Blobs (K = 3):`r`n  - K-Means ARI: 1.0000 &plusmn; 0.0000`r`n  - MST ARI:     1.0000 &plusmn; 0.0000`r`n`r`n&bull; Two Moons (K = 2):`r`n  - K-Means ARI: 0.1941 &plusmn; 0.0588 (Bisects crescents)`r`n  - MST ARI:     1.0000 &plusmn; 0.0000 (Traces crescents)`r`n`r`n&bull; Concentric Circles (K = 2):`r`n  - K-Means ARI: -0.0019 &plusmn; 0.0012 (Chance level)`r`n  - MST ARI:     1.0000 &plusmn; 0.0000 (Separates rings)"
    $b10.TextFrame.TextRange.Paragraphs(1).Font.Size = 13; $b10.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b10.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b10.TextFrame.TextRange.Font.Size = 11; $b10.TextFrame.TextRange.Font.Color.RGB = $cWhite

    if (Test-Path $moonsImg) {
        $s10.Shapes.AddPicture($moonsImg, 0, 1, 510, 110, 410, 240)
        $cTxt = $s10.Shapes.AddTextbox(1, 510, 360, 410, 60)
        $cTxt.TextFrame.TextRange.Text = "Figure 8.2: Ground Truth (Left) vs. K-Means (Center) vs. MST (Right) on Clean Two Moons (N = 300)"
        $cTxt.TextFrame.TextRange.Font.Size = 9.5; $cTxt.TextFrame.TextRange.Font.Color.RGB = $cTextMuted
    }
    Set-Notes $s10 "Parth Yadav" "On clean datasets, MST achieves perfect ARI of 1.0000 on all three geometries. K-Means matches MST on Blobs (1.0000), but fails on Two Moons (0.1941) and Concentric Circles (-0.0019) due to linear Voronoi boundaries and identical cluster centroids."

    # ==========================================
    # SLIDE 11: Noise Robustness Results
    # ==========================================
    Write-Host "Creating Slide 11..."
    $s11 = $presentation.Slides.Add(11, 12)
    Set-SlideTheme $s11
    Add-Header $s11 "EMPIRICAL RESULTS" "Experiment A: Gaussian Noise Sensitivity (&sigma; in [0, 0.20])" ""
    
    $b11 = $s11.Shapes.AddTextbox(1, 40, 95, 430, 380)
    $b11.TextFrame.TextRange.Text = "Key Numerical Findings`r`n`r`n&bull; Gaussian Blobs: Both K-Means and MST maintain perfect ARI = 1.0000 across all noise levels up to &sigma; = 0.20 (&Delta;ARI = 0.0000).`r`n`r`n&bull; Two Moons: MST holds ARI = 1.0000 at &sigma; = 0.05, drops to 0.6667 at &sigma; = 0.10, and collapses to 0.0000 at &sigma; = 0.20 (&Delta;ARI = 1.0000).`r`n`r`n&bull; Concentric Circles: MST holds ARI = 1.0000 through &sigma; = 0.10, but collapses to 0.0935 at &sigma; = 0.20 (&Delta;ARI = 0.9065).`r`n`r`n&bull; Mechanism: Noise creates Euclidean shortcuts bridging inter-cluster gaps."
    $b11.TextFrame.TextRange.Paragraphs(1).Font.Size = 13; $b11.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b11.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b11.TextFrame.TextRange.Font.Size = 11; $b11.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $noiseImg = Join-Path $figDir "ari_vs_noise.png"
    if (Test-Path $noiseImg) {
        $s11.Shapes.AddPicture($noiseImg, 0, 1, 490, 110, 430, 240)
        $cTxt = $s11.Shapes.AddTextbox(1, 490, 360, 430, 60)
        $cTxt.TextFrame.TextRange.Text = "Figure 8.4: Inlier ARI vs. Additive Gaussian Noise (&sigma; in [0.00, 0.20])"
        $cTxt.TextFrame.TextRange.Font.Size = 9.5; $cTxt.TextFrame.TextRange.Font.Color.RGB = $cTextMuted
    }
    Set-Notes $s11 "Himanshu Gupta" "Under Gaussian coordinate noise, both algorithms remain solid at 1.0000 on Blobs. But on Moons and Circles, once noise reaches sigma = 0.20, coordinate displacement bridges the gap, causing MST ARI to collapse to 0.0000 and 0.0935."

    # ==========================================
    # SLIDE 12: Outlier Robustness Results
    # ==========================================
    Write-Host "Creating Slide 12..."
    $s12 = $presentation.Slides.Add(12, 12)
    Set-SlideTheme $s12
    Add-Header $s12 "EMPIRICAL DISCOVERY" "Experiment B: Outlier Robustness & MST Cut Collapse" ""
    
    $b12 = $s12.Shapes.AddTextbox(1, 40, 95, 430, 380)
    $b12.TextFrame.TextRange.Text = "The Central Finding: Catastrophic MST Collapse`r`n`r`n&bull; 5% Outlier Plunge: On Two Moons, adding just 5% uniform outliers (15 points) causes MST ARI to drop instantly from 1.0000 to 0.0000 (&Delta;ARI = 1.0000).`r`n`r`n&bull; K-Means Resilience: On Blobs, K-Means maintains ARI = 1.0000 up to 20% outliers, while MST degrades to 0.3799.`r`n`r`n&bull; Pendant Edge Cut Misallocation: Outliers form long peripheral edges. The (K - 1) cuts sever isolated outliers into singleton clusters, leaving all 300 inliers trapped in one giant component!"
    $b12.TextFrame.TextRange.Paragraphs(1).Font.Size = 13; $b12.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b12.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b12.TextFrame.TextRange.Font.Size = 11; $b12.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $outlierImg = Join-Path $figDir "ari_vs_outliers.png"
    if (Test-Path $outlierImg) {
        $s12.Shapes.AddPicture($outlierImg, 0, 1, 490, 110, 430, 240)
        $cTxt = $s12.Shapes.AddTextbox(1, 490, 360, 430, 60)
        $cTxt.TextFrame.TextRange.Text = "Figure 8.5: Inlier ARI vs. Ambient Outlier Contamination (&eta; in [0%, 20%])"
        $cTxt.TextFrame.TextRange.Font.Size = 9.5; $cTxt.TextFrame.TextRange.Font.Color.RGB = $cTextMuted
    }
    Set-Notes $s12 "Parth Yadav" "This is our primary empirical discovery: on Two Moons, just 5% outliers causes MST ARI to plunge from 1.0000 to 0.0000. Outliers form long pendant edges that consume the K-1 cuts, isolating individual outlier points and leaving all 300 inliers lumped together in one component."

    # ==========================================
    # SLIDE 13: Performance Benchmark
    # ==========================================
    Write-Host "Creating Slide 13..."
    $s13 = $presentation.Slides.Add(13, 12)
    Set-SlideTheme $s13
    Add-Header $s13 "COMPUTATIONAL SCALABILITY" "Performance Benchmarks & Complexity Scaling" ""
    
    $b13 = $s13.Shapes.AddTextbox(1, 40, 95, 450, 380)
    $b13.TextFrame.TextRange.Text = "Measured Runtime Statistics (Blobs, K = 3)`r`n`r`n&bull; N = 100: KM 0.10 ms | MST 0.14 ms (Ratio: 1.40x mean, 2.00x median)`r`n&bull; N = 200: KM 0.16 ms | MST 0.38 ms (Ratio: 2.38x mean, 1.50x median)`r`n&bull; N = 400: KM 0.14 ms | MST 0.94 ms (Ratio: 6.71x mean, 10.00x median)`r`n&bull; N = 600: KM 0.14 ms | MST 1.70 ms (Ratio: 12.14x mean, 17.00x median)`r`n`r`n&bull; Asymptotics: Dense Prim exhibits &Theta;(N^2) quadratic growth. K-Means exhibits linear O(I &bull; K &bull; N) passes.`r`n&bull; Disambiguation: Median ratio (17.00x) guards against scheduling jitter; Mean ratio (12.14x) reflects aggregate work."
    $b13.TextFrame.TextRange.Paragraphs(1).Font.Size = 13; $b13.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b13.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b13.TextFrame.TextRange.Font.Size = 10.5; $b13.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $scaleImg = Join-Path $figDir "runtime_scaling.png"
    if (Test-Path $scaleImg) {
        $s13.Shapes.AddPicture($scaleImg, 0, 1, 510, 110, 410, 240)
        $cTxt = $s13.Shapes.AddTextbox(1, 510, 360, 410, 60)
        $cTxt.TextFrame.TextRange.Text = "Figure 8.7: Empirical Wall-Clock Runtime (ms) vs. Sample Size N in [100, 600]"
        $cTxt.TextFrame.TextRange.Font.Size = 9.5; $cTxt.TextFrame.TextRange.Font.Color.RGB = $cTextMuted
    }
    Set-Notes $s13 "Himanshu Gupta" "Micro-benchmarks from N = 100 to 600 confirm quadratic O(N^2) growth for dense Prim MST (rising to 1.70 ms), while K-Means remains sub-millisecond (0.14 ms). At N = 600, K-Means is 12.14x faster by ratio of means, and 17.00x faster by ratio of medians."

    # ==========================================
    # SLIDE 14: Conclusions & Limitations
    # ==========================================
    Write-Host "Creating Slide 14..."
    $s14 = $presentation.Slides.Add(14, 12)
    Set-SlideTheme $s14
    Add-Header $s14 "SYNTHESIS & VALUE" "Conclusions & Practitioner Decision Framework" ""
    
    $b14_1 = $s14.Shapes.AddTextbox(1, 40, 100, 440, 380)
    $b14_1.TextFrame.TextRange.Text = "Practitioner Selection Heuristic`r`n`r`n&bull; Spherical Clusters + Background Noise:`r`n  &rarr; SELECT K-MEANS (Robust centroid averaging; fast linear runtime).`r`n`r`n&bull; Non-Convex Manifolds + Clean Data:`r`n  &rarr; SELECT MST CLUSTERING (Perfect single-linkage topological discovery).`r`n`r`n&bull; Non-Convex Manifolds + Heavy Outliers:`r`n  &rarr; NEITHER STANDARD ALGORITHM WORKS!`r`n  Deploy density-based methods (DBSCAN) or outlier-trimmed MST variants."
    $b14_1.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b14_1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b14_1.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b14_1.TextFrame.TextRange.Font.Size = 11.5; $b14_1.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b14_2 = $s14.Shapes.AddTextbox(1, 500, 100, 420, 380)
    $b14_2.TextFrame.TextRange.Text = "Threats to Validity & Future Scope`r`n`r`n&bull; Experimental Limitations:`r`n  - Small seed sample (M = 3) reflects exploratory variance.`r`n  - 2D synthetic manifolds avoid high-dimensional distance concentration.`r`n  - Browser monotonic timer coarsening (5 - 100 &mu;s).`r`n`r`n&bull; Future Research Extensions:`r`n  - Outlier-trimmed MST (density filtering prior to tree cuts).`r`n  - Sparse Delaunay triangulations reducing MST to O(N log N).`r`n  - Higher-dimensional benchmark sweeps (D in [2, 100])."
    $b14_2.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b14_2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b14_2.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b14_2.TextFrame.TextRange.Font.Size = 11.5; $b14_2.TextFrame.TextRange.Font.Color.RGB = $cWhite
    Set-Notes $s14 "Parth Yadav" "To conclude: K-Means is ideal for noisy spherical clusters. MST is ideal for clean curved manifolds. When both non-convexity and outliers exist, neither standard method succeeds. We acknowledge limitations of 3 seeds, 2D data, and browser timer coarsening."

    # ==========================================
    # SLIDE 15: References & Defense Q&A
    # ==========================================
    Write-Host "Creating Slide 15..."
    $s15 = $presentation.Slides.Add(15, 12)
    Set-SlideTheme $s15
    Add-Header $s15 "ACADEMIC DEFENSE" "References & Viva Defense Q&A" ""
    
    $b15_1 = $s15.Shapes.AddTextbox(1, 40, 100, 440, 380)
    $b15_1.TextFrame.TextRange.Text = "Essential Academic References`r`n`r`n&bull; MacQueen (1967) / Lloyd (1982): Foundations of K-Means optimization & vector quantization.`r`n&bull; Arthur & Vassilvitskii (2007): k-means++ careful seeding approximation bounds.`r`n&bull; Prim (1957) / Zahn (1971): Minimum Spanning Trees & gestalt graph clustering.`r`n&bull; Hubert & Arabie (1985): Comparing partitions & Adjusted Rand Index.`r`n&bull; Jain (2010): Data clustering: 50 years beyond K-means."
    $b15_1.TextFrame.TextRange.Paragraphs(1).Font.Size = 14; $b15_1.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cCyan; $b15_1.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b15_1.TextFrame.TextRange.Font.Size = 10.5; $b15_1.TextFrame.TextRange.Font.Color.RGB = $cWhite

    $b15_2 = $s15.Shapes.AddTextbox(1, 500, 120, 420, 320)
    $b15_2.TextFrame.TextRange.Text = "Thank You`r`n`r`nWe welcome questions, critiques, and discussion from the examination committee.`r`n`r`nHimanshu Gupta (Alloc. No. 19) &bull; Parth Yadav`r`nDepartment of Computer Science and Engineering`r`nMRIIRS, Faridabad, India`r`n`r`nRepository: github.com/Himanshu102931/MST-KMeans-Robustness-Analysis"
    $b15_2.TextFrame.TextRange.Paragraphs(1).Font.Size = 24; $b15_2.TextFrame.TextRange.Paragraphs(1).Font.Color.RGB = $cWhite; $b15_2.TextFrame.TextRange.Paragraphs(1).Font.Bold = $msoTrue
    $b15_2.TextFrame.TextRange.Font.Size = 11; $b15_2.TextFrame.TextRange.Font.Color.RGB = 0x93c5fd
    Set-Notes $s15 "Himanshu Gupta" "Our research builds on foundational literature from MacQueen, Lloyd, Arthur, Prim, Zahn, and Hubert & Arabie. We thank our mentors and examiners, and we welcome your questions and look forward to demonstrating the live system."

    # Save Presentation
    Write-Host "Saving presentation to $outputPptx..."
    $presentation.SaveAs($outputPptx)
    Write-Host "Presentation saved successfully!"
}
finally {
    if ($presentation) { $presentation.Close() }
    $ppt.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
    Write-Host "PowerPoint COM released cleanly."
}

