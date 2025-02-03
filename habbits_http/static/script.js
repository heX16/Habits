// script.js

/**
 * This script handles the functionality for the main habit tracker page.
 * It fetches habits and tracking data for the last 7 days and renders a table.
 * Clicking on a cell toggles the habit status and updates the backend.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Calculate the date range for the last 7 days
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

    // Fetch habits and tracking data from the backend
    fetch(`/api/habits?start_date=${startDateStr}&end_date=${endDateStr}`)
        .then(response => response.json())
        .then(data => {
            renderTable(data, startDateStr, endDateStr);
        })
        .catch(error => {
            console.error('Error fetching habits:', error);
        });
});

/**
 * Renders the habit tracking table.
 * @param {Object} data - The JSON data from the backend.
 * @param {string} startDateStr - The start date of the tracking range.
 * @param {string} endDateStr - The end date of the tracking range.
 */
function renderTable(data, startDateStr, endDateStr) {
    const table = document.getElementById('habits-table');

    // Create header row with dates
    const headerRow = document.createElement('tr');
    const emptyHeaderCell = document.createElement('th');
    emptyHeaderCell.textContent = 'Habit / Date';
    headerRow.appendChild(emptyHeaderCell);

    const startDate = new Date(startDateStr);
    const endDate = new Date(endDateStr);
    const numDays = (endDate - startDate) / (1000 * 60 * 60 * 24) + 1;

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

    // Create rows for each habit
    data.habits.forEach(habit => {
        const row = document.createElement('tr');
        const habitCell = document.createElement('td');
        habitCell.textContent = habit.name;
        row.appendChild(habitCell);

        habit.tracking.forEach((status, index) => {
            const cell = document.createElement('td');
            cell.textContent = status;
            cell.style.cursor = 'pointer';
            cell.dataset.habitId = habit.id;
            cell.dataset.date = dates[index];
            cell.dataset.status = status;

            // Add click event to toggle status
            cell.addEventListener('click', function () {
                let newStatus = (parseInt(this.dataset.status) === 0) ? 1 : 0;
                updateHabitStatus(this.dataset.habitId, this.dataset.date, newStatus, this);
            });

            row.appendChild(cell);
        });

        table.appendChild(row);
    });
}

/**
 * Sends an update request to the backend to change the habit status.
 * @param {string} habitId - The habit ID.
 * @param {string} date - The date of the status.
 * @param {number} status - The new status.
 * @param {HTMLElement} cell - The table cell element to update.
 */
function updateHabitStatus(habitId, date, status, cell) {
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
        // Update cell display
        cell.textContent = status;
        cell.dataset.status = status;
    })
    .catch(error => {
        console.error('Error updating habit status:', error);
    });
}
