<template>
  <div>
    <sidebar @toggle-sidebar="togglesidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <h2 class="mb-4">All Registered Users</h2>

        <div class="d-flex flex-wrap gap-3 mb-3">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search by name, email, qualification..."
            class="form-control"
            style="max-width: 300px;"
          />

          <select v-model="selectedQualification" class="form-select" style="max-width: 200px;">
            <option value="">All Qualifications</option>
            <option v-for="q in uniqueQualifications" :key="q" :value="q">{{ q }}</option>
          </select>

          <select v-model="sortBy" class="form-select" style="max-width: 200px;">
            <option value="">Sort By</option>
            <option value="attempts">Total Attempts</option>
            <option value="score">Average Score</option>
          </select>

<button class="btn btn-success" @click="triggerBatchExport">Export CSV (Batch)</button>
        </div>

        <div
          v-for="user in sortedUsers"
          :key="user.id"
          class="user-card mb-4 d-flex align-items-start"
        >
          <img :src="user.image_url" alt="User" class="user-image me-3" />
          <div class="card-body">
            <h4>{{ user.username }}</h4>
            <p><strong>User ID:</strong> {{ user.user_id }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
            <p><strong>Qualification:</strong> {{ user.qualification || 'N/A' }}</p>
            <p><strong>DOB:</strong> {{ formatDate(user.dob) }}</p>
            <p><strong>Total Quizzes Attempted:</strong> {{ user.total_attempts }}</p>
            <p><strong>Average Score:</strong> {{ user.average_score }}%</p>

            <button class="btn btn-primary mt-2" @click="toggleDetails(user.id)">
              {{ expandedUser === user.id ? 'Hide Details' : 'View Details' }}
            </button>

            <div v-if="expandedUser === user.id" class="mt-3">
              <h5>Submitted Quizzes:</h5>
              <div v-if="user.scores.length === 0">No quiz attempts found.</div>
              <ul v-else>
                <li v-for="score in user.scores" :key="score.quiz_id">
                  <strong>{{ score.quiz_title }}</strong> -
                  {{ score.subject }} / {{ score.chapter }}<br />
                  Marks: {{ score.marks_scored }} / {{ score.total_score }}<br />
                  Attempted On: {{ formatDate(score.attempted_on) }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div v-if="sortedUsers.length === 0" class="alert alert-warning">
          No users match your search or filter.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import sidebar from './sidebar.vue';
import io from 'socket.io-client';

export default {
  name: 'admin_user',
  components: { sidebar },
  data() {
    return {
      isSidebarOpen: false,
      users: [],
      searchQuery: '',
      selectedQualification: '',
      sortBy: '',
      expandedUser: null,
      socket: null
    };
  },
  computed: {
    uniqueQualifications() {
      const qSet = new Set(this.users.map(u => u.qualification).filter(Boolean));
      return Array.from(qSet);
    },
    filteredUsers() {
      const query = this.searchQuery.toLowerCase();
      return this.users.filter(user => {
        const matchesQuery =
          user.username.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query) ||
          (user.qualification || '').toLowerCase().includes(query);
        const matchesFilter = this.selectedQualification
          ? user.qualification === this.selectedQualification
          : true;
        return matchesQuery && matchesFilter;
      });
    },
    sortedUsers() {
      let sorted = [...this.filteredUsers];
      if (this.sortBy === 'attempts') {
        sorted.sort((a, b) => b.total_attempts - a.total_attempts);
      } else if (this.sortBy === 'score') {
        sorted.sort((a, b) => b.average_score - a.average_score);
      }
      return sorted;
    }
  },
  mounted() {
    if (!localStorage.getItem("JWTToken")) {
      this.$router.push("/admin_login");
    } else {
      this.fetchUsers();
    }

    this.socket = io("http://127.0.0.1:8080");
    this.socket.on("csv_ready", (data) => {
      alert("CSV is ready. Downloading...");
      const link = document.createElement("a");
      link.href = `http://127.0.0.1:8080/exports/${data.filename}`;
      link.download = data.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  },
  beforeDestroy() {
    if (this.socket) this.socket.disconnect();
  },
  methods: {
    togglesidebar(open) {
      this.isSidebarOpen = open;
    },
    async fetchUsers() {
      try {
        const response = await fetch("http://127.0.0.1:8080/admin/users", {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`
          }
        });
        if (!response.ok) throw new Error("Failed to fetch users");
        const data = await response.json();
        this.users = data.users;
      } catch (error) {
        console.error("Error fetching users:", error);
      }
    },
    async triggerBatchExport() {
      try {
        const res = await fetch("http://127.0.0.1:8080/admin/export_users_csv", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`
          }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Export failed");
        alert(data.message);
      } catch (error) {
        console.error("Error triggering export:", error);
        alert("Failed to export file.");
      }
    },
    toggleDetails(userId) {
      this.expandedUser = this.expandedUser === userId ? null : userId;
    },
    formatDate(dateStr) {
      return dateStr ? new Date(dateStr).toLocaleDateString() : "N/A";
    }
  }
};
</script>


<style scoped>
.user-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 15px;
  display: flex;
}

.user-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #007bff;
}
.main-container {
  margin-left: 60px;
  transition: margin-left 0.3s ease-in-out;
}

.main-container.sidebar-open {
  margin-left: 250px;
}

.main-content {
  margin-top: 60px;
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: scroll;
  scrollbar-width: none;
  -ms-overflow-style: none;
  width: calc(100% - 60px);
}

.main-content::-webkit-scrollbar {
  display: none;
}
</style>
