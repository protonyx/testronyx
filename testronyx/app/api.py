from flask import Blueprint, request, current_app
import json


api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/api/version')
def version():
    agent = current_app.config.get('TSX_AGENT')

    return json.dumps(agent.get_version())


@api_blueprint.route('/api/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        func()
    return ''
