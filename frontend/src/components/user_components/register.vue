<template>
  <div class="register-container">
    <div class="register-box">
      <h1>User Registration</h1>
      <h4 v-if="error_msg" class="text-danger">{{ error_msg }}</h4>
      <form @submit.prevent="register_user" enctype="multipart/form-data">
        <div class="form-group">
          <label for="username">Username</label>
          <input v-model="username" class="form-control" type="text" name="username" required />
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input v-model="email" class="form-control" type="email" name="email" required />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input v-model="password" class="form-control" type="password" name="password" required />
        </div>

        <div class="form-group">
          <label for="qualification">Qualification</label>
          <input v-model="qualification" class="form-control" type="text" name="qualification" required />
        </div>

        <div class="form-group">
          <label for="dob">Date of Birth</label>
          <input v-model="dob" class="form-control" type="date" name="dob" required />
        </div>

        <div class="form-group">
          <label for="image">Profile Image</label>
          <input @change="handleImageUpload" class="form-control" type="file" name="image" accept="image/*" />
        </div>

        <button type="submit" class="btn btn-primary">Register</button>
      </form>

      <p class="login-link">
        Already have an account? <router-link to="/user_login">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserRegister",
  data() {
    return {
      username: "",
      email: "",
      password: "",
      qualification: "",
      dob: "",
      image: null,
      error_msg: "",
    };
  },
  methods: {
    handleImageUpload(event) {
      this.image = event.target.files[0];
    },
    async register_user() {
      const formData = new FormData();
      formData.append("username", this.username);
      formData.append("email", this.email);
      formData.append("password", this.password);
      formData.append("qualification", this.qualification);
      formData.append("dob", this.dob);
      if (this.image) {
        formData.append("image", this.image);
      }

      try {
        const response = await fetch("http://localhost:8080/register", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          this.error_msg = errorData.error || "Registration failed. Please try again.";
          return;
        }

        alert("Registration successful!");
        this.$router.push("/user_login");
      } catch (error) {
        console.error("Error during registration:", error);
        this.error_msg = "Registration failed. Please try again.";
      }
    },
  },
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 100vh;
  background-image: url('@/assets/lo.jpg');
  background-size: cover;
  background-position: center;
  padding-right: 5%;
  overflow-y: auto;
}

.register-box {
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem;
  border-radius: 10px;
  max-height: 90vh;
  overflow-y: auto;
  width: 420px;
  box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
}

form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-group {
  text-align: left;
}

label {
  font-weight: 500;
  margin-bottom: 4px;
  display: block;
}

input[type="text"],
input[type="email"],
input[type="password"],
input[type="date"],
input[type="file"] {
  width: 100%;
  padding: 8px;
  font-size: 14px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

.btn {
  margin-top: 12px;
  padding: 10px;
  font-weight: bold;
  border-radius: 5px;
  width: 100%;
}

.login-link {
  margin-top: 15px;
  font-size: 14px;
}
</style>
