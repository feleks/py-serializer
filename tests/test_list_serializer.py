import pytest
from typing import List, Tuple, Optional, Union, Dict, NamedTuple
from dataclasses import dataclass

from serializer import create_serializer
from serializer.exceptions import SerializerError


def test_list_serializer_plain():
    list_int_s = create_serializer(List[int])

    assert list_int_s.serialize([1, 2, 3]) == [1, 2, 3]
    assert list_int_s.deserialize([1, 2, 3]) == [1, 2, 3]
    # cause isinstance(True, int) == True! (but isinstance(1, bool) == False)
    assert list_int_s.deserialize([1, 2, 3, True]) == [1, 2, 3, 1]
    assert list_int_s.serialize(list_int_s.deserialize([1, 2, 3])) == [1, 2, 3]

    with pytest.raises(SerializerError):
        list_int_s.serialize([1, 2, 3, '4'])

    with pytest.raises(SerializerError):
        list_int_s.serialize([1, 2, 3, 1.1])


def test_list_serializer_complex():
    list_dict_s = create_serializer(List[Dict[str, float]])

    valid_serialized_list_1 = [
        {
            'a': 1.2,
            'b': 1.23
        },
        {
            'c': 5.5,
            'd': 3.33
        }
    ]

    invalid_serialized_dict_1 = [
        {
            'a': 1.1,
            'b': 5
        }
    ]
    invalid_serialized_dict_2 = [
        {
            'a': 1.1,
            'b': 5.1
        },
        33
    ]

    assert list_dict_s.deserialize(valid_serialized_list_1) == valid_serialized_list_1

    with pytest.raises(SerializerError):
        list_dict_s.deserialize(invalid_serialized_dict_1)

    with pytest.raises(SerializerError):
        list_dict_s.serialize(invalid_serialized_dict_2)
