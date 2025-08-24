from __future__ import annotations
from enum import Enum, unique

ValueType = int | float | str | bool


@unique
class ActivationRecordType(Enum):
    PROGRAM = "PROGRAM"
    FUNCTION = "FUNCTION"
    PROCEDURE = "PROCEDURE"


class ActivationRecord(object):
    __slots__ = ("name", "type", "nesting_level", "members")

    def __init__(
        self, name: str, type: ActivationRecordType, nesting_level: int
    ) -> None:
        self.name: str = name
        self.type: ActivationRecordType = type
        self.nesting_level: int = nesting_level
        self.members: dict[str, ValueType] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', type={self.type.name}, nesting_level={self.nesting_level})"

    def __str__(self) -> str:
        lines: list[str] = [f"{self.nesting_level}: {self.type.name} {self.name}:"]
        lines.extend(f"\t{key}: {value}" for key, value in self.members.items())
        return "\n".join(lines)

    def __setitem__(self, key: str, value: ValueType) -> None:
        self.members[key] = value

    def __getitem__(self, key: str) -> ValueType:
        return self.members[key]

    def get(self, key: str) -> ValueType | None:
        return self.members.get(key)


class CallStack(object):
    __slots__ = ("_activation_records",)

    def __init__(self) -> None:
        self._activation_records: list[ActivationRecord] = []

    def push(self, record: ActivationRecord) -> None:
        self._activation_records.append(record)

    def pop(self) -> ActivationRecord:
        return self._activation_records.pop()

    def peek(self) -> ActivationRecord:
        return self._activation_records[-1]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "Call Stack:\n" + "\n".join(repr(r) for r in self._activation_records)
