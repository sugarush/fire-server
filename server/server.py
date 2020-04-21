from sanic import Sanic

from sugar_api import CORS, Redis
from sugar_odm import MongoDB


CORS.set_origins('*')

server = Sanic('application-name')
'''
The Sanic server object.
'''

@server.listener('before_server_start')
async def before_server_start(app, loop):
    '''
    Set `MongoDB` and `Redis` event loops to the `Sanic` event loop, then
    set the default `Redis` connection.

    .. attention::

        You should not call this function, it is called automatically.
    '''
    MongoDB.set_event_loop(loop)
    await Redis.set_event_loop(loop)
    Redis.default_connection(host='redis://localhost', minsize=5, maxsize=10)

@server.listener('before_server_stop')
async def before_server_stop(app, loop):
    '''
    Close all `MongoDB` and `Redis` connections before the server stops.
    
    .. attention::

        You should not call this function, it is called automatically.
    '''
    MongoDB.close()
    await Redis.close()
