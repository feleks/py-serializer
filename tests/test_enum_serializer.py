import pytest
from typing import List, Tuple, Optional, Union, Dict, NamedTuple
from enum import Enum, IntEnum
from dataclasses import dataclass

from serializer import create_serializer
from serializer.exceptions import SerializerError


class UserRank(IntEnum):
    admin = 0
    user = 1
    chat_moderator = 2


class StrEnum(Enum):
    a = 'a'
    b = 'b'
    c = 'c'


def test_enum_serializer_plain():
    user_rank_s = create_serializer(UserRank)
    str_enum_s = create_serializer(StrEnum)

    assert user_rank_s.serialize(UserRank.admin) == 'admin'
    assert user_rank_s.serialize(UserRank.user) == 'user'
    assert user_rank_s.serialize(UserRank.chat_moderator) == 'chat_moderator'

    assert str_enum_s.serialize(StrEnum.a) == 'a'
    assert str_enum_s.serialize(StrEnum.b) == 'b'
    assert str_enum_s.serialize(StrEnum.c) == 'c'

    assert user_rank_s.deserialize('admin') is UserRank.admin
    assert user_rank_s.deserialize('user') is UserRank.user
    assert user_rank_s.deserialize('chat_moderator') is UserRank.chat_moderator

    assert str_enum_s.deserialize('a') is StrEnum.a
    assert str_enum_s.deserialize('b') is StrEnum.b
    assert str_enum_s.deserialize('c') is StrEnum.c


@dataclass
class User:
    login: str
    password: str
    rank: UserRank


def test_enum_serializer_complex():
    user_s = create_serializer(User)

    user = User('root', '123', UserRank.admin)
    user_serialized = {'login': 'root', 'password': '123', 'rank': 'admin'}

    assert user_s.serialize(user) == user_serialized
    assert user_s.deserialize(user_serialized) == user
