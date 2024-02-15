import abc
from typing import Iterator, Optional

from job_shop_lib import JobShopInstance


class BaseGenerator(abc.ABC):

    def __init__(self, iteration_limit: Optional[int] = None):
        self.current_iteration = 0
        self.iteration_limit = iteration_limit

    @abc.abstractmethod
    def generate(self) -> JobShopInstance:
        pass

    def __iter__(self) -> Iterator[JobShopInstance]:
        self.current_iteration = 0
        return self

    def __next__(self) -> JobShopInstance:
        if (
            self.iteration_limit is not None
            and self.current_iteration >= self.iteration_limit
        ):
            raise StopIteration
        self.current_iteration += 1
        return self.generate()
