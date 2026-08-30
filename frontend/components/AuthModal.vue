<template>
  <div v-if="isAuthModalOpen" class="modal-backdrop" @click="closeAuthModal">
    <div class="modal-card" @click.stop>
      <button class="modal-close-btn" @click="closeAuthModal">
        <i class="fa-solid fa-xmark"></i>
      </button>

      <div class="modal-header">
        <div class="modal-icon">
          <i class="fa-solid fa-shield-halved"></i>
        </div>
        <h3>{{ isSignupMode ? 'Create TaxPilot Account' : 'Sign In to View Analysis' }}</h3>
        <p>
          {{
            hasPendingResults
              ? 'Your Form 16 extraction is complete! Sign in to view your dynamic tax optimization breakdown.'
              : 'Access your saved tax calculations, Form 16 analyses, and multi-year comparisons.'
          }}
        </p>
      </div>

      <div v-if="authError" class="auth-error-banner">
        <i class="fa-solid fa-triangle-exclamation"></i>
        <span>{{ authError }}</span>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div v-if="isSignupMode" class="form-group">
          <label for="input-name">Full Name</label>
          <div class="input-icon-wrapper">
            <i class="fa-solid fa-user"></i>
            <input
              id="input-name"
              v-model="fullName"
              type="text"
              class="form-control"
              placeholder="e.g. Atul Pratap Singh"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="input-email">Email Address</label>
          <div class="input-icon-wrapper">
            <i class="fa-solid fa-envelope"></i>
            <input
              id="input-email"
              v-model="email"
              type="email"
              class="form-control"
              placeholder="taxpayer@example.com"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="input-password">Password</label>
          <div class="input-icon-wrapper">
            <i class="fa-solid fa-lock"></i>
            <input
              id="input-password"
              v-model="password"
              type="password"
              class="form-control"
              placeholder="••••••••"
              required
              minlength="6"
            />
          </div>
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="isSubmitting">
          <span v-if="isSubmitting"><i class="fa-solid fa-circle-notch fa-spin"></i> Authenticating...</span>
          <span v-else>{{ isSignupMode ? 'Create Free Account & View Tax' : 'Sign In & View Tax Summary' }}</span>
        </button>
      </form>

      <div class="modal-footer">
        <span>{{ isSignupMode ? 'Already have an account?' : "Don't have an account?" }}</span>
        <button class="switch-mode-btn" @click="isSignupMode = !isSignupMode">
          {{ isSignupMode ? 'Sign In' : 'Create an Account Free' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const {
  isAuthModalOpen,
  isSignupMode,
  hasPendingResults,
  authError,
  isSubmitting,
  login,
  register,
  closeAuthModal,
} = useAuth()

const { unlockResults } = useDocumentUpload()

const fullName = ref('')
const email = ref('')
const password = ref('')

const handleSubmit = async () => {
  let success = false
  if (isSignupMode.value) {
    success = await register(email.value, password.value, fullName.value)
  } else {
    success = await login(email.value, password.value)
  }

  if (success) {
    if (hasPendingResults.value) {
      unlockResults()
      hasPendingResults.value = false
    }
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(12px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-card {
  background: #0D1424;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  width: 100%;
  max-width: 440px;
  padding: 2.25rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8), 0 0 35px var(--accent-indigo-glow);
  position: relative;
}

.modal-close-btn {
  position: absolute;
  top: 1.25rem;
  right: 1.25rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: var(--trans-fast);
}

.modal-close-btn:hover {
  color: white;
}

.modal-header {
  text-align: center;
  margin-bottom: 1.75rem;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: var(--accent-indigo);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  margin: 0 auto 1rem;
}

.modal-header h3 {
  font-family: var(--font-heading);
  font-size: 1.35rem;
  font-weight: 700;
  margin-bottom: 0.4rem;
}

.modal-header p {
  font-size: 0.84rem;
  color: var(--text-secondary);
  line-height: 1.45;
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

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  text-align: left;
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
  font-size: 0.9rem;
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
  transition: var(--trans-fast);
}

.form-control:focus {
  outline: none;
  border-color: var(--accent-indigo);
  background: rgba(255, 255, 255, 0.07);
}

.modal-footer {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.82rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}

.switch-mode-btn {
  background: transparent;
  border: none;
  color: var(--accent-indigo);
  font-weight: 600;
  cursor: pointer;
  font-size: 0.82rem;
}

.switch-mode-btn:hover {
  text-decoration: underline;
}
</style>
