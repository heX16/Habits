"""
FileManager Service

Cross-platform file management service for CSV export/import and other file operations.
Handles platform-specific file dialogs and file system access.
"""

import os
import csv
from pathlib import Path
from typing import List, Optional, Callable
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.clock import Clock


class FileChooserDialog(Popup):
    """Cross-platform file chooser dialog"""
    
    def __init__(self, mode='open', file_filters=None, on_selection=None, **kwargs):
        super().__init__(**kwargs)
        
        self.mode = mode  # 'open' or 'save'
        self.file_filters = file_filters or []
        self.on_selection = on_selection
        
        self.title = 'Select File' if mode == 'open' else 'Save File'
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = False
        
        self._build_ui()
        
    def _build_ui(self):
        """Build the file chooser UI"""
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # File chooser
        self.file_chooser = FileChooserIconView(
            size_hint=(1, 0.8),
            filters=self.file_filters
        )
        layout.add_widget(self.file_chooser)
        
        # Filename input (for save mode)
        if self.mode == 'save':
            filename_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            filename_layout.add_widget(Label(text='Filename:', size_hint_x=0.2))
            
            self.filename_input = TextInput(
                text='habits_export.csv',
                size_hint_x=0.8,
                multiline=False
            )
            filename_layout.add_widget(self.filename_input)
            layout.add_widget(filename_layout)
        
        # Buttons
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        # Cancel button
        cancel_btn = Button(text='Cancel', background_color=(0.7, 0.7, 0.7, 1))
        cancel_btn.bind(on_press=self.dismiss)
        buttons_layout.add_widget(cancel_btn)
        
        # Confirm button
        confirm_text = 'Open' if self.mode == 'open' else 'Save'
        confirm_btn = Button(text=confirm_text, background_color=(0.3, 0.6, 1, 1))
        confirm_btn.bind(on_press=self._on_confirm)
        buttons_layout.add_widget(confirm_btn)
        
        layout.add_widget(buttons_layout)
        self.content = layout
        
    def _on_confirm(self, *args):
        """Handle file selection confirmation"""
        if self.mode == 'open':
            # Open mode - get selected file
            if self.file_chooser.selection:
                selected_file = self.file_chooser.selection[0]
                if self.on_selection:
                    self.on_selection(selected_file)
                self.dismiss()
        else:
            # Save mode - construct file path
            if hasattr(self, 'filename_input'):
                filename = self.filename_input.text.strip()
                if filename:
                    file_path = os.path.join(self.file_chooser.path, filename)
                    if self.on_selection:
                        self.on_selection(file_path)
                    self.dismiss()


class FileManager:
    """Cross-platform file management service"""
    
    def __init__(self):
        self.documents_path = self._get_documents_path()
        Logger.info(f'FileManager: Documents path: {self.documents_path}')
        
    def _get_documents_path(self) -> str:
        """Get platform-specific documents directory"""
        try:
            # Try to use user's documents directory
            from kivy.utils import platform
            
            if platform == 'android':
                # Android external storage
                try:
                    from android.storage import primary_external_storage_path
                    return primary_external_storage_path()
                except ImportError:
                    Logger.warning('FileManager: Android storage module not available')
                    return '/storage/emulated/0/Documents'
            elif platform == 'ios':
                # iOS documents directory
                try:
                    from ios import get_documents_dir
                    return get_documents_dir()
                except ImportError:
                    Logger.warning('FileManager: iOS module not available')
                    return str(Path.home() / "Documents")
            else:
                # Desktop platforms
                return str(Path.home() / "Documents")
        except Exception as e:
            Logger.warning(f'FileManager: Could not get documents path: {e}')
            # Fallback to current directory
            return str(Path.cwd())
    
    def show_export_dialog(self, on_file_selected: Callable[[str], None]):
        """Show file save dialog for CSV export"""
        Logger.info('FileManager: Showing export dialog')
        
        dialog = FileChooserDialog(
            mode='save',
            file_filters=['*.csv'],
            on_selection=on_file_selected
        )
        
        # Set initial path to documents
        dialog.file_chooser.path = self.documents_path
        dialog.open()
        
    def show_import_dialog(self, on_file_selected: Callable[[str], None]):
        """Show file open dialog for CSV import"""
        Logger.info('FileManager: Showing import dialog')
        
        dialog = FileChooserDialog(
            mode='open',
            file_filters=['*.csv'],
            on_selection=on_file_selected
        )
        
        # Set initial path to documents
        dialog.file_chooser.path = self.documents_path
        dialog.open()
    
    def write_csv_file(self, file_path: str, csv_lines: List[str]) -> bool:
        """Write CSV lines to file"""
        try:
            Logger.info(f'FileManager: Writing CSV to {file_path}')
            
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                for line in csv_lines:
                    f.write(line + '\n')
            
            Logger.info('FileManager: CSV file written successfully')
            return True
            
        except Exception as e:
            Logger.error(f'FileManager: Error writing CSV file: {e}')
            return False
    
    def read_csv_file(self, file_path: str) -> Optional[List[str]]:
        """Read CSV file and return lines"""
        try:
            Logger.info(f'FileManager: Reading CSV from {file_path}')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n\r') for line in f]
            
            Logger.info(f'FileManager: CSV file read successfully ({len(lines)} lines)')
            return lines
            
        except Exception as e:
            Logger.error(f'FileManager: Error reading CSV file: {e}')
            return None
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except:
            return 0 