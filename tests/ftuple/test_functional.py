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
from dtools.tuples.ftuple import FTuple as FT
# from dtools.tuples.ftuple import f_tuple as ft
from dtools.queues.restrictive import FIFOQueue as FQ
from dtools.queues.restrictive import fifo_queue as fq
from dtools.queues.splitends.splitend import SplitEnd as SE
from dtools.fp.iterables import FM
from dtools.fp.err_handling import MB


class TestFP:
    """FP test of FTuple with other datastructures"""
    def test_fold[S](self) -> None:
        """Test folding"""
        l1 = lambda x, y: x + y
        l2 = lambda x, y: x * y

        def push_fq_from_left(q: FQ[S], d: S) -> FQ[S]:
            q.push(d)
            return q

        def push_fq_from_right(d: S, q: FQ[S]) -> FQ[S]:
            q.push(d)
            return q

        def push_se(se: SE[S], d: S) -> SE[S]:
            se.push(d)
            return se

        ft0: FT[int] = FT()
        ft5: FT[int] = FT(1, 2, 3, 4, 5)
        se5 = SE(1, 2, 3, 4, 5)

        assert se5.peak() == 5
        assert ft5[1] == 2
        assert ft5[4] == 5

        assert ft0.foldl(l1, 42) == 42
        assert ft0.foldr(l1, 42) == 42
        assert ft5.foldl(l1) == 15
        assert ft5.foldl(l1, 0) == 15
        assert ft5.foldl(l1, 10) == 25
        assert ft5.foldl(l2, 1) == 120
        assert ft5.foldl(l2, 10) == 1200
        assert ft5.foldr(l1) == 15
        assert ft5.foldr(l1, 0) == 15
        assert ft5.foldr(l1, 10) == 25
        assert ft5.foldr(l2, 1) == 120
        assert ft5.foldr(l2, 10) == 1200

        assert ft0 == FT()
        assert ft5 == FT(1, 2, 3, 4, 5)

        fq1: FQ[int] = FQ()
        fq2: FQ[int] = FQ()
        assert ft5.foldl(push_fq_from_left, fq1.copy()) == fq(1, 2, 3, 4, 5)
        assert ft0.foldl(push_fq_from_left, fq2.copy()) == fq()
        assert ft5.foldr(push_fq_from_right, fq1.copy()) == fq(5, 4, 3, 2, 1)
        assert ft0.foldr(push_fq_from_right, fq2.copy()) == fq()

        fq5: FQ[int] = FQ()
        fq6 = FQ[int]()
        fq7: FQ[int] = FQ()
        fq8 = FQ[int]()
        assert ft5.foldl(push_fq_from_left, fq5) == fq(1, 2, 3, 4, 5)
        assert ft5.foldl(push_fq_from_left, fq6) == fq(1, 2, 3, 4, 5)
        assert ft0.foldl(push_fq_from_left, fq7) == fq()
        assert ft0.foldl(push_fq_from_left, fq8) == fq()
        assert fq5 == fq6 == fq(1, 2, 3, 4, 5)
        assert fq7 == fq8 == fq()

        assert se5.fold(l1) == 15
        assert se5.fold(l1, 10) == 25
        assert se5.fold(l2) == 120
        assert se5.fold(l2, 10) == 1200
        se_temp = se5.copy()
        se_temp.pop()
        se5_rev = se_temp.fold(push_se, SE(se5.peak()))
        assert se5_rev == SE(5, 4, 3, 2, 1)
        assert se5.fold(l1) == 15
        assert se5.fold(l1, 10) == 25

        assert ft5.accummulate(l1) == FT(1, 3, 6, 10, 15)
        assert ft5.accummulate(l1, 10) == FT(10, 11, 13, 16, 20, 25)
        assert ft5.accummulate(l2) == FT(1, 2, 6, 24, 120)
        assert ft0.accummulate(l1) == FT()
        assert ft0.accummulate(l2) == FT()

    def test_ftuple_bind(self) -> None:
        """Test bind (flatmap)"""
        ft0 = FT(*range(3, 101))
        l1 = lambda x: 2 * x + 1
        l2 = lambda x: FT(*range(2, x + 1)).accummulate(lambda x, y: x + y)
        ft1 = ft0.map(l1)
        ft2 = ft0.bind(l2, FM.CONCAT)
        ft3 = ft0.bind(l2, FM.MERGE)
        ft4 = ft0.bind(l2, FM.EXHAUST)
        assert (ft1[0], ft1[1], ft1[2], ft1[-1]) == (7, 9, 11, 201)
        assert (ft2[0], ft2[1]) == (2, 5)
        assert (ft2[2], ft2[3], ft2[4]) == (2, 5, 9)
        assert (ft2[5], ft2[6], ft2[7], ft2[8]) == (2, 5, 9, 14)
        assert ft2[-1] == ft2[4948] == 5049
        assert MB.idx(ft2, -1).get(42) == ft2[4948] == 5049
        assert MB.idx(ft2, 4949) == MB()
        assert (ft3[0], ft3[1]) == (2, 2)
        assert (ft3[2], ft3[3]) == (2, 2)
        assert (ft3[4], ft3[5]) == (2, 2)
        assert (ft3[96], ft3[97]) == (2, 2)
        assert (ft3[98], ft3[99]) == (5, 5)
        assert MB.idx(ft3, 196) == MB()
        assert (ft4[0], ft4[1], ft4[2]) == (2, 2, 2)
        assert (ft4[95], ft4[96], ft4[97]) == (2, 2, 2)
        assert (ft4[98], ft4[99], ft4[100]) == (5, 5, 5)
        assert (ft4[290], ft4[291], ft4[292]) == (9, 9, 9)
        assert (ft4[293], ft4[294], ft4[295]) == (14, 14, 14)
        assert (ft4[-4], ft4[-3], ft4[-2], ft4[-1]) == (4850, 4949, 4949, 5049)
        assert ft4[-1] == ft4[4948] == 5049
        assert MB.idx(ft2, 4949) == MB()
