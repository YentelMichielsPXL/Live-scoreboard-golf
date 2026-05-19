<template>
  <div class="leaderboard-wrapper py-4 text-white overflow-x-hidden" style="min-height: 100vh;">
    <div class="container-fluid px-2 px-md-3">
      
      <!-- Header -->
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center border-bottom border-secondary pb-3 mb-3 gap-2">
        <div class="w-100 w-md-auto mb-2 mb-md-0">
          <h4 class="scoreboard-title d-flex align-items-center m-0 text-nowrap fs-5 fs-sm-4 gap-2">
            <span><img src="/logo_golf_hasselt.png" alt="Logo Hasselt" width="100" class="img"/></span> 
            {{ leaderboardData.tournament_name }}
          </h4>
          <span class="badge bg-dark mt-1 text-uppercase border border-secondary" style="font-size: 0.7rem;">
            {{ leaderboardData.format }}
          </span>
        </div>
        
        <!-- Ronde Details Kiezers & Live Badge -->
        <div class="d-flex align-items-center justify-content-between justify-content-md-end w-100 w-md-auto gap-2">
          <div v-if="leaderboardData.num_rounds > 1" class="bg-light p-1 rounded border border-secondary d-flex align-items-center">
            <button @click="selectRound(1)" class="btn btn-xs px-2 py-1 fw-bold border-0" style="font-size: 0.75rem;" :class="viewRound === 1 ? 'btn-success' : 'btn-outline-light text-white bg-dark'">R1</button>
            <button @click="selectRound(2)" class="btn btn-xs px-2 py-1 fw-bold border-0 ms-1" style="font-size: 0.75rem;" :class="viewRound === 2 ? 'btn-success' : 'btn-outline-light text-white bg-dark'">R2</button>
          </div>
          
          <span class="badge bg-danger pulse-effect px-2 py-2 fw-bold text-nowrap" style="font-size: 0.8rem; letter-spacing: 0.5px;">
            <span class="d-none d-sm-inline">🔴 LIVE</span>
            <span class="d-inline d-sm-none">🔴 LIVE</span>
          </span>
        </div>
      </div>

      <!-- Giga Scorebord Tabel -->
      <div class="shadow-lg rounded overflow-hidden border border-dark bg-black-card table-responsive custom-scrollbar">
        <table class="table table-custom m-0 text-center align-middle text-uppercase">
          <thead>
            <tr class="header-main">
              <th style="width: 50px;">POS</th>
              <th class="text-start ps-3 ps-md-4" style="min-width: 180px;">PLAYER</th>
              
              <th style="width: 90px;" class="text-warning-emphasis">
                {{ leaderboardData.format === 'stableford' ? 'POINTS' : 'TO PAR' }}
              </th>
              
              <th style="width: 65px;">THRU</th>
              
              <!-- 18 Holes overzicht headers -->
              <th v-for="h in leaderboardData.holes" :key="h.hole_number" class="hole-header">
                <span class="fs-6 fw-bold text-white">{{ h.hole_number }}</span><br>
                <small class="text-warning-emphasis">Par{{ h.par }}</small><br>
                <small class="text-warning-emphasis fw-bold" style="font-size: 0.6rem; letter-spacing: 0px;">SI{{ h.stroke_index }}</small>
              </th>

              <th style="width: 65px;" class="bg-dark-gray text-black">R1</th>
              <th v-if="leaderboardData.num_rounds > 1" style="width: 65px;" class="bg-dark-gray text-black">R2</th>
              <th style="width: 80px;" class="text-warning bg-black fw-black">TOT</th>
            </tr>
          </thead>
          
          <transition-group tag="tbody" name="leaderboard-flip">
            <tr v-for="row in leaderboardData.rankings" :key="row.player_id" class="leaderboard-row" :class="{'opacity-50 bg-black bg-opacity-25': row.status !== 'ACTIVE'}">
              <!-- Positie -->
              <td class="fw-bold text-warning fs-4 px-1">{{ row.pos }}</td>
              
              <!-- Naam & Handicaps -->
              <td class="text-start ps-3 ps-md-4 py-2">
                <div class="player-name text-white fw-bold fs-5">
                  {{ row.name }}
                  <span v-if="row.status === 'CUT'" class="badge bg-secondary ms-2 text-dark fw-bold fs-6">CUT</span>
                </div>
                <div class="handicap-sub text-white-50 style-small">
                  HCP: <span class="text-warning fw-bold">{{ row.handicap }}</span>
                  <span v-if="leaderboardData.format === 'stableford'">
                    | PHCP: <span class="text-warning fw-bold">{{ row.playing_hcp }}</span>
                  </span>
                </div>
              </td>
              
              <!-- Totale Tussenstand -->
              <td class="fw-bold fs-3 font-numeric p-2">
                <span 
                  class="total-score-badge" 
                  :class="[
                    getToParBadgeClass(row),
                    getFontSizeClass(row)
                  ]"
                >
                  {{ formatMainMetric(row) }}
                </span>
              </td>
              
              <!-- Thru -->
              <td class="text-white-50 font-numeric fw-bold fs-5">{{ row.thru }}</td>
              
              <!-- Live Hole per Hole kaart -->
              <td v-for="h in leaderboardData.holes" :key="h.hole_number" class="p-0 font-numeric fw-bold fs-5 border-inline-dark position-relative" style="height: 44px;">
                <!-- De score (of het streepje) -->
                <span :class="getHoleStyleClass(row.round_scores[viewRound]?.[h.hole_number], h.par)">
                  {{ row.round_scores[viewRound]?.[h.hole_number] || '-' }}
                </span>
                
                <!-- NIEUW: De subtiele handicap-indicator (*) rechtsboven in de cel -->
                <span v-if="leaderboardData.format === 'stableford'">
                  <small 
                    v-if="getHandicapStrokes(row.playing_hcp, h.stroke_index) > 0" 
                    class="text-warning position-absolute fw-black" 
                    style="font-size: 0.65rem; top: 25%; right: 4px; line-height: 1; letter-spacing: -1px;"
                  >
                    {{ '*'.repeat(getHandicapStrokes(row.playing_hcp, h.stroke_index)) }}
                  </small>
                </span>
              </td>
              
              <!-- R1 Totaal -->
              <td class="fs-5 text-muted-white font-numeric fw-bold bg-dark-gray-rows">{{ sumRound(row.round_scores[1]) }}</td>
              
              <!-- R2 Totaal -->
              <td v-if="leaderboardData.num_rounds > 1" class="fs-5 text-muted-white font-numeric fw-bold bg-dark-gray-rows">{{ sumRound(row.round_scores[2]) }}</td>
              
              <!-- Totaal aantal Slagen -->
              <td class="fw-bold text-warning fs-4 font-numeric bg-black bg-opacity-50">{{ row.total_strokes || '-' }}</td>
            </tr>
          </transition-group>
          
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const tournamentId = route.params.tournament_id || route.params.id || 1
const leaderboardData = ref({ tournament_name: '', num_rounds: 1, holes: [], rankings: [] })
const viewRound = ref(1)
let pollingInterval = null

