from typing import Union

from flask import Blueprint

from dub.db.textures import Textures
from dub.models.http.minecraft_services import Skin, Cape
from nidhoggr.core.texture import TextureRequest, TextureType, SimpleTextureResponse

from nidhoggr.core.user import User

from dub.db.users import Users
from dub.models.http import AccessTokenRequest, MinecraftProfileResponse
from nidhoggr.errors.common import YggdrasilError
from nidhoggr.utils.decorator import typed
from nidhoggr.utils.repository import handle_status

minecraft_services_blueprint = Blueprint(
    'minecraft_services',
    __name__,
    url_prefix='/minecraftservices'
)


@minecraft_services_blueprint.route('/minecraft/profile', methods=['GET'])
@typed
def profile(req: AccessTokenRequest) -> Union[MinecraftProfileResponse, YggdrasilError]:
    user: User = handle_status(Users.get_user(access=req.accessToken))

    texture_request = TextureRequest(uuid=user.uuid, texture_types=list(TextureType))
    texture_response: SimpleTextureResponse = handle_status(Textures.get(request=texture_request))

    skins = []
    if TextureType.SKIN.value in texture_response.textures:
        skins = [Skin(
            # maybe this must be a texture id
            id=user.uuid,
            url=texture_response.textures[TextureType.SKIN.value].url
        )]

    capes = []
    if TextureType.CAPE.value in texture_response.textures:
        capes = [Cape(
            # maybe this must be a texture id
            id=user.uuid,
            url=texture_response.textures[TextureType.CAPE.value].url
        )]

    return MinecraftProfileResponse(
        id=user.uuid,
        name=user.login,
        skins=skins,
        capes=capes
    )


@minecraft_services_blueprint.route('/player/attributes', methods=['GET'])
def player_attributes():
    return {
      "privileges": {
        "onlineChat": {
          "enabled": True
        },
        "multiplayerServer": {
          "enabled": True
        },
        "multiplayerRealms": {
          "enabled": False
        },
        "telemetry": {
          "enabled": False
        }
      },
      "profanityFilterPreferences": {
        "profanityFilterOn": False
      }
    }
