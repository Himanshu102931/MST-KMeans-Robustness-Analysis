# Presentation Speaker Notes & Defense Speaking Script
## MST vs K-Means Robustness Analysis — Academic Viva & Evaluation

* **Course**: Pattern Matching Lab (`BCS-DS-777`)
* **Institution**: Manav Rachna International Institute of Research and Studies (MRIIRS)
* **Lead Presenter**: Himanshu Gupta (Allocation No. 19)
* **Co-Presenter**: Parth Yadav
* **Target Presentation Duration**: 10 to 12 Minutes (~45–50 seconds per slide)

---

### Slide 1: Title Slide (0:00 – 0:45)
* **Speaker**: Himanshu Gupta
* **Spoken Script**:
  > *"Respected external examiner, course coordinator, and faculty mentors. Good morning.  
  > I am Himanshu Gupta, Allocation Number 19, and alongside my project partner, Parth Yadav, we are presenting our final academic project in Pattern Matching Lab (`BCS-DS-777`): **'MST vs K-Means Robustness Analysis: A Comparative Quantitative Investigation of Graph-Theoretic Spanning Forest Clustering and Centroid Voronoi Partitioning Under Controlled Topological and Stochastic Perturbations.'**  
  > Our project compares how two fundamentally contrasting clustering algorithms behave when exposed to real-world data imperfections—specifically geometric non-linearity, Gaussian noise, and ambient outliers—evaluated natively using browser technologies."*
* **Transition**: *"To motivate this work, Parth will now introduce the core dilemma of unsupervised clustering."*

---

### Slide 2: Introduction — The Challenge of Unsupervised Clustering (0:45 – 1:30)
* **Speaker**: Parth Yadav
* **Spoken Script**:
  > *"Thank you, Himanshu. In unsupervised pattern recognition, our goal is to uncover natural group structure from unlabelled points without ground truth to guide us. However, every clustering algorithm comes with an underlying mathematical assumption—an inductive bias.  
  > For instance, K-Means assumes that clusters are spherical, compact, and linearly separable by central prototypes. In contrast, graph-based clustering, like Minimum Spanning Tree clustering, looks at topological connectivity, chaining points together based on local proximity.  
  > In real-world domains like medical imaging, flow cytometry, or geographical sensor networks, data is rarely clean and spherical. It contains noise, outliers, and curved manifolds. This motivated our research: to test where these two models succeed, where they fail, and exactly how their performance degrades under controlled stress."*
* **Transition**: *"Himanshu will now present our specific problem statement and research questions."*

---

### Slide 3: Problem Statement & Research Questions (1:30 – 2:15)
* **Speaker**: Himanshu Gupta
* **Spoken Script**:
  > *"Our official allocated objective for Allocation 19 is: 'Compare MST-based clustering and K-Means under noise, outliers, and non-linear data distributions using quantitative robustness measures.'  
  > To address this rigorously, we formulated four core research questions:  
  > First, can MST clustering cleanly recover non-convex shapes like interlocking moons and concentric rings where K-Means is expected to fail?  
  > Second, at what exact threshold of Gaussian noise does coordinate dispersion bridge the inter-cluster gap?  
  > Third, how vulnerable is single-linkage edge cutting to uniform ambient outliers?  
  > And fourth, how do the practical client-side execution times scale for dense Prim's MST ($O(N^2)$) versus Lloyd's K-Means ($O(N)$)?"*
* **Transition**: *"Parth will outline our measurable project objectives."*

---

### Slide 4: Measurable Objectives & Scope (2:15 – 3:00)
* **Speaker**: Parth Yadav
* **Spoken Script**:
  > *"To ensure scientific rigor, we defined five measurable learning objectives. First, we implemented both algorithms completely from scratch in pure vanilla JavaScript without relying on external libraries like scikit-learn. Our implementation passed 64 automated unit tests.  
  > Second, we constructed a deterministic synthetic data engine with reproducible pseudo-random seeds.  
  > Third, we executed 144 controlled experimental trials measuring the Adjusted Rand Index strictly over ground-truth inliers.  
  > Fourth, we profiled execution runtimes using high-resolution monotonic browser timers across sample sizes from 100 to 600.  
  > And fifth, we built an interactive, open-source dashboard with step-by-step algorithmic explorers and scientific CSV exports."*
* **Transition**: *"Let us now examine the mathematical mechanics of K-Means."*

---

### Slide 5: Centroid Optimization — Lloyd's K-Means & K-Means++ (3:00 – 3:50)
* **Speaker**: Himanshu Gupta
* **Spoken Script**:
  > *"K-Means seeks to minimize the Within-Cluster Sum of Squares, or Inertia $\mathcal{J}$. We implemented Lloyd's algorithm paired with Arthur and Vassilvitskii's K-Means++ seeding.  
  > K-Means++ samples initial centroids with probability proportional to the squared distance to existing centroids, providing an $O(\log K)$ approximation guarantee.  
  > In each iteration, points are assigned to their nearest centroid, and centroids are recomputed as arithmetic means. Because the centroid update is an average, it naturally dampens zero-mean Gaussian noise.  
  > However, K-Means has a severe structural limitation: because assignments depend strictly on Euclidean distance to central prototypes, cluster boundaries are always straight linear hyperplanes. As a result, it is mathematically incapable of wrapping around non-convex manifolds."*
