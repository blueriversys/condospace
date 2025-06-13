    <style>
        {% if info_data['settings'] %}
            :root {
                {% for key, value in info_data['settings'].items() %}
                  --{{key}}: {{value}};
                {% endfor %}
            }
        {% else %}
            :root {
                --sidebar-color: rgb(11, 83, 69);
                --error-sidebar-color: rgb(241, 196, 15);
            }
        {% endif %}
    </style>

