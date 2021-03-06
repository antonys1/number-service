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


class RouteInitTests(NumberServiceTestCase):

    def test_route_init(self):
        # When
        response = self.app.get("/version")
        # Then
        self.assertEqual(200, response.status_code)
        self.assertEqual("1.0", response.data.decode("utf-8"))
