import pytest
from typing import List, Tuple, Optional, Union, Dict, NamedTuple
from dataclasses import dataclass

from serializer import create_serializer
from serializer.exceptions import SerializerError


def test_union_serializer_plain():
    union_s = create_serializer(Union[str, int, float])

    assert union_s.serialize('1') == '1'
    assert union_s.deserialize('1') == '1'
    assert union_s.serialize(union_s.deserialize('1')) == '1'

    assert union_s.serialize(1) == 1
    assert union_s.deserialize(1) == 1
    assert union_s.serialize(union_s.deserialize(1)) == 1

    assert union_s.serialize(1.2) == 1.2
    assert union_s.deserialize(1.2) == 1.2
    assert union_s.serialize(union_s.deserialize(1.2)) == 1.2

    with pytest.raises(SerializerError):
        union_s.serialize([1, 2, 3])

    with pytest.raises(SerializerError):
        union_s.serialize({})

    # Optional[int] == Union[int, None]
    union_s_2 = create_serializer(Optional[str])

    assert union_s_2.serialize('1') == '1'
    assert union_s_2.deserialize('1') == '1'
    assert union_s_2.serialize(union_s_2.deserialize('1')) == '1'

    assert union_s_2.serialize(None) is None
    assert union_s_2.deserialize(None) is None
    assert union_s_2.serialize(union_s_2.deserialize(None)) is None


@dataclass
class User:
    login: str
    password: str


def test_union_serializer_complex():
    union_s = create_serializer(Union[User, List[Dict[int, int]]])

    assert union_s.serialize(User('root', '123')) == {'login': 'root', 'password': '123'}
    assert union_s.deserialize({'login': 'root', 'password': '123'}) == User('root', '123')
    assert union_s.serialize(union_s.deserialize({'login': 'root', 'password': '123'})) == \
           {'login': 'root', 'password': '123'}

    assert union_s.serialize([{1: 1}]) == [{1: 1}]
    assert union_s.deserialize([{1: 1}]) == [{1: 1}]
    assert union_s.serialize(union_s.deserialize([{1: 1}])) == [{1: 1}]
