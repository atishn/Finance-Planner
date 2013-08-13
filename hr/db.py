from sqlalchemy.types import SchemaType, TypeDecorator, Enum
from sqlalchemy.dialects.mysql import TINYINT

import re
from datetime import datetime
from hashlib import sha512
from uuid import uuid4

def db_utc_now(format='%Y-%m-%d %H:%M:%S'):
    return datetime.utcnow().strftime(format).decode()

def convert_db_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

def parse_datetime_string(s, format="%Y-%m-%d %H:%M:%S"):
    if isinstance(s, datetime):
        return s
    try:
        return datetime.strptime(s, format)
    except:
       return None

def random_key(length):
    return sha512(uuid4().hex).hexdigest()[0:length]

class IntEnumTypeMeta(type):
    def __init__(cls, classname, bases, dict_):
        values = dict_.get('values')
        if values:
            if isinstance(values, tuple):
                for v in values:
                    setattr(cls, v.upper(), v)
        return type.__init__(cls, classname, bases, dict_)

class IntEnumType(TypeDecorator):
    impl = TINYINT

    def __init__(self, enum, values):
        self.enum = enum
        self.values = values
        TypeDecorator.__init__(self)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return self.values.index(value) + 1

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.values[(value - 1)]

class IntEnum(object):
    __metaclass__ = IntEnumTypeMeta

    values = None

    @classmethod
    def db_type(cls):
        return IntEnumType(cls, cls.values)

    @classmethod
    def to_dict(cls):
        d = {}
        values = cls.values
        if values:
            if isinstance(values, tuple):
                for v in values:
                    d[v.upper()] = v
        return d

    @classmethod
    def from_string(cls, value):
        try:
            return cls.values.index(value)
        except KeyError:
            raise ValueError(
                "Invalid value for %r: %r" %
                (cls.__name__, value)
            )

# http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
class EnumSymbol(object):
    """Define a fixed symbol tied to a parent class."""

    def __init__(self, cls_, name, value, description):
        self.cls_ = cls_
        self.name = name
        self.value = value
        self.description = description

    def __reduce__(self):
        """Allow unpickling to return the symbol
        linked to the DeclEnum class."""
        return getattr, (self.cls_, self.name)

    def __iter__(self):
        return iter([self.value, self.description])

    def __repr__(self):
        return "<%s>" % self.name

class EnumMeta(type):
    """Generate new DeclEnum classes."""

    def __init__(cls, classname, bases, dict_):
        cls._reg = reg = cls._reg.copy()
        for k, v in dict_.items():
            if isinstance(v, tuple):
                sym = reg[v[0]] = EnumSymbol(cls, k, *v)
                setattr(cls, k, sym)
        return type.__init__(cls, classname, bases, dict_)

    def __iter__(cls):
        return iter(cls._reg.values())

    def __getitem__(cls, index):
        return list(cls.__iter__())[index]

    def __len__(cls):
        return len(list(cls.__iter__()))

class DeclEnumType(SchemaType, TypeDecorator):
    def __init__(self, enum):
        self.enum = enum
        self.impl = Enum(
                        *enum.values(),
                        name="ck%s" % re.sub(
                                    '([A-Z])',
                                    lambda m:"_" + m.group(1).lower(),
                                    enum.__name__)
                    )

    def _set_table(self, table, column):
        self.impl._set_table(table, column)

    def copy(self):
        return DeclEnumType(self.enum)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum.from_string(value.strip())

class DeclEnum(object):
    """Declarative enumeration."""

    __metaclass__ = EnumMeta
    _reg = {}

    @classmethod
    def db_type(cls):
        return DeclEnumType(cls)

    @classmethod
    def from_string(cls, value):
        try:
            return cls._reg[value]
        except KeyError:
            raise ValueError(
                "Invalid value for %r: %r" %
                (cls.__name__, value)
            )

    @classmethod
    def to_dict(cls):
        d = {}
        for v in cls._reg:
            enum = cls._reg[v]
            d[enum.name] = enum.value
        return d

    @classmethod
    def values(cls):
        return cls._reg.keys()
