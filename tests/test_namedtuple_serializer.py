import pytest
from typing import List, Tuple, Optional, Union, Dict, NamedTuple
from dataclasses import dataclass

from serializer import create_serializer
from serializer.exceptions import SerializerError


class User(NamedTuple):
    login: str
    password: str


def test_namedtuple_serializer_plain():
    named_tuple_serializer = create_serializer(User)

    user = User('root', '123')
    user_serialized = {
        'login': 'root',
        'password': '123'
    }

    assert named_tuple_serializer.serialize(user) == user_serialized
    assert named_tuple_serializer.deserialize(user_serialized) == user
