#!/usr/bin/env python3
from dub.application import create_app

app = create_app("config")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080", debug=app.config['DEBUG'])
