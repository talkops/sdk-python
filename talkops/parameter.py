import os
import re

class Parameter:
    ALLOWED_TYPES = [
        'text',
        'password',
        'textarea',
        'email',
        'search',
        'tel',
        'number',
        'url',
        'time',
        'date',
        'datetime-local',
        'select',
        'color',
    ]

    def __init__(self, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError('name must be a non-empty string.')
        if not re.match(r'^[A-Z0-9_]+$', name):
            raise ValueError('name expected uppercase letters, numbers, and underscores.')
        self._name = name
        self._description = None
        self._value = ''
        self._default_value = ''
        self._available_values = []
        self._possible_values = []
        self._optional = False
        self._type = 'text'

    @property
    def name(self):
        return self._name

    def set_optional(self, optional):
        if not isinstance(optional, bool):
            raise ValueError('optional must be a boolean.')
        self._optional = optional
        return self

    @property
    def is_optional(self):
        return self._optional

    def set_description(self, description):
        if not isinstance(description, str) or not description.strip():
            raise ValueError('description must be a non-empty string.')
        self._description = description
        return self

    def set_default_value(self, default_value):
        if not isinstance(default_value, str):
            raise ValueError('default_value must be a string.')
        self._default_value = default_value
        return self

    def set_type(self, type_):
        if type_ not in self.ALLOWED_TYPES:
            raise ValueError(f'type must be one of the following strings: {", ".join(self.ALLOWED_TYPES)}')
        self._type = type_
        return self

    @property
    def value(self):
        return os.environ.get(self._name) or self._value or self._default_value

    def set_value(self, value):
        if not isinstance(value, str):
            raise ValueError('value must be a string.')
        self._value = value
        return self

    @property
    def has_value(self):
        return self.value != ''

    def set_available_values(self, available_values):
        if not isinstance(available_values, list) or not available_values:
            raise ValueError('available_values must be a non-empty list.')
        if not all(isinstance(value, str) and value.strip() for value in available_values):
            raise ValueError('Each item in available_values must be a non-empty string.')
        self._available_values = available_values
        return self

    def set_possible_values(self, possible_values):
        if not isinstance(possible_values, list) or not possible_values:
            raise ValueError('possible_values must be a non-empty list.')
        if not all(isinstance(value, str) and value.strip() for value in possible_values):
            raise ValueError('Each item in possible_values must be a non-empty string.')
        self._possible_values = possible_values
        return self

    def to_json(self):
        return {
            'name': self._name,
            'description': self._description,
            'env': self._name in os.environ,
            'defaultValue': self._default_value,
            'availableValues': self._available_values,
            'possibleValues': self._possible_values,
            'optional': self._optional,
            'type': self._type,
        }
