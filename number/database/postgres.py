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

import os
import psycopg2
from psycopg2 import sql

HEROKU_NAME = os.environ.get('HEROKU_NAME')
DATABASE_URL = os.environ.get('DATABASE_URL')
SCHEMA = "public"
TABLES = ["users", "user_auth_tokens", "numbers", "number_users"]


def get_db_conn():
    if HEROKU_NAME is None:
        return psycopg2.connect(DATABASE_URL)
    else:
        return psycopg2.connect(DATABASE_URL, sslmode='require')


def initialized(conn):
    with conn.cursor() as cursor:
        for table in TABLES:
            cursor.execute(query_table_exists(SCHEMA, table))
            if cursor.fetchone()[0] is None:
                return False
        return True


def initialize(conn):
    drop_tables(conn)
    create_tables(conn)


def create_tables(conn):
    with conn.cursor() as cursor:
        cursor.execute("CREATE TABLE users (id text PRIMARY KEY, is_admin bool NOT NULL, hashed_password bytea NOT NULL)")
        cursor.execute("CREATE TABLE user_auth_tokens (user_id text NOT NULL, hashed_auth_token bytea NOT NULL, PRIMARY KEY(user_id, hashed_auth_token))")
        cursor.execute("CREATE TABLE numbers (id text PRIMARY KEY, value integer NOT NULL)")
        cursor.execute("CREATE TABLE number_users (number_id text NOT NULL, user_id text NOT NULL, PRIMARY KEY(number_id, user_id))")
        conn.commit()


def drop_tables(conn):
    with conn.cursor() as cursor:
        for table in TABLES:
            drop_table(cursor, SCHEMA, table)
        conn.commit()


def drop_table(cursor, schema, table):
    cursor.execute(query_table_exists(schema, table))
    if cursor.fetchone()[0] is not None:
        cursor.execute(sql.SQL("DROP TABLE {}").format(sql.Identifier(table)))


def query_table_exists(schema, table):
    return sql.SQL("SELECT to_regclass({})").format(sql.Literal(f"{schema}.{table}"))
