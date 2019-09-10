"""
Copyright (c) 2017 Wind River Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software  distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND, either express or implied.
"""
import traceback
import json
from flask import render_template, Response, jsonify
from requests.exceptions import ReadTimeout, ConnectionError
from bcdash import app
from bcdash.api import get_blockchain_nodes, get_ledger_address, ping_node, \
    get_bc_suppliers, get_bc_parts, get_bc_categories, get_bc_envelopes, get_blockchain_apps, \
    get_ledger_uptime, get_ledger_version, get_node_blocks
from bcdash.exceptions import APIError

def render_page(template, title="", *args, **kwargs):
    return render_template("site_template.html", page_title=title, \
        template=template, *args, **kwargs, page=template)

def stacktrace():
    return "<pre>" + str(traceback.format_exc()) + "</pre>"

@app.route("/about")
def about():
    return render_page("about")

@app.errorhandler(404)
def page_not_found(e):
    return render_page("404"), 404

@app.route("/ledger/components")
def query_ledger_components():
    """get parts, suppliers, envelopes, and categories from the blockchain ledger service
    """
    try:

        categories = get_bc_categories()
        suppliers = get_bc_suppliers()
        parts = get_bc_parts()
        envelopes = get_bc_envelopes()
        hyperledger_version = get_ledger_version()

        supplier_parts = {}
        categories_by_uuid = {}
        for category in categories:
            categories_by_uuid[category["uuid"]] = category

        envelopes_by_uuid = {}
        for envelope in envelopes:
            envelopes_by_uuid[envelope["uuid"]] = envelope

        for supplier in suppliers:
            supplier_parts[supplier["uuid"]] = {"supplier": supplier, "parts": []}

        for part in parts:

            if "categories" not in part:
                break

            category_uuids = [category["category_id"] for category in part.pop("categories")]
            part["categories"] = []

            envelope_uuids = [envelope["envelope_id"] for envelope in part.pop("envelopes")]
            part["envelopes"] = []

            #
            # handle invalid category UUID

            for category_uuid in category_uuids:
                if category_uuid in categories_by_uuid:
                    part["categories"].append(categories_by_uuid[category_uuid])

            for envelope_uuid in envelope_uuids:
                if envelope_uuid in envelopes_by_uuid:
                    part["envelopes"].append(envelopes_by_uuid[envelope_uuid])

            #
            # attach envelope
            #

            found_supplier = False
            for supplier in part["suppliers"]:
                supplier_uuid = supplier["supplier_id"]
                if supplier_uuid in supplier_parts:
                    found_supplier = True
                    supplier_parts[supplier_uuid]["parts"].append(part)

            if not found_supplier:
                if not "unknown" in supplier_parts:
                    supplier_parts["unknown"] = {"supplier": \
                        {"name": "[Unknown] Supplier UUID was not found."}, \
                        "parts": []}

                supplier_parts["unknown"]["parts"].append(part)

        return render_template("components.html", suppliers=suppliers,
            supplier_parts=supplier_parts,
            parts_count=len(parts),
            suppliers_count=len(suppliers),
            hyperledger_version=hyperledger_version,
            envelopes_count=len([envelope for envelope in envelopes \
                if envelope["content_type"] == "this"]))

    except APIError as error:
        return render_template("error.html", error_message=str(error))


@app.route("/")
def home():
    """display status information about the blockchain. Eventually, this might be its own app.
    """
    try:
        return render_page("home", \
            uptime=get_ledger_uptime(), \
            apps=get_blockchain_apps(), \
            nodes=get_blockchain_nodes() , \
            ledger_api_address=get_ledger_address(), \
            envelope_count=0, \
            supplier_count=0, \
            part_count=0)

    except APIError as error:
        return render_page("error", error_message=str(error))


@app.route("/blockchain/nodes/status/<uuid>")
def get_node_status(uuid):
    """json route for pinging a node and returning its status
    """
    try:
        return jsonify({"status": ping_node(uuid)})
    except APIError as error:
        return jsonify({"status": "Down. " + str(error)})


@app.route("/blockchain/nodes/blocks/<uuid>")
def node_blocks_table(uuid):
    """html route for getting list of ledger transactions (blocks) for a node and returning a table
    """
    try:
        return render_template("ledger_blocks_table.html", blocks=get_node_blocks(uuid))
    except APIError as error:
        return render_template("error.html", \
            error_message="Failed to retrieve list of blockchain transactions on this node. " \
            + str(error))

