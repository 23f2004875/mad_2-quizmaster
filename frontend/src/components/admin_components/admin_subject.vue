<template>
  <div>
    <sidebar @toggle-sidebar="togglesidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <div v-if="error_msg" class="alert alert-danger">{{ error_msg }}</div>

        <div v-if="subject" class="card p-4">
          <div class="row">
            <div class="col-md-4">
              <img
  :src="getSubjectImage(subject)"
  @error="handleImageError"
  alt="subject image"
  class="subject-image"
/>
            </div>
            <div class="col-md-8">
              <h2>{{ subject.name }}</h2>
              <p>{{ subject.description }}</p>
              <div class="text-center mt-3">
                <button class="btn btn-primary me-2" @click="showAddChapterModal = true">Add Chapter</button>
                <button class="btn btn-warning" @click="openUpdateModal()">Update Subject</button>
                <button @click.stop.prevent="deleteSubject(subject.id, $event)" class="btn btn-danger btn-sm ms-2"><i class="fas fa-trash"></i> Delete</button>
              </div>
            </div>
          </div>

          <h4 class="mt-4">Chapters</h4>
          <table class="table table-striped">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>No. of Quizzes</th>
                <th>Action</th>
                <th>Quiz</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="chapter in chapters" :key="chapter.id">
                <td>{{ chapter.id }}</td>
                <td>{{ chapter.name }}</td>
                <td>{{ chapter.description }}</td>
                <td>{{ chapter.quiz_count }}</td>
                <td>
                  <button class="btn btn-warning btn-sm me-2" @click="openEditChapterModal(chapter)">Edit</button>
                  <button class="btn btn-danger btn-sm" @click="deleteChapter(chapter.id)">Delete</button>
                </td>
                <td>
                  <button class="btn btn-success btn-sm ms-2" @click="goToAdminQuiz(subject.id, chapter.id)">
                    <i class="fas fa-plus"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <Modal v-if="showAddChapterModal" @close="showAddChapterModal = false">
          <template #header>
            <h5 class="modal-title">Add Chapter</h5>
          </template>
          <template #default>
            <input v-model="newChapter.name" class="form-control mb-2" placeholder="Chapter Name">
            <textarea v-model="newChapter.description" class="form-control mb-2" placeholder="Chapter Description"></textarea>
          </template>
          <template #footer>
            <button class="btn btn-secondary" @click="showAddChapterModal = false">Cancel</button>
            <button class="btn btn-primary" @click="addChapter()">Add</button>
          </template>
        </Modal>

        <Modal v-if="showUpdateModal" @close="showUpdateModal = false">
          <template #header>
            <h5 class="modal-title">Update Subject</h5>
          </template>
          <template #default>
            <input v-model="updatedSubject.name" class="form-control mb-2" placeholder="Subject Name">
            <textarea v-model="updatedSubject.description" class="form-control mb-2" placeholder="Subject Description"></textarea>
          </template>
          <template #footer>
            <button class="btn btn-secondary" @click="showUpdateModal = false">Cancel</button>
            <button class="btn btn-success" @click="updateSubject()">Update</button>
          </template>
        </Modal>

        <Modal v-if="showEditChapterModal" @close="showEditChapterModal = false">
          <template #header>
            <h5 class="modal-title">Update Chapter</h5>
          </template>
          <template #default>
            <input v-model="editedChapter.name" class="form-control mb-2" placeholder="Chapter Name">
            <textarea v-model="editedChapter.description" class="form-control mb-2" placeholder="Chapter Description"></textarea>
          </template>
          <template #footer>
            <button class="btn btn-secondary" @click="showEditChapterModal = false">Cancel</button>
            <button class="btn btn-success" @click="updateChapter()">Update</button>
          </template>
        </Modal>
      </div>
    </div>
  </div>
</template>

<script>
import sidebar from './sidebar.vue';
import Modal from '@/components/admin_components/Modal.vue';

