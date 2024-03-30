from flask import Blueprint

# Define the blueprint for client
client_bp = Blueprint('client_bp', __name__)
stylist_bp = Blueprint('stylist_bp', __name__)
auth_bp = Blueprint('auth_bp', __name__)

from .client import *
from .stylist import *