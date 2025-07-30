<template>
  <div>
    <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <h2 class="text-center">Upcoming Quizzes</h2>


 <input
          type="text"
          v-model="searchQuery"
          placeholder="Search quizzes..."
          class="search-bar"
        />

        <div class="row">
          <div
            v-for="quiz in filteredQuizzes"
            :key="quiz.id"
            class="col-md-6 mb-4"
          >
            <div class="card shadow rounded-3 p-3">
              <h5 class="card-title">{{ quiz.title }}</h5>
              <p class="card-text"><strong>Subject:</strong> {{ quiz.subject_name }}</p>
              <p class="card-text"><strong>Chapter:</strong> {{ quiz.chapter_name }}</p>
              <p class="card-text"><strong>Questions:</strong> {{ quiz.num_questions }}</p>
              <p class="card-text"><strong>Date:</strong> {{ quiz.date }}</p>
              <p class="card-text"><strong>Duration:</strong> {{ quiz.duration }} minutes</p>
              <div class="d-flex justify-content-between">
                <button class="btn btn-outline-primary" @click="showQuizModal(quiz)">View</button>
                <button class="btn btn-success" @click="() => startQuiz(quiz)">Start Quiz</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="filteredQuizzes.length === 0" class="text-center mt-4">
          <p>No quizzes found matching your search.</p>
        </div>

        <Modal v-if="showModal" @close="showModal = false">
          <template #header>
            <h5 class="modal-title">Quiz Details</h5>
          </template>

          <template #default>
            <p><strong>Title:</strong> {{ selectedQuiz.title }}</p>
            <p><strong>Subject:</strong> {{ selectedQuiz.subject_name }}</p>
            <p><strong>Chapter:</strong> {{ selectedQuiz.chapter_name }}</p>
            <p><strong>No. of Questions:</strong> {{ selectedQuiz.num_questions }}</p>
            <p><strong>Date:</strong> {{ selectedQuiz.date }}</p>
            <p><strong>Duration:</strong> {{ selectedQuiz.duration }} minutes</p>
          </template>

          <template #footer>
            <button class="close-modal" @click="showModal = false">Close</button>
          </template>
        </Modal>

      </div>
    </div>
  </div>
</template>

<script>
import user_sidebar from './user_sidebar.vue';
import user_quiz from './user_quiz.vue'; 
import Modal from '../admin_components/Modal.vue'; 


export default {
    data() {
        return {
            isSidebarOpen: false,
            error_msg: '',
            user: {},
            upcomingQuizzes: [],
            showModal: false,
            selectedQuiz: {},
            searchQuery: "",

        };
    },
    computed: {
  filteredQuizzes() {
    const q = this.searchQuery.toLowerCase();
    return this.upcomingQuizzes.filter((quiz) =>
      quiz.title.toLowerCase().includes(q) ||
      quiz.subject_name.toLowerCase().includes(q) ||
      quiz.chapter_name.toLowerCase().includes(q)
    );
  }
},
    components: {
        user_sidebar,
        user_quiz,
        Modal
    },
    methods: {
        toggleSidebar(open) {
            this.isSidebarOpen = open;
        },
        async fetchQuizzes() {
    const token = localStorage.getItem("JWTToken");

    try {
        const response = await fetch("http://127.0.0.1:8080/user_dashboard", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            mode: "cors",
            credentials: "include",
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.msg || "Failed to fetch");
        }

        const data = await response.json();
        this.upcomingQuizzes = data.upcoming_quizzes;
        this.user = data.user;

    } catch (error) {
        console.error("Error fetching quizzes:", error);
        this.error_msg = error.message;
        this.$router.push("/user_login");
    }
},
        showQuizModal(quiz) {
            this.selectedQuiz = quiz;
            this.showModal = true;
        },
        async startQuiz(quiz) {
  console.log("Starting quiz:", quiz);

  if (!quiz || !quiz.id) {
    console.error("Invalid quiz object:", quiz);
    return;
  }

  if (!this.$router || typeof this.$router.push !== 'function') {
    console.error("Vue Router is not available");
    return;
  }

  try {
    await this.$router.push({ name: 'user_quiz', params: { quizId: quiz.id } });
    console.log("Navigated to user_quiz");
  } catch (error) {
    console.error("Navigation error:", error);
  }
},
    },
  mounted() {
  const token = localStorage.getItem("JWTToken");

  if (!token) {
    this.$router.push("/user_login");
    return;
  }

  try {
    const decodedToken = JSON.parse(atob(token.split('.')[1]));
    const expiry = decodedToken.exp * 1000;
    const now = Date.now();

    if (now > expiry) {
      localStorage.removeItem("JWTToken");
      localStorage.removeItem("user_type");
      alert("Session expired. Please log in again.");
      this.$router.push("/user_login");
      return;
    }

    this.fetchQuizzes();

  } catch (err) {
    console.error("Invalid token:", err);
    localStorage.removeItem("JWTToken");
    localStorage.removeItem("user_type");
    this.$router.push("/user_login");
  }
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

.striped-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0 auto;
}

.striped-table th, .striped-table td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: center;
}

.striped-table th {
    background-color: #f0f0f0;
}

.striped-table tr.even-row {
    background-color: #f2f2f2;
}

.striped-table tr:hover {
    background-color: #e5e5e5;
}

.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}

.modal {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  max-width: 500px;
  width: 90%;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.close {
    background-color: transparent;
    border: none;
    font-size: 18px;
    cursor: pointer;
}

.close-modal {
    background-color: #4CAF50;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.close-modal:hover {
    background-color: #3e8e41;
}
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1050;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);

  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-modal-box {
  background-color: #212529;
  color: white;
  padding: 20px;
  border-radius: 6px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
}
.modal-title {
  text-align: center;
  width: 100%;
}
</style>
