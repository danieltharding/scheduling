from sqlalchemy import event, create_engine, DDL, Column, Boolean, Integer, String, DateTime, Text, Enum, ForeignKey, \
    Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os

Base = declarative_base()
SQLALCHEMY_DB_URL = "mysql+pymysql://p5rs0n8ml1amynog:cs187til91cux7wd@s465z7sj4pwhp7fn.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/zohis47bslyjovcl"
databse_name = "zohis47bslyjovcl"


class Graphs(Base):
    __tablename__ = "Graphs"

    name = Column(String(200), unique=True, primary_key=True)
    current_index = Column(Integer, server_default="0")

    name_to_vertex = relationship("Vertices", back_populates="vertex_to_name")
    name_to_edges = relationship("Edges", back_populates="edges_to_name")


class Vertices(Base):
    __tablename__ = "Vertices"

    vertex_name = Column(String(200), primary_key=True)
    index = Column(Integer, default=0)
    name = Column(String(200), ForeignKey("Graphs.name", ondelete="CASCADE"), primary_key=True)

    vertex_to_name = relationship("Graphs", back_populates="name_to_vertex")
    index_from_edge = relationship("Edges", back_populates="edge_from_index")
    index_to_edge = relationship("Edges", back_populates="edge_to_index")


vertices_index = Index("vertices_index", Vertices.index)


class Edges(Base):
    __tablename__ = "Edges"
    index_from = Column(Integer, ForeignKey("Vertices.index", ondelete="CASCADE"), default=0, primary_key=True)
    # index_from = Column(Integer, ForeignKey("Vertices.index", ondelete="CASCADE"), default=0, primary_key=True)
    index_to = Column(Integer, ForeignKey("Vertices.index", ondelete="CASCADE"), default=0, primary_key=True)
    # index_to = Column(Integer, ForeignKey("Vertices.index", ondelete="CASCADE"), default=0, primary_key=True)
    name = Column(String(200), ForeignKey("Graphs.name", ondelete="CASCADE"), primary_key=True)

    edges_to_name = relationship("Graphs", back_populates="name_to_edges")
    edge_from_index = relationship("Vertices", back_populates="index_from_edge")
    edge_to_index = relationship("Vertices", back_populates="index_to_edge")


trigger = DDL('''/
    CREATE TRIGGER trig AFTER INSERT On Vertices
    FOR EACH ROW
    BEGIN
        Update Graphs
            set current_index = current_index + 1
        where name = NEW.name;
    end;
''')

event.listen(Vertices, 'after_insert', trigger)


def populate_database(user, passw):
    print('Creating engine...')
    db_engine = create_database_engine(user, passw)
    print('Creating database and tables...')
    # drop_database(db_engine)
    create_database(db_engine)


def create_database_engine(user, passw):
    engine = create_engine("mysql+pymysql://" + user + ":" + passw + "@localhost", echo=False)
    engine = create_engine(SQLALCHEMY_DB_URL)
    return engine


def drop_database(engine):
    # engine.execute('DROP DATABASE IF EXISTS {};'.format(databse_name))
    return


def create_database(engine):
    # engine.execute('CREATE DATABASE {};'.format(databse_name))
    use(engine)
    Base.metadata.create_all(engine)
    create_trigger(engine)


def use(engine):
    engine.execute('USE {};'.format(databse_name))


def create_trigger(engine):
    engine.execute('''CREATE TRIGGER trig AFTER INSERT On Vertices
        FOR EACH ROW
        BEGIN
            Update Graphs
                set current_index = current_index + 1
            where name = NEW.name;
        end;''')


if __name__ == "__main__":
    username = "root"
    password = "sjc93545"
    populate_database(username, password)
