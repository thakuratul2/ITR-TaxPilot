<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-brand">
        <div class="footer-logo">
          <i class="fa-solid fa-file-invoice-dollar"></i>
          <span>ITR-TaxPilot</span>
        </div>
        <p class="footer-desc">
          High-performance, privacy-first Indian Income Tax optimizer for AY 2026-27 (FY 2025-26).
          100% deterministic tax computation engine powered by FastAPI & Nuxt 3.
        </p>
      </div>

      <div class="footer-links-group">
        <h4>Statutory References</h4>
        <ul>
          <li><a href="#regimes-guide">Section 115BAC Slabs</a></li>
          <li><a href="#marginal-relief-guide">Section 87A Marginal Relief</a></li>
          <li><a href="#deduction-guide">Chapter VI-A Catalog</a></li>
          <li><a href="#itr-selector-guide">ITR-1 vs ITR-2 Decision Tree</a></li>
        </ul>
      </div>

      <div class="footer-links-group">
        <h4>Platform & Guides</h4>
        <ul>
          <li><a href="#faq-section">Frequently Asked Questions</a></li>
          <li><a href="#security-guide">Bank-Grade Privacy Model</a></li>
          <li><a href="https://github.com/thakuratul2/ITR-TaxPilot" target="_blank">Open Source Repository</a></li>
          <li><a href="https://github.com/thakuratul2" target="_blank">Author Profile</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-bottom">
      <div class="footer-bottom-container">
        <span>© 2026 <strong>ITR-TaxPilot</strong> · Built with pride by <a href="https://github.com/thakuratul2" target="_blank" class="footer-author-link">Atul Pratap Singh</a>.</span>
        <a href="https://github.com/thakuratul2/ITR-TaxPilot" target="_blank" class="footer-repo-badge">
          <i class="fa-brands fa-github"></i> thakuratul2/ITR-TaxPilot
        </a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  border-top: 1px solid var(--border-subtle);
  background: #05080F;
  padding: 4rem 2rem 0;
  margin-top: 5rem;
}

.footer-container {
  max-width: 1440px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 3rem;
  padding-bottom: 3rem;
}

.footer-brand .footer-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-family: var(--font-heading);
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.footer-brand .footer-logo i {
  color: var(--accent-indigo);
}

.footer-desc {
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.6;
  max-width: 420px;
}

.footer-links-group h4 {
  font-family: var(--font-heading);
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1.25rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.footer-links-group ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-links-group a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.86rem;
  transition: var(--trans-fast);
}

.footer-links-group a:hover {
  color: var(--accent-indigo);
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding: 1.5rem 0;
}

.footer-bottom-container {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-muted);
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-author-link {
  color: #A5B4FC;
  text-decoration: none;
  font-weight: 600;
  transition: var(--trans-fast);
}

.footer-author-link:hover {
  color: white;
  text-decoration: underline;
}

.footer-repo-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  color: var(--text-primary);
  font-size: 0.8rem;
  font-weight: 600;
  text-decoration: none;
  transition: var(--trans-normal);
}

.footer-repo-badge:hover {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--accent-indigo);
  transform: translateY(-2px);
}

@media (max-width: 900px) {
  .footer-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
}
</style>
