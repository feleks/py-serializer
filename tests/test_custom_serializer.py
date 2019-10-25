import pytest
from datetime import datetime, timezone
from dateutil.parser import parse
from dataclasses import dataclass

from serializer import create_serializer, Serializer
from serializer.exceptions import SerializerError


@dataclass
class User:
    login: str
    password: str
    creation_date: datetime


def test_before_serializer_exist():
    with pytest.raises(SerializerError) as e:
        create_serializer(User)

    assert 'serializer class for typing' in str(e.value)
    assert 'datetime' in str(e.value)
    assert 'is not defined.' in str(e.value)


def test_after_serializer_defined():
    class DatetimeSerializer(Serializer):
        @staticmethod
        def test_typing(typing: datetime) -> bool:
            return typing is datetime

        def __init__(self, typing, prev_breadcrumbs: str = None):
            self._init_breadcrumbs('Datetime', prev_breadcrumbs)

        def _serialize(self, instance: datetime):
            return instance.replace(tzinfo=timezone.utc).isoformat()

        def _deserialize(self, instance: str) -> datetime:
            return parse(instance)

    user_serializer = create_serializer(User)

    user = User('feleks', '123', datetime.now().replace(tzinfo=timezone.utc))
    user_serialized = user_serializer.serialize(user)

    assert isinstance(user_serialized['creation_date'], str)

    user_deserialized: User = user_serializer.deserialize(user_serialized)

    assert isinstance(user_deserialized.creation_date, datetime)
    assert user == user_deserialized
    assert user is not user_deserialized
