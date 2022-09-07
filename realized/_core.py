from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Self
from zoneinfo import ZoneInfo

import orjson
from pydantic import BaseConfig, BaseModel


@dataclass(slots=True, frozen=True, order=True)
class Model:
    @classmethod
    def parse(cls, v: str) -> Self:
        raise NotImplementedError()

    def __post_init__(self):
        pass

    def str(self) -> str:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.str()

    def __str__(self) -> str:
        return self.str()


ORJSON_OPTS = (
    orjson.OPT_UTC_Z
    | orjson.OPT_SERIALIZE_NUMPY
    | orjson.OPT_STRICT_INTEGER  # 53-bit ints for JavaScript compat
    | orjson.OPT_NON_STR_KEYS
)


class Config(BaseConfig):
    @classmethod
    def json_loads(cls, v):
        return orjson.loads(v).encode("utf8")

    @classmethod
    def json_dumps(cls, v, *, options: int):
        return orjson.dumps(v, ORJSON_OPTS | options).decode("utf8")


dt = datetime.now().astimezone().astimezone(timezone.utc)
print(orjson.dumps(dt, option=ORJSON_OPTS).decode("utf8"))
