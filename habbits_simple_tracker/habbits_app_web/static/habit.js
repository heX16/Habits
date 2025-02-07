// habit.js

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
    fetch(`./api/habits?start_date=${startDate}&end_date=${endDate}&habit_id=${habitId}`)
        .then(response => response.json())
        .then(data => {
            if(data.habits && data.habits.length > 0) {
                let habit = data.habits[0];
                document.getElementById('habit-name').textContent = habit.name;
                let tracking = habit.tracking;
                renderCalendars(tracking, prevYear, prevMonth, currentYear, currentMonth);
            } else {
                document.getElementById('stat-container').textContent = 'No data available for this habit.';
            }
        })
        .catch(error => {
            console.error('Error fetching habit statistics:', error);
        });
});

/**
 * Renders calendar for a specific month
 * @param {Array} tracking - Array of statuses
 * @param {number} year - Year to render
 * @param {number} month - Month to render (0-11)
 * @param {number} trackingOffset - Offset in tracking array
 * @returns {HTMLElement} Table element with calendar
 */
function renderMonth(tracking, year, month, trackingOffset) {
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];

    const table = document.createElement('table');
    table.className = 'calendar-table';

    // Month header
    const caption = document.createElement('caption');
    caption.textContent = `${monthNames[month]} ${year}`;
    table.appendChild(caption);

    // Week days header
    const headerRow = document.createElement('tr');
    weekDays.forEach(day => {
        const th = document.createElement('th');
        th.textContent = day;
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // Get first day of month and total days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Create calendar grid
    let date = 1;
    for (let i = 0; i < 6; i++) {
        const row = document.createElement('tr');

        for (let j = 0; j < 7; j++) {
            const cell = document.createElement('td');

            if (i === 0 && j < firstDay) {
                // Empty cells before first day
                cell.className = 'empty';
            } else if (date > daysInMonth) {
                // Empty cells after last day
                cell.className = 'empty';
            } else {
                if (date <= daysInMonth) {
                    const status = tracking[trackingOffset + date - 1];
                    const statusOption = getStatusOptions().find(opt => opt.value === status);
                    
                    // Create wrapper for content
                    const contentDiv = document.createElement('div');
                    contentDiv.style.display = 'inline-block';
                    
                    // Add date number
                    contentDiv.textContent = date;
                    
                    // Check if date is in future
                    const cellDate = new Date(year, month, date);
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    
                    // Add current-day class if date matches today
                    if (cellDate.getTime() === today.getTime()) {
                        cell.classList.add('current-day');
                    }
                    
                    if (cellDate > today && (!statusOption || statusOption.value === 0 || statusOption.value === 9)) {
                        cell.style.backgroundColor = '#f5f5f5';  // Серый цвет только для будущих дат со статусом 0 или 9
                    } else if (statusOption) {
                        // Add status indicator
                        if (statusOption.icon) {
                            contentDiv.textContent += statusOption.icon;
                        } else {
                            contentDiv.textContent += statusOption.as_char;
                        }
                        cell.style.backgroundColor = statusOption.color === 'none' ? 'transparent' : statusOption.color;
                    }
                    
                    cell.appendChild(contentDiv);
                    date++;
                }
            }
            row.appendChild(cell);
        }

        table.appendChild(row);
        if (date > daysInMonth) break;
    }

    return table;
}

/**
 * Renders both calendar months
 */
function renderCalendars(tracking, prevYear, prevMonth, currentYear, currentMonth) {
    const container = document.getElementById('stat-container');
    container.innerHTML = '';

    const calendarsDiv = document.createElement('div');
    calendarsDiv.className = 'calendars-container';

    // Previous month calendar
    const prevMonthDays = new Date(prevYear, prevMonth + 1, 0).getDate();
    const prevMonthCalendar = renderMonth(tracking, prevYear, prevMonth, 0);

    // Current month calendar
    const currentMonthCalendar = renderMonth(tracking, currentYear, currentMonth, prevMonthDays);

    calendarsDiv.appendChild(prevMonthCalendar);
    calendarsDiv.appendChild(currentMonthCalendar);
    container.appendChild(calendarsDiv);
}

/**
 * Returns the background color based on status.
 * @param {number} status - The status code.
 * @returns {string} The corresponding background color.
 */
function getStatusColor(status) {
    const options = getStatusOptions();
    const statusOption = options.find(opt => opt.value === status);
    return statusOption ? statusOption.color : 'transparent';
}
