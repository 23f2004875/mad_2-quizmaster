export default function setupFetchInterceptor() {
  console.log("[Interceptor] Setting up fetch interceptor...");

  const originalFetch = window.fetch;

  window.fetch = async (url, options = {}) => {

    const token = localStorage.getItem("JWTToken");
    const role = localStorage.getItem("role");
  
    const isFormData = options.body instanceof FormData;
    const headers = new Headers(options.headers || {});

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    if (!isFormData && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }


    const response = await originalFetch(url, {
      ...options,
      headers,
    });


    if (response.status === 401) {
      alert("Login session expired. Please login again.");
      localStorage.removeItem("JWTToken");
      localStorage.removeItem("role");

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
  