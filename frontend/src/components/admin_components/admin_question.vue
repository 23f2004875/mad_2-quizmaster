<template>
  <div>
    <sidebar @toggle-sidebar="togglesidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">

        <Modal v-if="showQuestionModal" @close="closeQuestionModal">
          <template #header>
            <h5 class="modal-title">{{ editingQuestion ? 'Edit' : 'Add' }} Question</h5>
          </template>

          <input v-model="currentQuestion.question_title" class="form-control mb-2" placeholder="Question Title" />
          <textarea v-model="currentQuestion.question_statement" class="form-control mb-2" placeholder="Question Statement" />
          <input v-model="currentQuestion.option_1" class="form-control mb-2" placeholder="Option 1" />
          <input v-model="currentQuestion.option_2" class="form-control mb-2" placeholder="Option 2" />
          <input v-model="currentQuestion.option_3" class="form-control mb-2" placeholder="Option 3" />
          <input v-model="currentQuestion.option_4" class="form-control mb-2" placeholder="Option 4" />
          <select v-model="currentQuestion.correct_option" class="form-control mb-2">
            <option value="">Select Correct Option</option>
            <option value="option_1">Option 1</option>
            <option value="option_2">Option 2</option>
            <option value="option_3">Option 3</option>
            <option value="option_4">Option 4</option>
          </select>

          <template #footer>
            <button class="btn btn-secondary" @click="closeQuestionModal">Cancel</button>
            <button class="btn btn-primary" @click="saveQuestion">Save</button>
          </template>
        </Modal>

        <h4>Questions</h4>
        <div v-if="quiz.questions && quiz.questions.length">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Question No.</th>
                <th>Title</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="question in quiz.questions" :key="question.id">
                <td>{{ question.que_no }}</td>
                <td>{{ question.question_title }}</td>
                <td>
                  <button @click="editQuestion(question)" class="btn btn-sm btn-warning me-2">Edit</button>
                  <button @click="deleteQuestion(question.id)" class="btn btn-sm btn-danger">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else>No questions available</p>

        <button class="btn btn-primary mt-3" @click="addQuestion(quiz.id)">Add Question</button>

      </div>
    </div>
  </div>
</template>

<script>
import sidebar from './sidebar.vue';
import Modal from '@/components/admin_components/Modal.vue';

export default {
  name: 'AdminQuestion',
  components: { sidebar, Modal },
  data() {
    return {
      isSidebarOpen: false,
      showQuestionModal: false,
      editingQuestion: false,
      quiz: {
        id: null,
        questions: []
      },
      currentQuestion: {
        id: null,
        quiz_id: null,
        que_no: null,
        question_title: '',
        question_statement: '',
        option_1: '',
        option_2: '',
        option_3: '',
        option_4: '',
        option_5: '',
        option_6: '',
        correct_option: ''
      }
    };
  },
  mounted() {
    if (!localStorage.getItem("JWTToken")) {
      this.$router.push("/admin_login");
    } else {
      this.fetchQuiz();
    }
  },
  methods: {
    togglesidebar(open) {
      this.isSidebarOpen = open;
    },
    async fetchQuiz() {
      const { subject_id, chapter_id, quiz_id } = this.$route.params;
      try {
        const res = await fetch(`http://127.0.0.1:8080/admin/subject/${subject_id}/chapter/${chapter_id}/quiz/${quiz_id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("JWTToken")}`
          }
        });
        const data = await res.json();
        this.quiz = {
  ...data.quiz,
  questions: data.questions || []
};
      } catch (err) {
        console.error("Error fetching quiz:", err);
      }
    },
    addQuestion(quizId) {
      this.editingQuestion = false;
      this.currentQuestion = {
        quiz_id: quizId,
        que_no: this.getNextQuestionNumber(),
        question_title: '',
        question_statement: '',
        option_1: '',
        option_2: '',
        option_3: '',
        option_4: '',
        correct_option: ''
      };
      this.showQuestionModal = true;
    },
    editQuestion(question) {
      this.editingQuestion = true;
      this.currentQuestion = { ...question };
      this.showQuestionModal = true;
    },
    closeQuestionModal() {
      this.showQuestionModal = false;
    },
    getNextQuestionNumber() {
  if (!this.quiz || !this.quiz.questions || this.quiz.questions.length === 0) {
    return 1;
  }
  return Math.max(...this.quiz.questions.map(q => q.que_no || 0)) + 1;
},
    async saveQuestion() {
      const method = this.editingQuestion ? 'PUT' : 'POST';
      const url = this.editingQuestion
        ? `http://127.0.0.1:8080/question_update/${this.currentQuestion.id}`
        : 'http://127.0.0.1:8080/question_create';

      try {
        const res = await fetch(url, {
          method,
          headers: {
            Authorization: `Bearer ${localStorage.getItem("JWTToken")}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.currentQuestion)
        });
        if (res.ok) {
          await this.fetchQuiz();
          this.closeQuestionModal();
        } else {
          console.error("Failed to save question");
        }
      } catch (err) {
        console.error("Error saving question:", err);
      }
    },
    async deleteQuestion(questionId) {
      if (confirm("Are you sure you want to delete this question?")) {
        try {
          const res = await fetch(`http://127.0.0.1:8080/question_delete/${questionId}`, {
            method: 'DELETE',
            headers: {
              Authorization: `Bearer ${localStorage.getItem("JWTToken")}`
            }
          });
          if (res.ok) {
            await this.fetchQuiz();
          } else {
            console.error("Failed to delete question");
          }
        } catch (err) {
          console.error("Error deleting question:", err);
        }
      }
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
</style>
