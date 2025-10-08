// Coming Soon movies data and rendering
const comingSoonMovies = [
  {
    id: 101,
    title: "Quantum Paradox",
    genre: "Sci-Fi",
    rating: "N/A",
    duration: "2h 25m",
    releaseDate: "March 15, 2025",
    poster: `${STATIC_URL}images/futuristic-sci-fi-movie-poster-quantum-paradox.jpg`,
    description: "A mind-bending journey through parallel universes",
  },
  {
    id: 102,
    title: "Desert Kings",
    genre: "Action",
    rating: "N/A",
    duration: "2h 10m",
    releaseDate: "March 22, 2025",
    poster: `${STATIC_URL}images/action-movie-poster-desert-kings.jpg`,
    description: "An epic tale of survival in the unforgiving desert",
  },
  {
    id: 103,
    title: "Midnight Melody",
    genre: "Romance",
    rating: "N/A",
    duration: "1h 50m",
    releaseDate: "April 5, 2025",
    poster: `${STATIC_URL}images/romantic-movie-poster-midnight-melody.jpg`,
    description: "A love story that transcends time and space",
  },
];

function renderComingSoonMovies() {
  const comingSoonGrid = document.getElementById("comingSoonGrid")

  if (!comingSoonGrid) return

  comingSoonGrid.innerHTML = ""

  comingSoonMovies.forEach((movie) => {
    const movieCard = `
      <div class="movie-card">
        <div class="movie-poster-wrapper">
          <img src="${movie.poster}" alt="${movie.title}" class="movie-poster">
          <span class="movie-badge">${movie.genre}</span>
        </div>
        <div class="movie-header">
          <div class="movie-title-row">
            <h3 class="movie-title">${movie.title}</h3>
            <div class="movie-rating">
              <svg class="star-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <span style="font-size: 0.75rem;">Soon</span>
            </div>
          </div>
          <p class="movie-meta">${movie.duration} • ${movie.releaseDate}</p>
        </div>
        <div class="movie-content">
          <p style="font-size: 0.875rem; color: var(--color-text-muted); margin-bottom: 1rem;">
            ${movie.description}
          </p>
        </div>
        <div class="movie-footer">
          <button class="btn btn-primary btn-full" onclick="notifyMe(${movie.id}, '${movie.title}')">
            Notify Me
          </button>
        </div>
      </div>
    `
    comingSoonGrid.innerHTML += movieCard
  })
}

function notifyMe(movieId, movieTitle) {
  alert(`You'll be notified when "${movieTitle}" is available for booking!`)
  // In a real app, this would save the user's notification preference
}

// Render coming soon movies when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  renderComingSoonMovies()
})
