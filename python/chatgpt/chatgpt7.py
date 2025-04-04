"""
Directed graph example using SQLAlchemy.

This defines a simple graph with nodes and directed edges, and provides
methods for querying the neighbors of each node.
"""

from sqlalchemy import (
    Column,
    create_engine,
    ForeignKey,
    Integer,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Node(Base):
    """
    Represents a graph node.
    Each node has a unique ID and can access its neighbors through relationships.
    """
    __tablename__ = "node"

    node_id = Column(Integer, primary_key=True)

    def higher_neighbors(self):
        """
        Returns nodes this node has outgoing edges to.
        """
        return [edge.higher_node for edge in self.lower_edges]

    def lower_neighbors(self):
        """
        Returns nodes that have edges pointing to this node.
        """
        return [edge.lower_node for edge in self.higher_edges]


class Edge(Base):
    """
    Represents a directed edge between two nodes:
    - lower_node -> higher_node
    """
    __tablename__ = "edge"

    lower_id = Column(Integer, ForeignKey("node.node_id"), primary_key=True)
    higher_id = Column(Integer, ForeignKey("node.node_id"), primary_key=True)

    lower_node = relationship(
        Node,
        primaryjoin=lower_id == Node.node_id,
        backref="lower_edges"
    )
    higher_node = relationship(
        Node,
        primaryjoin=higher_id == Node.node_id,
        backref="higher_edges"
    )

    def __init__(self, from_node, to_node):
        self.lower_node = from_node
        self.higher_node = to_node


def setup_database(echo=False):
    """
    Sets up the in-memory SQLite database and returns a session.
    """
    engine = create_engine("sqlite://", echo=echo)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def build_sample_graph(session):
    """
    Constructs a sample directed graph and commits it to the database.
    Graph structure:
        n1 -> n2 -> n1
                   -> n5
                   -> n7
             -> n3 -> n6
    """
    # Create nodes
    n1, n2, n3, n4, n5, n6, n7 = [Node() for _ in range(7)]

    # Create directed edges
    edges = [
        Edge(n1, n2),
        Edge(n1, n3),
        Edge(n2, n1),
        Edge(n2, n5),
        Edge(n2, n7),
        Edge(n3, n6)
    ]

    session.add_all([n1, n2, n3, n4, n5, n6, n7] + edges)
    session.commit()

    return n1, n2, n3, n4, n5, n6, n7


if __name__ == "__main__":
    session = setup_database(echo=True)
    n1, n2, n3, _, n5, n6, n7 = build_sample_graph(session)

    # Assertions to validate graph structure
    assert n3.higher_neighbors() == [n6]
    assert n3.lower_neighbors() == [n1]
    assert n2.lower_neighbors() == [n1]
    assert sorted(n2.higher_neighbors(), key=lambda x: x.node_id) == sorted([n1, n5, n7], key=lambda x: x.node_id)
