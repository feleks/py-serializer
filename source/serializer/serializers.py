from inspect import signature, isclass
from typing import List, Tuple, Dict, Type, Any, Union, Optional, NamedTuple
from enum import Enum

from .serializer_manager import Serializer
from .utils import is_typing


class DictSerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        return is_typing(typing, Dict)

    def __init__(self, typing, prev_breadcrumbs: str = None):
        key_class = typing.__args__[0]
        value_class = typing.__args__[1]

        self._init_breadcrumbs('Dict[{}, {}]'.format(key_class.__name__, value_class.__name__), prev_breadcrumbs)

        self.key_formatter: Serializer = self._create_serializer(key_class, '(KEY)')
        self.value_formatter: Serializer = self._create_serializer(value_class, '(VALUE)')

    def _check_serialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, dict):
            return [dict]

    def _check_deserialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, dict):
            return [dict]

    def _serialize(self, instance: Any) -> Any:
        new_dict = dict()
        for dict_key in instance:
            key = self.key_formatter.serialize(dict_key)
            value = self.value_formatter.serialize(instance[dict_key])

            new_dict[key] = value

        return new_dict

    def _deserialize(self, instance: Any) -> Any:
        new_dict = dict()
        for dict_key in instance.keys():
            key = self.key_formatter.deserialize(dict_key)
            value = self.value_formatter.deserialize(instance[dict_key])

            new_dict[key] = value

        return new_dict


class ListSerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        return is_typing(typing, List)

    def __init__(self, typing, prev_breadcrumbs: str = None):
        list_class = typing.__args__[0]
        self._init_breadcrumbs('List[{}]'.format(list_class.__name__), prev_breadcrumbs)

        self.serializer: Serializer = self._create_serializer(list_class)

    def _check_serialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, list):
            return [list]

    def _check_deserialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, list):
            return [list]

    def _serialize(self, instance: Any) -> Any:
        new_list = list()
        for list_unit in instance:
            item = self.serializer.serialize(list_unit)
            new_list.append(item)

        return new_list

    def _deserialize(self, instance: Any) -> Any:
        new_list = list()
        for list_unit in instance:
            item = self.serializer.deserialize(list_unit)
            new_list.append(item)

        return new_list


class TupleSerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        return is_typing(typing, Tuple)

    def __init__(self, typing, prev_breadcrumbs: str = None):
        tuple_classes = typing.__args__

        breadcrumbs = 'Tuple[{}]'.format(', '.join([tuple_class.__name__ for tuple_class in tuple_classes]))
        self._init_breadcrumbs(breadcrumbs, prev_breadcrumbs)

        self.serializer_instances: List[Serializer] = list()
        i = 0
        for tuple_class in tuple_classes:
            self.serializer_instances.append(self._create_serializer(tuple_class, '[{}]'.format(i)))
            i += 1

    def _check_serialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not (isinstance(instance, list) or isinstance(instance, tuple)):
            return [list, tuple]

    def _check_deserialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not (isinstance(instance, list) or isinstance(instance, tuple)):
            return [list, tuple]

    def _check_serialization_format_validity(self, instance: Any) -> Optional[str]:
        if len(self.serializer_instances) != len(instance):
            return 'Expected input tuple instance with length {}, got {}.'.format(
                len(self.serializer_instances), len(instance)
            )

    def _check_deserialization_format_validity(self, instance: Any) -> Optional[str]:
        if len(self.serializer_instances) != len(instance):
            return 'Expected input tuple instance with length {}, got {}.'.format(
                len(self.serializer_instances), len(instance)
            )

    def _serialize(self, instance: Any) -> Any:
        new_list = list()
        i = 0
        for list_unit in instance:
            item = self.serializer_instances[i].serialize(list_unit)
            new_list.append(item)
            i += 1

        return tuple(new_list)

    def _deserialize(self, instance: Any) -> Any:
        new_list = list()
        i = 0
        for list_unit in instance:
            item = self.serializer_instances[i].deserialize(list_unit)
            new_list.append(item)
            i += 1

        return tuple(new_list)


class UnionSerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        return is_typing(typing, Union)

    def __init__(self, typing, prev_breadcrumbs: str = None):
        union_classes = typing.__args__

        breadcrumbs = 'Union[{}]'.format(', '.join([union_class.__name__ for union_class in union_classes]))
        self._init_breadcrumbs(breadcrumbs, prev_breadcrumbs)

        i = 0
        self.serializer_instances: List[Serializer] = list()
        for union_class in union_classes:
            self.serializer_instances.append(self._create_serializer(union_class, '[{}]'.format(i)))
            i += 1

    def _check_serialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        final_available_types = set()

        for serializer_instance in self.serializer_instances:
            available_types = serializer_instance._check_serialization_type_validity(instance)

            if available_types is None:
                return None
            else:
                for available_type in available_types:
                    final_available_types.add(available_type)
        else:
            return list(final_available_types)

    def _check_deserialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        final_available_types = set()

        for serializer_instance in self.serializer_instances:
            available_types = serializer_instance._check_deserialization_type_validity(instance)

            if available_types is None:
                return None
            else:
                for available_type in available_types:
                    final_available_types.add(available_type)
        else:
            return list(final_available_types)

    def _deserialize(self, instance: Any):
        for serializer_instance in self.serializer_instances:
            available_types = serializer_instance._check_deserialization_type_validity(instance)

            if available_types is None:
                return serializer_instance.deserialize(instance)

    def _serialize(self, instance: Any):
        for serializer_instance in self.serializer_instances:
            available_types = serializer_instance._check_deserialization_type_validity(instance)

            if available_types is None:
                return serializer_instance.serialize(instance)


class AnySerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        return typing is Any

    def __init__(self, typing: Any, prev_breadcrumbs: str = None):
        self._init_breadcrumbs('Any', prev_breadcrumbs)

    def _deserialize(self, instance):
        return instance

    def _serialize(self, instance):
        return instance


class EnumSerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        return isclass(typing) and issubclass(typing, Enum)

    def __init__(self, typing: Any, prev_breadcrumbs: str = None):
        self._init_breadcrumbs('Enum[{}]'.format(typing.__name__), prev_breadcrumbs)

        self.enum: Type[Enum] = typing

    def _check_serialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, self.enum):
            return [self.enum]

    def _check_deserialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, str):
            return [str]

    def _check_deserialization_format_validity(self, instance: Any) -> Optional[str]:
        if instance not in self.enum.__members__:
            return 'invalid enum member \'{}\', allowed members: {}.'.format(
                instance,
                list(self.enum.__members__)
            )

    def _serialize(self, instance: Any) -> Any:
        return instance.name

    def _deserialize(self, instance: Any) -> Any:
        return self.enum[instance]


class DataclassSerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        return hasattr(typing, '__dataclass_fields__')

    def __init__(self, typing: Any, prev_breadcrumbs: str = None):
        self._init_breadcrumbs('DC[{}]'.format(typing.__name__), prev_breadcrumbs)

        formatter_instances = dict()
        keys = list()
        keys_with_default = set()
        dataclass_signature = signature(typing)
        parameters = dataclass_signature.parameters
        for key in parameters.keys():
            keys.append(key)
            parameter = parameters[key]
            parameter_annotation = parameter.annotation

            if parameter.default is not parameter.empty:
                keys_with_default.add(key)

                if parameter.default is None:
                    parameter_annotation = Optional[parameter.annotation]

            formatter_instances[key] = self._create_serializer(parameter_annotation, '[{}]'.format(key))

        self.keys = keys
        self.keys_with_default = keys_with_default
        self.formatter_instances = formatter_instances
        self.dataclass = typing

    def _check_serialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, self.dataclass):
            return [self.dataclass]

    def _check_deserialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, dict):
            return [dict]

    def _check_deserialization_format_validity(self, instance: Any) -> Optional[str]:
        for key in self.keys:
            if key not in instance:
                if key not in self.keys_with_default:
                    return 'missing required key \'{key}\''.format(
                        breadcrumbs=self.breadcrumbs,
                        key=key
                    )

    def _serialize(self, instance: Any) -> Any:
        final_dict = dict()
        for key in self.keys:
            formatter_instance = self.formatter_instances[key]
            final_dict[key] = formatter_instance.serialize(getattr(instance, key))

        return final_dict

    def _deserialize(self, instance: Any) -> Any:
        final_dict = dict()
        for key in self.keys:
            formatter_instance = self.formatter_instances[key]
            final_dict[key] = formatter_instance.deserialize(instance[key])

        return self.dataclass(**final_dict)


class NamedTupleSerializer(Serializer):
    @staticmethod
    def test_typing(typing: Any) -> bool:
        return isclass(typing) and (len(typing.__bases__) == 1) and (typing.__bases__[0] == tuple)

    def __init__(self, typing: Any, prev_breadcrumbs: str = None):
        self._init_breadcrumbs('NT[{}]'.format(typing.__name__), prev_breadcrumbs)

        formatter_instances = dict()
        keys = list()
        keys_with_default = set()
        named_tuple_signature = signature(typing)
        parameters = named_tuple_signature.parameters
        for key in parameters.keys():
            keys.append(key)
            parameter = parameters[key]
            parameter_annotation = parameter.annotation

            if parameter.default is not parameter.empty:
                keys_with_default.add(key)

                if parameter.default is None:
                    parameter_annotation = Optional[parameter.annotation]

            formatter_instances[key] = self._create_serializer(parameter_annotation, '[{}]'.format(key))

        self.keys = keys
        self.keys_with_default = keys_with_default
        self.formatter_instances = formatter_instances
        self.named_tuple = typing

    def _check_serialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, self.named_tuple):
            return [self.named_tuple]

    def _check_deserialization_type_validity(self, instance: Any) -> Optional[List[Any]]:
        if not isinstance(instance, dict):
            return [dict]

    def _check_deserialization_format_validity(self, instance: Any) -> Optional[str]:
        for key in self.keys:
            if key not in instance:
                if key not in self.keys_with_default:
                    return 'missing required key \'{key}\''.format(
                        breadcrumbs=self.breadcrumbs,
                        key=key
                    )

    def _serialize(self, instance: Any) -> Any:
        final_dict = dict()
        for key in self.keys:
            formatter_instance = self.formatter_instances[key]
            final_dict[key] = formatter_instance.serialize(getattr(instance, key))

        return final_dict

    def _deserialize(self, instance: Any) -> Any:
        final_dict = dict()
        for key in self.keys:
            formatter_instance = self.formatter_instances[key]
            final_dict[key] = formatter_instance.deserialize(instance[key])

        return self.named_tuple(**final_dict)
