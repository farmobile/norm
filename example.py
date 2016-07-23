#!/usr/bin/python

import pprint
from norm import Normalize

if __name__ == '__main__':

    # Example data
    data = [
        {'id': 2, 'title': 'Other Article', 'author': [
            {'id': 10, 'name': 'Jason'},
            {'id': 2, 'name': 'Skippy', 'address': {
                'id': 1, 'street': '100 somewhere lane', 'city': 'somewhereville', 'state': 'Kansas'
                }
            }]
        },
        {'id': 1, 'title': 'Some Article', 'author': {
            'id': 1, 'name': 'Dan', 'address': [
                {'id': 2, 'street': '101 somewhere lane', 'city': 'somewhereville', 'state': 'Kansas'},
                {'id': 6, 'street': '106 somewhere lane', 'city': 'somewhereville', 'state': 'Kansas'}
                ]
            }
        },
        {'id': 3, 'title': 'Some Other Article', 'author': {
            'id': 3, 'name': 'Ben' 
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


    # rename fields for a given entity name
    # norm.rename_flds('addresses', 'street', 'road')

    # remove fields for a given entity name
    # norm.remove_flds('addresses', 'city')

    # entities nested multiple times require the depth to be defined so there is no
    # data loss. If not set, the code will dynamically determine the depth, but only
    # by using the first entry in the data set. If it's missing an entity it won't
    # parse correctly. If your data set is all structured the same (no rows are missing
    # an entity), you can skip this step. Otherwise, entities should be listed in order
    # of the most deeply nested to the least.
    #norm.set_entity_order(('addresses', 'users'))

    # you can swap the primary entity in the data set with a nested entity by setting
    # a nested entity name to swap to with this method. If the requested entity to
    # switch is not defined, a ValueError is raised.
    #norm.swap_primary('addresses')

    # You can create a new one to many key between entities by defining the key
    # relationship you want to create. The first argument is the name for the new key
    # field, the second argument is the reference key used to collect the matching rows
    # (the "one" in one to many), the thrid argument is the entity to add the key to,
    # and the forth argument is the entity to pull the keys from.
    #norm.add_one_to_many_key('user_ids', 'address', 'addresses', 'users')

    # normalize and return the data
    pprint.pprint(norm.parse(data))

    # result:

    #{'entities': {'addresses': {1: {'city': 'somewhereville',
    #               'id': 1,
    #               'state': 'Kansas',
    #               'street': '100 somewhere lane'},
    #           2: {'city': 'somewhereville',
    #               'id': 2,
    #               'state': 'Kansas',
    #               'street': '101 somewhere lane'},
    #           6: {'city': 'somewhereville',
    #               'id': 6,
    #               'state': 'Kansas',
    #               'street': '106 somewhere lane'}},
    #     'articles': {1: {'author': 1,
    #              'id': 1,
    #              'title': 'Some Article'},
    #              2: {'author': [10, 2],
    #              'id': 2,
    #              'title': 'Other Article'},
    #              3: {'author': 3,
    #              'id': 3,
    #              'title': 'Some Other Article'},
    #              4: {'id': 4, 'title': 'Some Other Article'}},
    #     'users': {1: {'address': [2, 6], 'id': 1, 'name': 'Dan'},
    #           2: {'address': 1, 'id': 2, 'name': 'Skippy'},
    #           3: {'id': 3, 'name': 'Ben'},
    #           10: {'id': 10, 'name': 'Jason'}}},
    #'results': [2, 1, 3, 4]}

