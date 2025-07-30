  <template>
    <div class="quiz-page">
      <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
      <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
        <div class="main-content p-4">
          <div class="summary-question-wrapper">
            <div class="left-panel">
              <section class="overview-score card">
                <h2>Quiz Details & Performance</h2>
                <ul>
                  <li><strong>Subject:</strong> {{ quiz.subjectName }} (ID: {{ quiz.subjectId }})</li>
                  <li><strong>Chapter:</strong> {{ quiz.chapterName }} (ID: {{ quiz.chapterId }})</li>
                  <li><strong>Quiz Name:</strong> {{ quiz.name }} (ID: {{ quiz.id }})</li>
                  <li><strong>Duration:</strong> {{ quiz.duration }} mins</li>
                  <li><strong>Total Questions:</strong> {{ totalQuestions }}</li>
                  <li><strong>Marks Scored:</strong> {{ marksScored }}</li>
                  <li><strong>Correct Answers:</strong> {{ questionsRight }}</li>
                  <li><strong>Wrong Answers:</strong> {{ questionsWrong }}</li>
                  <li><strong>Unattempted:</strong> {{ questionsUnattempted }}</li>
                </ul>
                <div class="chart-container">
                  <ScorePieChart
                    :correct="questionsRight"
                    :wrong="questionsWrong"
                    :unattempted="questionsUnattempted"
                  />
                </div>
              </section>
            </div>
  
            <div class="right-panel">
              <section class="quiz-question card" v-if="questions.length > 0">
                <h3>Question {{ currentQuestion + 1 }} of {{ questions.length }}</h3>
                <p class="question-text"><strong>{{ questions[currentQuestion].text }}</strong></p>
                <p class="question-status">
                  <strong>Status:</strong>
                  <span :class="['question-status-label', getCurrentQuestionStatus()]">
  {{ getCurrentQuestionStatus() }}
</span>

                </p>
                <ul class="option-list">
                  <li
  v-for="(text, key) in questions[currentQuestion].options"
  :key="key"
  :class="getOptionClass(key, questions[currentQuestion].correctOption, questions[currentQuestion].selectedOption)"
>
  <span class="option-label">Option {{ key }}:</span> {{ text }}
</li>
                </ul>
                <div class="nav-buttons">
                  <button @click="prevQuestion" :disabled="currentQuestion === 0">Previous</button>
                  <button @click="nextQuestion" :disabled="currentQuestion === questions.length - 1">Next</button>
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import user_sidebar from './user_sidebar.vue';
  import ScorePieChart from './ScorePieChart.vue';
  
  export default {
    data() {
      return {
        quiz: {},
        user: {},
        totalQuestions: 0,
        isSidebarOpen: false,
        marksScored: 0, 
        questionsWrong: 0,
        questionsRight: 0,
        questionsUnattempted: 0,
        currentQuestion: 0,
        questions: [],
        user: {}
      };
    },
    async mounted() {
      await this.fetchUser();  
      const quizId = this.$route.params.quizId;
      const token = localStorage.getItem("JWTToken");
      if (!token) {
        console.error("No JWT token found.");
        return;
      }
  
      try {
        const response = await fetch(`http://127.0.0.1:8080/user/scores/${quizId}`, {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        });
  
        if (!response.ok) throw new Error("Failed to fetch quiz scores");
  
        const data = await response.json();
  
        this.quiz = data.quiz;
        this.marksScored = data.marksScored;
  
        this.questions = data.questions.map(q => ({
  id: q.id,
  text: q.question_statement || q.question_title,
  correctOption: q.correct_option !== null ? String(q.correct_option) : null,
  selectedOption: q.selected_option !== null ? String(q.selected_option) : null,
  options: {
    "1": q.option_1,
    "2": q.option_2,
    "3": q.option_3,
    "4": q.option_4
  }
}));

  
        this.totalQuestions = this.questions.length;
  
        this.questionsRight = this.questions.filter(q => q.selectedOption && q.selectedOption === q.correctOption).length;
        this.questionsUnattempted = this.questions.filter(q => !q.selectedOption).length;
        this.questionsWrong = this.totalQuestions - this.questionsRight - this.questionsUnattempted;
  
      } catch (error) {
        console.error("Error fetching quiz scores:", error);
      }
    },
    components: {
      user_sidebar,
      ScorePieChart
    },
    methods: {
      async fetchUser() {
  try {
    const token = localStorage.getItem("JWTToken");
    const response = await fetch("http://127.0.0.1:8080/user_dashboard", {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
    const data = await response.json();
    this.user = data.user || {};
  } catch (err) {
    console.error("Failed to load user info:", err);
  }
},
      prevQuestion() {
        if (this.currentQuestion > 0) this.currentQuestion--;
      },
      nextQuestion() {
        if (this.currentQuestion < this.questions.length - 1) this.currentQuestion++;
      },
      getCurrentQuestionStatus() {
        const q = this.questions[this.currentQuestion];
        if (!q.selectedOption) return "Unattempted";
        return q.selectedOption === q.correctOption ? "Correct" : "Wrong";
      },
      getStatusClass() {
        return this.getCurrentQuestionStatus();
      },

getOptionClass(option, correct, selected) {
  if (option === correct && option === selected) {
    return 'option correct'; 
  }
  if (option === correct) {
    return 'option correct';
  }
  if (option === selected) {
    return 'option incorrect'; 
  }
  return 'option';
},
toggleSidebar(open) {
        this.isSidebarOpen = open;
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
.card {
  background-color: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quiz-question .selected {
  color: #007bff;
}
.quiz-question .correct {
  color: #28a745;
}
.correct-text {
  color: green;
  font-weight: bold;
}
.wrong-text {
  color: red;
  font-weight: bold;
}
.nav-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
}
.summary-section {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.quiz-summary, .quiz-score {
  flex: 1;
  min-width: 300px;
}
.option-list {
  list-style-type: none;
  padding: 0;
}
.option {
  padding: 10px;
  border: 1px solid #ccc;
  margin: 6px 0;
  border-radius: 8px;
  background-color: #f9f9f9;
  transition: background-color 0.3s;
}

.option.correct {
  background-color: #d4edda;
  border-color: #28a745;
  color: #155724;
  font-weight: bold;
}

.option.incorrect {
  background-color: #f8d7da;
  border-color: #dc3545;
  color: #721c24;
  font-weight: bold;
}

.option-label {
  font-weight: bold;
}
.question-status {
  margin: 10px 0;
  font-size: 16px;
}
.question-status-label.Correct {
  color: #28a745;
  font-weight: bold;
}

.question-status-label.Wrong {
  color: #dc3545;
  font-weight: bold;
}

.question-status-label.Unattempted {
  color: #6c757d;
  font-style: italic;
}


.summary-question-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.left-panel {
  flex: 1;
  min-width: 320px;
  max-width: 450px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.right-panel {
  flex: 2;
  min-width: 300px;
}
.overview-score.card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-container {
  max-width: 300px;
  margin: 0 auto;
}
.summary-question-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: flex-start;
}

.left-panel {
  flex: 1;
  min-width: 300px;
  max-width: 400px;
}

.right-panel {
  flex: 2;
  min-width: 400px;
}

.overview-score.card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-container {
  max-width: 300px;
  margin: 0 auto;
}
</style>
