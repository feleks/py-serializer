import pytest
from typing import Tuple
from dataclasses import dataclass

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


class SerializableClass1Error:
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

    a = SerializableClass1(1, '1')
    b = SerializableClass1(2, '2')

    a_s = serializable_class_s.serialize(a)
    b_s = serializable_class_s.serialize(b)
    with pytest.raises(SerializerError):
        serializable_class_error_s = create_serializer(SerializableClass1Error)

    assert a.a == a_s[0]
    assert a.b == a_s[1]
    assert b.a == b_s[0]
    assert b.b == b_s[1]

    a_d = serializable_class_s.deserialize(a_s)
    b_d = serializable_class_s.deserialize(b_s)

    assert a.a == a_d.a
    assert a.b == a_d.b
    assert b.a == b_d.a
    assert b.b == b_d.b


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

class TwoFactorAuth(SerializableClass):
    def __init__(self, secret_key: str, picture_url: str):
        self.secret_key = secret_key
        self.picture_url = picture_url

    def serialize(self) -> Tuple[str, str]:
        return self.secret_key, self.picture_url

    @staticmethod
    def deserialize(instance: Tuple[str, str]) -> 'TwoFactorAuth':
        return TwoFactorAuth(instance[0], instance[1])


@dataclass
class User:
    id: int
    login: str
    password: str
    two_factor_auth: TwoFactorAuth


def test_complex_class():
    user_serializer = create_serializer(User)

    user_serialized = {
        'id': 1,
        'login': 'feleks',
        'password': '228',
        'two_factor_auth': ('3DWR32GS', '9d2fa0ccf73d11e9b740784f439c7d4d')
    }

    user: User = user_serializer.deserialize(user_serialized)
    assert user.two_factor_auth.secret_key == '3DWR32GS'
    assert user.two_factor_auth.picture_url == '9d2fa0ccf73d11e9b740784f439c7d4d'
