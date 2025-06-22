#!/usr/bin/env python3
"""
Simple ScrollView + GridLayout Table Test

Простая таблица на основе ScrollView и GridLayout.
"""

from kivy.metrics import dp
from kivy.app import App  # type: ignore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class SimpleTableApp(App):
    """Простейшее приложение с таблицей"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table_data = []
        self.table_grid = None
        
    def build(self):
        # Основной вертикальный layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        # Горизонтальный layout для кнопок
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Создаем 4 кнопки
        button1 = Button(text="Add Row", size_hint_x=0.25, on_press=self.on_add_row)
        button2 = Button(text="Delete Row", size_hint_x=0.25, on_press=self.on_delete_row)
        
        button3 = Button(text="Button 3", size_hint_x=0.25)
        button4 = Button(text="Button 4", size_hint_x=0.25)
        
        # Добавляем кнопки в горизонтальный layout
        buttons_layout.add_widget(button1)
        buttons_layout.add_widget(button2)
        buttons_layout.add_widget(button3)
        buttons_layout.add_widget(button4)
        
        # Инициализируем данные таблицы
        self.table_data = [
            (f"1x{col}", f"2x{col}", f"3x{col}", f"4x{col}", f"5x{col}", f"6x{col}", f"7x{col}")
            for col in range(1, 11)  # 10 строк
        ]
        
        # Создаем ScrollView с таблицей
        scroll = ScrollView()
        
        # Создаем GridLayout для таблицы
        self.table_grid = GridLayout(
            cols=7,  # 7 колонок
            spacing=dp(1),
            size_hint_y=None,
            row_default_height=dp(40),
            row_force_default=True,
        )
        # Привязываем высоту к минимальной высоте для прокрутки
        self.table_grid.bind(minimum_height=self.table_grid.setter('height'))  # type: ignore
        
        # Заполняем таблицу
        self.populate_table()
        
        scroll.add_widget(self.table_grid)
        
        # Добавляем элементы в основной layout
        main_layout.add_widget(buttons_layout)
        main_layout.add_widget(scroll)
        
        return main_layout
    
    def populate_table(self):
        """Заполняет таблицу данными"""
        if not self.table_grid:
            return
            
        # Очищаем таблицу
        self.table_grid.clear_widgets()
        
        # Добавляем заголовки
        headers = ["Col1", "Col2", "Col3", "Col4", "Col5", "Col6", "Col7"]
        for header in headers:
            label = Label(
                text=header,
                size_hint_y=None,
                height=dp(40),
                halign="center",
                valign="middle"
            )
            label.bind(size=label.setter('text_size'))  # type: ignore
            self.table_grid.add_widget(label)
        
        # Добавляем данные
        for row in self.table_data:
            for cell in row:
                label = Label(
                    text=str(cell),
                    size_hint_y=None,
                    height=dp(40),
                    halign="center",
                    valign="middle"
                )
                label.bind(size=label.setter('text_size'))  # type: ignore
                self.table_grid.add_widget(label)
    
    def on_add_row(self, instance):
        """Добавляет новую строку в таблицу"""
        row_num = len(self.table_data) + 1
        new_row = (f"1x{row_num}", f"2x{row_num}", f"3x{row_num}", f"4x{row_num}", f"5x{row_num}", f"6x{row_num}", f"7x{row_num}")
        self.table_data.append(new_row)
        self.populate_table()
        print(f"Added row. Total rows: {len(self.table_data)}")
    
    def on_delete_row(self, instance):
        """Удаляет последнюю строку из таблицы"""
        if self.table_data:
            self.table_data.pop()
            self.populate_table()
            print(f"Removed row. Total rows: {len(self.table_data)}")


if __name__ == '__main__':
    SimpleTableApp().run()