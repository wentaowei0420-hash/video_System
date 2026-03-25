import json
from enum import Enum
from pathlib import Path


class ConfigValidator:
    def validate(self, value):
        return True

    def correct(self, value):
        return value


class BoolValidator(ConfigValidator):
    def validate(self, value):
        return isinstance(value, bool)

    def correct(self, value):
        return bool(value)


class FolderValidator(ConfigValidator):
    def validate(self, value):
        return Path(value).exists() and Path(value).is_dir()


class RangeValidator(ConfigValidator):
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value):
        try:
            number = int(value)
        except Exception:
            return False
        return self.minimum <= number <= self.maximum

    def correct(self, value):
        try:
            number = int(value)
        except Exception:
            number = self.minimum
        return max(self.minimum, min(self.maximum, number))


class OptionsValidator(ConfigValidator):
    def __init__(self, options):
        self.options = options

    def validate(self, value):
        if isinstance(self.options, type) and issubclass(self.options, Enum):
            return isinstance(value, self.options)
        return value in self.options


class EnumSerializer:
    def __init__(self, enum_type):
        self.enum_type = enum_type

    def serialize(self, value):
        if isinstance(value, self.enum_type):
            return value.value
        return value

    def deserialize(self, value):
        if isinstance(value, self.enum_type):
            return value
        for member in self.enum_type:
            if value == member.value or value == member.name:
                return member
        return next(iter(self.enum_type))


class ConfigItem:
    def __init__(self, group, name, default, validator=None):
        self.group = group
        self.name = name
        self.default = default
        self.validator = validator or ConfigValidator()
        self.serializer = None

    @property
    def key(self):
        return f"{self.group}.{self.name}"

    def serialize(self, value):
        if self.serializer is not None:
            return self.serializer.serialize(value)
        return value

    def deserialize(self, value):
        if self.serializer is not None:
            return self.serializer.deserialize(value)
        return value


class OptionsConfigItem(ConfigItem):
    def __init__(self, group, name, default, validator=None, serializer=None):
        super().__init__(group, name, default, validator)
        self.serializer = serializer


class RangeConfigItem(ConfigItem):
    pass


class QConfig:
    def __init__(self):
        self.file = None
        self._values = {}
        for _, item in self._iter_items():
            self._values[item.key] = item.default

    @classmethod
    def _iter_items(cls):
        seen = set()
        for klass in reversed(cls.mro()):
            for name, value in klass.__dict__.items():
                if isinstance(value, ConfigItem) and name not in seen:
                    seen.add(name)
                    yield name, value

    def get(self, item):
        return self._values.get(item.key, item.default)

    def set(self, item, value):
        value = item.deserialize(value)
        if not item.validator.validate(value):
            value = item.validator.correct(value)
        self._values[item.key] = value
        return value

    def save(self):
        if not self.file:
            return
        payload = {}
        for _, item in self._iter_items():
            payload.setdefault(item.group, {})[item.name] = item.serialize(self.get(item))
        target = Path(self.file)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=4), encoding="utf-8")


class _QConfigLoader:
    def load(self, file_path, config):
        path = Path(file_path)
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        for _, item in config._iter_items():
            raw_value = data.get(item.group, {}).get(item.name, item.default)
            config.set(item, raw_value)


qconfig = _QConfigLoader()
