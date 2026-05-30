<template>
  <div
    class="leaderboard-wrapper py-4 text-white overflow-x-hidden"
    style="min-height: 100vh"
  >
    <div class="container-fluid px-2 px-md-3">
      <div
        class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center border-bottom border-secondary pb-3 mb-3 gap-2"
      >
        <div class="w-100 w-md-auto mb-2 mb-md-0">
          <h4
            class="scoreboard-title d-flex align-items-center m-0 text-nowrap fs-5 fs-sm-4 gap-2"
          >
            <router-link to="/">
              <span
                ><img
                  src="/logo_golf_hasselt.png"
                  alt="Logo Hasselt"
                  width="100"
                  class="img"
              /></span>
            </router-link>
            {{ leaderboardData.tournament_name }}
          </h4>
          <span
            class="badge bg-dark mt-1 text-uppercase border border-secondary"
            style="font-size: 0.7rem"
          >
            {{ leaderboardData.format }}
          </span>
          <span
            v-if="currentProjectedCut !== null"
            class="badge bg-danger mt-1 ms-2 text-uppercase border border-danger border-opacity-50 badge-pulse"
            style="
              font-size: 0.7rem;
              box-shadow: 0 0 10px rgba(220, 53, 69, 0.5);
            "
          >
            PROJ. CUT:
            <span class="fw-black fs-6 ms-1">{{ currentProjectedCut }}</span>
          </span>
        </div>

        <div
          class="d-flex flex-wrap align-items-center justify-content-between justify-content-md-end w-100 w-md-auto gap-2"
        >
          <div
            class="d-flex align-items-center gap-1 bg-dark p-1 rounded border border-secondary"
          >
            <div class="btn-group">
              <button
                @click="setTabManually('M')"
                class="btn btn-xs fw-bold border-0"
                :class="
                  activeTab === 'M'
                    ? 'btn-primary text-white'
                    : 'btn-outline-light text-white-50'
                "
              >
                MANNEN
              </button>
              <button
                @click="setTabManually('F')"
                class="btn btn-xs fw-bold border-0"
                :class="
                  activeTab === 'F'
                    ? 'btn-primary text-white'
                    : 'btn-outline-light text-white-50'
                "
              >
                VROUWEN
              </button>
            </div>
            <button
              @click="toggleAutoSwitch"
              class="btn btn-xs fw-bold border-0 ms-1 px-2"
              :class="
                isAutoSwitching
                  ? 'btn-success text-white'
                  : 'btn-outline-secondary text-muted'
              "
              title="Automatisch wisselen"
            >
              <span v-if="isAutoSwitching">⏱️</span>
              <span v-else>⏱️</span>
            </button>
          </div>

          <div
            v-if="leaderboardData.num_rounds > 1"
            class="bg-light p-1 rounded border border-secondary d-flex align-items-center"
          >
            <button
              @click="selectRound(1)"
              class="btn btn-xs px-2 py-1 fw-bold border-0"
              style="font-size: 0.75rem"
              :class="
                viewRound === 1
                  ? 'btn-success'
                  : 'btn-outline-light text-white bg-dark'
              "
            >
              R1
            </button>
            <button
              @click="selectRound(2)"
              class="btn btn-xs px-2 py-1 fw-bold border-0 ms-1"
              style="font-size: 0.75rem"
              :class="
                viewRound === 2
                  ? 'btn-success'
                  : 'btn-outline-light text-white bg-dark'
              "
            >
              R2
            </button>
          </div>

          <span
            v-if="leaderboardData.is_active"
            class="badge bg-danger pulse-effect px-2 py-2 fw-bold text-nowrap"
            style="font-size: 0.8rem; letter-spacing: 0.5px"
          >
            <span class="d-none d-sm-inline">🔴 LIVE</span>
            <span class="d-inline d-sm-none">🔴 LIVE</span>
          </span>
        </div>
      </div>

      <div
        class="shadow-lg rounded overflow-hidden border border-dark bg-black-card table-responsive custom-scrollbar"
      >
        <table
          class="table table-custom m-0 text-center align-middle text-uppercase"
        >
          <thead>
            <tr class="header-main">
              <th style="width: 50px">POS</th>
              <th class="text-start ps-3 ps-md-4" style="min-width: 180px">
                PLAYER
              </th>

              <th style="width: 90px" class="text-warning-emphasis">
                {{
                  leaderboardData.format === "stableford" ? "POINTS" : "TO PAR"
                }}
              </th>

              <th style="width: 65px">THRU</th>

              <th
                v-for="h in leaderboardData.holes"
                :key="h.hole_number"
                class="hole-header"
              >
                <span class="fs-6 fw-bold text-white">{{ h.hole_number }}</span
                ><br />
                <small class="text-warning-emphasis">Par{{ h.par }}</small
                ><br />
                <small
                  class="text-warning-emphasis fw-bold"
                  style="font-size: 0.6rem; letter-spacing: 0px"
                  >SI{{ h.stroke_index }}</small
                >
              </th>

              <th style="width: 65px" class="bg-dark-gray text-black">R1</th>
              <th
                v-if="leaderboardData.num_rounds > 1"
                style="width: 65px"
                class="bg-dark-gray text-black"
              >
                R2
              </th>
              <th style="width: 80px" class="text-warning bg-black fw-black">
                TOT
              </th>
            </tr>
          </thead>

          <transition-group
            tag="tbody"
            name="leaderboard-flip"
            :key="activeTab"
          >
            <tr
              v-for="row in displayedRankings"
              :key="row.player_id"
              class="leaderboard-row"
              :class="{
                'opacity-50 bg-black bg-opacity-25':
                  row.status !== 'ACTIVE' && !row.isCutLine,
                'cut-line-row': row.isCutLine,
              }"
            >
              <td
                v-if="row.isCutLine"
                colspan="100"
                class="p-0 border-0 align-middle"
              >
                <div class="d-flex align-items-center w-100">
                  <span
                    class="bg-danger text-white fw-black px-2 py-1"
                    style="font-size: 0.75rem; letter-spacing: 1px"
                    >✂️ PROJ. CUT</span
                  >
                  <div
                    class="flex-grow-1 bg-danger shadow-sm"
                    style="height: 3px; opacity: 0.9"
                  ></div>
                </div>
              </td>

              <template v-else>
                <td class="fw-bold text-warning fs-4 px-1">{{ row.pos }}</td>

                <td class="text-start ps-3 ps-md-4 py-2">
                  <div class="player-name text-white fw-bold fs-5">
                    {{ row.name }}
                    <span
                      v-if="row.status === 'CUT'"
                      class="badge bg-secondary ms-2 text-dark fw-bold fs-6"
                      >CUT</span
                    >
                  </div>
                  <div class="handicap-sub text-white-50 style-small">
                    HCP:
                    <span class="text-warning fw-bold">{{ row.handicap }}</span>
                    <span v-if="leaderboardData.format === 'stableford'">
                      | PHCP:
                      <span class="text-warning fw-bold">{{
                        row.playing_hcp
                      }}</span>
                    </span>
                  </div>
                </td>

                <td class="fw-bold fs-3 font-numeric p-2">
                  <span
                    class="total-score-badge"
                    :class="[getToParBadgeClass(row), getFontSizeClass(row)]"
                  >
                    {{ formatMainMetric(row) }}
                  </span>
                </td>

                <td class="text-white-50 font-numeric fw-bold fs-5">
                  {{ row.thru }}
                </td>

                <td
                  v-for="h in leaderboardData.holes"
                  :key="h.hole_number"
                  class="p-0 font-numeric fw-bold fs-5 border-inline-dark position-relative"
                  style="height: 44px"
                >
                  <span
                    :class="
                      getHoleStyleClass(
                        row.round_scores[viewRound]?.[h.hole_number],
                        h.par,
                      )
                    "
                  >
                    {{ row.round_scores[viewRound]?.[h.hole_number] || "-" }}
                  </span>
                  <span v-if="leaderboardData.format === 'stableford'">
                    <small
                      v-if="
                        getHandicapStrokes(row.playing_hcp, h.stroke_index) > 0
                      "
                      class="text-warning position-absolute fw-black"
                      style="
                        font-size: 0.65rem;
                        top: 25%;
                        right: 4px;
                        line-height: 1;
                        letter-spacing: -1px;
                      "
                    >
                      {{
                        "*".repeat(
                          getHandicapStrokes(row.playing_hcp, h.stroke_index),
                        )
                      }}
                    </small>
                  </span>
                </td>

                <td
                  class="fs-5 text-white font-numeric fw-bold bg-dark-gray-rows py-1"
                >
                  <div>{{ sumRound(row.round_scores[1]) }}</div>
                  <div
                    v-if="sumRound(row.round_scores[1]) !== '-'"
                    class="text-white-50 fw-normal"
                    style="font-size: 0.68rem; line-height: 1; margin-top: 1px"
                  >
                    {{ getRoundToPar(row.round_scores[1]) }}
                  </div>
                </td>

                <td
                  v-if="leaderboardData.num_rounds > 1"
                  class="fs-5 text-white-50 font-numeric fw-bold bg-dark-gray-rows py-1"
                >
                  <div>{{ sumRound(row.round_scores[2]) }}</div>
                  <div
                    v-if="sumRound(row.round_scores[2]) !== '-'"
                    class="text-white-50 fw-normal"
                    style="font-size: 0.68rem; line-height: 1; margin-top: 1px"
                  >
                    {{ getRoundToPar(row.round_scores[2]) }}
                  </div>
                </td>

                <td
                  class="fw-bold text-warning fs-4 font-numeric bg-black bg-opacity-50"
                >
                  {{ row.total_strokes || "-" }}
                </td>
              </template>
            </tr>
          </transition-group>
        </table>
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
      `/api/tournaments/${tournamentId}/leaderboard`,
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
    return row.total_to_par < 0
      ? "bg-danger text-white"
      : "bg-warning text-black";
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
});

onUnmounted(() => {
  clearInterval(pollingInterval);
  if (autoSwitchTimer) clearInterval(autoSwitchTimer);
});
</script>

<style src="../assets/styles/leaderboard.css"></style>
