class Config:
    """Set Flask config variables."""

    FLASK_APP = 'start.py'
    FLASK_DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database/uitslag.sqlite'

    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    import secrets
    SECRET_KEY = secrets.token_hex(64)
