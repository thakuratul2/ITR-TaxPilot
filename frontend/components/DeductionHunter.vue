<template>
  <div class="simulator-card">
    <div class="simulator-header">
      <div>
        <h3 class="simulator-title"><i class="fa-solid fa-sliders text-green"></i> Deduction Hunter & What-If Simulator</h3>
        <p class="simulator-subtitle">Move sliders to see in real-time how additional exemptions impact your Old vs New Regime recommendation.</p>
      </div>
      <span class="ay-pill">Old Regime Optimizations</span>
    </div>

    <div class="sliders-grid">
      <!-- 80C -->
      <div class="slider-group">
        <div class="slider-label-row">
          <label>Section 80C (EPF, PPF, ELSS, Life Insurance)</label>
          <span class="slider-val">{{ formatINR(deduction80C) }} / ₹1.5L</span>
        </div>
        <input
          v-model.number="deduction80C"
          type="range"
          min="0"
          max="150000"
          step="5000"
          class="tax-range-slider"
        />
      </div>

      <!-- 80D -->
      <div class="slider-group">
        <div class="slider-label-row">
          <label>Section 80D (Health Insurance: Self & Parents)</label>
          <span class="slider-val">{{ formatINR(deduction80D) }} / ₹1.0L</span>
        </div>
        <input
          v-model.number="deduction80D"
          type="range"
          min="0"
          max="100000"
          step="2500"
          class="tax-range-slider"
        />
      </div>

      <!-- 80CCD(1B) NPS -->
      <div class="slider-group">
        <div class="slider-label-row">
          <label>Section 80CCD(1B) (National Pension Scheme - Tier 1)</label>
          <span class="slider-val">{{ formatINR(deductionNPS) }} / ₹50K</span>
        </div>
        <input
          v-model.number="deductionNPS"
          type="range"
          min="0"
          max="50000"
          step="5000"
          class="tax-range-slider"
        />
      </div>

      <!-- 24(b) Home Loan -->
      <div class="slider-group">
        <div class="slider-label-row">
          <label>Section 24(b) (Home Loan Interest - SOP)</label>
          <span class="slider-val">{{ formatINR(deductionHomeLoan) }} / ₹2.0L</span>
        </div>
        <input
          v-model.number="deductionHomeLoan"
          type="range"
          min="0"
          max="200000"
          step="10000"
          class="tax-range-slider"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const {
  deduction80C,
  deduction80D,
  deductionNPS,
  deductionHomeLoan,
  formatINR,
} = useTaxCalculator()
</script>

<style scoped>
.simulator-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 2.25rem;
  margin-bottom: 3rem;
  backdrop-filter: blur(16px);
}

.simulator-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.simulator-title {
  font-family: var(--font-heading);
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.simulator-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.sliders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.75rem;
}

.slider-group {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.slider-label-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.slider-val {
  font-family: var(--font-mono);
  color: var(--accent-indigo);
}

.tax-range-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.1);
  outline: none;
}

.tax-range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent-indigo);
  cursor: pointer;
  box-shadow: 0 0 10px var(--accent-indigo);
  transition: transform var(--trans-fast);
}

.tax-range-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}
</style>
