#!/usr/bin/python

data = [
        {'id': 1, 'title': 'Some Article', 'author': { 'id': 1, 'name': 'Dan', 'address': { 'id': 1, 'street': '1008 allen ct', 'city': 'lawrence', 'state': 'Kansas'}}},
        {'id': 3, 'title': 'Some Other Article', 'author': { 'id': 1, 'name': 'Ben' }},
        {'id': 2, 'title': 'Other Article', 'author': { 'id': 2, 'name': 'Skippy', 'address': { 'id': 2, 'street': '1009 allen ct', 'city': 'lawrence', 'state': 'Kansas'}}}
]

class Normalize:

    def __init__(self):
        self.entities = {}
        self.entity_order = []

    def define_entity(self, name, id_fld='id'):
        if len(self.entities):
            raise ValueError('Only one primary entity is allowed')
        self.entities[name] = {'id': id_fld, 'entities': {}}

    def search_entities(self, data, key):
        for index in data:
            if index == key:
                return data[index]['entities']
            return self.search_entities(data[index]['entities'], key)
        return None
       
    def set_nested_id(self, data, key, idval):
        for index in data:
            if index == key:
                data[index] = idval;
                return
            if isinstance(data[index], dict):
                return self.set_nested_id(data[index], key, idval)
        return

    def search_dict(self, data, key):
        for index in data:
            if index == key:
                return data[index]
            if isinstance(data[index], dict):
                return self.search_dict(data[index], key)
        return None
        
    def get_entity_depth(self, entity, data, depth=1):
        for index in data:
            if index == entity:
                return depth
            if isinstance(data[index], dict):
                depth += 1
                return self.get_entity_depth(entity, data[index], depth)
        return None

    def define_nested_entity(self, name, keyval, id_fld='id'):
        if not len(self.entities):
            raise ValueError('You must set an entity before setting a nested one')
        self.entities[self.entities.keys()[0]]['entities'][name] = {'id': id_fld, 'key': keyval}

    def set_entity_order(self, order):
        self.entity_order = order

    def base_data(self):
        name = self.entities.keys()[0]
        id_key = self.entities[name]['id']
        new_data = {'results': [], 'entities': {name: {}}}
        for entity in self.entities[name]['entities']:
            new_data['entities'][entity] = {}
        return (name, id_key, new_data)

    def get_entity_order(self, name, row):
        data = []
        for entity in self.entities[name]['entities']:
            key = self.entities[name]['entities'][entity]['key']
            level = self.get_entity_depth(key, row)
            data.append([level, entity])
        data.sort(key=lambda x:x[0])
        self.entity_order = [v[1] for v in data]
        self.entity_order.reverse()

    def parse(self, data):
        if not data:
            return None
        name, id_key, new_data = self.base_data()
        if not self.entity_order:
            self.get_entity_order(name, data[0])
        for entry in data:
            if id_key not in entry:
                raise ValueError('Id key "%s" missing from data' % id_key)

            for entity in self.entity_order:
                entity_id = self.entities[name]['entities'][entity]['id']
                entity_key = self.entities[name]['entities'][entity]['key']
                match = self.search_dict(entry, entity_key)
                if not match or entity_id not in match:
                    continue

                new_data['entities'][entity][match[entity_id]] = match
                self.set_nested_id(entry, entity_key, match[entity_id])

            new_data['entities'][name][entry[id_key]] = entry
            new_data['results'].append(entry[id_key])
        return new_data


norm = Normalize()
norm.define_entity('articles')
norm.define_nested_entity('users', 'author')
norm.define_nested_entity('addresses', 'address')
norm.set_entity_order(('addresses', 'users'))
print norm.parse(data)

#{
#    'entities': {
#        'articles': {
#            1: {'author': 1, 'id': 1, 'title': 'Some Article'},
#            2: {'author': 2, 'id': 2, 'title': 'Other Article'}},
#        'users': {
#            1: {'address': 1, 'id': 1, 'name': 'Dan'},
#            2: {'address': 2, 'id': 2, 'name': 'Skippy'}},
#        'addresses': {
#            1: {'city': 'lawrence', 'state': 'Kansas', 'street': '1008 allen ct', 'id': 1},
#            2: {'city': 'lawrence', 'state': 'Kansas', 'street': '1009 allen ct', 'id': 2}
#        }
#    },
#    'results': [1, 2]
#}
