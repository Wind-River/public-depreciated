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
import datetime
from requests.exceptions import ReadTimeout, ConnectionError
from bcdash import app, jsonify
from bcdash.exceptions import APIError

@app.route("/api/sparts/ping")
def ping_handler():
    """respond to a simple "ping" request, indicating whether this app (bcdash catalog) is running
    """
    return jsonify({"status": "success"})

def human_readable_filesize(size):
    """Print file size in human readable format"""
    for unit in [' bytes', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB']:
        if size < 1000.0:
            return str(round(size, 2)) + unit
        size /= 1000.0


def get_node_api_address(uuid):
    """Find the node with the given UUID and return its api_address"""
    selected_node = None
    for node in get_blockchain_nodes():
        if node["uuid"] == uuid:
            selected_node = node
            break

    if selected_node is None:
        raise APIError("Node UUID was not found on the network.")

    if "api_address" not in selected_node:
        raise APIError("Invalid conductor response. Mising 'api_address'.")

    if not selected_node["api_address"]:
        raise APIError("Node did not provide a ledger service API URL.")

    return selected_node["api_address"]

def ping_node(uuid, timeout=app.config["DEFAULT_API_TIMEOUT"]):
    """ping a blockchain node and return its status
    """
    node_api_url = get_node_api_address(uuid)

    try:
        response = requests.get(node_api_url + "/api/sparts/ping", timeout=timeout)
    except ReadTimeout:
        raise APIError("Timed out.")
    except ConnectionError:
        raise APIError("Connection refused.")

    if response.status_code != 200:
        raise APIError("(HTTP " + str(response.status_code) + ")")

    try:
        data = response.json()
    except:
        raise APIError("Returns invalid JSON.")

    if "status" not in data:
        raise APIError("Returns invalid JSON: missing 'status'")

    if data["status"] != "success":
        raise APIError("Status: '" + str(data["status"]) + "'")

    return "Running"


def get_node_blocks(uuid):
    """Get JSON data for set of transaction blocks for each node"""
    api_url = get_node_api_address(uuid) + "/api/sparts/ledger/blockchain_contents"
    blocks = call_api_service("get", api_url)

    for block in blocks:
        block["size"] = human_readable_filesize(block["size"])

    return blocks


def get_blockchain_nodes():
    """get a list of nodes running the ledger and their status from the conductor API
    """
    try:
        return call_conductor_api("get", "/ledger/nodes")
    except APIError as error:
        raise APIError("Failed to get list of blockchain nodes. " + str(error))

def get_blockchain_apps():
    """get a list of nodes running the ledger and their status from the conductor API
    """
    try:
        return call_conductor_api("get", "/apps")
    except APIError as error:
        raise APIError("Failed to get list of blockchain apps. " + str(error))

def register_app_with_blockchain():
    """call the  conductor service to register this app
    """
    print("Registering app with blockchain...")

    data = {
        "uuid": "520e7ee6-26f6-4cd0-6710-49c3579086f4",
        "name": "Blockchain Dashboard",
        "label": "Blockchain Dashboard",
        "api_address": "http://blockchain.open.windriver.com",
        "app_type": "website",
        "description": "Blockchain Dashboard"
    }

    try:
        return call_conductor_api("post", "/apps/register", data)
    except APIError as error:
        raise APIError("Failed to register app with blockchain. " + str(error))

def get_bc_suppliers():
    return call_ledger_api("get", "/ledger/suppliers")

def get_bc_parts():
    return call_ledger_api("get", "/ledger/parts")

def get_bc_envelopes():
    return call_ledger_api("get", "/ledger/envelopes")

def get_bc_categories():
    return call_ledger_api("get", "/ledger/categories")

def get_ledger_version():
    if app.config["BYPASS_API_CALLS"]:
            return "API calls are disabled."
    hyperledger_platform = call_ledger_api("get", "/ledger/sawtooth/version")
    hyperledger_version = str(hyperledger_platform["name"]) + " version " \
            + str(hyperledger_platform["version"])
    return hyperledger_version

def get_ledger_uptime():
    if app.config["BYPASS_API_CALLS"]:
            return "API calls are disabled."

    timestamp = call_conductor_api("get", "/ledger/uptime")["time_stamp"]

    # remove microseconds and timezone information
    timestamp_no_us = timestamp.split(".")[0]

    # calculate difference until now
    startup_time = datetime.datetime.strptime(timestamp_no_us, "%Y-%m-%d %H:%M:%S")
    uptime_duration = str(datetime.datetime.now() - startup_time)

    # remove microseconds from uptime
    return ".".join(uptime_duration.split(".")[:-1])

def call_ledger_api(method, url, data={}):
    """ call the blockchain ledger service with the given method (post or get), url, and data.
    """
    try:
        return call_api_service(method, get_ledger_address() + url, data)
    except APIError as error:
        raise APIError("Failed to call ledger API service. " + str(error))

def get_ledger_address():
    """get the address of the ledger service from the conductor
    """
    try:
        if app.config["BYPASS_API_CALLS"]:
            return "API calls are disabled."
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

def call_api_service(method, url, data={}):
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
