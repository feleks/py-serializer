import json
from typing import List, Dict, Type, Any, Optional
from abc import ABC, abstractmethod

from .exceptions import (
    SerializationTypeError,
    DeserializationTypeError,
    SerializationFormatError,
    DeserializationFormatError,
    MissingSerializer
)


class _SerializersManager:
    def __init__(self):
        self.__serializers: List[Type['Serializer']] = list()

    def register_serializer(self, serializer_class: Type['Serializer']):
        self.__serializers.append(serializer_class)

    def create_serializer(self, typing: Any, breadcrumbs: str) -> 'Serializer':
        serializer = None

        for _serializer in reversed(self.__serializers):
            if _serializer.test_typing(typing):
                serializer = _serializer(typing, breadcrumbs)

        if BuiltinTypesSerializer.test_typing(typing):
            serializer = BuiltinTypesSerializer(typing, breadcrumbs)

        if serializer is None:
            raise MissingSerializer(typing, breadcrumbs)

        return serializer


_serializers_manager = _SerializersManager()


def create_serializer(typing: Any) -> 'Serializer':
    return _serializers_manager.create_serializer(typing, '')


class Serializer(ABC):
    breadcrumbs: str = ''

    @staticmethod
    @abstractmethod
    def test_typing(typing: Any) -> bool:
        pass

    @classmethod
    def __init_subclass__(cls):
        _serializers_manager.register_serializer(cls)

    def _check_serialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        return None

    def _check_deserialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        return None

    def _check_serialization_format_validity(self, instance: Any) -> Optional[str]:
        return None

    def _check_deserialization_format_validity(self, instance: Any) -> Optional[str]:
        return None

    @abstractmethod
    def _serialize(self, instance: Any) -> Any:
        pass

    @abstractmethod
    def _deserialize(self, instance: Any) -> Any:
        pass

    def _init_breadcrumbs(self, personal_breadcrumbs: str, prev_breadcrumbs: str = None):
        if prev_breadcrumbs:
            self.breadcrumbs = '{}->{}'.format(prev_breadcrumbs, personal_breadcrumbs)
        else:
            self.breadcrumbs = personal_breadcrumbs

    def _create_serializer(self, typing: Any, additional_breadcrumbs: str = '') -> 'Serializer':
        breadcrumbs = self.breadcrumbs + additional_breadcrumbs

        return _serializers_manager.create_serializer(typing, breadcrumbs)

    def serialize(self, instance: Any) -> Any:
        available_types = self._check_serialization_type_validity(instance)
        if available_types is not None:
            raise SerializationTypeError(available_types, type(instance), self.breadcrumbs)

        format_error = self._check_serialization_format_validity(instance)
        if format_error is not None:
            raise SerializationFormatError(format_error)

        return self._serialize(instance)

    def deserialize(self, instance: Any) -> Any:
        available_types = self._check_deserialization_type_validity(instance)
        if available_types is not None:
            raise DeserializationTypeError(available_types, type(instance), self.breadcrumbs)

        format_error = self._check_deserialization_format_validity(instance)
        if format_error:
            raise DeserializationFormatError(format_error)

        return self._deserialize(instance)

    def serialize_json(self, instance: Any) -> str:
        return json.dumps(self.serialize(instance))

    def deserialize_json(self, json_string: str) -> Any:
        return self.deserialize(json.loads(json_string))


class BuiltinTypesSerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        is_primitive = (typing is int) or \
                       (typing is str) or \
                       (typing is float) or \
                       (typing is bool) or \
                       (typing is None) or \
                       (typing is type(None))
        is_collection = (typing is dict) or \
                        (typing is list) or \
                        (typing is tuple)

        return is_primitive or is_collection

    def __init__(self, typing: Any, prev_breadcrumbs: str = None):
        if typing is None:
            self.type = type(None)
            self._init_breadcrumbs('None', prev_breadcrumbs)
        else:
            self.type = typing
            self._init_breadcrumbs(typing.__name__, prev_breadcrumbs)

    def _check_serialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, self.type):
            return [self.type]

    def _check_deserialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, self.type):
            return [self.type]

    def _serialize(self, instance: Any) -> Any:
        return instance

    def _deserialize(self, instance: Any) -> Any:
        return instance
