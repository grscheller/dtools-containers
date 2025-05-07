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
from dtools.containers.ftuples.wrapped import WTuple as WT, wtuple as wt
from dtools.fp.iterables import FM
from dtools.fp.err_handling import MayBe as MB
from dtools.fp.err_handling import Xor, RIGHT

class TestWTuple:
    """WTuple test suite"""
    def test_method_returns_copy(self) -> None:
        """Test guarantee"""
        wt1 = wt(1, 2, 3, 4, 5, 6)
        wt2 = wt1.map(lambda x: x % 3)
        wt3 = wt1.copy()
        assert wt2[2] == wt2[5] == 0
        assert wt1[2] is not None and wt1[2]*2 == wt1[5] == 6
        assert wt3[2] is not None and wt3[2]*2 == wt3[5] == 6

    def test_empty(self) -> None:
        """Test functionality"""
        wt1: WT[int] = WT()
        wt2: WT[int] = wt()
        assert wt1 == wt2
        assert wt1 is not wt2
        assert not wt1
        assert not wt2
        assert len(wt1) == 0
        assert len(wt2) == 0
        wt3 = wt1 + wt2
        assert wt3 == wt2 == wt1
        assert wt3 is not wt1
        assert wt3 is not wt2
        assert not wt3
        assert len(wt3) == 0
        assert isinstance(wt3, WT)
        wt4 = wt3.copy()
        assert wt4 == wt3
        assert wt4 is not wt3
        assert MB.idx(wt1, 0).get(42) == 42
        assert str(Xor.idx(wt2, 42)) == str(Xor(IndexError('tuple index out of range'), RIGHT))
        assert str(Xor.idx(wt2, 42).get_right().get()) == 'tuple index out of range'

    def test_indexing(self) -> None:
        wt0: WT[str] = wt()
        wt1 = wt("Emily", "Rachel", "Sarah", "Rebekah", "Mary")
        assert wt1[2] == "Sarah"
        assert wt1[0] == "Emily"
        assert wt1[-1] == "Mary"
        assert wt1[1] == "Rachel"
        assert wt1[-2] == "Rebekah"
        assert MB.idx(wt1, -2).get('Buggy') == 'Rebekah'
        assert MB.idx(wt1, 42).get('Buggy') == 'Buggy'
        assert MB.idx(wt1, 0).get('Buggy') == 'Emily'
        assert MB.idx(wt0, 0).get('Buggy') == 'Buggy'

    def test_slicing(self) -> None:
        wt0: WT[int] = wt()
        wt1: WT[int]  = WT(range(0,101,10))
        assert wt1 == wt(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
        assert wt1[2:7:2] == wt(20, 40, 60)
        assert wt1[8:2:-2] == wt(80, 60, 40)
        assert wt1[8:] == wt(80, 90, 100)
        assert wt1[8:-1] == wt(80, 90)
        assert wt1 == wt1[:]
        assert wt1[8:130] == wt(80, 90, 100)
        assert wt0[2:6] == wt()

    def test_map(self) -> None:
        wt0: WT[int] = wt()
        wt1: WT[int]  = WT(range(6))
        assert wt1 == wt(0, 1, 2, 3, 4, 5)

        assert wt1.map(lambda t: t*t) == wt(0, 1, 4, 9, 16, 25)
        assert wt0.map(lambda t: t*t) == wt()

    def test_foldl(self) -> None:
        wt0: WT[int] = WT()
        wt1: WT[int]  = WT(range(1, 6))
        assert wt1 == wt(1, 2, 3, 4, 5)

        assert wt1.foldl(lambda s, t: s*t) == 120
        assert wt0.foldl(lambda s, t: s*t, default=42) == 42
        assert wt1.foldl(lambda s, t: s*t, 10) == 1200
        assert wt0.foldl(lambda s, t: s*t, start=10) == 10

    def test_foldr(self) -> None:
        wt0: WT[int] = wt()
        wt1: WT[int]  = WT(range(1, 4))
        assert wt1 == wt(1, 2, 3)

        assert wt1.foldr(lambda t, s: s*s - t) == 48
        assert wt0.foldr(lambda t, s: s*s - t, default = -1) == -1
        assert wt1.foldr(lambda t, s: s*s - t, start=5) == 232323
        assert wt0.foldr(lambda t, s: s*s - t, 5) == 5

        try:
            _ = wt0.foldr(lambda t, s: 5*t + 6*s)
        except ValueError:
            assert True
        else:
            assert False

        try:
            _ = wt0.foldl(lambda t, s: 5*t + 6*s)
        except ValueError:
            assert True
        else:
            assert False

    def test_accummulate(self) -> None:
        wt0: WT[int] = WT()
        wt1: WT[int]  = WT(range(1,6))
        assert wt1 == wt(1, 2, 3, 4, 5)

        def add(x: int, y: int) -> int:
            return x + y

        assert wt1.accummulate(add) == wt(1, 3, 6, 10, 15)
        assert wt0.accummulate(add) == wt()
        assert wt1.accummulate(lambda x, y: x+y, 1) == wt(1, 2, 4, 7, 11, 16)
        assert wt0.accummulate(lambda x, y: x+y, 1) == wt(1)

    def test_bind(self) -> None:
        wt0: WT[int] = wt()
        wt1 = wt(4, 2, 3, 5)
        wt2 = wt(4, 2, 0, 3)

        def ff(n: int) -> WT[int]:
            return WT(range(n))

        fm = wt1.bind(ff)
        mm = wt1.bind(ff, FM.MERGE)
        em = wt1.bind(ff, FM.EXHAUST)

        assert fm == wt(0, 1, 2, 3, 0, 1, 0, 1, 2, 0, 1, 2, 3, 4)
        assert mm == wt(0, 0, 0, 0, 1, 1, 1, 1)
        assert em == wt(0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4)

        fm = wt2.bind(ff, FM.CONCAT)
        mm = wt2.bind(ff, FM.MERGE)
        em = wt2.bind(ff, FM.EXHAUST)

        assert fm == wt(0, 1, 2, 3, 0, 1, 0, 1, 2)
        assert mm == wt()
        assert em == wt(0, 0, 0, 1, 1, 1, 2, 2, 3)

        fm = wt0.bind(ff, FM.CONCAT)
        mm = wt0.bind(ff, FM.MERGE)
        em = wt0.bind(ff, FM.EXHAUST)

        assert fm == wt()
        assert mm == wt()
        assert em == wt()
