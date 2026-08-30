<template>
  <section v-if="isUploading" class="pipeline-section">
    <div class="pipeline-card">
      <div class="pipeline-header">
        <div class="spinner-wrapper">
          <i class="fa-solid fa-circle-notch fa-spin"></i>
        </div>
        <div>
          <h2 class="pipeline-title">Extracting Form 16 & Verifying Slabs</h2>
          <p class="pipeline-desc">Executing security scans, PyMuPDF table parsing, and Section 115BAC statutory rule engine...</p>
        </div>
      </div>

      <div class="pipeline-steps">
        <div
          class="step-item"
          :class="{
            active: currentStep === 1,
            completed: currentStep > 1,
          }"
        >
          <div class="step-icon"><i class="fa-solid fa-shield-virus"></i></div>
          <div class="step-info">
            <span class="step-name">1. Binary & Sandbox Inspection</span>
            <span class="step-detail">ClamAV & PDF header integrity check</span>
          </div>
          <div class="step-status">
            <span v-if="currentStep > 1"><i class="fa-solid fa-check text-green"></i> Done</span>
            <span v-else-if="currentStep === 1"><i class="fa-solid fa-circle-notch fa-spin"></i></span>
            <span v-else>Queued</span>
          </div>
        </div>

        <div
          class="step-item"
          :class="{
            active: currentStep === 2,
            completed: currentStep > 2,
          }"
        >
          <div class="step-icon"><i class="fa-solid fa-table"></i></div>
          <div class="step-info">
            <span class="step-name">2. PyMuPDF Extraction & OCR</span>
            <span class="step-detail">Parsing Part A & Part B financial tables</span>
          </div>
          <div class="step-status">
            <span v-if="currentStep > 2"><i class="fa-solid fa-check text-green"></i> Done</span>
            <span v-else-if="currentStep === 2"><i class="fa-solid fa-circle-notch fa-spin"></i></span>
            <span v-else>Queued</span>
          </div>
        </div>

        <div
          class="step-item"
          :class="{
            active: currentStep === 3,
            completed: currentStep > 3,
          }"
        >
          <div class="step-icon"><i class="fa-solid fa-brain"></i></div>
          <div class="step-info">
            <span class="step-name">3. AI Schema Normalization</span>
            <span class="step-detail">Extracting gross income, PAN, TDS, and deductions</span>
          </div>
          <div class="step-status">
            <span v-if="currentStep > 3"><i class="fa-solid fa-check text-green"></i> Done</span>
            <span v-else-if="currentStep === 3"><i class="fa-solid fa-circle-notch fa-spin"></i></span>
            <span v-else>Queued</span>
          </div>
        </div>

        <div
          class="step-item"
          :class="{
            active: currentStep === 4,
            completed: currentStep > 4,
          }"
        >
          <div class="step-icon"><i class="fa-solid fa-calculator"></i></div>
          <div class="step-info">
            <span class="step-name">4. Deterministic Tax Engine</span>
            <span class="step-detail">AY 2026-27 statutory slabs, 87A rebate & cess</span>
          </div>
          <div class="step-status">
            <span v-if="currentStep > 4"><i class="fa-solid fa-check text-green"></i> Done</span>
            <span v-else-if="currentStep === 4"><i class="fa-solid fa-circle-notch fa-spin"></i></span>
            <span v-else>Queued</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { isUploading, currentStep } = useDocumentUpload()
</script>

<style scoped>
.pipeline-section {
  max-width: 780px;
  margin: 2rem auto;
  padding: 0 1.5rem;
}

.pipeline-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(16px);
}

.pipeline-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.spinner-wrapper {
  font-size: 2.2rem;
  color: var(--accent-indigo);
}

.pipeline-title {
  font-family: var(--font-heading);
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.pipeline-desc {
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.pipeline-steps {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: var(--trans-normal);
}

.step-item.active {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.4);
}

.step-item.completed {
  background: rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.3);
}

.step-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.step-item.active .step-icon {
  background: var(--accent-indigo);
  color: white;
}

.step-item.completed .step-icon {
  background: var(--accent-emerald);
  color: white;
}

.step-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.step-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.step-detail {
  font-size: 0.76rem;
  color: var(--text-muted);
}

.step-status {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-muted);
}
</style>
