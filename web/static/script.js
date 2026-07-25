// URL: http://server.test/habits/static/script.js
// Used on: http://server.test/habits/

/**
 * This script handles the functionality for the main habit tracker page.
 * It fetches habits and tracking data for the last 7 days and renders a table.
 * Single clicks cycle the status (0→1→...→0) and enqueue a backend update.
 * A global queue drains all pending updates on each 1s tick (sequentially, awaiting
 * each response). Double-clicking a cell shows a floating menu.
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

/**
 * Global queue of pending habit status updates.
 * Each packet: { habitId, date, status, cell, key }.
 * Only the latest packet per cell (habitId|date) is kept.
 * UPDATE_QUEUE_INTERVAL_MS comes from constants.js (Config.UPDATE_QUEUE_INTERVAL_MS).
 */
let updateQueue = [];
let updateTimerId = null;
let isProcessingUpdates = false;

const statusMenu = new FloatingMenu();

// Store the habits data for reference
let habitsData = {};

// Add at the beginning of the file
const notifications = new NotificationManager();

/**
 * Builds a unique key for a habit cell.
 * @param {number} habitId
 * @param {string} date
 * @returns {string}
 */
function makeUpdateKey(habitId, date) {
    return habitId + '|' + date;
}

/**
 * Shows or hides the save indicator based on whether there are
 * pending or in-flight updates.
 */
function updateSaveIndicatorVisibility() {
    const indicator = document.getElementById('save-indicator');
    if (!indicator) {
        return;
    }

    if (updateQueue.length > 0 || isProcessingUpdates) {
        indicator.classList.add('visible');
    } else {
        indicator.classList.remove('visible');
    }
}

/**
 * Removes any queued update for the given cell.
 * @param {number} habitId
 * @param {string} date
 */
function removePendingUpdatesForCell(habitId, date) {
    const key = makeUpdateKey(habitId, date);
    updateQueue = updateQueue.filter(function (packet) {
        return packet.key !== key;
    });
    updateSaveIndicatorVisibility();
}

/**
 * Returns true if two packets have identical field values.
 * @param {Object} a
 * @param {Object} b
 * @returns {boolean}
 */
function packetsAreEqual(a, b) {
    return a.habitId === b.habitId &&
        a.date === b.date &&
        a.status === b.status &&
        a.cell === b.cell &&
        a.key === b.key;
}

/**
 * Stops the drain timer if it is running.
 */
function stopUpdateTimer() {
    if (updateTimerId !== null) {
        clearInterval(updateTimerId);
        updateTimerId = null;
    }
}

/**
 * Ensures the drain timer is running while the queue is non-empty
 * and no batch is currently being processed.
 */
function ensureUpdateTimerRunning() {
    if (updateQueue.length > 0 && updateTimerId === null && !isProcessingUpdates) {
        updateTimerId = setInterval(onUpdateTimerTick, UPDATE_QUEUE_INTERVAL_MS);
    }
}

/**
 * Timer tick: if the queue has packets, pause the timer and drain them all.
 * If the queue is empty, stop the timer.
 */
function onUpdateTimerTick() {
    if (updateQueue.length === 0) {
        stopUpdateTimer();
        updateSaveIndicatorVisibility();
        return;
    }

    if (isProcessingUpdates) {
        return;
    }

    // Pause the timer while a batch is in flight
    stopUpdateTimer();
    processUpdateQueue();
}

/**
 * Drains all queued packets sequentially, awaiting a response for each.
 * A packet is removed only if its values are unchanged since the send started
 * (user may have clicked the same cell again and replaced it in the queue).
 * On network/HTTP error the loop aborts; remaining packets stay queued and
 * the timer is restarted.
 */
