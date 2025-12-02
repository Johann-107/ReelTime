// Hall Form JavaScript

let currentTool = "seat";
let seatCount = 0;

let gridContainer;
let layoutInput;
let capacityInput;

// History management for undo/redo
let history = [];
let historyIndex = -1;
const MAX_HISTORY = 50; // Limit history to prevent memory issues

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize DOM elements
    gridContainer = document.getElementById("grid-container");
    layoutInput = document.getElementById("layout-input");
    capacityInput = document.getElementById("capacity-input");

    // -------------------------------
    // TOOL SELECTOR + ACTIVE BUTTON
    // -------------------------------
    document.querySelectorAll(".tool-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            currentTool = btn.dataset.type;

            // Highlight active button
            document.querySelectorAll(".tool-btn").forEach(b => b.classList.remove("active-tool"));
            btn.classList.add("active-tool");
        });
    });

    // Default active tool = seat
    const defaultTool = document.querySelector('.tool-btn[data-type="seat"]');
    if (defaultTool) {
        defaultTool.classList.add("active-tool");
    }

    // -------------------------------
    // CLEAR GRID BUTTON
    // -------------------------------
    const clearBtn = document.getElementById("clear-grid");
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            seatCount = 0;
            clearGrid();
            saveToHistory();
        });
    }

    // -------------------------------
    // UNDO/REDO BUTTONS
    // -------------------------------
    const undoBtn = document.getElementById("undo-btn");
    const redoBtn = document.getElementById("redo-btn");

    if (undoBtn) {
        undoBtn.addEventListener("click", undo);
    }

    if (redoBtn) {
        redoBtn.addEventListener("click", redo);
    }

    // -------------------------------
    // TRIGGER GRID REBUILD ON ROW/COL CHANGES
    // -------------------------------
    document.getElementById("rows-input").addEventListener("change", regenerateGrid);
    document.getElementById("cols-input").addEventListener("change", regenerateGrid);

    // -------------------------------
    // FORM SUBMIT
    // -------------------------------
    document.getElementById("hall-form").addEventListener("submit", function(e) {
        const cells = document.querySelectorAll(".grid-cell");
        const layout = [];
        let actualSeatCount = 0;

        cells.forEach(c => {
            if (c.dataset.type) {
                layout.push({
                    row: parseInt(c.dataset.row),
                    col: parseInt(c.dataset.col),
                    type: c.dataset.type
                });
                
                // Count actual seats placed on grid
                if (c.dataset.type === "seat") {
                    actualSeatCount++;
                }
            }
        });

        // Validate: Actual seats on grid cannot exceed capacity
        const capacityValue = parseInt(capacityInput.value);
        if (actualSeatCount > capacityValue) {
            e.preventDefault();
            alert(`You have placed ${actualSeatCount} seats on the grid, but the maximum capacity is set to ${capacityValue}. Please remove ${actualSeatCount - capacityValue} seat(s) or increase the capacity.`);
            return false;
        }

        layoutInput.value = JSON.stringify(layout);
    });
});

