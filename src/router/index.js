import { createRouter, createWebHistory } from 'vue-router'
import { getCurrentUser } from 'aws-amplify/auth'

// Import views
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import UploadView from '../views/UploadView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global route guards with AWS Cognito authentication
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  
  if (requiresAuth) {
    try {
      // Check if user is authenticated with AWS Cognito
      const user = await getCurrentUser()
      console.log('Authenticated user:', user.username)
      next() // User is authenticated, proceed to route
    } catch (error) {
      console.log('User not authenticated, redirecting to login')
      next('/login') // User not authenticated, redirect to login
    }
  } else if (requiresGuest) {
    try {
      // Check if user is already authenticated
      const user = await getCurrentUser()
      console.log('User already authenticated, redirecting to dashboard')
      next('/') // User is already authenticated, redirect to dashboard
    } catch (error) {
      // User not authenticated, can access guest routes
      next()
    }
  } else {
    next() // Route doesn't require authentication, proceed
  }
})

export default router
