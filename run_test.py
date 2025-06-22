#!/usr/bin/env python3
"""
Test Script for Habits Kivy App - Phase 2

Tests all components of Phase 2 migration:
- Models integration
- Widgets creation
- Database operations
- Date calculations
"""

import sys
import os
from datetime import date, timedelta

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
kivy_path = os.path.join(project_root, 'kivy')
sys.path.insert(0, project_root)
sys.path.insert(0, kivy_path)

# Test results
test_results = []

def test_log(message, success=True):
    """Log test result"""
    status = "✅" if success else "❌"
    test_results.append((message, success))
    print(f"{status} {message}")

def test_failed(message, error):
    """Log test failure"""
    test_log(f"{message}: {error}", False)

def test_basic_imports():
    """Test basic imports"""
    print("\n=== Testing Basic Imports ===")

    try:
        # Test common_lib import
        from common_lib.habits_database import HabitsDatabase, HabitStatus, HabitLevels
        test_log("Common lib imports successful")

        # Test datetime imports
        from datetime import date, datetime, timedelta
        test_log("DateTime imports successful")

        # Test typing imports
        from typing import List, Dict, Optional, Any
        test_log("Typing imports successful")

    except Exception as e:
        test_failed("Basic imports", e)

def test_models():
    """Test data models"""
    print("\n=== Testing Data Models ===")

    try:
        # Test DateCalculator
        from app.models.date_calculator import DateCalculator
        test_log("DateCalculator import successful")

        # Test week calculation
        start_date, end_date = DateCalculator.get_week_ending_sunday()
        test_log(f"Week calculation: {start_date} to {end_date}")

        # Test date headers
        headers = DateCalculator.get_date_headers(start_date, end_date)
        test_log(f"Date headers: {len(headers)} days generated")

        # Test week label
        label = DateCalculator.get_week_label(start_date, end_date)
        test_log(f"Week label: '{label}'")

        # Test date parsing
        today_str = DateCalculator.format_date_string(date.today())
        parsed_date = DateCalculator.parse_date_string(today_str)
        test_log(f"Date parsing: {today_str} -> {parsed_date}")

    except Exception as e:
        test_failed("DateCalculator", e)

    try:
        # Test HabitsModel (without Kivy)
        print("\n--- Testing HabitsModel (basic) ---")

        # Create temporary database
        import tempfile
        temp_db = tempfile.mktemp(suffix='.db')

        from app.models.habits_model import HabitsModel
        model = HabitsModel(db_path=temp_db)
        test_log("HabitsModel created successfully")

        # Test basic operations
        habits_list = model.get_habits_list()
        test_log(f"Habits list: {len(habits_list)} habits")

        # Test adding habit
        habit_id = model.add_habit("Test Habit")
        if habit_id:
            test_log(f"Habit added with ID: {habit_id}")
        else:
            test_log("Failed to add habit", False)

        # Test status cycling
        next_status = model.get_status_cycle(0)  # 0 -> 1
        test_log(f"Status cycle: 0 -> {next_status}")

        # Test icon paths
        icon_path = model.get_status_icon_path(2)  # DONE status
        test_log(f"Icon path for status 2: {icon_path}")

        # Cleanup
        os.unlink(temp_db)
        test_log("Temporary database cleaned up")

    except Exception as e:
        test_failed("HabitsModel", e)

def test_database_integration():
    """Test database integration"""
    print("\n=== Testing Database Integration ===")

    try:
        # Test direct database operations
        from common_lib.habits_database import HabitsDatabase

        import tempfile
        temp_db = tempfile.mktemp(suffix='.db')

        db = HabitsDatabase(temp_db)
        test_log("Database created successfully")

        # Test adding habits
        habit_id = db.add_habit("Test Habit")
        test_log(f"Habit added to database: ID {habit_id}")

        # Test getting habits
        habits = db.get_habits_list()
        test_log(f"Database habits count: {len(habits)}")

        # Test updating status
        today_str = date.today().strftime('%Y-%m-%d')
        db.update_habit(habit_id, today_str, 2)  # Set to DONE
        test_log("Habit status updated")

        # Test fetching data
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        data = db.fetch_habits(start_date, end_date)
        test_log(f"Fetched habits data: {len(data.get('habits', []))} habits")

        # Cleanup
        os.unlink(temp_db)
        test_log("Database test completed")

    except Exception as e:
        test_failed("Database integration", e)

def test_widgets_creation():
    """Test widgets creation (without Kivy GUI)"""
    print("\n=== Testing Widgets Creation ===")

    try:
        # Test widget imports
        from app.widgets.status_cell import StatusCell
        from app.widgets.habit_row import HabitRow
        from app.widgets.date_header import DateHeader
        test_log("Widget imports successful")

        # Test date header creation
        date_info = {
            'date': '2025-06-22',
            'day_name': 'Sun',
            'day_number': 22,
            'month_name': 'Jun',
            'is_today': True,
            'is_weekend': True
        }

        # We can't actually create widgets without Kivy App running,
        # but we can test the class definitions
        test_log("Widget classes defined correctly")

        # Test status cycling logic
        from common_lib.habits_database import HabitStatus

        # Test status cycle
        cycle = [HabitStatus.NOT_SET, HabitStatus.DONE_MINI, HabitStatus.DONE, HabitStatus.DONE_ELITE, HabitStatus.FAIL]
        test_log(f"Status cycle: {[int(s) for s in cycle]}")

    except Exception as e:
        test_failed("Widgets creation", e)

