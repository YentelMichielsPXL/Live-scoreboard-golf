<template>
  <div>
    <div class="mb-3">
      <router-link to="/admin/tournaments" class="text-decoration-none text-secondary fw-bold">
        ← Terug naar Toernooi Overzicht
      </router-link>
    </div>
    <h2 class="mb-4 text-success border-bottom pb-2">Spelers & Scores Beheren</h2>

    <div v-if="userRole === 'admin' && tournamentDetails.has_cut" class="card shadow-sm mb-4 border-start border-danger border-4">
      <div class="card-header bg-white font-weight-bold text-danger d-flex justify-content-between align-items-center">
        <span>🛡️ Toernooi Cut Beheer (Huidige Instelling: {{ tournamentDetails.cut_percentage }}%)</span>
        <span v-if="cutPreview" class="badge bg-danger">Preview Actief</span>
      </div>
      <div class="card-body">
        <div class="d-flex align-items-center gap-2 mb-3 bg-light p-2 rounded border border-danger border-opacity-10" style="max-width: 480px;">
          <label class="form-label mb-0 small fw-bold text-dark text-nowrap">Cut Wijzigen naar:</label>
          <div class="input-group input-group-sm" style="width: 100px;">
            <input v-model.number="tournamentDetails.cut_percentage" type="number" min="1" max="99" class="form-control text-center fw-bold" />
            <span class="input-group-text">%</span>
          </div>
          <button @click="saveNewCutPercentage" class="btn btn-dark btn-sm fw-bold">Percentage Opslaan</button>
        </div>

        <div class="d-flex flex-wrap gap-2 align-items-center mb-2">
          <button @click="calculateCutPreview" class="btn btn-outline-danger btn-sm fw-bold">1. Bereken Cut Preview</button>
          <button @click="applyCutDefinitive" class="btn btn-danger btn-sm fw-bold">2. Pas Cut Definitief Toe</button>
          <button @click="removeCutDefinitive" class="btn btn-warning btn-sm fw-bold ms-auto text-dark">↩️ Cut Ongedaan Maken</button>
          <button v-if="cutPreview" @click="cutPreview = null" class="btn btn-link btn-sm text-secondary">Verberg Preview</button>
        </div>

        <div v-if="cutPreview" class="row g-3 pt-3 border-top border-light animate-fade-in">
          <div class="col-md-6">
            <div class="card border-success h-100 bg-success bg-opacity-10 text-success-emphasis">
              <div class="card-header bg-success text-white font-weight-bold py-1 small d-flex justify-content-between">
                <span>✅ GAAN DOOR</span>
                <span class="badge bg-white text-success fw-black">{{ cutPreview.will_survive_count }} spelers</span>
              </div>
              <div class="card-body p-2" style="max-height: 180px; overflow-y: auto;">
                <span v-for="name in cutPreview.safe_names" :key="name" class="badge bg-success text-white m-1 p-2 fs-6">🏌️ {{ name }}</span>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card border-danger h-100 bg-danger bg-opacity-10 text-danger-emphasis">
              <div class="card-header bg-danger text-white font-weight-bold py-1 small d-flex justify-content-between">
                <span>❌ VALLEN AF (CUT)</span>
                <span class="badge bg-white text-danger fw-black">{{ cutPreview.will_cut_count }} spelers</span>
              </div>
              <div class="card-body p-2" style="max-height: 180px; overflow-y: auto;">
                <span v-for="name in cutPreview.cut_names" :key="name" class="badge bg-danger text-white m-1 p-2 fs-6">❌ {{ name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="userRole === 'admin'" class="row g-4 mb-4 d-none d-md-flex">
      <div class="col-md-7">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white font-weight-bold">Handmatig Deelnemer Toevoegen</div>
          <div class="card-body">
            <form @submit.prevent="submitForm" class="row g-3 align-items-end">
              <div class="col-md-3">
                <label class="form-label">Voornaam</label>
                <input v-model="newPlayer.first_name" type="text" class="form-control form-control-sm" required />
              </div>
              <div class="col-md-3">
                <label class="form-label">Achternaam</label>
                <input v-model="newPlayer.last_name" type="text" class="form-control form-control-sm" required />
              </div>
              <div class="col-md-2">
                <label class="form-label">Geslacht</label>
                <select v-model="newPlayer.gender" class="form-select form-select-sm" required>
                  <option value="M">Man</option>
                  <option value="F">Vrouw</option>
                </select>
              </div>
              <div class="col-md-2">
                <label class="form-label">HCP</label>
                <input v-model.number="newPlayer.handicap" type="number" step="0.1" class="form-control form-control-sm" required />
              </div>
              <div class="col-12 text-end">
                <button type="submit" class="btn btn-sm btn-success px-4">Speler Opslaan</button>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div class="col-md-5">
        <div class="card shadow-sm border-0 h-100 bg-light">
          <div class="card-header bg-transparent font-weight-bold">Deelnemers via CSV inlezen</div>
          <div class="card-body d-flex flex-column justify-content-between">
            <small class="text-muted d-block mb-2">Vereiste kolommen: <strong>first_name, last_name, handicap, gender</strong> (M of V/F)</small>
            <div class="d-flex gap-2">
              <input type="file" ref="fileInput" @change="handleFileUpload" accept=".csv" class="form-control form-control-sm" />
              <button @click="submitCSV" :disabled="!csvFile" class="btn btn-sm btn-secondary">Uploaden</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mb-4 d-flex align-items-center justify-content-between bg-white p-3 rounded shadow-sm">
      <div>
        <label class="form-label fw-bold me-3 text-secondary mb-0">Actieve Invoer Ronde:</label>
        <div class="btn-group" role="group">
          <button @click="activeRound = 1" type="button" class="btn btn-sm" :class="activeRound == 1 ? 'btn-success' : 'btn-outline-success'">Ronde 1</button>
          <button v-if="tournamentDetails.num_rounds > 1" @click="activeRound = 2" type="button" class="btn btn-sm" :class="activeRound == 2 ? 'btn-success' : 'btn-outline-success'">Ronde 2</button>
        </div>
      </div>
      <span class="badge bg-warning text-dark px-3 py-2 fs-6 fw-bold">RONDE {{ activeRound }}</span>
    </div>

    <div class="mobile-wizard-container mb-4" :class="userRole === 'admin' ? 'd-block d-md-none' : 'd-block'">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-dark text-warning font-weight-bold">
          📱 Score Invoer (Mijn Flight)
        </div>
        <div class="card-body p-2 p-sm-3">
          <label class="form-label fw-bold text-secondary small mb-1">Stap 1: Stel je flight samen (max 3)</label>
          
          <div v-for="(id, index) in flightIds" :key="index" class="mb-2">
            <select v-model="flightIds[index]" class="form-select border-2 border-success fw-bold">
              <option :value="null">-- Kies Speler {{ index + 1 }} --</option>
              <option v-for="player in players" :key="player.id" :value="player.id">
                {{ player.gender === 'F' ? '👩‍🦰' : '🏌️' }} {{ player.first_name }} {{ player.last_name }} (Hcp: {{ player.handicap }})
              </option>
            </select>
          </div>

          <div v-if="selectedFlight.some(p => p !== null)" class="animate-fade-in border-top pt-3 mt-2">
            <label class="form-label fw-bold text-secondary small mb-2">Stap 2: Vul scores in voor Ronde {{ activeRound }}</label>
            
            <div class="table-responsive">
              <table class="table table-bordered text-center align-middle">
                <thead class="table-dark">
                  <tr>
                    <th style="width: 25%;">Hole</th>
                    <th v-for="(p, index) in selectedFlight" :key="'head'+index" v-show="p" style="width: 25%;">
                      <small>{{ p?.first_name }} {{ p?.last_name[0] }}</small>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="h in 18" :key="'hole'+h">
                    <td class="bg-light fw-bold font-numeric p-1">Hole {{ h }}</td>
                    <td v-for="(p, index) in selectedFlight" :key="'score'+index" v-show="p" class="p-1">
                      <input 
                        type="number" 
                        inputmode="numeric" 
                        pattern="[0-9]*" 
                        min="1" max="15" 
                        class="form-control text-center fw-black border-2 mx-auto"
                        style="font-size: 1.2rem; padding: 4px 0; max-width: 60px;"
                        :value="p ? getScore(p, activeRound, h) : ''"
                        @change="p ? saveHoleScore(p.id, h, $event.target.value) : null"
                        :disabled="p?.status !== 'ACTIVE'"
                        @focus="$event.target.select()"
                      />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <button @click="clearFlight" class="btn btn-outline-secondary w-100 mt-2">Flight Sluiten / Nieuwe Kiezen</button>

          </div>
        </div>
      </div>
    </div>

    <div v-if="userRole === 'admin'" class="d-none d-md-block">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <div class="btn-group bg-white p-1 rounded shadow-sm border">
          <button @click="activeGender = 'ALL'" class="btn btn-sm fw-bold" :class="activeGender === 'ALL' ? 'btn-primary' : 'btn-outline-secondary border-0'">
            🌍 ALLE
          </button>
          <button @click="activeGender = 'M'" class="btn btn-sm fw-bold" :class="activeGender === 'M' ? 'btn-primary' : 'btn-outline-secondary border-0'">
            👨 MANNEN
          </button>
          <button @click="activeGender = 'F'" class="btn btn-sm fw-bold" :class="activeGender === 'F' ? 'btn-primary' : 'btn-outline-secondary border-0'">
            👩‍🦰 VROUWEN
          </button>
        </div>
        <small class="text-muted fst-italic">Klik op de kolomkoppen om te sorteren</small>
      </div>

      <div class="card shadow-sm border-0">
        <div class="card-body p-0 table-responsive">
          <table class="table table-bordered table-striped align-middle m-0 text-center">
            <thead class="table-dark">
              <tr>
                <th @click="sortBy('name')" class="text-start ps-3" style="min-width: 180px; cursor: pointer;">
                  Speler <span v-if="sortKey === 'name'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th @click="sortBy('handicap')" style="min-width: 90px; cursor: pointer;">
                  HCP <span v-if="sortKey === 'handicap'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th @click="sortBy('status')" style="min-width: 150px; cursor: pointer;">
                  Status <span v-if="sortKey === 'status'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
                </th>
                <th v-for="h in 18" :key="h" style="width: 45px; min-width: 45px;">H{{ h }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="player in filteredAndSortedPlayers" :key="player.id" :class="{'table-danger text-muted opacity-50': player.status !== 'ACTIVE'}">
                <td class="text-start ps-3 table-light">
                  <div class="fw-bold">
                    {{ player.gender === 'F' ? '👩‍🦰' : '👨' }} {{ player.first_name }} {{ player.last_name }}
                    <span v-if="player.status === 'DQ'" class="badge bg-danger ms-1">DQ</span>
                    <span v-if="player.status === 'WD'" class="badge bg-warning text-dark ms-1">WD</span>
                    <span v-if="player.status === 'CUT'" class="badge bg-secondary ms-1 text-dark">CUT</span>
                  </div>
                  <small class="text-muted">{{ player.gender === 'M' ? 'Man' : 'Vrouw' }}</small>
                </td>
                
                <td class="fw-bold bg-light">
                  {{ player.handicap !== null ? player.handicap : '-' }}
                </td>

                <td class="p-2">
                  <div class="d-flex gap-1 align-items-center justify-content-center">
                    <select :value="player.status" @change="changePlayerStatus(player.id, $event.target.value)" class="form-select form-select-sm py-0" style="font-size: 0.8rem; height: 28px;">
                      <option value="ACTIVE">🟢 Speelt</option>
                      <option value="WD">🟡 WD</option>
                      <option value="DQ">🔴 DQ</option>
                      <option value="CUT">⚪ CUT</option>
                    </select>
                    <button @click="removePlayer(player.id)" class="btn btn-sm btn-outline-danger border-0 p-1">🗑️</button>
                  </div>
                </td>
                <td v-for="h in 18" :key="h" class="p-1">
                  <input 
                    type="number" 
                    min="1" max="15" 
                    class="form-control form-control-sm text-center px-0 fw-bold"
                    :value="getScore(player, activeRound, h)"
                    @change="saveHoleScore(player.id, h, $event.target.value)"
                    :disabled="player.status !== 'ACTIVE'"
                    @focus="$event.target.select()"
                  />
                </td>
              </tr>
              <tr v-if="filteredAndSortedPlayers.length === 0">
                <td colspan="21" class="text-muted py-4">Geen spelers gevonden in deze categorie.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, computed, watch } from 'vue'
import { usePlayers } from '../composables/usePlayers'

const userRole = ref(sessionStorage.getItem('role') || 'scorer')
const activeRound = ref(1)
const tournamentDetails = ref({ id: null, num_rounds: 1, has_cut: false, cut_percentage: 75 })
const cutPreview = ref(null)

const newPlayer = ref({ first_name: '', last_name: '', handicap: null, gender: 'M' })
const csvFile = ref(null)

const savedFlight = sessionStorage.getItem('active_flight')
const flightIds = ref(savedFlight ? JSON.parse(savedFlight) : [null, null, null])

// Sorteer- en filterstatussen
const activeGender = ref('ALL') // Start standaard op 'ALLE'
const sortKey = ref('handicap') 
const sortOrder = ref('asc')

watch(flightIds, (newFlight) => {
  sessionStorage.setItem('active_flight', JSON.stringify(newFlight))
}, { deep: true })
const playerComposable = shallowRef(null)

const players = computed(() => {
  const rawPlayers = playerComposable.value ? playerComposable.value.players.value : []
  return [...rawPlayers].sort((a, b) => {
    const hcpA = a.handicap !== null ? a.handicap : 99
    const hcpB = b.handicap !== null ? b.handicap : 99
    return hcpA - hcpB
  })
})

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const filteredAndSortedPlayers = computed(() => {
  // 1. Filter op 'ALL', 'M' of 'F'
  let result = activeGender.value === 'ALL' 
    ? [...players.value] 
    : players.value.filter(p => p.gender === activeGender.value)

  // 2. Sorteer de gefilterde lijst
  result.sort((a, b) => {
    let modifier = sortOrder.value === 'desc' ? -1 : 1
    let valA, valB

    if (sortKey.value === 'name') {
      valA = `${a.first_name} ${a.last_name}`.toLowerCase()
      valB = `${b.first_name} ${b.last_name}`.toLowerCase()
    } else if (sortKey.value === 'status') {
      valA = a.status || ''
      valB = b.status || ''
    } else {
      // Sorteer op handicap
      valA = a.handicap !== null ? a.handicap : 99
      valB = b.handicap !== null ? b.handicap : 99
    }

    if (valA < valB) return -1 * modifier
    if (valA > valB) return 1 * modifier
    return 0
  })

  return result
})

const clearFlight = () => {
  flightIds.value = [null, null, null]
  sessionStorage.removeItem('active_flight')
}

const selectedFlight = computed(() => {
  return flightIds.value.map(id => players.value?.find(p => p.id === id) || null)
})

const fetchActiveTournamentAndPlayers = async () => {
  const res = await fetch('/api/tournaments/active/metadata')
  if (res.ok) {
    tournamentDetails.value = await res.json()
    playerComposable.value = usePlayers(tournamentDetails.value.id)
    playerComposable.value.fetchPlayers()
  }
}

const changePlayerStatus = async (playerId, newStatus) => {
  const res = await fetch(`/api/tournaments/players/${playerId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${sessionStorage.getItem('token')}` },
    body: JSON.stringify({ status: newStatus })
  })
  if (res.ok) {
    playerComposable.value?.fetchPlayers()
    if (cutPreview.value) calculateCutPreview()
  }
}

