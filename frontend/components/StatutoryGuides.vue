<template>
  <div class="statutory-guides-container">
    <!-- 1. Old vs New Tax Regime Deep Dive -->
    <section id="regimes-guide" class="guide-section">
      <div class="guide-badge"><i class="fa-solid fa-scale-balanced"></i> Statutory Comparison</div>
      <h2 class="guide-title">Old vs. New Tax Regime: What Changed for AY 2026-27?</h2>
      <p class="guide-intro">
        Under Budget 2024 / 2025 modifications to <strong>Section 115BAC</strong>, the New Tax Regime is the default regime with widened tax slabs and an increased standard deduction of <strong>₹75,000</strong> for salaried individuals.
      </p>

      <div class="table-responsive">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Taxable Income Slab</th>
              <th>New Regime (Sec 115BAC) AY 2026-27</th>
              <th>Old Regime (Pre-Existing)</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>Up to ₹3,00,000</td><td class="text-green">0% (Nil)</td><td class="text-green">0% (Nil up to ₹2.5L)</td></tr>
            <tr><td>₹3,00,001 - ₹7,00,000</td><td>5% (Sec 87A rebate gives ₹0 tax up to ₹7L)</td><td>5% (₹2.5L to ₹5.0L)</td></tr>
            <tr><td>₹7,00,001 - ₹10,00,000</td><td>10%</td><td>20% (₹5.0L to ₹10.0L)</td></tr>
            <tr><td>₹10,00,001 - ₹12,00,000</td><td>15%</td><td>30% (Above ₹10.0L)</td></tr>
            <tr><td>₹12,00,001 - ₹15,00,000</td><td>20%</td><td>30%</td></tr>
            <tr><td>Above ₹15,00,000</td><td>30%</td><td>30%</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 2. Section 87A Marginal Relief & Cliff Engine -->
    <section id="marginal-relief-guide" class="guide-section">
      <div class="guide-badge"><i class="fa-solid fa-chart-line"></i> Section 87A Algorithm</div>
      <h2 class="guide-title">Understanding the Zero-Tax Cliff & Section 87A Marginal Relief</h2>
      <p class="guide-intro">
        Under Section 87A of the Income-tax Act, resident individuals with taxable income up to ₹7,00,000 receive a full rebate (up to ₹25,000), making their net tax zero. If your taxable income is slightly above ₹7,00,000 (e.g., ₹7,05,000), the statutory marginal relief ensures your tax does not exceed the income exceeding ₹7 Lakhs.
      </p>

      <div class="formula-box">
        <div class="formula-title">Statutory Marginal Relief Formula (New Regime)</div>
        <code>Tax Payable = Min(Computed Slab Tax, Taxable Income - ₹7,00,000) + 4% Health & Education Cess</code>
      </div>
    </section>

    <!-- 3. Chapter VI-A Deduction Hunter Catalog -->
    <section id="deduction-guide" class="guide-section">
      <div class="guide-badge"><i class="fa-solid fa-crosshairs"></i> Exemption Optimizer</div>
      <h2 class="guide-title">Chapter VI-A Deduction Hunter: Which Exemptions Qualify?</h2>
      <p class="guide-intro">
        If you opt for the <strong>Old Tax Regime</strong>, you can claim extensive deductions under Chapter VI-A to reduce your taxable income.
      </p>

      <div class="deductions-grid">
        <div class="deduction-card">
          <div class="deduction-header">
            <span class="deduction-sec">Section 80C</span>
            <span class="deduction-limit">Max ₹1,50,000</span>
          </div>
          <h4>EPF, PPF, ELSS, Life Insurance & Tuition Fees</h4>
          <p>Covers employee provident fund, Public Provident Fund, Equity Linked Saving Schemes, principal repayment on home loans, and children's tuition fees.</p>
        </div>

        <div class="deduction-card">
          <div class="deduction-header">
            <span class="deduction-sec">Section 80D</span>
            <span class="deduction-limit">Max ₹25K - ₹100K</span>
          </div>
          <h4>Medical & Health Insurance Premiums</h4>
          <p>₹25,000 for self/family, additional ₹25,000 for parents (&lt;60 yrs) or ₹50,000 for senior citizen parents. Includes ₹5,000 preventive health check-up.</p>
        </div>

        <div class="deduction-card">
          <div class="deduction-header">
            <span class="deduction-sec">Section 80CCD(1B)</span>
            <span class="deduction-limit">Max ₹50,000</span>
          </div>
          <h4>National Pension Scheme (NPS) Tier-1</h4>
          <p>Exclusive additional deduction over and above the ₹1.5L limit of Section 80C for voluntary contributions to the Central Government NPS.</p>
        </div>

        <div class="deduction-card">
          <div class="deduction-header">
            <span class="deduction-sec">Section 24(b)</span>
            <span class="deduction-limit">Max ₹2,00,000</span>
          </div>
          <h4>Interest on Housing Loan (Self-Occupied)</h4>
          <p>Deduction on interest paid for loan taken for purchase or construction of a self-occupied residential house property.</p>
        </div>
      </div>
    </section>

    <!-- 4. ITR Form Selector -->
    <section id="itr-selector-guide" class="guide-section">
      <div class="guide-badge"><i class="fa-solid fa-file-signature"></i> Compliance Engine</div>
      <h2 class="guide-title">ITR Form Selector: Which ITR Form Should You File?</h2>
      <p class="guide-intro">
        Filing the incorrect ITR form leads to a defective return notice under Section 139(9). Our deterministic rule engine recommends the appropriate return form:
      </p>

      <div class="itr-forms-grid">
        <div class="itr-form-card">
          <div class="itr-form-badge">ITR-1 (SAHAJ)</div>
          <h3>Salaried Individuals & Single House Property</h3>
          <ul>
            <li><i class="fa-solid fa-check text-green"></i> Total income up to ₹50,000,000 (₹50 Lakhs)</li>
            <li><i class="fa-solid fa-check text-green"></i> Income from Salary, 1 House Property, & Other Sources (Interest)</li>
            <li><i class="fa-solid fa-check text-green"></i> Agricultural income up to ₹5,000</li>
            <li><i class="fa-solid fa-xmark text-payable"></i> Not for Directors or unlisted equity shareholders</li>
          </ul>
        </div>

        <div class="itr-form-card">
          <div class="itr-form-badge">ITR-2</div>
          <h3>Capital Gains & Multiple House Properties</h3>
          <ul>
            <li><i class="fa-solid fa-check text-green"></i> Total income exceeds ₹50 Lakhs</li>
            <li><i class="fa-solid fa-check text-green"></i> Capital gains from mutual funds, stocks, or real estate</li>
            <li><i class="fa-solid fa-check text-green"></i> More than 1 house property or foreign assets/income</li>
            <li><i class="fa-solid fa-check text-green"></i> Holding directorship or unlisted equity shares</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 5. Security & Privacy Architecture -->
    <section id="security-guide" class="guide-section">
      <div class="guide-badge"><i class="fa-solid fa-shield-halved"></i> Bank-Grade Architecture</div>
      <h2 class="guide-title">Zero-Persistence Privacy & Ephemeral In-Memory Processing</h2>
      <p class="guide-intro">
        Your financial privacy is our highest priority. ITR-TaxPilot processes Form 16 documents entirely in ephemeral memory:
      </p>

      <div class="security-grid">
        <div class="security-item">
          <i class="fa-solid fa-memory"></i>
          <h4>Ephemeral RAM Lifecycle</h4>
          <p>Uploaded PDF binaries exist only during parsing and are scrubbed automatically via a 30-minute Redis TTL policy.</p>
        </div>
        <div class="security-item">
          <i class="fa-solid fa-user-secret"></i>
          <h4>Deterministic PII Masking</h4>
          <p>Aadhaar numbers and sensitive metadata are masked in-flight before entering any logging or telemetry pipelines.</p>
        </div>
        <div class="security-item">
          <i class="fa-solid fa-code-compare"></i>
          <h4>100% Deterministic Engine</h4>
          <p>Tax computations are executed by Python & Vue mathematical models—never approximated or generated by LLMs.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.statutory-guides-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.guide-section {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 24px;
  padding: 3rem;
  margin-bottom: 3rem;
  backdrop-filter: blur(16px);
}

