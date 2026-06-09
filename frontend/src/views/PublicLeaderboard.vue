<template>
  <div class="leaderboard-wrapper py-4 text-white overflow-x-hidden">
    <div class="container-fluid px-2 px-md-3">
      <!-- Top Bar met Toernooinaam en Knoppen -->
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
              
              <!-- Handmatige Paginering Knoppen -->
              <div v-if="totalPages > 1" class="d-inline-flex align-items-center gap-2 bg-dark px-2 py-1 rounded border border-secondary" style="font-size: 0.7rem; height: 26px;">
                <button @click="prevPage" class="btn btn-xs text-white p-0 px-1 border-0 fw-bold" :disabled="currentPage === 0" style="line-height: 1; opacity: currentPage === 0 ? 0.3 : 1;">
                  ◀
                </button>
                <span class="text-uppercase fw-bold text-white-50">PAGINA {{ currentPage + 1 }} / {{ totalPages }}</span>
                <button @click="nextPage" class="btn btn-xs text-white p-0 px-1 border-0 fw-bold" :disabled="currentPage + 1 === totalPages" style="line-height: 1; opacity: currentPage + 1 === totalPages ? 0.3 : 1;">
                  ▶
                </button>
              </div>
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
              <span>⏱️ {{ isAutoSwitching ? 'AAN' : 'UIT' }}</span>
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

          <span v-if="leaderboardData.is_live" class="badge bg-danger pulse-effect px-2 py-2 fw-bold text-nowrap" style="font-size: 0.8rem; letter-spacing: 0.5px">
            <span>🔴 LIVE</span>
          </span>
        </div>
      </div>

      <!-- DE VERDEELDE COMPACTE SCOREBORD LAYOUT -->
      <div class="shadow-lg rounded overflow-hidden border border-dark bg-black-card scoreboard-flex-container">
        
        <!-- BLOCK 1: LINKERKANT -->
        <div class="scoreboard-side-block left-block">
          
          <!-- Vaste Headers + Vaste Koplopers -->
          <table class="table table-custom left-fixed-table m-0 text-center align-middle text-uppercase mobile-responsive-grid" style="border-bottom: none !important;">
            <thead class="mobile-grid-header">
              <tr class="header-main">
                <th class="cell-pos"><div class="header-height-lock">POS</div></th>
                <th class="cell-player"><div class="header-height-lock justify-content-start ps-2">PLAYER</div></th>
                <th class="cell-metric text-warning-emphasis">
                  <div class="header-height-lock">{{ leaderboardData.format === "stableford" ? "PTS" : "TO PAR" }}</div>
                </th>
                <th class="d-none d-md-table-cell-custom cell-thru"><div class="header-height-lock">THRU</div></th>
                <th class="d-block d-md-none text-warning fw-black cell-tot"><div class="header-height-lock">TOT</div></th>
              </tr>
            </thead>
            <!-- AANGEPAST: transition-group is terug, lijn enkel als currentPage > 0 -->
            <transition-group tag="tbody" name="leaderboard-flip">
              <tr v-for="(row, idx) in stickyRankings" :key="'left-sticky-' + row.player_id" class="leaderboard-row mobile-grid-row sticky-leader-row" :class="{'sticky-leader-border': idx === stickyRankings.length - 1 && currentPage > 0}">
                <td class="fw-bold text-warning fs-4 cell-pos"><div class="cell-height-lock px-1">{{ row.pos }}</div></td>
                <td class="text-start ps-2 cell-player" style="min-width: 0;">
                  <div class="cell-height-lock flex-column justify-content-center align-items-start w-100" style="overflow: hidden;">
                    <div class="player-name text-white fw-bold fs-5 text-truncate-custom m-0 p-0 w-100">{{ formatName(row) }}</div>
                    <div class="handicap-sub text-white-50 small m-0 p-0 d-flex align-items-center gap-1 mt-1" style="font-size: 0.75rem; line-height: 1;">
                      <span>HCP: <span class="text-warning fw-bold">{{ row.handicap }}</span></span>
                    </div>
                  </div>
                </td>
                <td class="fw-bold fs-3 font-numeric cell-metric">
                  <div class="cell-height-lock px-1"><span class="total-score-badge" :class="[getToParBadgeClass(row), getFontSizeClass(row)]">{{ formatMainMetric(row) }}</span></div>
                </td>
                <td class="text-white-50 font-numeric fw-bold fs-5 d-none d-md-table-cell-custom cell-thru"><div class="cell-height-lock px-1">{{ row.thru }}</div></td>
                <td class="p-1 d-block d-md-none cell-tot"><div class="cell-height-lock px-1"><span class="total-score-badge text-warning border border-secondary border-opacity-50 fw-black fs-4 d-flex align-items-center justify-content-center h-100 w-100 rounded py-1" style="background-color: #0b2516;">{{ row.total_strokes || "-" }}</span></div></td>
              </tr>
            </transition-group>
          </table>

          <!-- Scrollend Venster met Achtervolgers -->
          <div :style="scrollWindowStyle">
            <table class="table table-custom left-fixed-table m-0 text-center align-middle text-uppercase mobile-responsive-grid" :style="scrollTableStyle">
              <!-- AANGEPAST: transition-group is terug -->
              <transition-group tag="tbody" name="leaderboard-flip">
                <tr v-for="row in scrollingRankings" :key="'left-scroll-' + row.player_id" class="leaderboard-row mobile-grid-row" :class="{'opacity-50 bg-general bg-opacity-25': row.status !== 'ACTIVE' && !row.isCutLine, 'cut-line-row': row.isCutLine}">
                  <td v-if="row.isCutLine" :colspan="isMobileBrowser ? 4 : 5" class="cell-cutline">
                    <div class="bg-danger text-white fw-black px-2 d-flex align-items-center text-start cell-height-lock w-100" style="font-size: 0.75rem; letter-spacing: 1px;">✂️ PROJ. CUT</div>
                  </td>
                  <template v-else>
                    <td class="fw-bold text-warning fs-4 cell-pos"><div class="cell-height-lock px-1">{{ row.pos }}</div></td>
                    <td class="text-start ps-2 cell-player" style="min-width: 0;">
                      <div class="cell-height-lock flex-column justify-content-center align-items-start w-100" style="overflow: hidden;">
                        <div class="player-name text-white fw-bold fs-5 text-truncate-custom m-0 p-0 w-100">{{ formatName(row) }}</div>
                        <div class="handicap-sub text-white-50 small m-0 p-0 d-flex align-items-center gap-1 mt-1" style="font-size: 0.75rem; line-height: 1;">
                          <span>HCP: <span class="text-warning fw-bold">{{ row.handicap }}</span></span>
                        </div>
                      </div>
                    </td>
                    <td class="fw-bold fs-3 font-numeric cell-metric">
                      <div class="cell-height-lock px-1"><span class="total-score-badge" :class="[getToParBadgeClass(row), getFontSizeClass(row)]">{{ formatMainMetric(row) }}</span></div>
                    </td>
                    <td class="text-white-50 font-numeric fw-bold fs-5 d-none d-md-table-cell-custom cell-thru"><div class="cell-height-lock px-1">{{ row.thru }}</div></td>
                    <td class="p-1 d-block d-md-none cell-tot"><div class="cell-height-lock px-1"><span class="total-score-badge text-warning border border-secondary border-opacity-50 fw-black fs-4 d-flex align-items-center justify-content-center h-100 w-100 rounded py-1" style="background-color: #0b2516;">{{ row.total_strokes || "-" }}</span></div></td>
                  </template>
                </tr>
              </transition-group>
            </table>
          </div>
        </div>

        <!-- BLOCK 2: SCROLLBARE MIDDENBOX -->
        <div class="scoreboard-middle-scroll custom-scrollbar d-none d-md-block">
          
          <!-- Vaste Headers + Vaste Koplopers -->
          <table class="table table-custom m-0 text-center align-middle text-uppercase" :style="{ minWidth: middleTableWidth + 'px', borderBottom: 'none !important' }">
            <thead>
              <tr class="header-main">
                <th v-for="h in leaderboardData.holes" :key="'h-' + h.hole_number" style="width: 50px;" class="hole-header">
                  <div class="header-height-lock flex-column lh-1">
                    <span class="fs-6 fw-bold text-white">{{ h.hole_number }}</span>
                    <small class="text-warning-emphasis mt-1" style="font-size: 0.6rem;">Par{{ h.par }}</small>
                    <small class="text-warning-emphasis fw-bold mt-1" style="font-size: 0.55rem;">SI{{ h.stroke_index }}</small>
                  </div>
                </th>
                <template v-if="leaderboardData.num_rounds > 1">
                  <th style="width: 60px;" class="bg-dark-gray text-black border-start border-secondary"><div class="header-height-lock">R1</div></th>
                  <th style="width: 60px;" class="bg-dark-gray text-black"><div class="header-height-lock">R2</div></th>
                </template>
              </tr>
            </thead>
            <!-- AANGEPAST: transition-group is terug, lijn enkel als currentPage > 0 -->
            <transition-group tag="tbody" name="leaderboard-flip">
              <tr v-for="(row, idx) in stickyRankings" :key="'mid-sticky-' + row.player_id" class="leaderboard-row sticky-leader-row" :class="{'sticky-leader-border': idx === stickyRankings.length - 1 && currentPage > 0}">
                <td v-for="h in leaderboardData.holes" :key="'score-s-' + h.hole_number" style="width: 50px; min-width: 50px; max-width: 50px;" class="font-numeric fw-bold fs-5 border-inline-dark position-relative p-0">
                  <div class="cell-height-lock position-relative w-100">
                    <span :class="getHoleStyleClass(row.round_scores[viewRound]?.[h.hole_number], h.par)">{{ row.round_scores[viewRound]?.[h.hole_number] || "-" }}</span>
                    <span v-if="leaderboardData.format === 'stableford' && getHandicapStrokes(row.playing_hcp, h.stroke_index) > 0" class="text-warning position-absolute fw-black" style="font-size: 0.55rem; top: 4px; right: 4px; line-height: 1;">{{ "*".repeat(getHandicapStrokes(row.playing_hcp, h.stroke_index)) }}</span>
                  </div>
                </td>
                <template v-if="leaderboardData.num_rounds > 1">
                  <td style="width: 60px; min-width: 60px; max-width: 60px;" class="fs-5 text-white font-numeric fw-bold bg-dark-gray-rows border-start border-secondary p-0">
                    <div class="cell-height-lock flex-column w-100" style="line-height: 1.15;">
                      <div>{{ sumRound(row.round_scores[1]) }}</div>
                      <div v-if="sumRound(row.round_scores[1]) !== '-'" class="text-white-50 fw-normal lh-1" style="font-size: 0.62rem;">{{ getRoundToPar(row.round_scores[1]) }}</div>
                    </div>
                  </td>
                  <td style="width: 60px; min-width: 60px; max-width: 60px;" class="fs-5 text-white-50 font-numeric fw-bold bg-dark-gray-rows p-0">
                    <div class="cell-height-lock flex-column w-100" style="line-height: 1.15;">
                      <div>{{ sumRound(row.round_scores[2]) }}</div>
                      <div v-if="sumRound(row.round_scores[2]) !== '-'" class="text-white-50 fw-normal lh-1" style="font-size: 0.62rem;">{{ getRoundToPar(row.round_scores[2]) }}</div>
                    </div>
                  </td>
                </template>
              </tr>
            </transition-group>
          </table>

          <!-- Scrollend Venster met Achtervolgers -->
          <div :style="scrollWindowStyle">
            <table class="table table-custom m-0 text-center align-middle text-uppercase" :style="[{ minWidth: middleTableWidth + 'px' }, scrollTableStyle]">
              <!-- AANGEPAST: transition-group is terug -->
              <transition-group tag="tbody" name="leaderboard-flip">
                <tr v-for="row in scrollingRankings" :key="'mid-scroll-' + row.player_id" class="leaderboard-row" :class="{'opacity-50 bg-general bg-opacity-25': row.status !== 'ACTIVE' && !row.isCutLine, 'cut-line-row': row.isCutLine}">
                  <td v-if="row.isCutLine" :colspan="leaderboardData.holes.length + (leaderboardData.num_rounds > 1 ? 2 : 0)">
                    <div class="bg-danger cell-height-lock w-100"></div>
                  </td>
                  <template v-else>
                    <td v-for="h in leaderboardData.holes" :key="'score-' + h.hole_number" style="width: 50px; min-width: 50px; max-width: 50px;" class="font-numeric fw-bold fs-5 border-inline-dark position-relative p-0">
                      <div class="cell-height-lock position-relative w-100">
                        <span :class="getHoleStyleClass(row.round_scores[viewRound]?.[h.hole_number], h.par)">{{ row.round_scores[viewRound]?.[h.hole_number] || "-" }}</span>
                        <span v-if="leaderboardData.format === 'stableford' && getHandicapStrokes(row.playing_hcp, h.stroke_index) > 0" class="text-warning position-absolute fw-black" style="font-size: 0.55rem; top: 4px; right: 4px; line-height: 1;">{{ "*".repeat(getHandicapStrokes(row.playing_hcp, h.stroke_index)) }}</span>
                      </div>
                    </td>
                    <template v-if="leaderboardData.num_rounds > 1">
                      <td style="width: 60px; min-width: 60px; max-width: 60px;" class="fs-5 text-white font-numeric fw-bold bg-dark-gray-rows border-start border-secondary p-0">
                        <div class="cell-height-lock flex-column w-100" style="line-height: 1.15;">
                          <div>{{ sumRound(row.round_scores[1]) }}</div>
                          <div v-if="sumRound(row.round_scores[1]) !== '-'" class="text-white-50 fw-normal lh-1" style="font-size: 0.62rem;">{{ getRoundToPar(row.round_scores[1]) }}</div>
                        </div>
                      </td>
                      <td style="width: 60px; min-width: 60px; max-width: 60px;" class="fs-5 text-white-50 font-numeric fw-bold bg-dark-gray-rows p-0">
                        <div class="cell-height-lock flex-column w-100" style="line-height: 1.15;">
                          <div>{{ sumRound(row.round_scores[2]) }}</div>
                          <div v-if="sumRound(row.round_scores[2]) !== '-'" class="text-white-50 fw-normal lh-1" style="font-size: 0.62rem;">{{ getRoundToPar(row.round_scores[2]) }}</div>
                        </div>
                      </td>
                    </template>
                  </template>
                </tr>
              </transition-group>
            </table>
          </div>

        </div>

        <!-- BLOCK 3: VASTE RECHTERKANT (DESKTOP) -->
        <div class="scoreboard-side-block right-block d-none d-md-block">
          
          <!-- Vaste Headers + Vaste Koplopers -->
          <table class="table table-custom m-0 text-center align-middle text-uppercase" style="border-bottom: none !important;">
            <thead>
              <tr class="header-main">
                <th style="width: 75px;"><div class="header-height-lock text-warning bg-black fw-black">TOT</div></th>
              </tr>
            </thead>
            <!-- AANGEPAST: transition-group is terug, lijn enkel als currentPage > 0 -->
            <transition-group tag="tbody" name="leaderboard-flip">
              <tr v-for="(row, idx) in stickyRankings" :key="'right-sticky-' + row.player_id" class="leaderboard-row sticky-leader-row" :class="{'sticky-leader-border': idx === stickyRankings.length - 1 && currentPage > 0}">
                <td style="width: 75px; min-width: 75px; max-width: 75px; background-color: rgba(11, 37, 22, 0.4);" class="p-0 h-100">
                  <div class="cell-height-lock p-2 w-100">
                    <span class="total-score-badge text-warning border border-secondary border-opacity-25 fw-black fs-4 d-flex align-items-center justify-content-center h-100 w-100 rounded py-1" style="background-color: #0b2516;">{{ row.total_strokes || "-" }}</span>
                  </div>
                </td>
              </tr>
            </transition-group>
          </table>

          <!-- Scrollend Venster met Achtervolgers -->
          <div :style="scrollWindowStyle">
            <table class="table table-custom m-0 text-center align-middle text-uppercase" :style="scrollTableStyle">
              <!-- AANGEPAST: transition-group is terug -->
              <transition-group tag="tbody" name="leaderboard-flip">
                <tr v-for="row in scrollingRankings" :key="'right-scroll-' + row.player_id" class="leaderboard-row" :class="{'opacity-50 bg-general bg-opacity-25': row.status !== 'ACTIVE' && !row.isCutLine, 'cut-line-row': row.isCutLine}">
                  <td v-if="row.isCutLine" style="width: 75px; min-width: 75px; max-width: 75px;" class="p-0 border-0 align-middle">
                    <div class="bg-danger shadow-sm cell-height-lock w-100"></div>
                  </td>
                  <template v-else>
                    <td style="width: 75px; min-width: 75px; max-width: 75px; background-color: rgba(11, 37, 22, 0.4);" class="p-0 h-100">
                      <div class="cell-height-lock p-2 w-100">
                        <span class="total-score-badge text-warning border border-secondary border-opacity-25 fw-black fs-4 d-flex align-items-center justify-content-center h-100 w-100 rounded py-1" style="background-color: #0b2516;">{{ row.total_strokes || "-" }}</span>
                      </div>
                    </td>
                  </template>
                </tr>
              </transition-group>
            </table>
          </div>

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
  is_live: false,
});
const viewRound = ref(1);
const activeTab = ref("M");

