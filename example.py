#!/usr/bin/python

from norm import Normalize

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