// -------------------------------
// CREATE GRID FUNCTION
// -------------------------------
function regenerateGrid() {
    const rows = parseInt(document.getElementById("rows-input").value);
    const cols = parseInt(document.getElementById("cols-input").value);

    // Read EXISTING layout from current grid BEFORE clearing
    let currentLayout = [];
    document.querySelectorAll(".grid-cell").forEach(cell => {
        if (cell.dataset.type) {
            currentLayout.push({
                row: parseInt(cell.dataset.row),
                col: parseInt(cell.dataset.col),
                type: cell.dataset.type
            });
        }
    });

    // Rebuild grid UI
    gridContainer.innerHTML = "";
    gridContainer.style.gridTemplateColumns = `repeat(${cols}, 40px)`;

    seatCount = 0; // will recalc below

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            let cell = document.createElement("div");
            cell.className = "grid-cell";
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.addEventListener("click", handleCellClick);
            gridContainer.appendChild(cell);
        }
    }

    // Edited here: Automatically place screen at top row (row 0, all columns)
    for (let c = 0; c < cols; c++) {
        const screenCell = document.querySelector(`.grid-cell[data-row="0"][data-col="${c}"]`);
        if (screenCell) {
            screenCell.dataset.type = "screen";
            screenCell.dataset.locked = "true"; // Lock the screen cells
            applyCellStyle(screenCell, "screen");
        }
    }

    // Restore saved items that still fit in new grid size (skip row 0 as it's reserved for screen)
    currentLayout.forEach(item => {
        // Skip row 0 (screen row) when restoring
        if (item.row > 0 && item.row < rows && item.col < cols) {
            const selector = `.grid-cell[data-row="${item.row}"][data-col="${item.col}"]`;
            const cell = document.querySelector(selector);
            if (cell) {
                cell.dataset.type = item.type;
                applyCellStyle(cell, item.type);
                if (item.type === "seat") {
                    seatCount++;
                }
            }
        }
    });
}

// -------------------------------
// APPLY CELL STYLE
// -------------------------------
function applyCellStyle(cell, type) {
    switch (type) {
        case "seat":
            cell.style.backgroundColor = "#007bff";
            break;
        case "screen":
            cell.style.backgroundColor = "#28a745";
            break;
        case "entrance":
            cell.style.backgroundColor = "#e8b923";
            break;
        case "exit":
            cell.style.backgroundColor = "#dc3545";
            break;
    }
}

// -------------------------------
// CLEAR GRID (Remove all placements)
// -------------------------------
function clearGrid() {
    const rows = parseInt(document.getElementById("rows-input").value);
    const cols = parseInt(document.getElementById("cols-input").value);

    // Rebuild grid UI completely empty
    gridContainer.innerHTML = "";
    gridContainer.style.gridTemplateColumns = `repeat(${cols}, 40px)`;

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            let cell = document.createElement("div");
            cell.className = "grid-cell";
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.addEventListener("click", handleCellClick);
            gridContainer.appendChild(cell);
        }
    }

    // Edited here: Automatically place screen at top row after clearing
    for (let c = 0; c < cols; c++) {
        const screenCell = document.querySelector(`.grid-cell[data-row="0"][data-col="${c}"]`);
        if (screenCell) {
            screenCell.dataset.type = "screen";
            screenCell.dataset.locked = "true"; // Lock the screen cells
            applyCellStyle(screenCell, "screen");
        }
    }
}

// -------------------------------
// HANDLE GRID CLICK
// -------------------------------
function handleCellClick(e) {
    const cell = e.target;
    const capacity = parseInt(capacityInput.value);

    // Edited here: Prevent editing locked screen cells
    if (cell.dataset.locked === "true") {
        alert("The screen is fixed and cannot be moved or removed.");
        return;
    }

    // ⚡ ERASER BEHAVIOR
    if (currentTool === "erase") {
        // If removing a seat, reduce count
        if (cell.dataset.type === "seat") {
            seatCount--;
        }
        delete cell.dataset.type;
        cell.style.backgroundColor = "";
        saveToHistory(); // Save state after change
        return;
    }

    // ⚡ Prevent placing too many seats
    if (currentTool === "seat") {
        if (!cell.dataset.type && seatCount >= capacity) {
            alert("You cannot place more seats than the hall capacity!");
            return;
        }
    }

    // If cell currently has a seat and we're changing tool
    if (cell.dataset.type === "seat" && currentTool !== "seat") {
        seatCount--;
    }

    // Reset cell
    cell.style.backgroundColor = "";
    delete cell.dataset.type;

    // Apply tool type
    cell.dataset.type = currentTool;
    applyCellStyle(cell, currentTool);

    if (currentTool === "seat") {
        seatCount++;
    }

    // Save state after change
    saveToHistory();
}