async function processUpdateQueue() {
    isProcessingUpdates = true;
    updateSaveIndicatorVisibility();

    try {
        // Snapshot keys present at tick start. Packets enqueued while sending
        // wait for the next timer cycle.
        const keysToProcess = updateQueue.map(function (packet) {
            return packet.key;
        });

        for (let i = 0; i < keysToProcess.length; i++) {
            const key = keysToProcess[i];
            const packetRef = updateQueue.find(function (packet) {
                return packet.key === key;
            });
            if (!packetRef) {
                // Cancelled (e.g. double-click) before we reached it
                continue;
            }

            const packetCopy = {
                habitId: packetRef.habitId,
                date: packetRef.date,
                status: packetRef.status,
                cell: packetRef.cell,
                key: packetRef.key
            };

            // Play animation at the same time as sending update
            if (packetCopy.status === 3) {
                playFireworkAnimation(packetCopy.cell, true);
            } else if (packetCopy.status === 2) {
                playFireworkAnimation(packetCopy.cell, false);
            }

            try {
                await sendUpdate(packetCopy.habitId, packetCopy.date, packetCopy.status, packetCopy.cell);
            } catch (error) {
                // Leave failed and remaining packets in the queue; timer will retry later
                break;
            }

            const currentPacket = updateQueue.find(function (packet) {
                return packet.key === packetCopy.key;
            });

            if (currentPacket && packetsAreEqual(packetCopy, currentPacket)) {
                // Values unchanged — remove the sent packet
                const removeIndex = updateQueue.indexOf(currentPacket);
                if (removeIndex !== -1) {
                    updateQueue.splice(removeIndex, 1);
                }
            }
            // If values differ or packet is gone, keep it for the next cycle
        }
    } finally {
        isProcessingUpdates = false;
        ensureUpdateTimerRunning();
        updateSaveIndicatorVisibility();
    }
}

/**
 * Enqueues a status update for a cell.
 * If a packet for the same cell already exists, it is removed first.
 * Starts the drain timer if it is not running.
 * @param {number} habitId
 * @param {string} date
 * @param {number} status
 * @param {HTMLElement} cell
 */
function enqueueUpdate(habitId, date, status, cell) {
    removePendingUpdatesForCell(habitId, date);
    updateQueue.push({
        habitId: habitId,
        date: date,
        status: status,
        cell: cell,
        key: makeUpdateKey(habitId, date)
    });
    ensureUpdateTimerRunning();
    updateSaveIndicatorVisibility();
}

/**
 * Calculate date range for the table, ending with Sunday
 * @returns {Object} Object containing start and end dates in 'YYYY-MM-DD' format
 */
function calculateDateRange() {
    // Get date from URL parameter if present
    const urlParams = new URLSearchParams(window.location.search);
    const dateParam = urlParams.get('date');

    let baseDate;
    if (dateParam) {
        // Parse date from URL parameter
        baseDate = new Date(dateParam);
        if (isNaN(baseDate.getTime())) {
            console.error('Invalid date parameter:', dateParam);
            baseDate = new Date(); // Fallback to current date if invalid
        }
    } else {
        baseDate = new Date();
    }

    const currentDay = baseDate.getDay();
    const endDate = new Date(baseDate);

    const daysToSunday = currentDay === 0 ? 0 : 7 - currentDay;
    endDate.setDate(baseDate.getDate() + daysToSunday);

    const startDate = new Date(endDate);
    startDate.setDate(endDate.getDate() - (tableDaysCount - 1));

    return {
        startDate: formatDate(startDate),
        endDate: formatDate(endDate)
    };
}

/**
 * Format date to YYYY-MM-DD string
 * @param {Date} date - Date object to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = ('0' + (date.getMonth() + 1)).slice(-2);
    const day = ('0' + date.getDate()).slice(-2);
    return `${year}-${month}-${day}`;
}

/**
 * Fetch habits data from the server
 * @param {string} startDate - Start date in YYYY-MM-DD format
 * @param {string} endDate - End date in YYYY-MM-DD format
 */
function fetchHabitsData(startDate, endDate) {
    fetch(`./api/main_page?start_date=${startDate}&end_date=${endDate}`)
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Error loading habits');
                });
            }
            return response.json();
        })
        .then(data => {
            // Store the habits data globally
            habitsData = data;
            console.log('After fetch, habitsData loaded:', !!habitsData.habits, 'count:', habitsData.habits?.length);

            // Show message if present
            if (data.message) {
                showMessage(data.message);
            }
            renderTable(data, startDate, endDate);
        })
        .catch(error => {
            console.error('Error fetching habits:', error);
            notifications.show(error.message);
        });
}

