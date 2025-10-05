// Global JavaScript for ReelTime Cinema

// Showtime button selection
document.addEventListener("DOMContentLoaded", () => {
  // Handle showtime button clicks
  const showtimeButtons = document.querySelectorAll(".btn-showtime")
  showtimeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      // Remove selected class from siblings
      const siblings = this.parentElement.querySelectorAll(".btn-showtime")
      siblings.forEach((btn) => btn.classList.remove("selected"))
      // Add selected class to clicked button
      this.classList.add("selected")
    })
  })
})
