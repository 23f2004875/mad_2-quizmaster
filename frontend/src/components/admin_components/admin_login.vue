<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Admin Login</h1>
      <h4 v-if="error_msg" class="text-danger">{{ error_msg }}</h4>
      <form @submit.prevent="admin_login">
        <label class="form-label" for="email">Email</label>
        <input v-model="email" class="form-control" type="text" name="email">
        <label class="form-label" for="password">Password</label>
        <input v-model="password" class="form-control" type="password" name="password">
        <button type="submit" class="btn btn-primary">Login</button>
      </form>
      <p class="signup-link">Existing User <router-link to="/user_login">UserLogin</router-link></p>
    </div>
  </div>
</template>
  
<script>
export default {
  name: 'AdminLogin',
  data() {
    return {
      email: '',
      password: '',
      error_msg: ''
    };
  },
  methods: {
    async admin_login() {
      try {
        const response = await fetch("http://127.0.0.1:8080/admin_login", {
          method: "POST",
          headers: { 'Content-Type': "application/json" },
          body: JSON.stringify({
            email: this.email,
            password: this.password
          }),
        });
        const data = await response.json();
        if (data.access_token) {
          localStorage.setItem("JWTToken", data.access_token);
          localStorage.setItem("name", this.email);

           // 👇 Decode the token to extract the role
  const payload = JSON.parse(atob(data.access_token.split('.')[1]));
  localStorage.setItem("role", payload.type);
          this.$router.replace("/admin_dashboard");
        } else {
          this.error_msg = data.message;
        }
      } catch (error) {
        console.error("Error during login:", error);
        this.error_msg = "Login failed. Please try again.";
      }
    }
  }
};
</script>

  
<style>
  html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  height: 100%;
}

.login-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 100vh;
  background-image: url('@/assets/lo.jpg');
  background-size: cover; 
  background-position: center;
  background-repeat: no-repeat;
  width: 100vw; 
  overflow: hidden; 
}

.login-box {
  background: rgba(255, 255, 255, 0.9);
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  width: 370px;
  margin-right: 5%;
}
  .signup-link {
    margin-top: 10px;
    text-align: center;
  }
  </style>