// Dashboard Movies JavaScript - Displays 4 movies per page.
// Note: STATIC_URL must be defined in user_dashboard.html.

// --- 1. MOVIE DATA (Only 'Now Showing' movies from your array are relevant for the dashboard) ---
// We'll use the 'allMovies' array, as 'comingSoonMovies' shouldn't show in the primary 'Now Showing' section.
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
    // Add more 'now showing' movies here if you want more pages
];

// --- 2. PAGINATION & DOM SETUP ---
const movieGrid = document.getElementById('movieDashboardGrid');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');

const moviesPerPage = 4;
let currentPage = 1;
const totalPages = Math.ceil(allMovies.length / moviesPerPage);


// --- 3. CORE FUNCTIONS ---

/**
 * Generates the HTML string for a single movie card (Now Showing only).
 * NOTE: The structure mirrors the working part of your movies.js render function.
 * @param {object} movie - The movie data object.
 * @returns {string} The HTML for the movie card.
 */
function createMovieCardHTML(movie) {
    const posterUrl = `${STATIC_URL}images/${movie.poster}`;

    // Generate time slot links
    const timeSlots = movie.showtimes.map((time) => 
        // Note: Using the same URL structure as your movies.js
        `<a href="booking.html?id=${movie.id}&time=${encodeURIComponent(time)}" class="time-slot">${time}</a>`
    ).join("");

    return `
        <div class="movie-card" data-genre="${movie.genre.toLowerCase()}">
            <img src="${posterUrl}" alt="${movie.title}" class="movie-poster" />
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
                    ${timeSlots}
                </div>
                
                <div class="movie-price">$${movie.price.toFixed(2)}</div>
                <a href="booking.html?id=${movie.id}" class="book-btn">Book Tickets</a>
            </div>
        </div>
    `;
}

/**
 * Renders the movies for the current page slice.
 */
function displayMovies() {
    // Calculate start and end indices for slicing the allMovies array
    const startIndex = (currentPage - 1) * moviesPerPage;
    const endIndex = startIndex + moviesPerPage;
    const moviesToShow = allMovies.slice(startIndex, endIndex);

    // Generate HTML for the movies
    const movieHTML = moviesToShow.map(createMovieCardHTML).join('');
    movieGrid.innerHTML = movieHTML;

    // Update button states
    updatePaginationControls();
}

/**
 * Enables/Disables the pagination buttons based on the current page.
 */
function updatePaginationControls() {
    prevPageBtn.disabled = currentPage <= 1;
    nextPageBtn.disabled = currentPage >= totalPages;
}


// --- 4. EVENT LISTENERS ---

nextPageBtn.addEventListener('click', () => {
    if (currentPage < totalPages) {
        currentPage++;
        displayMovies();
        // Scroll to the top of the movie grid for better UX
        movieGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});

prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        displayMovies();
        // Scroll to the top of the movie grid for better UX
        movieGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});


// --- 5. INITIALIZATION ---

// Load the first page of movies when the script runs
document.addEventListener('DOMContentLoaded', displayMovies);