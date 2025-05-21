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

from __future__ import annotations

from dtools.containers.functional_tuple import FunctionalTuple as FT
from dtools.containers.functional_tuple import functional_tuple as ft
from dtools.containers.maybe import MayBe as MB
from dtools.queues.de import DEQueue as DQ, de_queue as dq


class Test_MB_sequence:
    """Test MayBe sequence class function"""

    def test_no_empties(self) -> None:
        """Test without empty MayBe values"""
        list_mb_int = list(map(MB, range(1, 2501)))
        tuple_mb_int = tuple(map(MB, range(1, 2501)))
        ftuple_mb_int = FT(map(MB, range(1, 2501)))
        dqueue_mb_int = DQ(map(MB, range(1, 2501)))

        mb_list_int = MB.sequence(list_mb_int)
        mb_tuple_int = MB.sequence(tuple_mb_int)
        mb_ftuple_int = MB.sequence(ftuple_mb_int)
        mb_dqueue_int = MB.sequence(dqueue_mb_int)

        assert mb_list_int == MB(list(range(1, 2501)))
        assert mb_tuple_int == MB(tuple(range(1, 2501)))
        assert mb_ftuple_int == MB(FT(range(1, 2501)))
        assert mb_dqueue_int == MB(DQ(range(1, 2501)))

    def test_with_empties(self) -> None:
        """Test with empty MayBe values"""
        list_of_mb_int = [MB[int](), MB(2), MB(3), MB(4)]
        tuple_of_mb_int = MB(1), MB[int](), MB(3), MB(4)
        ftuple_of_mb_int = ft(MB(1), MB(2), MB[int](), MB(4))
        dqueue_of_mb_int = dq(MB(1), MB(2), MB(3), MB[int]())

        mb_list_int = MB.sequence(list_of_mb_int)
        mb_tuple_int = MB.sequence(tuple_of_mb_int)
        mb_ftuple_int = MB.sequence(ftuple_of_mb_int)
        mb_dqueue_int = MB.sequence(dqueue_of_mb_int)

        assert mb_list_int == MB()
        assert mb_tuple_int == MB()
        assert mb_ftuple_int == MB()
        assert mb_dqueue_int == MB()
