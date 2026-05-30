<template>
  <div class="home-wrapper py-5 text-white" style="min-height: 100vh;">
    <div class="container col-xxl-8 px-4">
      
      <!-- Top Navigatie met Admin Login Knop -->
      <div class="d-flex justify-content-between align-items-center mb-5 pb-3 border-bottom border-secondary border-opacity-25">
        <div class="d-flex align-items-center gap-2">
          <img src="../../public/logo_golf_hasselt.png" alt="Logo Hasselt" width="120" class="img-fluid" />
        </div>
        <router-link to="/login" class="btn btn-outline-dark btn-sm fw-bold px-3">
          🔒
        </router-link>
      </div>

      <!-- Hero Sectie -->
      <div class="row align-items-center g-5 py-4 mb-4">
        <div class="col-lg-12 text-center">
          <h1 class="display-4 fw-black scoreboard-title mb-3">LIVE SCORING</h1>
          <p class="lead text-white-50">Welkom bij het live scorebord van Golfclub Hasselt. Selecteer hieronder een actieve wedstrijd om de live tussenstanden te volgen, of bekijk de einduitslagen van voltooide toernooien.</p>
        </div>
      </div>

      <!-- Toernooien Overzicht -->
      <div class="row justify-content-center">
        <div class="col-lg-10">
          
          <!-- LADER -->
          <div v-if="loading" class="text-center py-5 text-white-50">
            <div class="spinner-border text-success mb-2" role="status"></div>
            <p>Wedstrijden ophalen...</p>
          </div>

          <div v-else>
            
            <!-- SECTIE 1: ACTIEVE WEDSTRIJDEN -->
            <h3 class="text-success fw-bold mb-4 border-start border-success border-4 ps-3">Actieve Wedstrijden</h3>
            
            <div v-if="activeTournaments.length === 0" class="card bg-black-card border border-secondary border-opacity-25 p-4 text-center rounded mb-5">
              <p class="text-warning-emphasis m-0">Er zijn momenteel geen actieve wedstrijden.</p>
            </div>
            
            <div v-else class="d-flex flex-column gap-3 mb-5">
              <div v-for="t in activeTournaments" :key="t.id" class="card bg-black-card border-0 shadow-lg border-start border-success border-4 tournament-card">
                <div class="card-body p-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
                  <div>
                    <h4 class="fw-bold text-white mb-1">{{ t.name }}</h4>
                    <div class="d-flex flex-wrap gap-2 text-white-50 small mt-2">
                      <span>📅 {{ t.date || 'Geen datum' }}</span>
                      <span>|</span>
                      <span>📍 {{ t.course?.name || 'Golf Hasselt' }}</span>
                      <span>|</span>
                      <span class="text-warning fw-bold text-uppercase">{{ t.format }}</span>
                    </div>
                  </div>
                  <div class="d-flex align-items-center gap-3 justify-content-between justify-content-md-end">
                    <span class="badge bg-danger pulse-effect px-3 py-2 fw-bold d-flex align-items-center justify-content-center" style="font-size: 0.75rem; height:40px;min-width: 100px;">🔴 LIVE</span>
                    <router-link :to="`/leaderboard/${t.id}`" class="btn btn-success fw-bold px-4 py-2 shadow-sm text-uppercase" style="font-size: 0.85rem;">
                      Bekijk Scorebord
                    </router-link>
                  </div>
                </div>
              </div>
            </div>

            <!-- SECTIE 2: AFGERONDE WEDSTRIJDEN (UITSLAGEN) -->
            <div v-if="completedTournaments.length > 0">
              <h3 class="text-secondary fw-bold mb-4 border-start border-secondary border-4 ps-3">Afgeronde Wedstrijden / Uitslagen</h3>
              
              <div class="d-flex flex-column gap-3">
                <div v-for="t in completedTournaments" :key="t.id" class="card bg-black-card opacity-75 border-0 shadow-sm border-start border-secondary border-4 tournament-card-completed">
                  <div class="card-body p-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
                    <div>
                      <h5 class="fw-bold text-white-50 mb-1">{{ t.name }}</h5>
                      <div class="d-flex flex-wrap gap-2 text-white-50 small mt-1">
                        <span>📅 {{ t.date || 'Geen datum' }}</span>
                        <span>|</span>
                        <span>📍 {{ t.course?.name || 'Golf Hasselt' }}</span>
                      </div>
                    </div>
                    <div class="d-flex align-items-center gap-3 justify-content-between justify-content-md-end">
                      <span class="badge bg-secondary text-dark fw-bold d-flex align-items-center justify-content-center" style="font-size: 0.85rem; height: 40px; min-width: 100px;">
                        VOLTOOID
                      </span>
                      <router-link :to="`/leaderboard/${t.id}`" class="btn btn-outline-secondary fw-bold px-4 text-uppercase d-flex align-items-center justify-content-center" style="font-size: 0.85rem; height: 40px;">
                        Bekijk Uitslag
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const tournaments = ref([])
const loading = ref(true)

const activeTournaments = computed(() => tournaments.value.filter(t => t.is_active && t.is_public))
const completedTournaments = computed(() => tournaments.value.filter(t => !t.is_active && t.is_public))

const fetchTournaments = async () => {
  try {
    const res = await fetch('tournaments/'')
    if (res.ok) {
      tournaments.value = await res.json()
    }
  } catch (error) {
    console.error("Fout bij ophalen toernooien op home:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTournaments()
})
</script>

<style scoped>
.home-wrapper { background-color: #0c0e12; }
.scoreboard-title { color: #ffffff; font-family: 'Arial Black', sans-serif; font-weight: 900; letter-spacing: 1px; }
.bg-black-card { background-color: #12161f; }
.fw-black { font-weight: 900; }

.tournament-card { transition: transform 0.2s ease, background-color 0.2s ease; }
.tournament-card:hover { transform: translateY(-2px); background-color: #171d29; }

.tournament-card-completed:hover { background-color: #1a1e26; }

.pulse-effect { animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
</style>