const saveNewCutPercentage = async () => {
  const pct = parseInt(tournamentDetails.value.cut_percentage)
  if (isNaN(pct) || pct < 1 || pct > 99) return
  const res = await fetch(`/api/tournaments/${tournamentDetails.value.id}/update-cut`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cut_percentage: pct, has_cut: true })
  })
  if (res.ok && cutPreview.value) calculateCutPreview()
}

const calculateCutPreview = async () => {
  const res = await fetch(`/api/tournaments/${tournamentDetails.value.id}/cut-preview`)
  if (res.ok) cutPreview.value = await res.json()
}

const applyCutDefinitive = async () => {
  if (confirm("Cut toepassen?")) {
    const res = await fetch(`/api/tournaments/${tournamentDetails.value.id}/apply-cut`, { method: 'POST' })
    if (res.ok) { 
      cutPreview.value = null
      playerComposable.value?.fetchPlayers()
    }
  }
}

const removeCutDefinitive = async () => {
  if (confirm("Weet je zeker dat je de toegepaste cut ongedaan wilt maken? Alle spelers die 'CUT' als status hadden, worden weer 'ACTIVE'.")) {
    const res = await fetch(`/api/tournaments/${tournamentDetails.value.id}/remove-cut`, { 
      method: 'POST',
      headers: { 'Authorization': `Bearer ${sessionStorage.getItem('token')}` }
    })
    if (res.ok) { 
      cutPreview.value = null
      playerComposable.value?.fetchPlayers()
    }
  }
}

