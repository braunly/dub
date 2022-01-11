import os
import uuid 

from flask_restful import Resource, reqparse
from mongoengine import Q 

from dub.models import User


class UserCreateResource(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("login", type=str, required=True, default=None)
        parser.add_argument("password", type=str, required=True, default=None)
        args = parser.parse_args()

        # FIXME: дописати вранці
        user = User(
            uuid=str(uuid.uuid4()),
            login=args['login'],
            password=args['password']
        ).save()

        # Create textures folder
        os.mkdir(f'media/{user.uuid}')

        return {"uuid": user.uuid}, 201

class UserGetResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, default=None)
        parser.add_argument("login", type=str, default=None)
        parser.add_argument("email", type=str, default=None)
        parser.add_argument("access", type=str, default=None)
        parser.add_argument("client", type=str, default=None)
        parser.add_argument("server", type=str, default=None)
        args = parser.parse_args()

        print(args)

        user = User.objects(
            Q(uuid=args['uuid']) |
            Q(login=args['login']) |
            Q(email=args['email']) |
            Q(access=args['access']) |
            Q(client=args['client'])
        ).exclude("password").no_cache().first()

        if user:
            resp = user.to_player_dict()
            print(resp)
            return resp, 200
        else:
            return "Not Found", 404

class UserCheckPasswordResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, required=True, default=None)
        parser.add_argument("password", type=str, required=True, default=None)
        args = parser.parse_args()

        print(args)

        user = User.objects(uuid=args['uuid'], password=args['password']).first()

        print(user)

        return {"status": bool(user)}
        

class UserSaveResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, required=True, default=None)
        parser.add_argument("access", type=str, required=True, default=None)
        parser.add_argument("client", type=str, required=True, default=None)
        parser.add_argument("server", type=str, required=True, default=None)
        args = parser.parse_args()

        user = User.objects(uuid=args['uuid']).first()
        user.access = args['access']
        user.client = args['client']
        user.server = args['server']
        user.save()

        return user.to_player_dict(), 200