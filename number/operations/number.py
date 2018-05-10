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


def form_id(request):
    return request.form.get('number_id')


def form_new(request):
    return request.form.get('new_number')


def add(conn, number_id, value=0):
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO numbers VALUES (%s, %s);", (number_id, value))
        conn.commit()


def remove(conn, number_id):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM numbers WHERE id = %s", (number_id,))
        cursor.execute("DELETE FROM number_users WHERE number_id = %s", (number_id,))
        conn.commit()


def exists(conn, number_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM numbers WHERE id = %s", (number_id,))
        result = cursor.fetchone()
        conn.commit()
        return result[0] > 0


def verify_not_exists(conn, number_id):
    if exists(conn, number_id):
        raise AlreadyExistsException(number_id)


def verify_exists(conn, number_id):
    if not exists(conn, number_id):
        raise NotFoundException(number_id)


def add_user(conn, number_id, user_id):
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO number_users VALUES (%s, %s);", (number_id, user_id))
        conn.commit()


def remove_user(conn, number_id, user_id):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM number_users WHERE number_id = %s AND user_id = %s;", (number_id, user_id))
        conn.commit()


def user_not_added(conn, number_id, user_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM number_users WHERE number_id = %s AND user_id = %s", (number_id, user_id))
        result = cursor.fetchone()
        conn.commit()
        return result is None or result[0] == 0


def verify_user_not_added(conn, number_id, user_id):
    if not user_not_added(conn, number_id, user_id):
        raise UserAlreadyAddedException(number_id, user_id)


def verify_user_added(conn, number_id, user_id):
    if user_not_added(conn, number_id, user_id):
        raise UserNotAddedException(number_id, user_id)


def update(conn, number_id, new_number):
    with conn.cursor() as cursor:
        cursor.execute("UPDATE numbers SET value = %s WHERE id = %s;", (new_number, number_id))
        conn.commit()


def get_current(conn, number_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT value FROM numbers WHERE id = %s;", (number_id,))
        result = cursor.fetchone()
        conn.commit()
        if result is not None:
            return result[0]


def get_next(conn, number_id):
    next_num = get_current(conn, number_id) + 1
    update(conn, number_id, next_num)
    return next_num


class NotFoundException(Exception):

    def __init__(self, number_id):
        super(NotFoundException, self).__init__(f"Number {number_id} not found")


class AlreadyExistsException(Exception):

    def __init__(self, number_id):
        super(AlreadyExistsException, self).__init__(f"Number {number_id} already exists")


class UserNotAddedException(Exception):

    def __init__(self, number_id, user_id):
        super(UserNotAddedException, self).__init__(f"User {user_id} not added to number {number_id}")


class UserAlreadyAddedException(Exception):

    def __init__(self, number_id, user_id):
        super(UserAlreadyAddedException, self).__init__(f"User {user_id} already added to number {number_id}")
