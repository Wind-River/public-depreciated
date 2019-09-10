"""
Copyright (c) 2017 Wind River Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software  distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND, either express or implied.

sparts catalog package
"""
import sys
import os

from flask import Flask, jsonify
from requests.exceptions import ReadTimeout, ConnectionError

app = Flask(__name__)

app.config.from_object("config")

def get_resource_as_string(name, charset='utf-8'):
    """write css or javascript files directly into the html document.
    """
    with app.open_resource(name) as file:
        return file.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

from sparts.database import db_session, Base, engine
import sparts.views
from sparts.views import render_page, stacktrace
import sparts.catalog
import sparts.envelope
import sparts.sampledata
import sparts.api

# do not run the following if no tables exist in the database
if engine.table_names():

    try:
        sparts.api.register_app_with_blockchain()
    except sparts.exceptions.APIError as error:
        print(str(error))

    try:
        sparts.catalog.populate_categories()
    except sparts.exceptions.APIError as error:
        print(str(error))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
