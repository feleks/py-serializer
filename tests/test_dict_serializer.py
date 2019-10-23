import pytest
from typing import List, Tuple, Optional, Union, Dict, NamedTuple
from dataclasses import dataclass

from serializer import create_serializer
from serializer.exceptions import SerializerError


def test_dict_serializer_plain():
    dict_int_str_s = create_serializer(Dict[int, str])

    assert dict_int_str_s.serialize({1: '3', 2: '4'}) == {1: '3', 2: '4'}
    assert dict_int_str_s.deserialize({1: '3', 2: '4'}) == {1: '3', 2: '4'}
    assert dict_int_str_s.serialize(dict_int_str_s.deserialize({1: '3', 2: '4'})) == {1: '3', 2: '4'}

    with pytest.raises(SerializerError):
        dict_int_str_s.serialize({1: False})

    with pytest.raises(SerializerError):
        dict_int_str_s.serialize({'1': '3333'})


def test_dict_serializer_complex():
    dict_tuple_list_s = create_serializer(Dict[Tuple[int, int], Tuple[str]])

    valid_serialized_dict_1 = {
        (1, 2): ['1'],
        (2, 1): ['3'],
        (0, 0): ['2']
    }

    valid_serialized_dict_2 = {
        (1, 2): ('1',),
        (2, 1): ('3',),
        (0, 0): ('2',)
    }

    assert dict_tuple_list_s.deserialize(valid_serialized_dict_1) == \
           dict_tuple_list_s.deserialize(valid_serialized_dict_2)
