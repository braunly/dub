from flask import Blueprint

auth_server_blueprint = Blueprint(
    'auth_server',
    __name__,
    url_prefix='/authserver'
)

@auth_server_blueprint.route('/authenticate', methods=['POST'])
def authenticate():
    pass

@auth_server_blueprint.route('/refresh', methods=['POST'])
def refresh():
    pass

@auth_server_blueprint.route('/validate', methods=['POST'])
def validate():
    pass

@auth_server_blueprint.route('/invalidate', methods=['POST'])
def invalidate():
    pass

@auth_server_blueprint.route('/signout', methods=['POST'])
def sign_out():
    pass


