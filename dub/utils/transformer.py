from flask import request
from pydantic import BaseModel, UUID4

from nidhoggr.utils.transformer import AbstractRequestTransformer


class AccessTokenRequestTransformer(AbstractRequestTransformer):
    @classmethod
    def transform(cls: BaseModel, *args, **kwargs):
        token = request.headers.get('Authorization').replace('Bearer ', '')
        return cls.parse_obj({"accessToken": UUID4(token)})
