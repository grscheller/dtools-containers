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
### Tuple based data structures

Only example here is the ftuple, basically an FP interface wrapping a tuple.
Originally it inherited from tuple, but I found containing the tuple in a
"has-a" relationship makes for a faster implementation. Buried in the git
history is another example called a "process array" (parray) which I might
return to someday. The idea of the parray is a fixed length sequence with
sentinel values.

#### FTuple and FT factory function.

* class FTuple: Wrapped tuple with a Functional Programming API
* function FE:

"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import cast, Never, overload#, TypeVar
from dtools.fp.iterables import FM, accumulate, concat, exhaust, merge

__all__ = ['FTuple']

# D = TypeVar('D')  # Hint for pdoc,
# E = TypeVar('E')  # not needed for mypy or Python.
# L = TypeVar('L')  # Uncomment these lines and
# R = TypeVar('R')  # the "#, TypeVar" above
# U = TypeVar('U')  #
# T = TypeVar('T')  #


class FTuple[D]():
    """
    #### Functional Tuple

    * immutable tuple-like data structure with a functional interface
    * supports both indexing and slicing
    * `FTuple` addition & `int` multiplication supported
      * addition concatenates results, resulting type a Union type
      * both left and right int multiplication supported

    """

    __slots__ = ('_ds',)

    def __init__(self, *dss: Iterable[D]) -> None:
        if (size := len(dss)) <= 1:
            self._ds: tuple[D, ...] = tuple(dss[0]) if size > 0 else tuple()
        else:
            msg = f'FTuple expects at most 1 iterable argument, got {size}'
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
    def __getitem__(self, idx: slice, /) -> FTuple[D]: ...

    def __getitem__(self, idx: slice | int, /) -> FTuple[D] | D:
        if isinstance(idx, slice):
            return FTuple(self._ds[idx])
        return self._ds[idx]

    def foldl[L](
        self,
        f: Callable[[L, D], L],
        /,
        start: L | None = None,
        default: L | None = None,
    ) -> L | None:
        """
        **Fold Left**

        * fold left with an optional starting value
        * first argument of function `f` is for the accumulated value
        * throws `ValueError` when `FTuple` empty and a start value not given

        """
        it = iter(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(L, next(it))  # L = D in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty FTuple'
                raise ValueError('FTuple.foldL - ' + msg)
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
        """
        **Fold Right**

        * fold right with an optional starting value
        * second argument of function `f` is for the accumulated value
        * throws `ValueError` when `FTuple` empty and a start value not given

        """
        it = reversed(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(R, next(it))  # R = D in this case
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty FTuple'
                raise ValueError('FTuple.foldR - ' + msg)
            acc = default
        for v in it:
            acc = f(v, acc)
        return acc

    def copy(self) -> FTuple[D]:
        """Return a shallow copy of FTuple in O(1) time & space complexity."""
        return FTuple(self)

    def __add__[E](self, other: FTuple[E], /) -> FTuple[D | E]:
        if not isinstance(other, FTuple):
            msg = 'Not an FTuple'
            raise ValueError(msg)
        return FTuple(concat(self, other))

    def __mul__(self, num: int, /) -> FTuple[D]:
        return FTuple(self._ds.__mul__(num if num > 0 else 0))

    def __rmul__(self, num: int, /) -> FTuple[D]:
        return FTuple(self._ds.__mul__(num if num > 0 else 0))

    def accummulate[L](
        self, f: Callable[[L, D], L], s: L | None = None, /
    ) -> FTuple[L]:
        """
        **Accumulate partial folds**

        Accumulate partial fold results in an FTuple with an optional starting
        value.

        """
        if s is None:
            return FTuple(accumulate(self, f))
        return FTuple(accumulate(self, f, s))

    def map[U](self, f: Callable[[D], U], /) -> FTuple[U]:
        return FTuple(map(f, self))

    def bind[U](
        self, f: Callable[[D], FTuple[U]], type: FM = FM.CONCAT, /
    ) -> FTuple[U] | Never:
        """
        Bind function `f` to the `FTuple`.

        * type = CONCAT: sequentially concatenate iterables one after the other
        * type = MERGE: merge iterables together until one is exhausted
        * type = Exhaust: merge iterables together until all are exhausted

        """
        match type:
            case FM.CONCAT:
                return FTuple(concat(*map(f, self)))
            case FM.MERGE:
                return FTuple(merge(*map(f, self)))
            case FM.EXHAUST:
                return FTuple(exhaust(*map(f, self)))
            case '*':
                raise ValueError('Unknown FM type')

def f_tuple[T](*ts: T) -> FTuple[T]:
    """Return an `FTuple` from multiple values."""
    return FTuple(ts)
