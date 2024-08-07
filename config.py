class Config:
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '890527'
    MYSQL_DB = 'venue_booking'
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_CURSORCLASS = 'DictCursor'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:890527@localhost/venue_booking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_ID = 'wx666e0c0e26d4d33e'
    APP_SECRET = '9c351869c1c6e30160dc832796dfdacc'
    SERVER_SECRET = 'a3c9f9b10a2e4a8fb0931fc2ed5ab1d4f3c5c34c79a6e6d0'
