import json
import pytest
from typing import List, Dict, Tuple, Union, Optional, NamedTuple
from enum import IntEnum
from dataclasses import dataclass
from serializer import create_serializer
from serializer.exceptions import SerializerError


class UserRank(IntEnum):
    user = 0
    admin = 1


@dataclass
class User:
    id: int
    login: str
    password: str
    rank: UserRank
    friend_ids: List[int]
    avatar_url: Optional[str] = None


def test_complex_example_user():
    user_serializer = create_serializer(User)

    user = User(1, 'feleks', '228', UserRank.user, [1, 2, 3])
    user_serialized = {
        'id': 1,
        'login': 'feleks',
        'password': '228',
        'friend_ids': [1, 2, 3],
        'avatar_url': None,
        'rank': 'user'
    }

    assert user_serializer.serialize(user) == user_serialized
    assert user_serializer.deserialize(user_serialized) == user
    assert json.loads(user_serializer.serialize_json(user)) == json.loads(json.dumps(user_serialized))

    user_serialized_faulty_1 = {
        # Id is now str instead if int
        'id': '1',
        'login': 'feleks',
        'password': '228',
        'avatar_url': None,
        'friend_ids': [1, 2, 3],
        'rank': 'user'
    }

    user_serialized_faulty_2 = {
        'id': 1,
        'login': 'feleks',
        'password': '228',
        'avatar_url': None,
        # Not all elements of list are int now
        'friend_ids': [1, 2, '3'],
        'rank': 'user'
    }

    user_serialized_faulty_3 = {
        'id': 1,
        'login': 'feleks',
        'password': '228',
        'avatar_url': None,
        'friend_ids': [1, 2, 3],
        # There is no such member in UserRank enum
        'rank': 'chat_moderator'
    }

    with pytest.raises(SerializerError) as e:
        user_serializer.deserialize(user_serialized_faulty_1)
    assert 'Validation error. ' \
           'dataclass.User[\'id\']->int: ' \
           'expected type: <class \'int\'>; got <class \'str\'>.' in str(e.value)

    with pytest.raises(SerializerError) as e:
        user_serializer.deserialize(user_serialized_faulty_2)
    assert 'Validation error. ' \
           'dataclass.User[\'friend_ids\']->List[]->int: ' \
           'expected type: <class \'int\'>; got <class \'str\'>.' in str(e.value)

    with pytest.raises(SerializerError) as e:
        user_serializer.deserialize(user_serialized_faulty_3)
    assert 'Invalid enum member \'chat_moderator\', allowed members: [\'user\', \'admin\'].' in str(e.value)


class UserAttribute(NamedTuple):
    name: str
    value: Union[int, float, str]


@dataclass
class UserStorage:
    users: Dict[int, User]
    user_location_coordinates: Dict[int, Tuple[float, float]]
    user_additional_attributes: Dict[int, List[UserAttribute]]

    def get_user(self, user_id: int) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise Exception('User not found.')
        return self.users[user_id]

    def get_user_by_login(self, login: str) -> User:
        for user in self.users.values():
            if user.login == login:
                return user
        else:
            raise Exception('User not found.')

    def get_user_attribute(self, user_id: int, name: str) -> Union[int, float, str]:
        user_attributes = self.user_additional_attributes.get(user_id)
        if user_attributes is None:
            raise Exception('No additional attributes for user.')
        for user_attribute in user_attributes:
            if user_attribute.name == name:
                return user_attribute.value
        else:
            raise Exception('Attribute not found.')

    def get_user_location_coordinates(self, user_id: int) -> Tuple[float, float]:
        coordinates = self.user_location_coordinates.get(user_id)
        if coordinates is None:
            raise Exception('No location for user.')
        return coordinates


def test_user_storage_example():
    user_storage_serializer = create_serializer(UserStorage)

    user_storage_serialized = {
        'users': {
            1: {
                'id': 1,
                'login': 'feleks',
                'password': '228',
                'friend_ids': [2, 3],
                'avatar_url': './assets/pepe.png',
                'rank': 'user'
            }
        },
        'user_location_coordinates': {
            1: (1.29485739, 23.232293)
        },
        'user_additional_attributes': {
            1: [
                {
                    'name': 'last_name',
                    'value': 'George'
                },
                {
                    'name': 'height_meters',
                    'value': 1.92
                },
                {
                    'name': 'weight_kilos',
                    'value': 110
                }
            ]
        }
    }

    user_storage: UserStorage = user_storage_serializer.deserialize(user_storage_serialized)

    user = user_storage.get_user_by_login('feleks')
    assert user.password == '228'

    assert user_storage.get_user_attribute(user.id, 'last_name') == 'George'
    assert user_storage.get_user_attribute(user.id, 'height_meters') == 1.92
    assert user_storage.get_user_attribute(user.id, 'weight_kilos') == 110

    assert user_storage.get_user_location_coordinates(user.id) == (1.29485739, 23.232293)
