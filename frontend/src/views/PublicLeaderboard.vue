<template>
  <div class="leaderboard-wrapper py-4 text-white overflow-x-hidden" style="min-height: 100vh">
    <div class="container-fluid px-2 px-md-3">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center border-bottom border-secondary pb-3 mb-3 gap-2">
        
        <div class="w-100 w-md-auto mb-2 mb-md-0 d-flex align-items-center gap-3">
          <router-link to="/">
            <img src="/logo_golf_hasselt.png" alt="Logo Hasselt" width="100" class="img" />
          </router-link>

          <div class="d-flex flex-column align-items-start">
            <h4 class="scoreboard-title m-0 text-nowrap fs-5 fs-sm-4">
              {{ leaderboardData.tournament_name }}
            </h4>
            <div class="d-flex flex-wrap align-items-center gap-2 mt-1">
              <span class="badge bg-dark text-uppercase border border-secondary" style="font-size: 0.7rem">
                {{ leaderboardData.format }}
              </span>
              <span v-if="currentProjectedCut !== null"
                class="badge bg-danger text-uppercase border border-danger border-opacity-50 badge-pulse" style="
                  font-size: 0.7rem;
                  box-shadow: 0 0 10px rgba(220, 53, 69, 0.5);
                ">
                PROJ. CUT:
                <span class="fw-black fs-6 ms-1">{{ currentProjectedCut }}</span>
              </span>
            </div>
          </div>
        </div>

        <div class="d-flex flex-wrap align-items-center justify-content-between justify-content-md-end w-100 w-md-auto gap-2">
          <div class="d-flex align-items-center gap-1 bg-dark p-1 rounded border border-secondary">
            <div class="btn-group">
              <button @click="setTabManually('M')" class="btn btn-xs fw-bold border-0" :class="activeTab === 'M' ? 'btn-primary text-white' : 'btn-outline-light text-white-50'">
                MANNEN
              </button>
              <button @click="setTabManually('F')" class="btn btn-xs fw-bold border-0" :class="activeTab === 'F' ? 'btn-primary text-white' : 'btn-outline-light text-white-50'">
                VROUWEN
              </button>
            </div>
            <button @click="toggleAutoSwitch" class="btn btn-xs fw-bold border-0 ms-1 px-2" :class="isAutoSwitching ? 'btn-success text-white' : 'btn-outline-secondary text-muted'" title="Automatisch wisselen">
              <span>⏱️</span>
            </button>
          </div>

          <div v-if="leaderboardData.num_rounds > 1" class="bg-light p-1 rounded border border-secondary d-flex align-items-center">
            <button @click="selectRound(1)" class="btn btn-xs px-2 py-1 fw-bold border-0" style="font-size: 0.75rem" :class="viewRound === 1 ? 'btn-success' : 'btn-outline-light text-white bg-dark'">
              R1
            </button>
            <button @click="selectRound(2)" class="btn btn-xs px-2 py-1 fw-bold border-0 ms-1" style="font-size: 0.75rem" :class="viewRound === 2 ? 'btn-success' : 'btn-outline-light text-white bg-dark'">
              R2
            </button>
          </div>

          <span v-if="leaderboardData.is_active" class="badge bg-danger pulse-effect px-2 py-2 fw-bold text-nowrap" style="font-size: 0.8rem; letter-spacing: 0.5px">
            <span>🔴 LIVE</span>
          </span>
        </div>
      </div>

      <div class="shadow-lg rounded overflow-hidden border border-dark bg-black-card scoreboard-flex-container">
        
        <div class="scoreboard-side-block left-block">
          <table class="table table-custom m-0 text-center align-middle text-uppercase mobile-responsive-grid">
            <thead class="mobile-grid-header-hide">
              <tr class="header-main">
                <th class="cell-pos">POS</th>
                <th class="text-start ps-2 cell-player">PLAYER</th>
                <th class="text-warning-emphasis cell-metric">
                  {{ leaderboardData.format === "stableford" ? "POINTS" : "TO PAR" }}
                </th>
                <th class="d-none d-md-table-cell-custom cell-thru" style="width: 65px;">THRU</th>
                <th class="d-block d-md-none text-warning bg-black fw-black cell-tot">TOT</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in displayedRankings" :key="'left-' + row.player_id" class="leaderboard-row mobile-grid-row" :class="{'opacity-50 bg-black bg-opacity-25': row.status !== 'ACTIVE' && !row.isCutLine, 'cut-line-row': row.isCutLine}">
                <td v-if="row.isCutLine" :colspan="isMobileBrowser ? 4 : 5" class="p-0 border-0 align-middle cell-cutline">
                  <div class="bg-danger text-white fw-black px-2 d-flex align-items-center text-start h-100 w-100" style="font-size: 0.75rem; letter-spacing: 1px;">
                    ✂️ PROJ. CUT
                  </div>
                </td>
                <template v-else>
                  <td class="fw-bold text-warning fs-4 px-1 cell-pos">{{ row.pos }}</td>
                  <td class="text-start ps-2 py-1 cell-player" style="min-width: 0;">
                    <div class="player-name text-white fw-bold fs-5 text-truncate-custom">
                      {{ formatName(row.name) }}
                    </div>
                    <div class="handicap-sub text-white-50 style-small d-flex align-items-center gap-1" style="white-space: nowrap; overflow: hidden;">
                      <span>HCP: <span class="text-warning fw-bold">{{ row.handicap }}</span></span>
                      <span class="d-inline d-md-none badge bg-secondary text-white font-numeric py-0 px-1" style="font-size: 0.65rem;">T:{{ row.thru }}</span>
                    </div>
                  </td>
                  <td class="fw-bold fs-3 font-numeric p-1 cell-metric">
                    <span class="total-score-badge" :class="[getToParBadgeClass(row), getFontSizeClass(row)]">
                      {{ formatMainMetric(row) }}
                    </span>
                  </td>
                  <td class="text-white-50 font-numeric fw-bold fs-5 d-none d-md-table-cell-custom cell-thru">{{ row.thru }}</td>
                  <td class="p-1 d-block d-md-none cell-tot">
                    <span class="total-score-badge bg-black text-warning border border-secondary border-opacity-50 fw-black fs-4 d-flex align-items-center justify-content-center h-100 rounded py-1">
                      {{ row.total_strokes || "-" }}
                    </span>
                  </td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="scoreboard-middle-scroll custom-scrollbar d-none d-md-block">
          <table class="table table-custom m-0 text-center align-middle text-uppercase" :style="{ minWidth: (leaderboardData.holes.length * 50 + (leaderboardData.num_rounds > 1 ? 120 : 0)) + 'px' }">
            <thead>
              <tr class="header-main">
                <th v-for="h in leaderboardData.holes" :key="'h-' + h.hole_number" style="width: 50px;" class="hole-header">
                  <span class="fs-6 fw-bold text-white">{{ h.hole_number }}</span><br />
                  <small class="text-warning-emphasis">P{{ h.par }}</small><br />
                  <small class="text-warning-emphasis fw-bold" style="font-size: 0.55rem;">SI{{ h.stroke_index }}</small>
                </th>
                <template v-if="leaderboardData.num_rounds > 1">
                  <th style="width: 60px;" class="bg-dark-gray text-black border-start border-secondary">R1</th>
                  <th style="width: 60px;" class="bg-dark-gray text-black">R2</th>
                </template>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in displayedRankings" :key="'mid-' + row.player_id" class="leaderboard-row" :class="{'opacity-50 bg-black bg-opacity-25': row.status !== 'ACTIVE' && !row.isCutLine, 'cut-line-row': row.isCutLine}">
                <td v-if="row.isCutLine" :colspan="leaderboardData.holes.length + (leaderboardData.num_rounds > 1 ? 2 : 0)" class="p-0 border-0 align-middle">
                  <div class="bg-danger h-100 w-100"></div>
                </td>
                <template v-else>
                  <td v-for="h in leaderboardData.holes" :key="'score-' + h.hole_number" class="p-0 font-numeric fw-bold fs-5 border-inline-dark position-relative h-100">
                    <span :class="getHoleStyleClass(row.round_scores[viewRound]?.[h.hole_number], h.par)">
                      {{ row.round_scores[viewRound]?.[h.hole_number] || "-" }}
                    </span>
                    <span v-if="leaderboardData.format === 'stableford' && getHandicapStrokes(row.playing_hcp, h.stroke_index) > 0" class="text-warning position-absolute fw-black" style="font-size: 0.6rem; top: 15%; right: 3px;">
                      {{ "*".repeat(getHandicapStrokes(row.playing_hcp, h.stroke_index)) }}
                    </span>
                  </td>
                  <template v-if="leaderboardData.num_rounds > 1">
                    <td class="fs-5 text-white font-numeric fw-bold bg-dark-gray-rows py-1 border-start border-secondary h-100">
                      <div>{{ sumRound(row.round_scores[1]) }}</div>
                      <div v-if="sumRound(row.round_scores[1]) !== '-'" class="text-white-50 fw-normal" style="font-size: 0.65rem; line-height: 1;">
                        {{ getRoundToPar(row.round_scores[1]) }}
                      </div>
                    </td>
                    <td class="fs-5 text-white-50 font-numeric fw-bold bg-dark-gray-rows py-1 h-100">
                      <div>{{ sumRound(row.round_scores[2]) }}</div>
                      <div v-if="sumRound(row.round_scores[2]) !== '-'" class="text-white-50 fw-normal" style="font-size: 0.65rem; line-height: 1;">
                        {{ getRoundToPar(row.round_scores[2]) }}
                      </div>
                    </td>
                  </template>
                </template>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="scoreboard-side-block right-block d-none d-md-block">
          <table class="table table-custom m-0 text-center align-middle text-uppercase">
            <thead>
              <tr class="header-main">
                <th style="width: 75px;" class="text-warning bg-black fw-black">TOT</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in displayedRankings" :key="'right-' + row.player_id" class="leaderboard-row" :class="{'opacity-50 bg-black bg-opacity-25': row.status !== 'ACTIVE' && !row.isCutLine, 'cut-line-row': row.isCutLine}">
                <td v-if="row.isCutLine" class="p-0 border-0 align-middle">
                  <div class="bg-danger shadow-sm h-100 w-100"></div>
                </td>
                <template v-else>
                  <td class="p-2 bg-black bg-opacity-50 h-100">
                    <span class="total-score-badge bg-black text-warning border border-secondary border-opacity-25 fw-black fs-4 d-flex align-items-center justify-content-center h-100 rounded py-1">
                      {{ row.total_strokes || "-" }}
                    </span>
                  </td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from "vue";
