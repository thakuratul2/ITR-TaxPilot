<template>
  <header class="app-header">
    <div class="header-container">
      <NuxtLink to="/" class="brand">
        <div class="brand-logo">
          <i class="fa-solid fa-file-invoice-dollar"></i>
        </div>
        <div class="brand-text">
          <span class="brand-name">ITR-TaxPilot</span>
          <span class="brand-tagline">Deterministic Tax Co-Pilot</span>
        </div>
      </NuxtLink>

      <nav class="nav-links">
        <a href="#upload-section" class="nav-link">
          <i class="fa-solid fa-cloud-arrow-up"></i> Upload
        </a>

        <!-- Tax Guides Dropdown -->
        <div class="nav-dropdown">
          <button class="nav-dropdown-btn">
            <span>Tax Guides</span>
            <i class="fa-solid fa-chevron-down dropdown-arrow"></i>
          </button>
          <div class="nav-dropdown-menu">
            <a href="#regimes-guide" class="dropdown-item">
              <div class="dropdown-item-icon"><i class="fa-solid fa-scale-balanced"></i></div>
              <div class="dropdown-item-text">
                <strong>Old vs New Regime</strong>
                <span>AY 2026-27 S.115BAC slabs & differences</span>
              </div>
            </a>
            <a href="#deduction-guide" class="dropdown-item">
              <div class="dropdown-item-icon"><i class="fa-solid fa-crosshairs"></i></div>
              <div class="dropdown-item-text">
                <strong>Deduction Hunter</strong>
                <span>80C, 80D, 80CCD(1B), 24(b) catalog</span>
              </div>
            </a>
            <a href="#marginal-relief-guide" class="dropdown-item">
              <div class="dropdown-item-icon"><i class="fa-solid fa-chart-line"></i></div>
              <div class="dropdown-item-text">
                <strong>Section 87A Marginal Relief</strong>
                <span>Zero tax cliff formula & example</span>
              </div>
            </a>
            <a href="#itr-selector-guide" class="dropdown-item">
              <div class="dropdown-item-icon"><i class="fa-solid fa-file-signature"></i></div>
              <div class="dropdown-item-text">
                <strong>ITR Form Selector</strong>
                <span>ITR-1 Sahaj vs ITR-2 decision tree</span>
              </div>
            </a>
            <a href="#security-guide" class="dropdown-item">
              <div class="dropdown-item-icon"><i class="fa-solid fa-shield-halved"></i></div>
              <div class="dropdown-item-text">
                <strong>Privacy & Security</strong>
                <span>Ephemeral in-memory data processing</span>
              </div>
            </a>
          </div>
        </div>

        <a href="#faq-section" class="nav-link">FAQ</a>
        <a href="https://github.com/thakuratul2/ITR-TaxPilot" target="_blank" class="nav-link github-nav-link">
          <i class="fa-brands fa-github"></i> GitHub
        </a>
      </nav>

      <div class="header-status">
        <div class="ay-pill">
          <i class="fa-solid fa-calendar-check"></i>
          <span>AY 2026-27</span>
        </div>

        <div class="api-status-badge">
          <span class="status-dot"></span>
          <span class="status-label">Backend Online</span>
        </div>

        <!-- Auth Slot -->
        <div v-if="!currentUser" class="auth-buttons-container">
          <button class="btn btn-sm btn-outline" @click="openAuthModal(false)">
            <i class="fa-solid fa-arrow-right-to-bracket"></i> Sign In
          </button>
          <button class="btn btn-sm btn-primary" @click="openAuthModal(true)">
            <i class="fa-solid fa-user-plus"></i> Sign Up Free
          </button>
        </div>

        <div v-else class="user-profile-badge">
          <div class="user-avatar">{{ userInitials }}</div>
          <div class="user-info">
            <span class="user-name">{{ displayName }}</span>
            <span class="user-tier">{{ isAdmin ? 'Administrator' : 'Taxpayer' }}</span>
          </div>
          <NuxtLink v-if="isAdmin" to="/admin" class="btn-admin-link" title="Admin Portal">
            <i class="fa-solid fa-gauge-high"></i>
          </NuxtLink>
          <button class="btn-icon" title="Sign Out" @click="logout">
            <i class="fa-solid fa-power-off"></i>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const { currentUser, openAuthModal, logout } = useAuth()

