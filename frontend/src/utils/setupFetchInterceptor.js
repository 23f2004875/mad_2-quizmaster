// src/utils/setupFetchInterceptor.js
export default function setupFetchInterceptor() {
    const originalFetch = window.fetch;
  
    window.fetch = async (url, options = {}) => {
      const token = localStorage.getItem("JWTToken");
      const role = localStorage.getItem("role");
  
      const headers = {
        ...(options.headers || {}),
        Authorization: token ? `Bearer ${token}` : undefined,
        'Content-Type': 'application/json',
      };
  
      const response = await originalFetch(url, {
        ...options,
        headers,
      });
  
      if (response.status === 401) {
        alert("Login session expired. Please login again.");
        localStorage.removeItem("token");
        localStorage.removeItem("role");
  
        // Redirect based on role
        if (role === "admin") {
          window.location.href = "/admin_login";
        } else {
          window.location.href = "/user_login";
        }
  
        return Promise.reject("Unauthorized");
      }
  
      return response;
    };
  }
  