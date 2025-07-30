<template>
  <div>
    <div :class="['sidebar', { open: isSidebarOpen }]" 
         @mouseover="isSidebarOpen = true" 
         @mouseleave="isSidebarOpen = false">
      <h4 v-if="isSidebarOpen" class="text-center text-white">User Panel</h4>
      
      <router-link to="/user_dashboard">
        <i class="fas fa-chart-line"></i>
        <span v-if="isSidebarOpen">Dashboard</span>
      </router-link>

      <router-link to="/user/subject">
        <i class="fas fa-book"></i>
        <span v-if="isSidebarOpen">Subjects</span>
      </router-link>

      <router-link to="/user/quizzes">
        <i class="fas fa-question"></i>
        <span v-if="isSidebarOpen">Quizzes</span>
      </router-link>

      <router-link to="/user/summary">
        <i class="fas fa-list-alt"></i>
        <span v-if="isSidebarOpen">Summary</span>
      </router-link>

      <a href="#" @click.prevent="logout()">
        <i class="fas fa-sign-out-alt"></i>
        <span v-if="isSidebarOpen">Logout</span>
      </a>
    </div>

    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <span class="navbar-brand">Welcome, {{ user.username || 'Guest' }}</span>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/user/profile">
                <i class="fas fa-user-circle"></i> Profile
              </router-link>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="logout()">
                <i class="fas fa-sign-out-alt"></i> Logout
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'user_sidebar',
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isSidebarOpen: false
    };
  },
  watch: {
    isSidebarOpen(newValue) {
      this.$emit('toggle-sidebar', newValue);
    }
  },
  methods: {
    async logout() {
      try {
        this.clearSession();
      } catch (error) {
        console.error("Logout error:", error);
      }
    },
    clearSession() {
      localStorage.removeItem("JWTToken");
      this.$router.push("/user_login");
    }
  }
};
</script>

<style>
.sidebar {
  width: 60px;
  transition: width 0.3s ease-in-out;
  position: fixed;
  left: 0;
  top: 0;
  height: 100%;
  background-color: #333;
  overflow-x: hidden;
  white-space: nowrap;
  padding-top: 10px;
  z-index: 1001;
}

.sidebar.open {
  width: 250px;
}

.sidebar a {
  padding: 15px;
  text-decoration: none;
  color: white;
  display: flex;
  align-items: center;
  transition: 0.3s;
  overflow: hidden;
  width: 100%;
}

.sidebar a:hover {
  background-color: #444;
}

.sidebar a span {
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
}

.sidebar.open a span {
  opacity: 1;
}

.sidebar i {
  width: 30px;
  text-align: center;
  margin-right: 10px;
  font-size: 18px;
}

.navbar {
  margin-left: 60px;
  width: calc(100% - 60px);
  position: fixed;
  top: 0;
  height: 60px;
  z-index: 1000;
  transition: margin-left 0.3s ease-in-out, width 0.3s ease-in-out;
}

.sidebar.open + .navbar {
  margin-left: 250px;
  width: calc(100% - 250px);
}
</style>
