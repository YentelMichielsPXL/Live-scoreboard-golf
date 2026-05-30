<template>
  <div>
    <div v-if="userRole == 'admin'"> 
      <h2 class="mb-4 text-success border-bottom pb-2">Toernooien Beheren</h2>
    </div>
    <div v-else>
      <h2 class="mb-4 text-success border-bottom pb-2">Scores Beheren</h2>
    </div>

    <div v-if="userRole === 'admin'" class="card shadow-sm mb-5 border-0">
      <div class="card-header bg-white font-weight-bold">Nieuw Toernooi Aanmaken</div>
      <div class="card-body">
        <form @submit.prevent="createTournament">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Toernooi Naam</label>
              <input v-model="newTournament.name" type="text" class="form-control" required placeholder="Bijv. Clubkampioenschap 2026" />
            </div>
            
            <div class="col-md-6">
              <label class="form-label">Datum</label>
              <input v-model="newTournament.date" type="date" class="form-control" required />
            </div>

            <div class="col-md-4">
              <label class="form-label">Selecteer Golfbaan</label>
              <select v-model="newTournament.course_id" class="form-select" required>
                <option value="" disabled>Kies een baan...</option>
                <option v-for="course in availableCourses" :key="course.id" :value="course.id">
                  {{ course.name }} ({{ course.num_holes }} holes)
                </option>
              </select>
            </div>

            <div class="col-md-4">
              <label class="form-label">Wedstrijd Formule</label>
              <select v-model="newTournament.format" class="form-select" required>
                <option value="stableford">Stableford</option>
                <option value="strokeplay">Strokeplay</option>
              </select>
            </div>

            <div class="col-md-4">
              <label class="form-label">Aantal Rondes</label>
              <select v-model="newTournament.num_rounds" class="form-select" required>
                <option :value="1">1 Ronde (18 holes)</option>
                <option :value="2">2 Rondes (36 holes)</option>
              </select>
            </div>

            <div v-if="newTournament.format === 'strokeplay'" class="col-md-4">
              <label class="form-label">Pas een Cut toe?</label>
              <div class="input-group">
                <div class="input-group-text">
                  <input v-model="newTournament.has_cut" class="form-check-input mt-0" type="checkbox">
                </div>
                <input v-model.number="newTournament.cut_percentage" type="number" class="form-control" placeholder="% dat doorgaat" min="1" max="99" :disabled="!newTournament.has_cut">
                <span class="input-group-text">%</span>
              </div>
            </div>

            <div class="col-12 mt-4">
              <button type="submit" class="btn btn-success px-4">Toernooi Aanmaken</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div class="row g-4">
      <div v-for="t in tournaments" :key="t.id" class="col-md-6">
        <div class="card shadow-sm border-0 h-100 border-start border-4" :class="t.is_public ? 'border-success' : 'border-secondary'">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title fw-bold text-dark">{{ t.name }}</h5>
              <div class="d-flex gap-2">
                <button v-if="userRole === 'admin'" @click="toggleVisibility(t)" class="btn btn-sm fw-bold shadow-sm" :class="t.is_public ? 'btn-success text-white' : 'btn-outline-secondary'">
                  {{ t.is_public ? '👁️ Zichtbaar' : '🙈 Verborgen' }}
                </button>
                <button v-if="userRole === 'admin'" @click="deleteTournament(t.id)" class="btn btn-sm btn-outline-danger shadow-sm">Verwijderen</button>
              </div>
            </div>
            
            <p class="text-muted mb-2">📅 {{ t.date || 'Geen datum' }} | 📍 {{ t.course?.name || 'Onbekende Baan' }}</p>
            
            <div class="mb-3">
              <span class="badge" :class="t.format === 'stableford' ? 'bg-primary' : 'bg-dark'">
                {{ t.format === 'stableford' ? 'Stableford' : 'Strokeplay' }}
              </span>
              <span class="badge bg-secondary ms-2">{{ t.num_rounds }} Ronde(s)</span>
              <span v-if="t.has_cut" class="badge bg-danger ms-2">Cut: Top {{ t.cut_percentage }}%</span>
            </div>

            <div class="d-flex justify-content-between align-items-center mt-4 pt-3 border-top">
              <span class="text-secondary small">Spelers geregistreerd: <strong>{{ t.players?.length || 0 }}</strong></span>
              <router-link :to="`/admin/tournaments/${t.id}/players`" class="btn btn-sm btn-dark fw-bold">
                👥 Spelers & Scores Beheren
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const tournaments = ref([])
const availableCourses = ref([])
const userRole = ref(sessionStorage.getItem('role') || 'scorer')

const API_URL = '/api/tournaments/'
const COURSES_API_URL = '/api/courses/'

const newTournament = ref({
  name: '',
  date: '',
  course_id: '',
  format: 'stableford',
  has_cut: false,
  cut_percentage: 75,
  num_rounds: 1,
  is_public: false
})

const fetchData = async () => {
  const resT = await fetch(API_URL)
  tournaments.value = await resT.json()
  const resC = await fetch(COURSES_API_URL)
  availableCourses.value = await resC.json()
}

const createTournament = async () => {
  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionStorage.getItem('token')}`
      },
      body: JSON.stringify(newTournament.value)
    })
    if (res.ok) {
      newTournament.value = { name: '', date: '', course_id: '', format: 'stableford', has_cut: false, cut_percentage: 75, num_rounds: 1, is_public: false }
      fetchData()
    } else {
      alert("Fout bij het aanmaken. Ben je wel admin?")
    }
  } catch (error) {
    console.error("Fout bij toevoegen toernooi:", error)
  }
}


const toggleVisibility = async (t) => {
  try {
    const res = await fetch(`${API_URL}${t.id}/visibility`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionStorage.getItem('token')}`
      },
      body: JSON.stringify({ is_public: !t.is_public })
    })
    if (res.ok) fetchData()
  } catch (error) {
    console.error("Fout bij aanpassen zichtbaarheid:", error)
  }
}

const deleteTournament = async (id) => {
  if(!confirm("Weet je zeker dat je dit toernooi wilt verwijderen?")) return
  try {
    const res = await fetch(`${API_URL}${id}`, { 
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${sessionStorage.getItem('token')}`
      }
    })
    if (res.ok) fetchData()
  } catch (error) {
    console.error("Fout bij verwijderen toernooi:", error)
  }
}

onMounted(() => {
  fetchData()
})
</script>