import os
from base64 import b64decode
from uuid import uuid4

from nidhoggr.core.user import User as nidhoggr_user
from werkzeug.security import generate_password_hash, safe_join

from dub.db.users import Users
from dub.models import User, Texture
from flask import Blueprint, request, current_app

api_blueprint = Blueprint(
    'api',
    __name__,
    url_prefix='/api'
)




@api_blueprint.route('/user/create/', methods=['POST'])
def create_user():
    login = request.json.get("login")
    password = request.json.get("password")

    if User.objects(login__iexact=login).first():
        return {"error": "Already exist"}, 409
    
    try:
        user = User(
            uuid=str(uuid4()),
            login=login,
            email=login,
            password=generate_password_hash(password)
        ).save()
    except Exception as exc:
        print(exc)
        return {"error": "Server error!"}, 500

    # Create textures folder
    os.mkdir(safe_join(current_app.config.get("MEDIA_ROOT"), user.uuid))

    return {"uuid": user.uuid}, 201


@api_blueprint.route('/user/get/', methods=['POST'])
def user_get():
    login = request.json.get("login")
    user = Users.get_user(login=login)
    if isinstance(user, nidhoggr_user):
        return dict(
            login=user.login,
            uuid=user.uuid,
            access=user.access,
            client=user.client,
            serverId=user.server,
            properties=user.properties
        )
    return "", 404


@api_blueprint.route('/user/save/', methods=['POST'])
def user_save():
    uuid = request.json.get("uuid")
    login = request.json.get("login", None)
    password = request.json.get("password", None)

    user = User.objects(uuid=uuid).first()
    if login:
        user.login = login
    if password:
        user.password = generate_password_hash(password)
    user.save()

    return {'status': 'OK'}, 200


@api_blueprint.route('/texture/upload/', methods=['POST'])
def texture_upload():
    uuid = request.json.get("uuid")
    kind = request.json.get("kind")
    data = request.json.get("data")
    metadata = request.json.get("metadata")

    texture = Texture(
        token=uuid,
        deleted=False,
        kind=kind,
        metadata=metadata
    )
    image_path = f'{uuid}/{uuid4()}.png'
    texture.image = image_path

    with open(f'media/{image_path}', 'wb') as f:
        f.write(b64decode(data))

    texture.save()

    return {"message": "Saved texture"}