from flask import Blueprint

root_blueprint = Blueprint(
    'root',
    __name__,
    url_prefix='/'
)


@root_blueprint.route('/', methods=['GET'])
def root():
    return {
            "meta": {
                "serverName": "Server name",
                "feature.non_email_login": True
            },
            "skinDomains": [
                "example.com"
            ],
            "signaturePublickey": ""
        }