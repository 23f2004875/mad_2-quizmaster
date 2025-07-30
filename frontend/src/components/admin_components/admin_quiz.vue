<template>
  <div>
    <sidebar @toggle-sidebar="togglesidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <h2 style="text-align: center;">
          Quizzes for {{ subject.name }} - {{ chapter.name }}
        </h2>
        <div class="d-flex justify-content-center">
          <button class="btn btn-primary mt-3" @click="showCreateModal = true">Create Quiz</button>
        </div>

        <div class="row">
          <div class="col-6 mb-4" v-for="quiz in quizzes" :key="quiz.id">
            <div class="card-body">
              <h5 class="card-title">Title: {{ quiz.title }}</h5>
              <p class="card-text">Date: {{ quiz.date_of_quiz }}</p>
              <p class="card-text">Duration: {{ quiz.time_duration }} minutes</p>
              <button @click="deleteQuiz(quiz.id)" class="btn btn-danger mt-2">Delete Quiz</button>
              <button @click="editQuiz(quiz.id)" class="btn btn-warning mt-2">Edit Quiz</button>
            
              <router-link
  :to="`/admin/subject/${subject.id}/chapter/${chapter.id}/quiz/${quiz.id}`"
  class="btn btn-primary mt-2"
  style="display: block; margin: 0 auto;"
>
  View
</router-link>
            </div>
          </div>
        </div>

     
        <Modal v-if="showCreateModal" @close="showCreateModal = false">
  <template v-slot:header>
    <h5 class="modal-title">Create New Quiz</h5>
  </template>

  <p><strong>Subject:</strong> {{ subject.name }}</p>
  <p><strong>Chapter:</strong> {{ chapter.name }}</p>
  <input v-model="newQuiz.title" class="form-control mb-3" placeholder="Quiz Title">
  <input v-model="newQuiz.date_of_quiz" type="date" class="form-control mb-3">
  <input v-model="newQuiz.time_duration" type="number" class="form-control mb-3" placeholder="Duration (minutes)">

  <template v-slot:footer>
    <button class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
    <button class="btn btn-primary" @click="createQuiz">Create</button>
  </template>
</Modal>


      <Modal v-if="showEditModal" @close="showEditModal = false">
  <template #header>
    <h5 class="modal-title">Edit Quiz</h5>
  </template>

  <input v-model="editingQuiz.title" class="form-control mb-3" placeholder="Quiz Title">
  <input v-model="editingQuiz.date_of_quiz" type="date" class="form-control mb-3">
  <input v-model="editingQuiz.time_duration" type="number" class="form-control mb-3" placeholder="Duration (minutes)">

  <template #footer>
    <button class="btn btn-secondary" @click="showEditModal = false">Cancel</button>
    <button class="btn btn-primary" @click="saveEditedQuiz">Save</button>
  </template>
</Modal>


      </div>
    </div>
  </div>
</template>
  <script>
import sidebar from './sidebar.vue';
import Modal from '@/components/admin_components/Modal.vue';

  export default {
    name: 'AdminQuiz',
    data() {
      return {
        subject: {},
        chapter: { id: null },  
        quizzes: [],
        showCreateModal: false,
        isSidebarOpen: false,
        newQuiz: {
          title: '',
          date_of_quiz: '',
          time_duration: null
        },
        showEditModal: false,
    editingQuiz: {
      id: null,
      title: '',
      date_of_quiz: '',
      time_duration: ''
    },
    };
  },
  components: {
        sidebar,
        Modal
    },
  watch: {
  quizzes: {
    handler(newQuizzes) {
      this.$nextTick(() => {
        this.$forceUpdate();
      });
    },
    deep: true
  }
},
mounted() {
    if (!localStorage.getItem("JWTToken")) {
        this.$router.push("/admin_login"); 
    } else {
        this.fetchQuizzes();
    }
},
    methods: {
      async fetchQuizzes() {
  const subjectId = this.$route.params.subject_id;
  const chapterId = this.$route.params.chapter_id;
  try {
    const response = await fetch(`http://127.0.0.1:8080/admin/subject/${subjectId}/chapter/${chapterId}`, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
      }
    });
    const data = await response.json();
    this.subject = data.subject;
    this.chapter = data.chapter;
    this.quizzes = data.quizzes;
        this.$forceUpdate();
  } catch (error) {
    console.error("Error fetching quizzes:", error);
  }
},
async createQuiz() {
    try {
        if (!this.chapter || !this.chapter.id) {
            console.error("Error: Missing chapter_id, quiz cannot be created.");
            return;
        }

        const duration = Number(this.newQuiz.time_duration) || 0;

        const formattedDate = this.newQuiz.date_of_quiz
            ? new Date(this.newQuiz.date_of_quiz).toISOString().split("T")[0]
            : null;

        const response = await fetch("http://127.0.0.1:8080/quiz_create", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                chapter_id: this.chapter.id,
                title: this.newQuiz.title || "Untitled Quiz",
                date_of_quiz: formattedDate,
                duration: duration, 
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error("Error creating quiz:", errorData);
            return;
        }

        const newQuiz = await response.json();
        this.quizzes.push(newQuiz);
        this.showCreateModal = false;
    } catch (error) {
        console.error("Error creating quiz:", error);
    }
},

editQuiz(quizId) {
    const quiz = this.quizzes.find(q => q.id === quizId);
    if (quiz) {
        this.editingQuiz = {
            id: quiz.id,
            title: quiz.title,
            date_of_quiz: quiz.date_of_quiz
                ? new Date(quiz.date_of_quiz).toISOString().split("T")[0]
                : "",
            time_duration: quiz.time_duration 
        };
        this.showEditModal = true;
    }
},

  togglesidebar(open) {
      this.isSidebarOpen = open;
    },
  formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
  },
  async saveEditedQuiz() {
    try {
      const response = await fetch(`http://127.0.0.1:8080/quiz_update/${this.editingQuiz.id}`, {
        method: 'PUT',
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(this.editingQuiz),
      });

      if (response.ok) {
        this.showEditModal = false;
        await this.fetchQuizzes();
      } else {
        console.error("Failed to update quiz");
      }
    } catch (error) {
      console.error("Error updating quiz:", error);
    }
  },
 async deleteQuiz(quizId) {
    if (confirm("Are you sure you want to delete this quiz?")) {
        try {
            const response = await fetch(`http://127.0.0.1:8080/quiz_delete/${quizId}`, {
                method: 'DELETE',
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
                },
            });

            const result = await response.json();

            if (!response.ok) {
                console.error("Failed to delete quiz:", result.error || result.message);
                alert(result.message || "Failed to delete quiz.");
                return;
            }

            if (result.message.includes("hard-deleted")) {
                this.quizzes = this.quizzes.filter(quiz => quiz.id !== quizId);
            } else if (result.message.includes("soft-deleted")) {
                this.quizzes = this.quizzes.filter(quiz => quiz.id !== quizId);
                alert("Quiz has been soft-deleted (kept for score reference).");
            }

            this.$root.$emit('refreshChapters');

        } catch (error) {
            console.error("Error deleting quiz:", error);
            alert("An error occurred while deleting the quiz.");
        }
    }
},
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
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1050;
}
.modal-content {
  background-color: white;
  border-radius: 5px;
  padding: 20px;
  max-width: 500px;
  width: 100%;
}
.modal-dialog {
    margin: 0;
}

.card-body {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

.card-title {
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.card-text {
  margin-bottom: 8px;
  color: #666;
}

.table {
  margin-top: 15px;
}

.btn {
  margin-top: 10px;
}
</style>