/**
 * Schedule page refresh for the next day
 */
function scheduleNextDayRefresh() {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);

    const msUntilMidnight = tomorrow - now;
    // Add random delay (0-60 seconds) to prevent simultaneous refresh by all users
    const randomDelay = Math.random() * 60000;

    setTimeout(() => {
        window.location.reload();
    }, msUntilMidnight + randomDelay);
}

/**
 * Initialize the habit tracker
 */
function initHabitTracker() {
    const { startDate, endDate } = calculateDateRange();

    // Create base date once
    const baseDate = new Date(startDate);
    baseDate.setHours(0, 0, 0, 0);

    // Initialize table headers with dates
    const headerRow = document.querySelector('#habits-table tr:first-child');
    const dates = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Skip first header (it's "Habit / Date")
    const dateHeaders = headerRow.querySelectorAll('th.date-header');

    for (let i = 0; i < tableDaysCount; i++) {
        const currentDate = new Date(baseDate);
        currentDate.setDate(baseDate.getDate() + i);
        const dateStr = formatDate(currentDate);
        dates.push(dateStr);

        const th = dateHeaders[i];
        const dayOfMonth = currentDate.getDate();
        const dayOfWeek = weekDays[currentDate.getDay()];
        th.textContent = `${dayOfMonth} ${dayOfWeek}`;
        th.dataset.date = dateStr;  // Store date in dataset

        if (currentDate.getFullYear() === today.getFullYear() &&
            currentDate.getMonth() === today.getMonth() &&
            currentDate.getDate() === today.getDate()) {
            th.classList.add('current-day');
        } else if (currentDate > today) {
            th.classList.add('future-day');
        }
    }

    // Initialize empty rows based on approximateHabitsCount
    const table = document.getElementById('habits-table');
    const currentRows = table.querySelectorAll('tr').length - 1; // -1 for header
    const neededRows = approximateHabitsCount;

    // Add or remove rows to match approximateHabitsCount
    if (currentRows < neededRows) {
        for (let i = currentRows; i < neededRows; i++) {
            const row = document.createElement('tr');
            row.innerHTML = '<td></td>' + '<td></td>'.repeat(tableDaysCount);
            table.appendChild(row);
        }
    } else if (currentRows > neededRows) {
        for (let i = currentRows; i > neededRows; i--) {
            table.deleteRow(-1);
        }
    }

    // Fetch actual data
    fetchHabitsData(startDate, endDate);

    // Setup status menu dismissal
    document.addEventListener('click', function (e) {
        if (openStatusMenu && !openStatusMenu.contains(e.target)) {
            removeStatusMenu();
        }
    });

    scheduleNextDayRefresh();
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if date parameter is present
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('date')) {
        // Create and add Today button
        const todayButton = document.createElement('button');
        todayButton.className = 'option-button';
        todayButton.textContent = 'Today';
        todayButton.title = 'Go to today';
        todayButton.style.marginLeft = '10px';
        todayButton.onclick = function() {
            goToToday();
        };

        // Add button after settings icon
        const settingsButton = document.querySelector('.settings-icon');
        settingsButton.parentNode.insertBefore(todayButton, settingsButton.nextSibling);
    }

    initHabitTracker();
});

/**
 * Returns a display string (emoji) based on the habit status.
 * @param {number} status - The status code.
 * @param {boolean} isBadHabit - Whether this is a bad habit.
 * @param {number} levels - The number of levels for this habit.
 * @returns {string} The corresponding emoji or an empty string.
 */
