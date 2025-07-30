<template>
  <div>
    <sidebar @toggle-sidebar="togglesidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <div class="search-bar-container mb-4">
          <input
            type="text"
            v-model="searchQuery"
            class="form-control"
            placeholder="Search chapters or subjects..."
          />
        </div>

        <div class="container">
          <div class="row">
            <div
              class="col-lg-4 col-md-6 col-sm-12 mb-4"
              v-for="chapter in filteredChapters"
              :key="chapter.id"
            >
              <div class="chapter-card" @click="goToChapter(chapter.subject_id)">
                <h3>{{ chapter.name }}</h3>
                <p><strong>Subject:</strong> {{ chapter.subject_name }}</p>
                <p><strong>Description:</strong> {{ chapter.description }}</p>
              </div>
            </div>

            <div v-if="filteredChapters.length === 0" class="text-center mt-4 text-danger">
              No chapters found for "{{ searchQuery }}"
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import sidebar from './sidebar.vue';
export default {
  name: 'admin_chapter',
  data() {
    return {
      isSidebarOpen: false,
      chapters: [],
      searchQuery: ''
    };
  },
  components: {
    sidebar
  },
  computed: {
    filteredChapters() {
      const q = this.searchQuery.toLowerCase();
      return this.chapters.filter(ch =>
        ch.name.toLowerCase().includes(q) ||
        ch.subject_name.toLowerCase().includes(q)
      );
    }
  },
  mounted() {
    if (!localStorage.getItem("JWTToken")) {
      this.$router.push("/admin_login"); 
    } else {
      this.fetchChapters();
    }
  },
  methods: {
    togglesidebar(open) {
      this.isSidebarOpen = open;
    },
    async fetchChapters() {
      try {
        const response = await fetch("http://127.0.0.1:8080/admin/chapters", {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`
          }
        });
        if (!response.ok) throw new Error("Failed to fetch chapters");
        const data = await response.json();
        this.chapters = data.chapters;
      } catch (error) {
        console.error("Error fetching chapters:", error);
      }
    },
    goToChapter(subjectId) {
      this.$router.push(`/admin/subject/${subjectId}`);
    }
  }
}
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

.chapter-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s ease-in-out;
  height: 100%;
}

.chapter-card:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.search-bar-container {
  max-width: 400px;
  margin-bottom: 20px;
}
</style>
