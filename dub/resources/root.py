from flask import Blueprint, current_app

root_blueprint = Blueprint(
    'root',
    __name__,
    url_prefix='/'
)


@root_blueprint.route('/', methods=['GET'])
def root():
    return {
            "meta": {
                "serverName": current_app.config.get("AUTH_SERVER_NAME", "Server name"),
                "feature.non_email_login": True,
                "feature.enable_profile_key": True,
                "feature.no_mojang_namespace": True,
                "feature.enable_mojang_anti_features": False
            },
            "skinDomains": [
                current_app.config.get("SKIN_DOMAIN", ".example.com")
            ],
            "signaturePublickey": current_app.config.get("PUBLIC_RSA_KEY").decode('utf-8')
        }