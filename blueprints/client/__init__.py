from flask import Blueprint

# Define the blueprint for client
client_bp = Blueprint('client_bp', __name__)

from .client import *