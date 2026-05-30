import { ref } from 'vue'

export function usePlayers(tournamentId) {
  const players = ref([])
  // De URL is nu dynamisch gekoppeld aan het toernooi ID
  const API_URL = `/api/tournaments/${tournamentId}/players/`

  const fetchPlayers = async () => {
    try {
      const res = await fetch(API_URL)
      players.value = await res.json()
    } catch (error) {
      console.error("Fout bij ophalen spelers:", error)
    }
  }

  const addPlayer = async (playerData) => {
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(playerData)
      })
      if (res.ok) {
        await fetchPlayers()
        return true
      }
    } catch (error) {
      console.error("Fout bij toevoegen speler:", error)
      return false
    }
  }

  // Nieuw: Update de status (ACTIVE, DQ, WD) van een speler
  const updatePlayerStatus = async (playerId, status) => {
    try {
      const res = await fetch(`${API_URL}${playerId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: status })
      })
      if (res.ok) {
        await fetchPlayers()
      }
    } catch (error) {
      console.error("Fout bij aanpassen spelerstatus:", error)
    }
  }

  const uploadCSV = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await fetch(`${API_URL}upload-csv`, {
        method: 'POST',
        body: formData
      })
      if (res.ok) {
        await fetchPlayers()
        return true
      }
    } catch (error) {
      console.error("Fout bij uploaden CSV:", error)
      return false
    }
  }
  // Verwijder een speler uit het toernooi
  const deletePlayer = async (playerId) => {
    try {
      const res = await fetch(`${API_URL}${playerId}`, {
        method: 'DELETE'
      })
      if (res.ok) {
        await fetchPlayers() // Ververs de tabel direct
        return true
      }
    } catch (error) {
      console.error("Fout bij verwijderen speler:", error)
      return false
    }
  }

  return {
    players,
    fetchPlayers,
    addPlayer,
    updatePlayerStatus,
    uploadCSV,
    deletePlayer
  }
}