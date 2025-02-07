// script.js

/**
 * This script handles the functionality for the main habit tracker page.
 * It fetches habits and tracking data for the last 7 days and renders a table.
 * Single clicks cycle the status (0→1→2→0) and schedule a backend update after 2 seconds.
 * Double-clicking a cell shows a floating menu for explicit status selection.
 */

let openStatusMenu = null; // Holds the currently open status menu (if any)

/**
 * Variables to handle double-click issue:
 * When user double-clicks, browser first triggers single click, which changes the cell state,
 * then triggers double click. These variables help to:
 * 1. Track which cell was clicked (lastClickedCell)
 * 2. Remember its original state (lastClickedStatus)
 * 3. Measure time between clicks (lastClickTime)
 * This allows us to restore the original state when double-click is detected,
 * preventing unwanted state change from the first click.
 */
let lastClickedCell = null;
let lastClickedStatus = null;
let lastClickTime = 0;

document.addEventListener('DOMContentLoaded', function () {
    // Calculate the date range ending with Sunday
    const now = new Date();
    const currentDay = now.getDay(); // 0 (Sun) to 6 (Sat)
    const endDate = new Date(now); // Clone current date
    
    // Adjust to next Sunday if not already Sunday
    const daysToSunday = currentDay === 0 ? 0 : 7 - currentDay;
    endDate.setDate(now.getDate() + daysToSunday);
    
    // Set start date by going back from end date
    const startDate = new Date(endDate);
    startDate.setDate(endDate.getDate() - (tableDaysCount - 1));

    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = ('0' + (date.getMonth() + 1)).slice(-2);
        const day = ('0' + date.getDate()).slice(-2);
        return `${year}-${month}-${day}`;
    };

    const startDateStr = formatDate(startDate);
    const endDateStr = formatDate(endDate);

    // Fetch habits and tracking data from the backend.
    fetch(`/api/habits?start_date=${startDateStr}&end_date=${endDateStr}`)
        .then(response => response.json())
        .then(data => {
            renderTable(data, startDateStr, endDateStr);
        })
        .catch(error => {
            console.error('Error fetching habits:', error);
        });

    // Listen for clicks on the document to dismiss the status menu.
    document.addEventListener('click', function (e) {
        if (openStatusMenu && !openStatusMenu.contains(e.target)) {
            removeStatusMenu();
        }
    });
});

/**
 * Returns a display string (emoji) based on the habit status.
 * @param {number} status - The status code (0, 1, or 2).
 * @returns {string} The corresponding emoji or an empty string.
 */
function getStatusEmoji(status) {
    const option = getStatusOptions().find(opt => opt.value === status);
    return option ? option.icon : '';
}

/**
 * Attaches click and double-click event listeners to a table cell.
 * @param {HTMLElement} cell - The table cell element.
 */
function attachCellListeners(cell) {
    cell.addEventListener('click', function (e) {
        handleCellClick(cell, e);
    });
    cell.addEventListener('dblclick', function (e) {
        handleCellDblClick(cell, e);
    });
}

/**
 * Handles a single click event on a cell.
 * It cycles the status and schedules an update after 2 seconds.
 * @param {HTMLElement} cell - The table cell element.
 * @param {MouseEvent} e - The mouse event.
 */
function handleCellClick(cell, e) {
    const currentTime = new Date().getTime();
    
    if (lastClickedCell !== cell || (currentTime - lastClickTime) > 300) {
        lastClickedCell = cell;
        lastClickedStatus = parseInt(cell.dataset.status);
        lastClickTime = currentTime;
        
        let currentStatus = parseInt(cell.dataset.status);
        let newStatus;
        switch(currentStatus) {
            case 0:
                newStatus = 1; // not set -> done mini
                break;
            case 1:
                newStatus = 2; // done mini -> done
                break;
            case 2:
                newStatus = 3; // done -> done elite
                break;
            case 3:
                newStatus = 9; // done elite -> fail
                break;
            case 9:
                newStatus = 0; // fail -> not set
                break;
            default:
                newStatus = 0;
        }
        
        cell.dataset.status = newStatus;
        cell.textContent = getStatusEmoji(newStatus);

        if (cell.pendingUpdateTimer) {
            clearTimeout(cell.pendingUpdateTimer);
        }
        
        cell.pendingUpdateTimer = setTimeout(() => {
            const status = parseInt(cell.dataset.status);
            // Play animation at the same time as sending update
            if (status === 3) {
                playFireworkAnimation(cell, true);
            } else if (status === 2) {
                playFireworkAnimation(cell, false);
            }
            sendUpdate(cell.dataset.habitId, cell.dataset.date, status, cell);
            cell.pendingUpdateTimer = null;
        }, 2000);
    }
}

