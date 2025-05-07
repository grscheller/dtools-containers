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

"""Test FP use cases"""

from __future__ import annotations
from dtools.containers.ftuples.hftuple import HFTuple as HFT, hftuple as hft
from dtools.splitends.splitend import SplitEnd as SE
from dtools.fp.iterables import FM
from dtools.fp.err_handling import MayBe as MB


class TestFP:
    """FP test of HFTuple with other datastructures"""
    def test_fold(self) -> None:
        """Test folding"""
        def add2(x: int, y: int) -> int:
            return x + y

        def mult2[S](x: int, y: int) -> int:
            return x * y

        def push_se[S](se: SE[S], d: S) -> SE[S]:
            se.push(d)
            return se

        hft0: HFT[int] = HFT()
        hft5: HFT[int] = hft(1, 2, 3, 4, 5)
        se5 = SE(1, 2, 3, 4, 5)

        assert se5.peak() == 5
        assert hft5[1] == 2
        assert hft5[4] == 5

        assert hft0.foldl(add2, 42) == 42
        assert hft0.foldr(add2, 42) == 42
        assert hft5.foldl(add2) == 15
        assert hft5.foldl(add2, 0) == 15
        assert hft5.foldl(add2, 10) == 25
        assert hft5.foldl(mult2, 1) == 120
        assert hft5.foldl(mult2, 10) == 1200
        assert hft5.foldr(add2) == 15
        assert hft5.foldr(add2, 0) == 15
        assert hft5.foldr(add2, 10) == 25
        assert hft5.foldr(mult2, 1) == 120
        assert hft5.foldr(mult2, 10) == 1200
        assert hft5 == hft(1, 2, 3, 4, 5)

        assert se5.fold(add2) == 15
        assert se5.fold(add2, 10) == 25
        assert se5.fold(mult2) == 120
        assert se5.fold(mult2, 10) == 1200
        se_temp = se5.copy()
        se_temp.pop()
        se5_rev = se_temp.fold(push_se, SE(se5.peak()))
        assert se5_rev == SE(5, 4, 3, 2, 1)
        assert se5.fold(add2) == 15
        assert se5.fold(add2, 10) == 25

        assert hft5.accummulate(add2) == hft(1, 3, 6, 10, 15)
        assert hft5.accummulate(add2, 10) == hft(10, 11, 13, 16, 20, 25)
        assert hft5.accummulate(mult2) == hft(1, 2, 6, 24, 120)
        assert hft0.accummulate(add2) == HFT()
        assert hft0.accummulate(mult2) == HFT()

    def test_hftuple_bind(self) -> None:
        """Test bind (flatmap)"""
        hft0 = HFT(range(3, 101))
        l1 = lambda x: 2 * x + 1
        l2 = lambda x: HFT(range(2, x + 1)).accummulate(lambda x, y: x + y)
        hft1 = hft0.map(l1)
        hft2 = hft0.bind(l2, FM.CONCAT)
        hft3 = hft0.bind(l2, FM.MERGE)
        hft4 = hft0.bind(l2, FM.EXHAUST)
        assert (hft1[0], hft1[1], hft1[2], hft1[-1]) == (7, 9, 11, 201)
        assert (hft2[0], hft2[1]) == (2, 5)
        assert (hft2[2], hft2[3], hft2[4]) == (2, 5, 9)
        assert (hft2[5], hft2[6], hft2[7], hft2[8]) == (2, 5, 9, 14)
        assert hft2[-1] == hft2[4948] == 5049
        assert MB.idx(hft2, -1).get(42) == hft2[4948] == 5049
        assert MB.idx(hft2, 4949) == MB()
        assert (hft3[0], hft3[1]) == (2, 2)
        assert (hft3[2], hft3[3]) == (2, 2)
        assert (hft3[4], hft3[5]) == (2, 2)
        assert (hft3[96], hft3[97]) == (2, 2)
        assert (hft3[98], hft3[99]) == (5, 5)
        assert MB.idx(hft3, 196) == MB()
        assert (hft4[0], hft4[1], hft4[2]) == (2, 2, 2)
        assert (hft4[95], hft4[96], hft4[97]) == (2, 2, 2)
        assert (hft4[98], hft4[99], hft4[100]) == (5, 5, 5)
        assert (hft4[290], hft4[291], hft4[292]) == (9, 9, 9)
        assert (hft4[293], hft4[294], hft4[295]) == (14, 14, 14)
        assert (hft4[-4], hft4[-3], hft4[-2], hft4[-1]) == (4850, 4949, 4949, 5049)
        assert hft4[-1] == hft4[4948] == 5049
        assert MB.idx(hft2, 4949) == MB()
