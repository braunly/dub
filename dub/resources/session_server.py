from datetime import datetime
from json import dumps
from typing import Union

from flask import Blueprint, current_app, request, jsonify

from dub.db.textures import Textures
from dub.db.users import Users
from nidhoggr.core.texture import TextureType, TextureRequest, ComplexTextureResponse
from nidhoggr.core.user import User

from nidhoggr.errors.auth import InvalidProfile
from nidhoggr.errors.common import YggdrasilError
from nidhoggr.errors.session import InvalidServer
from nidhoggr.models.auth import EmptyResponse, NoContent
from nidhoggr.models.session import JoinRequest, HasJoinedRequest, JoinedResponse, ProfileRequest
from nidhoggr.utils.crypto import sign_property
from nidhoggr.utils.decorator import typed
from nidhoggr.utils.repository import handle_status

session_server_blueprint = Blueprint(
    'session_server',
    __name__,
    url_prefix='/sessionserver'
)


@session_server_blueprint.before_request
def convert_get_to_post():
    """ Need for nidhoggr request validation """
    if request.method == 'GET':
        args_dict = request.args.to_dict()
        if 'profile' in request.path:
            args_dict['id'] = request.path.split('/')[-1]
        str_data = dumps(args_dict)
        request.data = bytes(str_data, 'utf-8')


@session_server_blueprint.route('/session/minecraft/join', methods=['POST'])
@typed
def join(req: JoinRequest) -> Union[EmptyResponse, YggdrasilError]:
    user: User = handle_status(Users.get_user(access=req.accessToken))

    if user.synthetic:
        return InvalidProfile

    if req.selectedProfile != user.uuid:
        return InvalidProfile

    user = user.copy(update=dict(server=req.serverId))
    handle_status(Users.save_user(user=user))
    return NoContent


@session_server_blueprint.route('/session/minecraft/hasJoined', methods=['GET'])
@typed
def has_joined(req: HasJoinedRequest) -> Union[JoinedResponse, YggdrasilError]:
    user: User = handle_status(Users.get_user(login=req.username))

    if user.synthetic:
        return InvalidProfile

    if req.serverId != user.server:
        return InvalidServer

    return JoinedResponse(
        id=user.uuid,
        name=user.login,
        properties=user.properties
    )


@session_server_blueprint.route('/session/minecraft/profile/<string:uuid>', methods=['GET'])
@typed
def profile(req: ProfileRequest) -> Union[JoinedResponse, YggdrasilError]:
    user: User = handle_status(Users.get_user(uuid=str(req.id)))
    if user.synthetic:
        return InvalidProfile

    texture_request = TextureRequest(uuid=str(req.id), texture_types=list(TextureType))
    texture_response = handle_status(Textures.get(request=texture_request))

    texture_prop = ComplexTextureResponse(
        timestamp=int(datetime.now().timestamp() * 1000),
        profileId=user.uuid,
        profileName=user.login,
        textures=texture_response.textures
    ).pack()

    raw_props = [texture_prop, *user.properties]

    if req.unsigned:
        properties = raw_props
    else:
        properties = [
            sign_property(private_key=current_app.config.get("PRIVATE_RSA_KEY"), prop=prop)
            for prop
            in raw_props
        ]

    return JoinedResponse(
        id=user.uuid,
        name=user.login,
        properties=properties
    )
