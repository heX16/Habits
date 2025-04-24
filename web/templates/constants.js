// This file is generated automatically
const tableDaysCount = {{ constants.tableDaysCount }};
const approximateHabitsCount = {{ constants.approximateHabitsCount }}; // Approximate number of habits

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function getStatusOptions(singleCheckbox, multiNumbers) {
    const options = {
        {% for category, options_list in status_options.items() -%}
        '{{ category }}': [
            {% for option in options_list -%}
            {{ option | safe }}{% if not loop.last %},{% endif %}
            {% endfor -%}
        ]{% if not loop.last %},{% endif %}
        {% endfor %}
    };

    if (multiNumbers) {
        // If multi_numbers mode is enabled, keep only status 0 and numeric values (10-19)
        return {
            'all': options['all'].filter(opt => opt.value === 0 || (opt.value >= 10 && opt.value <= 19))
        };
    }

    if (singleCheckbox) {
        // If single_checkbox mode is enabled, keep only statuses 0, 2 and 9
        return {
            'all': options['all'].filter(opt => opt.value === 0 || opt.value === 2 || opt.value === 9)
        };
    }

    return options;
}