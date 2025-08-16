#!/usr/bin/env python3
"""
Quick test script for Habits Simple Tracker

Tests basic functionality before mobile packaging.
"""

import sys
import os
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all imports work correctly"""
    print("🔍 Testing imports...")
    
    try:
        from app.models import HabitsModel, DateCalculator
        from app.screens import MainTrackerScreen, OptionsScreen, HabitEditScreen, HabitDetailScreen
        from app.widgets import NotificationManager
        from app.services import AppStateManager, FileManager
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("🔍 Testing database...")
    
    try:
        from app.models import HabitsModel
        
        # Test with temporary database
        test_db_path = "test_habits.db"
        model = HabitsModel(db_path=test_db_path)
        
        # Test basic operations
        habit_id = model.add_habit("Test Habit")
        habits = model.get_habits_list()
        
        assert len(habits) == 1
        assert habits[0]['name'] == "Test Habit"
        
        # Cleanup
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            
        print("✅ Database tests passed")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_app_structure():
    """Test app structure and files"""
    print("🔍 Testing app structure...")
    
    required_files = [
        "main.py",
        "app/__init__.py",
        "app/models/__init__.py",
        "app/screens/__init__.py", 
        "app/widgets/__init__.py",
        "app/services/__init__.py",
        "app/assets/kv/main_tracker.kv",
        "buildozer.spec",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all tests"""
    print("🚀 Habits Simple Tracker - Pre-packaging Test")
    print("=" * 50)
    
    tests = [
        test_app_structure,
        test_imports,
        test_database
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for packaging.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix before packaging.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