const currentPage = ref(0);
const itemsPerPage = ref(14); 

let pollingInterval = null;
let autoSwitchTimer = null;
const isAutoSwitching = ref(false);
const hasManuallySelected = ref(false);

const isMobileBrowser = ref(false);
const isDesktop = ref(true);

const checkScreenWidth = () => {
  isMobileBrowser.value = window.innerWidth < 768;
  isDesktop.value = window.innerWidth >= 1200;
};

const formatName = (row) => {
  if (row.first_name && row.last_name) {
    return `${row.first_name.charAt(0).toUpperCase()}. ${row.last_name}`;
  }
  if (!row.name) return "";
  const parts = row.name.trim().split(/\s+/);
  if (parts.length <= 1) return row.name;
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

const nobodyHasStarted = computed(() => {
  const men = leaderboardData.value.rankings_men || [];
  const women = leaderboardData.value.rankings_women || [];
  const allPlayers = [...men, ...women];
  
  if (allPlayers.length === 0) return true;
  
  return allPlayers.every(p => {
    return !p.thru || p.thru === 0 || p.thru === '-' || p.thru === '0';
  });
});

const currentStickyCount = computed(() => {
  if (nobodyHasStarted.value) return 0; 

  const total = displayedRankings.value.length;
  if (total <= itemsPerPage.value) return 0; 
  
  let count = 3; 
  const maxSticky = itemsPerPage.value - 4; 
  
  while (count < total && count < maxSticky) {
    const currentPos = displayedRankings.value[count - 1]?.pos;
    const nextPos = displayedRankings.value[count]?.pos;
    
    if (nextPos && currentPos && nextPos === currentPos && nextPos !== '-') {
      count++;
    } else {
      break;
    }
  }
  return count;
});

const stickyRankings = computed(() => {
  if (nobodyHasStarted.value) return [];
  return displayedRankings.value.slice(0, currentStickyCount.value);
});

const scrollingRankings = computed(() => {
  if (nobodyHasStarted.value) return displayedRankings.value;
  return displayedRankings.value.slice(currentStickyCount.value);
});

const totalPages = computed(() => {
  const scrollingCount = scrollingRankings.value.length;
  const slotsPerPage = itemsPerPage.value - currentStickyCount.value;
  if (scrollingCount === 0) return 1;
  return Math.ceil(scrollingCount / slotsPerPage);
});

const middleTableWidth = computed(() => {
  return leaderboardData.value.holes.length * 50 + (leaderboardData.value.num_rounds > 1 ? 120 : 0);
});

const ROW_HEIGHT = 53; // 52px celhoogte + 1px border

// AANGEPAST: Geen zwarte band meer. De hoogte past zich perfect aan de inhoud aan als er minder dan 14 spelers zijn.
const scrollWindowStyle = computed(() => {
  if (!isDesktop.value) return {};
  const slots = itemsPerPage.value - currentStickyCount.value;
  const actualRows = scrollingRankings.value.length;
  const visibleRows = Math.min(actualRows, slots);
  
  return {
    height: `${visibleRows * ROW_HEIGHT}px`,
    overflow: 'hidden',
    position: 'relative',
    display: 'block'
  };
});

const scrollTableStyle = computed(() => {
  if (!isDesktop.value) return {};
  
  const slots = itemsPerPage.value - currentStickyCount.value;
  let offset = currentPage.value * slots * ROW_HEIGHT;
  
  // Zorgt dat we nooit in het zwarte niets scrollen op de laatste pagina
  const totalScrollHeight = scrollingRankings.value.length * ROW_HEIGHT;
  const windowHeight = slots * ROW_HEIGHT;
  const maxOffset = Math.max(0, totalScrollHeight - windowHeight);
  
  offset = Math.min(offset, maxOffset);
  
  return {
    transform: `translateY(-${offset}px)`,
    transition: 'transform 1.2s ease-in-out' // TV-Kwaliteit soepele scroll animatie
  };
});

watch(activeTab, () => {
  currentPage.value = 0;
});

const nextPage = () => {
  if (isAutoSwitching.value) toggleAutoSwitch(); 
  if (currentPage.value + 1 < totalPages.value) {
    currentPage.value++;
  }
};

const prevPage = () => {
  if (isAutoSwitching.value) toggleAutoSwitch(); 
  if (currentPage.value > 0) {
    currentPage.value--;
  }
};

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
      // Loop door de pagina's
      if (currentPage.value + 1 < totalPages.value) {
        currentPage.value++;
      } else {
        // Geen pagina's meer? Ga naar pagina 1 van het andere geslacht
        currentPage.value = 0;
        activeTab.value = activeTab.value === "M" ? "F" : "M";
      }
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
    return `${row.total_stableford}`;
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
  pollingInterval = setInterval(fetchLeaderboard, 2000);
  checkScreenWidth();
  window.addEventListener('resize', checkScreenWidth);
  
  toggleAutoSwitch();
});

