"""
Copyright (c) 2017 Wind River Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software  distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND, either express or implied.

Ledger API service calls
"""
import json
import requests
from requests.exceptions import ReadTimeout
from sparts import app, jsonify
from sparts.exceptions import APIError

@app.route("/api/sparts/ping")
def ping_handler():
    """respond to a simple "ping" request, indicating whether this app (sparts catalog) is running
    """
    return jsonify({"status": "success"})

def get_uuid():
    """call the conductor service to a unique UUID
    """
    if app.config["BYPASS_API_CALLS"]:
        raise APIError("Could not retrieve a UUID from conductor service. API calls are disabled.")

    try:
        response = call_conductor_api("get", "/uuid")

        if "uuid" in response:
            return response["uuid"]
        else:
            raise APIError("The call to conductor service at '" \
                + str(app.config["BLOCKCHAIN_API"]) \
                + "/uuid' to get a new UUID failed. The response did not contain a UUID.")
    except APIError as error:
        raise APIError("Failed to get a new UUID from conductor service. " + str(error))

def register_app_with_blockchain():
    """call the  conductor service to register this app (sparts catalog) on the supply chain network
    """
    print("Registering app with blockchain...")

    data = {
        "name": "Software Parts Catalog",
        "label": "Software Parts Catalog",
        "uuid": "9fb84fa0-1716-4367-7012-61370e23028f",
        "api_address": "http://catalog.open.windriver.com",
        "app_type": "website",
        "description": "Software Parts Catalog"
    }

    try:
        return call_conductor_api("post", "/apps/register", data)
    except APIError as error:
        raise APIError("Failed to register app with blockchain. " + str(error))

def save_part_supplier_relation(part, supplier):
    """save part supplier relation to blockchain
    """
    try:
        call_ledger_api("post", "/ledger/mapping/PartSupplier", {
            "part_uuid": part.uuid,
            "supplier_uuid": supplier.uuid
        })
    except APIError as error:
        raise APIError("Failed to save part-supplier relation. " + str(error))

def save_part_category_relation(part, category):
    """save part category relation to blockchain
    """
    try:
        call_ledger_api("post", "/ledger/parts/AddCategory", {
            "part_uuid": part.uuid,
            "category_uuid": category.uuid
        })
    except APIError as error:
        raise APIError("Failed to save part-category relation. " + str(error))

def save_part_envelope_relation(part, envelope):
    """save part envelope relation to blockchain
    """
    try:
        call_ledger_api("post", "/ledger/parts/AddEnvelope", {
            "part_uuid": part.uuid,
            "envelope_uuid": envelope.uuid
        })
    except APIError as error:
        raise APIError("Failed to save part-envelope relation. " + str(error))

def get_blockchain_categories():
    """get list of part categories
    """
    try:
        return call_ledger_api("get", "/ledger/categories")
    except APIError as error:
        raise APIError("Failed to get blockchain categories. " + str(error))

def save_category_to_blockchain(category):
    """save category to blockchain
    """
    try:
        call_ledger_api("post", "/ledger/categories", {
            "uuid": category.uuid,
            "name": category.name,
            "description": category.description
        })
    except APIError as error:
        raise APIError("Failed to get save category to blockchain. " + str(error))

def save_supplier_to_blockchain(supplier):
    """save the given supplier on the blockchain by calling the ledger service
    """
    try:
        call_ledger_api("post", "/ledger/suppliers", {
            "uuid": supplier.uuid,
            "short_id": "",
            "name": supplier.name,
            "passwd": supplier.password,
            "url": ""
        })
    except APIError as error:
        raise APIError("Failed to save supplier to blockchain. " + str(error))

def save_part_to_blockchain(part):
    """save the given part on the blockchain by calling the ledger service
    """
    try:
        call_ledger_api("post", "/ledger/parts", {
            "uuid": part.uuid,
            "name": part.name,
            "checksum": "",
            "version": part.version,
            "src_uri": part.url,
            "licensing": part.licensing,
            "label": "",
            "description": part.description
        })
    except APIError as error:
        raise APIError("Failed to save part to blockchain. " + str(error))

def save_envelope_to_blockchain(envelope):
    """save the given envelope on the blockchain by calling the ledger service
    """
    try:
        call_ledger_api("post", "/ledger/envelopes", json.loads(envelope.toc))
    except APIError as error:
        raise APIError("Failed to save envelope to blockchain. " + str(error))

def call_ledger_api(method, url, data={}):
    """ call the blockchain ledger service with the given method (post or get), url, and data.
    """
    if app.config["BYPASS_LEDGER_CALLS"]:
        return {}

    try:
        return call_api_service(method, get_ledger_address() + url, data)
    except APIError as error:
        raise APIError("Failed to call ledger API service. " + str(error))

def get_ledger_address():
    """get the address of the ledger service from the conductor
    """
    try:
        ledger_address = call_conductor_api("get", "/ledger/address")
        return "http://" + str(ledger_address["ip_address"]) + ":" + str(ledger_address["port"]) \
            + "/api/sparts"
    except APIError as error:
        raise APIError("Failed to get the ledger API address. " + str(error))

def call_conductor_api(method, url, data={}):
    """call the conductor service
    """
    try:
        return call_api_service(method, app.config["BLOCKCHAIN_API"] + url, data)
    except APIError as error:
        raise APIError("Failed to call the conductor API service. " + str(error))

def call_api_service(method, url, data):
    """call the API service at url with given HTTP method and parameters
    """
    if app.config["BYPASS_API_CALLS"]:
        return {}

    try:
        print("Calling [" + method + "] " + url)
        print("with " + str(data))

        if method == "get":
            response = requests.get(url, params=data, \
                timeout=app.config["DEFAULT_API_TIMEOUT"])
        elif method == "post":
            response = requests.post(url, data=json.dumps(data), \
                headers={'Content-type': 'application/json'}, \
                timeout=app.config["DEFAULT_API_TIMEOUT"])
        else:
            raise APIError("Bad method passed to function `call_api()`. Got `" + method \
                + "`; expected 'get' or 'post'.")

        if response.status_code != 200:
            raise APIError("The call to " + url + " resulted in HTTP status " \
                + str(response.status_code))

        try:
            json_response = response.json()
        except:
            raise APIError("Failed to parse the JSON data in the response of API service at " \
                + url + ". The response was `" + str(response.content) + "`.")

        if "status" in json_response and json_response["status"] != "success":
            raise APIError("API service at '" + url + "' returned status '" \
                + str(json_response["status"]) + "', with the following details: " \
                + str(json_response))

        return json_response

    except ReadTimeout:
        raise APIError("Connection to " + url + " timed out.")

    except ConnectionError:
        raise APIError("API service at " + url + " refused connection.")

    except Exception as error:
        raise APIError("Failed to call the API service at " + url + ". " + str(error))
