import enum


class EdgeType(enum.Enum):
    """Enumeration of edge types."""

    # The values 0 and 1 could be used to index different adjacency matrices.
    CONJUNCTIVE = 0
    DISJUNCTIVE = 1


class NodeType(enum.Enum):
    """Enumeration of node types."""

    # The actual values are not important here.
    OPERATION = enum.auto()
    MACHINE = enum.auto()
    JOB = enum.auto()
    SOURCE = enum.auto()
    SINK = enum.auto()


# We use a default value of -1 to indicate that the node has not been
# assigned an id yet at the same time we avoid problems with the type checker.
NODE_ID_DEFAULT = -1
