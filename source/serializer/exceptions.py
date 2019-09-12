from typing import Any, List


class SerializerError(Exception):
    pass


# Type errors

class SerializerTypeError(TypeError, SerializerError):
    def __init__(self, action: str, expected_types: List[Any], passed_type: Any, breadcrumbs: str):
        if len(expected_types) == 1:
            expected_types_str = 'expected type: {}'.format(expected_types[0])
        else:
            expected_types_str = 'expected types: {}'.format(expected_types)

        super().__init__(
            '{} validation error. {}: '
            '{}; '
            'got {}. '.format(action, breadcrumbs, expected_types_str, passed_type)
        )

        self.expected_types = expected_types
        self.passed_type = passed_type
        self.breadcrumbs = breadcrumbs


class SerializationTypeError(SerializerTypeError):
    def __init__(self, expected_types: List[Any], passed_type: Any, breadcrumbs: str):
        super().__init__('Serialization', expected_types, passed_type, breadcrumbs)


class DeserializationTypeError(SerializerTypeError):
    def __init__(self, expected_types: List[Any], passed_type: Any, breadcrumbs: str):
        super().__init__('Deserialization', expected_types, passed_type, breadcrumbs)


# Format errors


class SerializerFormatError(SerializerError):
    pass


class DeserializationFormatError(SerializerFormatError):
    pass


class SerializationFormatError(SerializerFormatError):
    pass


# Etc

class MissingSerializer(Exception):
    def __init__(self, typing: Any, breadcrumbs: str):
        super().__init__(
            '{}: serializer class for typing \'{}\' is not defined. '
            'see serializer/_serializer.py for details.'.format(breadcrumbs, typing)
        )

        self.typing = typing
        self.breadcrumbs = breadcrumbs
