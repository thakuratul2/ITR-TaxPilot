// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: false },

  modules: [
    '@pinia/nuxt',
    '@vueuse/nuxt',
  ],

  css: [
    '@fortawesome/fontawesome-free/css/all.min.css',
    '~/assets/css/main.css',
  ],

  app: {
    head: {
      title: 'ITR-TaxPilot — Deterministic AI Tax Co-Pilot & Form 16 Optimizer (AY 2026-27)',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Free AI-assisted, 100% deterministic Indian income tax return optimizer for AY 2026-27 and AY 2025-26. Compare Old vs New regime, maximize deductions, and get ITR recommendations.',
        },
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap',
        },
      ],
    },
  },

  nitro: {
    routeRules: {
      '/api/**': { proxy: 'http://localhost:8000/api/**' },
      '/health': { proxy: 'http://localhost:8000/health' },
    },
  },

  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
    },
  },
})
