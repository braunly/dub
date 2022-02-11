from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, UUID4

from dub.utils.transformer import AccessTokenRequestTransformer
from nidhoggr.core.user import UserProperty
from nidhoggr.utils.transformer import YggdrasilRequestTransformer, JSONResponseTransformer


class SkinState(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class SkinVariant(Enum):
    CLASSIC = 'CLASSIC'
    SLIM = 'SLIM'


class Skin(BaseModel):
    id: UUID4
    state: SkinState = SkinState.ACTIVE
    url: str
    variant: SkinVariant = SkinVariant.CLASSIC

    class Config:
        allow_mutation = False


class Cape(Skin):
    pass


class AccessTokenRequest(BaseModel, AccessTokenRequestTransformer):
    accessToken: UUID4

    class Config:
        allow_mutation = False


class MinecraftProfileResponse(BaseModel, JSONResponseTransformer):
    id: UUID4
    name: str
    skins: List[Skin] = []
    capes: List[Cape] = []

    class Config:
        allow_mutation = False
