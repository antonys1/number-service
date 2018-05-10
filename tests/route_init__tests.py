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

from tests.number_service_test_case import NumberServiceTestCase
from number.database import postgres
from flask import json


class RouteInitTests(NumberServiceTestCase):

    def test_route_init(self):
        # Given
        with postgres.get_db_conn() as conn:
            postgres.drop_tables(conn)
        # When
        response = self.app.post("/init")
        # Then
        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Initialized", response_json["result"])

    def test_route_init__already_initialized(self):
        # Given
        with postgres.get_db_conn() as conn:
            postgres.create_tables(conn)
        # When
        response = self.app.post("/init")
        # Then
        self.assertEqual(200, response.status_code)
        response_json = json.loads(response.data)
        self.assertEqual("Already initialized", response_json["result"])
