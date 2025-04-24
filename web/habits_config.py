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