# Назначение этого файла

Привет, Claude! Этот файл создан для сохранения знаний об архитектуре проекта между сессиями диалога. Поскольку диалог может быть перезапущен, ты теряешь контекст и знания о проекте. Этот файл поможет тебе быстро восстановить понимание архитектуры и особенностей проекта без необходимости заново анализировать весь код.

Этот файл следует читать в начале новой сессии, когда пользователь просит тебя продолжить работу над проектом. Здесь будет содержаться самая важная информация, которая поможет тебе эффективно продолжить разработку.

# Описание проекта Habits Simple Tracker

Проект — трекер привычек. Пользователи создают привычки, отмечают выполнение по дням и смотрят прогресс в таблице.

Есть два клиента с общей SQLite-базой (`common_lib/habits_database.py`): веб (Flask) и Kivy. Этот файл описывает **веб-приложение**.

Комментарии в исходном коде — на английском.
Все сообщения и строки в проекте — на английском.

## Интерфейс главной страницы

### Внешний вид
- Таблица: привычки в строках, даты в столбцах (`tableDaysCount` = 10 дней)
- Диапазон дат заканчивается ближайшим воскресеньем (включительно)
- Заголовки столбцов: дата и день недели
- Текущий день визуально выделен, будущие дни отображаются иначе
- Статусы в ячейках — эмодзи из `getStatusOptions`
- Индикатор сохранения (💾) при непустой очереди обновлений
- Имя привычки — ссылка на страницу `/habit/<id>`

### Поведение
- Одиночный клик: циклическое переключение по списку статусов из `getStatusOptions(bad_habit, levels)`
- Двойной клик: откат первого клика (окно ~300 мс) и меню со всеми доступными статусами
- Обновления статусов копятся в очереди (последнее значение на ячейку) и уходят пакетом каждые `UPDATE_QUEUE_INTERVAL_MS` (по умолчанию 2000 мс)
- Автообновление страницы в полночь со случайной задержкой 0–60 с
- `fail_by_default`: на бэкенде неотмеченные дни строго между первой записью трекинга и сегодня маппятся в `FAIL` (9)
- `?date=YYYY-MM-DD` смещает базовую дату таблицы; появляется кнопка "Today", которая убирает параметр из URL
- Long-poll `/api/keepalive` (`connection_monitor.js`): при обрыве связи флаг `offline` и уведомление

## Интерфейс страницы Options (`/options`)

### Внешний вид
Секции: Habits Management, Backup & Restore, Global Options.

### Options, секция "Habits Management"
- Форма добавления привычки
- Список привычек: ↑ / ↓ / Options / Delete; ↑ и ↓ отключены у первой и последней

Поведение:
- Добавление: мгновенное обновление списка
- Удаление: `confirm("Are you sure you want to delete habit \"...\"?")`
- Перемещение: `POST /api/habits/reorder` (`direction`: `up` | `down`)
- Options ведёт на `/habit/<id>/options`

### Options, секция "Backup & Restore"
- Экспорт CSV: `HabitsDatabase.export_to_csv`
- Импорт CSV: `HabitsDatabase.import_from_csv` — **полная перезапись** БД (clear + recreate)

### Options, секция "Global Options"
- Путь к файлу БД (только отображение)
- Чекбокс `test_option` (тестовый параметр)
- `theme` есть в whitelist глобальных параметров, UI темы пока нет

## Страница настроек привычки (`/habit/<id>/options`)

Параметры: `fail_by_default`, `bad_habit`, `levels` (select: 1 / 3 / 10), переименование.

# Архитектура проекта

## Обзор структуры

1. **Общая БД**
   - `common_lib/habits_database.py` — класс `HabitsDatabase` (SQLite)

2. **Веб-бэкенд (Flask)**
   - `web/habits_core.py` — бизнес-логика API, путь к БД, `prepare_js_constants`
   - `web/flask_backend_core.py` — маршруты Flask
   - `web/habits_config.py` — лимиты и интервалы (`MAX_HABITS` 50, `MAX_RECORDS` 500_000)
   - `web/flask_backend.py` — точка входа

3. **Фронтенд**
   - `templates/`
     - `index.html` — главная таблица (предрендер пустых строк)
     - `habit.html` — календарь одной привычки
     - `habit_options.html` — настройки привычки
     - `options.html` — глобальные настройки
     - `constants.js` — **шаблон Jinja2**, не обычный JS
   - `static/`
     - `script.js` — главная таблица
     - `habit.js` — страница привычки
     - `habit_options.js` — настройки привычки
     - `options_habit_edit.js` — список привычек на Options
     - `menu.js` — плавающее меню статусов
     - `notifications.js` — уведомления
     - `connection_monitor.js` — long-poll keepalive
     - `style.css`

Путь к БД: `--db-path` > env `HABITS_WEB_DB_PATH` > `Config.HABITS_WEB_DB_PATH` (`habits.db`).

## API-эндпоинты

Страницы: `/`, `/options`, `/habit/<id>`, `/habit/<id>/options`.

