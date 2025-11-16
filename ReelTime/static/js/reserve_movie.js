document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById('reservationModal');
    const form = document.getElementById('reservationForm');
    const reserveButtons = document.querySelectorAll('.reserve-btn');
    const showtimesContainer = document.getElementById('showtimesContainer');
    const selectedShowtimeInput = document.getElementById('selectedShowtimeInput');
    const seatsInput = document.getElementById('seats');
    const dateInput = document.getElementById('selectedDate');
    const selectedCinemaName = document.getElementById('selectedCinemaName');

    const seatLayoutContainer = document.getElementById("seatLayoutContainer");
    const selectedSeatsInput = document.getElementById("selectedSeatsInput");

    const confirmReservationUrlPattern = window.confirmReservationUrlPattern;

    // Helper function: render seat layout
    function renderSeatLayout(seatMapArray, reservedSeats, maxSelectable) {
        seatLayoutContainer.innerHTML = "";
        selectedSeatsInput.value = "";
        let selectedSeats = [];

        if (!seatMapArray || seatMapArray.length === 0) {
            seatLayoutContainer.innerHTML = `<p class="no-seats">No seat layout available.</p>`;
            return;
        }

        console.log("Rendering seat layout with:", seatMapArray);

        // Find the minimum and maximum row and column for actual seats
        const seatRows = seatMapArray.filter(seat => seat.type === 'seat').map(seat => seat.row);
        const seatCols = seatMapArray.filter(seat => seat.type === 'seat').map(seat => seat.col);
        
        const minSeatRow = Math.min(...seatRows);
        const maxSeatRow = Math.max(...seatRows);
        const minSeatCol = Math.min(...seatCols);
        const maxSeatCol = Math.max(...seatCols);

        // Find overall max row and col for the entire layout (including screen, exits, etc.)
        const maxRow = Math.max(...seatMapArray.map(seat => seat.row));
        const maxCol = Math.max(...seatMapArray.map(seat => seat.col));

        // Create a 2D matrix to represent the layout
        const matrix = [];
        for (let r = 0; r <= maxRow; r++) {
            const row = [];
            for (let c = 0; c <= maxCol; c++) {
                // Find the seat object for this position
                const seat = seatMapArray.find(s => s.row === r && s.col === c);
                row.push(seat || { type: 'empty', row: r, col: c });
            }
            matrix.push(row);
        }

        // Add screen element
        const screen = document.createElement("div");
        screen.className = "screen";
        screen.textContent = "SCREEN";
        seatLayoutContainer.appendChild(screen);

        // Pre-calculate seat numbering for each row (right to left, skipping non-seats)
        const rowSeatNumbers = {};
        
        matrix.forEach((rowArr, rowIndex) => {
            // Get all seat columns in this row (filter out non-seats)
            const seatColumns = rowArr
                .map((seat, colIndex) => ({ seat, colIndex }))
                .filter(({ seat }) => seat.type === 'seat')
                .sort((a, b) => b.colIndex - a.colIndex); // Sort right to left
            
            // Assign seat numbers (1, 2, 3...) from right to left
            rowSeatNumbers[rowIndex] = {};
            seatColumns.forEach(({ seat, colIndex }, index) => {
                rowSeatNumbers[rowIndex][colIndex] = index + 1;
            });
        });

        // Render the grid
        matrix.forEach((rowArr, rowIndex) => {
            const rowDiv = document.createElement("div");
            rowDiv.className = "seat-row";

            rowArr.forEach((seat, colIndex) => {
                const seatId = `${seat.row}-${seat.col}`;
                const seatBtn = document.createElement("button");
                seatBtn.type = "button";
                seatBtn.className = "seat";
                seatBtn.dataset.seatId = seatId;
                seatBtn.dataset.type = seat.type;

                // Calculate seat label - right to left numbering, skipping non-seats
                let seatLabel = "";
                switch(seat.type) {
                    case 'seat':
                        // Calculate adjusted row letter (A, B, C, etc.) starting from the first seat row
                        const adjustedRowIndex = rowIndex - minSeatRow;
                        // Get the seat number from our pre-calculated mapping
                        const seatNumber = rowSeatNumbers[rowIndex][colIndex];
                        seatLabel = `${String.fromCharCode(65 + adjustedRowIndex)}${seatNumber}`;
                        break;
                    case 'screen':
                        seatLabel = "🎬";
                        break;
                    case 'entrance':
                        seatLabel = "🚪>";
                        break;
                    case 'exit':
                        seatLabel = "🚪<";
                        break;
                    default:
                        seatLabel = "";
                }

                seatBtn.textContent = seatLabel;

                // Apply styles based on seat type
                switch(seat.type) {
                    case 'seat':
                        seatBtn.classList.add("seat-available");
                        // Check if reserved
                        if (reservedSeats.includes(seatId)) {
                            seatBtn.classList.remove("seat-available");
                            seatBtn.classList.add("seat-reserved");
                            seatBtn.disabled = true;
                        }
                        break;
                    case 'screen':
                        seatBtn.classList.add("seat-screen");
                        seatBtn.disabled = true;
                        break;
                    case 'entrance':
                    case 'exit':
                        seatBtn.classList.add("seat-entrance-exit");
                        seatBtn.disabled = true;
                        break;
                    case 'empty':
                        seatBtn.classList.add("seat-empty");
                        seatBtn.disabled = true;
                        break;
                    default:
                        seatBtn.classList.add("seat-empty");
                        seatBtn.disabled = true;
                }

                // Add click event for available seats
                if (seat.type === 'seat' && !reservedSeats.includes(seatId)) {
                    seatBtn.addEventListener("click", function () {
                        if (seatBtn.classList.contains("seat-selected")) {
                            seatBtn.classList.remove("seat-selected");
                            selectedSeats = selectedSeats.filter(s => s !== seatId);
                        } else {
                            if (selectedSeats.length >= maxSelectable) {
                                alert(`You can only select ${maxSelectable} seat(s).`);
                                return;
                            }
                            seatBtn.classList.add("seat-selected");
                            selectedSeats.push(seatId);
                        }
                        selectedSeatsInput.value = JSON.stringify(selectedSeats);
                        updateSelectedSeatsDisplay(selectedSeats, minSeatRow, rowSeatNumbers, matrix);
                    });
                }

                rowDiv.appendChild(seatBtn);
            });

            seatLayoutContainer.appendChild(rowDiv);
        });

        // Add legend
        addSeatLegend();
        updateSelectedSeatsDisplay(selectedSeats, minSeatRow, rowSeatNumbers, matrix);
    }

    function addSeatLegend() {
        const legend = document.createElement("div");
        legend.className = "seat-legend";
        legend.innerHTML = `
            <div class="legend-item">
                <span class="seat-sample seat-available"></span>
                <span>Available</span>
            </div>
            <div class="legend-item">
                <span class="seat-sample seat-selected"></span>
                <span>Selected</span>
            </div>
            <div class="legend-item">
                <span class="seat-sample seat-reserved"></span>
                <span>Reserved</span>
            </div>
            <div class="legend-item">
                <span class="seat-sample seat-entrance-exit">🚪</span>
                <span>Entrance/Exit</span>
            </div>
        `;
        seatLayoutContainer.appendChild(legend);
    }

    function updateSelectedSeatsDisplay(selectedSeats, minSeatRow = 0, rowSeatNumbers = {}, matrix = []) {
        let display = document.getElementById('selectedSeatsDisplay');
        if (!display) {
            display = document.createElement('div');
            display.id = 'selectedSeatsDisplay';
            display.className = 'selected-seats-display';
            seatLayoutContainer.parentNode.insertBefore(display, seatLayoutContainer.nextSibling);
        }
        
        if (selectedSeats.length > 0) {
            const seatLabels = selectedSeats.map(seatId => {
                const [row, col] = seatId.split('-').map(Number);
                // Use the same row adjustment as in the main function
                const adjustedRowIndex = row - minSeatRow;
                // Get the seat number from our pre-calculated mapping
                const seatNumber = rowSeatNumbers[row] ? rowSeatNumbers[row][col] : 0;
                return `${String.fromCharCode(65 + adjustedRowIndex)}${seatNumber}`;
            });
            display.textContent = `Selected Seats: ${seatLabels.join(', ')}`;
            display.style.display = 'block';
        } else {
            display.textContent = 'No seats selected';
            display.style.display = 'block';
        }
    }

    // Helper: load seat map from server
    function loadSeatMap(detailId, date, showtime, maxSelectable) {
        const url = `/movies/get_seat_map/${detailId}/${date}/${encodeURIComponent(showtime)}/`;

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Seat map data received:", data);
                
                if (!data.seat_map) {
                    seatLayoutContainer.innerHTML = `<p class="error">No seat layout available for this showtime.</p>`;
                    return;
                }

                // Parse the seat_map if it's a string
                let seatMapData = data.seat_map;
                if (typeof seatMapData === 'string') {
                    try {
                        seatMapData = JSON.parse(seatMapData);
                    } catch (e) {
                        console.error("Failed to parse seat_map JSON:", e);
                        seatLayoutContainer.innerHTML = `<p class="error">Invalid seat layout data.</p>`;
                        return;
                    }
                }

                const reservedSeats = data.reserved || [];
                renderSeatLayout(seatMapData, reservedSeats, maxSelectable);
            })
            .catch(err => {
                console.error("Failed to load seat map:", err);
                seatLayoutContainer.innerHTML = `<p class="error">Failed to load seat layout: ${err.message}</p>`;
            });
    }

    // New function to convert seat map object to matrix
    function convertSeatMapToMatrix(seatMapObject) {
        if (Array.isArray(seatMapObject)) {
            // If it's already an array, return as-is
            return seatMapObject;
        }

        // If it's an object, convert to matrix format
        const rows = [];
        const rowIndices = Object.keys(seatMapObject).sort();
        
        rowIndices.forEach(rowKey => {
            const rowData = seatMapObject[rowKey];
            const row = [];
            
            if (Array.isArray(rowData)) {
                // If row data is already an array
                rowData.forEach((seat, colIndex) => {
                    if (seat && typeof seat === 'object') {
                        row.push(seat);
                    } else if (seat) {
                        row.push({ type: 'seat', label: seat });
                    } else {
                        row.push(0); // Empty seat
                    }
                });
            } else if (typeof rowData === 'object') {
                // If row data is an object with column indices
                const colIndices = Object.keys(rowData).sort((a, b) => a - b);
                let lastCol = -1;
                
                colIndices.forEach(colKey => {
                    const colIndex = parseInt(colKey);
                    const seat = rowData[colKey];
                    
                    // Fill gaps with empty seats
                    while (lastCol < colIndex - 1) {
                        row.push(0);
                        lastCol++;
                    }
                    
                    if (seat && typeof seat === 'object') {
                        row.push(seat);
                    } else if (seat) {
                        row.push({ type: 'seat', label: seat });
                    } else {
                        row.push(0);
                    }
                    lastCol = colIndex;
                });
            }
            
            rows.push(row);
        });
        
        return rows;
    }

    // Populate showtimes
    function populateShowtimes(showtimesData, detailId) {
        showtimesContainer.innerHTML = "";
        selectedShowtimeInput.value = "";
        seatLayoutContainer.innerHTML = "";
        selectedSeatsInput.value = "";
        seatsInput.value = 1;

        showtimesData.forEach(({time, remaining}) => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "showtime-option btn-secondary";
            btn.textContent = remaining > 0 ? time : `${time} (Sold Out)`;
            if (remaining <= 0) btn.disabled = true;

            btn.addEventListener("click", function () {
                document.querySelectorAll('.showtime-option').forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");
                selectedShowtimeInput.value = time;

                // Ensure date is selected
                if (!dateInput.value) {
                    dateInput.value = new Date().toISOString().slice(0,10);
                }

                loadSeatMap(detailId, dateInput.value, time, parseInt(seatsInput.value));
            });

            showtimesContainer.appendChild(btn);
        });
    }

    // Update seat layout when date or number of seats changes
    dateInput.addEventListener("change", () => {
        const detailId = form.action.split("/").slice(-2)[0];
        if (selectedShowtimeInput.value) {
            loadSeatMap(detailId, dateInput.value, selectedShowtimeInput.value, parseInt(seatsInput.value));
        }
    });

    seatsInput.addEventListener("input", () => {
        const detailId = form.action.split("/").slice(-2)[0];
        if (selectedShowtimeInput.value && dateInput.value) {
            loadSeatMap(detailId, dateInput.value, selectedShowtimeInput.value, parseInt(seatsInput.value));
        }
    });

    // Open modal on reserve button click
    reserveButtons.forEach(button => {
        button.addEventListener("click", function () {
            const detailId = this.getAttribute("data-detail-id");
            const cinemaName = this.getAttribute("data-cinema-name");
            const jsonId = this.getAttribute("data-showtimes-json-id");
            const showtimesScript = document.getElementById(jsonId);

            form.action = confirmReservationUrlPattern.replace("0", detailId);
            selectedCinemaName.textContent = cinemaName;

            let showtimes = [];
            try {
                showtimes = JSON.parse(showtimesScript.textContent.trim());
            } catch(e){ console.error("Invalid JSON", e); }

            dateInput.value = new Date().toISOString().slice(0,10);
            dateInput.min = dateInput.value;

            populateShowtimes(showtimes, detailId);

            modal.style.display = "flex";
        });
    });

    window.onclick = e => { if(e.target===modal) closeModal(); };
    document.addEventListener('keydown', e => { if(e.key==="Escape") closeModal(); });

});