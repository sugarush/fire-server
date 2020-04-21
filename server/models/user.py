import os
import hashlib
from uuid import uuid4
from datetime import datetime

import aiohttp
from sanic.log import logger

from sugar_document import Document
from sugar_odm import MongoDBModel, Field
from sugar_api import JSONAPIMixin, TimestampMixin


class User(MongoDBModel, JSONAPIMixin, TimestampMixin):
    '''
    A `user` model.
    '''

    __rate__ = ( 5, 'secondly' )

    __acl__ = {
        'self': ['read', 'update', 'delete', 'subscribe', 'acquire'],
        'administrator': ['all'],
        'other': ['read', 'subscribe'],
        'unauthorized': ['create']
    }

    __get__ = {
        'username': ['self', 'administrator'],
        'password': [ ],
        'groups': ['administrator'],
        'email': ['self', 'administrator'],
        'secret': [ ],
        'key': ['self'],
        'created': ['self','administrator'],
        'login': ['self', 'administrator']

    }

    __set__ = {
        'username': ['self', 'administrator', 'unauthorized'],
        'password': ['self', 'administrator', 'unauthorized'],
        'email': ['self', 'administrator', 'unauthorized'],
        'groups': ['administrator'],
        'secret': [ ],
        'key': ['self'],
        'created': [ ],
        'login': [ ]
    }

    __index__ = [
        {
            'keys': [ ('username', 1), ('email', 1) ],
            'options': {
                'unique': True
            }
        }

    ]

    username = Field(required=True)
    '''
    The user's `username`.
    '''

    password = Field(required=True, validated='validate_password', computed='encrypt_password', validated_before_computed=True)
    '''
    The user's `password`.
    '''

    email = Field(required=True)
    '''
    The user's `email`.
    '''

    secret = Field()
    '''
    The user's `secret`.
    '''

    key = Field(validated='confirm_key')
    '''
    The user's validation `key`.
    '''

    groups = Field(type=list, default=lambda: [ 'users' ], default_empty=True)
    '''
    A list of `groups` that the user belongs to.
    '''

    created = Field(type='timestamp', default=lambda: datetime.utcnow(), default_empty=True, default_type=True)
    '''
    Stores the date the user was created.
    '''

    updated = Field(type='timestamp', default=lambda: datetime.utcnow(), default_type=True)
    '''
    Stores when the user was last updated.
    '''

    login = Field(type='timestamp')
    '''
    Stores when the user last logged in.
    '''

    async def on_create(self, token):
        '''
        Verify that no existing user has taken the `username` or `email`, then
        generate a `secret` and send a confirmation email.
        '''
        if await self.find_one({ 'username': self.username }):
            raise Exception(f'Username {self.username} already exists.')

        if await self.find_one({ 'email': self.email }):
            raise Exception(f'Email {self.email} already taken.')

        self.secret = str(uuid4())
        await self.send_confirmation_email()

    async def on_update(self, token, attributes):
        '''
        Verify that the new `username` and `email` are not already taken. If
        not, generate a new `secret`, replacing the old one, set the `key` to
        `None` and send a confirmation email.
        '''
        username = attributes.get('username')
        user = await self.find_one({ 'username': username })
        if username and user and not (user.id == self.id):
            raise Exception(f'Username {username} already taken.')

        email = attributes.get('email')
        user = await self.find_one({ 'email': email })
        if email:
            if user and not (user.id == self.id):
                raise Exception(f'Email {email} already taken.')
            elif not (email == self.email):
                self.key = None
                self.secret = str(uuid4())
                await self.send_confirmation_email()

        key = attributes.get('key')
        if key == '$action-resend-key':
            attributes['key'] = self.key
            await self.send_confirmation_email()

        self.updated = datetime.utcnow()

    def validate_password(self, value):
        '''
        Used by the `password` field to validate a user's password.
        '''
        if len(self.password) < 8:
            raise Exception('Password length must be at least 8 characters.')

    def encrypt_password(self):
        '''
        Used by the `password` field to encrypt a user's password.
        '''
        if self.password == 'hashed-':
            raise Exception('Invalid password.')

        if self.password.startswith('hashed-'):
            return self.password

        return f'hashed-{hashlib.sha256(self.password.encode()).hexdigest()}'

    def confirm_key(self, key):
        '''
        Used by the `key` field to confirm a key.
        '''
        if not key == 'None' and key and not \
            (key == hashlib.sha256(self.secret.encode()).hexdigest()):
                raise Exception('Invalid key.')

    async def send_confirmation_email(self):
        '''
        Send a confirmation email.
        '''
        url = os.getenv('SUGAR_MAILGUN_URL')
        key = os.getenv('SUGAR_MAILGUN_API_KEY')
        sender = os.getenv('SUGAR_MAILGUN_FROM', 'Sugar Server <sugar@server.com>')

        if not (url and key):
            logger.warn('User.send_confirmation_email: Missing one or more environment variables.')
            return None

        async with aiohttp.ClientSession() as session:

            url = f'{url}/messages'

            data = {
                'from': sender,
                'to': [ self.email ],
                'subject': 'Account Confirmation',
                'text': f'{hashlib.sha256(self.secret.encode()).hexdigest()}'
            }

            auth = aiohttp.BasicAuth('api', key)

            async with session.request('POST', url, auth=auth, data=data) as response:
                json = Document(await response.json())
                if json.message == '\'to\' parameter is not a valid address. please check documentation':
                    raise Exception('Invalid email address.')
                elif not json.message == 'Queued. Thank you.':
                    raise Exception(f'Failed to send confirmation email: {json.message}')
