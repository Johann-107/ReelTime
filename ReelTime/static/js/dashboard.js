
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
      const genresData = card.getAttribute("data-genre") || "";
      
      // Parse genres as comma-separated list
      const genres = genresData.split(',').map(g => g.trim().toLowerCase());
      
      const matchesSearch = title.includes(searchTerm);
      const matchesGenre = selectedGenre === "all" || genres.includes(selectedGenre);
      
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


