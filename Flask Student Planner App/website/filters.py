import base64
from flask import Blueprint

filters = Blueprint('filters', __name__)

@filters.app_template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')
