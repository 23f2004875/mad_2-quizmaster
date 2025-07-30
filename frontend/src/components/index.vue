<template>
  <div class="landing-page bg-dark text-light d-flex flex-column min-vh-100">
    
    <header class="bg-black py-3 shadow-sm">
      <div class="container d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-lightning-charge text-warning" viewBox="0 0 16 16">
            <path d="M11.251 0a.5.5 0 0 1 .448.724L9.342 5.5h3.67a.5.5 0 0 1 .39.812l-8 10a.5.5 0 0 1-.874-.457l2.357-6.28H2.5a.5.5 0 0 1-.448-.724l5.5-10A.5.5 0 0 1 8 0h3.25z"/>
          </svg>
          <h1 class="h4 mb-0 text-light fw-bold">QuizMaster</h1>
        </div>
      </div>
    </header>

    <main class="flex-grow-1 d-flex align-items-center justify-content-center py-5">
      <div class="container text-center">
        <div class="card bg-secondary text-light p-4 rounded-4 shadow-lg mx-auto" style="max-width: 500px;">
          <h2 class="mb-3 fw-bold">Welcome to QuizMaster</h2>
          <p class="mb-4 text-muted">Challenge your brain with exciting quizzes!</p>

          <div class="row g-3 mb-3">
            <div class="col-12 col-md-6">
              <router-link to="/admin_login" class="text-decoration-none">
                <button class="btn btn-warning w-100 fw-semibold">
                  <i class="bi bi-person-gear me-2"></i> Admin Login
                </button>
              </router-link>
            </div>
            <div class="col-12 col-md-6">
              <router-link to="/user_login" class="text-decoration-none">
                <button class="btn btn-info w-100 fw-semibold">
                  <i class="bi bi-person-circle me-2"></i> User Login
                </button>
              </router-link>
            </div>
          </div>
          New here?<router-link to="/register" class="text-warning text-decoration-underline">Register Now</router-link>
        </div>
      </div>
    </main>

    <footer class="bg-black py-3 text-center text-muted small">
      <p class="mb-0">© 2025 QuizMaster. All rights reserved.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'LandingPage'
}
</script>

<style scoped>
body {
  background-color: #121212;
  font-family: 'Segoe UI', sans-serif;
}
.card {
  background-color: #1e1e1e;
  border: none;
}
.btn-warning, .btn-info {
  color: #000;
}
.btn-warning:hover, .btn-info:hover {
  filter: brightness(90%);
}
a {
  transition: color 0.2s ease;
}
a:hover {
  color: #ffc107 !important;
}
</style>
