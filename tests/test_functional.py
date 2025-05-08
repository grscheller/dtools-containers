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
from dtools.containers.ftuples.wrapped import Luple as WT, luple as wt
from dtools.splitends.splitend import SplitEnd as SE
from dtools.fp.iterables import FM
from dtools.fp.err_handling import MayBe as MB


class TestFP:
    """FP test of wtuple with other datastructures"""
    def test_fold(self) -> None:
        """Test folding"""
        def add2(x: int, y: int) -> int:
            return x + y

        def mult2[S](x: int, y: int) -> int:
            return x * y

        def push_se[S](se: SE[S], d: S) -> SE[S]:
            se.push(d)
            return se

        wt0: WT[int] = wt()
        wt5: WT[int] = wt(1, 2, 3, 4, 5)
        se5 = SE(1, 2, 3, 4, 5)

        assert se5.peak() == 5
        assert wt5[1] == 2
        assert wt5[4] == 5

        assert wt0.foldl(add2, 42) == 42
        assert wt0.foldr(add2, 42) == 42
        assert wt5.foldl(add2) == 15
        assert wt5.foldl(add2, 0) == 15
        assert wt5.foldl(add2, 10) == 25
        assert wt5.foldl(mult2, 1) == 120
        assert wt5.foldl(mult2, 10) == 1200
        assert wt5.foldr(add2) == 15
        assert wt5.foldr(add2, 0) == 15
        assert wt5.foldr(add2, 10) == 25
        assert wt5.foldr(mult2, 1) == 120
        assert wt5.foldr(mult2, 10) == 1200
        assert wt5 == wt(1, 2, 3, 4, 5)

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

        assert wt5.accummulate(add2) == wt(1, 3, 6, 10, 15)
        assert wt5.accummulate(add2, 10) == wt(10, 11, 13, 16, 20, 25)
        assert wt5.accummulate(mult2) == wt(1, 2, 6, 24, 120)
        assert wt0.accummulate(add2) == wt()
        assert wt0.accummulate(mult2) == wt()

    def test_wtuple_bind(self) -> None:
        """Test bind (flatmap)"""
        wt0 = WT(range(3, 101))
        l1 = lambda x: 2 * x + 1
        l2 = lambda x: WT(range(2, x + 1)).accummulate(lambda x, y: x + y)
        wt1 = wt0.map(l1)
        wt2 = wt0.bind(l2, FM.CONCAT)
        wt3 = wt0.bind(l2, FM.MERGE)
        wt4 = wt0.bind(l2, FM.EXHAUST)
        assert (wt1[0], wt1[1], wt1[2], wt1[-1]) == (7, 9, 11, 201)
        assert (wt2[0], wt2[1]) == (2, 5)
        assert (wt2[2], wt2[3], wt2[4]) == (2, 5, 9)
        assert (wt2[5], wt2[6], wt2[7], wt2[8]) == (2, 5, 9, 14)
        assert wt2[-1] == wt2[4948] == 5049
        assert MB.idx(wt2, -1).get(42) == wt2[4948] == 5049
        assert MB.idx(wt2, 4949) == MB()
        assert (wt3[0], wt3[1]) == (2, 2)
        assert (wt3[2], wt3[3]) == (2, 2)
        assert (wt3[4], wt3[5]) == (2, 2)
        assert (wt3[96], wt3[97]) == (2, 2)
        assert (wt3[98], wt3[99]) == (5, 5)
        assert MB.idx(wt3, 196) == MB()
        assert (wt4[0], wt4[1], wt4[2]) == (2, 2, 2)
        assert (wt4[95], wt4[96], wt4[97]) == (2, 2, 2)
        assert (wt4[98], wt4[99], wt4[100]) == (5, 5, 5)
        assert (wt4[290], wt4[291], wt4[292]) == (9, 9, 9)
        assert (wt4[293], wt4[294], wt4[295]) == (14, 14, 14)
        assert (wt4[-4], wt4[-3], wt4[-2], wt4[-1]) == (4850, 4949, 4949, 5049)
        assert wt4[-1] == wt4[4948] == 5049
        assert MB.idx(wt2, 4949) == MB()
