from datetime import datetime

from flask_restful import Resource


class HomeResource(Resource):
    """Home resource."""

    def get(self):
        return {"time": datetime.now().isoformat(), "version": 1}, 200