import bcrypt
import os
import uuid 

from dub.models import User
from flask import Blueprint

api_blueprint = Blueprint(
    'api',
    __name__,
    url_prefix='/api'
)

@api_blueprint.route('/user/create/', methods=['POST'])
def create_user():
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

@api_blueprint.route('/user/save/', methods=['POST'])
def user_save():
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

@api_blueprint.route('/texture/get/', methods=['POST'])
def texture_get():
    parser = reqparse.RequestParser()
    parser.add_argument("uuid", type=str, default=None)
    parser.add_argument("texture_types", type=str, action="append", default=list("SKIN"))
    args = parser.parse_args()

    print(args)

    textures_dict = {}
    textures = Texture.objects(
        token=args['uuid'], 
        kind__in=args['texture_types'],
        deleted=False
    ).order_by("-created").no_cache()

    print(textures)

    for row in textures:
        textures_dict[row.kind] = {
            "url": row.image,
            "metadata": row.metadata
        }
    
    return {"textures": textures_dict}

@api_blueprint.route('/texture/upload/', methods=['POST'])
def texture_upload():
    parser = reqparse.RequestParser()
    parser.add_argument("uuid", type=str, required=True)
    parser.add_argument("kind", type=str, required=True)
    parser.add_argument("data", type=str, required=True)
    parser.add_argument("metadata", type=dict, default=dict())
    args = parser.parse_args()

    print(args)

    texture = Texture(
        token=args['uuid'],
        deleted=False,
        kind=args['kind'],
        metadata=args['metadata']
    )
    image_path = f'{args["uuid"]}/{uuid.uuid4()}.png'
    texture.image = image_path

    with open(f'media/{image_path}', 'wb') as f:
        f.write(b64decode(args['data']))

    texture.save()

    return {"message": "Saved texture"}