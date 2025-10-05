// Authentication pages JavaScript

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
      e.preventDefault()
      const email = document.getElementById("email").value
      const password = document.getElementById("password").value

      if (email && password) {
        alert(`Welcome back! Logging in as ${email}`)
        // Clear form
        loginForm.reset()
      }
    })
  }

  // Register form submission
  const registerForm = document.getElementById("registerForm")
  if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
      e.preventDefault()
      const firstName = document.getElementById("firstName").value
      const lastName = document.getElementById("lastName").value
      const email = document.getElementById("email").value
      const phone = document.getElementById("phone").value
      const password = document.getElementById("password").value
      const confirmPassword = document.getElementById("confirmPassword").value
      const terms = document.getElementById("terms").checked

      if (!terms) {
        alert("Please agree to the Terms of Service and Privacy Policy.")
        return
      }

      if (password !== confirmPassword) {
        alert("Passwords do not match.")
        return
      }

      if (firstName && lastName && email && phone && password) {
        alert(`Account created successfully!\n\nWelcome, ${firstName} ${lastName}!`)
        // Clear form
        registerForm.reset()
      }
    })
  }
})
