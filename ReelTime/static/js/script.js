// Global JavaScript for ReelTime Cinema

document.addEventListener("DOMContentLoaded", () => {
    const showtimeButtons = document.querySelectorAll(".btn-showtime");
    showtimeButtons.forEach(button => {
        button.addEventListener("click", function () {
            const siblings = this.parentElement.querySelectorAll(".btn-showtime");
            siblings.forEach(btn => btn.classList.remove("selected"));
            this.classList.add("selected");
        });
    });
});