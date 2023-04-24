import os
import helpers

from flask import Flask


app = Flask(__name__)


@app.route('/')
def stat():
    return 'ok'


app.route('/create_analytics_user')(helpers.create_analytics_user)
app.route('/modify')(helpers.modify)
app.route('/read')(helpers.read)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
