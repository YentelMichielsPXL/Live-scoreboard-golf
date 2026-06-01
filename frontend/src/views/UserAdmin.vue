<template>
  <div>
    <h2 class="mb-4 text-success border-bottom pb-2">Gebruikers & Scorers Beheren</h2>

    <div class="row g-4">
      <div class="col-md-4">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-white font-weight-bold">Nieuwe Scorer Registreren</div>
          <div class="card-body">
            <form @submit.prevent="handleCreateUser" class="row g-3">
              <div class="col-12">
                <label class="form-label small fw-bold">Gebruikersnaam</label>
                <input v-model="newUser.username" type="text" class="form-control form-control-sm" required placeholder="bijv. johan_scorer" />
              </div>
              <div class="col-12">
                <label class="form-label small fw-bold">Wachtwoord</label>
                <input v-model="newUser.password" type="password" class="form-control form-control-sm" required placeholder="••••••••" />
              </div>
              <div class="col-12">
                <label class="form-label small fw-bold">Standaard Rol</label>
                <select v-model="newUser.role" class="form-select form-select-sm">
                  <option value="scorer">🟢 Scorer (Alleen scores invoeren)</option>
                  <option value="admin">🔴 Admin (Volledige controle)</option>
                </select>
              </div>
              <div class="col-12 text-end mt-4">
                <button type="submit" class="btn btn-sm btn-success w-100 fw-bold">Gebruiker Aanmaken</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-white font-weight-bold d-flex justify-content-between align-items-center">
            <span>Geregistreerde Systeemgebruikers</span>
            <span class="badge bg-secondary text-dark">{{ usersList.length }} Accounts</span>
          </div>
          <div class="card-body p-0 table-responsive">
            <table class="table table-striped align-middle m-0 text-center">
              <thead class="table-dark">
                <tr>
                  <th style="width: 70px;">ID</th>
                  <th class="text-start ps-3">Gebruikersnaam</th>
                  <th style="width: 160px;">Toezichthoudende Rol</th>
                  <th style="width: 130px;">Acties</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in usersList" :key="user.id">
                  <td class="text-muted small fw-bold">#{{ user.id }}</td>
                  <td class="text-start ps-3 fw-bold text-dark">
                    👤 {{ user.username }}
                  </td>
                  <td>
                    <select 
                      :value="user.role" 
                      @change="changeUserRole(user.id, $event.target.value)"
                      class="form-select form-select-sm py-0 mx-auto text-center fw-bold"
                      style="width: 130px; height: 28px; font-size: 0.8rem;"
                    >
                      <option value="scorer">🟢 Scorer</option>
                      <option value="admin">🔴 Admin</option>
                    </select>
                  </td>
                  <td>
                    <div class="d-flex justify-content-center gap-2">
                      <button 
                        @click="resetPassword(user.id, user.username)" 
                        class="btn btn-sm btn-outline-warning border-0 p-1"
                        title="Nieuw wachtwoord instellen"
                      >
                        🔑 Reset
                      </button>
                      <button 
                        @click="removeUser(user.id)" 
                        class="btn btn-sm btn-outline-danger border-0 p-1"
                        title="Verwijder account"
                      >
                        🗑️ Wissen
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="usersList.length === 0">
                  <td colspan="4" class="text-center text-muted py-4">Geen gebruikers gevonden.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router' 

const router = useRouter() 
const usersList = ref([])
const newUser = ref({ username: '', password: '', role: 'scorer' })

const fetchUsers = async () => {
  try {
    const res = await fetch(`/api/auth/allUsers`, { 
      headers: { 'Authorization': `Bearer ${sessionStorage.getItem('token')}` }
    })
    if (res.ok) {
      usersList.value = await res.json()
    }
  } catch (error) {
    console.error("Fout bij ophalen gebruikers:", error)
  }
}

const handleCreateUser = async () => {
  try {
    const res = await fetch(`/api/auth/register`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionStorage.getItem('token')}`
      },
      body: JSON.stringify(newUser.value)
    })
    
    if (res.ok) {
      newUser.value = { username: '', password: '', role: 'scorer' }
      fetchUsers()
    } else {
      const err = await res.json()
      alert(`🚨 Aanmaken mislukt: ${err.detail || 'Gebruikersnaam bestaat al.'}`)
    }
  } catch (error) {
    console.error("Fout bij aanmaken gebruiker:", error)
  }
}

const changeUserRole = async (userId, newRole) => {
  try {
    const res = await fetch(`/api/auth/updateRole/${userId}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionStorage.getItem('token')}`
      },
      body: JSON.stringify({ new_role: newRole }) 
    })
    
    if (res.ok) {
      const data = await res.json()
      
      if (data.is_self) {
        sessionStorage.setItem('role', data.new_role)
        alert("🔄 Je hebt je eigen rol gewijzigd naar Scorer. Je wordt direct doorverwezen naar de scorer-omgeving.")
        window.location.href = '/admin/tournaments' 
        return
      }
      
      fetchUsers()
    } else {
      const err = await res.json()
      alert(err.detail || "Kan rol niet aanpassen.")
      fetchUsers()
    }
  } catch (error) {
    console.error("Fout bij wijzigen rol:", error)
  }
}

// NIEUW: Functie om als Admin het wachtwoord van een gebruiker te forceren/resetten
const resetPassword = async (userId, username) => {
  const newPassword = prompt(`Vul een nieuw wachtwoord in voor de gebruiker '${username}':`);
  
  // Annuleren of leeg gelaten? Dan stoppen we.
  if (!newPassword || newPassword.trim() === '') return;

  try {
    const res = await fetch(`/api/auth/reset-password/${userId}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionStorage.getItem('token')}` 
      },
      body: JSON.stringify({ password: newPassword })
    })

    if (res.ok) {
      alert(`✅ Wachtwoord voor ${username} is succesvol gewijzigd!`);
    } else {
      const err = await res.json()
      alert(`🚨 Fout bij wijzigen: ${err.detail || 'Er ging iets mis.'}`)
    }
  } catch (error) {
    console.error("Fout bij resetten wachtwoord:", error)
  }
}

const removeUser = async (userId) => {
  if (!confirm("⚠️ Weet je zeker dat je dit account permanent wilt wissen?")) return
  try {
    const res = await fetch(`/api/auth/delete/${userId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${sessionStorage.getItem('token')}` }
    })
    if (res.ok) {
      fetchUsers()
    } else {
      const err = await res.json()
      alert(err.detail || "Kan gebruiker niet verwijderen.")
    }
  } catch (error) {
    console.error("Fout bij verwijderen gebruiker:", error)
  }
}

onMounted(() => {
  fetchUsers()
})
</script>