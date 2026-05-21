import { createRouter, createWebHistory } from 'vue-router'
import AdminDashboard from '../views/AdminDashboard.vue'
import TournamentsAdmin from '../views/TournamentsAdmin.vue'
import CoursesAdmin from '../views/CoursesAdmin.vue'
import PlayersAdmin from '../views/PlayersAdmin.vue'
import PublicLeaderboard from '../views/PublicLeaderboard.vue'
import LoginView from '../views/LoginView.vue'
import UserAdmin from '@/views/UserAdmin.vue'
import Home from '@/views/Home.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: LoginView },
  { path: '/leaderboard/:tournament_id', component: PublicLeaderboard },
  { 
    path: '/admin', 
    component: AdminDashboard,
    children: [
      { path: 'tournaments', component: TournamentsAdmin },
      { path: 'courses', component: CoursesAdmin },
      { path: 'users', component: UserAdmin },
      { path: 'tournaments/:tournament_id/players', component: PlayersAdmin },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from) => {
  const isAuthenticated = !!sessionStorage.getItem('token')
  const userRole = sessionStorage.getItem('role')

  // Voorkom een oneindige lus bij de loginpagina
  if (to.path === '/login') {
    if (isAuthenticated) {
      // MODERN: We returnen direct de string in plaats van next('/...)
      return userRole === 'admin' ? '/admin/courses' : '/admin/tournaments'
    }
    return // Geen return betekent: doorgaan naar /login
  }

  // REGEL 1: Ben je NIET ingelogd en probeer je in het admin-gedeelte te komen?
  if (to.path.startsWith('/admin') && !isAuthenticated) {
    return '/login' // MODERN: Direct returnen naar waar ze heen moeten
  }

  // REGEL 2: GECORRIGEERD VOOR DE SCORER
  if (isAuthenticated && userRole === 'scorer') {
    if (to.path.startsWith('/admin/users') || to.path.startsWith('/admin/courses')) {
      alert("⛔ Toegang geweigerd: Alleen een administrator mag gebruikers of banen beheren.")
      return '/admin/tournaments' // MODERN: Direct terugsturen naar hun hub
    }
  }

  // MODERN: Als er aan geen enkele if-voorwaarde is voldaan, 
  // hoef je niks te returnen (of 'return true' te typen). De reis wordt automatisch goedgekeurd!
})

export default router