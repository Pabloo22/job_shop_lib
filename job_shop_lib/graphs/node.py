from __future__ import annotations

from typing import Optional

from job_shop_lib import Operation
from job_shop_lib.graphs.constants import NodeType


class Node:
    __slots__ = "node_type", "_node_id", "_operation", "_machine_id", "_job_id"

    def __init__(
        self,
        node_type: NodeType,
        operation: Optional[Operation] = None,
        machine_id: Optional[int] = None,
        job_id: Optional[int] = None,
    ):
        if node_type == NodeType.OPERATION and operation is None:
            raise ValueError("Operation node must have an operation.")

        if node_type == NodeType.MACHINE and machine_id is None:
            raise ValueError("Machine node must have a machine_id.")

        if node_type == NodeType.JOB and job_id is None:
            raise ValueError("Job node must have a job_id.")

        self.node_type = node_type
        self._node_id: Optional[int] = None

        self._operation = operation
        self._machine_id = machine_id
        self._job_id = job_id

    @property
    def node_id(self) -> int:
        if self._node_id is None:
            raise ValueError("Node has not been assigned an id.")
        return self._node_id

    @node_id.setter
    def node_id(self, value: int) -> None:
        self._node_id = value

    @property
    def operation(self) -> Operation:
        if self._operation is None:
            raise ValueError("Node has no operation.")
        return self._operation

    @property
    def machine_id(self) -> int:
        if self._machine_id is None:
            raise ValueError("Node has no machine_id.")
        return self._machine_id

    @property
    def job_id(self) -> int:
        if self._job_id is None:
            raise ValueError("Node has no job_id.")
        return self._job_id

    def __hash__(self) -> int:
        return self.node_id

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Node):
            __value = __value.node_id
        return self.node_id == __value

    def __repr__(self) -> str:
        if self.node_type == NodeType.OPERATION:
            return (
                f"Node(node_type={self.node_type.name}, id={self._node_id}, "
                f"operation={self.operation})"
            )
        if self.node_type == NodeType.MACHINE:
            return (
                f"Node(node_type={self.node_type.name}, id={self._node_id}, "
                f"machine_id={self._machine_id})"
            )
        if self.node_type == NodeType.JOB:
            return (
                f"Node(node_type={self.node_type.name}, id={self._node_id}, "
                f"job_id={self._job_id})"
            )
        return f"Node(node_type={self.node_type.name}, id={self._node_id})"