import { useRouter } from "vue-router";
import { useTournamentStore } from "@/stores/tournamentStore";

const router = useRouter();
const store = useTournamentStore();

if (!store.selectedTournamentId) {
  router.push('/');
}

const tournamentId = store.selectedTournamentId;

const leaderboardData = ref({
  tournament_name: "",
  num_rounds: 1,
  holes: [],
  rankings_men: [],
  rankings_women: [],
  projected_cut_men: null,
  projected_cut_women: null,
});
const viewRound = ref(1);
const activeTab = ref("M");

let pollingInterval = null;
let autoSwitchTimer = null;
const isAutoSwitching = ref(false);
const hasManuallySelected = ref(false);

const isMobileBrowser = ref(false);
const checkScreenWidth = () => {
  isMobileBrowser.value = window.innerWidth < 768;
};

const formatName = (fullName) => {
  if (!fullName) return "";
  const parts = fullName.trim().split(/\s+/);
  if (parts.length <= 1) return fullName;
  const firstName = parts[0];
  const lastName = parts.slice(1).join(" "); 
  return `${firstName.charAt(0).toUpperCase()}. ${lastName}`;
};

const isCutApplied = computed(() => {
  const men = leaderboardData.value.rankings_men || [];
  const women = leaderboardData.value.rankings_women || [];
  return (
    men.some((p) => p.status === "CUT") || women.some((p) => p.status === "CUT")
  );
});

