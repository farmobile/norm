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
        self.new_keys = []
        self.remove_fldvals = {}
        self.rename_fldvals = {}
        self.swap_primary_to = None
        self.ignore_flds = []

    def _set_nested_id(self, data, key, idval, oldval=None):
        '''recursively replace nested data with an id'''

        for index in data:
            if index == key and (oldval == None or data[index] == oldval or data[index] == [oldval]):
                data[index] = idval;
                return True
            if index not in self.ignore_flds and isinstance(data[index], dict):
                if self._set_nested_id(data[index], key, idval, oldval):
                    return True
            elif index not in self.ignore_flds and isinstance(data[index], list):
                for row in data[index]:
                    if index not in self.ignore_flds and isinstance(row, list) or isinstance(row, dict):
                        if self._set_nested_id(row, key, idval, oldval):
                            return True
        return False

    def _search_dict_all(self, data, key, res=None):
        '''recursive search a dict for a all occurences of a key'''

        if not res:
            res = []
        for index in data:
            if index == key:
                res.append(data[index])
            if index not in self.ignore_flds and isinstance(data[index], dict):
                res = self._search_dict_all(data[index], key, res)
            elif index not in self.ignore_flds and isinstance(data[index], list):
                for row in data[index]:
                    if index not in self.ignore_flds and isinstance(row, list) or isinstance(row, dict):
                        res = self._search_dict_all(row, key, res)
        return res

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
        '''process renaming and removing fields from entities'''

        data = self._process_remove(entity, data)
        data = self._process_rename(entity, data)
        return data

    def _process_rename(self, entity, data):
        '''process renaming a field'''

        if entity in self.rename_fldvals:
            for fld in self.rename_fldvals[entity]:
                if fld[0] in data:
                    data[fld[1]] = data[fld[0]]
                    del data[fld[0]]
        return data

    def _process_remove(self, entity, data):
        '''process removing a field from an entity'''

        if entity in self.remove_fldvals:
            for fld in self.remove_fldvals[entity]:
                if fld in data:
                    del data[fld]
        return data

    def _process_primary_swap(self, data):
        '''process a change in primery entity'''

        if self.swap_primary_to not in data['entities']:
            raise ValueError('New primary entity does not exist')
        data['results'] = data['entities'][self.swap_primary_to].keys()
        return data

    def _process_new_keys(self, data):
        '''process new one to many keys'''

        for keyset in self.new_keys:
            if keyset['to'] not in data['entities'] or keyset['from'] not in data['entities']:
                raise ValueError('Invalid entity used in one to many key creation')
            data['entities'][keyset['to']] = self._add_new_key(data['entities'][keyset['to']], data['entities'][keyset['from']],
                keyset['name'], keyset['to_key'])
        return data

    def _add_new_key(self, to_data, from_data, name, to_key):
        for to_id in to_data:
            keys = []
            for from_id in from_data:
                if to_key in from_data[from_id]:
                    if from_data[from_id][to_key] == to_id:
                        keys.append(from_id)
            to_data[to_id][name] = keys

        return to_data

class Normalize(Normalize_Base):

    def swap_primary(self, name):
        '''Enable swapping the primary entity with a nest one'''
        self.swap_primary_to = name

    def define_primary(self, name, id_fld='id'):
        '''used to define the top level entity name used in the results'''
        
        if len(self.entities):
            raise ValueError('Only one primary entity is allowed')
        self.entities[name] = {'id': id_fld, 'entities': {}}

    def set_ignore_keys(self, keys):
        '''set the keys to ignore'''
        self.ignore_flds = keys

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

    def add_one_to_many_key(self, new_key, to_key, to_entity, from_entity):
        '''add a new key to an entity'''

        self.new_keys.append({'name': new_key, 'to_key': to_key, 'to': to_entity, 'from': from_entity})

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
                match = self._search_dict_all(entry, entity_key)
                if isinstance(match, list):
                    ids = []
                    updated = 0
                    for row in match:
                        if isinstance(row, list):
                            ids = []
                            for subrow in row:
                                if entity_id in subrow:
                                    new_data['entities'][entity][subrow[entity_id]] = subrow
                                    ids.append(subrow[entity_id])
                            if ids:
                                if self._set_nested_id(entry, entity_key, ids, subrow):
                                    updated += 1

                        else:
                            if entity_id in row:
                                new_data['entities'][entity][row[entity_id]] = row
                                ids.append(row[entity_id])
                    if len(match) != updated and isinstance(ids, list):
                        self._set_nested_id(entry, entity_key, ids)

            entry = self._process_data_changes(name, entry)
            new_data['entities'][name][entry[id_key]] = entry
            new_data['results'].append(entry[id_key])
        if self.swap_primary_to:
            new_data = self._process_primary_swap(new_data)
        if self.new_keys:
            new_data = self._process_new_keys(new_data)
        return new_data
