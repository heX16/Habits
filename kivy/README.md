# Habits Simple Tracker - Kivy App

Cross-platform mobile and desktop application for habit tracking, migrated from the web version.

## Features

- **Cross-platform**: Runs on Android, iOS, Windows, macOS, and Linux
- **Touch-friendly**: Optimized for both touch and mouse interaction
- **Offline-capable**: Full functionality without internet connection
- **Native integration**: Platform-specific notifications and file system access

## Project Structure

```
kivy/
├── main.py                 # Application entry point
├── app/
│   ├── models/            # Database and domain logic
│   ├── screens/           # UI screens (Main, Options, Details)
│   ├── widgets/           # Custom UI widgets
│   ├── services/          # Background services
│   └── assets/            # Images and Kivy layout files
│       ├── images/        # Status icons and app icons
│       └── kv/            # Kivy layout definitions
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Installation

### Development Setup

1. **Install Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

### Platform-Specific Packaging

#### Android (using Buildozer)
```bash
pip install buildozer
buildozer android debug
```

#### Windows Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

#### Linux AppImage
```bash
pip install appimage-builder
# Configure appimage-builder.yml
appimage-builder
```

## Usage

### Main Screen
- View your habits in a 7-day table format
- Single-click to cycle through status: Not Set → Mini → Done → Elite → Failed
- Double-click for status selection menu
- Swipe or use arrow buttons to navigate dates

### Options Screen
- Add/remove habits
- Reorder habits with drag-and-drop
- Export/import data as CSV
- Configure global settings

### Habit Details
- View individual habit calendar
- Edit habit-specific parameters
- Analyze habit statistics

## Migration from Web Version

This Kivy app reuses the existing SQLite database and core business logic from the web version:

- **Database**: Compatible with existing `habits.db` file
- **CSV Export/Import**: Same format as web version
- **Status System**: Identical status meanings and behavior
- **Business Logic**: Preserved habit parameters and validation rules

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
```

### Project Structure Notes

- **Models**: Reuse `common_lib/habits_database.py` without changes
- **Screens**: Each major UI view (Main, Options, Details, Edit)
- **Widgets**: Reusable UI components (StatusCell, HabitRow, etc.)
- **Services**: Background tasks, notifications, file management

## License

[Add your license here]

## Contributing

[Add contribution guidelines here] 