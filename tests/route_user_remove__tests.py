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


class RouteUserRemoveTests(NumberServiceInitializedTestCase):

    def test_route_remove_user__with_admin_auth_token(self):
        admin_auth_token = "abc123"
        user_auth_token = "xyz789"
        user_id = "amy@apple.com"

        # Given
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "oranges", auth_token=admin_auth_token, is_admin=True)
            user.add(conn, user_id, "sesame", auth_token=user_auth_token, is_admin=False)
        # When
        response = self.app.post("/user/remove",
                                 data={"user_id": user_id},
                                 headers=self.authorization_custom(admin_auth_token))
        # Then
        self.assertEqual(200, response.status_code)
        self.assertEqual("", response.data.decode("utf-8"))

    def test_route_remove_user__with_user_auth_token(self):
        admin_auth_token = "abc123"
        user_id = "amy@apple.com"
        user_auth_token = "xyz789"

        # Given
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "oranges", auth_token=admin_auth_token, is_admin=True)
            user.add(conn, user_id, "sesame", auth_token=user_auth_token, is_admin=False)
        # When
        response = self.app.post("/user/remove",
                                 data={"user_id": user_id},
                                 headers=self.authorization_custom(user_auth_token))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])

    def test_route_remove_user__with_invalid_auth_token(self):
        admin_auth_token = "abc123"
        user_id = "amy@apple.com"
        user_auth_token = "xyz789"
        invalid_auth_token = "ooo000"

        # Given
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "oranges", auth_token=admin_auth_token, is_admin=True)
            user.add(conn, user_id, "sesame", auth_token=user_auth_token, is_admin=False)
        # When
        response = self.app.post("/user/remove",
                                 data={"user_id": user_id},
                                 headers=self.authorization_custom(invalid_auth_token))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])

    def test_route_remove_user__with_invalid_user(self):
        # Given
        admin_auth_token = "abc123"
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "oranges", auth_token=admin_auth_token, is_admin=True)
        # When
        invalid_user_id = "amy@apple.com"
        response = self.app.post("/user/remove",
                                 data={"user_id": invalid_user_id},
                                 headers=self.authorization_custom(admin_auth_token))
        # Then
        self.assertEqual(404, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual(f"User {invalid_user_id} not found", response_json["error"])


if __name__ == '__main__':
    unittest.main()
