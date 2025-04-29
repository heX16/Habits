// This file is generated automatically
const tableDaysCount = {{ constants.tableDaysCount }};
const approximateHabitsCount = {{ constants.approximateHabitsCount }}; // Approximate number of habits

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const statusOptionsData = {
    {% for category, options_list in status_options.items() -%}
    '{{ category }}': [
        {% for option in options_list -%}
        {{ option | safe }}{% if not loop.last %},{% endif %}
        {% endfor -%}
    ]{% if not loop.last %},{% endif %}
    {% endfor %}
};

function getStatusOptions(bad_habit, levels) {
    // Determine options based on levels
    if (levels) {
        if (levels == 10) {
            // Numbers mode (0-9)
            return {
                'all': statusOptionsData['all'].filter(opt => opt.value === 0 || (opt.value >= 10 && opt.value <= 19))
            };
        } else if (levels == 1) {
            // Single checkbox mode (0, 2, 9)
            return {
                'all': statusOptionsData['all'].filter(opt => opt.value === 0 || opt.value === 2 || opt.value === 9)
            };
        }
    }

    // Default mode (levels == 3 or levels == 0)
    return statusOptionsData;
}