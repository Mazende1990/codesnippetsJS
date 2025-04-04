"""A directed graph example using SQLAlchemy."""

from sqlalchemy import Column, create_engine, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Node(Base):
    """Represents a node in the directed graph."""

    __tablename__ = "node"

    node_id = Column(Integer, primary_key=True)

    def higher_neighbors(self):
        """Returns a list of nodes that are higher neighbors of this node."""
        return [edge.higher_node for edge in self.lower_edges]

    def lower_neighbors(self):
        """Returns a list of nodes that are lower neighbors of this node."""
        return [edge.lower_node for edge in self.higher_edges]


class Edge(Base):
    """Represents a directed edge between two nodes."""

    __tablename__ = "edge"

    lower_id = Column(Integer, ForeignKey("node.node_id"), primary_key=True)
    higher_id = Column(Integer, ForeignKey("node.node_id"), primary_key=True)

    lower_node = relationship(
        Node, primaryjoin=lower_id == Node.node_id, backref="lower_edges"
    )
    higher_node = relationship(
        Node, primaryjoin=higher_id == Node.node_id, backref="higher_edges"
    )

    def __init__(self, lower_node, higher_node):
        """Initializes an edge with lower and higher nodes."""
        self.lower_node = lower_node
        self.higher_node = higher_node


# Setup database and session
engine = create_engine("sqlite://", echo=False)  # echo=False to avoid excessive output
Base.metadata.create_all(engine)
session = sessionmaker(engine)()

# Create nodes
node1 = Node()
node2 = Node()
node3 = Node()
node4 = Node()
node5 = Node()
node6 = Node()
node7 = Node()

# Create edges to form the directed graph
Edge(node1, node2)
Edge(node1, node3)
Edge(node2, node1)
Edge(node2, node5)
Edge(node2, node7)
Edge(node3, node6)

# Add nodes to the session and commit
session.add_all([node1, node2, node3, node4, node5, node6, node7])
session.commit()

# Assertions to verify the graph structure
assert [x for x in node3.higher_neighbors()] == [node6]
assert [x for x in node3.lower_neighbors()] == [node1]
assert [x for x in node2.lower_neighbors()] == [node1]
assert [x for x in node2.higher_neighbors()] == [node1, node5, node7]