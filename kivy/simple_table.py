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


def create_table_widget(table_data):
    """Создает виджет таблицы (ScrollView + GridLayout)"""
    # Определяем количество колонок из первой строки (заголовки)
    cols = len(table_data[0]) if table_data else 1
    
    # Создаем ScrollView с таблицей
    scroll = ScrollView(
        bar_width=15,  # Делаем полосу прокрутки шире (по умолчанию 2)
        bar_color=[0.5, 0.5, 0.5, 0.8],  # Серый цвет для активной полосы
        bar_inactive_color=[0.7, 0.7, 0.7, 0.4],  # Светло-серый для неактивной
        scroll_type=['bars', 'content']  # Можно прокручивать и по полосе, и по содержимому
    )
    
    # Создаем GridLayout для таблицы
    table_grid = GridLayout(
        cols=cols,
        spacing=dp(1),
        size_hint_y=None,
        row_default_height=dp(40),
        row_force_default=True,
    )
    # Привязываем высоту к минимальной высоте для прокрутки
    table_grid.bind(minimum_height=table_grid.setter('height'))  # type: ignore
    
    scroll.add_widget(table_grid)
    return scroll, table_grid


def add_row(table_data, row_data):
    """Добавляет строку данных в таблицу"""
    table_data.append(list(row_data))


def update_cell(table_data, row, col, text):
    """Обновляет конкретную ячейку"""
    if 0 <= row < len(table_data) and 0 <= col < len(table_data[row]):
        table_data[row][col] = str(text)
        return True
    else:
        print(f"Error: Invalid cell position ({row}, {col})")
        return False


def delete_row(table_grid, table_data, row_num):
    """Удаляет строку из таблицы (и данные, и виджеты)"""
      
    if row_num < 0 or row_num >= len(table_data):
        print(f"Error: Invalid row number {row_num}, table has {len(table_data)} rows")
        return False
    
    cols = table_grid.cols
    total_widgets = len(table_grid.children)
    
    # Проверяем, что у нас достаточно виджетов
    expected_widgets = len(table_data) * cols
    if total_widgets != expected_widgets:
        print(f"Warning: Expected {expected_widgets} widgets, but found {total_widgets}")
        return False
    
    # Удаляем строку из данных
    removed_row = table_data.pop(row_num)
    
    # Вычисляем индексы виджетов для удаления
    # В Kivy children хранятся в обратном порядке добавления
    # Последний добавленный виджет имеет индекс 0
    # Для строки row_num виджеты находятся в позициях:
    # start_idx = (len(table_data) - row_num) * cols - 1 (после удаления строки из данных)
    # end_idx = start_idx - cols + 1
    
    start_widget_idx = (len(table_data) - row_num) * cols - 1
    end_widget_idx = start_widget_idx - cols + 1
    
    # Удаляем виджеты (удаляем с конца, чтобы индексы не сбивались)
    widgets_to_remove = []
    for i in range(start_widget_idx, end_widget_idx - 1, -1):
        if 0 <= i < len(table_grid.children):
            widgets_to_remove.append(table_grid.children[i])
    
    for widget in widgets_to_remove:
        table_grid.remove_widget(widget)
    
    return True


