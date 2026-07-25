class Config:
    """Configuration settings for habits tracker"""

    # Path to database file
    HABITS_WEB_DB_PATH = "habits.db"

    # Maximum number of habits allowed
    MAX_HABITS = 50

    # Maximum number of tracking records allowed
    MAX_RECORDS = 500_000

    # Whether to create database tables if they are missing
    CREATE_TABLES_IF_MISSING = True

    # How often (in minutes) the browser reconnects after a failed keepalive.
    # Also used as the long-poll hold duration on the server.
    # 0 disables the connection monitor feature.
    CONNECTION_CHECK_INTERVAL_MIN = 5.0