const hasManuallySelected = ref(false)

const fetchLeaderboard = async () => {
  try {
    const res = await fetch(`http://${window.location.hostname}:8000/tournaments/${tournamentId}/leaderboard`)
    if (res.ok) {
      leaderboardData.value = await res.json()

      if (!hasManuallySelected.value && leaderboardData.value.num_rounds > 1) {
        const rankings = leaderboardData.value.rankings || []
        const round2Started = rankings.some(p => {
          const r2Scores = p.round_scores?.[2] || {}
          return Object.values(r2Scores).some(strokes => strokes > 0)
        })
          if (round2Started) {
            viewRound.value = 2
          }
        }
      }
    }
   catch (error) {
    console.error("Fout bij live verversen:", error)
  }
}

// NIEUW: Rekent live uit hoeveel extra slagen een specifieke speler op deze SI krijgt
const getHandicapStrokes = (playingHcp, si) => {
  if (!playingHcp || playingHcp <= 0 || !si) return 0
  const baseExtra = Math.floor(playingHcp / 18)
  const remainder = playingHcp % 18
  return baseExtra + (si <= remainder ? 1 : 0)
}

const selectRound = (roundNum) => {
  hasManuallySelected.value = true 
  viewRound.value = roundNum
}

watch(viewRound, () => {
  fetchLeaderboard()
})

const formatMainMetric = (row) => {
  if (row.status !== 'ACTIVE') return row.status
  if (row.thru === '-') return '-'
  
  if (leaderboardData.value.format === 'stableford') {
    return `${row.total_stableford} PT`
  } else {
    if (row.total_to_par === 0) return 'E'
    return row.total_to_par > 0 ? `+${row.total_to_par}` : row.total_to_par
  }
}

