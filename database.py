from sqlalchemy import create_engine, Column, Boolean, Integer, String, DateTime, Text, Enum, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Graphs(Base):
    __tablename__ = "Graphs"

    name = Column(String(200), unique=True, primary_key=True)
    current_index = Column(Integer, default=0)

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
    __tablename__ = "Egdes"
    index_from = Column(Integer, ForeignKey("Vertices.index", ondelete="CASCADE"), default=0, primary_key=True)
    # index_from = Column(Integer, ForeignKey("Vertices.index", ondelete="CASCADE"), default=0, primary_key=True)
    index_to = Column(Integer, ForeignKey("Vertices.index", ondelete="CASCADE"), default=0, primary_key=True)
    # index_to = Column(Integer, ForeignKey("Vertices.index", ondelete="CASCADE"), default=0, primary_key=True)
    name = Column(String(200), ForeignKey("Graphs.name", ondelete="CASCADE"), primary_key=True)

    edges_to_name = relationship("Graphs", back_populates="name_to_edges")
    edge_from_index = relationship("Vertices", back_populates="index_from_edge")
    edge_to_index = relationship("Vertices", back_populates="index_to_edge")


def populate_database(user, passw):
    print('Creating engine...')
    db_engine = create_database_engine(user, passw)
    print('Creating database and tables...')
    drop_database(db_engine)
    create_database(db_engine)


def create_database_engine(user, passw):
    engine = create_engine("mysql+pymysql://" + user + ":" + passw + "@localhost", echo=False)
    return engine


def drop_database(engine):
    engine.execute('DROP DATABASE IF EXISTS scheduling;')


def create_database(engine):
    engine.execute('CREATE DATABASE scheduling;')
    engine.execute('USE scheduling;')
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    username = "root"
    password = "sjc93545"
    populate_database(username, password)
