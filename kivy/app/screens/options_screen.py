"""
Options Screen

Screen for managing habits, global settings, and data import/export.
Equivalent to options.html from the web version.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, ListProperty

from ..models import HabitsModel
from ..widgets import StatusMenuPopup
from ..services import FileManager


class ConfirmationDialog(Popup):
    """Диалог подтверждения для удаления привычек"""
    
    def __init__(self, title, message, on_confirm=None, **kwargs):
        super().__init__(**kwargs)
        
        self.title = title
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False
        
        # Основной layout
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Сообщение
        message_label = Label(
            text=message,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        layout.add_widget(message_label)
        
        # Кнопки
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        # Кнопка отмены
        cancel_btn = Button(text='Отмена', background_color=(0.7, 0.7, 0.7, 1))
        cancel_btn.bind(on_press=self.dismiss)
        buttons_layout.add_widget(cancel_btn)
        
        # Кнопка подтверждения
        confirm_btn = Button(text='Подтвердить', background_color=(0.8, 0.3, 0.3, 1))
        confirm_btn.bind(on_press=lambda x: self._on_confirm(on_confirm))
        buttons_layout.add_widget(confirm_btn)
        
        layout.add_widget(buttons_layout)
        self.content = layout
    
    def _on_confirm(self, callback):
        """Обработка подтверждения"""
        if callback:
            callback()
        self.dismiss()


class HabitListItem(BoxLayout):
    """Элемент списка привычек с кнопками управления"""
    
    def __init__(self, habit_data, on_edit=None, on_delete=None, on_move_up=None, on_move_down=None, on_view_details=None, **kwargs):
        super().__init__(**kwargs)
        
        self.habit_data = habit_data
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(10), dp(5)]
        
        # Название привычки
        self.name_label = Label(
            text=habit_data.get('name', ''),
            size_hint_x=0.5,
            text_size=(None, None),
            halign='left',
            valign='middle',
            font_size='16sp'
        )
        self.add_widget(self.name_label)
        
        # Контейнер для кнопок
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_x=0.5)
        
        # Кнопка "Вверх"
        up_btn = Button(
            text='↑',
            size_hint_x=None,
            width=dp(40),
            font_size='18sp',
            background_color=(0.3, 0.6, 1, 1)
        )
        up_btn.bind(on_press=lambda x: on_move_up(habit_data) if on_move_up else None)
        buttons_layout.add_widget(up_btn)
        
        # Кнопка "Вниз"
        down_btn = Button(
            text='↓',
            size_hint_x=None,
            width=dp(40),
            font_size='18sp',
            background_color=(0.3, 0.6, 1, 1)
        )
        down_btn.bind(on_press=lambda x: on_move_down(habit_data) if on_move_down else None)
        buttons_layout.add_widget(down_btn)
        
        # Кнопка "View Details"
        details_btn = Button(
            text='📅',
            size_hint_x=None,
            width=dp(50),
            font_size='16sp',
            background_color=(0.3, 0.8, 0.6, 1)
        )
        details_btn.bind(on_press=lambda x: on_view_details(habit_data) if on_view_details else None)
        buttons_layout.add_widget(details_btn)
        
        # Кнопка "Настройки"
        edit_btn = Button(
            text='⚙️',
            size_hint_x=None,
            width=dp(50),
            font_size='16sp',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        edit_btn.bind(on_press=lambda x: on_edit(habit_data) if on_edit else None)
        buttons_layout.add_widget(edit_btn)
        
        # Кнопка "Удалить"
        delete_btn = Button(
            text='🗑️',
            size_hint_x=None,
            width=dp(50),
            font_size='16sp',
            background_color=(0.8, 0.3, 0.3, 1)
        )
        delete_btn.bind(on_press=lambda x: on_delete(habit_data) if on_delete else None)
        buttons_layout.add_widget(delete_btn)
        
        self.add_widget(buttons_layout)


class OptionsScreen(Screen):
    """Экран настроек и управления привычками"""
    
    # Properties for data binding
    habits_model = ObjectProperty(None, allownone=True)
    habits_list = ListProperty([])
    status_message = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info('OptionsScreen: Initializing options screen')
        
        # Initialize data model (will be set later by the main app)
        self.habits_model = None
        
        # Initialize file manager
        self.file_manager = FileManager()
        
        # UI components
        self.content_layout = None
        self.add_habit_input = None
        self.habits_list_layout = None
        self.status_label = None
        
        # Flag to prevent circular updates
        self._updating_habits_list = False
        
        # Build UI
        Clock.schedule_once(self.build_ui, 0.1)
        
    def on_habits_model(self, instance, value):
        """Called when habits_model property changes"""
        if value is not None:
            Logger.info('OptionsScreen: Habits model connected')
            value.bind(on_data_changed=self.on_data_changed)
            # Reload habits list
            self.load_habits_list()
        
    def build_ui(self, dt=None):
        """Построение интерфейса экрана"""
        Logger.info('OptionsScreen: Building UI')
        
        # Основной layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Заголовок
        title_label = Label(
            text='Настройки привычек',
            size_hint_y=None,
            height=dp(50),
            font_size='24sp',
            bold=True
        )
        main_layout.add_widget(title_label)
        
        # Секция добавления новой привычки
        self.add_habit_section(main_layout)
        
        # Секция списка привычек
        self.add_habits_list_section(main_layout)
        
        # Секция импорта/экспорта
        self.add_import_export_section(main_layout)
        
        # Статусная строка
        self.status_label = Label(
            text='Готов к работе',
            size_hint_y=None,
            height=dp(30),
            font_size='14sp',
            color=(0.6, 0.6, 0.6, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # Кнопка "Назад"
        back_btn = Button(
            text='← Назад к трекеру',
            size_hint_y=None,
            height=dp(50),
            font_size='16sp',
            background_color=(0.3, 0.6, 1, 1)
        )
        back_btn.bind(on_press=self.go_back_to_tracker)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)
        
        # Загрузить список привычек
        self.load_habits_list()
        
    def add_habit_section(self, parent_layout):
        """Добавляет секцию для создания новой привычки"""
        # Заголовок секции
        section_label = Label(
            text='Добавить новую привычку:',
            size_hint_y=None,
            height=dp(30),
            font_size='18sp',
            bold=True,
            halign='left'
        )
        section_label.bind(size=section_label.setter('text_size'))
        parent_layout.add_widget(section_label)
        
        # Layout для ввода
        input_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        # Поле ввода названия привычки
        self.add_habit_input = TextInput(
            hint_text='Название новой привычки',
            size_hint_x=0.7,
            multiline=False,
            font_size='16sp'
        )
        self.add_habit_input.bind(on_text_validate=self.add_new_habit)
        input_layout.add_widget(self.add_habit_input)
        
        # Кнопка добавления
        add_btn = Button(
            text='Добавить',
            size_hint_x=0.3,
            font_size='16sp',
            background_color=(0.3, 0.8, 0.3, 1)
        )
        add_btn.bind(on_press=self.add_new_habit)
        input_layout.add_widget(add_btn)
        
        parent_layout.add_widget(input_layout)
        
    def add_habits_list_section(self, parent_layout):
        """Добавляет секцию со списком привычек"""
        # Заголовок секции
        section_label = Label(
            text='Управление привычками:',
            size_hint_y=None,
            height=dp(30),
            font_size='18sp',
            bold=True,
            halign='left'
        )
        section_label.bind(size=section_label.setter('text_size'))
        parent_layout.add_widget(section_label)
        
        # Scrollable список привычек
        scroll = ScrollView(size_hint=(1, 0.4))
        self.habits_list_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.habits_list_layout.bind(minimum_height=self.habits_list_layout.setter('height'))
        scroll.add_widget(self.habits_list_layout)
        parent_layout.add_widget(scroll)
        
    def add_import_export_section(self, parent_layout):
        """Добавляет секцию импорта/экспорта данных"""
        # Section header
        section_label = Label(
            text='Backup & Restore:',
            size_hint_y=None,
            height=dp(30),
            font_size='18sp',
            bold=True,
            halign='left'
        )
        section_label.bind(size=section_label.setter('text_size'))
        parent_layout.add_widget(section_label)
        
        # Layout for import/export buttons
        backup_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        # Export button
        export_btn = Button(
            text='📤 Export CSV',
            font_size='16sp',
            background_color=(0.6, 0.8, 0.3, 1)
        )
        export_btn.bind(on_press=self.export_data)
        backup_layout.add_widget(export_btn)
        
        # Import button
        import_btn = Button(
            text='📥 Import CSV',
            font_size='16sp',
            background_color=(0.3, 0.6, 0.8, 1)
        )
        import_btn.bind(on_press=self.import_data)
        backup_layout.add_widget(import_btn)
        
        parent_layout.add_widget(backup_layout)
        
    def load_habits_list(self):
        """Загружает список привычек из модели данных"""
        Logger.info('OptionsScreen: Loading habits list')
        
        if not self.habits_model:
            Logger.warning('OptionsScreen: No habits model available')
            self.update_status('Модель данных не доступна')
            return
        
        # Set flag to prevent circular updates
        self._updating_habits_list = True
        
        try:
            self.habits_list = self.habits_model.get_habits_list()
            self.rebuild_habits_list()
            self.update_status(f'Загружено {len(self.habits_list)} привычек')
        except Exception as e:
            Logger.error(f'OptionsScreen: Error loading habits list: {e}')
            self.update_status(f'Ошибка загрузки: {e}')
        finally:
            # Always reset the flag
            self._updating_habits_list = False
            
    def _delayed_load_habits_list(self, dt):
        """Отложенная загрузка списка привычек"""
        # Additional check to prevent cascading calls
        if hasattr(self, '_last_load_time'):
            import time
            if time.time() - self._last_load_time < 0.5:  # Less than 0.5 seconds ago
                Logger.info('OptionsScreen: Skipping delayed load - too soon after last load')
                return
        
        import time
        self._last_load_time = time.time()
        self.load_habits_list()
            
    def rebuild_habits_list(self):
        """Перестраивает UI список привычек"""
        if not self.habits_list_layout:
            return
            
        # Очистить существующий список
        self.habits_list_layout.clear_widgets()
        
        # Добавить элементы для каждой привычки
        for habit in self.habits_list:
            item = HabitListItem(
                habit_data=habit,
                on_edit=self.edit_habit,
                on_delete=self.delete_habit,
                on_move_up=self.move_habit_up,
                on_move_down=self.move_habit_down,
                on_view_details=self.view_habit_details
            )
            self.habits_list_layout.add_widget(item)
            
        Logger.info(f'OptionsScreen: Rebuilt habits list with {len(self.habits_list)} items')
        
    def add_new_habit(self, *args):
        """Добавляет новую привычку"""
        if not self.add_habit_input:
            return
            
        name = self.add_habit_input.text.strip()
        if not name:
            self.update_status('Введите название привычки')
            return
            
        Logger.info(f'OptionsScreen: Adding new habit: {name}')
        
        # Добавить через модель данных
        habit_id = self.habits_model.add_habit(name)
        
        if habit_id:
            self.add_habit_input.text = ''
            self.update_status(f'Привычка "{name}" добавлена')
            # Note: load_habits_list() will be called automatically via on_data_changed event
        else:
            self.update_status('Ошибка добавления привычки')
            
    def view_habit_details(self, habit_data):
        """Открывает экран календаря привычки"""
        Logger.info(f'OptionsScreen: View habit details {habit_data.get("id")} - {habit_data.get("name")}')
        
        # Navigate to habit detail screen
        if self.manager:
            habit_detail_screen = self.manager.get_screen('habit_detail')
            habit_detail_screen.load_habit_data(habit_data.get("id"))
            self.manager.current = 'habit_detail'
        else:
            self.update_status('Error: No screen manager available')
            
    def edit_habit(self, habit_data):
        """Открывает экран редактирования привычки"""
        Logger.info(f'OptionsScreen: Edit habit {habit_data.get("id")} - {habit_data.get("name")}')
        
        # Navigate to habit edit screen
        if self.manager:
            habit_edit_screen = self.manager.get_screen('habit_edit')
            habit_edit_screen.load_habit_data(habit_data.get("id"))
            self.manager.current = 'habit_edit'
        else:
            self.update_status('Ошибка: Нет менеджера экранов')
        
    def delete_habit(self, habit_data):
        """Удаляет привычку с подтверждением"""
        habit_name = habit_data.get('name', 'Неизвестная привычка')
        habit_id = habit_data.get('id')
        
        Logger.info(f'OptionsScreen: Delete habit {habit_id} - {habit_name}')
        
        # Показать диалог подтверждения
        dialog = ConfirmationDialog(
            title='Удаление привычки',
            message=f'Вы уверены, что хотите удалить привычку "{habit_name}"?\n\nВсе данные отслеживания будут потеряны!',
            on_confirm=lambda: self._confirm_delete_habit(habit_id, habit_name)
        )
        dialog.open()
        
    def _confirm_delete_habit(self, habit_id, habit_name):
        """Подтверждение удаления привычки"""
        success = self.habits_model.delete_habit(habit_id)
        
        if success:
            self.update_status(f'Привычка "{habit_name}" удалена')
            # Note: load_habits_list() will be called automatically via on_data_changed event
        else:
            self.update_status('Ошибка удаления привычки')
            
    def move_habit_up(self, habit_data):
        """Перемещает привычку вверх"""
        habit_id = habit_data.get('id')
        habit_name = habit_data.get('name', '')
        
        Logger.info(f'OptionsScreen: Move habit up: {habit_id} - {habit_name}')
        
        success = self.habits_model.reorder_habit(habit_id, 'up')
        
        if success:
            self.update_status(f'Привычка "{habit_name}" перемещена вверх')
            # Note: load_habits_list() will be called automatically via on_data_changed event
        else:
            self.update_status('Ошибка перемещения привычки')
            
    def move_habit_down(self, habit_data):
        """Перемещает привычку вниз"""
        habit_id = habit_data.get('id')
        habit_name = habit_data.get('name', '')
        
        Logger.info(f'OptionsScreen: Move habit down: {habit_id} - {habit_name}')
        
        success = self.habits_model.reorder_habit(habit_id, 'down')
        
        if success:
            self.update_status(f'Привычка "{habit_name}" перемещена вниз')
            # Note: load_habits_list() will be called automatically via on_data_changed event
        else:
            self.update_status('Ошибка перемещения привычки')
            
    def export_data(self, *args):
        """Export data to CSV file"""
        Logger.info('OptionsScreen: Export data to CSV')
        
        if not self.habits_model:
            self.update_status('Error: No data model available')
            return
        
        try:
            # Show file save dialog
            self.file_manager.show_export_dialog(self._on_export_file_selected)
            self.update_status('Select export file location...')
            
        except Exception as e:
            Logger.error(f'OptionsScreen: Error starting export: {e}')
            self.update_status(f'Export error: {e}')
    
    def _on_export_file_selected(self, file_path):
        """Handle export file selection"""
        Logger.info(f'OptionsScreen: Export file selected: {file_path}')
        
        try:
            # Get CSV data from database
            csv_lines = list(self.habits_model.database.export_to_csv())
            
            # Write to file
            success = self.file_manager.write_csv_file(file_path, csv_lines)
            
            if success:
                self.update_status(f'Data exported successfully to {file_path}')
                Logger.info(f'OptionsScreen: Export completed: {len(csv_lines)} lines')
            else:
                self.update_status('Error writing CSV file')
                
        except Exception as e:
            Logger.error(f'OptionsScreen: Error during export: {e}')
            self.update_status(f'Export error: {e}')
        
    def import_data(self, *args):
        """Import data from CSV file"""
        Logger.info('OptionsScreen: Import data from CSV')
        
        if not self.habits_model:
            self.update_status('Error: No data model available')
            return
        
        try:
            # Show file open dialog
            self.file_manager.show_import_dialog(self._on_import_file_selected)
            self.update_status('Select CSV file to import...')
            
        except Exception as e:
            Logger.error(f'OptionsScreen: Error starting import: {e}')
            self.update_status(f'Import error: {e}')
    
    def _on_import_file_selected(self, file_path):
        """Handle import file selection"""
        Logger.info(f'OptionsScreen: Import file selected: {file_path}')
        
        try:
            # Check if file exists
            if not self.file_manager.file_exists(file_path):
                self.update_status('Error: File not found')
                return
            
            # Read CSV file
            csv_lines = self.file_manager.read_csv_file(file_path)
            
            if csv_lines is None:
                self.update_status('Error reading CSV file')
                return
            
            # Show confirmation dialog
            self._show_import_confirmation(file_path, csv_lines)
            
        except Exception as e:
            Logger.error(f'OptionsScreen: Error during import: {e}')
            self.update_status(f'Import error: {e}')
    
    def _show_import_confirmation(self, file_path, csv_lines):
        """Show import confirmation dialog"""
        file_size = self.file_manager.get_file_size(file_path)
        
        message = f'Import data from:\n{file_path}\n\nFile size: {file_size} bytes\nLines: {len(csv_lines)}\n\nWARNING: This will replace all existing data!'
        
        dialog = ConfirmationDialog(
            title='Confirm Import',
            message=message,
            on_confirm=lambda: self._perform_import(csv_lines)
        )
        dialog.open()
    
    def _perform_import(self, csv_lines):
        """Perform the actual import operation"""
        Logger.info(f'OptionsScreen: Performing import with {len(csv_lines)} lines')
        
        try:
            # Import data using database
            self.habits_model.database.import_from_csv(csv_lines)
            
            # Refresh the habits model and UI
            self.habits_model.refresh_all_data()
            self.load_habits_list()
            
            self.update_status(f'Import completed successfully ({len(csv_lines)} lines)')
            Logger.info('OptionsScreen: Import completed successfully')
            
        except Exception as e:
            Logger.error(f'OptionsScreen: Error during import: {e}')
            self.update_status(f'Import error: {e}')
        
    def go_back_to_tracker(self, *args):
        """Возврат к главному экрану трекера"""
        Logger.info('OptionsScreen: Go back to tracker')
        
        # Переключиться на главный экран
        if self.manager:
            self.manager.current = 'main_tracker'
        else:
            Logger.warning('OptionsScreen: No screen manager found')
            
    def on_data_changed(self, *args):
        """Обработка изменений в данных"""
        # Prevent circular updates
        if self._updating_habits_list:
            Logger.info('OptionsScreen: Data changed during update, skipping reload to prevent cycle')
            return
            
        Logger.info('OptionsScreen: Data changed, scheduling habits list reload')
        # Schedule reload to prevent immediate circular calls
        Clock.schedule_once(self._delayed_load_habits_list, 0.1)
        
    def update_status(self, message):
        """Обновляет статусное сообщение"""
        self.status_message = message
        if self.status_label:
            self.status_label.text = message
        Logger.info(f'OptionsScreen: Status - {message}')
        
    def on_enter(self):
        """Вызывается при входе на экран"""
        Logger.info('OptionsScreen: Screen entered')
        self.load_habits_list()
        
    def on_leave(self):
        """Вызывается при выходе с экрана"""
        Logger.info('OptionsScreen: Screen left') 