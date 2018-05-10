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

import unittest
from tests.number_service_initialized_test_case import NumberServiceInitializedTestCase
from number.database import postgres
from number.operations import number, user
from flask import json


class RouteNumberGetNextTests(NumberServiceInitializedTestCase):

    def test_route_number_get_next__with_valid_auth_token(self):
        # Given
        user_id = "amy@apple.com"
        user_auth_token = "abc123"
        number_id = "com.myapp"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, "oranges", auth_token=user_auth_token, is_admin=False)
            number.add(conn, number_id)
            number.add_user(conn, number_id, user_id)
        # When
        response = self.app.post("/number/next",
                                 data={"number_id": number_id},
                                 headers=self.authorization_custom(user_auth_token))
        # Then
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, int(response.data))

    def test_route_number_get_next__with_invalid_auth_token(self):
        # Given
        user_id = "amy@apple.com"
        user_auth_token = "abc123"
        number_id = "com.myapp"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, "oranges", auth_token=user_auth_token, is_admin=False)
            number.add(conn, number_id)
            number.add_user(conn, number_id, user_id)
        # When
        invalid_auth_token = "ooo000"
        response = self.app.post("/number/next",
                                 data={"number_id": number_id},
                                 headers=self.authorization_custom(invalid_auth_token))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])

    def test_route_number_get_next__with_invalid_number(self):
        # Given
        user_id = "amy@apple.com"
        user_auth_token = "abc123"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, "oranges", auth_token=user_auth_token, is_admin=False)
        # When
        invalid_number_id = "com.myapp.fake"
        response = self.app.post("/number/next",
                                 data={"number_id": invalid_number_id},
                                 headers=self.authorization_custom(user_auth_token))
        # Then
        self.assertEqual(400, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual(f"User {user_id} not added to number {invalid_number_id}", response_json["error"])


if __name__ == '__main__':
    unittest.main()
