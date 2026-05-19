<template>
  <!-- GECORRIGEERD: d-block op mobiel, d-md-flex op grotere schermen -->
  <div class="d-block d-md-flex" style="min-height: 100vh;">
    
    <!-- ==================== SIDEBAR (Verdwijnt op GSM) ==================== -->
    <!-- GECORRIGEERD: d-none d-md-block toegevoegd -->
    <div class="bg-blue text-white p-3 shadow flex-shrink-0 d-none d-md-block" style="width: 235px; display: flex; flex-direction: column;">
      <h4 class="text-center mb-4 mt-2"><img src="../../public/logo_golf_hasselt.png" alt="Logo golfclub Hasselt" width="150px"> Admin Panel</h4>
      
      <!-- Toont wie er is ingelogd -->
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
      </ul>

      <!-- Uitlogknop onderaan -->
      <div class="mt-auto pt-5">
        <button @click="logout" class="btn btn-outline-light w-100 btn-sm">Uitloggen</button>
      </div>
    </div>

    <!-- ==================== MAIN CONTENT AREA ==================== -->
    <!-- GECORRIGEERD: p-3 op mobiel voor maximale ruimte, p-md-5 op desktop -->
    <div class="flex-grow-1 p-3 p-md-5 bg-light">
      
      <!-- NIEUW: Compacte Top-bar die ALLEEN op GSM te zien is -->
      <div class="d-flex d-md-none justify-content-between align-items-center mb-4 bg-white p-3 rounded shadow-sm border">
        <div>
          
          <h5 class="text-dark fw-bold m-0">🏌️ Golf Panel</h5>
          <small class="text-muted">Scorer: <strong>{{ currentUsername }}</strong></small>
        </div>
        <button @click="logout" class="btn btn-sm btn-outline-danger fw-bold py-1 px-2">
          Uitloggen
        </button>
      </div>

      <!-- Hier worden de subpagina's geladen -->
      <router-view></router-view>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentRole = ref(localStorage.getItem('role') || 'scorer')
const currentUsername = ref(localStorage.getItem('username') || 'Onbekend')

const logout = () => {
  if(confirm("Weet je zeker dat je wilt uitloggen?")) {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('username')
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
</style>