# 🔄 Phase 5.1 Progress: Table Widget Refactoring

**Date:** 06.07.2025  
**Status:** 📋 PLANNING - Ready for Implementation  
**Current Progress:** 5/7 phases completed (71% complete)

## Project Overview - Habits Simple Tracker (Kivy)

This is a cross-platform habit tracking application migrated from a web version to Kivy. The project reuses the existing SQLite database and core business logic while providing native mobile/desktop experience.

### Architecture:
- **Data Layer**: SQLite database with HabitsDatabase class (unchanged from web version)
- **Domain Logic**: HabitsModel class adapted from web version
- **UI Layer**: Kivy screens (MainTrackerScreen, OptionsScreen, HabitDetailScreen, HabitEditScreen)
- **Widgets**: Custom components (StatusCell, HabitRow, DateHeader, etc.)
- **Services**: Background tasks, file management, notifications

### Key Features Implemented:
- ✅ Main habit tracking table (7-day view)
- ✅ Status cycling (single click) and status menu (double click)
- ✅ Options screen with habit management
- ✅ CSV export/import functionality
- ✅ Individual habit calendar view (2-month display)
- ✅ Cross-platform file management

## Current State: Table Widget Analysis

### Recent Achievements:
1. **HabitDetailScreen refactoring completed** - Successfully moved from duplicate code to using `table_widget.py`
2. **InteractiveCalendarCell added** - New widget class for calendar interactions
3. **create_calendar_table() function added** - Unified calendar creation approach

### Current Issues in `table_widget.py`:
The file has grown to 441 lines and contains several code quality issues that need refactoring.

## 🎯 NEXT TASK: Table Widget Refactoring

### **Priority 1: Core Refactoring (Critical)**

#### 1.1 **TableStyleManager** (LOW PRIORITY)
**Problem**: Styles are scattered across multiple functions and hardcoded
**Current Issues**:
- Colors hardcoded in `create_cell()`, `InteractiveCalendarCell._update_background()`, `update_table()`
- Sizes (dp(40), dp(2), dp(15)) repeated everywhere
- Status colors duplicated in UI code

**Solution**: Create centralized style management
```python
class TableStyleManager:
    # Centralized colors, sizes, themes
    # Methods: get_cell_style(), get_status_color(), get_table_config()
```

#### 1.2 **InteractiveCalendarCell Decomposition** (MEDIUM PRIORITY)
**Problem**: 200+ line monolithic class mixing multiple responsibilities
**Current Issues**:
- Display logic mixed with interaction logic
- Business logic (status handling) in UI code
- Hard to test and maintain

**Solution**: Split into components:
```python
class CalendarCellRenderer:      # Only visual display
class CalendarCellInteraction:   # Only event handling  
class StatusDisplayManager:      # Status logic
```

#### 1.3 **TableFactory Pattern** (MEDIUM PRIORITY)
**Problem**: Duplicate ScrollView+GridLayout creation code
**Current Issues**:
- `create_table_widget()` and `create_calendar_table()` duplicate setup
- No unified interface for table creation

**Solution**: Unified factory approach
```python
class TableFactory:
    @staticmethod
    def create_simple_table(...)
    @staticmethod  
    def create_interactive_table(...)
    @staticmethod
    def create_calendar_table(...)
```

### **Priority 2: Code Quality (Important)**

#### 2.1 **Configuration Management**
**Problem**: Magic numbers and hardcoded values
**Solution**: Create `TableConfig` class

#### 2.2 **Error Handling**
**Problem**: Inconsistent error handling and logging
**Solution**: Unified error handling system

#### 2.3 **Type Hints**
**Problem**: No type annotations
**Solution**: Add comprehensive type hints

### **Priority 3: Architecture (HI PRIORITY)**

#### 3.1 **Cell Type Hierarchy**
**Problem**: Отсутствие абстракции для типов ячеек
**Current Issues**:
- Сейчас есть только Label (простые ячейки) и InteractiveCalendarCell (сложные ячейки)
- Нет общего интерфейса для всех типов ячеек
- Дублирование кода при создании разных типов ячеек
- Сложно добавлять новые типы ячеек

**Solution**: Создать иерархию классов:
```python
BaseCell -> LabelCell, InteractiveCell
```
- `BaseCell` - базовый класс с общими свойствами
- `LabelCell` - наследник для простых ячеек
- `InteractiveCell` - наследник для интерактивных ячеек

#### 3.2 **Status Logic Separation**
Move status business logic to services layer

## 📋 Implementation Plan

### **Step 1: Create TableStyleManager**
1. Create `app/widgets/table_styles.py`
2. Move all style constants and color logic
3. Update all references in `table_widget.py`

### **Step 2: Refactor InteractiveCalendarCell**
1. Extract `CalendarCellRenderer` for display
2. Extract `CalendarCellInteraction` for events  
3. Move status logic to services
4. Update imports and usage

### **Step 3: Implement TableFactory**
1. Create factory methods
2. Refactor existing functions to use factory
3. Remove duplicated code

### **Step 4: Add Configuration & Error Handling**
1. Create `TableConfig` class
2. Add comprehensive error handling
3. Add type hints throughout

### **Step 5: Testing & Validation**
1. Test all table creation scenarios
2. Validate calendar interactions
3. Ensure backward compatibility

## 🎮 Instructions for Next AI Instance

### **Context Setup:**
1. **Read this file first** to understand current state
2. **Review `kivy/app/widgets/table_widget.py`** - the main file to refactor
3. **Check `kivy/app/screens/habit_detail_screen.py`** - main consumer of table widgets
4. **Understand the project structure** from `kivy/README.md`

### **Immediate Actions:**
1. **Start with Priority 1.1** - TableStyleManager is the highest impact
2. **Keep existing functionality** - This is refactoring, not rewriting
3. **Test after each change** - Use `python run_dev.py` to test
4. **Focus on one component at a time** - Don't try to refactor everything at once

### **Key Principles:**
- **Preserve existing interfaces** - Other screens depend on current functions
- **Maintain backward compatibility** - Don't break existing code
- **Follow Kivy best practices** - Use proper widget hierarchies
- **Keep it simple** - Don't over-engineer the solution

### **Success Criteria:**
- [ ] Styles centralized in TableStyleManager
- [ ] InteractiveCalendarCell split into logical components
- [ ] No duplicate ScrollView/GridLayout creation code
- [ ] All magic numbers moved to configuration
- [ ] Comprehensive error handling
- [ ] Type hints added
- [ ] All existing functionality preserved
- [ ] Tests pass: `python run_dev.py` works without errors

### **Files to Focus On:**
- `kivy/app/widgets/table_widget.py` (MAIN TARGET)
- `kivy/app/screens/habit_detail_screen.py` (MAIN CONSUMER)
- `kivy/app/screens/main_tracker_screen.py` (ANOTHER CONSUMER)
- `kivy/app/widgets/status_cell.py` (RELATED WIDGET)

### **Warning Signs:**
- If any screen stops working → rollback and try smaller changes
- If imports break → check all import statements
- If performance degrades → review widget creation logic

## 🏁 Next Phase After Refactoring

Once table widget refactoring is complete:
**Phase 6**: Visual effects, animations, notifications, and themes

**Current completion**: 71% → Target: 80% after this refactoring

---

**Remember**: This is a working application with users. Prioritize stability and backward compatibility over perfect architecture! 