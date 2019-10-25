import pytest
from typing import Tuple

from serializer import create_serializer, SerializableClass
from serializer.exceptions import SerializerError


class WrongClass:
    pass


def test_wrong_class():
    with pytest.raises(SerializerError):
        create_serializer(WrongClass)


# ----------------------------------------------------------------------------------------------------------------------


class SerializableClass1(SerializableClass):
    def __init__(self, a: int, b: str):
        self.a = a
        self.b = b

    def serialize(self) -> Tuple[int, str]:
        return [self.a, self.b]

    @staticmethod
    def deserialize(instance: Tuple[int, str]) -> 'SerializableClass1':
        return SerializableClass1(instance[0], instance[1])


class SerializableClass1Error(SerializableClass):
    def __init__(self, a: int, b: str):
        self.a = a
        self.b = b

    def serialize(self) -> Tuple[int, str]:
        return self.a, self.b

    @staticmethod
    def deserialize(instance: Tuple[int, str]) -> 'SerializableClass1':
        return SerializableClass1(instance[0], instance[1])


def test_simple_class():
    serializable_class_s = create_serializer(SerializableClass1)
    serializable_class_error_s = create_serializer(SerializableClass1Error)

    a = SerializableClass1(1, '1')
    b = SerializableClass1(2, '2')
    c = SerializableClass1Error(2, '2')

    a_s = serializable_class_s.serialize(a)
    b_s = serializable_class_s.serialize(b)
    with pytest.raises(SerializerError):
        serializable_class_error_s.serialize(c)

    assert a.a == a_s[0]
    assert a.b == a_s[1]
    assert b.a == b_s[0]
    assert b.b == b_s[1]

    a_d = serializable_class_s.deserialize(a_s)
    b_d = serializable_class_s.deserialize(b_s)
    c_d = serializable_class_error_s.deserialize(a_s)

    with pytest.raises(SerializerError):
        serializable_class_s.deserialize((1, '2'))

    assert a.a == a_d.a
    assert a.b == a_d.b
    assert b.a == b_d.a
    assert b.b == b_d.b
    assert c_d.a == a_d.a
    assert c_d.b == a_d.b


# ----------------------------------------------------------------------------------------------------------------------


class BaseClass(SerializableClass):
    def serialize(self) -> dict:
        return {
            'a': getattr(self, 'a', None)
        }


class InheritedClass(BaseClass):
    def __init__(self, a: int):
        self.a = a

    @staticmethod
    def deserialize(instance: dict) -> 'InheritedClass':
        return InheritedClass(instance['a'])


def test_inherited_class():
    serializable_class_s = create_serializer(InheritedClass)

    a = InheritedClass(1)

    a_s = serializable_class_s.serialize(a)

    assert a.a == a_s['a']

    a_d = serializable_class_s.deserialize(a_s)

    assert a.a == a_d.a


# ----------------------------------------------------------------------------------------------------------------------


# class AbstractClass(ABC, SerializableClass):
#     def __init__(self, a: int):
#         self.a = a
#
#     @abstractmethod
#     def serialize(self) -> Any:
#         pass
#
#     @staticmethod
#     @abstractmethod
#     def deserialize(instance: Any) -> 'AbstractClass':
#         pass
#
#
# class ImplementedClass(AbstractClass):
#     def serialize(self) -> str:
#         return str(self.a)
#
#     @staticmethod
#     def deserialize(instance: Any) -> 'ImplementedClass':
#         return ImplementedClass(int(instance))
#
#
# def test_abstract_class():
#     serializable_class_s = create_serializer(ImplementedClass)
#
#     a = ImplementedClass(1)
#
#     a_s = serializable_class_s.serialize(a)
#
#     assert str(a.a) == a_s
#
#     a_d = serializable_class_s.deserialize(a_s)
#
#     assert a.a == a_d.a
