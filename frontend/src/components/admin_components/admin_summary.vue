<template>
  <div>
    <sidebar @toggle-sidebar="togglesidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <h2>Admin Dashboard Summary</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="chart-box"><canvas ref="qualificationChart"></canvas></div>
          <div class="chart-box"><canvas ref="quizPerSubjectChart"></canvas></div>
          <div class="chart-box"><canvas ref="avgScoreSubjectChart"></canvas></div>
          <div class="chart-box"><canvas ref="userVsAvgChart"></canvas></div>
          <div class="chart-box"><canvas ref="quizPerChapterChart"></canvas></div>
          <div class="chart-box"><canvas ref="subjectAttemptsChart"></canvas></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);
import sidebar from './sidebar.vue';
import axios from 'axios';

export default {
  name: 'admin_summary',
  components: { sidebar },
  data() {
    return {
      isSidebarOpen: false,
      summaryData: null,
      charts: {}
    };
  },
  mounted() {
    if (!localStorage.getItem("JWTToken")) {
      this.$router.push("/admin_login");
    } else {
      this.fetchSummary();
    }
  },
  methods: {
    togglesidebar(open) {
      this.isSidebarOpen = open;
    },
    async fetchSummary() {
      try {
        const token = localStorage.getItem("JWTToken");
        const res = await axios.get("http://127.0.0.1:8080/admin/summary", {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.summaryData = res.data;
        this.renderCharts();
      } catch (err) {
        console.error("Error fetching summary:", err);
      }
    },
    renderCharts() {
      const { qualifications, quiz_per_subject, avg_score_subject, user_vs_avg, quiz_per_chapter, subject_attempts } = this.summaryData;

      this.renderBarChart(this.$refs.qualificationChart, "Users by Qualification", qualifications);
      this.renderDoughnutChart(this.$refs.quizPerSubjectChart, "Quizzes per Subject", quiz_per_subject);
      this.renderLineChart(this.$refs.avgScoreSubjectChart, "Average Score per Subject", avg_score_subject);
      this.renderRadarChart(this.$refs.userVsAvgChart, "User vs Avg Score", this.arrayToObject(user_vs_avg, "username", "avg_score"));
      this.renderPolarChart(this.$refs.quizPerChapterChart, "Quizzes per Chapter", quiz_per_chapter);
      this.renderPieChart(this.$refs.subjectAttemptsChart, "Subject-wise Attempts", subject_attempts);
    },
    arrayToObject(arr, labelKey, valueKey) {
      const obj = {};
      arr.forEach(item => {
        obj[item[labelKey]] = item[valueKey];
      });
      return obj;
    },
    getColors(count) {
  const palette = [
    // "#4e79a7", // Blue
    // "#f28e2b", // Orange
    // "#e15759", // Red
    "#76b7b2", // Teal
    "#59a14f", // Green
    "#edc949", // Yellow
    "#af7aa1", // Purple
    "#ff9da7", // Coral Pink
    // "#9c755f", // Brown
    // "#bab0ab", // Grey
    // "#8c564b", // Dark Brown
    // "#e377c2", // Magenta
    "#17becf"  // Cyan
  ];

  const repeated = Math.ceil(count / palette.length);
  return Array(repeated).fill(palette).flat().slice(0, count);
},
    renderBarChart(canvas, title, dataObj) {
      const ctx = canvas.getContext("2d");
      if (this.charts[title]) this.charts[title].destroy();
      this.charts[title] = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: Object.keys(dataObj),
          datasets: [{
            label: title,
            data: Object.values(dataObj),
            backgroundColor: this.getColors(Object.keys(dataObj).length)
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: title }
          }
        }
      });
    },
    renderDoughnutChart(canvas, title, dataObj) {
      const ctx = canvas.getContext("2d");
      if (this.charts[title]) this.charts[title].destroy();
      this.charts[title] = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(dataObj),
          datasets: [{
            label: title,
            data: Object.values(dataObj),
            backgroundColor: this.getColors(Object.keys(dataObj).length)
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
            title: { display: true, text: title }
          }
        }
      });
    },
    renderLineChart(canvas, title, dataObj) {
      const ctx = canvas.getContext("2d");
      if (this.charts[title]) this.charts[title].destroy();
      this.charts[title] = new Chart(ctx, {
        type: 'line',
        data: {
          labels: Object.keys(dataObj),
          datasets: [{
            label: title,
            data: Object.values(dataObj),
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: '#ff6384',
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: { display: true, text: title }
          }
        }
      });
    },
    renderRadarChart(canvas, title, dataObj) {
      const ctx = canvas.getContext("2d");
      if (this.charts[title]) this.charts[title].destroy();
      this.charts[title] = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: Object.keys(dataObj),
          datasets: [{
            label: title,
            data: Object.values(dataObj),
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: '#4bc0c0',
            pointBackgroundColor: '#4bc0c0'
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: { display: true, text: title }
          }
        }
      });
    },
    renderPolarChart(canvas, title, dataObj) {
      const ctx = canvas.getContext("2d");
      if (this.charts[title]) this.charts[title].destroy();
      this.charts[title] = new Chart(ctx, {
        type: 'polarArea',
        data: {
          labels: Object.keys(dataObj),
          datasets: [{
            label: title,
            data: Object.values(dataObj),
            backgroundColor: this.getColors(Object.keys(dataObj).length)
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: { display: true, text: title },
            legend: { position: 'bottom' }
          }
        }
      });
    },
    renderPieChart(canvas, title, dataObj) {
      const ctx = canvas.getContext("2d");
      if (this.charts[title]) this.charts[title].destroy();
      this.charts[title] = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: Object.keys(dataObj),
          datasets: [{
            label: title,
            data: Object.values(dataObj),
            backgroundColor: this.getColors(Object.keys(dataObj).length)
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: { display: true, text: title },
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
  align-items: center;
  justify-content: center;
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
