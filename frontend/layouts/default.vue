<template>
  <div class="app-layout">
    <!-- Ambient Glow Orbs -->
    <div class="glow-orb orb-1"></div>
    <div class="glow-orb orb-2"></div>
    <div class="glow-orb orb-3"></div>

    <!-- Header Navigation -->
    <AppHeader />

    <!-- Main Content Slot -->
    <main class="app-main-content">
      <slot />
    </main>

    <!-- Gated Auth Modal -->
    <AuthModal />

    <!-- Footer -->
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
const { initAuth } = useAuth()

onMounted(() => {
  initAuth()
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

.app-main-content {
  flex: 1;
  position: relative;
  z-index: 1;
}
</style>
