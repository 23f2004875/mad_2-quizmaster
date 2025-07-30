<template>
    <div>
        <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
        <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
            <div class="main-content">
                <div class="question-sidebar">
                    <h3>Questions</h3>
                    <ul>
                        <li 
                            v-for="(question, index) in questions" 
                            :key="question.id"
                        >
                            <button 
                                @click="navigateToQuestion(index)"
                                :class="getButtonClass(index)"
                                class="question-btn"
                            >
                                Q{{ index + 1 }}
                            </button>
                        </li>
                    </ul>
                    
                    <div class="preview-section">
                        <h4>Legend</h4>
                        <div class="legend">
                            <span class="btn grey">Not Visited</span>
                            <span class="btn red">Visited, Not Answered</span>
                            <span class="btn green">Answered</span>
                            <span class="btn purple">Marked for Review</span>
                        </div>
                    </div>
                </div>

                <div class="quiz-container">
                    <div class="quiz-header">
                        <div class="question-number">
                            Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}
                        </div>
                        <div class="timer">{{ formatTimer(timer) }}</div>
                    </div>

                    <div class="question-content">
                        <div v-for="(question, index) in questions" 
                             :key="question.id" 
                             v-show="currentQuestionIndex === index">
                            <h3 class="question-title">{{ question.question_title }}</h3>
                            <p class="question-statement">{{ question.question_statement }}</p>
                            
                            <div class="options">
                                <label v-for="(option, i) in getQuestionOptions(question)" 
                                       :key="i"
                                       :for="'option_' + (i+1)">
                                    <input type="radio" 
                                           :id="'option_' + (i+1)" 
                                           :value="option" 
                                           v-model="selectedOption"
                                           @change="markAnswered(currentQuestionIndex)">
                                    {{ option }}
                                </label>
                            </div>

                        </div>
                    </div>

                    <div class="navigation-buttons">
                        <button 
                            v-if="currentQuestionIndex > 0" 
                            @click="prevQuestion"
                            class="nav-button prev-button"
                        >
                            ← Previous
                        </button>
                         <!-- Mark for Review Button -->
                         <button @click="markForReview(currentQuestionIndex)" class="review-button">
                                Mark for Review
                            </button>
                            <button 
    @click="currentQuestionIndex < questions.length - 1 ? handleNavigation(true) : submitQuiz()"
    class="nav-button next-button"
>
    {{ currentQuestionIndex < questions.length - 1 ? 'Next →' : 'Submit Quiz' }}
</button>

                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import user_sidebar from './user_sidebar.vue';

