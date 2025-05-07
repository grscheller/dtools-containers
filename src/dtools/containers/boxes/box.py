# Copyright 2023-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""### dtools.containers.boxes.box

Stateful container holding at most one item.
"""

from __future__ import annotations

__all__ = ['Box']

from collections.abc import Callable, Iterator
from typing import cast, Final, Never, overload, TypeVar
from dtools.fp.singletons import Sentinel


D = TypeVar('D')


class Box[D]:
    """Container holding at most one item

    - where `Box(item)` contains at most one item of type `~D`
    - `Box()` semantically represents an empty container
    - mutable semantics, map & bind modify the current instance
      - with one exception can store any item of any type
        - trying to store `Sentinel('Box'): ~D` results in a Box()
    - use stateful methods `put` and `pop` to mutate the container
    - use functional methods `map` and `bind` to create boxes of other types

    """

    __slots__ = ('_item',)
    __match_args__ = ('_item',)

    U = TypeVar('U')

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, value: D) -> None: ...

    def __init__(self, value: D | Sentinel = Sentinel('Box')) -> None:
        self._item: D | Sentinel = value

    def __bool__(self) -> bool:
        return self._item is not Sentinel('Box')

    def __iter__(self) -> Iterator[D]:
        if self:
            yield cast(D, self._item)

    def __repr__(self) -> str:
        if self:
            return 'Box(' + repr(self._item) + ')'
        return 'Box()'

    def __len__(self) -> int:
        return 1 if self else 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self._item is other._item:
            return True
        if self._item == other._item:
            return True
        return False

    @overload
    def get(self) -> D | Never: ...
    @overload
    def get(self, alt: D) -> D: ...
    @overload
    def get(self, alt: Sentinel) -> D | Never: ...

    def get(self, alt: D | Sentinel = Sentinel('Box')) -> D | Never:
        """Return the contained value if it exists, otherwise an alternate value.

        - alternate value must be of type `~D`
        - raises `ValueError` if an alternate value is not provided but needed

        """
        _sentinel: Final[Sentinel] = Sentinel('Box')
        if self._item is not _sentinel:
            return cast(D, self._item)
        if alt is _sentinel:
            msg = 'Box: get from empty Box with no alt return value provided'
            raise ValueError(msg)
        return cast(D, alt)

    def put(self, item: D) -> None:
        """Put a value in the Box if empty, if not empty do nothing.

        - raises `ValueError` if box is not empty

        """
        if self._item is Sentinel('Box'):
            self._item = item
        else:
            msg = 'Box: Trying to put an item in an empty Box'
            raise ValueError(msg)

    def pop(self) -> D | Never:
        """Pop the value if the Box is not empty.

        - raises `ValueError` if box is empty

        """
        _sentinel: Final[Sentinel] = Sentinel('Box')
        if self._item is _sentinel:
            msg = 'Box: Trying to pop an item from an empty Box'
            raise ValueError(msg)
        popped = cast(D, self._item)
        self._item = _sentinel
        return popped

    def map[U](self, f: Callable[[D], U]) -> Box[U]:
        """Map function `f` over contents. Return new instance."""
        if self._item is Sentinel('Box'):
            return Box()
        return Box(f(cast(D, self._item)))

    def bind[U](self, f: Callable[[D], Box[U]]) -> Box[U]:
        """Flatmap `Box` with function `f`. Return new instance."""
        if self._item is Sentinel('Box'):
            return Box()
        return f(cast(D, self._item))
