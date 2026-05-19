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

        <div class="d-flex gap-2 align-items-center mb-2">
          <button @click="calculateCutPreview" class="btn btn-outline-danger btn-sm fw-bold">1. Bereken Cut Preview</button>
          <button @click="applyCutDefinitive" class="btn btn-danger btn-sm fw-bold">2. Pas Cut Definitief Toe</button>
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
              <div class="col-md-4">
                <label class="form-label">Voornaam</label>
                <input v-model="newPlayer.first_name" type="text" class="form-control form-control-sm" required />
              </div>
              <div class="col-md-4">
                <label class="form-label">Achternaam</label>
                <input v-model="newPlayer.last_name" type="text" class="form-control form-control-sm" required />
              </div>
              <div class="col-md-4">
                <label class="form-label">Exact Handicap</label>
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
            <small class="text-muted d-block mb-2">Vereiste kolommen: <strong>first_name, last_name, handicap</strong></small>
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


    <div class="d-block d-md-none mobile-wizard-container mb-4">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-dark text-warning font-weight-bold">
          📱 Mobiele Score Invoer Wizard
        </div>
        <div class="card-body">
          <label class="form-label fw-bold text-secondary small mb-1">Stap 1: Kies een Deelnemer</label>
          <select v-model="selectedPlayerId" class="form-select form-select-lg mb-3 border-2 border-success fw-bold">
            <option :value="null">-- Tik hier om speler te kiezen --</option>
            <option v-for="player in players" :key="player.id" :value="player.id">
              🏌️ {{ player.first_name }} {{ player.last_name }} (Hcp: {{ player.handicap }})
            </option>
          </select>

          <div v-if="selectedPlayer" class="animate-fade-in border-top pt-3 mt-2">
            <div class="p-2 mb-3 bg-light rounded d-flex justify-content-between align-items-center border">
              <div>
                <strong class="text-dark fs-5 d-block">{{ selectedPlayer.first_name }} {{ selectedPlayer.last_name }}</strong>
                <small class="text-muted">Status: {{ selectedPlayer.status }}</small>
              </div>
              <button v-if="selectedPlayer" @click="selectedPlayerId = null" class="btn btn-xs btn-outline-secondary py-1">Sluiten</button>
            </div>

            <div v-if="selectedPlayer.status !== 'ACTIVE'" class="alert alert-warning text-center fw-bold small">
              ⚠️ Deze speler staat gemarkeerd als '{{ selectedPlayer.status }}' en is geblokkeerd.
            </div>

            <div v-else>
              <label class="form-label fw-bold text-secondary small mb-2">Stap 2: Vul scores in voor Ronde {{ activeRound }}</label>
              
              <div class="row g-2">
                <div v-for="h in 18" :key="h" class="col-4">
                  <div class="card text-center border-secondary shadow-xs">
                    <div class="card-header py-1 bg-dark text-white font-numeric small fw-bold">
                      Hole {{ h }}
                    </div>
                    <div class="card-body p-2 bg-white">
                      <input 
                        type="number" 
                        inputmode="numeric" 
                        pattern="[0-9]*" 
                        min="1" max="15" 
                        class="form-control form-control-lg text-center fw-black border-2"
                        style="font-size: 1.4rem; padding: 4px 0;"
                        :value="getScore(selectedPlayer, activeRound, h)"
                        @change="saveHoleScore(selectedPlayer.id, h, $event.target.value)"
                        @focus="$event.target.select()"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>


    <div class="card shadow-sm border-0 d-none d-md-block">
      <div class="card-body p-0 table-responsive">
        <table class="table table-bordered table-striped align-middle m-0 text-center">
          <thead class="table-dark">
            <tr>
              <th class="text-start ps-3" style="min-width: 200px;">Speler</th>
              <th v-if="userRole === 'admin'" style="min-width: 160px;">Status / Acties</th>
              <th v-for="h in 18" :key="h" style="width: 45px; min-width: 45px;">H{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="player in players" :key="player.id" :class="{'table-danger text-muted opacity-50': player.status !== 'ACTIVE'}">
              <td class="text-start ps-3 table-light">
                <div class="fw-bold">
                  {{ player.first_name }} {{ player.last_name }}
                  <span v-if="player.status === 'DQ'" class="badge bg-danger ms-1">DQ</span>
                  <span v-if="player.status === 'WD'" class="badge bg-warning text-dark ms-1">WD</span>
                  <span v-if="player.status === 'CUT'" class="badge bg-secondary ms-1 text-dark">CUT</span>
                </div>
                <small class="text-muted">Hcp: {{ player.handicap }}</small>
              </td>
              <td v-if="userRole === 'admin'" class="p-2">
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
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, computed } from 'vue'
import { usePlayers } from '../composables/usePlayers'

const userRole = ref(localStorage.getItem('role') || 'scorer')
const activeRound = ref(1)
const tournamentDetails = ref({ id: null, num_rounds: 1, has_cut: false, cut_percentage: 75 })
const cutPreview = ref(null)

// Invoervelden & Selecties
const newPlayer = ref({ first_name: '', last_name: '', handicap: null })
const csvFile = ref(null)
const selectedPlayerId = ref(null)

const playerComposable = shallowRef(null)

// Spelerslijst computed tracker
const players = computed(() => {
  return playerComposable.value ? playerComposable.value.players.value : []
})

// Berekent live welke speler momenteel is aangeklikt in de gsm-lijst
const selectedPlayer = computed(() => {
  return players.value?.find(p => p.id === selectedPlayerId.value)
})

// GECORRIGEERD: Vanaf hier zijn alle 'localhost' links vervangen door ${window.location.hostname}

const fetchActiveTournamentAndPlayers = async () => {
  const res = await fetch(`http://${window.location.hostname}:8000/tournaments/active/metadata`)
  if (res.ok) {
    tournamentDetails.value = await res.json()
    playerComposable.value = usePlayers(tournamentDetails.value.id)
    playerComposable.value.fetchPlayers()
  }
}

const changePlayerStatus = async (playerId, newStatus) => {
  const res = await fetch(`http://${window.location.hostname}:8000/tournaments/players/${playerId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
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
  const res = await fetch(`http://${window.location.hostname}:8000/tournaments/${tournamentDetails.value.id}/update-cut`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cut_percentage: pct, has_cut: true })
  })
  if (res.ok && cutPreview.value) calculateCutPreview()
}

const calculateCutPreview = async () => {
  const res = await fetch(`http://${window.location.hostname}:8000/tournaments/${tournamentDetails.value.id}/cut-preview`)
  if (res.ok) cutPreview.value = await res.json()
}

const applyCutDefinitive = async () => {
  if (confirm("Cut toepassen?")) {
    const res = await fetch(`http://${window.location.hostname}:8000/tournaments/${tournamentDetails.value.id}/apply-cut`, { method: 'POST' })
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
  const res = await fetch(`http://${window.location.hostname}:8000/scores/player/${playerId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
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
    handicap: newPlayer.value.handicap 
  })
  if (success) newPlayer.value = { first_name: '', last_name: '', handicap: null }
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