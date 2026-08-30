<template>
  <div class="regime-grid">
    <!-- New Tax Regime Card -->
    <div
      class="regime-card"
      :class="{
        'is-winner': isNewRegimeRecommended,
      }"
    >
      <div v-if="isNewRegimeRecommended" class="winner-badge">
        <i class="fa-solid fa-crown"></i>
        <span>Recommended Regime</span>
      </div>

      <div class="regime-header">
        <span class="regime-pill pill-new">Default Regime</span>
        <h3 class="regime-title">New Tax Regime</h3>
        <span class="regime-ref">Section 115BAC (AY 2026-27)</span>
      </div>

      <div class="tax-amount-box">
        <span class="amount-label">Total Tax Payable</span>
        <div class="amount-value">{{ formatINR(newRegimeResult.totalTax) }}</div>
        <span class="effective-rate">Effective Rate: {{ newRegimeResult.effectiveRate.toFixed(1) }}%</span>
      </div>

      <div class="breakdown-list">
        <div class="breakdown-item">
          <span>Gross Total Income</span>
          <span>{{ formatINR(newRegimeResult.grossIncome) }}</span>
        </div>
        <div class="breakdown-item">
          <span>Standard Deduction (Sec 16(ia))</span>
          <span class="text-green">-{{ formatINR(newRegimeResult.stdDeduction) }}</span>
        </div>
        <div class="breakdown-item highlight">
          <span>Total Taxable Income</span>
          <span>{{ formatINR(newRegimeResult.taxableIncome) }}</span>
        </div>
        <div class="breakdown-item">
          <span>Computed Base Tax</span>
          <span>{{ formatINR(newRegimeResult.baseTax) }}</span>
        </div>
        <div v-if="newRegimeResult.rebate87a > 0" class="breakdown-item">
          <span>Section 87A Rebate</span>
          <span class="text-green">-{{ formatINR(newRegimeResult.rebate87a) }}</span>
        </div>
        <div class="breakdown-item">
          <span>Health & Education Cess (4%)</span>
          <span>{{ formatINR(newRegimeResult.cess) }}</span>
        </div>
        <div class="breakdown-item tds-row">
          <span>Total TDS Deducted</span>
          <span>{{ formatINR(tdsDeducted) }}</span>
        </div>
        <div class="breakdown-item final-row">
          <span>{{ newRegimeResult.netPayableOrRefund <= 0 ? 'Net Refund Due' : 'Balance Tax Payable' }}</span>
          <span :class="newRegimeResult.netPayableOrRefund <= 0 ? 'text-green' : 'text-payable'">
            {{ formatINR(Math.abs(newRegimeResult.netPayableOrRefund)) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Old Tax Regime Card -->
    <div
      class="regime-card"
      :class="{
        'is-winner': !isNewRegimeRecommended,
      }"
    >
      <div v-if="!isNewRegimeRecommended" class="winner-badge">
        <i class="fa-solid fa-crown"></i>
        <span>Recommended Regime</span>
      </div>

      <div class="regime-header">
        <span class="regime-pill pill-old">Optional Opt-In</span>
        <h3 class="regime-title">Old Tax Regime</h3>
        <span class="regime-ref">With Chapter VI-A Exemptions</span>
      </div>

      <div class="tax-amount-box">
        <span class="amount-label">Total Tax Payable</span>
        <div class="amount-value">{{ formatINR(oldRegimeResult.totalTax) }}</div>
        <span class="effective-rate">Effective Rate: {{ oldRegimeResult.effectiveRate.toFixed(1) }}%</span>
      </div>

      <div class="breakdown-list">
        <div class="breakdown-item">
          <span>Gross Total Income</span>
          <span>{{ formatINR(oldRegimeResult.grossIncome) }}</span>
        </div>
        <div class="breakdown-item">
          <span>Standard Deduction (Sec 16(ia))</span>
          <span class="text-green">-{{ formatINR(oldRegimeResult.stdDeduction) }}</span>
        </div>
        <div class="breakdown-item">
          <span>Chapter VI-A Deductions</span>
          <span class="text-green">-{{ formatINR(oldRegimeResult.totalDeductions || 0) }}</span>
        </div>
        <div class="breakdown-item highlight">
          <span>Total Taxable Income</span>
          <span>{{ formatINR(oldRegimeResult.taxableIncome) }}</span>
        </div>
        <div class="breakdown-item">
          <span>Computed Base Tax</span>
          <span>{{ formatINR(oldRegimeResult.baseTax) }}</span>
        </div>
        <div v-if="oldRegimeResult.rebate87a > 0" class="breakdown-item">
          <span>Section 87A Rebate</span>
          <span class="text-green">-{{ formatINR(oldRegimeResult.rebate87a) }}</span>
        </div>
        <div class="breakdown-item">
          <span>Health & Education Cess (4%)</span>
          <span>{{ formatINR(oldRegimeResult.cess) }}</span>
        </div>
        <div class="breakdown-item tds-row">
          <span>Total TDS Deducted</span>
          <span>{{ formatINR(tdsDeducted) }}</span>
        </div>
        <div class="breakdown-item final-row">
          <span>{{ oldRegimeResult.netPayableOrRefund <= 0 ? 'Net Refund Due' : 'Balance Tax Payable' }}</span>
          <span :class="oldRegimeResult.netPayableOrRefund <= 0 ? 'text-green' : 'text-payable'">
            {{ formatINR(Math.abs(oldRegimeResult.netPayableOrRefund)) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const {
  tdsDeducted,
  newRegimeResult,
  oldRegimeResult,
  isNewRegimeRecommended,
  formatINR,
} = useTaxCalculator()
</script>

<style scoped>
.regime-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.regime-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 2.25rem;
  position: relative;
  transition: var(--trans-normal);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.regime-card.is-winner {
  border-color: var(--accent-emerald);
  box-shadow: var(--shadow-emerald-glow);
}

.winner-badge {
  position: absolute;
  top: -14px;
  right: 24px;
  background: var(--accent-emerald);
  color: #042F2E;
  padding: 0.3rem 0.85rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.regime-header {
  margin-bottom: 1.5rem;
}

.regime-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: inline-block;
  margin-bottom: 0.5rem;
}

.pill-new {
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-emerald);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.pill-old {
  background: rgba(99, 102, 241, 0.15);
  color: #A5B4FC;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.regime-title {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.2rem;
}

.regime-ref {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.tax-amount-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 14px;
  padding: 1.5rem;
  text-align: center;
  margin-bottom: 1.5rem;
}

.amount-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  display: block;
  margin-bottom: 0.35rem;
}

.amount-value {
  font-family: var(--font-heading);
  font-size: 2.4rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
}

.effective-rate {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.35rem;
  display: block;
}

.breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.breakdown-item span:last-child {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--text-primary);
}

.breakdown-item.highlight {
  padding: 0.6rem 0;
  border-top: 1px dashed var(--border-subtle);
  border-bottom: 1px dashed var(--border-subtle);
  font-weight: 600;
}

.breakdown-item.highlight span:last-child {
  color: #A5B4FC;
}

.breakdown-item.tds-row {
  border-top: 1px solid var(--border-subtle);
  padding-top: 0.75rem;
}

.breakdown-item.final-row {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
}
</style>
