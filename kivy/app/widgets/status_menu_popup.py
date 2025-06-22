"""
Status Menu Popup Widget

Всплывающее меню для выбора статуса привычки при двойном клике.
Отображает доступные статусы в зависимости от настроек привычки.
"""

from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.logger import Logger

class StatusMenuPopup(Popup):
    """Всплывающее меню выбора статуса привычки"""
    
    def __init__(self, habit_data, current_status, on_status_selected, **kwargs):
        """
        Инициализация меню статусов
        
        Args:
            habit_data: данные привычки с параметрами
            current_status: текущий статус ячейки
            on_status_selected: callback функция для выбора статуса
        """
        super().__init__(**kwargs)
        
        self.habit_data = habit_data
        self.current_status = current_status
        self.on_status_selected = on_status_selected
        
        # Настройки popup
        self.title = f"Статус: {habit_data.get('name', 'Привычка')}"
        self.size_hint = (0.8, 0.6)
        self.auto_dismiss = True
        
        # Создаем содержимое
        self.content = self._create_content()
        
        Logger.info(f"StatusMenuPopup: Created for habit '{habit_data.get('name')}', current status: {current_status}")
    
    def _create_content(self):
        """Создает содержимое popup с кнопками статусов"""
        layout = GridLayout(cols=1, spacing=dp(10), padding=dp(10))
        
        # Заголовок
        header_label = Label(
            text="Выберите статус:",
            size_hint_y=None,
            height=dp(30),
            font_size='16sp'
        )
        layout.add_widget(header_label)
        
        # Получаем доступные статусы
        available_statuses = self._get_available_statuses()
        
        # Создаем сетку кнопок статусов
        buttons_grid = GridLayout(cols=2, spacing=dp(5))
        
        for status_value, status_info in available_statuses.items():
            button = Button(
                text=status_info['text'],
                size_hint_y=None,
                height=dp(50),
                font_size='14sp'
            )
            
            # Выделяем текущий статус
            if status_value == self.current_status:
                button.background_color = (0.3, 0.6, 1, 1)  # Синий цвет
            else:
                button.background_color = (0.9, 0.9, 0.9, 1)  # Серый цвет
            
            button.bind(on_press=lambda btn, status=status_value: self._on_status_button_press(status))
            buttons_grid.add_widget(button)
        
        layout.add_widget(buttons_grid)
        
        # Кнопка отмены
        cancel_button = Button(
            text="Отмена",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.8, 0.3, 0.3, 1)
        )
        cancel_button.bind(on_press=self._on_cancel)
        layout.add_widget(cancel_button)
        
        return layout
    
    def _get_available_statuses(self):
        """
        Определяет доступные статусы на основе настроек привычки
        
        Returns:
            dict: словарь {status_value: {'text': 'display_text', 'icon': 'icon_name'}}
        """
        # Получаем режим привычки (по умолчанию level3)
        mode = self.habit_data.get('mode', 'level3')
        levels = self.habit_data.get('levels', 3)
        
        statuses = {}
        
        if mode == 'level1' or levels == 1:
            # Только базовые статусы
            statuses = {
                0: {'text': '❌ Не выполнено', 'icon': 'not_set'},
                2: {'text': '✅ Выполнено', 'icon': 'done'},
                9: {'text': '❌ Провал', 'icon': 'fail'}
            }
        elif mode == 'level10' or levels == 10:
            # Числовые статусы 0-9
            statuses = {
                0: {'text': '0️⃣ Не выполнено', 'icon': 'not_set'},
                10: {'text': '0️⃣ Ноль', 'icon': 'number_0'},
                11: {'text': '1️⃣ Один', 'icon': 'number_1'},
                12: {'text': '2️⃣ Два', 'icon': 'number_2'},
                13: {'text': '3️⃣ Три', 'icon': 'number_3'},
                14: {'text': '4️⃣ Четыре', 'icon': 'number_4'},
                15: {'text': '5️⃣ Пять', 'icon': 'number_5'},
                16: {'text': '6️⃣ Шесть', 'icon': 'number_6'},
                17: {'text': '7️⃣ Семь', 'icon': 'number_7'},
                18: {'text': '8️⃣ Восемь', 'icon': 'number_8'},
                19: {'text': '9️⃣ Девять', 'icon': 'number_9'},
                9: {'text': '❌ Провал', 'icon': 'fail'}
            }
        else:
            # Полный режим level3 (по умолчанию)
            statuses = {
                0: {'text': '❌ Не выполнено', 'icon': 'not_set'},
                1: {'text': '🟡 Мини', 'icon': 'done_mini'},
                2: {'text': '✅ Выполнено', 'icon': 'done'},
                3: {'text': '⭐ Элита', 'icon': 'done_elite'},
                9: {'text': '❌ Провал', 'icon': 'fail'}
            }
        
        Logger.info(f"StatusMenuPopup: Available statuses for mode '{mode}': {list(statuses.keys())}")
        return statuses
    
    def _on_status_button_press(self, status_value):
        """Обработка нажатия на кнопку статуса"""
        Logger.info(f"StatusMenuPopup: Status selected: {status_value}")
        
        if self.on_status_selected:
            self.on_status_selected(status_value)
        
        self.dismiss()
    
    def _on_cancel(self, button):
        """Обработка отмены выбора"""
        Logger.info("StatusMenuPopup: Cancelled")
        self.dismiss()
    
    @staticmethod
    def show_for_cell(habit_data, current_status, on_status_selected):
        """
        Статический метод для показа popup
        
        Args:
            habit_data: данные привычки
            current_status: текущий статус
            on_status_selected: callback функция
        """
        popup = StatusMenuPopup(
            habit_data=habit_data,
            current_status=current_status,
            on_status_selected=on_status_selected
        )
        popup.open()
        return popup 