from email.policy import default
import bcrypt
import os
import uuid 

from flask_restful import Resource, reqparse
from mongoengine import Q
from dub.models import User


class UserCreateResource(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("login", type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()

        encrypted_password = bcrypt.hashpw(
            args['password'].encode('utf8'), 
            bcrypt.gensalt()
        )

        if User.objects(login__iexact=args['login']).first():
            return {"error": "Already exist"}, 409
        
        try:
            user = User(
                uuid=str(uuid.uuid4()),
                login=args['login'],
                email=args['login'],
                password=encrypted_password
            ).save()
        except Exception as exc:
            print(exc)
            return {"error": "Server error!"}, 500

        # Create textures folder
        os.mkdir(f'media/{user.uuid}')

        return {"uuid": user.uuid}, 201

class UserGetResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, store_missing=False)
        parser.add_argument("login", type=str, store_missing=False)
        parser.add_argument("email", type=str, store_missing=False)
        parser.add_argument("access", type=str, store_missing=False)
        parser.add_argument("client", type=str, store_missing=False)
        parser.add_argument("server", type=str, store_missing=False)
        args = parser.parse_args()
        print(args)

        query_set = User.objects.none()

        for key in args:
            if args[key]:
                query_set = User.objects(Q(**{f"{key}__iexact": args[key]}) | query_set._query_obj)

        user = query_set.exclude("password").no_cache().first()

        if user:
            resp = user.to_player_dict()
            print(resp)
            return resp, 200
        else:
            return User(
                    uuid="8de67985-09c5-443b-be60-8fa552560e0e",
                    login="empty",
                    email="empty@example.com",
                    synthetic=True
                ).to_player_dict(), 200

class UserCheckPasswordResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()

        print(args)

        try:
            user = User.objects(uuid=args['uuid']).first()
            print(user.uuid)
            print(user.password)
            if user and bcrypt.checkpw(args['password'].encode('utf8'), user.password.encode('utf8')):
                return {"status": True}, 200
        except Exception as exc:
            print(exc)
            return {'reason': 'Server error!', 'exception': str(exc)}, 400

        return {"status": False}, 200
        

class UserSaveResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, required=True)
        parser.add_argument("return_user", type=bool, default=True)
        parser.add_argument("login", type=str, store_missing=False)
        parser.add_argument("password", type=str, store_missing=False)
        parser.add_argument("email", type=str, store_missing=False)
        parser.add_argument("access", type=str, store_missing=False)
        parser.add_argument("client", type=str, store_missing=False)
        parser.add_argument("server", type=str, store_missing=False)
        args = parser.parse_args()

        print(args)

        user = User.objects(uuid=args['uuid']).first()
        if 'access' in args:
            user.access = args['access']
        if 'client' in args:
            user.client = args['client']
        if 'server' in args:
            user.server = args['server']
        if 'login' in args:
            user.login = args['login']
        if 'email' in args:
            user.email = args['email']
        if 'password' in args:
            encrypted_password = bcrypt.hashpw(
                args['password'].encode('utf8'), 
                bcrypt.gensalt()
            )
            user.password = encrypted_password.decode('utf8')
        user.save()

        if args['return_user']:
            user.password = None
            return user.to_player_dict(), 200
        else:
            return {'status': 'OK'}, 200

class UserDeleteResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, required=True)
        parser.add_argument("token", type=str, required=True, default="123")
        args = parser.parse_args()

        if args['token'] !=  "Magic":
            return "", 200

        User.objects(uuid=args['uuid']).delete()
        return {'status': 'OK'}, 200