/**
 * Handles a double-click event on a cell.
 * It cancels any pending update and shows a floating status selection menu.
 * @param {HTMLElement} cell - The table cell element.
 * @param {MouseEvent} e - The mouse event.
 */
function handleCellDblClick(cell, e) {
    e.stopPropagation();
    
    // Cancel update timer if exists
    if (cell.pendingUpdateTimer) {
        clearTimeout(cell.pendingUpdateTimer);
        cell.pendingUpdateTimer = null;
    }
    
    // Restore previous state
    if (lastClickedCell === cell && lastClickedStatus !== null) {
        cell.dataset.status = lastClickedStatus;
        cell.textContent = getStatusEmoji(lastClickedStatus);
    }
    
    // Clear last click information
    lastClickedCell = null;
    lastClickedStatus = null;
    lastClickTime = 0;
    
    // Show menu
    showStatusMenu(cell, e);
}

/**
 * Renders the habit tracking table.
 * @param {Object} data - The JSON data from the backend.
 * @param {string} startDateStr - The start date of the tracking range.
 * @param {string} endDateStr - The end date of the tracking range.
 */
function renderTable(data, startDateStr, endDateStr) {
    const table = document.getElementById('habits-table');
    table.innerHTML = '';

    const headerRow = document.createElement('tr');
    const emptyHeaderCell = document.createElement('th');
    emptyHeaderCell.textContent = 'Habit / Date';
    headerRow.appendChild(emptyHeaderCell);

    const startDate = new Date(startDateStr);
    const endDate = new Date(endDateStr);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time part for correct comparison

    const dates = [];
    for (let i = 0; i < tableDaysCount; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);
        const dateStr = currentDate.toISOString().split('T')[0];
        dates.push(dateStr);

        const th = document.createElement('th');
        const dayOfMonth = currentDate.getDate();
        const dayOfWeek = weekDays[currentDate.getDay()];
        th.textContent = `${dayOfMonth} ${dayOfWeek}`;
        
        // Подсветка текущего дня и будущих дней
        if (currentDate.getFullYear() === today.getFullYear() &&
            currentDate.getMonth() === today.getMonth() &&
            currentDate.getDate() === today.getDate()) {
            th.classList.add('current-day');
        } else if (currentDate > today) {
            th.classList.add('future-day');
        }
        
        headerRow.appendChild(th);
    }
    table.appendChild(headerRow);

    // Create a row for each habit using createHabitRow().
    data.habits.forEach(habit => {
        const row = createHabitRow(habit, dates, today);
        table.appendChild(row);
    });
}

/**
 * Creates a table row for a given habit.
 * @param {Object} habit - The habit object containing 'id', 'name', and 'tracking' array.
 * @param {Array} dates - Array of date strings corresponding to the tracking data.
 * @param {Date} today - The current date.
 * @returns {HTMLElement} The table row element.
 */
function createHabitRow(habit, dates, today) {
    const row = document.createElement('tr');

    // Create the habit name cell.
    const habitCell = document.createElement('td');
    const habitLink = document.createElement('a');
    habitLink.href = '/stat/' + habit.id;
    habitLink.textContent = habit.name;
    habitCell.appendChild(habitLink);
    row.appendChild(habitCell);

    // Create cells for each tracking status.
    habit.tracking.forEach((status, index) => {
        const cell = document.createElement('td');
        cell.textContent = getStatusEmoji(status);
        cell.style.cursor = 'pointer';
        cell.dataset.habitId = habit.id;
        cell.dataset.date = dates[index];
        cell.dataset.status = status;
        
        // Проверяем, является ли дата будущей
        const cellDate = new Date(dates[index]);
        cellDate.setHours(0, 0, 0, 0);
        if (cellDate > today) {
            cell.classList.add('future-day');
            // Отключаем интерактивность для будущих дней
            cell.style.cursor = 'default';
        } else {
            attachCellListeners(cell);
        }
        
        row.appendChild(cell);
    });

    return row;
}

/**
 * Displays a floating status selection menu near the specified cell.
 * @param {HTMLElement} cell - The table cell element.
 * @param {MouseEvent} event - The mouse event (used for positioning).
 */
