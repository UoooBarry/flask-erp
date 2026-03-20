from flask import Blueprint, request
from app.models import User
from app.utils.response import render_success
from app.utils.exceptions import UnauthorizedError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = user.create_access_token()
        return render_success({"access_token": access_token})

    raise UnauthorizedError("Invalid username or password")