* **Transition**: *"Parth will explain the graph-theoretic alternative: MST-based clustering."*

---

### Slide 6: Graph Connectivity — Prim's Algorithm & Zahn's Clustering (3:50 – 4:40)
* **Speaker**: Parth Yadav
* **Spoken Script**:
  > *"To overcome geometric rigidity, we turn to graph theory. In Zahn's MST clustering, the dataset is modeled as a complete graph where every pair of points is connected by an edge weighted by their Euclidean distance.  
  > We compute the Minimum Spanning Tree using Prim's dense algorithm. Prim's algorithm iteratively adds the shortest edge crossing the cut between visited and unvisited vertices, producing an acyclic tree of $N-1$ edges in $\Theta(N^2)$ time.  
  > To form $K$ clusters, we simply sort the edges and remove the $K-1$ longest edges. The graph disconnects into $K$ subtrees, which we extract using Union-Find.  
  > Because this operates on single-linkage connectivity, MST can discover arbitrary curved manifolds. However, as our experiments will demonstrate, this same single-linkage property makes it extraordinarily sensitive to outlier bridges."*
* **Transition**: *"Himanshu will now walk through our browser-native system architecture."*

---

### Slide 7: System Architecture & Technology Stack (4:40 – 5:25)
* **Speaker**: Himanshu Gupta
* **Spoken Script**:
  > *"A key innovation of our project is that the entire research laboratory runs natively inside the web browser. There is no Python, no Node.js, and no backend database.  
  > We built modular components: an internal Linear Congruential PRNG for deterministic seeds; synthetic manifold generators; pure algorithmic engines for K-Means and Prim's MST; and an evaluation engine calculating Hubert and Arabie's Adjusted Rand Index.  
  > The dashboard provides four dedicated sections: an Interactive Playground, an automated Robustness Suite, a Performance Benchmark runner, and an educational Algorithm Explorer.  
  > Everything runs client-side and exports real CSV data and high-resolution PNG charts."*
* **Transition**: *"Parth will describe the synthetic dataset families used in our protocol."*

---

### Slide 8: Synthetic Dataset Families (5:25 – 6:10)
* **Speaker**: Parth Yadav
* **Spoken Script**:
  > *"We evaluated both algorithms across three canonical dataset families, each with 300 baseline inliers:  
  > First, Gaussian Blobs with $K=3$: three compact, spherical normal distributions, representing the ideal convex case.  
  > Second, Two Moons with $K=2$: two interleaving semicircular arcs that require non-linear transitivity to separate.  
  > And third, Concentric Circles with $K=2$: an inner ring inside an outer ring. Here, both clusters share the exact same spatial center at $(0, 0)$, creating an impossible challenge for centroid-based methods.  
  > All coordinates were generated deterministically using fixed random seeds."*
* **Transition**: *"Himanshu will explain our controlled perturbation protocol."*

---

### Slide 9: Experimental Methodology & Robustness Protocol (6:10 – 6:55)
* **Speaker**: Himanshu Gupta
* **Spoken Script**:
  > *"To avoid confounding variables, we strictly separated our perturbations into two independent controlled experiments:  
  > In Experiment A, we varied Gaussian noise $\sigma$ from $0.00$ to $0.20$ while keeping outliers strictly at zero.  
  > In Experiment B, we varied uniform ambient outliers from $0\%$ to $20\%$ while keeping Gaussian noise at zero.  
  > We tested across three seeds—11, 22, and 33—supplying identical coordinates to both algorithms in every paired trial, totaling 144 evaluations.  
  > Crucially, when outliers were present, we evaluated the Adjusted Rand Index strictly over the 300 ground-truth inliers. Uniform outliers do not form a valid natural cluster, so excluding them prevents artificial distortion of clustering quality."*
* **Transition**: *"Parth will present our findings on clean baseline datasets."*

---

### Slide 10: Clean Baseline Results — The Topological Contrast (6:55 – 7:45)
* **Speaker**: Parth Yadav
* **Spoken Script**:
  > *"Looking at our clean baseline results in Table 10, the topological contrast is immediate:  
  > On Gaussian Blobs, both algorithms achieve perfect separation with an ARI of 1.0000.  
  > On Two Moons, MST achieves a perfect ARI of 1.0000, while K-Means fails with an ARI of 0.1941, because its straight Voronoi boundary slices across both crescents.  
  > On Concentric Circles, MST again scores a perfect 1.0000. But K-Means scores -0.0019—effectively zero concordance—because with coinciding centroids, its linear boundary merely splits both rings into semicircular halves.  
  > These clean results confirm theoretical expectations: MST cleanly recovers non-linear manifolds where K-Means is blind."*
