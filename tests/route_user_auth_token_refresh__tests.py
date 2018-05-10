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


class RouteUserAuthTokenRefreshTests(NumberServiceInitializedTestCase):

    def test_route_user_refresh_auth_token__valid_username_and_password(self):
        # Given
        user_id = "amy@apple.com"
        password = "oranges"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, password)
        # When
        response = self.app.post("/user/auth_token/refresh",
                                 headers=self.authorization_basic(user_id, password))
        # Then
        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data)
        self.assertIsNotNone(response_json["auth_token"])

    def test_route_user_refresh_auth_token__invalid_username(self):
        # Given
        user_id = "amy@apple.com"
        password = "oranges"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, password)
        # When
        response = self.app.post("/user/auth_token/refresh",
                                 headers=self.authorization_basic("fake.amy@apple.com", password))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])

    def test_route_user_refresh_auth_token__invalid_password(self):
        # Given
        user_id = "amy@apple.com"
        password = "oranges"
        invalid_password = "sesame"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, password)
        # When
        response = self.app.post("/user/auth_token/refresh",
                                 headers=self.authorization_basic(user_id, invalid_password))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])


if __name__ == '__main__':
    unittest.main()
