from flask import Blueprint
from flask_restful import Api

from dub.views.home_view import HomeResource
from dub.views.user_view import UserCreateResource, UserGetResource, UserCheckPasswordResource, UserSaveResource
from dub.views.texture_view import TextureGetResource, TextureUploadResource, TextureClearResource

blueprint = Blueprint("api", __name__)
api = Api(blueprint)

api.add_resource(HomeResource, "/", endpoint="home")

api.add_resource(UserCreateResource, "/user/create/", endpoint="user_create")
api.add_resource(UserGetResource, "/user/get/", endpoint="user_get")
api.add_resource(UserCheckPasswordResource, "/user/check_password/", endpoint="user_check")
api.add_resource(UserSaveResource, "/user/save/", endpoint="user_save")

api.add_resource(TextureGetResource, "/texture/get/")
api.add_resource(TextureUploadResource, "/texture/upload/")
api.add_resource(TextureClearResource, "/texture/clear/")