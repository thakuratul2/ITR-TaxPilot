<template>
  <section id="upload-section" class="hero-section">
    <div class="hero-content">
      <div class="hero-badge">
        <i class="fa-solid fa-sparkles text-green"></i>
        <span>Budget 2024/2025 S.115BAC Enforced · AY 2026-27 Ready</span>
      </div>

      <h1 class="hero-title">
        The Autonomous, Deterministic<br />
        <span class="gradient-text">Form 16 Tax Co-Pilot</span>
      </h1>

      <p class="hero-subtitle">
        Upload your Form 16 PDF to instantly extract, audit, and compare your taxes across
        Old vs New Regimes for <strong>AY 2026-27</strong>. 100% deterministic arithmetic with zero LLM hallucination risk.
      </p>

      <div
        class="upload-card"
        :class="{ 'is-dragging': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInputRef"
          type="file"
          accept=".pdf,application/pdf"
          class="hidden-file-input"
          @change="handleFileChange"
        />

        <div class="upload-icon-circle">
          <i class="fa-solid fa-cloud-arrow-up"></i>
        </div>

        <div class="upload-text-group">
          <h3>Drop your Form 16 PDF here, or <span class="upload-browse-link">browse files</span></h3>
          <p>Supports signed or digitally generated Part A & Part B PDFs (Max 10MB)</p>
        </div>

        <div class="upload-features">
          <div class="upload-feature"><i class="fa-solid fa-shield-check text-green"></i> 100% In-Memory RAM Only</div>
          <div class="upload-feature"><i class="fa-solid fa-lock text-green"></i> Client-Side PII Masking</div>
          <div class="upload-feature"><i class="fa-solid fa-bolt text-green"></i> Instant AI Extraction</div>
        </div>

        <div class="upload-divider">
          <span>OR</span>
        </div>

        <button class="btn btn-secondary btn-sm" @click.stop="handleSampleData">
          <i class="fa-solid fa-play"></i> Try with Sample Form 16 Data (₹26.06 Lakh)
        </button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { processForm16File } = useDocumentUpload()

const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    processForm16File(target.files[0])
  }
}

const handleDrop = (e: DragEvent) => {
  isDragging.value = false
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    const file = e.dataTransfer.files[0]
    if (file.name.toLowerCase().endsWith('.pdf')) {
      processForm16File(file)
    } else {
      alert('Please drop a valid Form 16 PDF document.')
    }
  }
}

const handleSampleData = () => {
  processForm16File()
}
</script>

<style scoped>
.hero-section {
  text-align: center;
  padding: 4rem 1.5rem 3rem;
  position: relative;
  z-index: 1;
}

.hero-content {
  max-width: 860px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.25);
  padding: 0.35rem 1rem;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #C7D2FE;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-family: var(--font-heading);
  font-size: 3.2rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin-bottom: 1.25rem;
}

.hero-subtitle {
  font-size: 1.05rem;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 720px;
  margin: 0 auto 2.5rem;
}

.upload-card {
  background: var(--bg-card);
  border: 2px dashed rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 3rem 2rem;
  cursor: pointer;
  transition: var(--trans-normal);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
  box-shadow: var(--shadow-md);
}

.upload-card:hover, .upload-card.is-dragging {
  border-color: var(--accent-indigo);
  background: var(--bg-card-hover);
  box-shadow: var(--shadow-glow);
  transform: translateY(-2px);
}

.hidden-file-input {
  display: none;
}

.upload-icon-circle {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--accent-indigo);
  transition: var(--trans-normal);
}

.upload-card:hover .upload-icon-circle {
  transform: scale(1.1);
  background: var(--accent-indigo);
  color: white;
}

.upload-text-group h3 {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.upload-browse-link {
  color: var(--accent-indigo);
  text-decoration: underline;
}

.upload-text-group p {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.upload-features {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  justify-content: center;
  margin: 0.5rem 0;
}

.upload-feature {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.upload-divider {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 280px;
}

.upload-divider::before, .upload-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.upload-divider span {
  padding: 0 0.75rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.2rem;
  }
}
</style>