const displayedRankings = computed(() => {
  const rankings =
    activeTab.value === "M"
      ? leaderboardData.value.rankings_men
      : leaderboardData.value.rankings_women;
  if (isCutApplied.value) return rankings;

  const cutScore =
    activeTab.value === "M"
      ? leaderboardData.value.projected_cut_men
      : leaderboardData.value.projected_cut_women;
  if (cutScore === null || cutScore === undefined) return rankings;

  const format = leaderboardData.value.format;
  let cutIndex = -1;

  for (let i = 0; i < rankings.length; i++) {
    const row = rankings[i];
    if (row.status !== "ACTIVE" || row.total_strokes === null) {
      cutIndex = i;
      break;
    }

    const hasRound2Scores =
      row.round_scores?.[2] &&
      Object.values(row.round_scores[2]).some((strokes) => strokes > 0);
    if (hasRound2Scores) {
      continue;
    }

    if (format === "stableford") {
      if (row.total_stableford < cutScore) {
        cutIndex = i;
        break;
      }
    } else {
      if (row.total_to_par > cutScore) {
        cutIndex = i;
        break;
      }
    }
  }

  if (cutIndex !== -1) {
    const newArray = [...rankings];
    newArray.splice(cutIndex, 0, {
      isCutLine: true,
      player_id: "cut-line-marker-" + activeTab.value,
    });
    return newArray;
  }

  return rankings;
});

