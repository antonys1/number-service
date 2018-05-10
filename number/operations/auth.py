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

import bcrypt
import secrets
import hashlib
import re


def verify_password_strength(password):
    if not password or len(password) < 12:
        raise PasswordException()
    # search for uppercase letters
    if re.search(r"[A-Z]", password) is None:
        raise PasswordException()
    # search for lowercase letters
    if re.search(r"[a-z]", password) is None:
        raise PasswordException()
    # search for digits
    if re.search(r"\d", password) is None:
        raise PasswordException()


def header_auth_token(request):
    return request.headers.get('Authorization')


def gen_auth_token():
    return secrets.token_urlsafe(32)


def get_hashed_auth_token(auth_token):
    sha256 = hashlib.sha256()
    sha256.update(auth_token.encode('utf-8'))
    return sha256.digest()


def check_user_password(conn, user_id, password):
    with conn.cursor() as cursor:
        query = "SELECT hashed_password FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result is None:
            raise AuthException()
        hashed_password = result[0]
        conn.commit()
        if not check_password(password, bytes(hashed_password)):
            raise AuthException()


def check_auth_token(conn, auth_token, check_is_admin=False):
    with conn.cursor() as cursor:
        hashed_auth_token = get_hashed_auth_token(auth_token)
        query = f"SELECT id FROM users WHERE id = ({get_user_id_for_auth_token_query()})"
        if check_is_admin:
            query = query + " AND is_admin = true"
        cursor.execute(query, (hashed_auth_token,))
        result = cursor.fetchone()
        conn.commit()
        if result is None:
            raise AuthException()
        else:
            return result[0]


def get_user_id_for_auth_token_query():
    return "SELECT user_id FROM user_auth_tokens WHERE hashed_auth_token = %s"


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt(12))


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)


class AuthException(Exception):

    def __init__(self):
        super(AuthException, self).__init__("Authentication failed")


class PasswordException(Exception):

    def __init__(self):
        super(PasswordException, self).__init__("Password must be at least 12 characters long, including an uppercase letter, a lowercase letter and a digit.")
