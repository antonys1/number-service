# Copyright 2018 Sean Antony
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from flask import Flask, request, jsonify, make_response
from number.database import postgres
from number.operations import auth, number, user

import sys
import logging

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


@app.errorhandler(auth.AuthException)
def unauthorized(error):
    resp = make_response(jsonify(error=str(error)), 401)
    return resp


@app.errorhandler(auth.PasswordException)
def password_error(error):
    resp = make_response(jsonify(error=str(error)), 401)
    return resp


@app.errorhandler(user.NotFoundException)
def user_not_found(error):
    resp = make_response(jsonify(error=str(error)), 404)
    return resp


@app.errorhandler(user.AlreadyExistsException)
def user_already_exists(error):
    resp = make_response(jsonify(error=str(error)), 400)
    return resp


@app.errorhandler(number.NotFoundException)
def number_not_found(error):
    resp = make_response(jsonify(error=str(error)), 404)
    return resp


@app.errorhandler(number.AlreadyExistsException)
def number_already_exists(error):
    resp = make_response(jsonify(error=str(error)), 400)
    return resp


@app.errorhandler(number.UserNotAddedException)
def number_user_not_added(error):
    resp = make_response(jsonify(error=str(error)), 400)
    return resp


@app.errorhandler(number.UserAlreadyAddedException)
def number_user_already_added(error):
    resp = make_response(jsonify(error=str(error)), 400)
    return resp


@app.route("/version", methods=['GET'])
def route_version():
    return "1.0"


@app.route("/init", methods=['POST'])
def route_init():
    with postgres.get_db_conn() as conn:
        if not postgres.initialized(conn):
            postgres.initialize(conn)
            user.add(conn, "admin", "password", is_admin=True)
            return jsonify(result="Initialized")
        else:
            return jsonify(result="Already initialized")


@app.route("/user/add", methods=['POST'])
def route_user_add():
    with postgres.get_db_conn() as conn:
        auth.check_auth_token(conn, auth.header_auth_token(request), check_is_admin=True)
        user_id = user.form_user_id(request)
        user.verify_not_exists(conn, user_id)
        auth_token = user.add(conn, user_id, user.form_password(request))
        return jsonify(auth_token=auth_token)


@app.route("/user/remove", methods=['POST'])
def route_user_remove():
    with postgres.get_db_conn() as conn:
        auth.check_auth_token(conn, auth.header_auth_token(request), check_is_admin=True)
        user_id = user.form_user_id(request)
        user.verify_exists(conn, user_id)
        user.remove(conn, user_id)
        return ""


@app.route("/user/auth_token/refresh", methods=['POST'])
def route_user_auth_token_refresh():
    with postgres.get_db_conn() as conn:
        user_id = request.authorization.username
        auth.check_user_password(conn, user_id, request.authorization.password)
        auth_token = user.refresh_auth_token(conn, user_id)
        return jsonify(auth_token=auth_token)


@app.route("/user/password/change", methods=['POST'])
def route_user_password_change():
    with postgres.get_db_conn() as conn:
        user_id = request.authorization.username
        auth.check_user_password(conn, user_id, request.authorization.password)
        new_password = user.form_new_password(request)
        user.change_password(conn, user_id, new_password)
        return ""


@app.route("/number/add", methods=['POST'])
def route_number_add():
    with postgres.get_db_conn() as conn:
        auth.check_auth_token(conn, auth.header_auth_token(request), check_is_admin=True)
        number_id = number.form_id(request)
        number.verify_not_exists(conn, number_id)
        number.add(conn, number_id)
        return ""


@app.route("/number/remove", methods=['POST'])
def route_number_remove():
    with postgres.get_db_conn() as conn:
        auth.check_auth_token(conn, auth.header_auth_token(request), check_is_admin=True)
        number_id = number.form_id(request)
        number.verify_exists(conn, number_id)
        number.remove(conn, number_id)
        return ""


@app.route("/number/user/add", methods=['POST'])
def route_number_add_user():
    with postgres.get_db_conn() as conn:
        auth.check_auth_token(conn, auth.header_auth_token(request), check_is_admin=True)
        number_id = number.form_id(request)
        number.verify_exists(conn, number_id)
        user_id = user.form_user_id(request)
        user.verify_exists(conn, user_id)
        number.verify_user_not_added(conn, number_id, user_id)
        number.add_user(conn, number_id, user_id)
        return ""


@app.route("/number/user/remove", methods=['POST'])
def route_number_remove_user():
    with postgres.get_db_conn() as conn:
        auth.check_auth_token(conn, auth.header_auth_token(request), check_is_admin=True)
        number_id = number.form_id(request)
        number.verify_exists(conn, number_id)
        user_id = user.form_user_id(request)
        user.verify_exists(conn, user_id)
        number.verify_user_added(conn, number_id, user_id)
        number.remove_user(conn, number_id, user_id)
        return ""


@app.route("/number/current", methods=['POST'])
def route_number_get_current():
    with postgres.get_db_conn() as conn:
        user_id = auth.check_auth_token(conn, auth.header_auth_token(request))
        number_id = number.form_id(request)
        number.verify_user_added(conn, number_id, user_id)
        return str(number.get_current(conn, number_id))


@app.route("/number/next", methods=['POST'])
def route_number_get_next():
    with postgres.get_db_conn() as conn:
        user_id = auth.check_auth_token(conn, auth.header_auth_token(request))
        number_id = number.form_id(request)
        number.verify_user_added(conn, number_id, user_id)
        return str(number.get_next(conn, number_id))


@app.route("/number/set", methods=['POST'])
def route_number_set():
    with postgres.get_db_conn() as conn:
        user_id = auth.check_auth_token(conn, auth.header_auth_token(request), check_is_admin=True)
        number_id = number.form_id(request)
        number.verify_user_added(conn, number_id, user_id)
        number.update(conn, number_id, number.form_new(request))
        return ""
