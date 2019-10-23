import pytest
from typing import List, Tuple, Optional, Union, Dict, NamedTuple
from dataclasses import dataclass
from enum import IntEnum

from serializer import create_serializer
from serializer.exceptions import SerializerError


@dataclass
class User:
    id: Optional[int]
    login: str
    password: str
    banned: bool = False
    balance_usd: float = 0.0
    auth_cnt: int = 0
    birth_date: Optional[str] = None


def test_dataclass_serializer_plain():
    user_1 = User(
        0,
        'root',
        '123'
    )

    user_2 = User(
        None,
        'feleks',
        '228',
        banned=True,
        balance_usd=10.0,
        auth_cnt=322,
        birth_date='01.06.1996'
    )

    user_1_serialized = {
        'id': 0,
        'login': 'root',
        'password': '123',
        'banned': False,
        'balance_usd': 0.0,
        'auth_cnt': 0,
        'birth_date': None
    }

    user_2_serialized = {
        'id': None,
        'login': 'feleks',
        'password': '228',
        'banned': True,
        'balance_usd': 10.0,
        'auth_cnt': 322,
        'birth_date': '01.06.1996'
    }

    user_serializer = create_serializer(User)

    assert user_serializer.serialize(user_1) == user_1_serialized
    assert user_serializer.deserialize(user_1_serialized) == user_1

    assert user_serializer.serialize(user_2) == user_2_serialized
    assert user_serializer.deserialize(user_2_serialized) == user_2

    with pytest.raises(SerializerError):
        user_serializer.deserialize({
            'id': 0,
            'login': 'root',
            # Password is not Optional.
            'password': None,
            'banned': False,
            'balance_usd': 0.0,
            'auth_cnt': 0,
            'birth_date': None
        })

    with pytest.raises(SerializerError):
        user_serializer.deserialize({
            'id': 0,
            # Missing non-default field 'login'.
            'password': '123',
            'banned': False,
            'balance_usd': 0.0,
            'auth_cnt': 0,
            'birth_date': None
        })

    with pytest.raises(SerializerError):
        user_serializer.deserialize({
            # Missing id field (id is Optional (=nullable), but it has no default value).
            'login': 'root',
            'password': '123',
            'banned': False,
            'balance_usd': 0.0,
            'auth_cnt': 0,
            'birth_date': None
        })


class UserStorageStatus(IntEnum):
    outdated = 0
    synchronized = 1


@dataclass
class UserStorage:
    user_ids: List[int]
    users: Dict[int, User]
    status: UserStorageStatus


def test_dataclass_serializer_complex():
    user_storage_serializer = create_serializer(UserStorage)

    user_storage = UserStorage(
        user_ids=[0, 1],
        users={
            0: User(
                0,
                'root',
                '123'
            ),
            1: User(
                1,
                'feleks',
                '228',
                banned=True,
                balance_usd=10.0,
                auth_cnt=322,
                birth_date='01.06.1996'
            )
        },
        status=UserStorageStatus.synchronized
    )

    user_storage_serialized = {
        'user_ids': [0, 1],
        'users': {
            0: {
                'id': 0,
                'login': 'root',
                'password': '123',
                'banned': False,
                'balance_usd': 0.0,
                'auth_cnt': 0,
                'birth_date': None
            },
            1: {
                'id': 1,
                'login': 'feleks',
                'password': '228',
                'banned': True,
                'balance_usd': 10.0,
                'auth_cnt': 322,
                'birth_date': '01.06.1996',
            }
        },
        'status': 'synchronized'
    }

    assert user_storage_serializer.serialize(user_storage) == user_storage_serialized
    assert user_storage_serializer.deserialize(user_storage_serialized) == user_storage
