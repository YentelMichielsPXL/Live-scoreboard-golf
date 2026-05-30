import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTournamentStore = defineStore('tournament', () => {
  // Haal ID uit sessionStorage (voor als de pagina ververst wordt), of start met null
  const selectedTournamentId = ref(sessionStorage.getItem('current_tournament_id') || null)

  function setTournamentId(id) {
    selectedTournamentId.value = id
    // Sla het tijdelijk op in de browser tab, zodat F5 blijft werken
    sessionStorage.setItem('current_tournament_id', id)
  }

  function clearTournamentId() {
    selectedTournamentId.value = null
    sessionStorage.removeItem('current_tournament_id')
  }

  return { selectedTournamentId, setTournamentId, clearTournamentId }
})