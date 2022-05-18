"""This module contains the main classes used in binread."""

from abc import ABC, abstractmethod
from struct import unpack
from typing import Any, Callable, Dict, Tuple, Union, Optional
import sys


try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


ByteOrder = Literal["little", "big", "native"]
"""Specifies the endiannes. `native` equals `sys.byteorder`."""


class NotEnoughBytes(Exception):
    def __init__(self, msg: str = "not enough bytes") -> None:
        super().__init__(msg)


class FieldType(ABC):
    """Abstract base class of all field types. Can be used to create a custom field type.

    Args:
       byteorder: specifies the endiannes of this type.
       to: specifies a callable to transform the extracted data.
    """

    def __init__(
        self,
        byteorder: Optional[ByteOrder] = None,
        to: Optional[Callable] = None,
    ):
        self._byteorder: Optional[ByteOrder] = byteorder
        self._default_byteorder: ByteOrder = "native"
        self.to = to

    @abstractmethod
    def extract(self, data: bytes, fields: Dict[str, Any]) -> Tuple[Any, int]:
        """Extracts the required bytes to construct this field.

        Args:
            data: The buffer to read.
            fields: Any previous read fields used as context.

        Returns:
            (Any, int): The field value that is constructed and the bytes read.

        Raises:
            NotEnoughBytes: If not enough bytes are provided to construct this field.

        """
        pass

    def read_field(self, data: bytes, fields: Dict[str, Any]) -> Tuple[Any, int]:
        value, size = self.extract(data, fields)

        if self.to:
            value = self.to(value)

        return value, size

    def byteorder(self) -> Literal["little", "big"]:
        if self._byteorder:
            byteorder = self._byteorder
        else:
            byteorder = self._default_byteorder

        if byteorder == "little" or byteorder == "big":
            return byteorder
        else:
            return sys.byteorder


class Integer(FieldType):
    def __init__(self, size: int, signed: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signed = signed
        self._size = size

    def extract(self, data: bytes, fields: Dict[str, Any]):
        if self._size > len(data):
            raise NotEnoughBytes()

        return (
            int.from_bytes(data[: self._size], self.byteorder(), signed=self.signed),
            self._size,
        )


class Float(FieldType):
    def __init__(self, size: Literal[2, 4, 8], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._size = size

    def extract(self, data: bytes, fields: Dict[str, Any]) -> Tuple[Any, int]:
        if self._size > len(data):
            raise NotEnoughBytes()

        byteorder = self.byteorder()
        if byteorder == "little":
            char = "<"
        else:
            char = ">"

        if self._size == 2:
            char += "e"
        elif self._size == 4:
            char += "f"
        elif self._size == 8:
            char += "d"
        else:
            raise Exception("invalid float size, must be either 2, 4 or 8")

        return *unpack(char, data[: self._size]), self._size


class Format(FieldType):
    def __init__(self, fields: Dict[str, Union[FieldType, type]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields: dict[str, FieldType] = {}

        if self._byteorder:
            byteorder = self._byteorder
        else:
            byteorder = self._default_byteorder

        for name, field in fields.items():
            if isinstance(field, FieldType):
                field._default_byteorder = byteorder
                self.fields[name] = field
            elif issubclass(field, FieldType) and field != FieldType:
                field_instance = field()  # type: ignore
                field_instance._default_byteorder = byteorder
                self.fields[name] = field_instance

    def extract(self, data: bytes, fields: Dict[str, Any]) -> Tuple[Any, int]:
        value, bytes_read = self.read(data, allow_leftover=True, return_bytes=True)
        return value, bytes_read  # type: ignore

    def read(
        self, data: bytes, allow_leftover: bool = False, return_bytes: bool = False
    ) -> Dict[str, Any]:
        result = {}
        total = 0
        for name, field in self.fields.items():
            result[name], bytes_read = field.read_field(data, result)
            data = data[bytes_read:]
            total += bytes_read

        if len(data) != 0 and not allow_leftover:
            raise Exception("left over bytes")

        if return_bytes:
            return result, total  # type: ignore
        else:
            return result
