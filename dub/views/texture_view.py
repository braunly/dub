from base64 import b64decode
import uuid

from flask_restful import Resource, reqparse

from dub.models import Texture


class TextureGetResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, default=None)
        parser.add_argument("texture_types", type=str, action="append", default=list("SKIN"))
        args = parser.parse_args()

        print(args)

        textures_dict = {}
        textures = Texture.objects(
            token=args['uuid'], 
            kind__in=args['texture_types'],
            deleted=False
        ).order_by("-created").no_cache()

        print(textures)

        for row in textures:
            textures_dict[row.kind] = {
                "url": row.image,
                "metadata": row.metadata
            }
        
        return {"textures": textures_dict}

class TextureUploadResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, required=True)
        parser.add_argument("kind", type=str, required=True)
        parser.add_argument("data", type=str, required=True)
        parser.add_argument("metadata", type=dict, default=dict())
        args = parser.parse_args()

        print(args)

        texture = Texture(
            token=args['uuid'],
            deleted=False,
            kind=args['kind'],
            metadata=args['metadata']
        )
        image_path = f'{args["uuid"]}/{uuid.uuid4()}.png'
        texture.image = image_path

        with open(f'media/{image_path}', 'wb') as f:
            f.write(b64decode(args['data']))

        texture.save()

        return {"message": "Saved texture"}
        

class TextureClearResource(Resource):
    """User resource."""

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("uuid", type=str, default=None)
        parser.add_argument("texture_types", type=str, action="append", default=list("SKIN"))
        args = parser.parse_args()

        print(args)

        Texture.objects(
            token=args['uuid'], 
            kind__in=args['texture_types'],
            deleted=False
        ).update(deleted=True)

        return {"message": "Cleaned requested textures"}