export default {
    name: "user_quiz", 

    data() {
        return {
            isSidebarOpen: false,
            error_msg: '',
            user: {},
            quiz: {},
            questions: [],
            currentQuestionIndex: 0,
            answers: [],
            timer: null,
            showModal: false,  
            duration: null,
            selectedOption: null,
            questionStatus: Array(10).fill("notVisited"), 
        };
    },
    computed: {
        currentQuestion() {
            return this.questions.length > 0 ? this.questions[this.currentQuestionIndex] : null;
        },
        savedAnswer() {
    if (!this.currentQuestion) return null;
    return this.answers.find(a => a.question_id === this.currentQuestion.id)?.selected_option || null;
},

    },
    components: {
        user_sidebar
    },
    async mounted() {
        await this.fetchUser();  

        const token = localStorage.getItem("JWTToken");
        if (!token) {
            this.$router.push("/user_login");
        } else {
            const decodedToken = JSON.parse(atob(token.split('.')[1]));
            if (decodedToken.type !== "user") {
                this.$router.push("/user_login");
            } else {
                this.fetchQuizData();
            }
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
        async fetchQuizData() {
    try {
        const quizId = this.$route.params.quizId;
        this.questions = []; 

        const response = await fetch(`http://127.0.0.1:8080/user/quiz/${quizId}/questions`, {
            headers: { "Authorization": `Bearer ${localStorage.getItem("JWTToken")}` },
        });

        if (!response.ok) throw new Error("Failed to fetch quiz data");

        const data = await response.json();

        this.questions = Array.isArray(data.questions) ? data.questions : data;

        if (this.questions.length === 0) {
            console.warn("No questions found for quiz ID:", quizId);
        }

        this.quiz = await this.getQuizDetails(quizId);

        if (this.quiz.duration) {
            this.startTimer();
        } else {
            console.warn("Quiz data is invalid or missing duration:", this.quiz);
        }
    } catch (error) {
        console.error("Error fetching quiz data:", error);
        this.$router.push("/user_login");
    }
},
markForReview(index) {
    this.questionStatus[index] = "review";
    this.saveAnswer();
},

        saveAnswer() {
    if (!this.currentQuestion || this.selectedOption === null) return;

    const options = [
        this.currentQuestion.option_1,
        this.currentQuestion.option_2,
        this.currentQuestion.option_3,
        this.currentQuestion.option_4,
        this.currentQuestion.option_5,
        this.currentQuestion.option_6
    ];

    let selectedKey = null;
    for (let i = 0; i < options.length; i++) {
        if (options[i] && options[i] === this.selectedOption) {
            selectedKey = `option_${i + 1}`;
            break;
        }
    }

    if (!selectedKey) {
        console.warn("Selected option does not match any known option key.");
        return;
    }

    const answer = {
        question_id: this.currentQuestion.id,
        selected_option: selectedKey
    };

    const existingAnswerIndex = this.answers.findIndex(a => a.question_id === this.currentQuestion.id);
    if (existingAnswerIndex !== -1) {
        this.answers[existingAnswerIndex] = answer;
    } else {
        this.answers.push(answer);
    }

    this.questionStatus[this.currentQuestionIndex] = "answered";
},
        restoreSelectedOption() {
            const savedAnswer = this.answers.find(a => a.question_id === this.currentQuestion?.id);
            this.selectedOption = savedAnswer ? savedAnswer.selected_option : null;
        },
        getQuestionOptions(question) {
            return [
                question.option_1,
                question.option_2,
                ...(question.option_3 ? [question.option_3] : []),
                ...(question.option_4 ? [question.option_4] : [])
            ].filter(Boolean);
        },
        prevQuestion() {
    if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex -= 1;
        this.restoreSelectedOption(); 
    }
},
markAnswered(index) {
    if (!this.selectedOption) return; 
    this.questionStatus[index] = "answered";
    this.saveAnswer();
},
async getQuizDetails(quizId) {
    try {
        const response = await fetch(`http://127.0.0.1:8080/user_dashboard`, {
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
            }
        });

        if (!response.ok) throw new Error("Failed to fetch quiz details");

        const data = await response.json();

        let quizzes = [...(data.attempted_quizzes || []), ...(data.upcoming_quizzes || [])];

        const quiz = quizzes.find(q => q.id === parseInt(quizId));

        if (!quiz) {
            console.warn(`Quiz with ID ${quizId} not found`);
            return {}; 
        }
        return quiz;
    } catch (error) {
        console.error("Error fetching quiz details:", error);
        this.$router.push("/user_login");
        return {}; 
    }
},
startTimer() {
    if (!this.quiz || !this.quiz.duration) {
        console.error("Cannot start timer: quiz data is missing or invalid", this.quiz);
        return;
    }
    if (this.intervalId) clearInterval(this.intervalId); 
    this.timer = parseInt(this.quiz.duration, 10) * 60; 
    console.log("Quiz timer started for:", this.timer, "seconds");

    this.intervalId = setInterval(() => {
        if (this.timer > 0) {
            this.timer -= 1;
        } else {
            clearInterval(this.intervalId); 
            this.submitQuiz();
        }
    }, 1000);
},
handleNavigation(next = true) {
    if (!this.currentQuestion || !Array.isArray(this.questions) || this.questions.length === 0) {
        console.warn("No questions available for navigation.");
        return;
    }

    this.saveAnswer(); 

    if (!["review", "answered"].includes(this.questionStatus[this.currentQuestionIndex])) {
        this.questionStatus[this.currentQuestionIndex] = "visited";
    }

    if (next && this.currentQuestionIndex === this.questions.length - 1) {
        console.log("Submit button clicked!"); 
        this.submitQuiz();
        return; 
    }

    if (next && this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex += 1;
    } else if (!next && this.currentQuestionIndex > 0) {
        this.currentQuestionIndex -= 1;
    } else {
        console.warn("Navigation out of bounds.");
    }

    this.selectedOption = null; 
    this.restoreSelectedOption(); 
},
        formatTimer(seconds) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        },
        navigateToQuestion(index) {
            this.saveAnswer(); 
            this.currentQuestionIndex = index;

            if (this.questionStatus[index] === "notVisited") {
                this.questionStatus[index] = "visited";
            }

            this.restoreSelectedOption(); 
        },
        getButtonClass(index) {
            switch (this.questionStatus[index]) {
                case "visited": return "red";
                case "answered": return "green";
                case "review": return "purple";
                default: return "grey";
            }
        },
        async submitQuiz() {
    console.log("Submit button clicked!"); // Debugging Log

    try {
        if (this.answers.length === 0) {
    alert("You must answer at least one question before submitting.");
    return; // ✅ stop execution
}

        const quizId = this.$route.params.quizId;
        
        const response = await fetch(`http://127.0.0.1:8080/user/quiz/${quizId}/submit`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(this.answers),
        });

        if (!response.ok) throw new Error("Failed to submit quiz");

        const data = await response.json();
        
        alert(`Quiz submitted successfully!`);
        
        // Refresh quizzes after submission
        // In user_quiz.vue
        this.$emit("refreshQuizzes");

        // Redirect to scores page or dashboard
        this.$router.push({ name: "user_scores" });
        
    } catch (error) {
        console.error("Error submitting quiz:", error);
        alert("An error occurred while submitting the quiz.");
    }
},

        toggleSidebar(open) {
            this.isSidebarOpen = open;
        }
    },
};
</script>

