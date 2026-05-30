<template>
  <div>
    <ToastNotification ref="toast" />

    <h2 class="mb-4 text-success border-bottom pb-2">Golfbanen Beheren</h2>

    <div class="card shadow-sm mb-5 border-0" :class="{'border-top border-warning border-4': isEditing}">
      <div class="card-header bg-white font-weight-bold d-flex justify-content-between align-items-center">
        <span>{{ isEditing ? '⚠️ Golfbaan Gegevens Aanpassen' : 'Nieuwe Golfbaan Toevoegen' }}</span>
        <button v-if="isEditing" @click="cancelEdit" class="btn btn-sm btn-secondary">Annuleren</button>
      </div>
      <div class="card-body">
        <form @submit.prevent="submitCourse">
          <div class="row g-3 mb-4">
            <div class="col-md-3">
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
              <label class="form-label fw-bold text-primary">Mannen (CR / SR)</label>
              <div class="input-group">
                <input v-model.number="newCourse.course_rating_men" type="number" step="0.1" class="form-control" placeholder="CR" required />
                <input v-model.number="newCourse.slope_rating_men" type="number" min="55" max="155" class="form-control" placeholder="SR" required />
              </div>
            </div>
            <div class="col-md-3">
              <label class="form-label fw-bold text-danger">Vrouwen (CR / SR)</label>
              <div class="input-group">
                <input v-model.number="newCourse.course_rating_women" type="number" step="0.1" class="form-control" placeholder="CR" required />
                <input v-model.number="newCourse.slope_rating_women" type="number" min="55" max="155" class="form-control" placeholder="SR" required />
              </div>
            </div>
          </div>

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
                <tr v-for="i in 9" :key="i">
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

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white font-weight-bold">Beschikbare Banen</div>
      <div class="card-body p-0 table-responsive">
        <table class="table table-striped table-hover m-0">
          <thead class="table-dark">
            <tr>
              <th class="ps-4">Baan Naam</th>
              <th>Holes</th>
              <th>Mannen (CR/SR)</th>
              <th>Vrouwen (CR/SR)</th>
              <th class="text-end pe-4">Acties</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id" :class="{'table-warning': isEditing && editingId === course.id}">
              <td class="ps-4 align-middle fw-bold">{{ course.name }}</td>
              <td class="align-middle"><span class="badge bg-secondary">{{ course.num_holes }} Holes</span></td>
              <td class="align-middle text-primary fw-bold">{{ course.course_rating_men }} / {{ course.slope_rating_men }}</td>
              <td class="align-middle text-danger fw-bold">{{ course.course_rating_women }} / {{ course.slope_rating_women }}</td>
              <td class="text-end pe-4">
                <button @click="startEdit(course)" class="btn btn-sm btn-outline-warning me-2" :disabled="isEditing">Bewerken</button>
                <button @click="handleDelete(course.id)" class="btn btn-sm btn-outline-danger" :disabled="isEditing">Verwijderen</button>
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
import ToastNotification from '../components/ToastNotification.vue'

const { courses, fetchCourses, createCourse, deleteCourse, updateCourse } = useCourses()

const toast = ref(null)

const isEditing = ref(false)
const editingId = ref(null)

const newCourse = ref({
  name: '',
  num_holes: 18,
  course_rating_men: 72.0,
  slope_rating_men: 113,
  course_rating_women: 72.0,
  slope_rating_women: 113,
  holes: []
})

const generateHoleRows = () => {
  if (isEditing.value) return 
  newCourse.value.holes = Array.from({ length: newCourse.value.num_holes }, (_, i) => ({
    hole_number: i + 1,
    par: 4,
    stroke_index: i + 1
  }))
}

const startEdit = (course) => {
  isEditing.value = true
  editingId.value = course.id
  
  newCourse.value = {
    name: course.name,
    num_holes: course.num_holes,
    course_rating_men: course.course_rating_men,
    slope_rating_men: course.slope_rating_men,
    course_rating_women: course.course_rating_women,
    slope_rating_women: course.slope_rating_women,
    holes: [...course.holes].sort((a, b) => a.hole_number - b.hole_number)
  }
  
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const cancelEdit = () => {
  isEditing.value = false
  editingId.value = null
  resetForm()
}

const resetForm = () => {
  newCourse.value.name = ''
  newCourse.value.course_rating_men = 72.0
  newCourse.value.slope_rating_men = 113
  newCourse.value.course_rating_women = 72.0
  newCourse.value.slope_rating_women = 113
  isEditing.value = false
  editingId.value = null
  generateHoleRows()
}

const submitCourse = async () => {
  if (isEditing.value) {
    const success = await updateCourse(editingId.value, newCourse.value)
    if (success) {
      toast.value.show('Golfbaan succesvol bijgewerkt!')
      resetForm()
    } else {
      toast.value.show('Fout bij bijwerken van golfbaan.')
    }
  } else {
    const success = await createCourse(newCourse.value)
    if (success) {
      toast.value.show('Golfbaan succesvol toegevoegd!')
      resetForm()
    } else {
      toast.value.show('Fout bij toevoegen van golfbaan.')
    }
  }
}

const handleDelete = async (id) => {
  const success = await deleteCourse(id)
  if (success) {
    toast.value.show('Golfbaan succesvol verwijderd!')
  }
}

onMounted(() => {
  fetchCourses()
  generateHoleRows()
})
</script>