const getFontSizeClass = (row) => {
  const text = formatMainMetric(row)
  const len = String(text).length
  if (len <= 2) return 'fs-3'
  if (len === 3 || len === 4) return 'fs-5'
  return 'fs-6'
}

const sumRound = (scoresObj) => {
  if (!scoresObj) return '-'
  const values = Object.values(scoresObj).filter(v => v > 0)
  if (values.length === 0) return '-'
  return values.reduce((a, b) => a + b, 0)
}

const getToParBadgeClass = (row) => {
  if (row.status !== 'ACTIVE') return 'bg-secondary text-dark'
  if (row.thru === '-') return 'bg-dark text-muted border border-secondary border-opacity-25'
  
  if (leaderboardData.value.format === 'stableford') {
    return 'bg-warning text-black fw-black'
  } else {
    if (row.total_to_par === 0) return 'bg-success text-black'
    return row.total_to_par < 0 ? 'bg-danger text-white' : 'bg-warning text-black'
  }
}

const getHoleStyleClass = (strokes, par) => {
  if (!strokes || strokes === 0) return 'text-muted-dash'
  const diff = strokes - par
  if (diff === -1) return 'score-birdie'      
  if (diff <= -2) return 'score-eagle'       
  if (diff === 1) return 'score-bogey'        
  if (diff >= 2) return 'score-double'       
  return 'score-par'                         
}

onMounted(() => {
  fetchLeaderboard()
  pollingInterval = setInterval(fetchLeaderboard, 10000)
})

onUnmounted(() => {
  clearInterval(pollingInterval)
})
</script>

<style scoped>
:global(html), :global(body) {
  background-color: #0c0e12 !important;
  overflow-x: hidden;
}
.img{
  margin-bottom: 5px;
}
.fw-black {
  font-weight: 900;
}

.leaderboard-wrapper { background-color: #0b2516; overflow-x: hidden; }
.scoreboard-title { color: #ffffff; font-family: 'Arial Black', sans-serif; font-weight: 900; }
.font-numeric { font-family: 'Courier New', Courier, monospace; }
.bg-black-card { background-color: #12161f; }
.style-small { font-size: 0.72rem; }
.text-muted-white { color: #d1d5db; }
.text-muted-dash { color: #4b5563; }

.table-responsive {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table-custom { --bs-table-bg:#0b2516; background-color: #0b2516 !important; color: #ffffff !important; }
.table-custom th { background-color: #0b2516 !important; color: #ffc107 !important; padding: 6px 4px; font-size: 0.8rem; border-bottom: 2px solid #0c0e12 !important; }
.hole-header { width: 38px; min-width: 38px; font-size: 0.7rem; line-height: 1.2; }
.bg-dark-gray { background-color: #2d3545 !important; }
.bg-dark-gray-rows { background-color: #0b2516 !important; }
.border-inline-dark { border-left: 1px solid #1a202c; border-right: 1px solid #1a202c; }

.leaderboard-row { border-bottom: 1px solid #353536 !important; }

.total-score-badge { 
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 76px;                
  height: 34px;               
  font-weight: 900; 
  border-radius: 4px; 
  box-shadow: 0 2px 4px rgba(0,0,0,0.4); 
  overflow: hidden;
  white-space: nowrap;        
}

.leaderboard-flip-move {
  transition: transform 2.0s cubic-bezier(0.55, 0, 0.1, 1);
}

.leaderboard-row {
  transition: background-color 0.2s ease, transform 2s cubic-bezier(0.55, 0, 0.1, 1);
}

.score-birdie { background-color: #ff3b30; color: #ffffff; border-radius: 50%; display: inline-block; width: 26px; height: 26px; line-height: 26px; text-align: center; font-size: 0.85rem; }
.score-eagle { background-color: #ff9500; color: #000000; border-radius: 50%; display: inline-block; width: 26px; height: 26px; line-height: 26px; text-align: center; box-shadow: 0 0 0 2px #ff9500; font-weight: 900; font-size: 0.85rem; }
.score-bogey { background-color: #007aff; color: #ffffff; display: inline-block; width: 24px; height: 24px; line-height: 24px; text-align: center; border-radius: 2px; font-size: 0.85rem; }
.score-double { background-color: #5856d6; color: #ffffff; display: inline-block; width: 24px; height: 24px; line-height: 24px; text-align: center; border-radius: 2px; border: 1px solid #ffffff; font-size: 0.85rem; }
.score-par { color: #ffffff; display: inline-block; width: 26px; height: 26px; line-height: 26px; font-size: 0.9rem; }

.pulse-effect { animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
</style>