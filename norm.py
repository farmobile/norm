#!/usr/bin/python

# This code takes nested data structures and flattens them into groups, keyed
# on id fields, and linked to each other by id values. You must first set some
# values to define the output keys and any entities that you want to flatten.
# Nested data that is not defined to be flattened will be left in place

class Normalize_Base:

    def __init__(self):
        '''init data'''

        self.entities = {}
        self.entity_order = []
        self.remove_fldvals = {}
        self.rename_fldvals = {}
        self.swap_primary_to = None

    def _set_nested_id(self, data, key, idval):
        '''recursively replace nested data with an id'''

        for index in data:
            if index == key:
                data[index] = idval;
                return
            if isinstance(data[index], dict):
                self._set_nested_id(data[index], key, idval)
            elif isinstance(data[index], list):
                for row in data[index]:
                    self._set_nested_id(row, key, idval)

    def _search_dict(self, data, key):
        '''recursive search a dict for a key'''

        for index in data:
            if index == key:
                return data[index]
            if isinstance(data[index], dict):
                res = self._search_dict(data[index], key)
                if res:
                    return res
            elif isinstance(data[index], list):
                for row in data[index]:
                    res = self._search_dict(row, key)
                    if res:
                        return res
        return None
        
    def _get_entity_depth(self, entity, data, depth=1):
        '''determine the nesting depth of a key'''

        for index in data:
            if index == entity:
                return depth
            if isinstance(data[index], dict):
                depth += 1
                return self._get_entity_depth(entity, data[index], depth)
            elif isinstance(data[index], list):
                for row in data[index]:
                    res = self._get_entity_depth(entity, row, (depth + 1))
                    if res and res > depth:
                        return res
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
        '''determine entity depth order from the first row of data'''

        data = []
        for entity in self.entities[name]['entities']:
            key = self.entities[name]['entities'][entity]['key']
            level = self._get_entity_depth(key, row)
            data.append([level, entity])
        data.sort(key=lambda x:x[0])
        self.entity_order = [v[1] for v in data]
        self.entity_order.reverse()

    def _process_data_changes(self, entity, data):
        data = self._process_remove(entity, data)
        data = self._process_rename(entity, data)
        return data

    def _process_rename(self, entity, data):
        if entity in self.rename_fldvals:
            for fld in self.rename_fldvals[entity]:
                if fld[0] in data:
                    data[fld[1]] = data[fld[0]]
                    del data[fld[0]]
        return data

    def _process_remove(self, entity, data):
        if entity in self.remove_fldvals:
            for fld in self.remove_fldvals[entity]:
                if fld in data:
                    del data[fld]
        return data

    def _process_primary_swap(self, data):
        if self.swap_primary_to not in data['entities']:
            raise ValueError('New primary entity does not exist')
        data['results'] = data['entities'][self.swap_primary_to].keys()
        return data


class Normalize(Normalize_Base):

    def swap_primary(self, name):
        '''Enable swapping the primary entity with a nest one'''
        self.swap_primary_to = name

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
            raise ValueError('You must set the primary first')
        self.entities[self.entities.keys()[0]]['entities'][name] = {
            'id': id_fld, 'key': keyval}

    def remove_flds(self, entity, fld):
        '''remove a field from a defined entity'''

        if entity in self.remove_fldvals:
            self.remove_fldvals[entity].append(fld)
        else:
            self.remove_fldvals[entity] = [fld]

    def rename_flds(self, entity, name, new_name):
        '''rename a field for an entity'''

        if entity in self.rename_fldvals:
            self.rename_fldvals[entity].append((name, new_name))
        else:
            self.rename_fldvals[entity] = [(name, new_name)]

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
                if match and entity_id in match:
                    match = self._process_data_changes(entity, match)
                    new_data['entities'][entity][match[entity_id]] = match
                    self._set_nested_id(entry, entity_key, match[entity_id])
                elif isinstance(match, list):
                    ids = []
                    for row in match:
                        if entity_id in row:
                            new_data['entities'][entity][row[entity_id]] = row
                            ids.append(row[entity_id])
                    if ids:
                        self._set_nested_id(entry, entity_key, ids)

            entry = self._process_data_changes(name, entry)
            new_data['entities'][name][entry[id_key]] = entry
            new_data['results'].append(entry[id_key])
        if self.swap_primary_to:
            return self._process_primary_swap(new_data)
        return new_data
