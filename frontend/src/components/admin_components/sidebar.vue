<template>
  <div>
    <div :class="['sidebar', { open: isSidebarOpen }]" 
         @mouseover="isSidebarOpen = true" 
         @mouseleave="isSidebarOpen = false">
      <h4 v-if="isSidebarOpen" class="text-center">Admin Panel</h4>

      <router-link to="/admin_dashboard">
        <i class="fas fa-book"></i> <span v-if="isSidebarOpen">Subjects</span>
      </router-link>

      <router-link to="/admin/chapter_mgmt">
        <i class="fas fa-layer-group"></i> <span v-if="isSidebarOpen">Chapters</span>
      </router-link>

      <router-link to="/admin/quiz_mgmt">
        <i class="fas fa-question-circle"></i> <span v-if="isSidebarOpen">Quizzes</span>
      </router-link>

      <router-link to="/admin/summary">
        <i class="fas fa-chart-bar"></i> <span v-if="isSidebarOpen">Summary</span>
      </router-link>

      <router-link to="/admin/user">
        <i class="fas fa-users"></i> <span v-if="isSidebarOpen">Users</span>
      </router-link>

      <a href="#" @click.prevent="logout()">
        <i class="fas fa-sign-out-alt"></i> <span v-if="isSidebarOpen">Logout</span>
      </a>
    </div>

    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <span class="navbar-brand">Dashboard</span>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="logout()">Logout</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'sidebar',
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
      } catch (error) {}
    },
    clearSession() {
      localStorage.removeItem("JWTToken");
      localStorage.removeItem("name");
      this.$router.push("/admin_login");
    }
  }
};
</script>

<style scoped>
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
  padding: 12px 10px;
  text-decoration: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.3s;
  overflow: hidden;
  width: 100%;
}

.sidebar a span {
  display: none;
  margin-left: 10px;
}

.sidebar.open a {
  justify-content: flex-start;
  padding-left: 20px;
}

.sidebar.open a span {
  display: inline;
  opacity: 1;
}

.sidebar i {
  font-size: 18px;
  min-width: 30px;
  text-align: center;
  margin-right: 0;
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
