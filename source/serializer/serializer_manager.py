import json
from typing import List, Type, Any
from abc import ABC, abstractmethod
from inspect import isclass, isfunction

from .serializable_class import SerializableClass
from .exceptions import SerializerError


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
            raise SerializerError(
                '{}: serializer class for typing \'{}\' is not defined. You can write one. '
                'See serializer/serializers.py for details.'.format(breadcrumbs, typing)
            )

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

    def _create_standard_type_error(self, expected_types: List[Any], instance: Any) -> SerializerError:
        if len(expected_types) == 1:
            expected_types_str = 'expected type: {}'.format(expected_types[0])
        else:
            expected_types_str = 'expected types: {}'.format(expected_types)

        return SerializerError(
            'Validation error. {}: '
            '{}; '
            'got {}. '.format(self.breadcrumbs, expected_types_str, type(instance))
        )

    def serialize(self, instance: Any) -> Any:
        return self._serialize(instance)

    def deserialize(self, instance: Any) -> Any:
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

    def _serialize(self, instance: Any) -> Any:
        if not isinstance(instance, self.type):
            raise self._create_standard_type_error([self.type], instance)

        return instance

    def _deserialize(self, instance: Any) -> Any:
        if not isinstance(instance, self.type):
            raise self._create_standard_type_error([self.type], instance)

        return instance


class SerializableClassSerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        return isclass(typing) and issubclass(typing, SerializableClass)
        # return (
        #     isclass(typing) and
        #     hasattr(typing, 'serialize') and
        #     hasattr(typing, 'deserialize') and
        #     isfunction(getattr(typing, 'serialize')) and
        #     isfunction(getattr(typing, 'deserialize'))
        # )

    def __init__(self, typing: Any, prev_breadcrumbs: str = None):
        self._init_breadcrumbs('serializable_class.{}'.format(typing.__name__), prev_breadcrumbs)

        self.type = typing

    @staticmethod
    def __ensure_serialization_valid(instance: Any):
        instance_type = type(instance)
        is_primitive = (instance_type is int) or \
                       (instance_type is str) or \
                       (instance_type is float) or \
                       (instance_type is bool) or \
                       (instance_type is None) or \
                       (instance_type is type(None))

        is_collection = (instance_type is dict) or \
                        (instance_type is list) or \
                        (instance_type is tuple)

        if (not is_collection) and (not is_primitive):
            raise SerializerError('Only primitive json serializable types can be result of '
                                  'serialize and arg of deserialize for SerializableClasses.')

        return instance

    def _serialize(self, instance: Any) -> Any:
        if not isinstance(instance, self.type):
            raise self._create_standard_type_error([self.type], instance)

        return self.__ensure_serialization_valid(instance.serialize())

    def _deserialize(self, instance: Any) -> Any:
        return self.type.deserialize(self.__ensure_serialization_valid(instance))
