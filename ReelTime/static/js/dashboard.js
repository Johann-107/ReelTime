// Dashboard JavaScript for filtering database-driven movies
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("movieSearch");
  const genreFilter = document.getElementById("genreFilter");
  const movieGrid = document.getElementById("movieGrid");

  if (!movieGrid) return; // Exit if no movie grid exists

  function filterMovies() {
    const searchTerm = searchInput.value.toLowerCase();
    const selectedGenre = genreFilter.value.toLowerCase();
    
    const movieCards = movieGrid.querySelectorAll(".movie-card");
    
    movieCards.forEach((card) => {
      const title = card.querySelector("h3").textContent.toLowerCase();
      const genre = card.getAttribute("data-genre") || "";
      
      const matchesSearch = title.includes(searchTerm);
      const matchesGenre = selectedGenre === "all" || genre === selectedGenre;
      
      if (matchesSearch && matchesGenre) {
        card.style.display = "block";
      } else {
        card.style.display = "none";
      }
    });
  }

  // Add event listeners
  if (searchInput) {
    searchInput.addEventListener("input", filterMovies);
  }
  
  if (genreFilter) {
    genreFilter.addEventListener("change", filterMovies);
  }
});