.guide-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.25);
  padding: 0.3rem 0.85rem;
  border-radius: 20px;
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--accent-indigo);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}

.guide-title {
  font-family: var(--font-heading);
  font-size: 1.85rem;
  font-weight: 800;
  margin-bottom: 0.85rem;
  line-height: 1.25;
}

.guide-intro {
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.65;
  margin-bottom: 2rem;
  max-width: 900px;
}

.table-responsive {
  overflow-x: auto;
}

.guide-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.guide-table th, .guide-table td {
  padding: 1rem 1.25rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.9rem;
}

.guide-table th {
  font-family: var(--font-heading);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.02);
}

.formula-box {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1.5rem 0;
}

.formula-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.formula-box code {
  font-family: var(--font-mono);
  font-size: 0.95rem;
  color: var(--accent-emerald);
}

.deductions-grid, .itr-forms-grid, .security-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.deduction-card, .itr-form-card, .security-item {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 1.75rem;
  transition: var(--trans-normal);
}

.deduction-card:hover, .itr-form-card:hover, .security-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--accent-indigo);
  transform: translateY(-3px);
}

.deduction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.85rem;
}

.deduction-sec {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--accent-indigo);
  background: rgba(99, 102, 241, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
}

.deduction-limit {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--accent-emerald);
}

.deduction-card h4, .itr-form-card h3 {
  font-family: var(--font-heading);
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.deduction-card p, .security-item p {
  font-size: 0.84rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.itr-form-badge {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--accent-emerald);
  margin-bottom: 0.6rem;
}

.itr-form-card ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-top: 1rem;
}

.itr-form-card li {
  font-size: 0.84rem;
  color: var(--text-secondary);
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
}

.security-item i {
  font-size: 1.8rem;
  color: var(--accent-indigo);
  margin-bottom: 1rem;
}

.security-item h4 {
  font-family: var(--font-heading);
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}
</style>
