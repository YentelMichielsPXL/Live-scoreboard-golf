<template>
  <div class="container d-flex flex-column justify-content-center align-items-center" style="min-height: 80vh;">
    <div>
      <h2>Golfclub Hasselt</h2>
    </div>
    <div class="card shadow border-0 p-4 bg-card" style="width: 100%; max-width: 400px;">
      <h3 class="text-center text-success mb-4">🔐 Golf App Login</h3>
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

const username = ref('')
const password = ref('')
const router = useRouter()

const handleLogin = async () => {
  const res = await fetch(`http://${window.location.hostname}:8000/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: username.value, password: password.value })
  })
  if (res.ok) {
    const user = await res.json()
    localStorage.setItem('token', user.token)
    localStorage.setItem('role', user.role)
    localStorage.setItem('username', user.username)
    router.push('/admin/tournaments')
  } else {
    alert("Inloggen mislukt. Controleer uw gegevens.")
  }
}
</script>

<style scoped>
.bg-card{
  background-color: rgb(29, 27, 185);
}
</style>