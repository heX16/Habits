// stat.js

/**
 * This script renders the statistics table for a given habit.
 * It fetches data for the previous month and the current month,
 * then builds a table with two rows (Previous Month and Current Month)
 * and 31 columns (days). The background color of each cell depends on the status:
 * 0 - transparent, 1 - lightgreen, 2 - lightcoral.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Compute previous and current month boundaries.
    let now = new Date();
    let currentYear = now.getFullYear();
    let currentMonth = now.getMonth(); // 0-indexed (January = 0)
    let prevMonth, prevYear;
    if (currentMonth === 0) {
        prevMonth = 11;
        prevYear = currentYear - 1;
    } else {
        prevMonth = currentMonth - 1;
        prevYear = currentYear;
    }
    // First day of previous month.
    let prevMonthStart = new Date(prevYear, prevMonth, 1);
    // Last day of current month.
    let currentMonthEnd = new Date(currentYear, currentMonth + 1, 0);

    /**
     * Formats a Date object as 'YYYY-MM-DD'.
     * @param {Date} date
     * @returns {string}
     */
    function formatDate(date) {
        const year = date.getFullYear();
        const month = ('0' + (date.getMonth() + 1)).slice(-2);
        const day = ('0' + date.getDate()).slice(-2);
        return `${year}-${month}-${day}`;
    }

    let startDate = formatDate(prevMonthStart);
    let endDate = formatDate(currentMonthEnd);

    // Number of days in previous and current month.
    let daysInPrevMonth = new Date(prevYear, prevMonth + 1, 0).getDate();
    let daysInCurrentMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    // Fetch data for the specified habit.
    fetch(`/api/habits?start_date=${startDate}&end_date=${endDate}&habit_id=${habitId}`)
        .then(response => response.json())
        .then(data => {
            if(data.habits && data.habits.length > 0) {
                let habit = data.habits[0];
                let tracking = habit.tracking; // Array for the entire date range.
                renderStatTable(tracking, daysInPrevMonth, daysInCurrentMonth);
            } else {
                document.getElementById('stat-container').textContent = 'No data available for this habit.';
            }
        })
        .catch(error => {
            console.error('Error fetching habit statistics:', error);
        });
});

/**
 * Renders the statistics table.
 * @param {Array} tracking - Array of statuses for previous and current month.
 * @param {number} daysInPrevMonth - Number of days in the previous month.
 * @param {number} daysInCurrentMonth - Number of days in the current month.
 */
function renderStatTable(tracking, daysInPrevMonth, daysInCurrentMonth) {
    const container = document.getElementById('stat-container');
    // Create table element.
    const table = document.createElement('table');
    table.style.borderCollapse = 'collapse';
    table.style.width = '100%';

    // Create header row (days 1 to 31).
    const headerRow = document.createElement('tr');
    // First empty header cell.
    const emptyHeader = document.createElement('th');
    emptyHeader.style.border = '1px solid #ccc';
    headerRow.appendChild(emptyHeader);
    for (let i = 1; i <= 31; i++) {
        const th = document.createElement('th');
        th.textContent = i;
        th.style.border = '1px solid #ccc';
        headerRow.appendChild(th);
    }
    table.appendChild(headerRow);

    // Create row for previous month.
    const prevRow = document.createElement('tr');
    const prevLabel = document.createElement('td');
    prevLabel.textContent = 'Previous Month';
    prevLabel.style.border = '1px solid #ccc';
    prevRow.appendChild(prevLabel);
    for (let i = 1; i <= 31; i++) {
        const td = document.createElement('td');
        td.style.border = '1px solid #ccc';
        if (i <= daysInPrevMonth) {
            // Index in tracking array: day-1.
            let status = tracking[i - 1];
            td.style.backgroundColor = getStatusColor(status);
        }
        prevRow.appendChild(td);
    }
    table.appendChild(prevRow);

    // Create row for current month.
    const currRow = document.createElement('tr');
    const currLabel = document.createElement('td');
    currLabel.textContent = 'Current Month';
    currLabel.style.border = '1px solid #ccc';
    currRow.appendChild(currLabel);
    // Current month tracking starts after previous month's days.
    for (let i = 1; i <= 31; i++) {
        const td = document.createElement('td');
        td.style.border = '1px solid #ccc';
        if (i <= daysInCurrentMonth) {
            let status = tracking[daysInPrevMonth + i - 1];
            td.style.backgroundColor = getStatusColor(status);
        }
        currRow.appendChild(td);
    }
    table.appendChild(currRow);

    container.innerHTML = '';
    container.appendChild(table);
}

/**
 * Returns the background color based on status.
 * @param {number} status - The status code.
 * @returns {string} The corresponding background color.
 */
function getStatusColor(status) {
    if (status == 1) {
        return 'lightgreen';
    } else if (status == 2) {
        return 'lightcoral';
    }
    return 'transparent';
}
