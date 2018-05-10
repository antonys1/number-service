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


class RouteNumberAddTests(NumberServiceInitializedTestCase):

    def test_route_add_number__with_admin_auth_token(self):
        # Given
        admin_auth_token = "abc123"
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "oranges", auth_token=admin_auth_token, is_admin=True)
        # When
        number_id = "com.myapp"
        response = self.app.post("/number/add",
                                 data={"number_id": number_id},
                                 headers=self.authorization_custom(admin_auth_token))
        # Then
        self.assertEqual(200, response.status_code)
        self.assertEqual("", response.data.decode("utf-8"))

    def test_route_add_number__with_user_auth_token(self):
        # Given
        user_auth_token = "xyz789"
        with postgres.get_db_conn() as conn:
            user.add(conn, "user", "apples", auth_token=user_auth_token, is_admin=False)
        # When
        number_id = "com.myapp"
        response = self.app.post("/number/add",
                                 data={"number_id": number_id},
                                 headers=self.authorization_custom(user_auth_token))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])

    def test_route_add_number__with_invalid_auth_token(self):
        # When
        invalid_auth_token = "ooo000"
        number_id = "com.myapp"
        response = self.app.post("/number/add",
                                 data={"number_id": number_id},
                                 headers=self.authorization_custom(invalid_auth_token))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])

    def test_route_add_number__existing(self):
        # Given
        admin_auth_token = "abc123"
        number_id = "com.myapp"
        with postgres.get_db_conn() as conn:
            user.add(conn, "admin", "oranges", auth_token=admin_auth_token, is_admin=True)
            number.add(conn, number_id)
        # When
        response = self.app.post("/number/add",
                                 data={"number_id": number_id},
                                 headers=self.authorization_custom(admin_auth_token))
        # Then
        self.assertEqual(400, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual(f"Number {number_id} already exists", response_json["error"])


if __name__ == '__main__':
    unittest.main()
