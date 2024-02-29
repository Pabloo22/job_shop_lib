from __future__ import annotations

from typing import Optional

from job_shop_lib import Operation
from job_shop_lib.graphs.constants import NodeType


class Node:
    __slots__ = "node_type", "_node_id"

    def __init__(self, node_type: NodeType):
        self.node_type = node_type
        self._node_id: Optional[int] = None

    @staticmethod
    def create_node_with_data(
        node_type: NodeType, data: Operation | int
    ) -> Node | OperationNode | MachineNode | JobNode:
        node_info_map = {
            NodeType.OPERATION: (OperationNode, Operation),
            NodeType.MACHINE: (MachineNode, int),
            NodeType.JOB: (JobNode, int),
        }
        if node_type not in node_info_map:
            raise ValueError(
                f"NodeTypes not supported by the factory must "
                f"Supported types are {list(node_info_map.keys())}"
            )

        node_class, expected_type = node_info_map[node_type]

        if not isinstance(data, expected_type):
            raise ValueError(
                f"Expected value type {expected_type}, got {type(data)}"
            )

        return node_class(data)

    @property
    def node_id(self) -> int:
        if self._node_id is None:
            raise ValueError("Node has not been assigned an id.")
        return self._node_id

    @node_id.setter
    def node_id(self, value: int) -> None:
        self._node_id = value

    def __hash__(self) -> int:
        return self.node_id

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Node):
            __value = __value.node_id
        return self.node_id == __value

    def __repr__(self) -> str:
        return f"Node(node_type={self.node_type.name}, id={self._node_id})"


class OperationNode(Node):
    __slots__ = ("operation",)

    def __init__(self, operation: Operation):
        super().__init__(NodeType.OPERATION)
        self.operation = operation

    @property
    def machine_id(self) -> int:
        return self.operation.machine_id

    @property
    def machines(self) -> int:
        return self.operation.machines

    @property
    def job_id(self) -> int:
        return self.operation.job_id

    @property
    def duration(self) -> int:
        return self.operation.duration

    def __repr__(self) -> str:
        return (
            f"OperationNode(node_type={self.node_type.name}, "
            f"id={self._node_id}, operation={self.operation})"
        )


class MachineNode(Node):
    __slots__ = ("machine_id",)

    def __init__(self, machine_id: int):
        super().__init__(NodeType.MACHINE)
        self.machine_id = machine_id

    def __repr__(self) -> str:
        return (
            f"MachineNode(node_type={self.node_type.name}, id={self._node_id},"
            f" machine_id={self.machine_id})"
        )


class JobNode(Node):
    __slots__ = ("job_id",)

    def __init__(self, job_id: int):
        super().__init__(NodeType.JOB)
        self.job_id = job_id

    def __repr__(self) -> str:
        return (
            f"JobNode(node_type={self.node_type.name}, id={self._node_id}, "
            f"job_id={self.job_id})"
        )