function showStatusMenu(cell, event) {
    // Remove any existing menu first.
    removeStatusMenu();

    // Create the menu container.
    const menu = document.createElement('div');
    menu.style.position = 'absolute';
    menu.style.backgroundColor = 'white';
    menu.style.border = '1px solid #ccc';
    menu.style.padding = '5px';
    menu.style.zIndex = 1000;
    menu.style.boxShadow = '2px 2px 6px rgba(0,0,0,0.2)';

    // Create a table for the menu items.
    const menuTable = document.createElement('table');
    menuTable.style.borderCollapse = 'collapse';

    getStatusOptions().forEach(option => {
        const row = document.createElement('tr');
        row.style.cursor = 'pointer';
        row.style.borderBottom = '1px solid #ddd';

        // Create the icon cell.
        const iconCell = document.createElement('td');
        iconCell.textContent = option.icon;
        iconCell.style.padding = '4px 8px';
        row.appendChild(iconCell);

        // Create the label cell.
        const labelCell = document.createElement('td');
        labelCell.textContent = option.label;
        labelCell.style.padding = '4px 8px';
        row.appendChild(labelCell);

        // When a menu option is clicked, update the cell accordingly.
        row.addEventListener('click', function (e) {
            e.stopPropagation();
            const newStatus = option.value;
            cell.dataset.status = newStatus;
            cell.textContent = option.icon;
            
            if (cell.pendingUpdateTimer) {
                clearTimeout(cell.pendingUpdateTimer);
            }
            
            cell.pendingUpdateTimer = setTimeout(() => {
                const status = parseInt(cell.dataset.status);
                // Play animation at the same time as sending update
                if (status === 3) {
                    playFireworkAnimation(cell, true);
                } else if (status === 2) {
                    playFireworkAnimation(cell, false);
                }
                sendUpdate(cell.dataset.habitId, cell.dataset.date, status, cell);
                cell.pendingUpdateTimer = null;
            }, 2000);
            
            removeStatusMenu();
        });

        menuTable.appendChild(row);
    });

    menu.appendChild(menuTable);

    // Position the menu relative to the cell.
    const rect = cell.getBoundingClientRect();
    menu.style.top = (rect.bottom + window.scrollY) + 'px';
    menu.style.left = (rect.left + window.scrollX) + 'px';

    document.body.appendChild(menu);
    openStatusMenu = menu;
}

/**
 * Removes the currently open status menu (if any).
 */
function removeStatusMenu() {
    if (openStatusMenu) {
        openStatusMenu.remove();
        openStatusMenu = null;
    }
}

/**
 * Sends an update request to the backend to change the habit status.
 * @param {string} habitId - The habit ID.
 * @param {string} date - The date of the status.
 * @param {number} status - The new status.
 * @param {HTMLElement} cell - The table cell element (for logging purposes).
 */
function sendUpdate(habitId, date, status, cell) {
    fetch('/api/habits/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            habit_id: parseInt(habitId),
            date: date,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Update successful for habit', habitId, 'on', date, ':', data);
    })
    .catch(error => {
        console.error('Error updating habit status:', error);
    });
}

/**
 * Creates and plays a firework animation near the cell
 * @param {HTMLElement} cell - The table cell element to show firework near
 * @param {boolean} isElite - Whether this is an elite status animation (more particles)
 */
function playFireworkAnimation(cell, isElite = false) {
    const emojis = ['✨', '🌟', '⭐', '💫', '🎇'];
    const rect = cell.getBoundingClientRect();
    
    // Add scroll offset to get absolute position
    const centerX = rect.left + rect.width / 2 + window.scrollX;
    const centerY = rect.top + rect.height / 2 + window.scrollY;

    // Number of particles based on status
    const particleCount = isElite ? 10 : 3;

    // Create particles
    for (let i = 0; i < particleCount; i++) {
        const firework = document.createElement('div');
        firework.className = 'firework';
        
        // Calculate angle for circular distribution
        const angle = (i / particleCount) * 2 * Math.PI + Math.random() * 0.5;
        const distance = 25 + Math.random() * 75;
        
        // Calculate final position using angle and distance
        const offsetX = Math.cos(angle) * distance;
        const offsetY = Math.sin(angle) * distance;
        
        // Start from center, adjusting for element size
        firework.style.left = (centerX - 8) + 'px';
        firework.style.top = (centerY - 8) + 'px';
        
        firework.style.setProperty('--final-x', `${offsetX}px`);
        firework.style.setProperty('--final-y', `${offsetY}px`);
        
        // Randomize animation parameters
        const delay = Math.random() * 0.2;
        const duration = 1.8 + Math.random() * 0.4;
        // Slightly smaller scale for regular done status
        const scale = isElite ? (2.4 + Math.random() * 1.2) : (1.8 + Math.random() * 0.8);
        
        firework.style.animationDelay = `${delay}s`;
        firework.style.animationDuration = `${duration}s`;
        firework.style.fontSize = `${16 * scale}px`;
        
        // Randomly select emoji
        const emoji = emojis[Math.floor(Math.random() * emojis.length)];
        firework.setAttribute('data-emoji', emoji);
        
        document.body.appendChild(firework);
        
        setTimeout(() => {
            firework.remove();
        }, (delay + duration) * 1000);
    }
}