def delete_col(table_grid, table_data, col_num):
    """Удаляет колонку из таблицы (и данные, и виджеты)"""
        
    if col_num < 0 or col_num >= table_grid.cols:
        print(f"Error: Invalid col number {col_num}, table has {table_grid.cols} cols")
        return False
    
    if not table_data or len(table_data) == 0:
        print("Error: table_data is empty")
        return False
    
    # Проверяем, что все строки имеют достаточно колонок
    for i, row in enumerate(table_data):
        if len(row) <= col_num:
            print(f"Error: Row {i} has only {len(row)} columns, cannot delete column {col_num}")
            return False
    
    cols = table_grid.cols
    rows = len(table_data)
    total_widgets = len(table_grid.children)
    
    # Проверяем, что у нас достаточно виджетов
    expected_widgets = rows * cols
    if total_widgets != expected_widgets:
        print(f"Warning: Expected {expected_widgets} widgets, but found {total_widgets}")
        return False
    
    # Собираем индексы виджетов для удаления
    # В каждой строке r нужно удалить виджет в колонке col_num
    widgets_to_remove = []
    
    for row in range(rows):
        # Логическая позиция виджета: (row, col_num)
        # Линейный индекс в порядке добавления: row * cols + col_num
        # Индекс в children (обратный порядок): total_widgets - 1 - (row * cols + col_num)
        widget_idx = total_widgets - 1 - (row * cols + col_num)
        
        if 0 <= widget_idx < len(table_grid.children):
            widgets_to_remove.append(table_grid.children[widget_idx])
    
    # Удаляем виджеты
    for widget in widgets_to_remove:
        table_grid.remove_widget(widget)
    
    # Удаляем колонку из данных (из всех строк)
    for row in table_data:
        if col_num < len(row):
            removed_cell = row.pop(col_num)
    
    # Уменьшаем количество колонок в GridLayout
    table_grid.cols -= 1
    
    return True


def insert_row(table_grid, table_data, row_num, row_data):
    """Вставляет строку в произвольное место таблицы"""
    
    if row_num < 0 or row_num > len(table_data):
        print(f"Error: Invalid row number {row_num}, table has {len(table_data)} rows")
        return False
    
    if not row_data:
        print("Error: row_data is empty")
        return False
    
    cols = table_grid.cols
    
    # Проверяем, что row_data имеет правильное количество колонок
    if len(row_data) != cols:
        print(f"Error: row_data has {len(row_data)} columns, but table has {cols} columns")
        return False
    
    # Вставляем данные в table_data
    table_data.insert(row_num, list(row_data))
    
    # Создаем виджеты для новой строки
    new_widgets = []
    for cell_data in row_data:
        label = Label(
            text=str(cell_data),
            size_hint_y=None,
            height=dp(40),
            halign="center",
            valign="middle"
        )
        label.bind(size=label.setter('text_size'))  # type: ignore
        new_widgets.append(label)
    
    # Вычисляем позицию для вставки виджетов
    # В children виджеты хранятся в обратном порядке
    # Для строки row_num нужна позиция: (len(table_data) - row_num - 1) * cols
    total_rows = len(table_data)
    insert_position = (total_rows - row_num - 1) * cols
    
    print(f"Inserting {len(new_widgets)} widgets at position {insert_position}")
    print(f"Children before: {len(table_grid.children)}")
    
    # Вставляем виджеты в обратном порядке (справа налево)
    for i, widget in enumerate(reversed(new_widgets)):
        table_grid.add_widget(widget, index=insert_position + i)
    
    print(f"Children after: {len(table_grid.children)}")
    print(f"Table now has {len(table_data)} rows")
    
    return True


