import base64
from datetime import datetime, timedelta
from typing import Union

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
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


@minecraft_services_blueprint.route('/player/certificates', methods=['POST'])
def player_certificates():
    # FIXME!!!: implement player certificates
    private_key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_pem = private_key.private_bytes(
        encoding=crypto_serialization.Encoding.PEM,
        format=crypto_serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=crypto_serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=crypto_serialization.Encoding.PEM,
        format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo
    )
    message = b"meow"  # FIXME: ???
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    base64_bytes = base64.b64encode(signature)
    base64_signature = base64_bytes.decode('utf-8')

    signature_v2 = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    base64_bytes_v2 = base64.b64encode(signature_v2)
    base64_signature_v2 = base64_bytes_v2.decode('utf-8')

    expires_at = datetime.now() + timedelta(hours=48)
    refreshed_after = datetime.now() + timedelta(hours=40)

    return {
      "keyPair": {
        "privateKey": private_pem,
        "publicKey": public_pem
      },
      "publicKeySignature": base64_signature,
      "publicKeySignatureV2": base64_signature_v2,
      "expiresAt": expires_at.isoformat(),
      "refreshedAfter": refreshed_after.isoformat()
    }
