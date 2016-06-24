#!/usr/bin/python

import unittest
from norm import Normalize, Normalize_Base

class TestNormalizeBase(unittest.TestCase):

    def test_base_data(self):
        norm = Normalize()
        norm.define_primary('foo')
        self.assertEqual(norm._base_data(), ('foo', 'id', {'entities': {'foo':
            {}}, 'results': []}))

    def test_set_nested_id(self):
        data = {'id': 1, 'title': 'One', 'baz': {'id': 1, 'bar': {'id': 1}}}
        norm = Normalize()
        norm._set_nested_id(data, 'bar', 3)
        self.assertEqual(data , {'baz': {'bar': 3, 'id': 1}, 'id': 1, 'title':
            'One'})

    def test_search_dict(self):
        data = {'id': 1, 'title': 'One', 'baz': {'id': 1, 'bar': {'id': 1}}}
        norm = Normalize()
        self.assertEqual(norm._search_dict(data, 'bar'), {'id': 1})

    def test_get_entity_depth(self):
        data = {'id': 1, 'title': 'One', 'baz': {'id': 1, 'bar': {'id': 1}}}
        norm = Normalize()
        self.assertEqual(norm._get_entity_depth('bar', data), 2)

    def test_get_entity_order(self):
        data = {'id': 1, 'title': 'One', 'baz': {'id': 1}}
        norm = Normalize()
        norm.define_primary('foo')
        norm.define_nested_entity('bar', 'baz')
        norm._get_entity_order('foo', data)
        self.assertEqual(norm.entity_order, ['bar'])

    def test_process_data_changes(self):
        data = {'id': 1, 'title': 'One', 'baz': {'id': 1}}
        norm = Normalize()
        norm.define_primary('foo')
        norm.define_nested_entity('bar', 'baz')
        self.assertEqual(norm._process_data_changes('baz', data), data)
        norm.rename_flds('foo', 'title', 'heading')
        self.assertEqual(norm._process_data_changes('foo', data), {'baz':
            {'id': 1}, 'id': 1, 'heading': 'One'})

    def test_process_rename(self):
        data = {'id': 1, 'title': 'One', 'baz': {'id': 1}}
        norm = Normalize()
        norm.define_primary('foo')
        norm.rename_flds('foo', 'title', 'heading')
        norm.rename_flds('foo', 'asdf', 'qwer')
        self.assertEqual(norm._process_data_changes('foo', data), {'baz':
            {'id': 1}, 'id': 1, 'heading': 'One'})

    def test_process_remove(self):
        data = {'id': 1, 'title': 'One', 'baz': {'id': 1}}
        norm = Normalize()
        norm.define_primary('foo')
        norm.remove_flds('foo', 'title')
        norm.remove_flds('foo', 'asdf')
        self.assertEqual(norm._process_data_changes('foo', data), {'baz':
            {'id': 1}, 'id': 1})


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
        norm = Normalize()
        norm.define_primary('test', 'ID')
        try:
            norm.parse([{'id': 1, 'title': 'Some Article'}])
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        norm = Normalize()
        norm.define_primary('test')
        self.assertEqual(norm.parse([{'id': 1, 'title': 'Some Article'}]),
            {'entities': {'test': {1: {'id': 1, 'title': 'Some Article'}}}, 'results': [1]})
        norm = Normalize()
        norm.define_primary('foo')
        norm.define_nested_entity('bar', 'baz')
        norm.define_nested_entity('asdf', 'qwer')
        self.assertEqual(norm.parse([]), None)
        self.assertEqual(norm.parse([{'id': 1, 'title': 'One', 'baz': {'id': 1}},{'id': 2,
            'title': 'Two', 'baz': {'id': 2}}]), {'entities': {'foo': {1: {'baz': 1, 'id': 1,
                'title': 'One'}, 2: {'baz': 2, 'id': 2, 'title': 'Two'}}, 'asdf': {}, 'bar': {1: {'id': 1},
            2: {'id': 2}}}, 'results': [1, 2]})

    def test_rename_flds(self):
        norm = Normalize()
        norm.define_primary('foo')
        norm.rename_flds('foo', 'title', 'heading')
        self.assertEqual(norm.parse([{'id': 1, 'title': 'One'}]), {'entities': {'foo': {1:
            {'heading': 'One', 'id': 1}}}, 'results': [1]})

    def test_remove_flds(self):
        norm = Normalize()
        norm.define_primary('foo')
        norm.remove_flds('foo', 'title')
        self.assertEqual(norm.parse([{'id': 1, 'title': 'One'}]), {'entities': {'foo': {1:
            {'id': 1}}}, 'results': [1]})

    def test_set_entity_order(self):
        norm = Normalize()
        norm.set_entity_order(('foo', 'bar'))
        self.assertEqual(norm.entity_order, ('foo', 'bar'))


if __name__ == '__main__':
    unittest.main()
