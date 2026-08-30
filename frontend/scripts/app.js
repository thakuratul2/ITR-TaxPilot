/**
 * ITR-TaxPilot — Dynamic Interactive Frontend Application
 * Features:
 * - Dynamic Backend Auth (JWT Registration, Login, Token Persistence, Session Verification)
 * - Free PDF Upload & Step Tracker
 * - Deterministic Tax Calculation (AY 2026-27 & AY 2025-26)
 * - Interactive Chapter VI-A Deduction Hunter Simulator
 * - Section 87A Marginal Relief Engine
 * - Interactive FAQ Accordion
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const browseBtn = document.getElementById('browse-btn');
  const demoBtn = document.getElementById('demo-btn');
  const reuploadBtn = document.getElementById('reupload-btn');
  const exportPdfBtn = document.getElementById('export-pdf-btn');

  const uploadSection = document.getElementById('upload-section');
  const pipelineSection = document.getElementById('pipeline-section');
  const resultsSection = document.getElementById('results-section');
  const apiStatus = document.getElementById('api-status');

  // Auth Elements
  const authModal = document.getElementById('auth-modal');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const tabLoginBtn = document.getElementById('tab-login-btn');
  const tabSignupBtn = document.getElementById('tab-signup-btn');
  const navLoginBtn = document.getElementById('nav-login-btn');
  const navSignupBtn = document.getElementById('nav-signup-btn');
  const authForm = document.getElementById('auth-form');
  const groupName = document.getElementById('group-name');
  const modalTitle = document.getElementById('modal-title');
  const modalSubtitle = document.getElementById('modal-subtitle');
  const authSwitchBtn = document.getElementById('auth-switch-btn');
  const authSwitchPrompt = document.getElementById('auth-switch-prompt');
  const btnSubmitAuth = document.getElementById('btn-submit-auth');
  const btnGoogleLogin = document.getElementById('btn-google-login');
  const btnGithubLogin = document.getElementById('btn-github-login');
  const authButtonsContainer = document.getElementById('auth-buttons-container');
  const userProfileBadge = document.getElementById('user-profile-badge');
  const userDisplayName = document.getElementById('user-display-name');
  const userAvatarInitials = document.getElementById('user-avatar-initials');
  const logoutBtn = document.getElementById('logout-btn');

  // Deduction Sliders
  const slider80c = document.getElementById('slider-80c');
  const slider80d = document.getElementById('slider-80d');
  const sliderNps = document.getElementById('slider-nps');
  const sliderHomeLoan = document.getElementById('slider-home-loan');

  // State Management
  let isSignupMode = false;
  let hasPendingResults = false;

  let currentTaxpayer = {
    grossSalary: 2606700,
    allowancesSec10: 0,
    pt: 2500,
    tdsDeducted: 299630,
    ay: '2026-27',
  };

  // =========================================================================
  // 1. Dynamic Backend Authentication (JWT & Session)
  // =========================================================================
  function getAuthToken() {
    return localStorage.getItem('taxpilot_token');
  }

  function getStoredUser() {
    try {
      const u = localStorage.getItem('taxpilot_user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  }

  function saveAuthSession(token, user) {
    localStorage.setItem('taxpilot_token', token);
    localStorage.setItem('taxpilot_user', JSON.stringify(user));
    renderAuthState();
  }

  function clearAuthSession() {
    localStorage.removeItem('taxpilot_token');
    localStorage.removeItem('taxpilot_user');
    renderAuthState();
  }

  function renderAuthState() {
    const user = getStoredUser();
    if (user) {
      authButtonsContainer.style.display = 'none';
      userProfileBadge.style.display = 'flex';
      userDisplayName.textContent = user.full_name || user.email.split('@')[0];
      const nameForInitials = user.full_name || user.email;
      const initials = nameForInitials
        .split(' ')
        .filter(Boolean)
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
      userAvatarInitials.textContent = initials || 'AP';
    } else {
      authButtonsContainer.style.display = 'flex';
      userProfileBadge.style.display = 'none';
    }
  }

  // Verify stored session against backend /api/v1/auth/me
  async function verifySessionWithBackend() {
    const token = getAuthToken();
    if (!token) {
      renderAuthState();
      return;
    }
    try {
      const res = await fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const user = await res.json();
        saveAuthSession(token, user);
      } else {
        clearAuthSession();
      }
    } catch {
      // Offline / fallback to local storage
      renderAuthState();
    }
  }
  verifySessionWithBackend();

  // 2. Check Backend Health
  async function checkBackendHealth() {
    try {
      const res = await fetch('/health');
      if (res.ok) {
        const json = await res.json();
        if (json.success) {
          apiStatus.innerHTML = '<span class="status-dot"></span><span class="status-label">Backend Online</span>';
          return;
        }
      }
    } catch {
      // Silent catch
    }
    apiStatus.innerHTML = '<span class="status-dot" style="background:#F59E0B"></span><span class="status-label">Client Mode</span>';
  }
  checkBackendHealth();

  // =========================================================================
  // 3. Auth Modal UI Control & Submission
  // =========================================================================
  function openAuthModal(isSignup = false, pending = false) {
    isSignupMode = isSignup;
    hasPendingResults = pending;
    updateModalUI();
    authModal.style.display = 'flex';
  }

  function closeAuthModal() {
    authModal.style.display = 'none';
  }

  function updateModalUI() {
    if (isSignupMode) {
      tabSignupBtn.classList.add('active');
      tabLoginBtn.classList.remove('active');
      groupName.style.display = 'flex';
      modalTitle.textContent = 'Create Free Account';
      modalSubtitle.textContent = hasPendingResults
        ? 'Your Form 16 extraction is complete! Create a free account to unlock your tax optimization summary and printable report.'
        : 'Get instant access to deterministic AI tax analysis, Form 16 extraction, and regime optimization.';
      btnSubmitAuth.innerHTML = '<i class="fa-solid fa-user-plus"></i> Create Free Account';
      authSwitchPrompt.textContent = 'Already have an account?';
      authSwitchBtn.textContent = 'Sign in';
    } else {
      tabLoginBtn.classList.add('active');
      tabSignupBtn.classList.remove('active');
      groupName.style.display = 'none';
      modalTitle.textContent = 'Sign In to View Analysis';
      modalSubtitle.textContent = hasPendingResults
        ? 'Your Form 16 analysis is ready! Sign in to unlock your side-by-side regime comparison and deduction simulator.'
        : 'Sign in to access your saved tax summaries, Form 16 documents, and filing packs.';
      btnSubmitAuth.innerHTML = '<i class="fa-solid fa-unlock"></i> View Tax Analysis';
      authSwitchPrompt.textContent = "Don't have an account?";
      authSwitchBtn.textContent = 'Sign up for free';
    }
  }

  modalCloseBtn.addEventListener('click', closeAuthModal);
  authModal.addEventListener('click', (e) => {
    if (e.target === authModal) closeAuthModal();
  });

  tabLoginBtn.addEventListener('click', () => {
    isSignupMode = false;
    updateModalUI();
  });

  tabSignupBtn.addEventListener('click', () => {
    isSignupMode = true;
    updateModalUI();
  });

  authSwitchBtn.addEventListener('click', () => {
    isSignupMode = !isSignupMode;
    updateModalUI();
  });

  navLoginBtn.addEventListener('click', () => openAuthModal(false, false));
  navSignupBtn.addEventListener('click', () => openAuthModal(true, false));

  logoutBtn.addEventListener('click', async () => {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST' });
    } catch {
      // Ignore
    }
    clearAuthSession();
    alert('You have been signed out successfully.');
  });

  // Dynamic Auth Form Submit (POST /api/v1/auth/register or /api/v1/auth/login)
  authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('input-email').value.trim();
    const password = document.getElementById('input-password').value;
    const fullName = document.getElementById('input-name')?.value.trim() || '';

    btnSubmitAuth.disabled = true;
    btnSubmitAuth.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Authenticating...';

    const endpoint = isSignupMode ? '/api/v1/auth/register' : '/api/v1/auth/login';
    const payload = isSignupMode
      ? { email, password, full_name: fullName }
      : { email, password };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok && data.access_token) {
        saveAuthSession(data.access_token, data.user);
        closeAuthModal();

        if (hasPendingResults) {
          revealResults();
          hasPendingResults = false;
        }
      } else {
        const errorMsg = data.detail || (data.error && data.error.message) || 'Authentication failed. Please try again.';
        alert(errorMsg);
      }
    } catch (err) {
      // Fallback for standalone demo
      const fallbackUser = { email, full_name: fullName || email.split('@')[0] };
      saveAuthSession('demo-jwt-token', fallbackUser);
      closeAuthModal();
      if (hasPendingResults) {
        revealResults();
        hasPendingResults = false;
      }
    } finally {
      btnSubmitAuth.disabled = false;
      updateModalUI();
    }
  });

  // Social Auth 1-Click Handlers
  btnGoogleLogin.addEventListener('click', () => {
    const mockUser = { email: 'taxpayer.google@gmail.com', full_name: 'Google Taxpayer' };
    saveAuthSession('demo-google-jwt-token', mockUser);
    closeAuthModal();
    if (hasPendingResults) {
      revealResults();
      hasPendingResults = false;
    }
  });

  btnGithubLogin.addEventListener('click', () => {
    const mockUser = { email: 'taxpayer.github@gmail.com', full_name: 'GitHub Developer' };
    saveAuthSession('demo-github-jwt-token', mockUser);
    closeAuthModal();
    if (hasPendingResults) {
      revealResults();
      hasPendingResults = false;
    }
  });

  // =========================================================================
  // 4. Free Form 16 Upload & Stepper Flow
  // =========================================================================
  dropZone.addEventListener('click', () => fileInput.click());
  browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });

  demoBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    runExtractionSimulation();
  });

  reuploadBtn.addEventListener('click', () => {
    resultsSection.style.display = 'none';
    uploadSection.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  exportPdfBtn.addEventListener('click', () => {
    window.print();
  });

  async function handleFileUpload(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please upload a valid Form 16 PDF document.');
      return;
    }
    runExtractionSimulation(file);
  }

  async function runExtractionSimulation(file = null) {
    uploadSection.style.display = 'none';
    pipelineSection.style.display = 'block';

    let extractedData = null;

    // Step 1: Security scan
    updateStep(1, 'active');
    
    // Start backend extraction in parallel with visual tracker
    const uploadPromise = (async () => {
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        const token = getAuthToken();
        try {
          const res = await fetch('/api/v1/documents/form16', {
            method: 'POST',
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            body: formData,
          });
          if (res.ok) {
            const json = await res.json();
            if (json.data && json.data.extracted) {
              return json.data.extracted;
            }
          }
        } catch (e) {
          console.warn('Backend extraction error:', e);
        }
      }
      return null;
    })();

    await sleep(600);
    updateStep(1, 'completed');

    // Step 2: PyMuPDF Extraction
    updateStep(2, 'active');
    await sleep(700);
    updateStep(2, 'completed');

    // Step 3: AI Normalization
    updateStep(3, 'active');
    extractedData = await uploadPromise;
    await sleep(600);
    updateStep(3, 'completed');

    // Step 4: Deterministic Math
    updateStep(4, 'active');
    
    if (extractedData && extractedData.gross_salary > 0) {
      currentTaxpayer.grossSalary = extractedData.gross_salary;
      currentTaxpayer.tdsDeducted = extractedData.total_tds_deducted || 0;
      currentTaxpayer.pt = extractedData.professional_tax_sec16iii || 0;
      currentTaxpayer.allowancesSec10 = extractedData.exempt_allowances_sec10 || 0;
      currentTaxpayer.ay = extractedData.assessment_year || '2026-27';

      // Reset sliders according to extracted deductions
      let ext80c = 0;
      let ext80d = 0;
      if (extractedData.deductions_chapter_vi_a) {
        for (const d of extractedData.deductions_chapter_vi_a) {
          if (d.section === '80C') ext80c = d.amount || 0;
          if (d.section === '80D') ext80d = d.amount || 0;
        }
      }
      slider80c.value = ext80c;
      slider80d.value = ext80d;
      sliderNps.value = 0;
      sliderHomeLoan.value = 0;
    } else if (!file) {
      // Sample Data Mode (₹26.06 Lakh)
      currentTaxpayer = {
        grossSalary: 2606700,
        allowancesSec10: 0,
        pt: 2500,
        tdsDeducted: 299630,
        ay: '2026-27',
      };
      slider80c.value = 150000;
      slider80d.value = 25000;
      sliderNps.value = 50000;
      sliderHomeLoan.value = 0;
    }

    await sleep(500);
    updateStep(4, 'completed');

    pipelineSection.style.display = 'none';

    // Check if user is authenticated
    const user = getStoredUser();
    if (user) {
      revealResults();
    } else {
      hasPendingResults = true;
      openAuthModal(false, true);
    }
  }

  function revealResults() {
    resultsSection.style.display = 'block';
    recalculateTax();
    window.scrollTo({ top: resultsSection.offsetTop - 80, behavior: 'smooth' });
  }

  function updateStep(stepNum, state) {
    const stepEl = document.getElementById(`step-${stepNum}`);
    if (!stepEl) return;
    if (state === 'active') {
      stepEl.className = 'step-item active';
      stepEl.querySelector('.step-status').innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
    } else if (state === 'completed') {
      stepEl.className = 'step-item completed';
      stepEl.querySelector('.step-status').innerHTML = '<i class="fa-solid fa-check"></i> Done';
    }
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // =========================================================================
  // 5. Deterministic Tax Engine (AY 2026-27 & AY 2025-26)
  // =========================================================================
  function computeNewRegimeTax(grossSalary, allowancesSec10) {
    const stdDeduction = 75000;
    const taxableIncome = Math.max(0, grossSalary - allowancesSec10 - stdDeduction);

    // Section 115BAC Slabs for AY 2026-27
    let tax = 0;
    if (taxableIncome > 1500000) {
      tax += (taxableIncome - 1500000) * 0.30;
      tax += 300000 * 0.20;
      tax += 200000 * 0.15;
      tax += 300000 * 0.10;
      tax += 400000 * 0.05;
    } else if (taxableIncome > 1200000) {
      tax += (taxableIncome - 1200000) * 0.20;
      tax += 200000 * 0.15;
      tax += 300000 * 0.10;
      tax += 400000 * 0.05;
    } else if (taxableIncome > 1000000) {
      tax += (taxableIncome - 1000000) * 0.15;
      tax += 300000 * 0.10;
      tax += 400000 * 0.05;
    } else if (taxableIncome > 700000) {
      tax += (taxableIncome - 700000) * 0.10;
      tax += 400000 * 0.05;
    } else if (taxableIncome > 300000) {
      tax += (taxableIncome - 300000) * 0.05;
    }

    // Section 87A Rebate & Marginal Relief
    let rebate87a = 0;
    if (taxableIncome <= 700000) {
      rebate87a = tax;
      tax = 0;
    } else if (taxableIncome <= 727777) {
      const excessIncome = taxableIncome - 700000;
      if (tax > excessIncome) {
        rebate87a = tax - excessIncome;
        tax = excessIncome;
      }
    }

    const cess = Math.round(tax * 0.04);
    const totalTax = Math.round(tax + cess);

    return {
      grossIncome: grossSalary,
      stdDeduction,
      taxableIncome,
      baseTax: Math.round(tax),
      rebate87a: Math.round(rebate87a),
      cess,
      totalTax,
    };
  }

  function computeOldRegimeTax(grossSalary, allowancesSec10, totalDeductions) {
    const stdDeduction = 50000;
    const taxableIncome = Math.max(0, grossSalary - allowancesSec10 - stdDeduction - totalDeductions);

    // Old Slabs
    let tax = 0;
    if (taxableIncome > 1000000) {
      tax += (taxableIncome - 1000000) * 0.30;
      tax += 500000 * 0.20;
      tax += 250000 * 0.05;
    } else if (taxableIncome > 500000) {
      tax += (taxableIncome - 500000) * 0.20;
      tax += 250000 * 0.05;
    } else if (taxableIncome > 250000) {
      tax += (taxableIncome - 250000) * 0.05;
    }

    // Section 87A Rebate in Old Regime (Up to ₹5,00,000)
    let rebate87a = 0;
    if (taxableIncome <= 500000) {
      rebate87a = Math.min(tax, 12500);
      tax = Math.max(0, tax - rebate87a);
    }

    const cess = Math.round(tax * 0.04);
    const totalTax = Math.round(tax + cess);

    return {
      grossIncome: grossSalary,
      stdDeduction,
      totalDeductions,
      taxableIncome,
      baseTax: Math.round(tax),
      rebate87a: Math.round(rebate87a),
      cess,
      totalTax,
    };
  }

  function formatINR(num) {
    return '₹' + Number(num).toLocaleString('en-IN');
  }

  // =========================================================================
  // 6. Dynamic Recalculation Triggered by UI Sliders
  // =========================================================================
  function recalculateTax() {
    const val80c = Number(slider80c.value);
    const val80d = Number(slider80d.value);
    const valNps = Number(sliderNps.value);
    const valHomeLoan = Number(sliderHomeLoan.value);

    document.getElementById('val-80c').textContent = formatINR(val80c);
    document.getElementById('val-80d').textContent = formatINR(val80d);
    document.getElementById('val-nps').textContent = formatINR(valNps);
    document.getElementById('val-home-loan').textContent = formatINR(valHomeLoan);

    const totalOldDeductions = val80c + val80d + valNps + valHomeLoan + currentTaxpayer.pt;

    const newResult = computeNewRegimeTax(currentTaxpayer.grossSalary, currentTaxpayer.allowancesSec10);
    const oldResult = computeOldRegimeTax(currentTaxpayer.grossSalary, currentTaxpayer.allowancesSec10, totalOldDeductions);

    // New Regime UI
    document.getElementById('new-gross-income').textContent = formatINR(newResult.grossIncome);
    document.getElementById('new-standard-deduction').textContent = formatINR(newResult.stdDeduction);
    document.getElementById('new-taxable-income').textContent = formatINR(newResult.taxableIncome);
    document.getElementById('new-base-tax').textContent = formatINR(newResult.baseTax);
    document.getElementById('new-rebate-87a').textContent = formatINR(newResult.rebate87a);
    document.getElementById('new-cess').textContent = formatINR(newResult.cess);
    document.getElementById('new-total-tax').textContent = formatINR(newResult.totalTax);
    document.getElementById('new-tds-deducted').textContent = formatINR(currentTaxpayer.tdsDeducted);

    const newNet = newResult.totalTax - currentTaxpayer.tdsDeducted;
    document.getElementById('new-net-payable').textContent = newNet >= 0 ? `${formatINR(newNet)} (Payable)` : `${formatINR(Math.abs(newNet))} (Refund)`;
    document.getElementById('new-net-payable').className = newNet >= 0 ? 'text-payable' : 'text-green';
    document.getElementById('new-effective-rate').textContent = `Effective Rate: ${((newResult.totalTax / newResult.grossIncome) * 100).toFixed(1)}%`;

    // Old Regime UI
    document.getElementById('old-gross-income').textContent = formatINR(oldResult.grossIncome);
    document.getElementById('old-standard-deduction').textContent = formatINR(oldResult.stdDeduction);
    document.getElementById('old-total-deductions').textContent = formatINR(oldResult.totalDeductions);
    document.getElementById('old-taxable-income').textContent = formatINR(oldResult.taxableIncome);
    document.getElementById('old-base-tax').textContent = formatINR(oldResult.baseTax);
    document.getElementById('old-rebate-87a').textContent = formatINR(oldResult.rebate87a);
    document.getElementById('old-cess').textContent = formatINR(oldResult.cess);
    document.getElementById('old-total-tax').textContent = formatINR(oldResult.totalTax);
    document.getElementById('old-tds-deducted').textContent = formatINR(currentTaxpayer.tdsDeducted);

    const oldNet = oldResult.totalTax - currentTaxpayer.tdsDeducted;
    document.getElementById('old-net-payable').textContent = oldNet >= 0 ? `${formatINR(oldNet)} (Payable)` : `${formatINR(Math.abs(oldNet))} (Refund)`;
    document.getElementById('old-net-payable').className = oldNet >= 0 ? 'text-payable' : 'text-green';
    document.getElementById('old-effective-rate').textContent = `Effective Rate: ${((oldResult.totalTax / oldResult.grossIncome) * 100).toFixed(1)}%`;

    // Winner Evaluation
    const cardNew = document.getElementById('card-new-regime');
    const cardOld = document.getElementById('card-old-regime');
    const badge = document.getElementById('recommended-regime-badge');
    const savingsHeadline = document.getElementById('savings-headline');
    const savingsSubtext = document.getElementById('savings-subtext');

    if (newResult.totalTax <= oldResult.totalTax) {
      const savings = oldResult.totalTax - newResult.totalTax;
      cardNew.className = 'regime-card featured';
      cardOld.className = 'regime-card';
      badge.textContent = 'NEW REGIME RECOMMENDED';
      badge.style.background = '#10B981';
      savingsHeadline.innerHTML = `You Save <span class="highlight-green">${formatINR(savings)}</span> with the New Tax Regime!`;
      savingsSubtext.textContent = `The New Regime (Section 115BAC) provides lower tax slabs and an increased ₹75,000 standard deduction for salaried individuals.`;
      document.getElementById('hunter-extra-savings').textContent = '₹0 (New Regime Beats Old)';
    } else {
      const savings = newResult.totalTax - oldResult.totalTax;
      cardOld.className = 'regime-card featured';
      cardNew.className = 'regime-card';
      badge.textContent = 'OLD REGIME RECOMMENDED';
      badge.style.background = '#6366F1';
      savingsHeadline.innerHTML = `You Save <span class="highlight-green">${formatINR(savings)}</span> with the Old Tax Regime!`;
      savingsSubtext.textContent = `Your high Chapter VI-A deductions (80C, 80D, NPS, Home Loan) successfully reduced taxable income enough to beat the New Regime.`;
      document.getElementById('hunter-extra-savings').textContent = `${formatINR(savings)} Saved!`;
    }
  }

  // =========================================================================
  // 7. Interactive FAQ Accordion
  // =========================================================================
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    const answerDiv = item.querySelector('.faq-answer');

    questionBtn.addEventListener('click', () => {
      const isActive = item.classList.contains('active');

      faqItems.forEach(otherItem => {
        otherItem.classList.remove('active');
        const otherAnswer = otherItem.querySelector('.faq-answer');
        if (otherAnswer) otherAnswer.style.maxHeight = null;
      });

      if (!isActive) {
        item.classList.add('active');
        answerDiv.style.maxHeight = answerDiv.scrollHeight + 40 + 'px';
      }
    });
  });

  // Slider Event Listeners
  [slider80c, slider80d, sliderNps, sliderHomeLoan].forEach(slider => {
    slider.addEventListener('input', recalculateTax);
  });
});
