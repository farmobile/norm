#!/usr/bin/python

# This code takes nested data structures and flattens them into groups, keyed
# on id fields, and linked to each other by id values. You must first set some
# values to define the output keys and any entities that you want to flatten.
# Nested data that is not defined to be flattened will be left in place

# TODO:
# - move example to its own file
# - fix long lines if any
# - support field rename and remove
# - license
# - benchmark performance

class Normalize_Base:

    def __init__(self):
        '''init data'''

        self.entities = {}
        self.entity_order = []

    def _set_nested_id(self, data, key, idval):
        '''recursively replace nested data with an id'''

        for index in data:
            if index == key:
                data[index] = idval;
                return
            if isinstance(data[index], dict):
                return self._set_nested_id(data[index], key, idval)
        return

    def _search_dict(self, data, key):
        '''recursive search a dict for a key'''

        for index in data:
            if index == key:
                return data[index]
            if isinstance(data[index], dict):
                return self._search_dict(data[index], key)
        return None
        
    def _get_entity_depth(self, entity, data, depth=1):
        '''determine the nesting depth of a key'''

        for index in data:
            if index == entity:
                return depth
            if isinstance(data[index], dict):
                depth += 1
                return self._get_entity_depth(entity, data[index], depth)
        return None

    def _base_data(self):
        '''setup the basic wrapper around the newly normalized data'''

        name = self.entities.keys()[0]
        id_key = self.entities[name]['id']
        new_data = {'results': [], 'entities': {name: {}}}
        for entity in self.entities[name]['entities']:
            new_data['entities'][entity] = {}
        return (name, id_key, new_data)

    def _get_entity_order(self, name, row):
        '''dynamically determine entity depth order from the first row of data'''

        data = []
        for entity in self.entities[name]['entities']:
            key = self.entities[name]['entities'][entity]['key']
            level = self._get_entity_depth(key, row)
            data.append([level, entity])
        data.sort(key=lambda x:x[0])
        self.entity_order = [v[1] for v in data]
        self.entity_order.reverse()


class Normalize(Normalize_Base):

    def define_primary(self, name, id_fld='id'):
        '''used to define the top level entity name used in the results'''
        
        if len(self.entities):
            raise ValueError('Only one primary entity is allowed')
        self.entities[name] = {'id': id_fld, 'entities': {}}

    def set_entity_order(self, order):
        '''set the nested depth order (deepest first)'''

        self.entity_order = order

    def define_nested_entity(self, name, keyval, id_fld='id'):
        '''set a nested entity to be flattend'''

        if not len(self.entities):
            raise ValueError('You must set an entity before setting a nested one')
        self.entities[self.entities.keys()[0]]['entities'][name] = {'id': id_fld, 'key': keyval}

    def remove_flds(entity, flds):
        pass

    def rename_flds(entity, name, new_name):
        pass

    def parse(self, data):
        '''convert data'''

        if not data:
            return None
        name, id_key, new_data = self._base_data()
        if not self.entity_order:
            self._get_entity_order(name, data[0])
        for entry in data:
            if id_key not in entry:
                raise ValueError('Id key "%s" missing from data' % id_key)

            for entity in self.entity_order:
                entity_id = self.entities[name]['entities'][entity]['id']
                entity_key = self.entities[name]['entities'][entity]['key']
                match = self._search_dict(entry, entity_key)
                if not match or entity_id not in match:
                    continue

                new_data['entities'][entity][match[entity_id]] = match
                self._set_nested_id(entry, entity_key, match[entity_id])

            new_data['entities'][name][entry[id_key]] = entry
            new_data['results'].append(entry[id_key])
        return new_data


if __name__ == '__main__':

    # Example data
    data = [
        {'id': 1, 'title': 'Some Article', 'author': {
            'id': 1, 'name': 'Dan', 'address': {
                'id': 2, 'street': '101 somewhere lane', 'city': 'somewhereville', 'state': 'Kansas'
                }
            }
        },
        {'id': 3, 'title': 'Some Other Article', 'author': {
            'id': 1, 'name': 'Ben' 
            }
        },
        {'id': 2, 'title': 'Other Article', 'author': {
            'id': 2, 'name': 'Skippy', 'address': {
                'id': 1, 'street': '100 somewhere lane', 'city': 'somewhereville', 'state': 'Kansas'
                }
            }
        },
        {'id': 4, 'title': 'Some Other Article'}
    ]

    # init
    norm = Normalize()

    # set the top level name
    norm.define_primary('articles')

    # define an entity and key to flatten. Optionally pass the id field as the thrid
    # positional argument, or 'id' will be used instead. Multiple nested entities are
    # recursively searched for.
    norm.define_nested_entity('users', 'author')
    norm.define_nested_entity('addresses', 'address')

    # entities nested multiple times require the depth to be defined so there is no
    # data loss. If not set, the code will dynamically determine the depth, but only
    # by using the first entry in the data set. If it's missing an entity it won't
    # parse correctly. If your data set is all structured the same (no rows are missing
    # an entity), you can skip this step. Otherwise, entities should be listed in order
    # of the most deeply nested to the least.
    norm.set_entity_order(('addresses', 'users'))

    # normalize and return the data
    print norm.parse(data)

    # Results from the example:

    #{
    #    'entities': {
    #        'articles': {
    #            1: {'author': 1, 'id': 1, 'title': 'Some Article'},
    #            2: {'author': 2, 'id': 2, 'title': 'Other Article'},
    #            3: {'author': 1, 'id': 3, 'title': 'Some Other Article'},
    #            4: {'id': 4, 'title': 'Some Other Article'}},
    #        'users': {
    #            1: {'id': 1, 'name': 'Ben'},
    #            2: {'address': 1, 'id': 2, 'name': 'Skippy'}
    #        },
    #        'addresses': {
    #            1: {'city': 'somewhereville', 'state': 'Kansas', 'street': '100 somewhere lane', 'id': 1},
    #            2: {'city': 'somewhereville', 'state': 'Kansas', 'street': '101 somewhere lane', 'id': 2}
    #        }
    #    },
    #    'results': [1, 3, 2, 4]
    #}
