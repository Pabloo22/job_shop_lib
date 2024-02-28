import enum


class EdgeType(enum.Enum):
    """Enumeration of edge types."""

    CONJUNCTIVE = 0
    DISJUNCTIVE = 1


class NodeType(enum.Enum):
    """Enumeration of node types."""

    OPERATION = enum.auto()
    MACHINE = enum.auto()
    JOB = enum.auto()
    GLOBAL = enum.auto()
    SOURCE = enum.auto()
    SINK = enum.auto()


# We use a default value of -1 to indicate that the node has not been
# assigned an id yet at the same time we avoid problems with the type checker.
NODE_ID_DEFAULT = -1