<style scoped>
.main-container {
    transition: margin-left 0.3s;
}
.main-container.sidebar-open { 
    margin-left: 250px; 
}
.main-content { 
    display: flex;
    margin-top: 60px;
    min-height: calc(100vh - 60px);
}

.question-sidebar {
    width: 200px;
    background-color: #f8f9fa;
    padding: 20px;
    position: fixed;
    height: calc(100vh - 60px);
    overflow-y: auto;
    border-right: 1px solid #ddd;
}
.question-sidebar h3 { 
    text-align: center;
    margin-bottom: 20px;
    color: #333;
}
.question-sidebar ul { 
    list-style-type: none; 
    padding: 0;
    margin: 0;
}
.question-sidebar li { 
    padding: 12px 15px;
    cursor: pointer;
    border-radius: 4px;
    margin-bottom: 5px;
    transition: all 0.2s;
}
.question-sidebar li:hover {
    background-color: #e9ecef;
}
.question-sidebar li.active {
    background-color: #007bff;
    color: white;
    font-weight: bold;
}
.question-sidebar li.answered {
    background-color: #d4edda;
}
.quiz-container {
    flex: 1;
    margin-left: 220px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    min-height: calc(100vh - 60px);
}
.quiz-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
}
.question-number {
    font-size: 18px;
    font-weight: bold;
    color: #495057;
}
.timer {
    font-size: 18px;
    font-weight: bold;
    color: #dc3545;
    background: #fff3f3;
    padding: 5px 15px;
    border-radius: 20px;
}
.question-content {
    flex: 1;
    padding: 20px 0;
}
.question-title {
    font-size: 24px;
    margin-bottom: 15px;
    color: #212529;
    text-align: center;
}
.question-statement {
    font-size: 18px;
    margin-bottom: 30px;
    color: #495057;
    text-align: center;
}
.options {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-width: 800px;
    margin: 0 auto;
}
.options label {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 20px;
    background: #f8f9fa;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid #dee2e6;
}
.options label:hover {
    background: #e9ecef;
    border-color: #ced4da;
}
.options input[type="radio"] {
    transform: scale(1.2);
    cursor: pointer;
}
.navigation-buttons {
    display: flex;
    justify-content: space-between;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}
.nav-button {
    padding: 10px 25px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
}
.prev-button {
    background: #6c757d;
    color: white;
}
.prev-button:hover {
    background: #5a6268;
}
.next-button {
    background: #28a745;
    color: white;
}
.next-button:hover {
    background: #218838;
}
.question-sidebar ul {
    list-style-type: none;
    padding: 0;
}
.question-sidebar ul li {
    margin-bottom: 5px;
}
.question-btn {
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 5px;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.3s ease;
    text-align: center;
}
.grey { background-color: grey; color: white; }
.red { background-color: red; color: white; }
.green { background-color: green; color: white; }
.purple { background-color: purple; color: white; }
.review-button {
    margin-top: 10px;
    background-color: purple;
    color: white;
    border: none;
    padding: 10px;
    cursor: pointer;
}
.preview-section {
    margin-top: 20px;
}
.legend {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
    max-width: 250px; 
}
.legend .btn {
    padding: 10px;
    border-radius: 5px;
    font-size: 14px;
    text-align: center;
    color: white;
    width: 120px;
}
</style>