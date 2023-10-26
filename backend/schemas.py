import database as db
import sqlalchemy

metadata = sqlalchemy.MetaData()
types = sqlalchemy.Table("types", metadata, autoload_with=db.engine)
move_categories = sqlalchemy.Table("move_categories", metadata, autoload_with=db.engine)
moves = sqlalchemy.Table("moves", metadata, autoload_with=db.engine)
pokemon = sqlalchemy.Table("pokemon", metadata, autoload_with=db.engine)