<template>
  <Doughnut :data="chartData" :options="chartOptions" />
</template>

<script>
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, ArcElement);

export default {
  name: 'ScorePieChart',
  components: { Doughnut },
  props: {
    correct: Number,
    wrong: Number,
    unattempted: Number
  },
  computed: {
    chartData() {
      return {
        labels: ['Correct', 'Wrong', 'Unattempted'],
        datasets: [
          {
            data: [this.correct, this.wrong, this.unattempted],
            backgroundColor: ['#4caf50', '#f44336', '#9e9e9e'],
            borderWidth: 1
          }
        ]
      };
    },
    chartOptions() {
      return {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      };
    }
  }
};
</script>
<style scoped>
.chart-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 16px;
}
</style>
