# Copyright 2023-2024 Geoffrey R. Scheller
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

from __future__ import annotations
from dtools.containers.functional_tuple import FunctionalTuple as IT
from dtools.containers.maybe import MayBe as MB
from dtools.containers.xor import Xor, RIGHT
from dtools.fp.iterables import FM

class TestITuple:
    """ITuple test suite"""
    def test_method_returns_copy(self) -> None:
        """Test guarantee"""
        it1 = IT(1, 2, 3, 4, 5, 6)
        it2 = it1.map(lambda x: x % 3)
        it3 = it1.copy()
        assert it2[2] == it2[5] == 0
        assert it1[2] is not None and it1[2]*2 == it1[5] == 6
        assert it3[2] is not None and it3[2]*2 == it3[5] == 6

    def test_empty(self) -> None:
        """Test functionality"""
        it1: IT[int] = IT()
        it2: IT[int] = IT()
        assert it1 == it2
        assert it1 is not it2
        assert not it1
        assert not it2
        assert len(it1) == 0
        assert len(it2) == 0
        it3 = it1 + it2
        assert it3 == it2 == it1
        assert it3 is not it1
        assert it3 is not it2
        assert not it3
        assert len(it3) == 0
        assert isinstance(it3, IT)
        it4 = it3.copy()
        assert it4 == it3
        assert it4 is not it3
        assert MB.idx(it1, 0).get(42) == 42
        assert str(Xor.idx(it2, 42)) == str(Xor(IndexError('tuple index out of range'), RIGHT))
        assert str(Xor.idx(it2, 42).get_right().get()) == 'tuple index out of range'

    def test_indexing(self) -> None:
        it0: IT[str] = IT()
        it1 = IT("Emily", "Rachel", "Sarah", "Rebekah", "Mary")
        assert it1[2] == "Sarah"
        assert it1[0] == "Emily"
        assert it1[-1] == "Mary"
        assert it1[1] == "Rachel"
        assert it1[-2] == "Rebekah"
        assert MB.idx(it1, -2).get('Buggy') == 'Rebekah'
        assert MB.idx(it1, 42).get('Buggy') == 'Buggy'
        assert MB.idx(it1, 0).get('Buggy') == 'Emily'
        assert MB.idx(it0, 0).get('Buggy') == 'Buggy'

    def test_slicing(self) -> None:
        it0: IT[int] = IT()
        it1: IT[int]  = IT(*range(0,101,10))
        assert it1 == IT(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
        assert it1[2:7:2] == IT(20, 40, 60)
        assert it1[8:2:-2] == IT(80, 60, 40)
        assert it1[8:] == IT(80, 90, 100)
        assert it1[8:-1] == IT(80, 90)
        assert it1 == it1[:]
        assert it1[8:130] == IT(80, 90, 100)
        assert it0[2:6] == IT()

    def test_map(self) -> None:
        it0: IT[int] = IT()
        it1: IT[int]  = IT(*range(6))
        assert it1 == IT(0, 1, 2, 3, 4, 5)

        assert it1.map(lambda t: t*t) == IT(0, 1, 4, 9, 16, 25)
        assert it0.map(lambda t: t*t) == IT()

    def test_foldl(self) -> None:
        it0: IT[int] = IT()
        it1: IT[int]  = IT(*range(1, 6))
        assert it1 == IT(1, 2, 3, 4, 5)

        assert it1.foldl(lambda s, t: s*t) == 120
        assert it0.foldl(lambda s, t: s*t, default=42) == 42
        assert it1.foldl(lambda s, t: s*t, 10) == 1200
        assert it0.foldl(lambda s, t: s*t, start=10) == 10

    def test_foldr(self) -> None:
        it0: IT[int] = IT()
        it1: IT[int]  = IT(*range(1, 4))
        assert it1 == IT(1, 2, 3)

        assert it1.foldr(lambda t, s: s*s - t) == 48
        assert it0.foldr(lambda t, s: s*s - t, default = -1) == -1
        assert it1.foldr(lambda t, s: s*s - t, start=5) == 232323
        assert it0.foldr(lambda t, s: s*s - t, 5) == 5

        try:
            _ = it0.foldr(lambda t, s: 5*t + 6*s)
        except ValueError:
            assert True
        else:
            assert False

        try:
            _ = it0.foldl(lambda t, s: 5*t + 6*s)
        except ValueError:
            assert True
        else:
            assert False

    def test_accummulate(self) -> None:
        it0: IT[int] = IT()
        it1: IT[int]  = IT(*range(1,6))
        assert it1 == IT(1, 2, 3, 4, 5)

        def add(x: int, y: int) -> int:
            return x + y

        assert it1.accummulate(add) == IT(1, 3, 6, 10, 15)
        assert it0.accummulate(add) == IT()
        assert it1.accummulate(lambda x, y: x+y, 1) == IT(1, 2, 4, 7, 11, 16)
        assert it0.accummulate(lambda x, y: x+y, 1) == IT(1)

    def test_bind(self) -> None:
        it0: IT[int] = IT()
        it1 = IT(4, 2, 3, 5)
        it2 = IT(4, 2, 0, 3)

        def ff(n: int) -> IT[int]:
            return IT(*range(n))

        fm = it1.bind(ff)
        mm = it1.bind(ff, FM.MERGE)
        em = it1.bind(ff, FM.EXHAUST)

        assert fm == IT(0, 1, 2, 3, 0, 1, 0, 1, 2, 0, 1, 2, 3, 4)
        assert mm == IT(0, 0, 0, 0, 1, 1, 1, 1)
        assert em == IT(0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4)

        fm = it2.bind(ff, FM.CONCAT)
        mm = it2.bind(ff, FM.MERGE)
        em = it2.bind(ff, FM.EXHAUST)

        assert fm == IT(0, 1, 2, 3, 0, 1, 0, 1, 2)
        assert mm == IT()
        assert em == IT(0, 0, 0, 1, 1, 1, 2, 2, 3)

        fm = it0.bind(ff, FM.CONCAT)
        mm = it0.bind(ff, FM.MERGE)
        em = it0.bind(ff, FM.EXHAUST)

        assert fm == IT()
        assert mm == IT()
        assert em == IT()
