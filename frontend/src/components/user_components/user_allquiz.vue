<template>
  <div>
    <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <h2>All Quizzes</h2>

        <div class="filters">
          <input type="text" v-model="searchQuery" placeholder="Search quizzes..." />

          <select v-model="selectedStatus">
            <option value="">All Status</option>
            <option value="Attempted">Attempted</option>
            <option value="Unattempted">Unattempted</option>
            <option value="Missed">Missed</option>
          </select>

          <select v-model="selectedSubject">
            <option value="">All Subjects</option>
            <option v-for="subject in subjects" :key="subject" :value="subject">
              {{ subject }}
            </option>
          </select>

          <select v-model="selectedChapter">
            <option value="">All Chapters</option>
            <option v-for="chapter in chapters" :key="chapter" :value="chapter">
              {{ chapter }}
            </option>
          </select>

          <select v-model="sortOrder">
            <option value="asc">Sort by Date ↑</option>
            <option value="desc">Sort by Date ↓</option>
          </select>

          <button @click="resetFilters" class="btn reset-btn">Reset Filters</button>
        </div>

        <div class="card-grid">
          <div v-for="quiz in filteredAndSortedQuizzes" :key="quiz.id" class="card">
            <h3>{{ quiz.title }}</h3>
            <p><strong>Subject:</strong> {{ quiz.subject }}</p>
            <p><strong>Chapter:</strong> {{ quiz.chapter }}</p>
            <p><strong>Duration:</strong> {{ quiz.time_duration }} mins</p>
            <p><strong>Date:</strong> {{ formatDate(quiz.date_of_quiz) }}</p>
            <p v-if="quiz.submitted_at"><strong>Submitted At:</strong> {{ formatDate(quiz.submitted_at) }}</p>
            <p><strong>Status:</strong> {{ quiz.status }}</p>

            <router-link
              v-if="quiz.status === 'Attempted'"
              :to="`/user/scores/${quiz.id}`"
              class="btn scores-btn"
            >
              View Score
            </router-link>

            <router-link
              v-else-if="quiz.status === 'Missed'"
              :to="`/user/missed/${quiz.id}`"
              class="btn view-btn"
            >
              View Missed Quiz
            </router-link>

            <router-link
              v-else
              :to="`/user/quiz/${quiz.id}`"
              class="btn start-btn"
            >
              Start Quiz
            </router-link>
          </div>
        </div>

        <p v-if="error_msg" class="error">{{ error_msg }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import user_sidebar from './user_sidebar.vue';

export default {
  components: { user_sidebar },
  data() {
    return {
      isSidebarOpen: false,
      error_msg: '',
      user: {},
      quizzes: [],
      searchQuery: '',
      selectedSubject: '',
      selectedStatus: '',
      selectedChapter: '',
      sortOrder: 'asc'
    };
  },
  computed: {
    subjects() {
      return [...new Set(this.quizzes.map(q => q.subject))].sort();
    },
    chapters() {
      return [...new Set(this.quizzes.map(q => q.chapter))].sort();
    },
    filteredAndSortedQuizzes() {
      return this.quizzes
        .filter(quiz =>
          (!this.searchQuery || quiz.title.toLowerCase().includes(this.searchQuery.toLowerCase())) &&
          (!this.selectedSubject || quiz.subject === this.selectedSubject) &&
          (!this.selectedChapter || quiz.chapter === this.selectedChapter) &&
          (!this.selectedStatus || quiz.status === this.selectedStatus)
        )
        .sort((a, b) => {
          const dateA = new Date(a.date_of_quiz);
          const dateB = new Date(b.date_of_quiz);
          return this.sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
        });
    }
  },
  methods: {
    async fetchUser() {
      try {
        const token = localStorage.getItem("JWTToken");
        const response = await fetch("http://127.0.0.1:8080/user_dashboard", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();
        this.user = data.user || {};
      } catch (err) {
        this.error_msg = "Failed to load user data.";
      }
    },
    async fetchQuizzes() {
      try {
        const token = localStorage.getItem("JWTToken");
        const res = await fetch("http://127.0.0.1:8080/user/all_quizzes", {
          headers: { "Authorization": `Bearer ${token}` }
        });

        const data = await res.json();
        this.quizzes = data.quizzes || [];


      } catch (err) {
        this.error_msg = "Failed to fetch quizzes.";
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return "N/A";
      const date = new Date(dateStr);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },
    resetFilters() {
      this.searchQuery = '';
      this.selectedSubject = '';
      this.selectedChapter = '';
      this.selectedStatus = '';
      this.sortOrder = 'asc';
    },
    toggleSidebar(open) {
      this.isSidebarOpen = open;
    }
  },
  mounted() {
    this.fetchUser();
    this.fetchQuizzes();
  },
  watch: {
    '$route'() {
      this.fetchQuizzes();
    }
  }
};
</script>

<style scoped>
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}
.card {
  background-color: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.card:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}
.btn {
  display: inline-block;
  margin-top: 10px;
  padding: 8px 14px;
  text-decoration: none;
  border-radius: 5px;
  font-weight: bold;
}
.scores-btn {
  background-color: #4caf50;
  color: white;
}
.start-btn {
  background-color: #2196f3;
  color: white;
}
.view-btn {
  background-color: #ff9800;
  color: white;
}
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.filters input,
.filters select {
  padding: 8px;
  border-radius: 5px;
  border: 1px solid #ccc;
}
.reset-btn {
  margin-top: 10px;
  padding: 5px 12px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.reset-btn:hover {
  background-color: #d32f2f;
}
</style>
