// script.js

/**
 * This script handles the functionality for the main habit tracker page.
 * It fetches habits and tracking data for the last 7 days and renders a table.
 * Single clicks cycle the status (0→1→2→0) and schedule a backend update after 2 seconds.
 * Double-clicking a cell shows a floating menu for explicit status selection.
 */

let openStatusMenu = null; // Holds the currently open status menu (if any)

document.addEventListener('DOMContentLoaded', function () {
    // Calculate the date range for the last 7 days.
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 6);

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
    if (status === 0) {
        return '';
    } else if (status === 1) {
        return '✅'; // Green check mark
    } else if (status === 2) {
        return '❌'; // Red cross mark
    }
    return '';
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
 * It cycles the status (0→1→2→0) and schedules an update after 2 seconds.
 * @param {HTMLElement} cell - The table cell element.
 * @param {MouseEvent} e - The mouse event.
 */
function handleCellClick(cell, e) {
    // Ignore the click if it is flagged to be ignored (after a double-click).
    if (cell.ignoreClick) {
        cell.ignoreClick = false;
        return;
    }
    let currentStatus = parseInt(cell.dataset.status);
    let newStatus = (currentStatus + 1) % 3;
    cell.dataset.status = newStatus;
    cell.textContent = getStatusEmoji(newStatus);

    // Cancel any pending update and schedule a new one after 2 seconds.
    if (cell.pendingUpdateTimer) {
        clearTimeout(cell.pendingUpdateTimer);
    }
    cell.pendingUpdateTimer = setTimeout(() => {
        sendUpdate(cell.dataset.habitId, cell.dataset.date, parseInt(cell.dataset.status), cell);
        cell.pendingUpdateTimer = null;
    }, 2000);
}

/**
 * Handles a double-click event on a cell.
 * It cancels any pending update and shows a floating status selection menu.
 * @param {HTMLElement} cell - The table cell element.
 * @param {MouseEvent} e - The mouse event.
 */
function handleCellDblClick(cell, e) {
    e.stopPropagation();
    // Flag the cell to ignore the subsequent single-click.
    cell.ignoreClick = true;
    if (cell.pendingUpdateTimer) {
        clearTimeout(cell.pendingUpdateTimer);
        cell.pendingUpdateTimer = null;
    }
    showStatusMenu(cell, e);
}

/**
 * Creates a table row for a given habit.
 * @param {Object} habit - The habit object containing 'id', 'name', and 'tracking' array.
 * @param {Array} dates - Array of date strings corresponding to the tracking data.
 * @returns {HTMLElement} The table row element.
 */
function createHabitRow(habit, dates) {
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
        attachCellListeners(cell);
        row.appendChild(cell);
    });

    return row;
}

/**
 * Renders the habit tracking table.
 * @param {Object} data - The JSON data from the backend.
 * @param {string} startDateStr - The start date of the tracking range.
 * @param {string} endDateStr - The end date of the tracking range.
 */
function renderTable(data, startDateStr, endDateStr) {
    const table = document.getElementById('habits-table');
    table.innerHTML = ''; // Clear any previous content.

    // Create header row with dates.
    const headerRow = document.createElement('tr');
    const emptyHeaderCell = document.createElement('th');
    emptyHeaderCell.textContent = 'Habit / Date';
    headerRow.appendChild(emptyHeaderCell);

    const startDate = new Date(startDateStr);
    const endDate = new Date(endDateStr);
    const numDays = Math.round((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;

    const dates = [];
    for (let i = 0; i < numDays; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);
        const dateStr = currentDate.toISOString().split('T')[0];
        dates.push(dateStr);

        const th = document.createElement('th');
        th.textContent = dateStr;
        headerRow.appendChild(th);
    }
    table.appendChild(headerRow);

    // Create a row for each habit using createHabitRow().
    data.habits.forEach(habit => {
        const row = createHabitRow(habit, dates);
        table.appendChild(row);
    });
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

    // Define the status options.
    const statusOptions = [
        { value: 0, icon: '_', label: 'not set' },
        { value: 1, icon: '✅', label: 'done' },
        { value: 2, icon: '❌', label: 'fail' }
    ];

    statusOptions.forEach(option => {
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
            cell.dataset.status = option.value;
            cell.textContent = getStatusEmoji(option.value);
            if (cell.pendingUpdateTimer) {
                clearTimeout(cell.pendingUpdateTimer);
            }
            cell.pendingUpdateTimer = setTimeout(() => {
                sendUpdate(cell.dataset.habitId, cell.dataset.date, parseInt(cell.dataset.status), cell);
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
