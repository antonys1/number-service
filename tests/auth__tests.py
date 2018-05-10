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
from number.operations import auth


class RouteUserAuthTokenRefreshTests(NumberServiceTestCase):

    def test_strong_password(self):
        # Given
        password = "Oranges12345"
        # When
        auth.verify_password_strength(password)

    def test_weak_password__empty(self):
        # Given
        password = ""
        # When
        with self.assertRaises(auth.PasswordException):
            auth.verify_password_strength(password)

    def test_weak_password__no_uppercase(self):
        # Given
        password = "123456789abc"
        # When
        with self.assertRaises(auth.PasswordException):
            auth.verify_password_strength(password)

    def test_weak_password__no_lowercase(self):
        # Given
        password = "123456789ABC"
        # When
        with self.assertRaises(auth.PasswordException):
            auth.verify_password_strength(password)

    def test_weak_password__no_digits(self):
        # Given
        password = "ApplesAndOranges"
        # When
        with self.assertRaises(auth.PasswordException):
            auth.verify_password_strength(password)
