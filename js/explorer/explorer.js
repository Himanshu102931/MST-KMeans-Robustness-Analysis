/**
 * MST vs K-Means Robustness Analysis
 * Module: Interactive Algorithm Explorer Controller
 * Manages playback, state progression, and step-by-step rendering for K-Means and MST
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};
  const { Datasets, KMeans, MST, ExplorerRenderer } = window.MSTKMeans;

  class AlgorithmExplorerController {
    constructor() {
      this.algorithm = 'kmeans'; // 'kmeans' or 'mst'
      this.datasetType = 'blobs';
      this.sampleSize = 20; // 10-40 for K-Means, 8-25 for MST
      this.k = 3;
      this.seed = 42;
      this.points = [];
      this.trace = null;
      this.currentStep = 0;
      this.isPlaying = false;
      this.timer = null;
      this.speed = 1.0; // 0.5x, 1x, 2x

      this.dom = {};
    }

    /**
     * Bind DOM elements for explorer controls
     */
    bindDOM(domElements) {
      this.dom = domElements;
      this.initEvents();
      this.resetDataAndTrace();
    }

    initEvents() {
      // Algorithm Switcher Tabs
      if (this.dom.btnTabKMeans) {
        this.dom.btnTabKMeans.addEventListener('click', () => this.switchAlgorithm('kmeans'));
      }
      if (this.dom.btnTabMST) {
        this.dom.btnTabMST.addEventListener('click', () => this.switchAlgorithm('mst'));
      }

      // Dataset & Parameter controls
      if (this.dom.selectDataset) {
        this.dom.selectDataset.addEventListener('change', (e) => {
          this.datasetType = e.target.value;
          this.resetDataAndTrace();
        });
      }
      if (this.dom.inputSampleSize) {
        this.dom.inputSampleSize.addEventListener('change', (e) => {
          this.sampleSize = parseInt(e.target.value, 10);
          this.resetDataAndTrace();
        });
      }
      if (this.dom.inputK) {
        this.dom.inputK.addEventListener('change', (e) => {
          this.k = parseInt(e.target.value, 10);
          this.recomputeTrace();
        });
      }
      if (this.dom.inputSeed) {
        this.dom.inputSeed.addEventListener('change', (e) => {
          this.seed = parseInt(e.target.value, 10) || 42;
          this.resetDataAndTrace();
        });
      }
      if (this.dom.btnRegenerate) {
        this.dom.btnRegenerate.addEventListener('click', () => {
          this.seed = Math.floor(Math.random() * 10000);
          if (this.dom.inputSeed) this.dom.inputSeed.value = this.seed;
          this.resetDataAndTrace();
        });
      }

      // Playback Controls
      if (this.dom.btnPrev) {
        this.dom.btnPrev.addEventListener('click', () => this.prevStep());
      }
      if (this.dom.btnNext) {
        this.dom.btnNext.addEventListener('click', () => this.nextStep());
      }
      if (this.dom.btnPlayPause) {
        this.dom.btnPlayPause.addEventListener('click', () => this.togglePlay());
      }
      if (this.dom.btnRestart) {
        this.dom.btnRestart.addEventListener('click', () => this.restart());
      }
      if (this.dom.selectSpeed) {
        this.dom.selectSpeed.addEventListener('change', (e) => {
          this.speed = parseFloat(e.target.value) || 1.0;
          if (this.isPlaying) {
            this.pause();
            this.play();
          }
        });
      }
      if (this.dom.stepSlider) {
        this.dom.stepSlider.addEventListener('input', (e) => {
          this.pause();
          this.goToStep(parseInt(e.target.value, 10));
        });
      }
    }

    /**
     * Switch between K-Means and MST explorer views
     */
    switchAlgorithm(algo) {
      if (this.algorithm === algo) return;
      this.pause();
      this.algorithm = algo;

      if (this.dom.btnTabKMeans && this.dom.btnTabMST) {
        if (algo === 'kmeans') {
          this.dom.btnTabKMeans.classList.add('active');
          this.dom.btnTabMST.classList.remove('active');
          if (this.sampleSize < 12) this.sampleSize = 20;
        } else {
          this.dom.btnTabMST.classList.add('active');
          this.dom.btnTabKMeans.classList.remove('active');
          if (this.sampleSize > 25) this.sampleSize = 15;
        }
        if (this.dom.inputSampleSize) this.dom.inputSampleSize.value = this.sampleSize;
      }

      this.resetDataAndTrace();
    }

    /**
     * Generate small reproducible dataset
     */
    generateData() {
      const actualN = Math.max(8, Math.min(this.sampleSize, 40));
      const dataset = Datasets.generateDataset(this.datasetType, {
        n: actualN,
        k: this.k,
        noise: 0.12,
        outlierFraction: 0.0,
        seed: this.seed
      });
      // Extract 2D point array
      this.points = dataset.points.map(p => ({ x: p.x, y: p.y }));
    }

    /**
     * Generate computational trace for the active algorithm
     */
    recomputeTrace() {
      this.pause();
      if (this.algorithm === 'kmeans') {
        this.trace = KMeans.generateKMeansTrace(this.points, this.k, {
          seed: this.seed,
          maxIterations: 30,
          tolerance: 1e-4,
          initMethod: 'kmeans++'
        });
      } else {
        this.trace = MST.generateMSTTrace(this.points, this.k);
      }

      this.currentStep = 0;
      this.updateUI();
    }

    /**
     * Regenerate data and recompute trace from step 0
     */
    resetDataAndTrace() {
      this.generateData();
      this.recomputeTrace();
    }

    goToStep(index) {
      if (!this.trace || !this.trace.steps.length) return;
      const maxIdx = this.trace.steps.length - 1;
      this.currentStep = Math.max(0, Math.min(index, maxIdx));
      this.updateUI();
    }

    nextStep() {
      if (!this.trace || !this.trace.steps.length) return;
      if (this.currentStep < this.trace.steps.length - 1) {
        this.currentStep++;
        this.updateUI();
      } else {
        this.pause();
      }
    }

    prevStep() {
      if (!this.trace || !this.trace.steps.length) return;
      if (this.currentStep > 0) {
        this.currentStep--;
        this.updateUI();
      }
    }

    restart() {
      this.pause();
      this.goToStep(0);
    }

    togglePlay() {
      if (this.isPlaying) {
        this.pause();
      } else {
        this.play();
      }
    }

    play() {
      if (this.isPlaying) return;
      if (!this.trace || !this.trace.steps.length) return;

      // If already at end, restart from step 0
      if (this.currentStep >= this.trace.steps.length - 1) {
        this.currentStep = 0;
      }

      this.isPlaying = true;
      if (this.dom.btnPlayPause) {
        this.dom.btnPlayPause.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
          Pause
        `;
        this.dom.btnPlayPause.classList.add('btn-warning');
        this.dom.btnPlayPause.classList.remove('btn-success');
      }

      const delayMs = Math.max(250, Math.floor(1000 / this.speed));
      this.timer = setInterval(() => {
        if (this.currentStep < this.trace.steps.length - 1) {
          this.nextStep();
        } else {
          this.pause();
        }
      }, delayMs);
    }

    pause() {
      this.isPlaying = false;
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
      if (this.dom.btnPlayPause) {
        this.dom.btnPlayPause.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          Play
        `;
        this.dom.btnPlayPause.classList.remove('btn-warning');
        this.dom.btnPlayPause.classList.add('btn-success');
      }
    }

    /**
     * Update UI readouts and trigger Canvas rendering
     */
    updateUI() {
      if (!this.trace || !this.trace.steps.length) return;
      const step = this.trace.steps[this.currentStep];
      const totalSteps = this.trace.steps.length;

      // 1. Slider & Counter
      if (this.dom.stepSlider) {
        this.dom.stepSlider.min = 0;
        this.dom.stepSlider.max = totalSteps - 1;
        this.dom.stepSlider.value = this.currentStep;
      }
      if (this.dom.stepCounter) {
        this.dom.stepCounter.textContent = `Step ${this.currentStep + 1} of ${totalSteps}`;
      }

      // 2. Button states
      if (this.dom.btnPrev) this.dom.btnPrev.disabled = this.currentStep === 0;
      if (this.dom.btnNext) this.dom.btnNext.disabled = this.currentStep === totalSteps - 1;

      // 3. Explanation text
      if (this.dom.explanationBox) {
        this.dom.explanationBox.textContent = step.explanation || '';
      }

      // 4. Metric Readouts
      if (this.algorithm === 'kmeans') {
        if (this.dom.lblMetric1Name) this.dom.lblMetric1Name.textContent = 'Iteration:';
        if (this.dom.lblMetric1Val) this.dom.lblMetric1Val.textContent = step.iteration !== undefined ? step.iteration : 0;

        if (this.dom.lblMetric2Name) this.dom.lblMetric2Name.textContent = 'Inertia (WCSS):';
        if (this.dom.lblMetric2Val) this.dom.lblMetric2Val.textContent = step.inertia !== null && step.inertia !== undefined ? step.inertia.toFixed(3) : '-';

        if (this.dom.lblMetric3Name) this.dom.lblMetric3Name.textContent = 'Centroid Shift:';
        if (this.dom.lblMetric3Val) this.dom.lblMetric3Val.textContent = step.maxShift !== null && step.maxShift !== undefined ? step.maxShift.toFixed(5) : '-';

        if (this.dom.lblMetric4Name) this.dom.lblMetric4Name.textContent = 'Convergence:';
        if (this.dom.lblMetric4Val) {
          this.dom.lblMetric4Val.textContent = step.converged ? 'Converged ✓' : 'In Progress...';
          this.dom.lblMetric4Val.style.color = step.converged ? '#10b981' : '#f59e0b';
        }
      } else {
        if (this.dom.lblMetric1Name) this.dom.lblMetric1Name.textContent = 'MST Phase:';
        if (this.dom.lblMetric1Val) {
          if (step.type === 'prim_init' || step.type === 'prim_step') this.dom.lblMetric1Val.textContent = `Prim's Tree (${step.treeEdges.length}/${this.points.length - 1} edges)`;
          else if (step.type === 'mst_complete') this.dom.lblMetric1Val.textContent = 'Tree Complete';
          else if (step.type === 'cut_selection') this.dom.lblMetric1Val.textContent = `Selecting ${this.k - 1} Longest`;
          else if (step.type === 'cut_applied') this.dom.lblMetric1Val.textContent = `Clustered (${step.k} Components)`;
        }

        if (this.dom.lblMetric2Name) this.dom.lblMetric2Name.textContent = 'Total Tree Weight:';
        if (this.dom.lblMetric2Val) this.dom.lblMetric2Val.textContent = step.totalWeight ? step.totalWeight.toFixed(3) : '0.000';

        if (this.dom.lblMetric3Name) this.dom.lblMetric3Name.textContent = 'Cut Edges:';
        if (this.dom.lblMetric3Val) this.dom.lblMetric3Val.textContent = `${step.cutEdges ? step.cutEdges.length : 0} of ${Math.max(0, this.k - 1)}`;

        if (this.dom.lblMetric4Name) this.dom.lblMetric4Name.textContent = 'Status:';
        if (this.dom.lblMetric4Val) {
          const isDone = step.type === 'cut_applied';
          this.dom.lblMetric4Val.textContent = isDone ? 'Finished ✓' : 'Constructing...';
          this.dom.lblMetric4Val.style.color = isDone ? '#10b981' : '#38bdf8';
        }
      }

      // 5. Render Canvas
      if (this.dom.canvas) {
        if (this.algorithm === 'kmeans') {
          ExplorerRenderer.renderKMeansTraceStep(this.dom.canvas, this.points, step);
        } else {
          ExplorerRenderer.renderMSTTraceStep(this.dom.canvas, this.points, step);
        }
      }
    }
  }

  window.MSTKMeans.Explorer = {
    AlgorithmExplorerController
  };
})(window);
