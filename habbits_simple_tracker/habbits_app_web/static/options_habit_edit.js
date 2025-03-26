// edit.js
// URL: http://server.test/habits/static/edit.js
// Used on: http://server.test/habits/options

/**
 * This script handles the functionality for the habit editing page.
 * It fetches the list of habits, renders them, and provides functions
 * to add and delete habits.
 */

document.addEventListener('DOMContentLoaded', function () {
    loadHabits();

    // Handle form submission for adding a new habit
    const addHabitForm = document.getElementById('add-habit-form');
    addHabitForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const habitNameInput = document.getElementById('habit-name');
        const habitName = habitNameInput.value.trim();
        if (habitName) {
            addHabit(habitName);
            habitNameInput.value = '';
        }
    });
});

/**
 * Fetches all habits from the backend and renders them.
 */
function loadHabits() {
    fetch('./api/habits/list')
        .then(response => response.json())
        .then(data => {
            renderHabitsList(data.habits);
        })
        .catch(error => {
            console.error('Error fetching habits:', error);
        });
}

/**
 * Renders the list of habits with delete buttons.
 * @param {Array} habits - Array of habit objects.
 */
function renderHabitsList(habits) {
    const habitsList = document.getElementById('habits-list');
    habitsList.innerHTML = '';

    habits.forEach((habit, index) => {
        const li = document.createElement('li');

        // Create name span
        const nameSpan = document.createElement('span');
        nameSpan.className = 'options-habit-name';
        nameSpan.textContent = habit.name;
        li.appendChild(nameSpan);

        // Create buttons container
        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'options-habit-buttons';

        // Create reorder buttons
        const upButton = document.createElement('button');
        upButton.textContent = '↑';
        upButton.title = 'Move up';
        upButton.disabled = index === 0;
        upButton.addEventListener('click', function() {
            reorderHabit(habit.id, 'up');
        });

        const downButton = document.createElement('button');
        downButton.textContent = '↓';
        downButton.title = 'Move down';
        downButton.disabled = index === habits.length - 1;
        downButton.addEventListener('click', function() {
            reorderHabit(habit.id, 'down');
        });

        // Create options button
        const optionsButton = document.createElement('button');
        optionsButton.textContent = 'Options';
        optionsButton.addEventListener('click', function() {
            window.location.href = `habit/${habit.id}/options`;
        });

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.dataset.habitId = habit.id;
        deleteButton.addEventListener('click', function () {
            deleteHabit(this.dataset.habitId);
        });

        // Add all buttons to container
        buttonsContainer.appendChild(upButton);
        buttonsContainer.appendChild(downButton);
        buttonsContainer.appendChild(optionsButton);
        buttonsContainer.appendChild(deleteButton);

        // Add container to list item
        li.appendChild(buttonsContainer);
        habitsList.appendChild(li);
    });
}

/**
 * Sends a request to add a new habit.
 * @param {string} habitName - The name of the new habit.
 */
function addHabit(habitName) {
    fetch('./api/habits/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: habitName })
    })
    .then(response => response.json())
    .then(data => {
        loadHabits();
    })
    .catch(error => {
        console.error('Error adding habit:', error);
    });
}

/**
 * Sends a request to delete a habit.
 * @param {string} habitId - The ID of the habit to delete.
 */
function deleteHabit(habitId) {
    if (confirm('Are you sure you want to delete this habit?')) {
        fetch('./api/habits/delete', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ habit_id: parseInt(habitId) })
        })
        .then(response => response.json())
        .then(data => {
            loadHabits();
        })
        .catch(error => {
            console.error('Error deleting habit:', error);
        });
    }
}

/**
 * Sends a request to reorder a habit.
 * @param {string} habitId - The ID of the habit to reorder.
 * @param {string} direction - The direction to move ('up' or 'down').
 */
function reorderHabit(habitId, direction) {
    fetch('./api/habits/reorder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            habit_id: parseInt(habitId),
            direction: direction
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error reordering habit:', data.error);
        } else {
            loadHabits();
        }
    })
    .catch(error => {
        console.error('Error reordering habit:', error);
    });
}
