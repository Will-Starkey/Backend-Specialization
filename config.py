class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Dragonfly@localhost/mechanics_db'
    DEBUG = True
    
class TestingConfig:
    pass

class ProductionConfig:
    pass