function getStatusEmoji(status, isBadHabit = false, levels = 3) {
    const options = getStatusOptions(isBadHabit, levels);
    // TODO: optimize???
    const option = options.find(opt => opt.value === status);
    return option ? option.icon : '???';
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
 * It cycles the status and enqueues a backend update.
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

        // Get the habit_id from the cell
        const habitId = parseInt(cell.dataset.habitId);

        // Get habit parameters
        const habit = habitsData.habits.find(h => h.id === habitId);
        const isBadHabit = habit && habit.bad_habit;
        const levels = habit && habit.levels;

        // Get available status options based on habit settings
        const statusOptions = getStatusOptions(isBadHabit, levels);

        // Find current status in the array
        const currentIndex = statusOptions.findIndex(opt => opt.value === currentStatus);

        // Get next status (cycle to first if at end)
        const nextIndex = (currentIndex + 1) % statusOptions.length;
        const newStatus = statusOptions[nextIndex].value;

        updateCellContent(cell, newStatus);
        enqueueUpdate(habitId, cell.dataset.date, newStatus, cell);
    }
}

/**
 * Handles a double-click event on a cell.
 * It cancels any pending queued update and shows a floating status selection menu.
 * @param {HTMLElement} cell - The table cell element.
 * @param {MouseEvent} e - The mouse event.
 */
function handleCellDblClick(cell, e) {
    e.stopPropagation();

    const habitId = parseInt(cell.dataset.habitId);
    removePendingUpdatesForCell(habitId, cell.dataset.date);

    // Restore previous state
    if (lastClickedCell === cell && lastClickedStatus !== null) {
        // Get habit parameters
        const habit = habitsData.habits.find(h => h.id === habitId);
        const isBadHabit = habit && habit.bad_habit;
        const levels = habit && habit.levels;

        cell.dataset.status = lastClickedStatus;
        cell.textContent = getStatusEmoji(lastClickedStatus, isBadHabit, levels);
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
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Get dates from headers
    const dateHeaders = table.querySelectorAll('th.date-header');
    const dates = Array.from(dateHeaders).map(th => th.dataset.date);

    // Adjust number of rows if needed
    const currentRows = table.querySelectorAll('tr').length - 1; // -1 for header
    const neededRows = data.habits.length;

    if (currentRows < neededRows) {
        for (let i = currentRows; i < neededRows; i++) {
            const row = document.createElement('tr');
            row.innerHTML = '<td></td>' + '<td></td>'.repeat(tableDaysCount);
            table.appendChild(row);
        }
    } else if (currentRows > neededRows) {
        for (let i = currentRows; i > neededRows; i--) {
            table.deleteRow(-1);
        }
    }

    // Fill data into rows
    const rows = table.querySelectorAll('tr');
    data.habits.forEach((habit, index) => {
        const row = rows[index + 1]; // +1 to skip header row
        initializeHabitRow(row, habit, dates, today);
    });
}

/**
 * Updates a table row with habit data
 * @param {HTMLTableRowElement} row - Table row to update
 * @param {Object} habit - Habit data object
 * @param {Array<string>} dates - Array of dates in YYYY-MM-DD format
 * @param {Date} today - Current date (with time set to 00:00:00)
 */
function initializeHabitRow(row, habit, dates, today) {
    // Set habit name in first cell
    const habitCell = row.cells[0];
    const habitLink = document.createElement('a');
    habitLink.href = './habit/' + habit.id;
    habitLink.textContent = habit.name;
    habitCell.innerHTML = ''; // Clear cell
    habitCell.appendChild(habitLink);

    // Fill tracking data
    habit.tracking.forEach((status, cellIndex) => {
        const cell = row.cells[cellIndex + 1];
        initializeHabitCell(cell, status, habit.id, dates[cellIndex], today);
    });
}

/**
 * Shows a floating menu with status options.
 * @param {HTMLElement} cell - The table cell element.
 * @param {MouseEvent} event - The mouse event.
 */
function showStatusMenu(cell, event) {
    removeStatusMenu(); // Remove existing menu if any

    const habitId = parseInt(cell.dataset.habitId);

    // Get habit parameters
    const habit = habitsData.habits.find(h => h.id === habitId);
    const isBadHabit = habit && habit.bad_habit;
    const levels = habit && habit.levels;

    const items = getStatusOptions(isBadHabit, levels).map(option => ({
        icon: option.icon || option.as_char,
        label: option.label,
        onClick: () => {
            updateCellContent(cell, option.value);
            enqueueUpdate(habitId, cell.dataset.date, option.value, cell);
        }
    }));

    statusMenu.show(cell, items);
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
 * @param {number} habitId - The habit ID.
 * @param {string} date - The date of the status.
 * @param {number} status - The new status.
 * @param {HTMLElement} cell - The table cell element (for logging purposes).
 * @returns {Promise<Object>} Resolves with response data on success; rejects on error.
 */
function sendUpdate(habitId, date, status, cell) {
    return fetch('./api/habits/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            habit_id: habitId,
            date: date,
            status: status
        })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Error updating status');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Update successful for habit', habitId, 'on', date, ':', data);
            return data;
        })
        .catch(error => {
            console.error('Error updating habit status:', error);
            notifications.show(error.message);
            throw error;
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

/**
 * Creates menu button for empty cell
 * @param {HTMLElement} cell - The table cell element
 */
function createCellMenuButton(cell) {
    const button = document.createElement('button');
    button.textContent = '...';
    button.className = 'cell-menu-button';
    button.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent cell click
        showStatusMenu(cell, e);
    });
    cell.appendChild(button);
}

