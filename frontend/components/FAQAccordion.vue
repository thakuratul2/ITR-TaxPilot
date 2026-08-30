<template>
  <section id="faq-section" class="faq-section">
    <div class="faq-container">
      <div class="faq-header">
        <div class="guide-badge"><i class="fa-solid fa-circle-question"></i> Help & Clarity</div>
        <h2 class="guide-title">Frequently Asked Questions</h2>
        <p class="guide-intro">Everything you need to know about Form 16 extraction, New vs Old Regime selection, and statutory accuracy.</p>
      </div>

      <div class="faq-accordion">
        <div
          v-for="(item, idx) in faqItems"
          :key="idx"
          class="faq-item"
          :class="{ open: openIdx === idx }"
          @click="toggle(idx)"
        >
          <button class="faq-question">
            <span>{{ item.q }}</span>
            <i class="fa-solid fa-chevron-down faq-arrow"></i>
          </button>
          <div v-show="openIdx === idx" class="faq-answer">
            <p>{{ item.a }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const openIdx = ref<number | null>(0)

const toggle = (idx: number) => {
  openIdx.value = openIdx.value === idx ? null : idx
}

const faqItems = [
  {
    q: 'What is the standard deduction for AY 2026-27 under the New Tax Regime?',
    a: 'For AY 2026-27 (Financial Year 2025-26), the standard deduction under Section 16(ia) for salaried individuals and pensioners has been increased from ₹50,000 to ₹75,000 in the New Tax Regime (Section 115BAC). In the Old Tax Regime, it remains ₹50,000.',
  },
  {
    q: 'How does Section 87A Marginal Relief work if my income is slightly above ₹7 Lakhs?',
    a: 'Under Section 115BAC, if your taxable income is up to ₹7,00,000, your tax is ₹0 due to the Section 87A rebate. If your income slightly exceeds ₹7 Lakhs (e.g. ₹7,05,000), marginal relief guarantees that your tax payable cannot exceed the amount by which your income exceeds ₹7 Lakhs (i.e. maximum ₹5,000 + 4% cess).',
  },
  {
    q: 'Is my Form 16 PDF permanently stored on your server?',
    a: 'No. ITR-TaxPilot enforces an ephemeral in-memory privacy architecture. Uploaded PDF files are processed purely in memory, parsed via PyMuPDF, and scrubbed automatically. Your PAN and sensitive identifiers are masked client-side.',
  },
  {
    q: 'Can I switch between the Old and New Tax Regime every year?',
    a: 'Salaried taxpayers with no business or professional income (ITR-1 and ITR-2 filers) can choose between the Old and New Regime every assessment year at the time of filing their return. Taxpayers with business income (ITR-3 / ITR-4) can opt out of the New Regime only once by filing Form 10-IEA.',
  },
  {
    q: 'Why does ITR-TaxPilot produce 100% deterministic tax figures without LLM hallucination?',
    a: 'We use Large Language Models solely for structural JSON schema normalization of non-standard PDF formats. All financial math, slab lookups, marginal relief algorithms, and surcharge rates are strictly computed by deterministic Python and TypeScript engines.',
  },
]
</script>

<style scoped>
.faq-section {
  max-width: 1000px;
  margin: 0 auto 5rem;
  padding: 0 1.5rem;
}

.faq-header {
  text-align: center;
  margin-bottom: 2.5rem;
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
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.guide-intro {
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.faq-accordion {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.faq-item {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  overflow: hidden;
  transition: var(--trans-normal);
}

.faq-item.open {
  border-color: var(--accent-indigo);
}

.faq-question {
  width: 100%;
  padding: 1.25rem 1.5rem;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: left;
  cursor: pointer;
  gap: 1rem;
}

.faq-arrow {
  font-size: 0.85rem;
  color: var(--text-muted);
  transition: transform var(--trans-fast);
}

.faq-item.open .faq-arrow {
  transform: rotate(180deg);
  color: var(--accent-indigo);
}

.faq-answer {
  padding: 0 1.5rem 1.25rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.faq-answer p {
  padding-top: 0.75rem;
}
</style>
