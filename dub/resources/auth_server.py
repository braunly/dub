from typing import Union
from uuid import uuid4

from flask import Blueprint
from nidhoggr.core.user import User
from nidhoggr.errors.auth import InvalidCredentials, InvalidClientToken, InvalidAccessToken
from nidhoggr.errors.common import YggdrasilError, BadRequest
from nidhoggr.models import auth
from nidhoggr.utils.decorator import typed
from nidhoggr.utils.repository import handle_status

from dub.db.users import Users

auth_server_blueprint = Blueprint(
    'auth_server',
    __name__,
    url_prefix='/authserver'
)


@auth_server_blueprint.route('/authenticate', methods=['POST'])
@typed
def authenticate(
        req: auth.AuthenticationRequest
) -> Union[auth.AuthenticationResponse, YggdrasilError]:
    print(req.json())

    user: User = handle_status(Users.get_user(email=req.username, login=req.username))
    print(user)
    if user.synthetic:
        return InvalidCredentials

    password_check = handle_status(Users.check_password(clean=req.password, uuid=str(user.uuid)))
    if not password_check.status:
        return InvalidCredentials

    # Need to implement session reset command in bot
    # if req.clientToken is not None and user.client is not None and user.client != req.clientToken:
    #     return InvalidClientToken

    user = user.copy(update=dict(access=uuid4(), client=req.clientToken))

    if req.agent is not None:
        profile = auth.Profile(id=user.uuid, name=user.login)
        selected_profile, available_profiles = profile, [profile]
    else:
        selected_profile = available_profiles = None

    if req.requestUser:
        user_instance = auth.UserInstance(id=user.uuid, properties=user.properties)
    else:
        user_instance = None

    handle_status(Users.save_user(user=user))

    return auth.AuthenticationResponse(
        accessToken=user.access,
        clientToken=user.client,
        availableProfiles=available_profiles,
        selectedProfile=selected_profile,
        user=user_instance,
    )


@auth_server_blueprint.route('/refresh', methods=['POST'])
@typed
def refresh(req: auth.RefreshRequest) -> Union[auth.RefreshResponse, YggdrasilError]:
    user: User = handle_status(Users.get_user(client=req.clientToken))

    if user.synthetic:
        return BadRequest

    user = user.copy(update=dict(access=uuid4()))
    selected_profile = auth.Profile(id=user.uuid, name=user.login)

    if req.requestUser:
        user_instance = auth.UserInstance(id=user.uuid, properties=user.properties)
    else:
        user_instance = None

    handle_status(Users.save_user(user=user))

    return auth.RefreshResponse(
        accessToken=user.access,
        clientToken=user.client,
        selectedProfile=selected_profile,
        user=user_instance,
    )


@auth_server_blueprint.route('/validate', methods=['POST'])
@typed
def validate(req: auth.ValidateRequest) -> Union[auth.EmptyResponse, YggdrasilError]:
    user: User = handle_status(Users.get_user(access=req.accessToken))

    if user.synthetic:
        return InvalidAccessToken

    if req.clientToken is not None and req.clientToken != user.client:
        return InvalidClientToken

    return auth.NoContent


@auth_server_blueprint.route('/invalidate', methods=['POST'])
@typed
def invalidate(req: auth.InvalidateRequest) -> Union[auth.EmptyResponse, YggdrasilError]:
    user: User = handle_status(Users.get_user(access=req.accessToken))

    if user.synthetic:
        return InvalidAccessToken

    if req.clientToken != user.client:
        return InvalidClientToken

    user = user.copy(update=dict(access=None))

    handle_status(Users.save_user(user=user))

    return auth.NoContent


@auth_server_blueprint.route('/signout', methods=['POST'])
@typed
def sign_out(req: auth.SignOutRequest) -> Union[auth.EmptyResponse, YggdrasilError]:
    user: User = handle_status(Users.get_user(email=req.username))

    if user.synthetic:
        return InvalidCredentials

    password_check = handle_status(Users.check_password(clean=req.password, uuid=user.uuid))
    if not password_check.status:
        return InvalidCredentials

    user = user.copy(update=dict(access=None))

    handle_status(Users.save_user(user=user))

    return auth.NoContent