/**
 * Updates cell display with appropriate emoji and menu button
 * @param {HTMLElement} cell - The table cell element
 * @param {number} status - Status value for the cell
 * @param {number} habitId - ID of the habit
 * @param {boolean} isFutureDay - Whether this cell represents a future date
 */
function updateCellDisplay(cell, status, habitId, isFutureDay = false) {
    cell.dataset.status = status;

    // Get habit parameters
    const habit = habitsData.habits.find(h => h.id === habitId);
    const isBadHabit = habit && habit.bad_habit;
    const levels = habit && habit.levels;

    cell.textContent = getStatusEmoji(status, isBadHabit, levels);

    const hasButton = cell.querySelector('.cell-menu-button') !== null;
    const needsButton = parseInt(status) === 0 && !isFutureDay;

    // Remove existing button if status is not 0 or it's a future date
    if (hasButton && !needsButton) {
        cell.querySelector('.cell-menu-button').remove();
    }
    // Add button if status is 0 and it's not a future date
    else if (!hasButton && needsButton) {
        createCellMenuButton(cell);
    }
}

/**
 * Updates cell content after user interaction
 * @param {HTMLElement} cell - The table cell element
 * @param {number} status - New status value
 */
function updateCellContent(cell, status) {
    const habitId = parseInt(cell.dataset.habitId);
    const isFutureDay = cell.classList.contains('future-day');
    updateCellDisplay(cell, status, habitId, isFutureDay);
}

/**
 * Initializes a single cell in the habit tracking table
 * @param {HTMLTableCellElement} cell - The table cell to update
 * @param {number} status - Status value for the cell
 * @param {number} habitId - ID of the habit
 * @param {string} date - Date string in YYYY-MM-DD format
 * @param {Date} today - Current date (with time set to 00:00:00)
 */
function initializeHabitCell(cell, status, habitId, date, today) {
    cell.style.cursor = 'pointer';

    cell.dataset.habitId = habitId;
    cell.dataset.date = date;

    const cellDate = new Date(date);
    cellDate.setHours(0, 0, 0, 0);

    // Handle future dates
    const isFutureDay = cellDate > today;
    if (isFutureDay) {
        cell.classList.add('future-day');
        cell.style.cursor = 'default';
    } else {
        attachCellListeners(cell);
    }

    // Update display (emoji and menu button)
    updateCellDisplay(cell, status, habitId, isFutureDay);
}

function showMessage(message) {
    // Remove existing message if any
    const existingMessage = document.getElementById('index-page-message');
    if (existingMessage) {
        existingMessage.remove();
    }

    // Create new message element
    const messageDiv = document.createElement('div');
    messageDiv.id = 'index-page-message';
    messageDiv.textContent = message;

    // Insert before the table
    const table = document.getElementById('habits-table');
    table.parentNode.insertBefore(messageDiv, table);
}

/**
 * Redirects to the current page (effectively refreshing to today's view)
 */
function goToToday() {
    window.location.href = window.location.pathname;
}
