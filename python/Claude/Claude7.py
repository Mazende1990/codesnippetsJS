"""A directed graph implementation using SQLAlchemy."""

from sqlalchemy import Column, Integer, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Create base class for declarative models
Base = declarative_base()


class Node(Base):
    """Represents a node in a directed graph."""
    
    __tablename__ = "node"
    node_id = Column(Integer, primary_key=True)
    
    def higher_neighbors(self):
        """Return all nodes that this node points to."""
        return [edge.higher_node for edge in self.lower_edges]
    
    def lower_neighbors(self):
        """Return all nodes that point to this node."""
        return [edge.lower_node for edge in self.higher_edges]


class Edge(Base):
    """Represents a directed edge between two nodes."""
    
    __tablename__ = "edge"
    
    lower_id = Column(Integer, ForeignKey("node.node_id"), primary_key=True)
    higher_id = Column(Integer, ForeignKey("node.node_id"), primary_key=True)
    
    # Relationships to access connected nodes
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
    
    def __init__(self, lower_node, higher_node):
        """Initialize an edge from lower_node to higher_node."""
        self.lower_node = lower_node
        self.higher_node = higher_node


def main():
    # Set up database
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create a directed graph like this:
    #       n1 -> n2 -> n1
    #                -> n5
    #                -> n7
    #          -> n3 -> n6
    
    # Create nodes
    nodes = {i: Node() for i in range(1, 8)}
    
    # Create edges
    edges = [
        Edge(nodes[1], nodes[2]),  # n1 -> n2
        Edge(nodes[1], nodes[3]),  # n1 -> n3
        Edge(nodes[2], nodes[1]),  # n2 -> n1
        Edge(nodes[2], nodes[5]),  # n2 -> n5
        Edge(nodes[2], nodes[7]),  # n2 -> n7
        Edge(nodes[3], nodes[6]),  # n3 -> n6
    ]
    
    # Add all objects to the session
    session.add_all(list(nodes.values()))
    session.commit()
    
    # Verify the graph structure
    n1, n2, n3 = nodes[1], nodes[2], nodes[3]
    
    assert [x for x in n3.higher_neighbors()] == [nodes[6]]
    assert [x for x in n3.lower_neighbors()] == [nodes[1]]
    assert [x for x in n2.lower_neighbors()] == [nodes[1]]
    assert sorted([x.node_id for x in n2.higher_neighbors()]) == sorted([nodes[1].node_id, nodes[5].node_id, nodes[7].node_id])
    print("All assertions passed!")


if __name__ == "__main__":
    main()