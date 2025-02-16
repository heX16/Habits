// This file is generated automatically
const singleClickMaxStatus = {{ constants.singleClickMaxStatus }};
const tableDaysCount = {{ constants.tableDaysCount }};
const approximateHabitsCount = {{ constants.approximateHabitsCount }}; // Approximate number of habits

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function getStatusOptions() {
    return [
        {% for option in status_options %}
        {{ option | safe }}{% if not loop.last %},{% endif %}
        {% endfor %}
    ];
} 