// -------------------------------
// LOAD EXISTING LAYOUT
// -------------------------------
function loadSavedLayout(savedLayout) {
    if (savedLayout && savedLayout.length > 0) {
        setTimeout(() => {
            regenerateGrid();

            // Edited here: Load saved items but skip row 0 (screen is auto-placed)
            savedLayout.forEach(item => {
                // Skip screen items from saved layout as screen is auto-placed at row 0
                if (item.type === "screen") {
                    return;
                }
                
                const selector = `.grid-cell[data-row="${item.row}"][data-col="${item.col}"]`;
                const cell = document.querySelector(selector);
                if (cell) {
                    cell.dataset.type = item.type;
                    applyCellStyle(cell, item.type);
                    if (item.type === "seat") {
                        seatCount++;
                    }
                }
            });
            
            // Save initial state to history
            saveToHistory();
        }, 10);
    } else {
        setTimeout(() => {
            regenerateGrid();
            // Save initial empty state to history
            saveToHistory();
        }, 10);
    }
}

// Export for use in template
window.loadSavedLayout = loadSavedLayout;

// -------------------------------
// HISTORY MANAGEMENT (UNDO/REDO)
// -------------------------------
function getCurrentState() {
    const cells = document.querySelectorAll(".grid-cell");
    const state = [];
    
    cells.forEach(cell => {
        if (cell.dataset.type) {
            state.push({
                row: parseInt(cell.dataset.row),
                col: parseInt(cell.dataset.col),
                type: cell.dataset.type
            });
        }
    });
    
    return {
        layout: state,
        seatCount: seatCount,
        rows: parseInt(document.getElementById("rows-input").value),
        cols: parseInt(document.getElementById("cols-input").value)
    };
}

function saveToHistory() {
    const state = getCurrentState();
    
    // Remove any future states if we're not at the end
    if (historyIndex < history.length - 1) {
        history = history.slice(0, historyIndex + 1);
    }
    
    // Add new state
    history.push(state);
    
    // Limit history size
    if (history.length > MAX_HISTORY) {
        history.shift();
    } else {
        historyIndex++;
    }
    
    updateHistoryButtons();
}

function restoreState(state) {
    if (!state) return;
    
    // Set grid dimensions if changed
    const rowsInput = document.getElementById("rows-input");
    const colsInput = document.getElementById("cols-input");
    
    if (parseInt(rowsInput.value) !== state.rows || parseInt(colsInput.value) !== state.cols) {
        rowsInput.value = state.rows;
        colsInput.value = state.cols;
    }
    
    // Clear grid
    const rows = state.rows;
    const cols = state.cols;
    
    gridContainer.innerHTML = "";
    gridContainer.style.gridTemplateColumns = `repeat(${cols}, 40px)`;
    
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            let cell = document.createElement("div");
            cell.className = "grid-cell";
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.addEventListener("click", handleCellClick);
            gridContainer.appendChild(cell);
        }
    }
    
    // Restore layout
    seatCount = 0;
    state.layout.forEach(item => {
        const selector = `.grid-cell[data-row="${item.row}"][data-col="${item.col}"]`;
        const cell = document.querySelector(selector);
        if (cell) {
            cell.dataset.type = item.type;
            applyCellStyle(cell, item.type);
            if (item.type === "seat") {
                seatCount++;
            }
        }
    });
}

function undo() {
    if (historyIndex > 0) {
        historyIndex--;
        restoreState(history[historyIndex]);
        updateHistoryButtons();
    }
}

function redo() {
    if (historyIndex < history.length - 1) {
        historyIndex++;
        restoreState(history[historyIndex]);
        updateHistoryButtons();
    }
}

function updateHistoryButtons() {
    const undoBtn = document.getElementById("undo-btn");
    const redoBtn = document.getElementById("redo-btn");
    
    if (undoBtn) {
        undoBtn.disabled = historyIndex <= 0;
    }
    
    if (redoBtn) {
        redoBtn.disabled = historyIndex >= history.length - 1;
    }
}
