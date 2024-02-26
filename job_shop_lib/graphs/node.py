from typing import Any
from dataclasses import dataclass, field

from job_shop_lib.graphs.constants import NodeTypes, NODE_ID_DEFAULT


@dataclass(slots=True)
class Node:
    node_type: NodeTypes
    value: Any = None
    node_id: int = field(default=NODE_ID_DEFAULT, init=False)

    def __hash__(self) -> int:
        if self.node_id == NODE_ID_DEFAULT:
            raise ValueError("Node has not been assigned an id.")
        return hash(self.node_id)
