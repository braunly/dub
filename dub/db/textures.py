from typing import Union

from dub.models import db
from nidhoggr.core.response import ErrorResponse, TextureStatusResponse
from nidhoggr.core.texture import TextureRequest, TextureUploadRequest, SimpleTextureResponse
from nidhoggr.core.repository import BaseTextureRepo


class Textures(BaseTextureRepo):
    @staticmethod
    def get(*, request: TextureRequest) -> Union[ErrorResponse, SimpleTextureResponse]:
        textures_dict = {}
        textures = db.Texture.objects(
            token=str(request.uuid),
            kind__in=[t.value for t in request.texture_types],
            deleted=False
        ).order_by("-created").no_cache()

        for row in textures:
            textures_dict[row.kind] = {
                "url": row.image,
                "metadata": row.metadata
            }

        return SimpleTextureResponse(
            textures=textures_dict
        )

    def upload(self, *, request: TextureUploadRequest) -> Union[ErrorResponse, TextureStatusResponse]:
        pass

    def clear(self, *, request: TextureRequest) -> Union[ErrorResponse, TextureStatusResponse]:
        pass