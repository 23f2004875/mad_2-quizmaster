<template>
  <div>
    <user_sidebar :user="user" @toggle-sidebar="toggleSidebar" />
    <div class="main-container" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="main-content">
        <h2>User Profile</h2>

        <div v-if="error_msg" class="text-red-500 mb-2">{{ error_msg }}</div>
        <div v-if="success_msg" class="text-green-600 mb-2">{{ success_msg }}</div>

        <div v-if="user" class="profile-container">
          <div class="left-section">
            <img
  :src="getUserProfileImage(user)"
  @error="handleProfileImageError"
  alt="Profile Image"
  class="profile-img"
/>


            <button @click="showImageInput = !showImageInput">
  {{ showImageInput ? 'Cancel' : 'Change Profile Picture' }}
</button>
<input v-if="showImageInput" type="file" @change="uploadImage" />

          </div>

          <div class="right-section">
            <div v-if="!isEditing">
              <p><strong>Username:</strong> {{ user.username }}</p>
              <p><strong>Email:</strong> {{ user.email }}</p>
              <p><strong>Qualification:</strong> {{ user.qualification }}</p>
              <p><strong>Date of Birth:</strong> {{ user.dob?.split('T')[0] }}</p>
              <button @click="isEditing = true">Edit Profile</button>
            </div>

            <form v-else @submit.prevent="updateProfile">
              <label>Username:</label>
              <input v-model="user.username" />

              <label>Email:</label>
              <input v-model="user.email" readonly />

              <label>Qualification:</label>
              <input v-model="user.qualification" />

              <label>Date of Birth:</label>
              <input v-model="user.dob" type="date" />

              <button type="submit">Save</button>
              <button type="button" @click="isEditing = false">Cancel</button>
            </form>

            <div>
              <button @click="showPasswordForm = !showPasswordForm">
                {{ showPasswordForm ? 'Hide' : 'Change Password' }}
              </button>
              <form v-if="showPasswordForm" @submit.prevent="changePassword">
                <input v-model="oldPassword" placeholder="Old Password" type="password" />
                <input v-model="newPassword" placeholder="New Password" type="password" />
                <button type="submit">Change Password</button>
              </form>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import user_sidebar from './user_sidebar.vue';
import axios from "axios";


export default {
  components: { user_sidebar },
  data() {
    return {
      user: {},
      isSidebarOpen: false,
      oldPassword: '',
      newPassword: '',
      isEditing: false,
      showPasswordForm: false,
      error_msg: '',
      success_msg: '',
      showImageInput: false,
    };
  },
  methods: {
  
    async fetchUser() {
  try {
    const token = localStorage.getItem("JWTToken");
    const res = await fetch("http://127.0.0.1:8080/user_dashboard", {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json();

    if (data.user.dob) {
      data.user.dob = data.user.dob.split('T')[0]; 
    }

    this.user = data.user;
  } catch {
    this.error_msg = "Failed to load user.";
  }
},
async updateProfile() {
  try {
    const token = localStorage.getItem("JWTToken");
    const res = await fetch("http://127.0.0.1:8080/user/update_profile", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: this.user.username,
        qualification: this.user.qualification,
        dob: this.user.dob
      })
    });

    const data = await res.json();

    if (!res.ok) {
      this.error_msg = data.message || "Profile update failed.";
      this.success_msg = "";
    } else {
      this.error_msg = "";
      this.success_msg = data.message;
      this.isEditing = false;
      this.fetchUser();
    }
  } catch (err) {
    this.error_msg = "Failed to fetch. Please check server or internet.";
    this.success_msg = "";
    console.error(err);
  }
},   
async changePassword() {
      try {
        const token = localStorage.getItem("JWTToken");
        const res = await fetch("http://127.0.0.1:8080/user/change_password", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            old_password: this.oldPassword,
            new_password: this.newPassword
          })
        });
        const data = await res.json();

        if (!res.ok) {
          this.error_msg = data.message || "Password change failed.";
        } else {
          this.success_msg = data.message;
          this.error_msg = "";
        }
      } catch (err) {
        this.error_msg = "Network error during password change.";
        this.success_msg = "";
      }
    },

uploadImage(event) {
  const file = event.target.files[0];
  const formData = new FormData();
  formData.append("image", file);

  const token = localStorage.getItem("JWTToken"); 
  console.log("Token being sent:", token); 

  axios
    .post("http://127.0.0.1:8080/user/upload_profile_image", formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data"
      }
    })
    .then((res) => {
      console.log("Upload success:", res.data);
      this.fetchUser();
      this.showImageInput = false;
    })
    .catch((err) => {
      console.error("Upload failed:", err.response?.data || err);
    });
},  
getUserProfileImage(user) {
  if (!user || !user.image_url) {
    return 'http://127.0.0.1:8080/static/images/profile/default.png';
  }
  const timestamp = new Date().getTime(); 
  return `http://127.0.0.1:8080${user.image_url}?t=${timestamp}`;
},
    handleProfileImageError(event) {
      event.target.onerror = null;
      event.target.src = 'http://127.0.0.1:8080/static/images/profile/default.png';
    },

    toggleSidebar(open) {
      this.isSidebarOpen = open;
    }
  },
  mounted() {
    this.fetchUser();
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
  padding: 30px;
  height: calc(100vh - 60px);
  overflow-y: auto;
  width: calc(100% - 60px);
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.main-content::-webkit-scrollbar {
  display: none;
}

.profile-container {
  display: flex;
  flex-wrap: wrap;
  gap: 40px;
  margin-top: 20px;
  background: #fff;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.left-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 250px;
}

.profile-img {
  width: 220px;
  height: 220px;
  border-radius: 50%;
  margin-bottom: 15px;
  object-fit: cover;
  border: 4px solid #1976d2;
}

.right-section {
  flex: 1;
  min-width: 300px;
}

form {
  margin-top: 15px;
}

input {
  display: block;
  width: 100%;
  margin: 10px 0;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 15px;
}

button {
  padding: 8px 16px;
  margin-top: 10px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button[type="button"] {
  background-color: #888;
  margin-left: 10px;
}

button:hover {
  opacity: 0.9;
}

h2 {
  margin-bottom: 20px;
}

.text-red-500 {
  color: #e53935;
}

.text-green-600 {
  color: #43a047;
}
</style>

