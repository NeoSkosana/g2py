"""
Tests for G2Py client
"""

import unittest
from g2py.client import G2Client

class TestG2Client(unittest.TestCase):
    def setUp(self):
        self.client = G2Client()

    def test_initialization(self):
        self.assertIsInstance(self.client, G2Client)