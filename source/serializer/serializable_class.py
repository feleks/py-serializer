from typing import Any
from abc import ABC, abstractmethod


class SerializableClass(ABC):
    @abstractmethod
    def serialize(self) -> Any:
        pass

    @staticmethod
    @abstractmethod
    def deserialize(instance: Any) -> 'SerializableClass':
        pass
