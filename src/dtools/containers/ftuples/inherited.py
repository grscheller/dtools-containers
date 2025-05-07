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

Providing a FP interface for tuples. Implemented by inheriting from tuple.

- class `ITuple`
  - inherits from tuple with an "is-a" implementation
    - intended to be further inherited
    - unslotted 
  - function `ituple`
    - return an ITuple from function's arguments

"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import cast, Never, overload, TypeVar
from dtools.fp.iterables import FM, accumulate, concat, exhaust, merge

__all__ = ['ITuple', 'ituple']

D = TypeVar('D')
T = TypeVar('T')


class ITuple[D]():
    """
    #### Functional Tuple suitable for inheritance

    TODO: replace this from one I have in my GIT history

    * immutable tuple-like data structure with a functional interface
    * supports both indexing and slicing
    * `ITuple` addition & `int` multiplication supported
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
            msg = f'ITuple expects at most 1 iterable argument, got {size}'
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
    def __getitem__(self, idx: slice, /) -> ITuple[D]: ...

    def __getitem__(self, idx: slice | int, /) -> ITuple[D] | D:
        if isinstance(idx, slice):
            return ITuple(self._ds[idx])
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
        * throws `ValueError` when `ITuple` empty and a start value not given

        """
        it = iter(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(L, next(it))  # L = D in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty ITuple'
                raise ValueError('ITuple.foldl - ' + msg)
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
        * throws `ValueError` when `ITuple` empty and a start value not given

        """
        it = reversed(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(R, next(it))  # R = D in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty ITuple'
                raise ValueError('ITuple.foldR - ' + msg)
            acc = default
        for v in it:
            acc = f(v, acc)
        return acc

    def copy(self) -> ITuple[D]:
        """Return a shallow copy of ITuple in O(1) time & space complexity."""
        return ITuple(self)

    def __add__[E](self, other: ITuple[E], /) -> ITuple[D | E]:
        if not isinstance(other, ITuple):
            msg = 'Not an ITuple'
            raise ValueError(msg)
        return ITuple(concat(self, other))

    def __mul__(self, num: int, /) -> ITuple[D]:
        return ITuple(self._ds.__mul__(num if num > 0 else 0))

    def __rmul__(self, num: int, /) -> ITuple[D]:
        return ITuple(self._ds.__mul__(num if num > 0 else 0))

    def accummulate[L](
        self, f: Callable[[L, D], L], s: L | None = None, /
    ) -> ITuple[L]:
        """Accumulate partial folds

        Accumulate partial fold results in an ITuple with an optional starting
        value.

        """
        if s is None:
            return ITuple(accumulate(self, f))
        return ITuple(accumulate(self, f, s))

    def map[U](self, f: Callable[[D], U], /) -> ITuple[U]:
        return ITuple(map(f, self))

    def bind[U](
        self, f: Callable[[D], ITuple[U]], type: FM = FM.CONCAT, /
    ) -> ITuple[U] | Never:
        """Bind function `f` to the `ITuple`.

        * FM Enum types
          * CONCAT: sequentially concatenate iterables one after the other
          * MERGE: round-robin merge iterables until one is exhausted
          * EXHAUST: round-robin merge iterables until all are exhausted

        """
        match type:
            case FM.CONCAT:
                return ITuple(concat(*map(f, self)))
            case FM.MERGE:
                return ITuple(merge(*map(f, self)))
            case FM.EXHAUST:
                return ITuple(exhaust(*map(f, self)))

        raise ValueError('Unknown FM type')

def ituple[T](*ts: T) -> ITuple[T]:
    """Return an `ITuple` from multiple values."""
    return ITuple(ts)
