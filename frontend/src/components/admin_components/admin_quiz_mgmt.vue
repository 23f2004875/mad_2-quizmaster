<template>
  <div>
    <sidebar @toggle-sidebar="togglesidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <div class="search-bar-container">
          <input 
            type="text" 
            v-model="searchQuery" 
            @input="searchQuizzes" 
            class="search-bar" 
            placeholder="Search quizzes..."
          />
        </div>
        <div v-if="showNoResultsMessage" class="alert alert-warning mt-3">
          {{ noResultsMessage }}
          <button type="button" class="btn-close float-end" @click="clearSearch" aria-label="Close"></button>
        </div>
        <div class="container mt-4">
          <div class="row">
            <div class="col-lg-4 col-md-6 col-sm-12 mb-4" v-for="quiz in displayedQuizzes" :key="quiz.id">
              <div class="quiz-card" @click="goToQuiz(quiz.subject_id, quiz.chapter_id)">
                <h3>{{ quiz.title }}</h3>
                <p>Subject: {{ quiz.subject_name }}</p>
                <p>Chapter: {{ quiz.chapter_name }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import sidebar from './sidebar.vue';

export default {
  name: 'admin_quiz_mgmt',
  components: { sidebar },
  data() {
    return {
      quizzes: [],
      searchQuery: '',
      searchResults: [],
      noResultsMessage: '',
      isSidebarOpen: false,
      showNoResultsMessage: false,
      subjects: [],
      chapters: []
    };
  },
  computed: {
    displayedQuizzes() {
      return this.searchResults.length > 0 ? this.searchResults : this.quizzes;
    }
  },
  mounted() {
    if (!localStorage.getItem("JWTToken")) {
      this.$router.push("/admin_login");
    } else {
      this.fetchQuizzes();
      this.fetchSubjects();
      this.fetchChapters();
    }
  },
  methods: {
    async fetchQuizzes() {
      try {
        const response = await fetch("http://127.0.0.1:8080/admin/quiz_mgmt", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
            "Content-Type": "application/json"
          }
        });
        if (!response.ok) throw new Error("Failed to fetch quizzes");
        const data = await response.json();
        this.quizzes = data.quizzes;
      } catch (error) {
        console.error("Error fetching quizzes:", error);
      }
    },
    togglesidebar(open) {
      this.isSidebarOpen = open;
    },
    async fetchSubjects() {
      try {
        const response = await fetch("http://127.0.0.1:8080/admin/quiz_mgmt", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
            "Content-Type": "application/json"
          }
        });
        if (!response.ok) throw new Error("Failed to fetch subjects");
        const data = await response.json();
        this.subjects = data.subjects;
      } catch (error) {
        console.error("Error fetching subjects:", error);
      }
    },
    async fetchChapters() {
      try {
        const response = await fetch("http://127.0.0.1:8080/admin/chapters", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
            "Content-Type": "application/json"
          }
        });
        if (!response.ok) throw new Error("Failed to fetch chapters");
        const data = await response.json();
        this.chapters = data.chapters;
      } catch (error) {
        console.error("Error fetching chapters:", error);
      }
    },
    goToQuiz(subjectId, chapterId) {
      this.$router.push(`/admin/subject/${subjectId}/chapter/${chapterId}`);
    },
    async searchQuizzes() {
      if (!this.searchQuery.trim()) {
        this.noResultsMessage = "Please enter a search query.";
        this.showNoResultsMessage = true;
        this.searchResults = [];
        return;
      }
      try {
        const response = await fetch(`http://127.0.0.1:8080/search_quizzes?query=${encodeURIComponent(this.searchQuery)}`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
            "Content-Type": "application/json"
          }
        });
        if (response.status === 404) {
          const data = await response.json();
          this.noResultsMessage = data.message;
          this.showNoResultsMessage = true;
          this.searchResults = [];
        } else if (response.ok) {
          const data = await response.json();
          this.searchResults = data.quizzes;
          this.showNoResultsMessage = false;
        } else {
          throw new Error("Failed to search quizzes");
        }
      } catch (error) {
        console.error("Error searching quizzes:", error);
        this.noResultsMessage = "An error occurred while searching.";
        this.showNoResultsMessage = true;
      }
    },
    clearSearch() {
      this.searchQuery = '';
      this.searchResults = [];
      this.showNoResultsMessage = false;
    }
  }
};
</script>

<style scoped>
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

.quiz-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s ease-in-out;
  margin-bottom: 20px;
}

.quiz-card:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
</style>