const currentProjectedCut = computed(() => {
  if (isCutApplied.value) return null;

  const val =
    activeTab.value === "M"
      ? leaderboardData.value.projected_cut_men
      : leaderboardData.value.projected_cut_women;
  if (val === null || val === undefined) return null;

  if (leaderboardData.value.format === "stableford") {
    return `${val} PT`;
  } else {
    if (val === 0) return "E";
    return val > 0 ? `+${val}` : val;
  }
});

const getRoundToPar = (scoresObj) => {
  if (!scoresObj || !leaderboardData.value.holes) return "-";
  let totalStrokes = 0;
  let totalPar = 0;
  let hasPlayed = false;

  leaderboardData.value.holes.forEach((h) => {
    const strokes = scoresObj[h.hole_number];
    if (strokes > 0) {
      totalStrokes += strokes;
      totalPar += h.par;
      hasPlayed = true;
    }
  });

  if (!hasPlayed) return "-";
  const diff = totalStrokes - totalPar;
  if (diff === 0) return "E";
  return diff > 0 ? `+${diff}` : `${diff}`;
};

const fetchLeaderboard = async () => {
  try {
    const res = await fetch(
      `/api/tournaments/${tournamentId}/leaderboard`
    );
    if (res.ok) {
      leaderboardData.value = await res.json();

      if (!hasManuallySelected.value && leaderboardData.value.num_rounds > 1) {
        const rankings = [
          ...(leaderboardData.value.rankings_men || []),
          ...(leaderboardData.value.rankings_women || []),
        ];
        const round2Started = rankings.some((p) => {
          const r2Scores = p.round_scores?.[2] || {};
          return Object.values(r2Scores).some((strokes) => strokes > 0);
        });
        if (round2Started) {
          viewRound.value = 2;
        }
      }
    }
  } catch (error) {
    console.error("Fout bij live verversen:", error);
  }
};

const toggleAutoSwitch = () => {
  isAutoSwitching.value = !isAutoSwitching.value;
  if (isAutoSwitching.value) {
    autoSwitchTimer = setInterval(() => {
      activeTab.value = activeTab.value === "M" ? "F" : "M";
    }, 10000);
  } else {
    clearInterval(autoSwitchTimer);
    autoSwitchTimer = null;
  }
};

const setTabManually = (tab) => {
  activeTab.value = tab;
  if (isAutoSwitching.value) {
    toggleAutoSwitch();
  }
};

const getHandicapStrokes = (playingHcp, si) => {
  if (!playingHcp || playingHcp <= 0 || !si) return 0;
  const baseExtra = Math.floor(playingHcp / 18);
  const remainder = playingHcp % 18;
  return baseExtra + (si <= remainder ? 1 : 0);
};

const selectRound = (roundNum) => {
  hasManuallySelected.value = true;
  viewRound.value = roundNum;
};

watch(viewRound, () => {
  fetchLeaderboard();
});

const formatMainMetric = (row) => {
  if (row.status !== "ACTIVE") return row.status;
  if (row.total_strokes === null || row.total_strokes === undefined) return "-";

  if (leaderboardData.value.format === "stableford") {
    return `${row.total_stableford} PT`;
  } else {
    if (row.total_to_par === 0) return "E";
    return row.total_to_par > 0 ? `+${row.total_to_par}` : row.total_to_par;
  }
};

const getFontSizeClass = (row) => {
  const text = formatMainMetric(row);
  const len = String(text).length;
  if (len <= 2) return "fs-3";
  if (len === 3 || len === 4) return "fs-5";
  return "fs-6";
};

const sumRound = (scoresObj) => {
  if (!scoresObj) return "-";
  const values = Object.values(scoresObj).filter((v) => v > 0);
  if (values.length === 0) return "-";
  return values.reduce((a, b) => a + b, 0);
};

const getToParBadgeClass = (row) => {
  if (row.status !== "ACTIVE") return "bg-secondary text-dark";
  if (row.total_strokes === null || row.total_strokes === undefined)
    return "bg-dark text-muted border border-secondary border-opacity-25";

  if (leaderboardData.value.format === "stableford") {
    return "bg-warning text-black fw-black";
  } else {
    if (row.total_to_par === 0) return "bg-success text-black";
    return row.total_to_par < 0 ? "bg-danger text-white" : "bg-warning text-black";
  }
};

