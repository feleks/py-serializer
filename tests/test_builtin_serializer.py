import pytest

from serializer import create_serializer
from serializer.exceptions import SerializerError


def test_int_serializer():
    int_s = create_serializer(int)

    assert int_s.serialize(1) == 1
    assert int_s.deserialize(1) == 1
    assert int_s.serialize(int_s.deserialize(1)) == 1

    with pytest.raises(SerializerError):
        int_s.serialize('q')

    with pytest.raises(SerializerError):
        int_s.serialize(1.1)

    with pytest.raises(SerializerError):
        int_s.serialize([])

    with pytest.raises(SerializerError):
        int_s.deserialize('q')


def test_float_serializer():
    float_s = create_serializer(float)

    assert float_s.serialize(1.1) == 1.1
    assert float_s.deserialize(1.1) == 1.1
    assert float_s.serialize(float_s.deserialize(1.1)) == 1.1

    with pytest.raises(SerializerError):
        float_s.serialize(1)

    with pytest.raises(SerializerError):
        float_s.deserialize(1)


def test_str_serializer():
    str_s = create_serializer(str)

    assert str_s.serialize('hello') == 'hello'
    assert str_s.deserialize('hello') == 'hello'
    assert str_s.serialize(str_s.deserialize('hello')) == 'hello'

    with pytest.raises(SerializerError):
        str_s.serialize(1)

    with pytest.raises(SerializerError):
        str_s.deserialize(1)


def test_dict_serializer():
    dict_s = create_serializer(dict)

    assert dict_s.serialize({'a': {'a': 3}}) == {'a': {'a': 3}}
    assert dict_s.deserialize({'a': {'a': 3}}) == {'a': {'a': 3}}
    assert dict_s.serialize(dict_s.deserialize({'a': {'a': 3}})) == {'a': {'a': 3}}

    with pytest.raises(SerializerError):
        dict_s.serialize([])

    with pytest.raises(SerializerError):
        dict_s.deserialize([])


def test_list_serializer():
    list_s = create_serializer(list)

    assert list_s.serialize([1, 2, 3, 'w']) == [1, 2, 3, 'w']
    assert list_s.deserialize([1, 2, 3, 'w']) == [1, 2, 3, 'w']
    assert list_s.serialize(list_s.deserialize([1, 2, 3, 'w'])) == [1, 2, 3, 'w']

    with pytest.raises(SerializerError):
        list_s.serialize({})

    with pytest.raises(SerializerError):
        list_s.deserialize({1, 2, 3})


def test_tuple_serializer():
    tuple_s = create_serializer(tuple)

    assert tuple_s.serialize((1, 2, 3, 'w')) == (1, 2, 3, 'w')
    assert tuple_s.deserialize((1, 2, 3, 'w')) == (1, 2, 3, 'w')
    assert tuple_s.serialize(tuple_s.deserialize((1, 2, 3, 'w'))) == (1, 2, 3, 'w')

    with pytest.raises(SerializerError):
        tuple_s.serialize([1, 2, 3, 4])

    with pytest.raises(SerializerError):
        tuple_s.deserialize({})


def test_none_serializer():
    none_s = create_serializer(None)
    none_t_s = create_serializer(type(None))

    assert none_s.serialize(None) is None
    assert none_s.deserialize(None) is None
    assert none_s.serialize(none_s.deserialize(None)) is None

    assert none_t_s.serialize(None) is None
    assert none_t_s.deserialize(None) is None
    assert none_t_s.serialize(none_t_s.deserialize(None)) is None

    with pytest.raises(SerializerError):
        none_s.serialize(True)

    with pytest.raises(SerializerError):
        none_s.deserialize(35)

