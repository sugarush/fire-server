from json import loads, dumps

from dictdiffer import diff
from sanic.log import logger

from sugar_odm import MongoDBModel, Model, Field
from sugar_api import JSONAPIMixin, TimestampMixin


class Thread(Model, TimestampMixin):
    topic = Field(required=True)
    description = Field(required=True)
    created = Field(type='timestamp', required=True)


class Comment(Model, TimestampMixin):
    user = Field(required=True)
    text = Field(required=True)
    created = Field(type='timestamp', required=True)


Comment.add_field('comments', Field(type=[ Comment ]))


class Discussion(MongoDBModel, JSONAPIMixin):

    __rate__ = ( 10, 'secondly' )

    __index__ = [
        {
            'keys': [ ('$**', 'text') ]
        }
    ]

    __acl__ = {
        'administrator': ['all'],
        'user': ['read_all', 'read'],
        '#users': ['read', 'update'],
        'other': ['read_all', 'read'],
        'unauthorized': ['read_all', 'read']
    }

    thread = Field(type=Thread, required=True)
    comments = Field(type=[ Comment ])
    users = Field(type=[ str ])

    async def on_update(self, token, new):
        alpha = self.serialize()
        del alpha['_id']
        beta = type(self)(new).serialize()
        delta = diff(alpha, beta)
        if not all(map(lambda modification: modification == 'add', \
            map(lambda change: change[0], delta))):
            raise Exception('You may only add to this model.')
