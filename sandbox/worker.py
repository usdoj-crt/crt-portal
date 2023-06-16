import os
import helpers

from flask import Flask


app = Flask(__name__)


@app.route('/')
def stat():
    return 'ok'


app.route('/try_to_import')(helpers.try_to_import)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
