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

from tests.number_service_initialized_test_case import NumberServiceInitializedTestCase
from number.database import postgres
from number.operations import user
from flask import json


class RouteUserAuthTokenRefreshTests(NumberServiceInitializedTestCase):

    def test_route_user_password_change__valid_username_and_password(self):
        # Given
        user_id = "amy@apple.com"
        password = "Oranges12345"
        new_password = "Bananas12345"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, password)
        # When
        response = self.app.post("/user/password/change",
                                 data={"new_password": new_password},
                                 headers=self.authorization_basic(user_id, password))
        # Then
        self.assertEqual(200, response.status_code)
        self.assertEqual("", response.data.decode("utf-8"))

    def test_route_user_password_change__invalid_username(self):
        # Given
        user_id = "amy@apple.com"
        password = "Oranges12345"
        invalid_user_id = "fake.amy@apple.com"
        new_password = "Bananas12345"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, password)
        # When
        response = self.app.post("/user/password/change",
                                 data={"new_password": new_password},
                                 headers=self.authorization_basic(invalid_user_id, password))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])

    def test_route_user_password_change__invalid_password(self):
        # Given
        user_id = "amy@apple.com"
        password = "Oranges12345"
        invalid_password = "apples"
        new_password = "bananas"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, password)
        # When
        response = self.app.post("/user/password/change",
                                 data={"new_password": new_password},
                                 headers=self.authorization_basic(user_id, invalid_password))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Authentication failed", response_json["error"])

    def test_route_user_password_change__weak_new_password(self):
        # Given
        user_id = "amy@apple.com"
        password = "Oranges12345"
        weak_new_password = "12345"
        with postgres.get_db_conn() as conn:
            user.add(conn, user_id, password)
        # When
        response = self.app.post("/user/password/change",
                                 data={"new_password": weak_new_password},
                                 headers=self.authorization_basic(user_id, password))
        # Then
        self.assertEqual(401, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Password must be at least 12 characters long, including an uppercase letter, a lowercase letter and a digit.", response_json["error"])
