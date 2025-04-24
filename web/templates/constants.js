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
        // Если включен режим multi_numbers, оставляем только статусы 0 и числовые (10-19)
        return {
            'all': options['all'].filter(opt => opt.value === 0 || (opt.value >= 10 && opt.value <= 19))
        };
    }

    if (singleCheckbox) {
        // Если включен режим single_checkbox, оставляем только статусы 0, 2 и 9
        return {
            'all': options['all'].filter(opt => opt.value === 0 || opt.value === 2 || opt.value === 9)
        };
    }

    return options;
}