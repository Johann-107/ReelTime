// Movies page JavaScript
// Note: STATIC_URL must be defined in movies.html before loading this script.

const allMovies = [
  {
    id: 1,
    title: "The Roses",
    genre: "Comedy",
    rating: 7.5,
    duration: "1h 50m",
    day: "Today",
    showtimes: ["10:30 AM", "3:00 PM", "7:30 PM"],
    price: 11.99, 
    poster: "comedy-movie-the-roses.jpg",
  },
  {
    id: 2,
    title: "Demon Slayer: Kimetsu No Yaiba",
    genre: "Action",
    rating: 8.9, 
    duration: "2h 0m", 
    day: "Today",
    showtimes: ["11:00 AM", "4:30 PM", "9:00 PM"], 
    price: 13.99, 
    poster: "anime-demon-slayer.jpg", 
  },
  {
    id: 3,
    title: "The Conjuring: Last Rites",
    genre: "Horror",
    rating: 8.1, 
    duration: "2h 15m", 
    day: "Today",
    showtimes: ["1:00 PM", "5:30 PM", "9:45 PM"], 
    price: 14.99, 
    poster: "horror-the-conjuring.jpg", 
  },
  {
    id: 4,
    title: "Weapons",
    genre: "Thriller",
    rating: 7.8, 
    duration: "2h 5m", 
    day: "Tomorrow",
    showtimes: ["12:00 PM", "3:30 PM", "7:00 PM"], 
    price: 12.99, 
    poster: "thriller-movie-weapons.jpg", 
  },
  {
    id: 5,
    title: "The Fantastic Four: First Steps",
    genre: "Sci-Fi",
    rating: 8.4, 
    duration: "2h 20m", 
    day: "Today",
    showtimes: ["2:30 PM", "6:00 PM", "8:30 PM"], 
    price: 13.99, 
    poster: "scifi-fantastic-four.jpg", 
  },
  {
    id: 6,
    title: "Bambi: The Reckoning",
    genre: "Horror",
    rating: 6.5, 
    duration: "1h 40m", 
    day: "Tomorrow",
    showtimes: ["1:30 PM", "5:00 PM", "8:00 PM"], 
    price: 11.99, 
    poster: "horror-bambi-reckoning.jpg", 
  },
]

const comingSoonMovies = [
  {
    id: 101,
    title: "Tron: Ares",
    genre: "Sci-Fi",
    rating: "N/A",
    duration: "2h 25m", 
    releaseDate: "May 3, 2025", 
    poster: "futuristic-sci-fi-movie-poster-tron-ares.jpeg", // FIX 1: Removed leading slash and corrected extension
    isComingSoon: true,
  },
  {
    id: 102,
    title: "Avatar: Fire and Ash",
    genre: "Adventure",
    rating: "N/A",
    duration: "3h 10m", 
    releaseDate: "December 19, 2025", 
    poster: "adventure-movie-poster-avatar-fire-ash.jpg", // FIX 1: Removed leading slash
    isComingSoon: true,
  },
  {
    id: 103,
    title: "Predator: Badlands",
    genre: "Action",
    rating: "N/A",
    duration: "2h 5m", 
    releaseDate: "August 1, 2025", 
    poster: "action-movie-poster-predator-badlands.webp", // FIX 1: Removed leading slash and corrected extension
    isComingSoon: true,
  },
  {
    id: 104,
    title: "The Strangers: Chapter 2",
    genre: "Thriller",
    rating: "N/A",
    duration: "1h 45m", 
    releaseDate: "October 31, 2025", 
    poster: "thriller-movie-poster-strangers-chapter-2.jpg", // FIX 1: Removed leading slash
    isComingSoon: true,
  },
]

let filteredMovies = [...allMovies]

function renderMovies(movies) {
  const movieGrid = document.getElementById("movieGrid")
  movieGrid.innerHTML = ""

  movies.forEach((movie) => {
    // FIX 2: Construct the full URL using the global STATIC_URL variable
    const posterUrl = `${STATIC_URL}images/${movie.poster}`

    if (movie.isComingSoon) {
      const comingSoonCard = `
        <div class="movie-card">
          <div class="movie-poster-wrapper">
            <img src="${posterUrl}" alt="${movie.title}" class="movie-poster">
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
            <p style="font-size: 1.25rem; font-weight: 600; color: var(--color-primary);">Coming Soon</p>
          </div>
          <div class="movie-footer">
            <button class="btn btn-primary btn-full" onclick="notifyMe(${movie.id}, '${movie.title}')">
              Notify Me
            </button>
          </div>
        </div>
      `
      movieGrid.innerHTML += comingSoonCard
    } else {
      const movieCard = `
        <div class="movie-card">
          <div class="movie-poster-wrapper">
            <img src="${posterUrl}" alt="${movie.title}" class="movie-poster">
            <span class="movie-badge">${movie.genre}</span>
          </div>
          <div class="movie-header">
            <div class="movie-title-row">
              <h3 class="movie-title">${movie.title}</h3>
              <div class="movie-rating">
                <svg class="star-icon" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                <span>${movie.rating}</span>
              </div>
            </div>
            <p class="movie-meta">${movie.duration} • ${movie.day}</p>
          </div>
          <div class="movie-content">
            <div class="showtime-buttons">
              ${movie.showtimes.map((time) => `<button class="btn-showtime">${time}</button>`).join("")}
            </div>
            <p class="movie-price">$${movie.price}</p>
          </div>
          <div class="movie-footer">
            <a href="booking.html?id=${movie.id}" class="btn btn-accent btn-full">Book Tickets</a>
          </div>
        </div>
      `
      movieGrid.innerHTML += movieCard
    }
  })

  // Re-attach showtime button listeners
  const showtimeButtons = document.querySelectorAll(".btn-showtime")
  showtimeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const siblings = this.parentElement.querySelectorAll(".btn-showtime")
      siblings.forEach((btn) => btn.classList.remove("selected"))
      this.classList.add("selected")
    })
  })
}

function filterMovies() {
  const searchTerm = document.getElementById("movieSearch").value.toLowerCase()
  const genreFilter = document.getElementById("genreFilter").value

  const allMoviesIncludingComingSoon = [...allMovies, ...comingSoonMovies]

  filteredMovies = allMoviesIncludingComingSoon.filter((movie) => {
    const matchesSearch = movie.title.toLowerCase().includes(searchTerm)
    const matchesGenre = genreFilter === "all" || movie.genre.toLowerCase() === genreFilter
    return matchesSearch && matchesGenre
  })

  renderMovies(filteredMovies)
}

function notifyMe(movieId, movieTitle) {
  alert(`You'll be notified when "${movieTitle}" is available for booking!`)
}

document.addEventListener("DOMContentLoaded", () => {
  renderMovies([...allMovies, ...comingSoonMovies])

  document.getElementById("movieSearch").addEventListener("input", filterMovies)
  document.getElementById("genreFilter").addEventListener("change", filterMovies)
})