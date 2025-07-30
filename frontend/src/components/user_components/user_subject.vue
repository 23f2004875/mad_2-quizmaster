<template>
  <div>
    <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search subjects..."
          class="search-bar"/>

        <div class="container mt-4">
          <div class="row">
            <div
              class="col-lg-4 col-md-6 col-sm-12 mb-4"
              v-for="subject in filteredSubjects"
              :key="subject.id">
              <div class="subject-card" @click="goToSubject(subject.id)">
                  <img
  :src="getSubjectImage(subject)"
  @error="handleImageError"
  alt="subject image"
  class="subject-image"
/>
                <h3>{{ subject.name }}</h3>
                <p>{{ subject.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="filteredSubjects.length === 0" class="text-center mt-4">
          <p>No subjects match your search.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import user_sidebar from './user_sidebar.vue';

export default {
  components: {
    user_sidebar
  },
  data() {
    return {
      isSidebarOpen: false,
      error_msg: '',
      user: {},
      subjects: [],
      searchQuery: ''
    };
  },
  computed: {
    filteredSubjects() {
      return this.subjects.filter(subject =>
        subject.name.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }},
  methods: {
    toggleSidebar(open) {
      this.isSidebarOpen = open;
    },
    async fetch_data() {
      try {
        const token = localStorage.getItem("JWTToken");
        if (!token) throw new Error("No authentication token found.");

        const [userResponse, subjectResponse] = await Promise.all([
          fetch("http://127.0.0.1:8080/user_dashboard", {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json"
            }
          }),
          fetch("http://127.0.0.1:8080/user/subjects", {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json"
            }
          })
        ]);

        if (!userResponse.ok || !subjectResponse.ok) {
          throw new Error("Failed to fetch user or subjects");
        }

        const userData = await userResponse.json();
        const subjectData = await subjectResponse.json();

        this.user = userData.user || {};
        this.subjects = subjectData || [];
      } catch (error) {
        console.error("Error fetching data:", error);
        this.error_msg = error.message;
      }},
    goToSubject(subjectId) {
      this.$router.push({ name: "user_subject_chapter", params: { subjectId } });
    },
    getSubjectImage(subject) {
  if (!subject || !subject.image_url) return 'http://127.0.0.1:8080/static/images/subjects/default.png';
  return `http://127.0.0.1:8080${subject.image_url}`;
},
  handleImageError(event) {
    event.target.onerror = null; 
    event.target.src = '/images/subjects/default.png';
  }},
  mounted() {
    this.fetch_data();
  }};
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
.subject-card {
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.2s;
  cursor: pointer;
}

.subject-card:hover {
  transform: scale(1.03);
}

.subject-card img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 10px;
}

.search-bar {
  width: 100%;
  max-width: 400px;
  padding: 10px 15px;
  margin: 20px auto;
  display: block;
  border: 1px solid #ccc;
  border-radius: 5px;
}

</style>