const displayName = computed(() => {
  if (!currentUser.value) return 'Taxpayer'
  return currentUser.value.full_name || currentUser.value.name || currentUser.value.email.split('@')[0]
})

const isAdmin = computed(() => {
  if (!currentUser.value) return false
  const email = (currentUser.value.email || '').toLowerCase()
  return email === 'admin@itrtaxpilot.com' || email.includes('admin')
})

const userInitials = computed(() => {
  const name = displayName.value
  return name
    .split(' ')
    .filter(Boolean)
    .map((n: string) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || 'AP'
})
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(7, 11, 20, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-subtle);
  padding: 0.75rem 2rem;
}

.header-container {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--grad-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: white;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-family: var(--font-heading);
  font-size: 1.22rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  line-height: 1.15;
}

.brand-tagline {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: nowrap;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.86rem;
  font-weight: 500;
  transition: var(--trans-fast);
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.nav-link:hover {
  color: var(--text-primary);
}

.github-nav-link {
  color: #A5B4FC;
}

/* Nav Dropdown */
.nav-dropdown {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.nav-dropdown-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: 0.86rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  cursor: pointer;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  transition: var(--trans-fast);
}

.nav-dropdown-btn:hover, .nav-dropdown:hover .nav-dropdown-btn {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.06);
}

.dropdown-arrow {
  font-size: 0.7rem;
  color: var(--text-muted);
  transition: transform var(--trans-fast);
}

.nav-dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
  color: var(--accent-indigo);
}

.nav-dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%) translateY(8px);
  min-width: 320px;
  background: #0D1424;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 0.6rem;
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.7), 0 0 25px rgba(99, 102, 241, 0.2);
  opacity: 0;
  pointer-events: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 200;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  backdrop-filter: blur(16px);
}

.nav-dropdown:hover .nav-dropdown-menu,
.nav-dropdown:focus-within .nav-dropdown-menu {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(-50%) translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  border-radius: 10px;
  text-decoration: none;
  color: var(--text-primary);
  transition: var(--trans-fast);
}

.dropdown-item:hover {
  background: rgba(99, 102, 241, 0.12);
}

.dropdown-item-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--accent-indigo);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.dropdown-item:hover .dropdown-item-icon {
  background: var(--accent-indigo);
  color: white;
}

.dropdown-item-text {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.dropdown-item-text strong {
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.25;
}

.dropdown-item-text span {
  font-size: 0.74rem;
  color: var(--text-secondary);
  line-height: 1.35;
}

.header-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.ay-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  padding: 0 0.85rem;
  height: 36px;
  border-radius: 18px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  flex-shrink: 0;
  line-height: 1;
}

.ay-pill i {
  color: var(--accent-indigo);
}

.api-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 0 0.85rem;
  height: 36px;
  border-radius: 18px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--accent-emerald);
  white-space: nowrap;
  flex-shrink: 0;
  line-height: 1;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--accent-emerald);
  box-shadow: 0 0 8px var(--accent-emerald);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

.auth-buttons-container {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.user-profile-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  padding: 0 0.75rem;
  height: 36px;
  border-radius: 18px;
  flex-shrink: 0;
}

.user-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--grad-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.1;
}

.user-tier {
  font-size: 0.62rem;
  color: var(--accent-emerald);
  font-weight: 600;
}

.btn-admin-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-indigo);
  text-decoration: none;
  font-size: 0.75rem;
  transition: var(--trans-fast);
}

.btn-admin-link:hover {
  background: var(--accent-indigo);
  color: white;
}

.btn-icon {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 6px;
  transition: var(--trans-fast);
}

.btn-icon:hover {
  color: var(--accent-rose);
}
</style>
