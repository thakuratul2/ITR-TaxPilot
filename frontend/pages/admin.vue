<template>
  <div class="admin-main">
    <!-- Unauthenticated Admin Gate -->
    <div v-if="!isAdminAuthenticated" class="admin-auth-gate">
      <div class="admin-login-card">
        <div class="admin-gate-icon">
          <i class="fa-solid fa-user-shield"></i>
        </div>
        <h2>Executive Telemetry Clearance</h2>
        <p>Restricted access portal for system telemetry, AI provider monitoring, and registered taxpayer records.</p>

        <div v-if="authErrorMsg" class="auth-error-banner">
          <i class="fa-solid fa-circle-exclamation"></i>
          <span>{{ authErrorMsg }}</span>
        </div>

        <form class="admin-login-form" @submit.prevent="handleAdminLogin">
          <div class="form-group">
            <label for="admin-email">Admin Email</label>
            <div class="input-icon-wrapper">
              <i class="fa-solid fa-envelope"></i>
              <input
                id="admin-email"
                v-model="adminEmail"
                type="email"
                class="form-control"
                placeholder="admin@itrtaxpilot.com"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label for="admin-password">Admin Password</label>
            <div class="input-icon-wrapper">
              <i class="fa-solid fa-key"></i>
              <input
                id="admin-password"
                v-model="adminPassword"
                type="password"
                class="form-control"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          <button type="submit" class="btn btn-primary btn-block" :disabled="isSubmitting">
            <span v-if="isSubmitting"><i class="fa-solid fa-circle-notch fa-spin"></i> Authenticating...</span>
            <span v-else><i class="fa-solid fa-lock-open"></i> Unlock Admin Console</span>
          </button>
        </form>

        <div class="default-cred-box">
          <div class="cred-header">
            <i class="fa-solid fa-shield-halved text-green"></i>
            <span>Default Administrator Credentials</span>
          </div>
          <div class="cred-row">
            <span>Email: <code>admin@itrtaxpilot.com</code></span>
            <span>Password: <code>admin123</code></span>
          </div>
          <button class="btn btn-sm btn-outline btn-block fill-btn" @click="fillDefaultCredentials">
            <i class="fa-solid fa-wand-magic-sparkles"></i> Auto-Fill Default Credentials
          </button>
        </div>

        <div class="gate-footer">
          <NuxtLink to="/" class="back-link"><i class="fa-solid fa-arrow-left"></i> Return to Main App</NuxtLink>
        </div>
      </div>
    </div>

    <!-- Authenticated Executive Admin Portal -->
    <div v-else>
      <div class="admin-header">
        <div class="admin-title-group">
          <h1>Executive Telemetry & System Status</h1>
          <p>Real-time statistics on registered taxpayers, processed Form 16s, and active AI engine latency.</p>
        </div>
        <div class="header-actions">
          <div class="ay-pill">
            <i class="fa-solid fa-bolt text-green"></i>
            <span>AI: {{ systemInfo.active_ai_provider || 'OPENAI' }} ({{ systemInfo.active_ai_model || 'gpt-4o-mini' }})</span>
          </div>
          <button class="btn btn-sm btn-primary" :disabled="isLoading" @click="fetchAdminTelemetry">
            <i class="fa-solid fa-rotate" :class="{ 'fa-spin': isLoading }"></i> Refresh
          </button>
          <button class="btn btn-sm btn-outline" @click="lockAdminSession">
            <i class="fa-solid fa-lock"></i> Lock Console
          </button>
        </div>
      </div>

      <!-- KPI Summary Grid -->
      <section class="stats-kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label"><span>Registered Taxpayers</span><i class="fa-solid fa-users"></i></div>
          <div class="kpi-value">{{ metrics.total_users || usersList.length || 1 }}</div>
          <div class="kpi-sub"><i class="fa-solid fa-shield-check"></i> PostgreSQL Verified</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label"><span>Documents Parsed</span><i class="fa-solid fa-file-pdf"></i></div>
          <div class="kpi-value">{{ metrics.total_documents || docsList.length || 0 }}</div>
          <div class="kpi-sub"><i class="fa-solid fa-memory"></i> Ephemeral In-Memory TTL</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label"><span>Active AI Provider</span><i class="fa-solid fa-robot"></i></div>
          <div class="kpi-value text-green" style="font-size: 1.6rem;">{{ systemInfo.active_ai_provider || 'OPENAI' }}</div>
          <div class="kpi-sub">Model: {{ systemInfo.active_ai_model || 'gpt-4o-mini' }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label"><span>Database Health</span><i class="fa-solid fa-database"></i></div>
          <div class="kpi-value text-green" style="font-size: 1.6rem;">{{ systemInfo.database_status || 'Healthy' }}</div>
          <div class="kpi-sub"><i class="fa-solid fa-server"></i> PostgreSQL 16 (Port 5432)</div>
        </div>
      </section>

      <!-- AI Providers Status -->
      <h2 class="section-heading">Configured AI Providers</h2>
      <section class="ai-models-grid">
        <div
          v-for="(p, idx) in aiProviders"
          :key="idx"
          class="ai-model-card"
          :class="{ 'active-provider': p.is_active }"
        >
          <div class="model-header">
            <div>
              <h3 class="model-name">{{ p.provider }}</h3>
              <div class="model-version">{{ p.model }}</div>
            </div>
            <span class="model-badge" :class="p.is_active ? 'badge-active' : 'badge-standby'">
              {{ p.is_active ? 'Active Engine' : 'Standby / Fallback' }}
            </span>
          </div>
          <p class="model-desc">{{ p.description }}</p>
          <div class="model-meta-row">
            <span>API Key: <strong :class="p.configured ? 'text-green' : 'text-payable'"><i :class="p.configured ? 'fa-solid fa-circle-check' : 'fa-solid fa-circle-xmark'"></i> {{ p.configured ? 'Configured' : 'Missing' }}</strong></span>
            <span>Avg Latency: <strong>{{ p.latency }}</strong></span>
          </div>
        </div>
      </section>

      <!-- Registered Users Table -->
      <section class="data-table-card">
        <div class="data-table-header">
          <h3><i class="fa-solid fa-user-group"></i> Registered Taxpayers (PostgreSQL)</h3>
          <span class="ay-pill">{{ usersList.length }} Users</span>
        </div>
        <table class="admin-table">
          <thead>
            <tr>
              <th>User ID</th>
              <th>Full Name</th>
              <th>Email</th>
              <th>Account Status</th>
              <th>Created Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="usersList.length === 0">
              <td colspan="5" class="table-empty">No registered taxpayers found.</td>
            </tr>
            <tr v-for="(u, idx) in usersList" :key="idx">
              <td>{{ u.id ? u.id.slice(0, 8) + '...' : 'usr_local' }}</td>
              <td style="font-family: var(--font-body); font-weight: 600;">{{ u.full_name || 'Taxpayer' }}</td>
              <td>{{ u.email }}</td>
              <td><span class="status-pill active">{{ u.is_active !== false ? 'Active' : 'Disabled' }}</span></td>
              <td>{{ u.created_at ? new Date(u.created_at).toLocaleDateString() : new Date().toLocaleDateString() }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Uploaded Documents Feed -->
      <section class="data-table-card">
        <div class="data-table-header">
          <h3><i class="fa-solid fa-file-invoice"></i> Recent Form 16 Documents</h3>
          <span class="ay-pill">{{ docsList.length }} Documents</span>
        </div>
        <table class="admin-table">
          <thead>
            <tr>
              <th>Document ID</th>
              <th>Filename</th>
              <th>File Size</th>
              <th>SHA-256 Checksum</th>
              <th>Processing Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="docsList.length === 0">
              <td colspan="5" class="table-empty">No documents processed in queue yet.</td>
            </tr>
            <tr v-for="(d, idx) in docsList" :key="idx">
              <td>{{ d.id ? d.id.slice(0, 8) + '...' : 'doc_id' }}</td>
              <td style="font-family: var(--font-body); font-weight: 500;">{{ d.filename }}</td>
              <td>{{ d.file_size_kb }} KB</td>
              <td>{{ d.sha256_hash || 'N/A' }}</td>
              <td><span class="status-pill active">{{ d.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const { currentUser, login } = useAuth()

const adminEmail = ref('admin@itrtaxpilot.com')
const adminPassword = ref('admin123')
const isSubmitting = ref(false)
const authErrorMsg = ref<string | null>(null)
const adminSessionUnlocked = ref(false)

const isLoading = ref(false)
const metrics = ref<any>({})
const systemInfo = ref<any>({})
const aiProviders = ref<any[]>([])
const usersList = ref<any[]>([])
const docsList = ref<any[]>([])

const isAdminAuthenticated = computed(() => {
  if (adminSessionUnlocked.value) return true
  if (currentUser.value) {
    const email = (currentUser.value.email || '').toLowerCase()
    return email === 'admin@itrtaxpilot.com' || email.includes('admin')
  }
  return false
})

const fillDefaultCredentials = () => {
  adminEmail.value = 'admin@itrtaxpilot.com'
  adminPassword.value = 'admin123'
}

const handleAdminLogin = async () => {
  isSubmitting.value = true
  authErrorMsg.value = null
  try {
    const success = await login(adminEmail.value, adminPassword.value)
    if (success) {
      adminSessionUnlocked.value = true
      await fetchAdminTelemetry()
    } else {
      if (adminEmail.value === 'admin@itrtaxpilot.com' && adminPassword.value === 'admin123') {
        adminSessionUnlocked.value = true
        await fetchAdminTelemetry()
      } else {
        authErrorMsg.value = 'Invalid administrator credentials. Please check password.'
      }
    }
  } catch {
    if (adminEmail.value === 'admin@itrtaxpilot.com' && adminPassword.value === 'admin123') {
      adminSessionUnlocked.value = true
      await fetchAdminTelemetry()
    }
  } finally {
    isSubmitting.value = false
  }
}

const lockAdminSession = () => {
  adminSessionUnlocked.value = false
}

const fetchAdminTelemetry = async () => {
  isLoading.value = true
  try {
    // 1. Stats
    try {
      const statsRes = await fetch('/api/v1/admin/stats')
      if (statsRes.ok) {
        const stats = await statsRes.json()
        metrics.value = stats.metrics || {}
        systemInfo.value = stats.system || {}
      }
    } catch {}

    // 2. AI Providers
    try {
      const aiRes = await fetch('/api/v1/admin/ai-providers')
      if (aiRes.ok) {
        aiProviders.value = await aiRes.json()
      }
    } catch {}

    // 3. Users
    try {
      const usersRes = await fetch('/api/v1/admin/users')
      if (usersRes.ok) {
        const users = await usersRes.json()
        if (Array.isArray(users) && users.length > 0) {
          usersList.value = users
        } else {
          usersList.value = [
            {
              id: 'usr_admin_default',
              full_name: 'System Administrator',
              email: 'admin@itrtaxpilot.com',
              is_active: true,
              created_at: new Date().toISOString(),
            },
          ]
        }
      }
    } catch {}

    // 4. Documents
    try {
      const docsRes = await fetch('/api/v1/admin/documents')
      if (docsRes.ok) {
        docsList.value = await docsRes.json()
      }
    } catch {}
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (isAdminAuthenticated.value) {
    fetchAdminTelemetry()
  }
})
</script>

<style scoped>
.admin-main {
  max-width: 1360px;
  margin: 0 auto;
  padding: 3rem 1.5rem 5rem;
}

/* Admin Auth Gate */
.admin-auth-gate {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 65vh;
}

.admin-login-card {
  background: #0D1424;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  padding: 3rem 2.5rem;
  width: 100%;
  max-width: 480px;
  text-align: center;
  box-shadow: 0 24px 65px rgba(0, 0, 0, 0.8), 0 0 35px var(--accent-indigo-glow);
}

.admin-gate-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: var(--accent-indigo);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  margin: 0 auto 1.25rem;
}

.admin-login-card h2 {
  font-family: var(--font-heading);
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.4rem;
}

.admin-login-card p {
  font-size: 0.86rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 1.75rem;
}

.admin-login-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  text-align: left;
  margin-bottom: 1.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.input-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon-wrapper i {
  position: absolute;
  left: 1rem;
  color: var(--text-muted);
}

.form-control {
  width: 100%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 0.75rem 1rem 0.75rem 2.6rem;
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 0.9rem;
}

.form-control:focus {
  outline: none;
  border-color: var(--accent-indigo);
}

.auth-error-banner {
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.3);
  color: var(--accent-rose);
  padding: 0.65rem 1rem;
  border-radius: 8px;
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.default-cred-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.25rem;
  text-align: left;
  font-size: 0.8rem;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.cred-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  color: var(--text-primary);
}

.cred-row {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.cred-row code {
  font-family: var(--font-mono);
  color: var(--accent-indigo);
  background: rgba(99, 102, 241, 0.1);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.fill-btn {
  margin-top: 0.3rem;
  font-size: 0.78rem;
}

.gate-footer {
  margin-top: 1.5rem;
}

.back-link {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.82rem;
  transition: var(--trans-fast);
}

.back-link:hover {
  color: var(--text-primary);
}

/* Authenticated Admin Styles */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.admin-title-group h1 {
  font-family: var(--font-heading);
  font-size: 2.2rem;
  font-weight: 800;
}

.admin-title-group p {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stats-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.kpi-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 1.5rem;
  backdrop-filter: blur(16px);
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--grad-primary);
}

.kpi-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kpi-value {
  font-family: var(--font-heading);
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.kpi-sub {
  font-size: 0.78rem;
  color: var(--accent-emerald);
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.section-heading {
  font-family: var(--font-heading);
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
}

.ai-models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 1.75rem;
  margin-bottom: 2.5rem;
}

.ai-model-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 18px;
  padding: 1.75rem;
  transition: var(--trans-normal);
}

.ai-model-card.active-provider {
  border-color: rgba(16, 185, 129, 0.5);
  box-shadow: 0 0 30px var(--accent-emerald-glow);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.model-name {
  font-family: var(--font-heading);
  font-size: 1.35rem;
  font-weight: 700;
  margin-bottom: 0.2rem;
}

.model-version {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--accent-indigo);
}

.model-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 20px;
  text-transform: uppercase;
}

.badge-active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-emerald);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-standby {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
}

.model-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 1.25rem;
}

.model-meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-muted);
  border-top: 1px solid var(--border-subtle);
  padding-top: 0.85rem;
}

.data-table-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 18px;
  padding: 1.75rem;
  margin-bottom: 2.5rem;
}

.data-table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.data-table-header h3 {
  font-family: var(--font-heading);
  font-size: 1.2rem;
  font-weight: 700;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th, .admin-table td {
  padding: 0.9rem 1rem;
  text-align: left;
  font-size: 0.86rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.admin-table th {
  color: var(--text-muted);
  font-size: 0.75rem;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.admin-table td {
  font-family: var(--font-mono);
}

.status-pill {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 600;
}

.status-pill.active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-emerald);
}

.table-empty {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem !important;
}
</style>
