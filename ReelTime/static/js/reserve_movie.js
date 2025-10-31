// Function defined in the HTML script tag, but repeated here for completeness (and good practice)
// function closeModal() {
//     document.getElementById('reservationModal').style.display = 'none';
// }

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById('reservationModal');
    const form = document.getElementById('reservationForm');
    const reserveButtons = document.querySelectorAll('.reserve-btn');
    const showtimesContainer = document.getElementById('showtimesContainer');
    const selectedShowtimeInput = document.getElementById('selectedShowtimeInput');
    const seatsInput = document.getElementById('seats');
    const dateInput = document.getElementById('selectedDate');
    const selectedCinemaName = document.getElementById('selectedCinemaName');

    // Get the base URL pattern passed from the Django template
    const confirmReservationUrlPattern = window.confirmReservationUrlPattern;

    // Dynamically create a <p> element for remaining seat info if it doesn't exist
    let seatInfo = document.getElementById('seatInfo');
    if (!seatInfo) {
        seatInfo = document.createElement('p');
        seatInfo.id = "seatInfo";
        seatInfo.style.marginTop = "8px";
        seatInfo.style.fontWeight = "500";
        // Place it after the showtimes container
        showtimesContainer.parentNode.insertBefore(seatInfo, showtimesContainer.nextSibling); 
    }

    // Function to populate showtimes buttons
    function populateShowtimes(showtimesData) {
        showtimesContainer.innerHTML = "";
        seatInfo.textContent = "";
        selectedShowtimeInput.value = "";
        seatsInput.value = 1;
        seatsInput.max = 10; // Default max

        if (showtimesData.length === 0) {
            showtimesContainer.innerHTML = "<p class='no-showtimes'>No showtimes available.</p>";
        } else {
            showtimesData.forEach(({time, remaining, max_seats}) => {
                const btn = document.createElement('button');
                btn.type = "button";
                btn.className = "showtime-option btn-secondary"; // Add a class for styling/selection
                btn.textContent = `${time}`;

                // Disable button if no seats remaining
                if (remaining <= 0) {
                     btn.disabled = true;
                     btn.textContent = `${time} (Sold Out)`;
                     btn.className = "showtime-option btn-disabled";
                }
                
                btn.addEventListener('click', function() {
                    // Remove selected class from all buttons
                    document.querySelectorAll('.showtimes-grid .showtime-option').forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');

                    // Set hidden input
                    selectedShowtimeInput.value = time;

                    // Update seat info
                    seatInfo.textContent = `Seats remaining: ${remaining} / ${max_seats}`;

                    // Limit number of seats input
                    seatsInput.max = remaining > 0 ? remaining : 1;
                    seatsInput.value = 1; // Reset to 1 seat upon selecting new time
                });

                showtimesContainer.appendChild(btn);
            });
        }
    }

    reserveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const detailId = this.getAttribute('data-detail-id');
            const cinemaName = this.getAttribute('data-cinema-name');
            const jsonId = this.getAttribute('data-showtimes-json-id');
            const showtimesScript = document.getElementById(jsonId);
            
            // 1. Update form action using the global URL pattern
            form.action = confirmReservationUrlPattern.replace('0', detailId);

            // 2. Update cinema name in the modal summary
            selectedCinemaName.textContent = cinemaName;

            let showtimes = [];
            if (showtimesScript) {
                try {
                    showtimes = JSON.parse(showtimesScript.textContent.trim());
                } catch (err) {
                    console.error("Error parsing showtimes JSON:", err);
                }
            }

            // Set default date to today and prevent backdating
            const today = new Date();
            const todayISO = today.toISOString().substring(0, 10);
            
            dateInput.value = todayISO;
            dateInput.min = todayISO; 
            
            // Populate showtimes immediately on button click
            populateShowtimes(showtimes);

            // 3. Show modal
            modal.style.display = 'flex';
        });
    });

    window.onclick = function(e){ if (e.target === modal) window.closeModal(); };
    document.addEventListener('keydown', e => { if (e.key === 'Escape') window.closeModal(); });
});