* **Transition**: *"However, what happens when noise and outliers enter? Himanshu will present Experiment A."*

---

### Slide 11: Noise Sensitivity Analysis (7:45 – 8:35)
* **Speaker**: Himanshu Gupta
* **Spoken Script**:
  > *"In Experiment A, we introduced Gaussian coordinate noise. As shown in Figure 8.4:  
  > On Gaussian Blobs, K-Means and MST remain completely rock-solid at an ARI of 1.0000 all the way to $\sigma = 0.20$.  
  > On Concentric Circles, MST remains resilient up to $\sigma = 0.10$ with an ARI of 1.0000, but at $\sigma = 0.20$, it collapses to 0.0935—a degradation of 0.9065.  
  > On Two Moons, MST holds at $\sigma = 0.05$, drops to 0.6667 at $\sigma = 0.10$, and collapses to 0.0000 at $\sigma = 0.20$.  
  > The mechanism is clear: when coordinate noise exceeds half the distance between clusters, noisy points create Euclidean 'shortcuts' across the gap, causing the spanning tree to cut within a cluster rather than between clusters."*
* **Transition**: *"Now consider our most critical finding: outlier vulnerability, presented by Parth."*

---

### Slide 12: Outlier Vulnerability & MST Pendant Edge Collapse (8:35 – 9:35)
* **Speaker**: Parth Yadav
* **Spoken Script**:
  > *"This brings us to the central discovery of our research: the catastrophic vulnerability of standard MST clustering to outliers.  
  > Looking at Figure 8.5, on Two Moons, injecting just 5% uniform outliers—only 15 points—causes MST Inlier ARI to plunge instantly from 1.0000 to exactly 0.0000.  
  > Why does this happen? We call it 'Pendant Edge Cut Misallocation.' When outliers land in sparse background areas, the edges connecting them to the spanning tree are very long. Because Zahn's algorithm blindly cuts the $K-1$ longest edges, it cuts those isolated outlier branches!  
  > The algorithm isolates single outlier points into their own clusters, while leaving all 300 true inliers trapped in a single giant component.  
  > In contrast, K-Means on Blobs stays at 1.0000 up to 20% outliers, because centroid averaging balances out uniform pulling forces."*
* **Transition**: *"Himanshu will now review our computational benchmarks."*

---

### Slide 13: Performance Benchmarking & Scalability (9:35 – 10:25)
* **Speaker**: Himanshu Gupta
* **Spoken Script**:
  > *"We benchmarked execution runtimes across sample sizes from 100 to 600 points on Gaussian Blobs with 5 repetitions per size.  
  > In our audit, we carefully distinguished the ratio of means from the ratio of medians:  
  > At $N = 100$, both algorithms execute in under 0.2 milliseconds.  
  > But at $N = 600$, dense Prim's MST scales quadratically to 1.70 milliseconds, while K-Means remains flat at 0.14 milliseconds.  
  > This yields a speedup ratio of 12.14x using means, and 17.00x using medians.  
  > While microsecond runtimes are subject to browser timer quantization, the empirical curves clearly illustrate the theoretical complexity contrast: $O(N^2)$ distance evaluations for Prim versus linear $O(I \cdot K \cdot N)$ passes for Lloyd."*
* **Transition**: *"Parth will summarize our conclusions and practical recommendations."*

---

### Slide 14: Conclusions, Decision Heuristic & Limitations (10:25 – 11:15)
* **Speaker**: Parth Yadav
* **Spoken Script**:
  > *"To summarize our conclusions:  
  > Neither algorithm is universally superior. K-Means excels on convex, spherical clusters and shrugs off noise and uniform outliers, but fails completely on non-convex manifolds.  
  > MST clustering easily untangles clean non-linear manifolds, but collapses catastrophically under ambient outliers.  
  > For practitioners, our decision heuristic is clear:  
  > Use K-Means if clusters are compact and noisy.  
  > Use MST only if data is clean and manifold-structured.  
  > And if data contains BOTH non-convex manifolds AND heavy outliers, neither standard algorithm works—density-based methods like DBSCAN or outlier-trimmed MST variants are required.  
  > We acknowledge our experimental limitations: 3 random seeds, 2D synthetic datasets, and browser timer coarsening."*
* **Transition**: *"Himanshu will conclude our presentation."*

---

### Slide 15: Academic References & Defense Q&A (11:15 – 12:00)
* **Speaker**: Himanshu Gupta
* **Spoken Script**:
  > *"Our work builds on foundational literature: MacQueen and Lloyd for K-Means, Arthur and Vassilvitskii for K-Means++, Prim and Zahn for spanning trees, Hubert and Arabie for the Adjusted Rand Index, and Anil Jain's 50-year clustering retrospective.  
  > Our complete application, reproducible datasets, 64-test automated suite, and evidence reports are publicly hosted on GitHub.  
  > We thank our respected examiners and mentors for their guidance and attention, and we are now delighted to demonstrate the live system and answer your questions."*
