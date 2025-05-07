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
from dtools.containers.ftuples.hftuple import HFTuple as HFT, hftuple as hft
from dtools.fp.iterables import FM
from dtools.fp.err_handling import MayBe as MB
from dtools.fp.err_handling import Xor, RIGHT

class TestHFT:
    """HFTuple test suite"""
    def test_method_returns_copy(self) -> None:
        """Test guarantee"""
        hft1 = hft(1, 2, 3, 4, 5, 6)
        hft2 = hft1.map(lambda x: x % 3)
        hft3 = hft1.copy()
        assert hft2[2] == hft2[5] == 0
        assert hft1[2] is not None and hft1[2]*2 == hft1[5] == 6
        assert hft3[2] is not None and hft3[2]*2 == hft3[5] == 6

    def test_empty(self) -> None:
        """Test functionality"""
        hft1: HFT[int] = HFT()
        hft2: HFT[int] = hft()
        assert hft1 == hft2
        assert hft1 is not hft2
        assert not hft1
        assert not hft2
        assert len(hft1) == 0
        assert len(hft2) == 0
        hft3 = hft1 + hft2
        assert hft3 == hft2 == hft1
        assert hft3 is not hft1
        assert hft3 is not hft2
        assert not hft3
        assert len(hft3) == 0
        assert isinstance(hft3, HFT)
        hft4 = hft3.copy()
        assert hft4 == hft3
        assert hft4 is not hft3
        assert MB.idx(hft1, 0).get(42) == 42
        assert str(Xor.idx(hft2, 42)) == str(Xor(IndexError('tuple index out of range'), RIGHT))
        assert str(Xor.idx(hft2, 42).get_right().get()) == 'tuple index out of range'

    def test_indexing(self) -> None:
        hft0: HFT[str] = hft()
        hft1 = hft("Emily", "Rachel", "Sarah", "Rebekah", "Mary")
        assert hft1[2] == "Sarah"
        assert hft1[0] == "Emily"
        assert hft1[-1] == "Mary"
        assert hft1[1] == "Rachel"
        assert hft1[-2] == "Rebekah"
        assert MB.idx(hft1, -2).get('Buggy') == 'Rebekah'
        assert MB.idx(hft1, 42).get('Buggy') == 'Buggy'
        assert MB.idx(hft1, 0).get('Buggy') == 'Emily'
        assert MB.idx(hft0, 0).get('Buggy') == 'Buggy'

    def test_slicing(self) -> None:
        hft0: HFT[int] = hft()
        hft1: HFT[int]  = HFT(range(0,101,10))
        assert hft1 == hft(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
        assert hft1[2:7:2] == hft(20, 40, 60)
        assert hft1[8:2:-2] == hft(80, 60, 40)
        assert hft1[8:] == hft(80, 90, 100)
        assert hft1[8:-1] == hft(80, 90)
        assert hft1 == hft1[:]
        assert hft1[8:130] == hft(80, 90, 100)
        assert hft0[2:6] == hft()

    def test_map(self) -> None:
        hft0: HFT[int] = hft()
        hft1: HFT[int]  = HFT(range(6))
        assert hft1 == hft(0, 1, 2, 3, 4, 5)

        assert hft1.map(lambda t: t*t) == hft(0, 1, 4, 9, 16, 25)
        assert hft0.map(lambda t: t*t) == hft()

    def test_foldl(self) -> None:
        hft0: HFT[int] = HFT()
        hft1: HFT[int]  = HFT(range(1, 6))
        assert hft1 == hft(1, 2, 3, 4, 5)

        assert hft1.foldl(lambda s, t: s*t) == 120
        assert hft0.foldl(lambda s, t: s*t, default=42) == 42
        assert hft1.foldl(lambda s, t: s*t, 10) == 1200
        assert hft0.foldl(lambda s, t: s*t, start=10) == 10

    def test_foldr(self) -> None:
        hft0: HFT[int] = hft()
        hft1: HFT[int]  = HFT(range(1, 4))
        assert hft1 == hft(1, 2, 3)

        assert hft1.foldr(lambda t, s: s*s - t) == 48
        assert hft0.foldr(lambda t, s: s*s - t, default = -1) == -1
        assert hft1.foldr(lambda t, s: s*s - t, start=5) == 232323
        assert hft0.foldr(lambda t, s: s*s - t, 5) == 5

        try:
            _ = hft0.foldr(lambda t, s: 5*t + 6*s)
        except ValueError:
            assert True
        else:
            assert False

        try:
            _ = hft0.foldl(lambda t, s: 5*t + 6*s)
        except ValueError:
            assert True
        else:
            assert False

    def test_accummulate(self) -> None:
        hft0: HFT[int] = HFT()
        hft1: HFT[int]  = HFT(range(1,6))
        assert hft1 == hft(1, 2, 3, 4, 5)

        def add(x: int, y: int) -> int:
            return x + y

        assert hft1.accummulate(add) == hft(1, 3, 6, 10, 15)
        assert hft0.accummulate(add) == hft()
        assert hft1.accummulate(lambda x, y: x+y, 1) == hft(1, 2, 4, 7, 11, 16)
        assert hft0.accummulate(lambda x, y: x+y, 1) == hft(1)

    def test_bind(self) -> None:
        hft0: HFT[int] = hft()
        hft1 = hft(4, 2, 3, 5)
        hft2 = hft(4, 2, 0, 3)

        def ff(n: int) -> HFT[int]:
            return HFT(range(n))

        fm = hft1.bind(ff)
        mm = hft1.bind(ff, FM.MERGE)
        em = hft1.bind(ff, FM.EXHAUST)

        assert fm == hft(0, 1, 2, 3, 0, 1, 0, 1, 2, 0, 1, 2, 3, 4)
        assert mm == hft(0, 0, 0, 0, 1, 1, 1, 1)
        assert em == hft(0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4)

        fm = hft2.bind(ff, FM.CONCAT)
        mm = hft2.bind(ff, FM.MERGE)
        em = hft2.bind(ff, FM.EXHAUST)

        assert fm == hft(0, 1, 2, 3, 0, 1, 0, 1, 2)
        assert mm == hft()
        assert em == hft(0, 0, 0, 1, 1, 1, 2, 2, 3)

        fm = hft0.bind(ff, FM.CONCAT)
        mm = hft0.bind(ff, FM.MERGE)
        em = hft0.bind(ff, FM.EXHAUST)

        assert fm == hft()
        assert mm == hft()
        assert em == hft()
