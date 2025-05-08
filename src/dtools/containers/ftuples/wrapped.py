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
### dtools.containers.ftuples.wrapped

Providing FP interfaces for tuples. Implemented with a wrapped tuple.

- class `WTuple`
  - wrapped tuple with a "has-a" implementation
    - intended to be a "better" tuple
    - not intended to be inherited from
    - slotted 
  - function `wtuple`
    - return an WTuple from function's arguments

"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import cast, Never, overload, TypeVar
from dtools.fp.iterables import FM, accumulate, concat, exhaust, merge

__all__ = ['WTuple', 'wtuple']

D_co = TypeVar('D_co', covariant=True)
T_co = TypeVar('T_co', covariant=True)


class WTuple[D_co]():
    """
    #### Functional Tuple giving a tuple a more FP API

    * immutable tuple-like data structure with a functional interface
    * supports both indexing and slicing
    * `WTuple` addition & `int` multiplication supported
      * addition concatenates results, resulting type a Union type
      * both left and right int multiplication supported

    """

    __slots__ = ('_ds',)

    E = TypeVar('E')
    L = TypeVar('L')
    R = TypeVar('R')
    U = TypeVar('U')


    def __init__(self, *dss: Iterable[D_co]) -> None:
        if (size := len(dss)) <= 1:
            self._ds: tuple[D_co, ...] = tuple(dss[0]) if size == 1 else tuple()
        else:
            msg = f'WTuple expects at most 1 iterable argument, got {size}'
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
    def __getitem__(self, idx: slice, /) -> WTuple[D_co]: ...

    def __getitem__(self, idx: slice | int, /) -> WTuple[D_co] | D_co:
        if isinstance(idx, slice):
            return WTuple(self._ds[idx])
        return self._ds[idx]

    def foldl[L](
        self,
        f: Callable[[L, D_co], L],
        /,
        start: L | None = None,
        default: L | None = None,
    ) -> L | None:
        """Fold Left

        * fold left with an optional starting value
        * first argument of function `f` is for the accumulated value
        * throws `ValueError` when `WTuple` empty and a start value not given

        """
        it = iter(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(L, next(it))  # L = D in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty WTuple'
                raise ValueError('WTuple.foldl - ' + msg)
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
        * throws `ValueError` when `WTuple` empty and a start value not given

        """
        it = reversed(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(R, next(it))  # R = D in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty WTuple'
                raise ValueError('WTuple.foldR - ' + msg)
            acc = default
        for v in it:
            acc = f(v, acc)
        return acc

    def copy(self) -> WTuple[D_co]:
        """Return a shallow copy of WTuple in O(1) time & space complexity."""
        return WTuple(self)

    def __add__[E](self, other: WTuple[E], /) -> WTuple[D_co | E]:
        if not isinstance(other, WTuple):
            msg = 'Not an WTuple'
            raise ValueError(msg)
        return WTuple(concat(self, other))

    def __mul__(self, num: int, /) -> WTuple[D_co]:
        return WTuple(self._ds.__mul__(num if num > 0 else 0))

    def __rmul__(self, num: int, /) -> WTuple[D_co]:
        return WTuple(self._ds.__mul__(num if num > 0 else 0))

    def accummulate[L](
        self, f: Callable[[L, D_co], L], s: L | None = None, /
    ) -> WTuple[L]:
        """Accumulate partial folds

        Accumulate partial fold results in an WTuple with an optional starting
        value.

        """
        if s is None:
            return WTuple(accumulate(self, f))
        return WTuple(accumulate(self, f, s))

    def map[U](self, f: Callable[[D_co], U], /) -> WTuple[U]:
        return WTuple(map(f, self))

    def bind[U](
        self, f: Callable[[D_co], WTuple[U]], type: FM = FM.CONCAT, /
    ) -> WTuple[U] | Never:
        """Bind function `f` to the `WTuple`.

        * FM Enum types
          * CONCAT: sequentially concatenate iterables one after the other
          * MERGE: round-robin merge iterables until one is exhausted
          * EXHAUST: round-robin merge iterables until all are exhausted

        """
        match type:
            case FM.CONCAT:
                return WTuple(concat(*map(f, self)))
            case FM.MERGE:
                return WTuple(merge(*map(f, self)))
            case FM.EXHAUST:
                return WTuple(exhaust(*map(f, self)))

        raise ValueError('Unknown FM type')

def wtuple[T_co](*ts: T_co) -> WTuple[T_co]:
    """Return an `WTuple` from multiple values."""
    return WTuple(ts)
