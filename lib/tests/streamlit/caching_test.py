# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""st.caching unit tests."""

import unittest
from mock import patch

import streamlit as st
from streamlit.caching import _build_args_mutated_message


class CacheTest(unittest.TestCase):
    @patch.object(st, 'warning')
    def test_args(self, warning):
        called = [False]

        @st.cache
        def f(x):
            called[0] = True
            return x

        self.assertFalse(called[0])
        f(0)

        self.assertTrue(called[0])

        called = [False]  # Reset called

        f(0)
        self.assertFalse(called[0])

        f(1)
        self.assertTrue(called[0])

        warning.assert_not_called()

    @patch.object(st, 'warning')
    def test_modify_args(self, warning):
        @st.cache
        def f(x):
            x[0] = 2

        warning.assert_not_called()

        f([1, 2])

        warning.assert_called_with(_build_args_mutated_message(f))
