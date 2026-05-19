import { ref } from 'vue'

export function useCourses() {
  const courses = ref([])
  const API_URL = 'http://localhost:8000/courses/'

  const fetchCourses = async () => {
    try {
      const res = await fetch(API_URL)
      courses.value = await res.json()
    } catch (error) {
      console.error("Fout bij ophalen banen:", error)
    }
  }

  const createCourse = async (courseData) => {
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
         },
        body: JSON.stringify(courseData)
      })
      if (res.ok) {
        await fetchCourses()
        return true
      }
    } catch (error) {
      console.error("Fout bij aanmaken baan:", error)
      return false
    }
  }

  const deleteCourse = async (id) => {
    try {
      const res = await fetch(`${API_URL}${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      if (res.ok) await fetchCourses()
    } catch (error) {
      console.error("Fout bij verwijderen baan:", error)
    }
  }

  
  // Wijzig een bestaande baan
  const updateCourse = async (id, courseData) => {
    try {
      const res = await fetch(`${API_URL}${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
         },
        body: JSON.stringify(courseData)
      })
      if (res.ok) {
        await fetchCourses()
        return true
      }
    } catch (error) {
      console.error("Fout bij updaten baan:", error)
      return false
    }
  }
  return { courses, fetchCourses, createCourse, deleteCourse, updateCourse }
}