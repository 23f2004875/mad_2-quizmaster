<template>
  <div>
    <sidebar @toggle-sidebar="togglesidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
<Modal v-if="showCreateModal" @close="closeCreateModal">
  <template #header>
    <h5 class="modal-title">Create New Subject</h5>
  </template>

  <label>Subject Name:</label>
  <input v-model="newSubject.name" type="text" class="form-control mb-3" required />

  <label>Description:</label>
  <textarea v-model="newSubject.description" class="form-control mb-3"></textarea>

  <label>Upload Image:</label>
  <input type="file" @change="handleFileUpload" class="form-control mb-3" accept="image/*" />

  <template #footer>
    <button class="btn btn-success" @click="createSubject">Submit</button>
    <button class="btn btn-danger" @click="closeCreateModal">Cancel</button>
  </template>
</Modal>


        <div v-if="error_msg" class="error">{{ error_msg }}</div>

        <div class="search-bar-container">
          <input
            type="text"
            v-model="searchQuery"
            @input="searchSubjects"
            class="search-bar"
            placeholder="Search subjects..."
          />
        </div>

        <div><button class="add-button" @click="openCreateModal">Create new Subject</button></div>

        <div class="container mt-4">
          <div class="row">
            <div
  class="col-lg-4 col-md-6 col-sm-12 mb-4"
  v-for="subject in displayedSubjects"
  :key="subject.id"
  v-if="subject && subject.id && subject.name"
>

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

        <div v-if="showNoResultsMessage" class="alert alert-warning mt-3">
          {{ noResultsMessage }}
          <button type="button" class="btn-close float-end" @click="clearSearch" aria-label="Close"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import sidebar from './sidebar.vue';
import Modal from '@/components/admin_components/Modal.vue';

export default {
  name: 'admin_dashboard',
  components: { sidebar, Modal },
  data() {
    return {
      email: '',
      subjects: [],
      displayedSubjects: [],
      searchQuery: '',
      showNoResultsMessage: false,
      noResultsMessage: 'No subjects found matching your search.',
      error_msg: '',
      isSidebarOpen: false,
      hoveredSubject: null,
      showCreateModal: false,
      newSubject: { name: '', description: '', image: null }
    };
  },
  mounted() {
    this.email = localStorage.getItem("name") || 'Admin';
    if (!localStorage.getItem("JWTToken")) {
      this.$router.push("/admin_login");
    } else {
      this.fetch_data();
    }
  },
  beforeRouteEnter(to, from, next) {
  next(vm => {
    vm.fetch_data(); 
  });
},
  methods: {
    async fetch_data() {
      try {
        const response = await fetch('http://127.0.0.1:8080/admin_dashboard', {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('JWTToken')}`,
            'Content-Type': 'application/json',
          },
        });
        if (!response.ok) throw new Error('Failed to fetch data');
        const data = await response.json();
        this.subjects = Array.isArray(data.subjects) ? data.subjects : [];
        this.displayedSubjects = this.subjects;
      } catch (error) {
        console.error('Error fetching admin data:', error);
      }
    },
    getSubjectImage(subject) {
  // fallback to default image
  if (!subject || !subject.image_url) return 'http://127.0.0.1:8080/static/images/subjects/default.png';
  return `http://127.0.0.1:8080${subject.image_url}`;
},
  handleImageError(event) {
    event.target.onerror = null; // Prevent infinite loop
    event.target.src = '/images/subjects/default.png';
  },
    searchSubjects() {
      const query = this.searchQuery.toLowerCase();
      this.displayedSubjects = this.subjects.filter(subject =>
        subject.name.toLowerCase().includes(query)
      );
      this.showNoResultsMessage = this.displayedSubjects.length === 0;
    },
    clearSearch() {
      this.searchQuery = '';
      this.displayedSubjects = this.subjects;
      this.showNoResultsMessage = false;
    },
    togglesidebar(open) {
      this.isSidebarOpen = open;
    },
    goToSubject(subject_id) {
      this.$router.push(`/admin/subject/${subject_id}`);
    },
    openCreateModal() {
      this.$nextTick(() => {
        this.showCreateModal = true;
      });
    },
    closeCreateModal() {
      this.showCreateModal = false;
      this.newSubject = { name: '', description: '', image: null };
    },
    handleFileUpload(event) {
      this.newSubject.image = event.target.files[0];
    },
 
    async createSubject() {
  if (this.subjects.some(subject => subject.name.toLowerCase() === this.newSubject.name.toLowerCase())) {
    alert("Subject already exists!");
    return;
  }

  let formData = new FormData();
  formData.append("name", this.newSubject.name);
  formData.append("description", this.newSubject.description);
  if (this.newSubject.image) {
    formData.append("image", this.newSubject.image);
  }

  try {
    const response = await fetch("http://127.0.0.1:8080/subject_create", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("JWTToken")}`,
      },
      body: formData,
    });

    const result = await response.json();

    if (response.ok) {
      alert("Subject created successfully!");
      this.subjects.push({
        id: result.id,
        name: this.newSubject.name,
        description: this.newSubject.description,
        image_url: result.image_url || '/static/images/subjects/default.png'
      });
      this.displayedSubjects = [...this.subjects];
      this.closeCreateModal();
    } else {
      alert("Error: " + result.message);
    }
  } catch (error) {
    alert("An error occurred while creating the subject.");
  }
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
.container {
  flex-grow: 1;
}

.row {
  flex-wrap: wrap;
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

.add-button {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 20px auto;
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
.subject-card {
    background: white;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    text-align: center;
    cursor: pointer;
    transition: transform 0.3s ease-in-out;
    margin-bottom: 20px;
}

.subject-card:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.selected {
    background-color: #f8f9fa !important;
    border: 2px solid #151516;
}

.subject-image {
    width: 100%;
    height: 180px;
    object-fit: cover;
    border-radius: 8px;
}

body {
    padding-top: 60px;
}
.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
}
.submit-btn,
.cancel-btn {
  padding: 0.6rem 1.5rem;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.submit-btn {
  background-color: #28a745;
  color: white;
}
.submit-btn:hover {
  background-color: #218838;
}
.cancel-btn {
  background-color: #dc3545;
  color: white;
}
.cancel-btn:hover {
  background-color: #c82333;
}

.error {
    color: red;
}

.search-bar-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.search-bar {
  width: 50%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 16px;
}

.search-bar:focus {
  border-color: #007bff;
}

.search-btn {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
}

.search-btn:hover {
  background-color: #0056b3;
}
</style>

