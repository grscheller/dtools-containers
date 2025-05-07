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
### dtools.containers.ftuples.iftuples

Providing a FP interface for tuples.

- class `IFTuple`
  - inherits from tuple with a "is-a" implemetation
    - intended to be further inherited
    - unslotted 
  - function `iftuple`
    - return an IFTuple from multiple values

"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import cast, Never, overload, TypeVar
from dtools.fp.iterables import FM, accumulate, concat, exhaust, merge

__all__ = ['IFTuple']

D = TypeVar('D')
T = TypeVar('T')


class IFTuple[D]():
    """
    #### Functional Tuple

    * immutable tuple-like data structure with a functional interface
    * supports both indexing and slicing
    * `IFTuple` addition & `int` multiplication supported
      * addition concatenates results, resulting type a Union type
      * both left and right int multiplication supported

    """
    E = TypeVar('E')
    L = TypeVar('L')
    R = TypeVar('R')
    U = TypeVar('U')

 #   def __new__(cls) ...
 #
    def __init__(self, *dss: Iterable[D]) -> None:
        if (size := len(dss)) <= 1:
            self._ds: tuple[D, ...] = tuple(dss[0]) if size == 1 else tuple()
        else:
            msg = f'IFTuple expects at most 1 iterable argument, got {size}'
            #raise TypeError(msg)
            raise ValueError(msg)

    def __iter__(self) -> Iterator[D]:
        return iter(self._ds)

    def __reversed__(self) -> Iterator[D]:
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
    def __getitem__(self, idx: int, /) -> D: ...
    @overload
    def __getitem__(self, idx: slice, /) -> IFTuple[D]: ...

    def __getitem__(self, idx: slice | int, /) -> IFTuple[D] | D:
        if isinstance(idx, slice):
            return IFTuple(self._ds[idx])
        return self._ds[idx]

    def foldl[L](
        self,
        f: Callable[[L, D], L],
        /,
        start: L | None = None,
        default: L | None = None,
    ) -> L | None:
        """Fold Left

        * fold left with an optional starting value
        * first argument of function `f` is for the accumulated value
        * throws `ValueError` when `IFTuple` empty and a start value not given

        """
        it = iter(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(L, next(it))  # L = D in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty IFTuple'
                raise ValueError('IFTuple.foldl - ' + msg)
            acc = default
        for v in it:
            acc = f(acc, v)
        return acc

    def foldr[R](
        self,
        f: Callable[[D, R], R],
        /,
        start: R | None = None,
        default: R | None = None,
    ) -> R | None:
        """Fold Right

        * fold right with an optional starting value
        * second argument of function `f` is for the accumulated value
        * throws `ValueError` when `IFTuple` empty and a start value not given

        """
        it = reversed(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(R, next(it))  # R = D in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty IFTuple'
                raise ValueError('IFTuple.foldR - ' + msg)
            acc = default
        for v in it:
            acc = f(v, acc)
        return acc

    def copy(self) -> IFTuple[D]:
        """Return a shallow copy of IFTuple in O(1) time & space complexity."""
        return IFTuple(self)

    def __add__[E](self, other: IFTuple[E], /) -> IFTuple[D | E]:
        if not isinstance(other, IFTuple):
            msg = 'Not an IFTuple'
            raise ValueError(msg)
        return IFTuple(concat(self, other))

    def __mul__(self, num: int, /) -> IFTuple[D]:
        return IFTuple(self._ds.__mul__(num if num > 0 else 0))

    def __rmul__(self, num: int, /) -> IFTuple[D]:
        return IFTuple(self._ds.__mul__(num if num > 0 else 0))

    def accummulate[L](
        self, f: Callable[[L, D], L], s: L | None = None, /
    ) -> IFTuple[L]:
        """Accumulate partial folds

        Accumulate partial fold results in an IFTuple with an optional starting
        value.

        """
        if s is None:
            return IFTuple(accumulate(self, f))
        return IFTuple(accumulate(self, f, s))

    def map[U](self, f: Callable[[D], U], /) -> IFTuple[U]:
        return IFTuple(map(f, self))

    def bind[U](
        self, f: Callable[[D], IFTuple[U]], type: FM = FM.CONCAT, /
    ) -> IFTuple[U] | Never:
        """Bind function `f` to the `IFTuple`.

        * FM Enum types
          * CONCAT: sequentially concatenate iterables one after the other
          * MERGE: round-robin merge iterables until one is exhausted
          * EXHAUST: round-robin merge iterables until all are exhausted

        """
        match type:
            case FM.CONCAT:
                return IFTuple(concat(*map(f, self)))
            case FM.MERGE:
                return IFTuple(merge(*map(f, self)))
            case FM.EXHAUST:
                return IFTuple(exhaust(*map(f, self)))

        raise ValueError('Unknown FM type')

def iftuple[T](*ts: T) -> IFTuple[T]:
    """Return an `IFTuple` from multiple values."""
    return IFTuple(ts)
