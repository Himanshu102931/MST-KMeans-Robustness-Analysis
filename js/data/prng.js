/**
 * MST vs K-Means Robustness Analysis
 * Module: Seeded Pseudo-Random Number Generator (PRNG) & Distributions
 * Pure Vanilla JavaScript - No dependencies
 */

(function (window) {
  'use strict';

  window.MSTKMeans = window.MSTKMeans || {};

  /**
   * Mulberry32 32-bit PRNG
   * Fast, reproducible, deterministic random float in [0, 1)
   * @param {number} seed 32-bit integer seed
   * @returns {function(): number}
   */
  function createPRNG(seed) {
    let s = (Math.floor(seed) >>> 0) || 1337;
    return function next() {
      s = (s + 0x6d2b79f5) >>> 0;
      let t = Math.imul(s ^ (s >>> 15), 1 | s);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /**
   * Box-Muller transform for standard normal distribution N(mean, std^2)
   * @param {function(): number} rng Uniform [0, 1) generator
   * @param {number} mean Distribution mean (default 0)
   * @param {number} std Distribution standard deviation (default 1)
   * @returns {number}
   */
  function sampleGaussian(rng, mean = 0, std = 1) {
    let u1 = rng();
    let u2 = rng();
    // Guard against log(0)
    while (u1 <= 1e-15) {
      u1 = rng();
    }
    const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
    return mean + z0 * std;
  }

  /**
   * Sample uniform float in [min, max]
   * @param {function(): number} rng
   * @param {number} min
   * @param {number} max
   * @returns {number}
   */
  function sampleUniform(rng, min = 0, max = 1) {
    return min + rng() * (max - min);
  }

  window.MSTKMeans.PRNG = {
    createPRNG,
    sampleGaussian,
    sampleUniform
  };
})(window);
