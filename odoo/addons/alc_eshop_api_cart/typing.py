# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Protocol


class ByteReader(Protocol):
    """Protocol for a file-like object that can be read as bytes."""

    # pylint: disable=method-required-super
    def read(self, n: int | None = None) -> bytes:
        ...

    def seek(self, n: int) -> None:
        ...