const getHoleStyleClass = (strokes, par) => {
  if (!strokes || strokes === 0) return "text-muted-dash";
  const diff = strokes - par;
  if (diff === -1) return "score-birdie";
  if (diff <= -2) return "score-eagle";
  if (diff === 1) return "score-bogey";
  if (diff >= 2) return "score-double";
  return "score-par";
};

onMounted(() => {
  fetchLeaderboard();
  pollingInterval = setInterval(fetchLeaderboard, 10000);
  checkScreenWidth();
  window.addEventListener('resize', checkScreenWidth);
});

onUnmounted(() => {
  clearInterval(pollingInterval);
  if (autoSwitchTimer) clearInterval(autoSwitchTimer);
  window.removeEventListener('resize', checkScreenWidth);
});
</script>

<style scoped>
/* DE KLEUR AANPASSING IS VERWIJDERD: Het neemt weer netjes de kleur over van je eigen stijlen! */
.scoreboard-flex-container {
  display: flex;
  width: 100%;
}

.scoreboard-side-block {
  flex: 0 0 auto;
}

.left-block {
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.5);
  z-index: 5;
}

.right-block {
  box-shadow: -4px 0 10px rgba(0, 0, 0, 0.5);
  z-index: 5;
}

.scoreboard-middle-scroll {
  flex: 1 1 auto;
  overflow-x: auto !important;
}

.table-custom th {
  height: 85px !important;
  max-height: 85px !important;
  min-height: 85px !important;
  vertical-align: middle !important;
  box-sizing: border-box !important;
}

.table-custom tbody tr,
.table-custom tbody td {
  height: 65px !important;
  max-height: 65px !important;
  min-height: 65px !important;
  box-sizing: border-box !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  vertical-align: middle !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.text-truncate-custom {
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  display: block !important;
  max-width: 160px; 
}


/* --- OPTIMALISATIE VOOR SMARTPHONES --- */
@media (max-width: 767.98px) {
  .scoreboard-flex-container {
    display: block;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }
  .left-block {
    width: 100% !important;
    box-shadow: none !important;
  }

  .mobile-responsive-grid thead, 
  .mobile-responsive-grid tbody, 
  .mobile-responsive-grid tr {
    display: block !important;
    width: 100% !important;
  }

  .mobile-grid-header-hide {
    display: none !important;
  }

  .mobile-responsive-grid tbody tr {
    display: grid !important;
    grid-template-columns: 42px 1fr 75px 65px !important;
    align-items: center !important;
    height: auto !important; 
    min-height: 65px !important; 
    max-height: none !important; 
    padding: 10px 8px !important; 
    margin-bottom: 8px !important; 
    /* Gebruikt nu jouw eigen bg-black-card achtige kleur in plaats van een willekeurige zwarte tint */
    background-color: #12161f !important; 
    border: 1px solid rgba(255, 255, 255, 0.08) !important; 
    border-radius: 8px !important; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important; 
  }

  .table-custom td, .table-custom th {
    border-bottom: none !important; 
    padding: 4px 2px !important; 
    height: auto !important;
    max-height: none !important;
    min-height: auto !important;
  }

  .cell-pos    { grid-column: 1 !important; text-align: center !important; width: 100% !important; }
  .cell-player { grid-column: 2 !important; text-align: left !important; width: 100% !important; min-width: 0 !important; }
  .cell-metric { grid-column: 3 !important; text-align: center !important; width: 100% !important; }
  .cell-tot    { grid-column: 4 !important; text-align: center !important; width: 100% !important; }
  
  .cell-cutline {
    grid-column: 1 / span 4 !important;
    width: 100% !important;
    margin: 4px 0 !important;
    padding: 0 !important;
  }

  .text-truncate-custom {
    max-width: 100% !important;
  }
}

/* --- VANAF TABLET EN GROTER --- */
@media (min-width: 768px) {
  .d-none.d-md-table-cell-custom {
    display: table-cell !important;
  }
}

/* --- OPTIMALISATIE VOOR TV'S EN GROTE SCHERMEN --- */
@media (min-width: 1600px) {
  /* Alleen zoom toepassen. De wrapper pakt zelf de juiste hoogte nu `min-height: 100vh` inline staat */
  .leaderboard-wrapper {
    zoom: 0.8;
    min-height: 125vh !important; 
  }
}
</style>
<style src="../assets/styles/leaderboard.css"></style>