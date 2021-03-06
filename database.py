from sqlalchemy import event, create_engine, DDL, Column, Boolean, Integer, String, DateTime, Text, Enum, ForeignKey, \
    Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from dotenv import load_dotenv
import os

Base = declarative_base()
load_dotenv()
SQLALCHEMY_DB_URL = os.getenv("DB_CONN")
# databse_name = "zohis47bslyjovcl"
database_name = "scheduling"


class Graphs(Base):
    __tablename__ = "Graphs"

    name = Column(String(200), unique=True, primary_key=True)
    current_index = Column(Integer, server_default="0")

    name_to_vertex = relationship("Vertices", back_populates="vertex_to_name")
    name_to_edges = relationship("Edges", back_populates="edges_to_name")
    name_to_pot_edges = relationship("Pot_edges", back_populates="pot_edges_to_name")


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


class Pot_Edges(Base):
    __tablename__ = "Pot_edges"

    name = Column(String(200), ForeignKey("Graphs.name", ondelete="CASCADE"), primary_key=True)
    edges = Column(Text)

    pot_edges_to_name = relationship("Graphs", back_populates="name_to_pot_edges")


def populate_database():
    print('Creating engine...')
    db_engine = create_database_engine()
    print('Creating database and tables...')
    drop_database(db_engine)
    create_database(db_engine)


def create_database_engine():
    engine = create_engine(SQLALCHEMY_DB_URL)
    return engine


def drop_database(engine):
    engine.execute("DROP TABLE Pot_edges")
    engine.execute("DROP TABLE Edges")
    engine.execute("DROP TABLE Vertices")
    engine.execute("DROP TABLE Graphs")
    return


def create_database(engine):
    use(engine)
    Base.metadata.create_all(engine)
    create_trigger(engine)


def use(engine):
    engine.execute('USE {};'.format(database_name))


def create_trigger(engine):
    engine.execute('''CREATE TRIGGER trig AFTER INSERT On Vertices
        FOR EACH ROW
        BEGIN
            Update Graphs
                set current_index = current_index + 1
            where name = NEW.name;
        end;''')
    engine.execute('''
    CREATE TRIGGER trig2 AFTER INSERT ON Graphs
    FOR EACH ROW 
    BEGIN 
        INSERT INTO Pot_edges (`name`, edges) VALUE (NEW.name, '');
    end;
        
''')


if __name__ == "__main__":
    populate_database()