def insert_col(table_grid, table_data, col_num, col_data):
    """Вставляет колонку в произвольное место таблицы"""
    
    if col_num < 0 or col_num > table_grid.cols:
        print(f"Error: Invalid col number {col_num}, table has {table_grid.cols} cols")
        return False
    
    if not col_data:
        print("Error: col_data is empty")
        return False
    
    if len(col_data) != len(table_data):
        print(f"Error: col_data has {len(col_data)} rows, but table has {len(table_data)} rows")
        return False
    
    # Вставляем данные колонки во все строки table_data
    for i, row in enumerate(table_data):
        if i < len(col_data):
            row.insert(col_num, str(col_data[i]))
    
    old_cols = table_grid.cols
    rows = len(table_data)
    
    # Увеличиваем количество колонок в GridLayout
    table_grid.cols += 1
    new_cols = table_grid.cols
    
    print(f"Inserting column at position {col_num}")
    print(f"Columns: {old_cols} -> {new_cols}")
    print(f"Children before: {len(table_grid.children)}")
    
    # ЦИКЛ 1: Рассчитываем все индексы для вставки
    insert_indices = []
    
    # Идем снизу вверх, чтобы индексы не сбивались при вставке
    for row in range(rows - 1, -1, -1):
        # Для строки row нужно вставить виджет в колонку col_num
        
        # Количество виджетов которые мы уже вставили (в строки ниже)
        widgets_already_inserted = (rows - 1 - row)
        
        # Текущее количество children (с учетом уже вставленных)
        current_children_count = old_cols * rows + widgets_already_inserted
        
        # Количество виджетов "левее и выше" в старой структуре
        widgets_before_in_old_structure = row * old_cols + col_num
        
        # Индекс для вставки (children в обратном порядке)
        insert_index = current_children_count - widgets_before_in_old_structure
        
        insert_indices.append((row, insert_index))
        print(f"Row {row}: will insert at index {insert_index}")
    
    # ЦИКЛ 2: Создаем и вставляем виджеты по рассчитанным индексам  
    for row, insert_index in insert_indices:
        cell_data = col_data[row] if row < len(col_data) else ""
        
        # Создаем виджет для ячейки
        label = Label(
            text=str(cell_data),
            size_hint_y=None,
            height=dp(40),
            halign="center",
            valign="middle"
        )
        label.bind(size=label.setter('text_size'))  # type: ignore
        
        # Вставляем виджет по заранее рассчитанному индексу
        table_grid.add_widget(label, index=insert_index)
        print(f"Inserted widget for row {row} at index {insert_index}")
    
    print(f"Children after: {len(table_grid.children)}")
    
    return True


def refresh_table(table_grid, table_data):
    """Обновляет всю таблицу на основе table_data"""
    if not table_grid or not table_data:
        return
        
    # Очищаем таблицу
    table_grid.clear_widgets()
    
    # Добавляем все строки (включая заголовки в первой строке)
    for row in table_data:
        for cell in row:
            label = Label(
                text=str(cell),
                size_hint_y=None,
                height=dp(40),
                halign="center",
                valign="middle"
            )
            label.bind(size=label.setter('text_size'))  # type: ignore
            table_grid.add_widget(label)


