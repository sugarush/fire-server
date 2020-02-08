from server import server

from authentication import Authentication

from models.user import User

from models.discussion import Discussion


server.blueprint(Authentication.resource(url_prefix='/v1'))

server.blueprint(User.resource(url_prefix='/v1'))

server.blueprint(Discussion.resource(url_prefix='/v1', realtime=True))
