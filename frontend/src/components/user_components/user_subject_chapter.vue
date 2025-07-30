<template>
  <div>
    <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <h2>Chapters for Subject: {{ subjectname }}</h2>

        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search chapters..."
          class="search-bar"
        />

        <div class="card-grid">
          <div
            v-for="chapter in filteredChapters"
            :key="chapter.id"
            class="card"
            @click="goToChapterQuizzes(chapter.id)"
          >
            <h3>{{ chapter.title }}</h3>
            <p>{{ chapter.description }}</p>
          </div>
        </div>

        <p v-if="error_msg" class="error">{{ error_msg }}</p>
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
      subjectname: "",      
      chapters: [],
      user: {},
      searchQuery: '',

    };
  },
 computed: {
  subjectId() {
    return this.$route.params.subject_id || this.$route.params.subjectId;
  },
  filteredChapters() {
  return this.chapters.filter(chapter =>
    chapter.title &&
    chapter.title.toLowerCase().includes(this.searchQuery.toLowerCase())
  );
}
},
  methods: {
    async fetchChapters() {
      try {
        const token = localStorage.getItem("JWTToken");
        const response = await fetch(`http://127.0.0.1:8080/user/subject/${this.subjectId}/chapters`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        if (!response.ok) throw new Error("Failed to load chapters");

        const data = await response.json();
        this.subjectname = data.subjectname;  
        this.chapters = data.chapters || [];
      } catch (err) {
        console.error(err);
        this.error_msg = err.message;
      }
    },
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
        this.error_msg = "Failed to load user data.";
      }
    },
    goToChapterQuizzes(chapterId) {
  this.$router.push({
    name: 'user_subject_quiz',
    params: {
      subject_id: this.subjectId,
      chapter_id: chapterId
    }
  });
},
    toggleSidebar(open) {
      this.isSidebarOpen = open;
    }
  },
  mounted() {
    this.fetchUser();
    this.fetchChapters();
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
  height: calc(100vh - 60px);
  overflow-y: scroll;
  scrollbar-width: none;
  -ms-overflow-style: none;
  width: calc(100% - 60px);
}

.main-content::-webkit-scrollbar {
  display: none;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}
.card {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}
.card:hover {
  transform: scale(1.02);
}
.error {
  color: red;
  margin-top: 20px;
}
.search-bar {
  padding: 10px;
  width: 100%;
  max-width: 400px;
  margin: 10px 0 20px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 16px;
}

</style>