class SimpleTableApp(App):
    """Простейшее приложение с таблицей"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table_data = []
        self.table_grid = None
        self.scroll_widget = None
        
    def build(self):
        # Основной вертикальный layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        # Первый ряд кнопок
        buttons_layout1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Создаем первые 5 кнопок
        button1 = Button(text="Add Row", size_hint_x=0.2, on_press=self.on_add_row)
        button2 = Button(text="Insert Row", size_hint_x=0.2, on_press=self.on_insert_row)
        button3 = Button(text="Update Cell", size_hint_x=0.2, on_press=self.on_update_cell)
        button4 = Button(text="Refresh Table", size_hint_x=0.2, on_press=self.on_refresh_table)
        button5 = Button(text="Count Widgets", size_hint_x=0.2, on_press=self.on_count_widgets)
        
        # Добавляем первые кнопки в первый layout
        buttons_layout1.add_widget(button1)
        buttons_layout1.add_widget(button2)
        buttons_layout1.add_widget(button3)
        buttons_layout1.add_widget(button4)
        buttons_layout1.add_widget(button5)
        
        # Второй ряд кнопок для изменения размеров таблицы
        buttons_layout2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Создаем кнопки для изменения размеров
        button6 = Button(text="Insert Col", size_hint_x=0.25, on_press=self.on_insert_col)
        button7 = Button(text="Delete Col", size_hint_x=0.25, on_press=self.on_delete_col_new)
        button8 = Button(text="+1 rows", size_hint_x=0.25, on_press=self.on_add_row_size)
        button9 = Button(text="-1 rows", size_hint_x=0.25, on_press=self.on_remove_row_size)
        
        # Добавляем вторые кнопки во второй layout
        buttons_layout2.add_widget(button6)
        buttons_layout2.add_widget(button7)
        buttons_layout2.add_widget(button8)
        buttons_layout2.add_widget(button9)
        
        # Инициализируем данные таблицы (первая строка - заголовки)
        self.table_data = [
            ["Col1", "Col2", "Col3", "Col4", "Col5", "Col6", "Col7"]  # Заголовки
        ]
        
        # Добавляем строки данных
        for col in range(1, 11):  # 10 строк
            add_row(self.table_data, [f"1x{col}", f"2x{col}", f"3x{col}", f"4x{col}", f"5x{col}", f"6x{col}", f"7x{col}"])
        
        # Создаем виджет таблицы
        self.scroll_widget, self.table_grid = create_table_widget(self.table_data)
        
        # Заполняем таблицу
        refresh_table(self.table_grid, self.table_data)
        
        # Добавляем элементы в основной layout
        main_layout.add_widget(buttons_layout1)
        main_layout.add_widget(buttons_layout2)
        main_layout.add_widget(self.scroll_widget)
        
        return main_layout
    

    
    def on_add_row(self, instance):
        """Добавляет новую строку в таблицу"""
        row_num = len(self.table_data)  # -1 для заголовков + 1 для нового номера = len
        new_row = [f"1x{row_num}", f"2x{row_num}", f"3x{row_num}", f"4x{row_num}", f"5x{row_num}", f"6x{row_num}", f"7x{row_num}"]
        add_row(self.table_data, new_row)
        refresh_table(self.table_grid, self.table_data)
        print(f"Added row. Total rows: {len(self.table_data) - 1}")  # -1 для заголовков
    
    def on_delete_row(self, instance):
        """Удаляет последнюю строку из таблицы"""
        if len(self.table_data) > 1:  # Оставляем заголовки
            self.table_data.pop()
            refresh_table(self.table_grid, self.table_data)
            print(f"Removed row. Total rows: {len(self.table_data) - 1}")  # -1 для заголовков
    
    def on_delete_row_new(self, instance):
        """Удаляет вторую строку из таблицы (первую строку данных) используя новую функцию delete_row"""
        if len(self.table_data) > 1:  # Проверяем, что есть данные кроме заголовков
            # Удаляем первую строку данных (индекс 1, так как 0 - это заголовки)
            success = delete_row(self.table_grid, self.table_data, 1)
            if success:
                print(f"Successfully deleted row. Total rows: {len(self.table_data) - 1}")  # -1 для заголовков
            else:
                print("Failed to delete row")
        else:
            print("No data rows to delete (only headers remain)")
    
    def on_update_cell(self, instance):
        """Демонстрация обновления ячейки"""
        if len(self.table_data) > 1:  # Проверяем, что есть данные кроме заголовков
            # Обновляем первую ячейку первой строки данных (не заголовков)
            update_cell(self.table_data, 1, 0, "UPDATED!")
            refresh_table(self.table_grid, self.table_data)
            print("Updated cell (1,0)")
    
    def on_refresh_table(self, instance):
        """Принудительно обновляет таблицу"""
        refresh_table(self.table_grid, self.table_data)
        print("Table refreshed")
    
    def on_count_widgets(self, instance):
        """Выводит количество виджетов в таблице"""
        if self.table_grid:
            count = len(self.table_grid.children)
            print(f"Количество виджетов в таблице: {count}")
            print(f"Размер таблицы: {self.table_grid.cols} колонок")
            print(f"Всего строк данных: {len(self.table_data)}")
        else:
            print("Таблица не создана")
    
    def on_add_col(self, instance):
        """Увеличивает количество колонок на 1"""
        if self.table_grid:
            old_cols = self.table_grid.cols
            self.table_grid.cols += 1
            print(f"Колонки: {old_cols} -> {self.table_grid.cols}")
            print(f"Виджетов в таблице: {len(self.table_grid.children)}")
    
    def on_remove_col(self, instance):
        """Уменьшает количество колонок на 1"""
        if self.table_grid and self.table_grid.cols > 1:
            old_cols = self.table_grid.cols
            self.table_grid.cols -= 1
            print(f"Колонки: {old_cols} -> {self.table_grid.cols}")
            print(f"Виджетов в таблице: {len(self.table_grid.children)}")
        else:
            print("Нельзя уменьшить количество колонок меньше 1")
    
    def on_add_row_size(self, instance):
        """Увеличивает количество строк на 1"""
        if self.table_grid:
            old_rows = self.table_grid.rows if self.table_grid.rows else "auto"
            if not self.table_grid.rows:
                self.table_grid.rows = 2  # Устанавливаем минимум 2 строки
            else:
                self.table_grid.rows += 1
            print(f"Строки: {old_rows} -> {self.table_grid.rows}")
            print(f"Виджетов в таблице: {len(self.table_grid.children)}")
    
    def on_remove_row_size(self, instance):
        """Уменьшает количество строк на 1"""
        if self.table_grid and self.table_grid.rows and self.table_grid.rows > 1:
            old_rows = self.table_grid.rows
            self.table_grid.rows -= 1
            print(f"Строки: {old_rows} -> {self.table_grid.rows}")
            print(f"Виджетов в таблице: {len(self.table_grid.children)}")
        else:
            print("Нельзя уменьшить количество строк меньше 1 или строки в режиме auto")
    
    def on_delete_col_new(self, instance):
        """Удаляет первую колонку из таблицы используя новую функцию delete_col"""
        if self.table_grid and self.table_grid.cols > 1:
            # Удаляем первую колонку (индекс 0)
            success = delete_col(self.table_grid, self.table_data, 0)
            if success:
                print(f"Successfully deleted column. Remaining cols: {self.table_grid.cols}")
                print(f"Remaining widgets: {len(self.table_grid.children)}")
            else:
                print("Failed to delete column")
        else:
            print("Cannot delete column - only 1 column remaining")
    
    def on_insert_row(self, instance):
        """Вставляет новую строку в позицию 2 (после заголовков и первой строки данных)"""
        if self.table_grid and len(self.table_data) > 0:
            # Создаем данные для новой строки
            new_row_data = ["NEW", "ROW", "INSERT", "TEST", "HERE", "NOW", "!!!"]
            
            # Вставляем в позицию 2 (после заголовков и первой строки данных)
            insert_position = 2 if len(self.table_data) > 1 else 1
            
            success = insert_row(self.table_grid, self.table_data, insert_position, new_row_data)
            if success:
                print(f"Successfully inserted row at position {insert_position}")
                print(f"Table now has {len(self.table_data)} rows total")
                print(f"Widgets in table: {len(self.table_grid.children)}")
            else:
                print("Failed to insert row")
        else:
            print("Cannot insert row - table not initialized")
    
    def on_insert_col(self, instance):
        """Вставляет новую колонку в позицию 2 (между Col2 и Col3)"""
        if self.table_grid and len(self.table_data) > 0:
            # Создаем данные для новой колонки (по одному значению для каждой строки)
            col_data = ["NEW_COL"]  # Заголовок для новой колонки
            
            # Добавляем данные для каждой строки данных
            for i in range(1, len(self.table_data)):  # Начинаем с 1, так как 0 - заголовки
                col_data.append(f"N{i}")
            
            # Вставляем в позицию 2 (между Col2 и Col3)
            insert_position = 2
            
            success = insert_col(self.table_grid, self.table_data, insert_position, col_data)
            if success:
                print(f"Successfully inserted column at position {insert_position}")
                print(f"Table now has {self.table_grid.cols} columns")
                print(f"Widgets in table: {len(self.table_grid.children)}")
            else:
                print("Failed to insert column")
        else:
            print("Cannot insert column - table not initialized")


if __name__ == '__main__':
    SimpleTableApp().run()