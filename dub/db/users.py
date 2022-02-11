from typing import Dict, Union
from uuid import UUID

from mongoengine import Q, OperationError
from werkzeug.security import check_password_hash

from dub.models import db
from nidhoggr.core.user import User
from nidhoggr.core.response import ErrorResponse, StatusResponse
from nidhoggr.core.repository import BaseUserRepo


def _mongo_to_user(*, db_user: db.User) -> User:
    return User(
        uuid=db_user.uuid,
        login=db_user.login,
        email=db_user.email,
        access=db_user.access,
        client=db_user.client,
        server=db_user.server,
        properties=db_user.properties,
        synthetic=db_user.synthetic
    )


class Users(BaseUserRepo):
    @staticmethod
    def get_user(**kw: Dict[str, Union[str, UUID]]) -> Union[ErrorResponse, User]:
        query_set = db.User.objects.none()

        for key in kw:
            if kw[key]:
                value = kw[key]
                if isinstance(value, UUID):
                    value = str(value)
                query_set = db.User.objects(Q(**{f"{key}__iexact": value}) | query_set._query_obj)

        try:
            db_user = query_set.no_cache().first()
            if not db_user:
                return BaseUserRepo.EMPTY_USER
            return _mongo_to_user(db_user=db_user)
        except OperationError as exc:
            print(exc)
            return ErrorResponse(reason="Database error!")

    @staticmethod
    def check_password(*, clean: str, uuid: str) -> Union[ErrorResponse, StatusResponse]:
        try:
            db_user = db.User.objects(uuid=uuid).first()
            if db_user and check_password_hash(db_user.password, clean):
                return StatusResponse(status=True)
            else:
                return StatusResponse(status=False)
        except OperationError as exc:
            print(exc)
            return ErrorResponse(reason="Database error!")

    @staticmethod
    def save_user(*, user: User) -> Union[ErrorResponse, User]:
        db_user = db.User.objects(uuid=str(user.uuid)).first()
        if not user:
            return ErrorResponse(reason="User not found!")

        db_user.access = str(user.access)
        db_user.client = str(user.client)
        if user.server:
            db_user.server = user.server
        db_user.save()

        return _mongo_to_user(db_user=db_user)
