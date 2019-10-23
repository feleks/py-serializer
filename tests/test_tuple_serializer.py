import pytest
from typing import List, Tuple, Optional, Union, Dict, NamedTuple
from dataclasses import dataclass

from serializer import create_serializer
from serializer.exceptions import SerializerError


def test_tuple_serializer_plain():
    tuple_s = create_serializer(Tuple[int, str, bool, float])

    assert tuple_s.serialize([1, '2', False, 1.1]) == [1, '2', False, 1.1]
    assert tuple_s.deserialize([1, '2', False, 1.1]) == (1, '2', False, 1.1)
    assert tuple_s.serialize(tuple_s.deserialize([1, '2', False, 1.1])) == [1, '2', False, 1.1]

    with pytest.raises(SerializerError):
        tuple_s.serialize([1, '2', False, 1])

    with pytest.raises(SerializerError):
        tuple_s.serialize([[1, True, False, 1.1]])


@dataclass
class User:
    login: str
    password: str


def test_tuple_serializer_complex():
    tuple_s = create_serializer(List[Tuple[User, Dict[str, str]]])

    serialized_tuple = [
        [
            {
                'login': 'root',
                'password': '228'
            },
            {
                'rank': 'admin'
            }
        ],
        [
            {
                'login': 'solo',
                'password': '322'
            },
            {
                'rank': 'user'
            }
        ]
    ]

    deserialized_tuple = tuple_s.deserialize(serialized_tuple)
    assert isinstance(deserialized_tuple[0][0], User)
    assert isinstance(deserialized_tuple[1][0], User)
    assert isinstance(deserialized_tuple[0][1], dict)
    assert isinstance(deserialized_tuple[1][1], dict)

    assert deserialized_tuple[0][0].login == 'root'
    assert deserialized_tuple[0][0].password == '228'
    assert deserialized_tuple[1][0].login == 'solo'
    assert deserialized_tuple[1][0].password == '322'

    assert deserialized_tuple[0][1]['rank'] == 'admin'
    assert deserialized_tuple[1][1]['rank'] == 'user'

    serialized_tuple_error_1 = [
        [
            {
                'login': 'root',
                'password': '228'
            },
            {
                'rank': 1
            }
        ]
    ]

    serialized_tuple_error_2 = [
        [
            {
                'login': 'root',
                'password': '228'
            },
            False
        ]
    ]

    with pytest.raises(SerializerError):
        tuple_s.deserialize(serialized_tuple_error_1)

    with pytest.raises(SerializerError):
        tuple_s.deserialize(serialized_tuple_error_2)



