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
    title: "Demon Slayer: Infinity Castle",
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
    poster: "futuristic-sci-fi-movie-poster-tron-ares.jpeg",
    isComingSoon: true,
  },
  {
    id: 102,
    title: "Avatar: Fire and Ash",
    genre: "Adventure",
    rating: "N/A",
    duration: "3h 10m",
    releaseDate: "December 19, 2025",
    poster: "adventure-movie-poster-avatar-fire-ash.jpg",
    isComingSoon: true,
  },
  {
    id: 103,
    title: "Predator: Badlands",
    genre: "Action",
    rating: "N/A",
    duration: "2h 5m",
    releaseDate: "August 1, 2025",
    poster: "action-movie-poster-predator-badlands.webp",
    isComingSoon: true,
  },
  {
    id: 104,
    title: "The Strangers: Chapter 2",
    genre: "Thriller",
    rating: "N/A",
    duration: "1h 45m",
    releaseDate: "October 31, 2025",
    poster: "thriller-movie-poster-strangers-chapter-2.jpg",
    isComingSoon: true,
  },
]

let filteredMovies = [...allMovies]

function renderMovies(movies) {
  const movieGrid = document.getElementById("movieGrid")
  movieGrid.innerHTML = ""

  movies.forEach((movie) => {
    const posterUrl = `${STATIC_URL}images/${movie.poster}`

    if (movie.isComingSoon) {
      // Structure updated to match the final simpler card design
      const comingSoonCard = `
        <div class="movie-card">
          <img src="${posterUrl}" alt="${movie.title}" class="movie-poster">
          <div class="movie-info">
            <div class="movie-title">${movie.title}</div>
            
            <div class="movie-rating">
              <svg class="star-icon" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
              <span>N/A</span>
            </div>
            
            <div class="movie-meta">
              <span>${movie.duration}</span> | <span>${movie.releaseDate}</span>
            </div>
            
            <div class="coming-soon">Coming Soon</div>
            
            <button class="btn btn-accent" style="margin-top: 1rem;" onclick="notifyMe(${movie.id}, '${movie.title}')">
              Notify Me
            </button>
          </div>
        </div>
      `
      movieGrid.innerHTML += comingSoonCard
    } else {
      // Structure updated to match the final simpler card design
      const movieCard = `
        <div class="movie-card">
          <img src="${posterUrl}" alt="${movie.title}" class="movie-poster">
          <div class="movie-info">
            <div class="movie-title">${movie.title}</div>
            
            <div class="movie-rating">
              <svg class="star-icon" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
              <span>${movie.rating}</span>
            </div>
            
            <div class="movie-meta">
              <span>${movie.duration}</span> | <span>${movie.day}</span>
            </div>
            
            <div class="movie-times">
              ${movie.showtimes.map((time) => `<a href="booking.html?id=${movie.id}&time=${encodeURIComponent(time)}" class="time-slot">${time}</a>`).join("")}
            </div>
            
            <div class="movie-price">$${movie.price.toFixed(2)}</div>
            <a href="booking.html?id=${movie.id}" class="btn btn-accent" style="margin-top: 1rem;">Book Tickets</a>
          </div>
        </div>
      `
      movieGrid.innerHTML += movieCard
    }
  })

  // Re-attach showtime button listeners:
  // Since we changed to <a> tags (links) with the class 'time-slot',
  // we don't necessarily need the selection logic here anymore,
  // as selecting a time slot would typically navigate the user.
  // I've commented out the original selection logic, as it seems redundant 
  // with the new `<a>` tag structure intended for navigation/booking.
  /*
  const showtimeButtons = document.querySelectorAll(".time-slot") // Changed selector
  showtimeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const siblings = this.parentElement.querySelectorAll(".time-slot")
      siblings.forEach((btn) => btn.classList.remove("selected"))
      this.classList.add("selected")
    })
  })
  */
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