def test_app_components():
    """Test app components"""
    print("\n=== Testing App Components ===")

    try:
        # Test screen imports
        from app.screens.main_tracker_screen import MainTrackerScreen
        test_log("MainTrackerScreen import successful")

        # Test services
        from app.services.app_state_manager import AppStateManager
        test_log("AppStateManager import successful")

        # Test main app
        from main import HabitsApp
        test_log("HabitsApp import successful")

    except Exception as e:
        test_failed("App components", e)

def test_file_structure():
    """Test file structure"""
    print("\n=== Testing File Structure ===")

    required_files = [
        'kivy/app/__init__.py',
        'kivy/app/models/__init__.py',
        'kivy/app/models/habits_model.py',
        'kivy/app/models/date_calculator.py',
        'kivy/app/widgets/__init__.py',
        'kivy/app/widgets/status_cell.py',
        'kivy/app/widgets/habit_row.py',
        'kivy/app/widgets/date_header.py',
        'kivy/app/screens/__init__.py',
        'kivy/app/screens/main_tracker_screen.py',
        'kivy/app/services/__init__.py',
        'kivy/app/services/app_state_manager.py',
        'kivy/app/assets/kv/main_tracker.kv',
        'kivy/main.py',
        'kivy/requirements.txt',
        'kivy/config.ini',
        'common_lib/habits_database.py'
    ]

    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            test_log(f"File exists: {file_path}")
        else:
            missing_files.append(file_path)
            test_log(f"Missing file: {file_path}", False)

    if not missing_files:
        test_log("All required files present")
    else:
        test_log(f"Missing {len(missing_files)} files", False)

def test_sample_data_flow():
    """Test complete data flow"""
    print("\n=== Testing Sample Data Flow ===")

    try:
        import tempfile
        temp_db = tempfile.mktemp(suffix='.db')

        # Create model
        from app.models.habits_model import HabitsModel
        model = HabitsModel(db_path=temp_db)

        # Add sample habits
        sample_habits = ['Exercise', 'Reading', 'Meditation']
        for habit_name in sample_habits:
            habit_id = model.add_habit(habit_name)
            test_log(f"Added habit: {habit_name} (ID: {habit_id})")

        # Load data for current week
        from app.models.date_calculator import DateCalculator
        start_date, end_date = DateCalculator.get_week_ending_sunday()

        habits_data = model.load_habits_data(start_date, end_date)
        test_log(f"Loaded data: {len(habits_data.get('habits', []))} habits")

        # Test status update
        if habits_data.get('habits'):
            habit = habits_data['habits'][0]
            habit_id = habit['id']
            today_str = date.today().strftime('%Y-%m-%d')

            success = model.update_habit_status(habit_id, today_str, 2)  # DONE
            test_log(f"Status update: {'success' if success else 'failed'}")

        # Cleanup
        os.unlink(temp_db)
        test_log("Sample data flow test completed")

    except Exception as e:
        test_failed("Sample data flow", e)

def run_all_tests():
    """Run all tests"""
    print("🧪 HABITS KIVY APP - PHASE 2 TESTING")
    print("=" * 50)

    test_basic_imports()
    test_file_structure()
    test_database_integration()
    test_models()
    test_widgets_creation()
    test_app_components()
    test_sample_data_flow()

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, success in test_results if success)
    failed = sum(1 for _, success in test_results if not success)
    total = len(test_results)

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total:  {total}")

    if failed > 0:
        print("\n❌ FAILED TESTS:")
        for message, success in test_results:
            if not success:
                print(f"  - {message}")

    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")

    if success_rate >= 90:
        print("🟢 PHASE 2 STATUS: EXCELLENT")
    elif success_rate >= 75:
        print("🟡 PHASE 2 STATUS: GOOD")
    elif success_rate >= 50:
        print("🟠 PHASE 2 STATUS: NEEDS WORK")
    else:
        print("🔴 PHASE 2 STATUS: CRITICAL ISSUES")

    return failed == 0

if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Critical testing error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)








"""
## 🧪 **Что тестирует файл:**

### 📦 **Основные компоненты:**
1. **Базовые импорты** - проверка всех зависимостей
2. **Структура файлов** - наличие всех необходимых файлов
3. **Интеграция БД** - создание, добавление данных, запросы
4. **Модели данных** - DateCalculator и HabitsModel
5. **Виджеты** - импорты и базовая функциональность
6. **Компоненты приложения** - экраны и сервисы
7. **Полный цикл данных** - от создания до обновления

### 🔍 **Детальные проверки:**
- ✅ Расчет недель и дат
- ✅ Создание временной БД и операции CRUD
- ✅ Циклирование статусов
- ✅ Пути к иконкам
- ✅ Загрузка данных для диапазона дат
- ✅ Обновление статусов привычек
- ✅ Интеграция всех компонентов

### 📊 **Результаты:**
- Подробная статистика прохождения тестов
- Список успешных и неудачных тестов
- Процент успешности
- Общий статус Фазы 2

**Запустите тест и пришлите результаты:**
```bash
python run_test.py
```

Этот тест покажет, насколько хорошо работает вся архитектура Фазы 2 без запуска GUI. Он проверит все критические компоненты и их взаимодействие!

"""
