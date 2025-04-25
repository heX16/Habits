// habitId is declared in the HTML file

document.addEventListener('DOMContentLoaded', function () {
    // Load habit name
    fetchHabitName();

    // Load all parameters
    loadParameters();

    // Add event listeners
    setupEventListeners();
});

// Fetch habit name
function fetchHabitName() {
    fetch(`../../api/habits/list`)
        .then(response => response.json())
        .then(data => {
            const habit = data.habits.find(h => h.id === habitId);
            if (habit) {
                document.getElementById('habit-name').textContent = habit.name;
            }
        });
}

// Load all parameters from the server
function loadParameters() {
    const parameters = ['fail_by_default', 'single_checkbox', 'multi_numbers', 'bad_habit', 'levels'];

    parameters.forEach(param => {
        if (param === 'levels') {
            // Handle select input
            fetch(`../../api/param/${param}/${habitId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById(param).value = data.value || 'level1';
                });
        } else {
            // Handle checkbox inputs
            fetch(`../../api/param/${param}/${habitId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById(param).checked = data.value === '1';
                });
        }
    });
}

// Setup event listeners for all parameters
function setupEventListeners() {
    const checkboxParams = ['fail-by-default', 'single-checkbox', 'multi-numbers', 'bad-habit'];

    // Add event listeners for all checkboxes
    checkboxParams.forEach(param => {
        document.getElementById(param).addEventListener('change', function(e) {
            const value = e.target.checked ? '1' : '0';
            updateParameter(param, value);
        });
    });

    // Add event listener for the select input
    document.getElementById('levels').addEventListener('change', function(e) {
        updateParameter('levels', e.target.value);
    });
}

// Update parameter on the server
function updateParameter(param, value) {
    fetch(`../../api/param/${param}/${habitId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            value: value
        })
    });
}

// Rename habit function
function renameHabit() {
    const newName = document.getElementById('new-habit-name').value.trim();
    if (!newName) {
        showRenameStatus('Name cannot be empty', 'error');
        return;
    }

    fetch(`../../api/habits/rename`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            habit_id: habitId,
            new_name: newName
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showRenameStatus(data.error, 'error');
            } else {
                showRenameStatus('Habit renamed successfully', 'success');
                document.getElementById('habit-name').textContent = newName;
                document.getElementById('new-habit-name').value = '';
            }
        })
        .catch(error => {
            showRenameStatus('Error occurred while renaming', 'error');
        });
}

// Show rename status message
function showRenameStatus(message, type) {
    const statusDiv = document.getElementById('rename-status');
    statusDiv.textContent = message;
    statusDiv.className = type === 'error' ? 'habit-options-error' : 'habit-options-success';
}