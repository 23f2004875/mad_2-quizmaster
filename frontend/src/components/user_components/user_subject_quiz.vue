 <template>
  <div>
    <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <h2>Quizzes for Chapter:  {{ chapterName }}</h2>

        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search quizzes..."
          class="search-bar"
        />

        <div class="card-grid">
          <div v-for="quiz in filteredQuizzes" :key="quiz.id" class="card">
            <h3>{{ quiz.title }}</h3>
            <p><strong>Duration:</strong> {{ quiz.time_duration }} mins</p>
            <p><strong>Date:</strong> {{ formatDate(quiz.date_of_quiz) }}</p>
            <p><strong>Status:</strong> {{ getQuizStatus(quiz) }}</p>
            <p v-if="quiz.submitted_at"><strong>Submitted At:</strong> {{ formatDate(quiz.submitted_at) }}</p>

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
  class="btn missed-btn"
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
  components: {
    user_sidebar
  },
  data() {
    return {
      isSidebarOpen: false,
      error_msg: '',
      user: {},
      quizzes: [],
      upcomingQuizIds: [],
      searchQuery: '',
      chapterName: '',

    };
  },
  computed: {
    subjectId() {
      return this.$route.params.subject_id;
    },
    chapterId() {
      return this.$route.params.chapter_id;
    },
    filteredQuizzes() {
      return this.quizzes.filter(quiz =>
        quiz.title.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  methods: {
    async fetchUser() {
      try {
        const token = localStorage.getItem("JWTToken");
        const response = await fetch("http://127.0.0.1:8080/user_dashboard", {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await response.json();
        this.user = data.user || {};
      } catch (err) {
        this.error_msg = "Failed to load user.";
      }
    },
    async fetchQuizzes() {
      try {
        const token = localStorage.getItem("JWTToken");

        const [quizRes, dashboardRes] = await Promise.all([
          fetch(`http://127.0.0.1:8080/user/subject/${this.subjectId}/chapter/${this.chapterId}/quizzes`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          fetch("http://127.0.0.1:8080/user_dashboard", {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        const quizData = await quizRes.json();
        const dashData = await dashboardRes.json();

        this.quizzes = quizData.quizzes || [];
        this.chapterName = quizData.chapter_name || '';

        this.upcomingQuizIds = (dashData.upcoming_quizzes || []).map(q => q.id);
      } catch (err) {
        console.error(err);
        this.error_msg = "Failed to fetch quizzes.";
      }
    },
    formatDate(dateStr) {
      const date = new Date(dateStr);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },
    isAttempted(quiz) {
      return !this.upcomingQuizIds.includes(quiz.id);
    },
    getQuizStatus(quiz) {
  const now = new Date();
  const due = new Date(quiz.date_of_quiz);

  if (quiz.submitted_at) return "Attempted";
  if (due < now) return "Missed";
  return "Unattempted";
},
    toggleSidebar(open) {
      this.isSidebarOpen = open;
    }
  },
  mounted() {
    this.fetchUser();
    this.fetchQuizzes();
  }
};
</script>
<style>
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
  min-height: calc(100vh - 60px);
  width: calc(100% - 60px);
  overflow-y: auto;
}
.search-bar {
  padding: 10px;
  width: 100%;
  max-width: 400px;
  margin-bottom: 20px;
  border-radius: 5px;
  border: 1px solid #ccc;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}
.card {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}
.card:hover {
  transform: scale(1.02);
}
.btn {
  display: inline-block;
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
  margin-top: 10px;
  text-align: center;
  text-decoration: none;
  color: white;
  cursor: pointer;
}
.scores-btn {
  background-color: #007bff;
}
.start-btn {
  background-color: #28a745;
}
.error {
  color: red;
  margin-top: 20px;
}
.missed-btn {
  background-color: #f87171;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.missed-btn:hover {
  background-color: #ef4444; 
}
</style>
