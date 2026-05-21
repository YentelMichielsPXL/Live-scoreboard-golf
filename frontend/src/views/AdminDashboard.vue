<template>
  <div class="d-block d-md-flex" style="min-height: 100vh;">
    
    <div class="bg-blue text-white p-3 shadow flex-shrink-0 d-none d-md-block" style="width: 235px; display: flex; flex-direction: column;">
      <h4 class="text-center mb-4 mt-2">
        <router-link to="/">
          <img src="/logo_golf_hasselt.png" alt="Logo golfclub Hasselt" width="150px">
        </router-link>
        <br><span class="fs-5">Admin Panel</span>
      </h4>
      
      <div class="text-center mb-4 pb-3 border-bottom border-light border-opacity-25">
        <small class="d-block text-white-50">Ingelogd als:</small>
        <strong>{{ currentUsername }}</strong> 
        <span class="badge bg-dark ms-1">{{ currentRole }}</span>
      </div>

      <ul class="nav flex-column mb-auto">
        <li class="nav-item mb-2">
          <router-link to="/admin/tournaments" class="nav-link text-white" active-class="selected rounded shadow-sm">
            🏆 Toernooien
          </router-link>
        </li>
        <li v-if="currentRole == 'admin'" class="nav-item mb-2">
          <router-link to="/admin/courses" class="nav-link text-white" active-class="selected rounded shadow-sm">
            ⛳ Banen Beheren
          </router-link>
        </li>
        <li v-if="currentRole === 'admin'" class="nav-item mb-2">
          <router-link to="/admin/users" class="nav-link text-white" active-class="selected rounded shadow-sm">
            👥 Gebruikers
          </router-link>
        </li>
        <li class="nav-item mt-4">
          <a href="/" target="_blank" class="nav-link text-warning fw-bold border border-warning border-opacity-50 rounded bg-dark bg-opacity-25 text-center">
            📺 Scorebord Openen
          </a>
        </li>
      </ul>

      <div class="mt-auto pt-5">
        <button @click="logout" class="btn btn-outline-light w-100 btn-sm">Uitloggen</button>
      </div>
    </div>

    <div class="flex-grow-1 p-3 p-md-5 bg-light">
      
      <div class="d-block d-md-none mb-4">
        
        <div class="d-flex justify-content-between align-items-center bg-white p-3 rounded shadow-sm border">
          <div class="d-flex align-items-center gap-3">
            <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="btn btn-light border shadow-sm px-2 py-1">
              <span class="fs-4" style="line-height: 1;">☰</span>
            </button>
            <div>
              <h5 class="text-dark fw-bold m-0">🏌️ Golf Panel</h5>
              <small class="text-muted">Scorer: <strong>{{ currentUsername }}</strong></small>
            </div>
          </div>
          <button @click="logout" class="btn btn-sm btn-outline-danger fw-bold py-1 px-2">
            Uitloggen
          </button>
        </div>

        <div v-if="isMobileMenuOpen" class="bg-white border rounded shadow-sm mt-2 p-2 animate-fade-in">
          <ul class="nav flex-column">
            <li class="nav-item mb-1">
              <router-link to="/admin/tournaments" @click="isMobileMenuOpen = false" class="nav-link text-dark fw-bold" active-class="bg-light rounded text-primary border-start border-primary border-4">
                🏆 Toernooien
              </router-link>
            </li>
            <li v-if="currentRole == 'admin'" class="nav-item mb-1">
              <router-link to="/admin/courses" @click="isMobileMenuOpen = false" class="nav-link text-dark fw-bold" active-class="bg-light rounded text-primary border-start border-primary border-4">
                ⛳ Banen Beheren
              </router-link>
            </li>
            <li v-if="currentRole === 'admin'" class="nav-item mb-2">
              <router-link to="/admin/users" @click="isMobileMenuOpen = false" class="nav-link text-dark fw-bold" active-class="bg-light rounded text-primary border-start border-primary border-4">
                👥 Gebruikers
              </router-link>
            </li>
            <li class="nav-item mt-2 border-top pt-2">
              <a href="/" target="_blank" @click="isMobileMenuOpen = false" class="nav-link text-warning-emphasis bg-warning bg-opacity-10 fw-bold border border-warning rounded text-center">
                📺 Scorebord Openen
              </a>
            </li>
          </ul>
        </div>

      </div>

      <router-view></router-view>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentRole = ref(sessionStorage.getItem('role') || 'scorer')
const currentUsername = ref(sessionStorage.getItem('username') || 'Onbekend')

const isMobileMenuOpen = ref(false)

const logout = () => {
  if(confirm("Weet je zeker dat je wilt uitloggen?")) {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('role')
    sessionStorage.removeItem('username')
    router.push('/login')
  }
}
</script>

<style scoped>
.bg-blue{
  background-color: rgb(43, 40, 223);
}

.selected{
  background-color: whitesmoke;
  color: black !important;
}

.animate-fade-in { 
  animation: fadeIn 0.2s ease-out; 
}

@keyframes fadeIn { 
  from { opacity: 0; transform: translateY(-5px); } 
  to { opacity: 1; transform: translateY(0); } 
}
</style>