const getScore = (player, roundNum, holeNum) => {
  const match = player.scores?.find(s => s.round_number === roundNum && s.hole_number === holeNum)
  return match ? match.strokes : ''
}

const saveHoleScore = async (playerId, holeNum, strokes) => {
  const strokeCount = strokes === '' ? 0 : parseInt(strokes)
  if (isNaN(strokeCount) || strokeCount < 0) return
  const res = await fetch(`/api/scores/player/${playerId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${sessionStorage.getItem('token')}` },
    body: JSON.stringify({ hole_number: holeNum, strokes: strokeCount, round_number: activeRound.value })
  })
  if (res.ok) {
    playerComposable.value?.fetchPlayers()
    if (cutPreview.value) calculateCutPreview()
  }
}

const submitForm = async () => {
  if (!playerComposable.value) return
  const success = await playerComposable.value.addPlayer({ 
    first_name: newPlayer.value.first_name, 
    last_name: newPlayer.value.last_name, 
    handicap: newPlayer.value.handicap,
    gender: newPlayer.value.gender
  })
  if (success) newPlayer.value = { first_name: '', last_name: '', handicap: null, gender: 'M' }
}

const handleFileUpload = (event) => { csvFile.value = event.target.files[0] }

const submitCSV = async () => {
  if (!csvFile.value || !playerComposable.value) return
  await playerComposable.value.uploadCSV(csvFile.value)
  csvFile.value = null
}

const removePlayer = async (id) => { 
  if (confirm("Speler wissen?") && playerComposable.value) {
    await playerComposable.value.deletePlayer(id)
    flightIds.value = flightIds.value.map(fid => fid === id ? null : fid) 
  } 
}

onMounted(() => {
  fetchActiveTournamentAndPlayers()
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.25s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-3px); } to { opacity: 1; transform: translateY(0); } }
.font-numeric { font-family: Arial, sans-serif; }
.fw-black { font-weight: 900; }
.shadow-xs { box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
</style>