export default {
  name: 'SubjectDetails',
  components: {
    sidebar,
    Modal,
  },
  data() {
    return {
      subject: null,
      chapters: [],
      error_msg: '',
      subjectImageFile: null,
      showAddChapterModal: false,
      isSidebarOpen: false,
      showUpdateModal: false,
      showEditChapterModal: false,
      newChapter: { name: '', description: '' },
      updatedSubject: { id: '', name: '', description: '' },
      editedChapter: { id: '', name: '', description: '' }
    };
  },
  watch: {
    $route(to, from) {
      if (to.name === 'admin_dashboard') {
        this.fetch_data();
      }
    }
  },
  mounted() {
    if (!localStorage.getItem("JWTToken")) {
      this.$router.push("/admin_login");
    } else {
      this.fetchSubjectDetails();
      this.$root.$on('refreshChapters', () => {
        this.fetchSubjectDetails();
      });
    }
  },
  methods: {
    goToAdminQuiz(subjectId, chapterId) {
      this.$router.push(`/admin/subject/${subjectId}/chapter/${chapterId}`);
    },
    async fetchSubjectDetails() {
      const subjectId = this.$route.params.subject_id;
      try {
        const response = await fetch(`http://127.0.0.1:8080/admin/subject/${subjectId}`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
            "Content-Type": "application/json",
          },
        });
        if (!response.ok) throw new Error("Failed to fetch subject details");
        const data = await response.json();
        this.subject = data.subject;
        this.chapters = data.chapters;

        this.updatedSubject = { ...this.subject };
      } catch (error) {
        this.error_msg = error.message;
      }
    },

  getSubjectImage(subject) {
  if (!subject || !subject.image_url) return 'http://127.0.0.1:8080/static/images/subjects/default.png';
  return `http://127.0.0.1:8080${subject.image_url}`;
},
  handleImageError(event) {
    event.target.onerror = null; 
    event.target.src = '/images/subjects/default.png';
  },
    togglesidebar(open) {
      this.isSidebarOpen = open;
    },
    async addChapter() {
      if (!this.subject) {
        this.error_msg = "Subject details not loaded.";
        return;
      }
      try {
        const response = await fetch("http://127.0.0.1:8080/chapter_create", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: this.newChapter.name,
            description: this.newChapter.description,
            subject_id: this.subject.id,
          }),
        });
        if (!response.ok) throw new Error("Failed to add chapter");
        this.showAddChapterModal = false;
        this.fetchSubjectDetails();
      } catch (error) {
        this.error_msg = error.message;
      }
    },
    openUpdateModal() {
      this.updatedSubject = { ...this.subject };
      this.showUpdateModal = true;
    },
    
    async updateSubject() {
  try {
    const response = await fetch("http://127.0.0.1:8080/subject_update", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id: this.updatedSubject.id,
        name: this.updatedSubject.name,
        description: this.updatedSubject.description,
      }),
    });

    if (!response.ok) throw new Error("Failed to update subject");
    this.showUpdateModal = false;
    this.fetchSubjectDetails();
  } catch (error) {
    this.error_msg = error.message;
  }
},
    async deleteSubject(subjectId, event) {
  if (event) event.preventDefault();
  if (confirm("Are you sure you want to delete this subject?")) {
    try {
      const response = await fetch(`http://127.0.0.1:8080/subject_delete/${subjectId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
          "Content-Type": "application/json"
        }
      });
      const result = await response.json();
      if (response.ok) {
        alert("Subject deleted successfully!");
        this.$router.push('/admin_dashboard');
      } else {
        alert("Error: " + result.message);
      }
    } catch (error) {
      console.error("Delete error:", error);
      alert("An error occurred while deleting the subject.");
    }
  }
},
    openEditChapterModal(chapter) {
      this.editedChapter = { ...chapter };
      this.showEditChapterModal = true;
    },
    async updateChapter() {
      try {
        const response = await fetch("http://127.0.0.1:8080/chapter_update", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(this.editedChapter),
        });
        if (!response.ok) throw new Error("Failed to update chapter");
        this.showEditChapterModal = false;
        this.fetchSubjectDetails();
      } catch (error) {
        this.error_msg = error.message;
      }
    },
    async deleteChapter(chapterId) {
      try {
        const response = await fetch("http://127.0.0.1:8080/chapter_delete", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${localStorage.getItem("JWTToken")}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ id: chapterId }),
        });
        if (!response.ok) throw new Error("Failed to delete chapter");
        this.fetchSubjectDetails();
      } catch (error) {
        this.error_msg = error.message;
      }
    },
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
.subject-image {
  width: 100%;
  max-width: 400px;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

</style>
