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

"""
#### Immutable homogeneous "lists"

- immutable data structure whose elements are all of the same type
- a Luple can be of arbitrary length >= 1
- hashable if elements are hashable
- declared covariant in its generic datatype
  - hashability will be enforced by LSP tooling
  - Luple addition supported 

"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import cast, Never, overload, TypeVar
from dtools.fp.iterables import FM, accumulate, concat, exhaust, merge

__all__ = ['Luple']

D_co = TypeVar('D_co', covariant=True)


class Luple[D_co]:
    """Immutable List like data structures 

    - immutable "lists" all whose elements are all of the same type
    - hashable if elements are hashable
      - A `Luple` is declared covariant in its generic datatype
      - hashability will be enforced by LSP tooling
    - supports both indexing and slicing
    - `Luple` addition & `int` multiplication supported
      - addition concatenates results, resulting type a Union type
      - both left and right int multiplication supported

    """

    __slots__ = ('_ds', '_len')
    __match_args__ = ('_ds', '_len')

    L_co = TypeVar('L_co', covariant=True)
    R_co = TypeVar('R_co', covariant=True)
    U_co = TypeVar('U_co', covariant=True)


    def __init__(self, *dss: Iterable[D_co]) -> None:
        if (size := len(dss)) <= 1:
            self._ds: tuple[D_co, ...] = tuple(dss[0]) if size == 1 else tuple()
            self._len = len(self._ds)
        else:
            msg = f'Luple expects at most 1 iterable argument, got {size}'
            raise ValueError(msg)

    def __iter__(self) -> Iterator[D_co]:
        return iter(self._ds)

    def __reversed__(self) -> Iterator[D_co]:
        return reversed(self._ds)

    def __bool__(self) -> bool:
        return bool(self._ds)

    def __len__(self) -> int:
        return len(self._ds)

    def __repr__(self) -> str:
        return 'FT(' + ', '.join(map(repr, self)) + ')'

    def __str__(self) -> str:
        return '((' + ', '.join(map(repr, self)) + '))'

    def __eq__(self, other: object, /) -> bool:
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self._ds == other._ds

    @overload
    def __getitem__(self, idx: int, /) -> D_co: ...
    @overload
    def __getitem__(self, idx: slice, /) -> Luple[D_co]: ...

    def __getitem__(self, idx: slice | int, /) -> Luple[D_co] | D_co:
        if isinstance(idx, slice):
            return Luple(self._ds[idx])
        return self._ds[idx]

    def foldl[L_co](
        self,
        f: Callable[[L_co, D_co], L_co],
        /,
        start: L_co | None = None,
        default: L_co | None = None,
    ) -> L_co | None:
        """Fold Left

        * fold left with an optional starting value
        * first argument of function `f` is for the accumulated value
        * throws `ValueError` when `Luple` empty and a start value not given

        """
        it = iter(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(L_co, next(it))  # L_co = D_co in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty L_couple'
                raise ValueError('Luple.foldl - ' + msg)
            acc = default
        for v in it:
            acc = f(acc, v)
        return acc

    def foldr[R](
        self,
        f: Callable[[D_co, R], R],
        /,
        start: R | None = None,
        default: R | None = None,
    ) -> R | None:
        """Fold Right

        * fold right with an optional starting value
        * second argument of function `f` is for the accumulated value
        * throws `ValueError` when `Luple` empty and a start value not given

        """
        it = reversed(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(R, next(it))  # R = D in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty Luple'
                raise ValueError('Luple.foldR - ' + msg)
            acc = default
        for v in it:
            acc = f(v, acc)
        return acc

    def copy(self) -> Luple[D_co]:
        """Return a shallow copy of Luple in O(1) time & space complexity."""
        return Luple(self)

    def __add__(self, other: Luple[D_co], /) -> Luple[D_co]:
        if not isinstance(other, Luple):
            msg = 'Luple being added to something not a Luple'
            raise ValueError(msg)

        return Luple(concat(self, other))

    def __mul__(self, num: int, /) -> Luple[D_co]:
        return Luple(self._ds.__mul__(num if num > 0 else 0))

    def __rmul__(self, num: int, /) -> Luple[D_co]:
        return Luple(self._ds.__mul__(num if num > 0 else 0))

    def accummulate[L_co](
        self, f: Callable[[L_co, D_co], L_co], s: L_co | None = None, /
    ) -> Luple[L_co]:
        """Accumulate partial folds

        Accumulate partial fold results in an Luple with an optional starting
        value.

        """
        if s is None:
            return Luple(accumulate(self, f))
        return Luple(accumulate(self, f, s))

    def map[U_co](self, f: Callable[[D_co], U_co], /) -> Luple[U_co]:
        return Luple(map(f, self))

    def bind[U_co](
        self, f: Callable[[D_co], Luple[U_co]], type: FM = FM.CONCAT, /
    ) -> Luple[U_co] | Never:
        """Bind function `f` to the `Luple`.

        * FM Enum types
          * CONCAT: sequentially concatenate iterables one after the other
          * MERGE: round-robin merge iterables until one is exhausted
          * EXHAUST: round-robin merge iterables until all are exhausted

        """
        match type:
            case FM.CONCAT:
                return Luple(concat(*map(f, self)))
            case FM.MERGE:
                return Luple(merge(*map(f, self)))
            case FM.EXHAUST:
                return Luple(exhaust(*map(f, self)))

        raise ValueError('Unknown FM type')


def luple[D_co](*ds: D_co) -> Luple[D_co]:
    return Luple(ds)
