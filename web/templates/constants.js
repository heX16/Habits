// This file is generated automatically
const tableDaysCount = {{ constants.tableDaysCount }};
const approximateHabitsCount = {{ constants.approximateHabitsCount }}; // Approximate number of habits
const CONNECTION_CHECK_INTERVAL_MIN = {{ constants.connectionCheckIntervalMin }};

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
    let  l = '1';
    if (levels) {
        if (levels == 10) {
            // Numbers mode
            l = '10';
        } else if (levels == 1) {
            // Single checkbox mode
            l = '1';
        } else if (levels == 3) {
            // Tiple levels
            l = '3';
        }
    }
    let h = 'gh';
    if ((bad_habit) && (bad_habit == true)) {
        h = 'bh';
    }
    // return array by key. Key example: 'gb1'
    return statusOptionsData[h+l];
}