- `GET /api/habits` — трекинг за диапазон дат (`start_date`, `end_date`, опционально `habit_id`)
- `POST /api/habits/update` — статус ячейки (`habit_id`, `date`, `status`); статус `0` удаляет запись
- `POST /api/habits/add` — новая привычка
- `DELETE /api/habits/delete` — удаление
- `GET /api/habits/list` — список (id, name, sequence)
- `POST /api/habits/rename`
- `POST /api/habits/reorder` — `{ habit_id, direction: "up"|"down" }`
- `GET /api/habits/export` / `POST /api/habits/import`
- `GET|POST /api/param/<name>` — глобальный параметр (`habit_id = -1`)
- `GET|POST /api/param/<name>/<id>` — параметр привычки
- `GET /api/main_page` — данные главной страницы (+ `message`, если БД read-only)
- `GET /api/keepalive` — long-poll на `CONNECTION_CHECK_INTERVAL_MIN` минут (0 = выключено)
- `GET /js/constants.js` — сгенерированные константы и `statusOptionsData`

На странице привычки данные берутся через `/habit/<id>/api/habits`.

## База данных

SQLite, три таблицы:

- `habits_list` — `id`, `name` (UNIQUE), `sequence` (порядок; при добавлении `max(sequence)+10`)
- `habit_tracking` — PK `(habit_id, date)`, `status`; дата `'YYYY-MM-DD'`
- `habit_params` — PK `(habit_id, param_name)`, `value` всегда строка; глобальные параметры: `habit_id = -1` (`HabitsDatabase.GLOBAL_PARAMS`)

Версия схемы: `db_version` в глобальных параметрах (`HabitsDatabase.DB_VERSION`).

# Ключевые механизмы

## Параметры

Whitelist:

- `VALID_HABIT_PARAMS`: `fail_by_default`, `bad_habit`, `levels`
- `VALID_GLOBAL_PARAMS`: `theme`, `test_option`, `db_version`

Неизвестные имена отклоняются в `validate_param`. Устаревшие `single_checkbox`, `multi_numbers`, `mode` **не** входят в whitelist.

- `fail_by_default` (`'1'`/`'0'`): в `status_mapping` неотмеченный день (`NOT_SET`) между `first_tracking_date` (не включая) и `today` (не включая) становится `FAIL` (9)
- `bad_habit`: на фронте выбирается набор `bh*` вместо `gh*` (инвертированные подписи/цвета)
- `levels`:
  - `1` — три статуса: not set / done / fail (`gh1` / `bh1`)
  - `3` — полный набор mini / done / elite / fail (`gh3` / `bh3`)
  - `10` — числа 0–9 (коды 10–19) плюс fail (`gh10` / `bh10`)
  - отсутствие параметра или `0`: бэкенд не применяет сжатие LEVEL_1/LEVEL_10; фронт `getStatusOptions` при falsy `levels` берёт набор `'1'`

В ответе `fetch_habit` у каждой привычки уже есть `bad_habit`, `levels`, `first_tracking_date`, массив `tracking`.

## Сортировка

`ORDER BY sequence, id`. `set_habit_sequence` / `reorder_habit` (обмен sequence; при равных значениях +1). Порядок сохраняется в CSV.

## Статусы (`HabitStatus`)

Внутренние коды:

- `0` NOT_SET — не установлено (в БД запись не хранится)
- `1` DONE_MINI, `2` DONE, `3` DONE_ELITE
- `9` FAIL
- `10`–`19` NUMBER_0 … NUMBER_9 (на экране цифры 0–9)

`status_mapping` при чтении: в режиме LEVEL_1 mini/elite → DONE; в LEVEL_10 нечисловые статусы (кроме 0) → NOT_SET; плюс `fail_by_default`.

Наборы для UI задаёт `get_status_lists()` (`gh1`/`gh3`/`gh10`, `bh1`/`bh3`/`bh10`) и попадают в `constants.js` как `statusOptionsData`. `getStatusEmoji` и цикл клика опираются на `getStatusOptions`, а не на захардкоженную цепочку 0→1→2→3→9.

## Рендеринг главной страницы

`fetchHabitsData` → `GET /api/main_page` → `habitsData` → `renderTable`. Ячейки: `handleCellClick` / `handleCellDblClick` / `enqueueUpdate`.

## `constants.js`

Генерируется `prepare_js_constants`: `tableDaysCount`, `approximateHabitsCount`, `CONNECTION_CHECK_INTERVAL_MIN`, `UPDATE_QUEUE_INTERVAL_MS`, `weekDays`, `statusOptionsData`, `getStatusOptions(bad_habit, levels)`. Кеширующие заголовки на эндпоинте.

## Оптимизации

- Предрендер пустых строк таблицы
- Кеш `constants.js`
- Очередь обновлений статусов (дедуп по ячейке)
- Keepalive long-poll вместо частого ping

# Страница отдельной привычки

- Календари с квадратными ячейками (~32×32), выравнивание влево
- `renderMonth` всегда рисует 6 строк; пустые ячейки — класс `empty`
- Ссылки `W<n>` ведут на `/?date=YYYY-MM-DD`
- Данные: `GET` с `habit_id` за диапазон дат

# Заметки

- Параметры в БД — строки; булевы привычные значения `'0'`/`'1'` (глобальный `test_option` в UI сравнивается с `'true'`)
- Импорт CSV полностью затирает текущую БД
- Read-only файл БД: главная страница получает `data.message`
- TODO в `fetch_habit`: `first_tracking_date` уходит как объект `date` (сериализация Flask не в `YYYY-MM-DD`)
