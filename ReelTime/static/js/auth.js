  document.addEventListener("DOMContentLoaded", () => {
    const togglePassword = document.getElementById("togglePassword")
    if (togglePassword) {
      togglePassword.addEventListener("click", () => {
        const passwordInput = document.getElementById("password")
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password"
        passwordInput.setAttribute("type", type)
      })
    }

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

    const registerForm = document.getElementById("registerForm")
    if (registerForm) {
      registerForm.addEventListener("submit", (e) => {
        const password = document.getElementById("password").value
        const confirmPassword = document.getElementById("confirmPassword").value
        const terms = document.getElementById("terms").checked

        if (!terms) {
          e.preventDefault() 
          alert("Please agree to the Terms of Service and Privacy Policy.")
          return
        }

        if (password !== confirmPassword) {
          e.preventDefault() 
          alert("Passwords do not match.")
          return
        }

      })
    }
})
