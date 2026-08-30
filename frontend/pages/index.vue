<template>
  <div>
    <!-- Hero / Upload Section -->
    <Form16Uploader v-if="!isUploading && !isResultsVisible" />

    <!-- Live Pipeline Stepper -->
    <PipelineStepper />

    <!-- Results Section (Revealed upon extraction completion & auth) -->
    <section v-if="isResultsVisible" id="results-section" class="results-section">
      <div class="results-container">
        <!-- Results Header Banner -->
        <div class="results-header-banner">
          <div class="results-summary-info">
            <span class="ay-pill">
              <i class="fa-solid fa-file-check text-green"></i> Form 16 Analyzed (AY {{ assessmentYear }})
            </span>
            <h2 class="results-heading">
              <span v-if="newRegimeResult.totalTax === 0 && oldRegimeResult.totalTax === 0">
                🎉 Zero Tax Liability under Section 87A Rebate!
              </span>
              <span v-else>
                {{
                  isNewRegimeRecommended
                    ? 'New Tax Regime saves you more tax!'
                    : 'Old Tax Regime saves you more tax!'
                }}
              </span>
            </h2>
            <p class="results-subheading">
              <span v-if="newRegimeResult.totalTax === 0 && oldRegimeResult.totalTax === 0">
                Based on your extracted income of <strong>{{ formatINR(grossSalary) }}</strong>, your net tax is <strong>₹0</strong> under both regimes.
              </span>
              <span v-else>
                Based on your gross salary of <strong>{{ formatINR(grossSalary) }}</strong>, you save
                <strong class="text-green">{{ formatINR(savingsAmount) }}</strong> by opting for the
                <strong>{{ isNewRegimeRecommended ? 'New Tax Regime' : 'Old Tax Regime' }}</strong>.
              </span>
            </p>
          </div>

          <div class="results-actions">
            <button class="btn btn-outline btn-sm" @click="handlePrint">
              <i class="fa-solid fa-download"></i> Export PDF
            </button>
            <button class="btn btn-primary btn-sm" @click="resetToUpload">
              <i class="fa-solid fa-rotate-left"></i> Analyze Another
            </button>
          </div>
        </div>

        <!-- Winning Regime Comparison Cards -->
        <RegimeComparison />

        <!-- Reactive Deduction Hunter Simulator -->
        <DeductionHunter />
      </div>
    </section>

    <!-- Comprehensive Statutory Guides (Old vs New, 87A, Deductions, ITR Forms, Security) -->
    <StatutoryGuides />

    <!-- FAQ Accordion -->
    <FAQAccordion />
  </div>
</template>

<script setup lang="ts">
const { isUploading, isResultsVisible } = useDocumentUpload()
const {
  grossSalary,
  assessmentYear,
  isNewRegimeRecommended,
  savingsAmount,
  newRegimeResult,
  oldRegimeResult,
  formatINR,
} = useTaxCalculator()

const resetToUpload = () => {
  isResultsVisible.value = false
  if (import.meta.client) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const handlePrint = () => {
  if (import.meta.client) {
    window.print()
  }
}
</script>

<style scoped>
.results-section {
  padding: 3rem 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.results-container {
  display: flex;
  flex-direction: column;
}

.results-header-banner {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 2rem 2.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  flex-wrap: wrap;
  gap: 1.5rem;
  backdrop-filter: blur(16px);
}

.results-heading {
  font-family: var(--font-heading);
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0.5rem 0 0.25rem;
}

.results-subheading {
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.results-actions {
  display: flex;
  gap: 0.75rem;
}
</style>
