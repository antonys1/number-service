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

from number.operations import auth


def form_user_id(request):
    return request.form.get('user_id')


def form_password(request):
    password = request.form.get('password')
    auth.verify_password_strength(password)
    return password


def form_new_password(request):
    password = request.form.get('new_password')
    auth.verify_password_strength(password)
    return password


def add(conn, user_id, password, is_admin=False, auth_token=auth.gen_auth_token()):
    hashed_password = auth.get_hashed_password(password)
    hashed_auth_token = auth.get_hashed_auth_token(auth_token)
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO users VALUES (%s, %s, %s)", (user_id, is_admin, hashed_password))
        cursor.execute("INSERT INTO user_auth_tokens VALUES (%s, %s)", (user_id, hashed_auth_token))
        conn.commit()
        return auth_token


def remove(conn, user_id):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        cursor.execute("DELETE FROM user_auth_tokens WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM number_users WHERE user_id = %s", (user_id,))
        conn.commit()


def exists(conn, user_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        conn.commit()
        return result[0] > 0


def verify_not_exists(conn, user_id):
    if exists(conn, user_id):
        raise AlreadyExistsException(user_id)


def verify_exists(conn, user_id):
    if not exists(conn, user_id):
        raise NotFoundException(user_id)


def refresh_auth_token(conn, user_id):
    with conn.cursor() as cursor:
        auth_token = auth.gen_auth_token()
        hashed_auth_token = auth.get_hashed_auth_token(auth_token)
        cursor.execute("UPDATE user_auth_tokens SET hashed_auth_token = %s WHERE user_id = %s", (hashed_auth_token, user_id))
        conn.commit()
        return auth_token


def change_password(conn, user_id, new_password):
    with conn.cursor() as cursor:
        hashed_password = auth.get_hashed_password(new_password)
        cursor.execute("UPDATE users SET hashed_password = %s WHERE id = %s", (hashed_password, user_id))
        conn.commit()


class NotFoundException(Exception):

    def __init__(self, user_id):
        super(NotFoundException, self).__init__(f"User {user_id} not found")


class AlreadyExistsException(Exception):

    def __init__(self, user_id):
        super(AlreadyExistsException, self).__init__(f"User {user_id} already exists")
