// edit.js
// URL: http://server.test/habits/static/edit.js
// Used on: http://server.test/habits/edit

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

    habits.forEach(habit => {
        const li = document.createElement('li');
        li.textContent = habit.name + ' ';

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

        li.appendChild(optionsButton);
        li.appendChild(deleteButton);
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
