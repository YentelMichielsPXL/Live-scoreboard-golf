<template>
  <ToastNotification ref="Toast" />
  <div class="container d-flex flex-column justify-content-center align-items-center" style="min-height: 100vh;">
    <router-link to="/" class="mb-4">
      <img src="/logo_golf_hasselt.png" alt="Logo Hasselt" width="150" class="logo" />
    </router-link>
    <div>
      <h2>Golfclub Hasselt</h2>
    </div>
    <div class="card shadow border-0 p-4 bg-card" style="width: 100%; max-width: 400px;">
      <h3 class="text-center text-white mb-4">🔐 Golf App Login</h3>
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label class="form-label text-white">Gebruikersnaam</label>
          <input v-model="username" type="text" class="class form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label text-white">Wachtwoord</label>
          <input v-model="password" type="password" class="form-control" required />
        </div>
        <button type="submit" class="btn btn-success w-100 mt-2">Inloggen</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ToastNotification from '@/components/ToastNotification.vue'

const username = ref('')
const password = ref('')
const router = useRouter()
const Toast = ref(null)

const handleLogin = async () => {
  const res = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: username.value, password: password.value })
  })
  if (res.ok) {
    const user = await res.json()
    sessionStorage.setItem('token', user.token)
    sessionStorage.setItem('role', user.role)
    sessionStorage.setItem('username', user.username)
    router.push('/admin/tournaments')
  } else {
    console.log('Login failed:',  res.statusText)
    Toast.value.show('Fout bij inloggen. Controleer je gegevens en probeer het opnieuw.', 'danger')
  }
}
</script>

<style scoped>
.bg-card{
  background-color: rgb(13,13,170);
}
.logo{
  border: 3px solid black;
  border-radius: 15%;
  background-color: rgb(13, 13, 170);
  padding: 10px;
  
}

</style>