onUnmounted(() => {
  clearInterval(pollingInterval);
  if (autoSwitchTimer) clearInterval(autoSwitchTimer);
  window.removeEventListener('resize', checkScreenWidth);
});
</script>

<style scoped>
.leaderboard-wrapper {
  background-color: #0b2516; 
  min-height: 100vh;
}

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

/* TABLE BASIS SETTINGS */
.table-custom {
  border-collapse: separate !important; 
  border-spacing: 0 !important;
}

.table-custom th, .table-custom td {
  padding: 0 !important; 
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
  vertical-align: middle !important;
  box-sizing: border-box !important;
}

.table-custom thead th {
  border-bottom: 2px solid rgba(255, 255, 255, 0.2) !important;
}

/* --- TV & GROTE SCHERMEN OPTIMALISATIE --- */
@media (min-width: 1200px) {
  .leaderboard-wrapper {
    zoom: 1; 
  }
  
  .left-fixed-table {
    table-layout: fixed !important;
    width: 360px !important;
  }
  .cell-pos { width: 45px !important; }
  .cell-player { width: 175px !important; }
  .cell-metric { width: 75px !important; }
  .cell-thru { width: 65px !important; }

  .text-truncate-custom {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    display: block !important;
    max-width: 100% !important;
  }
  
  .table-custom th {
    height: 53px !important;
    line-height: 1.1 !important;
  }
  
  /* Hard-locked rij hoogtes inclusief border */
  .table-custom tbody tr {
    height: 53px !important;
    max-height: 53px !important;
  }

  .table-custom tbody td {
    height: 53px !important;
    max-height: 53px !important;
    padding: 0 !important; 
    vertical-align: middle !important;
    box-sizing: border-box !important;
  }

  .header-height-lock, .cell-height-lock {
    height: 52px !important; /* De binnenkant is 52px, de border is 1px */
    max-height: 52px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box !important;
  }

  .cell-height-lock span[class^="score-"] {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 32px !important;
    width: 32px !important;
    line-height: 1 !important;
    margin: 0 !important;
    flex-shrink: 0;
  }

  .player-name {
    font-size: 1.15rem !important;
    line-height: 1.2 !important;
  }

  .sticky-leader-row {
    background-color: rgba(255, 255, 255, 0.03) !important;
  }
  
  .sticky-leader-border td {
    border-bottom: 2px solid #ffc107 !important; 
  }
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

  .mobile-grid-header {
    display: block !important;
  }
  .mobile-grid-header .header-main {
    display: grid !important;
    grid-template-columns: 42px 1fr 75px 65px !important;
    align-items: center !important;
    padding: 4px !important; 
    margin-bottom: 4px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  }
  .mobile-grid-header th {
    display: block !important;
    padding: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    border: none !important;
    font-size: 0.75rem !important;
    color: rgba(255,255,255,0.6) !important;
  }

  .mobile-responsive-grid tbody tr {
    display: grid !important;
    grid-template-columns: 42px 1fr 75px 65px !important;
    align-items: center !important;
    height: auto !important; 
    min-height: 65px !important; 
    max-height: none !important; 
    padding: 4px !important; 
    margin-bottom: 6px !important; 
    background-color: rgba(255, 255, 255, 0.03) !important; 
    border: none !important; 
    border-radius: 6px !important; 
    box-shadow: none !important; 
  }

  .table-custom td {
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
</style>
<style src="../assets/styles/leaderboard.css"></style>