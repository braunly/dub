from flask import Blueprint

session_server_blueprint = Blueprint(
    'session_server',
    __name__,
    url_prefix='/sessionserver'
)

@session_server_blueprint.route('/session/minecraft/join', methods=['POST'])
def join():
    pass

@session_server_blueprint.route('/session/minecraft/profile/<string:uuid>', methods=['GET'])
def get_profile(uuid):
    pass

@session_server_blueprint.route('/session/minecraft/hasJoined', methods=['GET'])
def has_joined():
    pass

