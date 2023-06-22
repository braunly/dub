import base64
from datetime import datetime, timedelta
from typing import Union

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from flask import Blueprint, current_app

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


def generate_player_certificates():
    private_key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_pem = private_key.private_bytes(
        encoding=crypto_serialization.Encoding.DER,
        format=crypto_serialization.PrivateFormat.PKCS8,
        encryption_algorithm=crypto_serialization.NoEncryption()
    )

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=crypto_serialization.Encoding.DER,
        format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo
    )

    private_key_str = "-----BEGIN RSA PRIVATE KEY-----" + \
                      base64.encodebytes(private_pem).decode('utf-8') + \
                      "-----END RSA PRIVATE KEY-----"

    public_key_str = "-----BEGIN RSA PUBLIC KEY-----" + \
                     base64.encodebytes(public_pem).decode('utf-8') + \
                     "-----END RSA PUBLIC KEY-----"

    message = b"meow"  # FIXME: UUID ???
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA1()
    )
    base64_bytes = base64.b64encode(signature)

    signature_v2 = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA1()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA1()
    )
    base64_bytes_v2 = base64.b64encode(signature_v2)

    expires_at = datetime.now() + timedelta(days=8)
    refreshed_after = datetime.now() + timedelta(days=7)

    return {
        "keyPair": {
            "privateKey": private_key_str,
            "publicKey": public_key_str
        },
        "publicKeySignature": base64_bytes.decode('utf-8'),
        "publicKeySignatureV2": base64_bytes_v2.decode('utf-8'),
        "expiresAt": expires_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "refreshedAfter": refreshed_after.strftime('%Y-%m-%dT%H:%M:%SZ')
    }


@minecraft_services_blueprint.route('/player/certificates', methods=['POST'])
def player_certificates():
    # FIXME!!!: implement player certificates

    return generate_player_certificates()


@minecraft_services_blueprint.route('/publickeys', methods=['GET'])
def public_keys():
    keys = list()

    player_public_key = generate_player_certificates()['keyPair']['publicKey']

    keys.append({
        "publicKey": base64.b64encode(player_public_key.encode('utf-8')).decode("utf-8")
    })

    return {
        "profilePropertyKeys": keys,
        "playerCertificateKeys": keys
    }
