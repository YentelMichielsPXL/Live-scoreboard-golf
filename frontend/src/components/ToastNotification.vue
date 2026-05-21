<template>
  <transition name="toast-fade">
    <div v-if="visible" class="toast-bar">
      {{ message }}
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')

const show = (msg) => {
  message.value = msg
  visible.value = true
  setTimeout(() => { visible.value = false }, 5000) 
}

defineExpose({ show })
</script>

<style scoped>
.toast-bar {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: #198754; /* Succes groen */
  color: white;
  padding: 12px 24px;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 9999;
  font-weight: bold;
}
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 0.5s, transform 0.5s; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(-20px); }
</style>