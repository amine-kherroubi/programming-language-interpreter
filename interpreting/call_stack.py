from enum import Enum
from typing import Optional, Union

NumericType = Union[int, float, str, bool]


class ActivationRecordType(Enum):
    PROGRAM = "PROGRAM"
    FUNCTION = "FUNCTION"
    PROCEDURE = "PROCEDURE"


class ActivationRecord:
    __slots__ = ("name", "type", "nesting_level", "members")

    def __init__(
        self, name: str, type: ActivationRecordType, nesting_level: int
    ) -> None:
        self.name = name
        self.type = type
        self.nesting_level = nesting_level
        self.members: dict[str, NumericType] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', type={self.type.name}, nesting_level={self.nesting_level})"

    def __str__(self) -> str:
        lines = [f"{self.nesting_level}: {self.type.name} {self.name}:"]
        lines.extend(f"\t{key}: {value}" for key, value in self.members.items())
        return "\n".join(lines)

    def __setitem__(self, key: str, value: NumericType) -> None:
        self.members[key] = value

    def __getitem__(self, key: str) -> NumericType:
        return self.members[key]

    def get(self, key: str) -> Optional[NumericType]:
        return self.members.get(key)


class CallStack:
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
