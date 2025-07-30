<template>
  <div>
    <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <h2>User Dashboard Summary</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="chart-box"><canvas ref="attemptChart"></canvas></div>
          <div class="chart-box"><canvas ref="scoreChart"></canvas></div>
          <div class="chart-box"><canvas ref="subjectChart"></canvas></div>
          <div class="chart-box"><canvas ref="timeChart"></canvas></div>
          <div class="chart-box"><canvas ref="completionChart"></canvas></div>
          <div class="chart-box"><canvas ref="distributionChart"></canvas></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import user_sidebar from './user_sidebar.vue';

Chart.register(...registerables);

export default {
  components: { user_sidebar },
  data() {
    return {
      isSidebarOpen: false,
      user: {},
      scores: [],
      charts: {},
    };
  },
  mounted() {
    this.initDashboard();
  },
  methods: {
    toggleSidebar(open) {
      this.isSidebarOpen = open;
    },

    async initDashboard() {
      try {
        await this.fetchUserDashboard();
        await this.fetchSummaryScores();
        this.renderCharts();
      } catch (e) {
        console.error('Error initializing dashboard:', e);
      }
    },

    async fetchUserDashboard() {
      const token = localStorage.getItem("JWTToken");
      const response = await fetch("http://127.0.0.1:8080/user_dashboard", {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      this.user = data.user || {};
    },

  
    async fetchSummaryScores() {
  const token = localStorage.getItem("JWTToken");
  const response = await fetch("http://127.0.0.1:8080/user/summary", {
    headers: { Authorization: `Bearer ${token}` }
  });
  const data = await response.json();
  this.scores = data.scores || [];
  this.attemptedCount = data.summary?.attempted || 0;
  this.missedCount = data.summary?.missed || 0;
  this.unattemptedCount = data.summary?.unattempted || 0;
},
    destroyChart(key) {
      if (this.charts[key]) {
        this.charts[key].destroy();
        delete this.charts[key];
      }
    },

    renderCharts() {
      const attempted = this.scores;

      // 1. Attempt Status (Pie)
      this.destroyChart('attemptChart');
this.charts.attemptChart = new Chart(this.$refs.attemptChart.getContext('2d'), {
  type: 'pie',
  data: {
    labels: ['Attempted', 'Missed', 'Unattempted'],
    datasets: [{
      data: [this.attemptedCount, this.missedCount, this.unattemptedCount],
      backgroundColor: ['#4ade80', '#f87171', '#a78bfa']
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: { display: true, text: 'Quiz Attempt Status' },
      legend: { position: 'bottom' }
    }
  }
});


      // 2. Score Trend Over Time (Line)
      const scoreTrend = attempted
        .filter(q => q.timestamp)
        .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

      const trendLabels = scoreTrend.map(q => new Date(q.timestamp).toLocaleDateString());
      const trendScores = scoreTrend.map(q => (q.marks_scored / q.total_score) * 100);

      this.destroyChart('scoreChart');
      this.charts.scoreChart = new Chart(this.$refs.scoreChart.getContext('2d'), {
        type: 'line',
        data: {
          labels: trendLabels,
          datasets: [{
            label: 'Score %',
            data: trendScores,
            borderColor: '#3b82f6',
            fill: false,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          plugins: { title: { display: true, text: 'Score Trend Over Time' } }
        }
      });

      // 3. Avg Score by Subject (Bar)
      const subjectScoresMap = {};
      attempted.forEach(q => {
        const percent = q.total_score ? (q.marks_scored / q.total_score) * 100 : 0;
        if (!subjectScoresMap[q.subject]) subjectScoresMap[q.subject] = [];
        subjectScoresMap[q.subject].push(percent);
      });

      const subjectLabels = Object.keys(subjectScoresMap);
      const avgScores = subjectLabels.map(sub =>
        subjectScoresMap[sub].reduce((a, b) => a + b) / subjectScoresMap[sub].length
      );

      this.destroyChart('subjectChart');
      this.charts.subjectChart = new Chart(this.$refs.subjectChart.getContext('2d'), {
        type: 'bar',
        data: {
          labels: subjectLabels,
          datasets: [{
            label: 'Avg Score %',
            data: avgScores,
            backgroundColor: '#38bdf8'
          }]
        },
        options: {
          responsive: true,
          plugins: { title: { display: true, text: 'Avg Score by Subject' } },
          scales: { y: { beginAtZero: true, max: 100 } }
        }
      });

      // 4. Time Spent per Quiz (Horizontal Bar)
      const quizTimes = attempted.map(q => ({
  label: q.quiz_title,  
  duration: q.time_duration || 0  
}));


      this.destroyChart('timeChart');
      this.charts.timeChart = new Chart(this.$refs.timeChart.getContext('2d'), {
        type: 'bar',
        data: {
          labels: quizTimes.map(q => q.label),
          datasets: [{
            label: 'Time Spent (seconds)',
            data: quizTimes.map(q => q.duration),
            backgroundColor: '#f472b6'
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          plugins: {
            title: { display: true, text: 'Time Spent per Quiz' }
          },
          scales: {
            x: { beginAtZero: true }
          }
        }
      });

      // 5. Completion Rate Over Time (Line)
      const completionMap = {};
      scoreTrend.forEach(q => {
        const date = new Date(q.timestamp).toLocaleDateString();
        completionMap[date] = (completionMap[date] || 0) + 1;
      });

      const completionDates = Object.keys(completionMap).sort((a, b) => new Date(a) - new Date(b));
      const cumulative = [];
      let total = 0;
      completionDates.forEach(date => {
        total += completionMap[date];
        cumulative.push(total);
      });

      this.destroyChart('completionChart');
      this.charts.completionChart = new Chart(this.$refs.completionChart.getContext('2d'), {
        type: 'line',
        data: {
          labels: completionDates,
          datasets: [{
            label: 'Quizzes Completed (Cumulative)',
            data: cumulative,
            fill: true,
            backgroundColor: 'rgba(34,197,94,0.2)',
            borderColor: '#22c55e',
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          plugins: { title: { display: true, text: 'Completion Rate Over Time' } }
        }
      });

      // 6. Quiz Distribution by Subject (Doughnut)
      const distMap = {};
      attempted.forEach(q => {
        distMap[q.subject] = (distMap[q.subject] || 0) + 1;
      });

      const distLabels = Object.keys(distMap);
      const distCounts = distLabels.map(sub => distMap[sub]);

      this.destroyChart('distributionChart');
      this.charts.distributionChart = new Chart(this.$refs.distributionChart.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: distLabels,
          datasets: [{
            data: distCounts,
            backgroundColor: ['#818cf8', '#fca5a5', '#86efac', '#fde68a', '#a5f3fc', '#f9a8d4']
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: { display: true, text: 'Quiz Distribution by Subject' },
            legend: { position: 'bottom' }
          }
        }
      });
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
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

canvas {
  background: #fff;
  border-radius: 10px;
  padding: 6px;
  height: 350px;
  max-width: 240%;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.chart-box {
  background: #fff;
  padding: 8px;
  border-radius: 10px;
  height: 350px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.chart-box:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 2;
}
</style>