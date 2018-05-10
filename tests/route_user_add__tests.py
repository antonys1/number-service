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
from number.operations import user
from flask import json


class RouteUserAddTests(NumberServiceInitializedTestCase):

    def test_route_add_user__with_valid_auth_token(self):
        # Given
        admin_auth_token = "abc123"
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "Oranges12345", auth_token=admin_auth_token, is_admin=True)
        # When
        response = self.app.post("/user/add",
                                 data={"user_id": "amy@apple.com", "password": "Sesame123456"},
                                 headers=self.authorization_custom(admin_auth_token))
        # Then
        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data)
        self.assertIsNotNone(response_json["auth_token"])

    def test_route_add_user__with_invalid_auth_token(self):
        # Given
        admin_auth_token = "abc123"
        invalid_auth_token = "xyz789"
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "Oranges12345", auth_token=admin_auth_token, is_admin=True)
        # When
        response = self.app.post("/user/add",
                                 data={"user_id": "amy@apple.com", "password": "Sesame123456"},
                                 headers=self.authorization_custom(invalid_auth_token))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])

    def test_route_add_user__with_weak_password(self):
        # Given
        admin_auth_token = "abc123"
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "Oranges12345", auth_token=admin_auth_token, is_admin=True)
        weak_password = "12345"
        # When
        response = self.app.post("/user/add",
                                 data={"user_id": "amy@apple.com", "password": weak_password},
                                 headers=self.authorization_custom(admin_auth_token))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Password must be at least 12 characters long, including an uppercase letter, a lowercase letter and a digit.", response_json["error"])

    def test_route_add_user__already_exists(self):
        # Given
        admin_auth_token = "abc123"
        user_id = "amy@apple.com"
        password = "Sesame123456"
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "Oranges12345", auth_token=admin_auth_token, is_admin=True)
            user.add(conn, user_id, password)
        # When
        response = self.app.post("/user/add",
                                 data={"user_id": user_id, "password": password},
                                 headers=self.authorization_custom(admin_auth_token))
        # Then
        self.assertEqual(400, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual(f"User {user_id} already exists", response_json["error"])


if __name__ == '__main__':
    unittest.main()
