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
from dtools.containers.immutable_list import ImmutableList as IL
from dtools.containers.immutable_list import immutable_list as il
from dtools.containers.maybe import MayBe as MB
from dtools.containers.xor import Xor, RIGHT
from dtools.iterables import FM

class TestImmutableList:
    """ImmutableList test suite"""
    def test_method_returns_copy(self) -> None:
        """Test guarantee"""
        il1 = il(1, 2, 3, 4, 5, 6)
        il2 = il1.map(lambda x: x % 3)
        assert il2[2] == il2[5] == 0
        assert il1[2] is not None and il1[2]*2 == il1[5] == 6

    def test_empty(self) -> None:
        """Test functionality"""
        il1: IL[int] = IL()
        il2: IL[int] = il()
        assert il1 == il2
        assert il1 is not il2
        assert not il1
        assert not il2
        assert len(il1) == 0
        assert len(il2) == 0
        il3 = il1 + il2
        assert il3 == il2 == il1
        assert il3 is not il1
        assert il3 is not il2
        assert not il3
        assert len(il3) == 0
        assert isinstance(il3, IL)
        assert MB.failable_index(il1, 0).get(42) == 42
        assert str(Xor.failable_index(il2, 42)) == str(Xor(IndexError('tuple index out of range'), RIGHT))
        assert str(Xor.failable_index(il2, 42).get_right().get()) == 'tuple index out of range'

    def test_indexing(self) -> None:
        il0: IL[str] = il()
        il1 = il("Emily", "Rachel", "Sarah", "Rebekah", "Mary")
        assert il1[2] == "Sarah"
        assert il1[0] == "Emily"
        assert il1[-1] == "Mary"
        assert il1[1] == "Rachel"
        assert il1[-2] == "Rebekah"
        assert MB.failable_index(il1, -2).get('Buggy') == 'Rebekah'
        assert MB.failable_index(il1, 42).get('Buggy') == 'Buggy'
        assert MB.failable_index(il1, 0).get('Buggy') == 'Emily'
        assert MB.failable_index(il0, 0).get('Buggy') == 'Buggy'

    def test_slicing(self) -> None:
        il0: IL[int] = il()
        il1: IL[int]  = IL(range(0,101,10))
        assert il1 == il(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
        assert il1[2:7:2] == il(20, 40, 60)
        assert il1[8:2:-2] == il(80, 60, 40)
        assert il1[8:] == il(80, 90, 100)
        assert il1[8:-1] == il(80, 90)
        assert il1 == il1[:]
        assert il1[8:130] == il(80, 90, 100)
        assert il0[2:6] == il()

    def test_map(self) -> None:
        il0: IL[int] = il()
        il1: IL[int]  = IL(range(6))
        assert il1 == il(0, 1, 2, 3, 4, 5)

        assert il1.map(lambda t: t*t) == il(0, 1, 4, 9, 16, 25)
        assert il0.map(lambda t: t*t) == il()

    def test_foldl(self) -> None:
        il0: IL[int] = IL()
        il1: IL[int]  = IL(range(1, 6))
        assert il1 == il(1, 2, 3, 4, 5)

        assert il1.foldl(lambda s, t: s*t) == 120
        assert il0.foldl(lambda s, t: s*t, default=42) == 42
        assert il1.foldl(lambda s, t: s*t, 10) == 1200
        assert il0.foldl(lambda s, t: s*t, start=10) == 10

    def test_foldr(self) -> None:
        il0: IL[int] = il()
        il1: IL[int]  = IL(range(1, 4))
        assert il1 == il(1, 2, 3)

        assert il1.foldr(lambda t, s: s*s - t) == 48
        assert il0.foldr(lambda t, s: s*s - t, default = -1) == -1
        assert il1.foldr(lambda t, s: s*s - t, start=5) == 232323
        assert il0.foldr(lambda t, s: s*s - t, 5) == 5

        try:
            _ = il0.foldr(lambda t, s: 5*t + 6*s)
        except ValueError:
            assert True
        else:
            assert False

        try:
            _ = il0.foldl(lambda t, s: 5*t + 6*s)
        except ValueError:
            assert True
        else:
            assert False

    def test_accummulate(self) -> None:
        il0: IL[int] = IL()
        il1: IL[int]  = IL(range(1,6))
        assert il1 == il(1, 2, 3, 4, 5)

        def add(x: int, y: int) -> int:
            return x + y

        assert il1.accummulate(add) == il(1, 3, 6, 10, 15)
        assert il0.accummulate(add) == il()
        assert il1.accummulate(lambda x, y: x+y, 1) == il(1, 2, 4, 7, 11, 16)
        assert il0.accummulate(lambda x, y: x+y, 1) == il(1)

    def test_bind(self) -> None:
        il0: IL[int] = il()
        il1 = il(4, 2, 3, 5)
        il2 = il(4, 2, 0, 3)

        def ff(n: int) -> IL[int]:
            return IL(range(n))

        fm = il1.bind(ff)
        mm = il1.bind(ff, FM.MERGE)
        em = il1.bind(ff, FM.EXHAUST)

        assert fm == il(0, 1, 2, 3, 0, 1, 0, 1, 2, 0, 1, 2, 3, 4)
        assert mm == il(0, 0, 0, 0, 1, 1, 1, 1)
        assert em == il(0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4)

        fm = il2.bind(ff, FM.CONCAT)
        mm = il2.bind(ff, FM.MERGE)
        em = il2.bind(ff, FM.EXHAUST)

        assert fm == il(0, 1, 2, 3, 0, 1, 0, 1, 2)
        assert mm == il()
        assert em == il(0, 0, 0, 1, 1, 1, 2, 2, 3)

        fm = il0.bind(ff, FM.CONCAT)
        mm = il0.bind(ff, FM.MERGE)
        em = il0.bind(ff, FM.EXHAUST)

        assert fm == il()
        assert mm == il()
        assert em == il()
