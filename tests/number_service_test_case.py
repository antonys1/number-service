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
from number import number_service
from number.database import postgres
import base64
import os


class NumberServiceTestCase(unittest.TestCase):

    def setUp(self):
        number_service.app.testing = True
        self.app = number_service.app.test_client()
        postgres.DATABASE_URL = os.environ.get('TEST_DATABASE_URL')
        with number_service.app.app_context():
            with postgres.get_db_conn() as conn:
                postgres.drop_tables(conn)

    def tearDown(self):
        with number_service.app.app_context():
            with postgres.get_db_conn() as conn:
                postgres.drop_tables(conn)

    def authorization_basic(self, username, password):
        basic = base64.b64encode(f"{username}:{password}".encode('utf-8'))
        return {'Authorization': b'Basic ' + basic}

    def authorization_custom(self, token):
        return {'Authorization': token}
