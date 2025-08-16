"""
Habit Edit Screen

Screen for editing individual habit parameters and settings.
Allows editing habit name, fail_by_default, bad_habit, and levels parameters.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.logger import Logger
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock


class HabitEditScreen(Screen):
    """Screen for editing individual habit parameters"""
    
    # Properties
    habit_id = NumericProperty(0)
    habit_name = StringProperty('')
    habits_model = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info('HabitEditScreen: Initializing')
        
        # UI components
        self.name_input: TextInput = None
        self.fail_by_default_checkbox: CheckBox = None
        self.bad_habit_checkbox: CheckBox = None
        self.levels_spinner: Spinner = None
        self.status_label: Label = None
        
        # Current parameter values
        self.current_params = {
            'fail_by_default': '0',
            'bad_habit': '0',
            'levels': '0'
        }
        
        # Build UI
        Clock.schedule_once(self.build_ui, 0.1)
        
    def build_ui(self, *args):
        """Build the user interface"""
        try:
            # Main container
            main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            
            # Header with back button
            header_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            
            back_btn = Button(
                text='← Back to Options',
                size_hint_x=None,
                width=dp(150),
                font_size='16sp',
                background_color=(0.3, 0.6, 1, 1)
            )
            back_btn.bind(on_press=self.go_back)
            header_layout.add_widget(back_btn)
            
            # Title
            title_label = Label(
                text='Edit Habit',
                font_size='24sp',
                size_hint_x=None,
                width=dp(200),
                halign='center'
            )
            header_layout.add_widget(title_label)
            
            # Spacer
            header_layout.add_widget(Label())
            
            main_layout.add_widget(header_layout)
            
            # Scrollable content
            from kivy.uix.scrollview import ScrollView
            scroll = ScrollView()
            content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(20))
            content_layout.bind(minimum_height=content_layout.setter('height'))
            
            # Habit name section
            content_layout.add_widget(self.create_name_section())
            
            # Parameters section
            content_layout.add_widget(self.create_parameters_section())
            
            # Action buttons
            content_layout.add_widget(self.create_action_buttons())
            
            # Status message
            self.status_label = Label(
                text='',
                size_hint_y=None,
                height=dp(30),
                font_size='14sp',
                color=(0.8, 0.8, 0.8, 1)
            )
            content_layout.add_widget(self.status_label)
            
            scroll.add_widget(content_layout)
            main_layout.add_widget(scroll)
            
            self.add_widget(main_layout)
            
            Logger.info('HabitEditScreen: UI built successfully')
            
        except Exception as e:
            Logger.error(f'HabitEditScreen: Error building UI: {e}')
            
    def create_name_section(self):
        """Create the habit name editing section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(10))
        
        # Title
        title = Label(
            text='Habit Name',
            font_size='18sp',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Input field
        self.name_input = TextInput(
            text=self.habit_name,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size='16sp'
        )
        section.add_widget(self.name_input)
        
        # Rename button
        rename_btn = Button(
            text='Rename Habit',
            size_hint_y=None,
            height=dp(40),
            font_size='16sp',
            background_color=(0.2, 0.7, 0.2, 1)
        )
        rename_btn.bind(on_press=self.rename_habit)
        section.add_widget(rename_btn)
        
        return section
        
    def create_parameters_section(self):
        """Create the parameters editing section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(300), spacing=dp(15))
        
        # Title
        title = Label(
            text='Habit Parameters',
            font_size='18sp',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Parameters grid
        from kivy.uix.gridlayout import GridLayout
        params_grid = GridLayout(cols=2, size_hint_y=None, height=dp(250), spacing=dp(10))
        
        # Fail by default parameter
        params_grid.add_widget(Label(
            text='Fail by Default:\n(Mark as failed if not set)',
            font_size='14sp',
            halign='left',
            valign='middle'
        ))
        
        fail_layout = BoxLayout(size_hint_x=None, width=dp(60))
        self.fail_by_default_checkbox = CheckBox(
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        fail_layout.add_widget(self.fail_by_default_checkbox)
        params_grid.add_widget(fail_layout)
        
        # Bad habit parameter
        params_grid.add_widget(Label(
            text='Bad Habit:\n(Invert status colors)',
            font_size='14sp',
            halign='left',
            valign='middle'
        ))
        
        bad_layout = BoxLayout(size_hint_x=None, width=dp(60))
        self.bad_habit_checkbox = CheckBox(
            size_hint=(None, None),
            size=(dp(40), dp(40))
        )
        bad_layout.add_widget(self.bad_habit_checkbox)
        params_grid.add_widget(bad_layout)
        
        # Levels parameter
        params_grid.add_widget(Label(
            text='Status Levels:\n(Number of available statuses)',
            font_size='14sp',
            halign='left',
            valign='middle'
        ))
        
        levels_layout = BoxLayout(size_hint_x=None, width=dp(150))
        self.levels_spinner = Spinner(
            text='Standard (All)',
            values=['Simple (3)', 'Standard (All)', 'Numeric (0-9)'],
            size_hint=(None, None),
            size=(dp(140), dp(40))
        )
        levels_layout.add_widget(self.levels_spinner)
        params_grid.add_widget(levels_layout)
        
        # Add explanation
        explanation = Label(
            text='• Simple: Only Not Set, Done, Failed\n• Standard: All status types\n• Numeric: Numbers 0-9',
            font_size='12sp',
            size_hint_y=None,
            height=dp(60),
            halign='left',
            valign='top',
            color=(0.6, 0.6, 0.6, 1)
        )
        explanation.bind(size=explanation.setter('text_size'))
        params_grid.add_widget(explanation)
        params_grid.add_widget(Label())  # Empty cell
        
        section.add_widget(params_grid)
        
        return section
        
    def create_action_buttons(self):
        """Create action buttons section"""
        section = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # Save button
        save_btn = Button(
            text='Save Changes',
            font_size='16sp',
            background_color=(0.2, 0.7, 0.2, 1)
        )
        save_btn.bind(on_press=self.save_parameters)
        section.add_widget(save_btn)
        
        # Reset button
        reset_btn = Button(
            text='Reset to Defaults',
            font_size='16sp',
            background_color=(0.7, 0.7, 0.2, 1)
        )
        reset_btn.bind(on_press=self.reset_parameters)
        section.add_widget(reset_btn)
        
        return section
        
    def go_back(self, *args):
        """Go back to options screen"""
        if self.manager:
            self.manager.current = 'options'
            
    def load_habit_data(self, habit_id: int):
        """Load habit data for editing"""
        try:
            self.habit_id = habit_id
            
            if not self.habits_model:
                self.show_status('Error: No data model available', 'error')
                return
                
            # Get habit data
            habit_data = self.habits_model.get_habit_data(habit_id)
            if not habit_data:
                self.show_status('Error: Habit not found', 'error')
                return
                
            self.habit_name = habit_data.get('name', '')
            
            # Load parameters
            self.current_params['fail_by_default'] = self.habits_model.get_habit_parameter(habit_id, 'fail_by_default', '0')
            self.current_params['bad_habit'] = self.habits_model.get_habit_parameter(habit_id, 'bad_habit', '0')
            self.current_params['levels'] = self.habits_model.get_habit_parameter(habit_id, 'levels', '0')
            
            # Update UI
            self.update_ui_from_params()
            
            Logger.info(f'HabitEditScreen: Loaded habit data for ID {habit_id}')
            self.show_status(f'Editing habit: {self.habit_name}', 'info')
            
        except Exception as e:
            Logger.error(f'HabitEditScreen: Error loading habit data: {e}')
            self.show_status('Error loading habit data', 'error')
            

        
    def update_ui_from_params(self):
        """Update UI elements from current parameters"""
        try:
            # Update name input
            if self.name_input:
                self.name_input.text = self.habit_name
            
            # Update checkboxes
            if self.fail_by_default_checkbox:
                self.fail_by_default_checkbox.active = self.current_params['fail_by_default'] == '1'
                
            if self.bad_habit_checkbox:
                self.bad_habit_checkbox.active = self.current_params['bad_habit'] == '1'
                
            # Update levels spinner
            if self.levels_spinner:
                levels_value = self.current_params['levels']
                if levels_value == '1':
                    self.levels_spinner.text = 'Simple (3)'
                elif levels_value == '10':
                    self.levels_spinner.text = 'Numeric (0-9)'
                else:
                    self.levels_spinner.text = 'Standard (All)'
                    
        except Exception as e:
            Logger.error(f'HabitEditScreen: Error updating UI from params: {e}')
            
    def rename_habit(self, *args):
        """Rename the habit"""
        try:
            new_name = self.name_input.text.strip()
            if not new_name:
                self.show_status('Error: Name cannot be empty', 'error')
                return
                
            if not self.habits_model:
                self.show_status('Error: No data model available', 'error')
                return
                
            # Rename through model
            success = self.habits_model.rename_habit(self.habit_id, new_name)
            
            if success:
                self.habit_name = new_name
                self.show_status(f'Habit renamed to: {new_name}', 'success')
                Logger.info(f'HabitEditScreen: Renamed habit {self.habit_id} to {new_name}')
            else:
                self.show_status('Error: Failed to rename habit', 'error')
                
        except Exception as e:
            Logger.error(f'HabitEditScreen: Error renaming habit: {e}')
            self.show_status('Error renaming habit', 'error')
            
    def save_parameters(self, *args):
        """Save all parameters"""
        try:
            if not self.habits_model:
                self.show_status('Error: No data model available', 'error')
                return
                
            # Get values from UI
            fail_by_default = '1' if self.fail_by_default_checkbox.active else '0'
            bad_habit = '1' if self.bad_habit_checkbox.active else '0'
            
            # Convert levels spinner text to value
            levels_text = self.levels_spinner.text
            if levels_text == 'Simple (3)':
                levels = '1'
            elif levels_text == 'Numeric (0-9)':
                levels = '10'
            else:
                levels = '0'  # Standard
                
            # Save each parameter
            params_to_save = {
                'fail_by_default': fail_by_default,
                'bad_habit': bad_habit,
                'levels': levels
            }
            
            success_count = 0
            for param_name, value in params_to_save.items():
                if self.habits_model.set_habit_parameter(self.habit_id, param_name, value):
                    success_count += 1
                    
            if success_count == len(params_to_save):
                self.current_params.update(params_to_save)
                self.show_status('All parameters saved successfully', 'success')
                Logger.info(f'HabitEditScreen: Saved parameters for habit {self.habit_id}')
            else:
                self.show_status(f'Warning: Only {success_count}/{len(params_to_save)} parameters saved', 'warning')
                
        except Exception as e:
            Logger.error(f'HabitEditScreen: Error saving parameters: {e}')
            self.show_status('Error saving parameters', 'error')
            
    def reset_parameters(self, *args):
        """Reset parameters to default values"""
        try:
            # Show confirmation dialog
            self.show_reset_confirmation()
            
        except Exception as e:
            Logger.error(f'HabitEditScreen: Error resetting parameters: {e}')
            self.show_status('Error resetting parameters', 'error')
            
    def show_reset_confirmation(self):
        """Show confirmation dialog for resetting parameters"""
        from kivy.uix.popup import Popup
        
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        message = Label(
            text='Reset all parameters to default values?\n\nThis action cannot be undone.',
            font_size='16sp',
            halign='center'
        )
        content.add_widget(message)
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        yes_btn = Button(
            text='Yes, Reset',
            background_color=(0.8, 0.3, 0.3, 1)
        )
        
        no_btn = Button(
            text='Cancel',
            background_color=(0.3, 0.6, 1, 1)
        )
        
        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        
        content.add_widget(buttons)
        
        popup = Popup(
            title='Reset Parameters',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        yes_btn.bind(on_press=lambda x: self.confirm_reset(popup))
        no_btn.bind(on_press=lambda x: popup.dismiss())
        
        popup.open()
        
    def confirm_reset(self, popup):
        """Confirm and execute parameter reset"""
        try:
            popup.dismiss()
            
            if not self.habits_model:
                self.show_status('Error: No data model available', 'error')
                return
                
            # Reset to default values
            default_params = {
                'fail_by_default': '0',
                'bad_habit': '0',
                'levels': '0'
            }
            
            success_count = 0
            for param_name, value in default_params.items():
                if self.habits_model.set_habit_parameter(self.habit_id, param_name, value):
                    success_count += 1
                    
            if success_count == len(default_params):
                self.current_params.update(default_params)
                self.update_ui_from_params()
                self.show_status('Parameters reset to defaults', 'success')
                Logger.info(f'HabitEditScreen: Reset parameters for habit {self.habit_id}')
            else:
                self.show_status(f'Warning: Only {success_count}/{len(default_params)} parameters reset', 'warning')
                
        except Exception as e:
            Logger.error(f'HabitEditScreen: Error confirming reset: {e}')
            self.show_status('Error resetting parameters', 'error')
            

            
    def show_status(self, message: str, status_type: str = 'info'):
        """Show status message"""
        if not self.status_label:
            return
            
        colors = {
            'info': (0.8, 0.8, 0.8, 1),
            'success': (0.2, 0.8, 0.2, 1),
            'warning': (0.8, 0.8, 0.2, 1),
            'error': (0.8, 0.2, 0.2, 1)
        }
        
        self.status_label.text = message
        self.status_label.color = colors.get(status_type, colors['info'])
        
        # Clear status after 5 seconds
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', ''), 5)
        
    def on_enter(self):
        """Called when entering the screen"""
        Logger.info('HabitEditScreen: Screen entered')
        
    def on_leave(self):
        """Called when leaving the screen"""
        Logger.info('HabitEditScreen: Screen left') 