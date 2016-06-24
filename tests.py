#!/usr/bin/python

import unittest
from norm import Normalize, Normalize_Base

class TestNormalize(unittest.TestCase):
    def test_define_primary(self):
        norm = Normalize()
        norm.define_primary('foo')
        self.assertEqual(norm.entities, {'foo': {'entities': {}, 'id': 'id'}})
        norm = Normalize()
        norm.define_primary('foo', 'bar')
        self.assertEqual(norm.entities, {'foo': {'entities': {}, 'id': 'bar'}})
        try:
            norm.define_primary('bar')
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

    def test_define_nested_entity(self):
        norm = Normalize()
        try:
            norm.define_nested_entity('foo', 'bar')
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        norm.define_primary('foo')
        norm.define_nested_entity('bar', 'foo')
        self.assertEqual(norm.entities, {'foo': {'entities': {'bar': {
            'id': 'id', 'key': 'foo'}}, 'id': 'id'}})
        norm.define_nested_entity('name', 'key', 'id')
        self.assertEqual(norm.entities, {'foo': {'entities': {'bar': {
            'id': 'id', 'key': 'foo'}, 'name': {'id': 'id', 'key': 'key'}}, 'id': 'id'}})

    def test_parse(self):
        pass

    def test_rename_flds(self):
        pass

    def test_remove_flds(self):
        pass

if __name__ == '__main__':
    unittest.main()
