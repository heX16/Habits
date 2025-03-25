// This file is generated automatically
const singleClickMaxStatus = {{ constants.singleClickMaxStatus }};
const tableDaysCount = {{ constants.tableDaysCount }};
const approximateHabitsCount = {{ constants.approximateHabitsCount }}; // Approximate number of habits

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function getStatusOptions(singleCheckbox) {
    const options = [
        {% for option in status_options %}
        {{ option | safe }}{% if not loop.last %},{% endif %}
        {% endfor %}
    ];

    if (singleCheckbox) {
        // Если включен режим single_checkbox, оставляем только статусы 0, 2 и 9
        return options.filter(opt => opt.value === 0 || opt.value === 2 || opt.value === 9);
    }

    return options;
}