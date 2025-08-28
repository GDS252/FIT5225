<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
    <div class="container-fluid">
      <!-- Logo和品牌名称 -->
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <i class="bi bi-camera-fill me-2 fs-3"></i>
        <span class="fw-bold">Bird Recognition System</span>
      </router-link>

      <!-- 移动端切换按钮 -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- 导航菜单 -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/" active-class="active">
              <i class="bi bi-house-fill me-1"></i>
              Dashboard
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/upload" active-class="active">
              <i class="bi bi-cloud-upload-fill me-1"></i>
              Upload Files
            </router-link>
          </li>
        </ul>

        <!-- User Info and Actions -->
        <div class="navbar-nav">
          <div class="nav-item dropdown">
            <a
              class="nav-link dropdown-toggle d-flex align-items-center"
              href="#"
              role="button"
              data-bs-toggle="dropdown"
            >
              <div class="user-avatar me-2">
                <i class="bi bi-person-circle fs-4"></i>
              </div>
              <span>{{ userDisplayName }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li>
                <h6 class="dropdown-header">
                  <i class="bi bi-person-fill me-1"></i>
                  {{ userEmail }}
                </h6>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <a class="dropdown-item" href="#" @click="handleLogout">
                  <i class="bi bi-box-arrow-right me-2"></i>
                  Logout
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { getCurrentUser, signOut } from 'aws-amplify/auth'

export default {
  name: 'AppHeader',
  data() {
    return {
      user: null,
      isLoading: false
    }
  },
  computed: {
    userDisplayName() {
      if (this.user) {
        const firstName = this.user.given_name || ''
        const lastName = this.user.family_name || ''
        return firstName && lastName ? `${firstName} ${lastName}` : this.userEmail
      }
      return 'User'
    },
    userEmail() {
      return this.user ? this.user.email : ''
    }
  },
  async mounted() {
    await this.loadCurrentUser()
  },
  methods: {
    async loadCurrentUser() {
      try {
        const user = await getCurrentUser()
        this.user = {
          username: user.username,
          email: user.signInDetails?.loginId || user.username,
          given_name: user.signInDetails?.authFlowType === 'USER_SRP_AUTH' ? '' : '',
          family_name: user.signInDetails?.authFlowType === 'USER_SRP_AUTH' ? '' : ''
        }
        console.log('Current user loaded:', this.user)
      } catch (error) {
        console.error('Error getting current user:', error)
        this.user = null
      }
    },
    async handleLogout() {
      if (this.isLoading) return
      
      this.isLoading = true
      try {
        console.log('Signing out user...')
        await signOut()
        console.log('User signed out successfully')
        this.$router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        // Force redirect even if sign out fails
        this.$router.push('/login')
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

.navbar-brand {
  font-size: 1.5rem;
}

.nav-link {
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 0.375rem;
}

.user-avatar {
  color: rgba(255, 255, 255, 0.9);
}

.dropdown-menu {
  border: none;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  border-radius: 0.5rem;
}

.dropdown-item {
  transition: all 0.3s ease;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
  transform: translateX(5px);
}

@media (max-width: 991.98px) {
  .navbar-nav {
    padding-top: 1rem;
  }
  
  .nav-link {
    padding: 0.75rem 1rem;
    margin: 0.25rem 0;
    border-radius: 0.375rem;
  }
}
</style>
