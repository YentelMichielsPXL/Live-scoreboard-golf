<template>
  <div>
    <h2 class="mb-4 text-success border-bottom pb-2">Golfbanen Beheren</h2>

    <!-- Baan Aanmaken / Bewerken Kaart -->
    <div class="card shadow-sm mb-5 border-0" :class="{'border-top border-warning border-4': isEditing}">
      <div class="card-header bg-white font-weight-bold d-flex justify-content-between align-items-center">
        <span>{{ isEditing ? '⚠️ Golfbaan Gegevens Aanpassen' : 'Nieuwe Golfbaan Toevoegen' }}</span>
        <button v-if="isEditing" @click="cancelEdit" class="btn btn-sm btn-secondary">Annuleren</button>
      </div>
      <div class="card-body">
        <form @submit.prevent="submitCourse">
          <!-- Algemene Baan Info -->
          <div class="row g-3 mb-4">
            <div class="col-md-4">
              <label class="form-label">Naam van de Golfbaan</label>
              <input v-model="newCourse.name" type="text" class="form-control" placeholder="Bijv. The International" required />
            </div>
            <div class="col-md-2">
              <label class="form-label">Aantal Holes</label>
              <select v-model="newCourse.num_holes" @change="generateHoleRows" class="form-select" :disabled="isEditing">
                <option :value="9">9 Holes</option>
                <option :value="18">18 Holes</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Course Rating (CR)</label>
              <input v-model.number="newCourse.course_rating" type="number" step="0.1" class="form-control" placeholder="Bijv. 72.4" required />
            </div>
            <div class="col-md-3">
              <label class="form-label">Slope Rating (SR)</label>
              <input v-model.number="newCourse.slope_rating" type="number" min="55" max="155" class="form-control" placeholder="Bijv. 113" required />
            </div>
          </div>

          <!-- Dynamische Hole Specificaties Tabel -->
          <h5 class="mb-3 text-secondary">Hole Specificaties (Par & Stroke Index)</h5>
          <div class="table-responsive mb-4" >
            <table class="table table-sm table-bordered align-middle text-center">
              <thead class="table-light sticky-top">
                <tr>
                  <th style="width: 10%;">Hole</th>
                  <th style="width: 20%;">Par</th>
                  <th style="width: 20%;">Stroke Index (SI)</th>
                  <th style="width: 10%;">Hole</th>
                  <th style="width: 20%;">Par</th>
                  <th style="width: 20%;">Stroke Index (SI)</th>
                </tr>
              </thead>
              <tbody>
      <!-- We lussen hier maar 9 keer (index 0 t/m 8) -->
      <tr v-for="i in 9" :key="i">
        
        <!-- LINKER KOLOM: Hole 1 t/m 9 (index i - 1) -->
        <template v-if="newCourse.holes[i - 1]">
          <td class="fw-bold bg-light">#{{ newCourse.holes[i - 1].hole_number }}</td>
          <td>
            <input v-model.number="newCourse.holes[i - 1].par" type="number" min="3" max="6" class="form-control form-control-sm text-center mx-auto" style="max-width: 100px;" required />
          </td>
          <td>
            <input v-model.number="newCourse.holes[i - 1].stroke_index" type="number" min="1" :max="newCourse.num_holes" class="form-control form-control-sm text-center mx-auto" style="max-width: 100px;" required />
          </td>
        </template>
        <template v-else>
          <td colspan="3" class="bg-light text-muted small">Nvt</td>
        </template>

        <!-- RECHTER KOLOM: Hole 10 t/m 18 (index i + 8) -->
        <template v-if="newCourse.holes[i + 8]">
          <td class="fw-bold bg-light">#{{ newCourse.holes[i + 8].hole_number }}</td>
          <td>
            <input v-model.number="newCourse.holes[i + 8].par" type="number" min="3" max="6" class="form-control form-control-sm text-center mx-auto" style="max-width: 100px;" required />
          </td>
          <td>
            <input v-model.number="newCourse.holes[i + 8].stroke_index" type="number" min="1" :max="newCourse.num_holes" class="form-control form-control-sm text-center mx-auto" style="max-width: 100px;" required />
          </td>
        </template>
        <template v-else>
          <!-- Lege cellen als de baan bijvoorbeeld maar 9 holes heeft -->
          <td class="fw-bold bg-light text-muted">-</td>
          <td><input type="number" class="form-control form-control-sm text-center mx-auto" style="max-width: 100px;" disabled /></td>
          <td><input type="number" class="form-control form-control-sm text-center mx-auto" style="max-width: 100px;" disabled /></td>
        </template>

      </tr>
    </tbody>
            </table>
          </div>

          <button type="submit" class="btn" :class="isEditing ? 'btn-warning text-dark' : 'btn-success'">
            {{ isEditing ? 'Wijzigingen Opslaan' : 'Baan & Holes Opslaan' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Bestaande Banen Lijst -->
    <div class="card shadow-sm border-0">
      <div class="card-header bg-white font-weight-bold">Beschikbare Banen</div>
      <div class="card-body p-0">
        <table class="table table-striped table-hover m-0">
          <thead class="table-dark">
            <tr>
              <th class="ps-4">Baan Naam</th>
              <th>Holes</th>
              <th>Course Rating (CR)</th>
              <th>Slope Rating (SR)</th>
              <th class="text-end pe-4">Acties</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id" :class="{'table-warning': isEditing && editingId === course.id}">
              <td class="ps-4 align-middle fw-bold">{{ course.name }}</td>
              <td class="align-middle"><span class="badge bg-secondary">{{ course.num_holes }} Holes</span></td>
              <td class="align-middle">{{ course.course_rating }}</td>
              <td class="align-middle">{{ course.slope_rating }}</td>
              <td class="text-end pe-4">
                <!-- BEWERK KNOP TOEGEVOEGD -->
                <button @click="startEdit(course)" class="btn btn-sm btn-outline-warning me-2" :disabled="isEditing">Bewerken</button>
                <button @click="deleteCourse(course.id)" class="btn btn-sm btn-outline-danger" :disabled="isEditing">Verwijderen</button>
              </td>
            </tr>
            <tr v-if="courses.length === 0">
              <td colspan="5" class="text-center text-muted py-4">Nog geen golfbanen aangemaakt.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCourses } from '../composables/useCourses'

const { courses, fetchCourses, createCourse, deleteCourse, updateCourse } = useCourses()

// State om bij te houden of we bewerken of aanmaken
const isEditing = ref(false)
const editingId = ref(null)

const newCourse = ref({
  name: '',
  num_holes: 18,
  course_rating: 72.0,
  slope_rating: 113,
  holes: []
})

const generateHoleRows = () => {
  if (isEditing.value) return // Voorkom overschrijven tijdens bewerken
  newCourse.value.holes = Array.from({ length: newCourse.value.num_holes }, (_, i) => ({
    hole_number: i + 1,
    par: 4,
    stroke_index: i + 1
  }))
}

// Activeer de bewerkmodus en laad de baandata in het formulier
const startEdit = (course) => {
  isEditing.value = true
  editingId.value = course.id
  
  // We maken een diepe kopie zodat we de originele lijst pas updaten na het opslaan
  newCourse.value = {
    name: course.name,
    num_holes: course.num_holes,
    course_rating: course.course_rating,
    slope_rating: course.slope_rating,
    // Sorteer de holes netjes op nummer zodat ze op volgorde staan in de tabel
    holes: [...course.holes].sort((a, b) => a.hole_number - b.hole_number)
  }
  
  // Scroll elegant omhoog naar het formulier
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const cancelEdit = () => {
  isEditing.value = false
  editingId.value = null
  resetForm()
}

const resetForm = () => {
  newCourse.value.name = ''
  newCourse.value.course_rating = 72.0
  newCourse.value.slope_rating = 113
  isEditing.value = false
  editingId.value = null
  generateHoleRows()
}

const submitCourse = async () => {
  if (isEditing.value) {
    // We zitten in bewerkmodus -> stuur PUT request
    const success = await updateCourse(editingId.value, newCourse.value)
    if (success) {
      alert("Golfbaan succesvol bijgewerkt!")
      resetForm()
    }
  } else {
    // We zitten in aanmaakmodus -> stuur POST request
    const success = await createCourse(newCourse.value)
    if (success) {
      alert("Golfbaan succesvol opgeslagen!")
      resetForm()
    }
  }
}

onMounted(() => {
  fetchCourses()
  generateHoleRows()
})
</script>