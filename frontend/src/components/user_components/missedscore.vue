   <template>
    <div class="quiz-page">
      <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
      <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
        <div class="main-content p-4">
          <div class="summary-question-wrapper">
            <div class="left-panel">
              <section class="overview-score card">
                <h2>Missed Quiz Details</h2>
                <ul>
                  <li v-if="quiz"><strong>Subject:</strong> {{ quiz.subjectName }} (ID: {{ quiz.subjectId }})</li>
                  <li><strong>Chapter:</strong> {{ quiz.chapterName }} (ID: {{ quiz.chapterId }})</li>
                  <li><strong>Quiz Name:</strong> {{ quiz.name }} (ID: {{ quiz.id }})</li>
                  <li><strong>Duration:</strong> {{ quiz.duration }} mins</li>
                  <li><strong>Total Questions:</strong> {{ questions.length }}</li>
                  <li><strong>Status:</strong> <span class="text-red-500 font-semibold">Missed</span></li>
                </ul>
              </section>
  <section class="card" v-if="questions.length">
    <h3>Question Stats</h3>
    <ScorePieChart :correct="0" :incorrect="0" :unattempted="questions.length" />
  </section>
            </div>
  
            <div class="right-panel">
              <section class="quiz-question card" v-if="questions.length > 0">
                <h3>Question {{ currentQuestion + 1 }} of {{ questions.length }}</h3>
                <p class="question-text"><strong>{{ questions[currentQuestion].text }}</strong></p>
                <p class="question-status">
                  <strong>Status:</strong>
                  <span :class="['question-status-label', 'Unattempted']">Unattempted</span>
                </p>
                <ul class="option-list">
                  <li
  v-for="(text, key) in questions[currentQuestion].options"
  :key="key"
  :class="{
    option: true,
    correct: key === questions[currentQuestion].correctOption
  }"
>
  <span class="option-label">Option {{ key }}:</span> {{ text }}
</li>

                </ul>
                <p class="mt-2 italic text-sm text-gray-600">
                  Correct Option: {{ questions[currentQuestion].correctOption }}
                </p>
  
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
    name: 'user_missedscore',
    components: {
      user_sidebar,
      ScorePieChart   

    },
    data() {
      return {
        user: {},
        quiz: {},
        questions: [],
        currentQuestion: 0,
        isSidebarOpen: false
      };
    },
   
async mounted() {
  await this.fetchUser();  
  const quizId = this.$route.params.quiz_id;
  const token = localStorage.getItem("JWTToken");
  
  if (!token) {
    console.error("No JWT token found");
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:8080/user/missed_scores/${quizId}`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      console.error("Error fetching missed quiz:", response.statusText);
      return;
    }

    const data = await response.json();
    if (!data.quiz || !data.questions) {
      console.error("Invalid data format", data);
      return;
    }

    if (data.attempted) {
      this.$router.push("/user/scores/" + quizId);
      return;
    }

    this.quiz = data.quiz;

    this.questions = data.questions.map(q => {
      const index = parseInt(q.correctOption.split("_")[1]) - 1;
      const optionLetter = ["A", "B", "C", "D"][index];

      return {
        id: q.id,
        text: q.text,
        correctOption: optionLetter,
        options: {
          A: q.options.A,
          B: q.options.B,
          C: q.options.C,
          D: q.options.D
        }
      };
    });

  } catch (err) {
    console.error("Failed to load missed quiz:", err);
  }
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
      toggleSidebar(open) {
        this.isSidebarOpen = open;
      },
      getOptionClass(optionKey, correctOption) {
  return optionKey.toUpperCase() === correctOption.toUpperCase()
    ? 'option correct'
    : 'option';
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
  .option-list {
    list-style: none;
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
  .option-label {
    font-weight: bold;
  }
  .nav-buttons {
    display: flex;
    justify-content: space-between;
    margin-top: 12px;
  }
  .question-status {
    margin: 10px 0;
    font-size: 16px;
  }
  .question-status-label.Unattempted {
    color: #6c757d;
    font-style: italic;
  }
  </style>
  