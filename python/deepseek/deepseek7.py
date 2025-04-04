"""
A directed graph implementation using SQLAlchemy ORM.

This module defines Node and Edge classes to represent a directed graph structure,
with methods to traverse relationships between nodes.
"""

from sqlalchemy import Column, Integer, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Node(Base):
    """
    Represents a node in a directed graph.
    
    Attributes:
        node_id: Primary key identifier for the node
        lower_edges: Relationship to edges where this node is the lower node
        higher_edges: Relationship to edges where this node is the higher node
    """
    __tablename__ = "node"
    node_id = Column(Integer, primary_key=True)

    def higher_neighbors(self):
        """Get all nodes that this node points to (outgoing edges)."""
        return [edge.higher_node for edge in self.lower_edges]

    def lower_neighbors(self):
        """Get all nodes that point to this node (incoming edges)."""
        return [edge.lower_node for edge in self.higher_edges]

    def __repr__(self):
        return f"<Node(id={self.node_id})>"


class Edge(Base):
    """
    Represents a directed edge between two nodes.
    
    Attributes:
        lower_id: Foreign key to the source node
        higher_id: Foreign key to the target node
        lower_node: Relationship to the source node
        higher_node: Relationship to the target node
    """
    __tablename__ = "edge"
    
    lower_id = Column(
        Integer, 
        ForeignKey("node.node_id"), 
        primary_key=True,
        doc="ID of the source node"
    )
    
    higher_id = Column(
        Integer, 
        ForeignKey("node.node_id"), 
        primary_key=True,
        doc="ID of the target node"
    )

    lower_node = relationship(
        "Node",
        primaryjoin=(lower_id == Node.node_id),
        backref="lower_edges",
        doc="Source node of this edge"
    )

    higher_node = relationship(
        "Node", 
        primaryjoin=(higher_id == Node.node_id),
        backref="higher_edges",
        doc="Target node of this edge"
    )

    def __init__(self, source_node, target_node):
        """
        Initialize a directed edge from source to target node.
        
        Args:
            source_node: The source Node object
            target_node: The target Node object
        """
        self.lower_node = source_node
        self.higher_node = target_node

    def __repr__(self):
        return f"<Edge(from={self.lower_id}, to={self.higher_id})>"


def create_sample_graph(session):
    """
    Create a sample directed graph for demonstration purposes.
    
    The graph structure:
        n1 -> n2 -> n1
                -> n5
                -> n7
          -> n3 -> n6
    """
    # Create nodes
    nodes = {f"n{i}": Node() for i in range(1, 8)}
    
    # Create edges
    edges = [
        Edge(nodes["n1"], nodes["n2"]),
        Edge(nodes["n1"], nodes["n3"]),
        Edge(nodes["n2"], nodes["n1"]),
        Edge(nodes["n2"], nodes["n5"]),
        Edge(nodes["n2"], nodes["n7"]),
        Edge(nodes["n3"], nodes["n6"])
    ]
    
    # Add all objects to session
    session.add_all(nodes.values())
    session.add_all(edges)
    session.commit()
    
    return nodes


def test_graph_relationships(nodes):
    """Verify the expected graph relationships."""
    n1, n2, n3 = nodes["n1"], nodes["n2"], nodes["n3"]
    
    # Test neighbor relationships
    assert [x for x in n3.higher_neighbors()] == [nodes["n6"]]
    assert [x for x in n3.lower_neighbors()] == [nodes["n1"]]
    assert [x for x in n2.lower_neighbors()] == [nodes["n1"]]
    assert [x for x in n2.higher_neighbors()] == [nodes["n1"], nodes["n5"], nodes["n7"]]
    print("All tests passed!")


if __name__ == "__main__":
    # Initialize database
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create and test sample graph
    nodes = create_sample_graph(session)
    test_graph_relationships(nodes)
