  document.addEventListener("DOMContentLoaded", () => {
    // Password visibility toggle
    const togglePassword = document.getElementById("togglePassword")
    if (togglePassword) {
      togglePassword.addEventListener("click", () => {
        const passwordInput = document.getElementById("password")
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password"
        passwordInput.setAttribute("type", type)
      })
    }

    // Login form submission
    const loginForm = document.getElementById("loginForm")
    if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      const usernameOrEmail = document.getElementById("username_or_email").value
      const password = document.getElementById("password").value

      if (!usernameOrEmail || !password) {
        e.preventDefault() 
        alert("Please fill in both fields before signing in.")
      }
    })
  }

  // Register form submission
    const registerForm = document.getElementById("registerForm")
    if (registerForm) {
      registerForm.addEventListener("submit", (e) => {
        const password = document.getElementById("password").value
        const confirmPassword = document.getElementById("confirmPassword").value
        const terms = document.getElementById("terms").checked

        // 1. Check Terms and Conditions
        if (!terms) {
          e.preventDefault() 
          alert("Please agree to the Terms of Service and Privacy Policy.")
          return
        }

        // 2. Check Password Match
        if (password !== confirmPassword) {
          e.preventDefault() 
          alert("Passwords do not match.")
          return
        }

      })
    }
})
