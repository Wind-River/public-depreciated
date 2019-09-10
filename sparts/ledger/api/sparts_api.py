#copyright 2017 Wind River Systems
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

#!flask/bin/python
import subprocess, shlex, re
from flask import Flask, jsonify, make_response, request, json
app = Flask(__name__)

#Retrieves list of all envelopes from the ledger
@app.route('/api/sparts/ledger/envelopes', methods=['GET'])
def get_envelopes():
	try:
		cmd = "comp list-envelope"
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		process.wait()
		output = "" 
		for line in process.stdout:
			output+=line.decode("UTF-8").strip()
		return output
	except Exception as e:
		exp = ret_exception(e) 
		return exp

#Retreives envelope record by envelope id from the ledger 
@app.route('/api/sparts/ledger/envelopes/<string:envelope_id>',methods=['GET'])
def get_envelope(envelope_id):
	try:
		cmd = "comp retrieve " + envelope_id
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		process.wait()
		output = ''
		for line in process.stdout:
			output+=line.decode("utf-8").strip()
		return output
	except Exception as e:
		exp = ret_exception(e) 
		return exp


#Retrieves list of all categories from the ledger 
@app.route('/api/sparts/ledger/categories', methods=['GET'])
def get_categories():
	try:
		cmd = "category list-category"
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		process.wait()
		output = ""
		for line in process.stdout:
			output+=line.decode("UTF-8").strip()
		return output
	except Exception as e:
		exp = ret_exception(e) 
		return exp

#Retrieves list of all suppliers from the ledger
@app.route('/api/sparts/ledger/suppliers', methods=['GET'])
def get_suppliers():
        try:
                cmd = "supplier list-supplier"
                process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
                process.wait()
                output = ''
                for line in process.stdout:
                        output+=line.decode("utf-8").strip()
                return output
        except Exception as e:
                exp = ret_exception(e) 
                return exp

def ret_exception(exception):
        exp = "{\"status\":\"failed\",\"error_message\":\""+str(exception)+"\"}" 
        return exp

#Retrieves category record by category id   
@app.route('/api/sparts/ledger/categories/<string:category_id>', methods=['GET'])
def get_category(category_id):
	try:
		cmd = "category retrieve " + category_id
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		process.wait()
		output = ''
		for line in process.stdout:
			output+=line.decode("utf-8").strip()
		return output
	except Exception as e:
		exp = ret_exception(e) 
		return exp

#Retrieves supplier record by supplier id
@app.route('/api/sparts/ledger/suppliers/<string:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
	try:
		cmd = "supplier retrieve " + supplier_id
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		process.wait()
		output = ''
		for line in process.stdout:
			output+=line.decode("utf-8").strip()
		return output
	except Exception as e:
		exp = ret_exception(e) 
		return exp

#Retrieves list of all parts from the ledger 
@app.route('/api/sparts/ledger/parts', methods=['GET'])
def get_parts():
	try:
		cmd = "pt list-part"
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		process.wait()
		output = ''
		for line in process.stdout:
			output+=line.decode("utf-8").strip()
		return output
	except Exception as e:
		exp = ret_exception(e) 
		return exp

#Retrieves part record by part id
@app.route('/api/sparts/ledger/parts/<string:part_id>', methods=['GET'])
def get_part(part_id):
	try:	
		cmd = "pt retrieve " + part_id
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		process.wait()
		output = ''
		for line in process.stdout:
			output+=line.decode("utf-8").strip()
		return output
	except Exception as e: 
		exp = ret_exception(e)
		return exp


def format_str(inputstr):
	str = "\"{}\"".format(inputstr)
	return str 

#Creates supplier record in the ledger
@app.route('/api/sparts/ledger/suppliers', methods=['POST'])
def create_supplier():
	try:
		if not request.json or not 'uuid' in request.json:
			return 'Invalid JSON'
		uuid = request.json['uuid']
		short_id = request.json['short_id']
		short_id = format_str(short_id) 
		name = request.json['name']
		name = format_str(name) 
		passwd = request.json['passwd']
		passwd = format_str(passwd) 
		url = request.json['url']
		url = format_str(url) 
        	
		cmd = "supplier create " + uuid + " " + short_id + " " + str(name) + " " + passwd + " " + str(url)
		cmd = shlex.split(cmd)
	
		process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		process.wait()
		output = ''
		for line in process.stdout:
			output+=line.decode("utf-8").strip()
		return output
	except Exception as e:
		exp = ret_exception(e)
		return exp

#Creates part record in the ledger	
@app.route('/api/sparts/ledger/parts', methods=['POST'])
def create_part():
	try:

		if not request.json or not 'uuid' in request.json:
			return 'Invalid JSON'
		uuid = request.json['uuid']
		name = request.json['name']
		name = format_str(name)
		sp = " "
		checksum = request.json['checksum']
		checksum = format_str(checksum)
		version = request.json['version']
		version = format_str(version)
		src_uri = request.json['src_uri']

		src_uri = format_str(src_uri)
		licensing = request.json['licensing']
		licensing = format_str(licensing)
		label = request.json['label']
		label = format_str(label)
		description = request.json['description']
		description = format_str(description)
		cmd = "pt create " + uuid + sp + str(name) + sp + checksum + sp +version + sp + str(src_uri) + sp + str(licensing) + sp + str(label) + sp + str(description)
		cmd = shlex.split(cmd)
		process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		process.wait()
		output = '' 
		for line in process.stdout:
			output+=line.decode("utf-8").strip()
		return output
	except Exception as e:
                exp = ret_exception(e) 
                return exp

#Establishes relationship between envelope and part in the ledger
@app.route('/api/sparts/ledger/parts/AddEnvelope', methods=['POST'])
def add_envelope_to_part():
	try:
		if not request.json or not 'part_uuid' or not 'envelope_uuid' in request.json:
			return 'Invalid JSON'
		uuid = request.json['part_uuid']
		sp = " "
		envelope_uuid= request.json['envelope_uuid']
		cmd = "pt AddEnvelope " + uuid + sp + envelope_uuid
		cmd = shlex.split(cmd)
		process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		process.wait()
		output = ''
		for line in process.stdout:
			output+=line.decode("utf-8").strip()
		return output
	except Exception as e:
		exp = ret_exception(e) 
		return exp

#Establishes relationship between supplier and part in the ledger
@app.route('/api/sparts/ledger/mapping/PartSupplier', methods=['POST'])
def add_supplier_to_part():
        try:
                if not request.json or not 'part_uuid' or not 'supplier_uuid' in request.json:
                        return 'Invalid JSON'
                uuid = request.json['part_uuid']
                supplier_uuid= request.json['supplier_uuid']
                cmd = "pt AddSupplier " + uuid + " " + supplier_uuid
                cmd = shlex.split(cmd)
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                process.wait()
                output = ''
                add_part_to_supplier(supplier_uuid,uuid)

                for line in process.stdout:
                        output+=line.decode("utf-8").strip()
                return output
        except Exception as e:
                exp = ret_exception(e) 
                return exp

#Establishes relationship between part and supplier 
def add_part_to_supplier(uuid,part_uuid):
        try:	
                cmd = "supplier AddPart " + uuid + " " + part_uuid
                cmd = shlex.split(cmd)
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                process.wait()
                output = ''
                for line in process.stdout:
                        output+=line.decode("utf-8").strip()
                return output
        except Exception as e:
                exp = ret_exception(e) 
                return exp


#Establishes relationship between category and part
@app.route('/api/sparts/ledger/parts/AddCategory', methods=['POST'])
def add_category_to_part():
        try:
                if not request.json or not 'part_uuid' or not 'category_uuid' in request.json:
                        return 'Invalid JSON'
                uuid = request.json['part_uuid']
                category_uuid = request.json['category_uuid']
                cmd = "pt AddCategory " + uuid + " " + category_uuid
                cmd = shlex.split(cmd)
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                process.wait()
                output = ''
                for line in process.stdout:
                        output+=line.decode("utf-8").strip()
                return output
        except Exception as e:
                exp = ret_exception(e) 
                return exp

#Create record for category in the ledger
@app.route('/api/sparts/ledger/categories', methods=['POST'])
def create_category():
	try:
		if not request.json or not 'uuid' in request.json:
			return 'Invalid JSON'
		uuid = request.json['uuid']
		name = request.json['name']
		name = format_str(name) 
		description = request.json['description']
		description = format_str(description)
		cmd = "category create " + uuid + " " + str(name) +" " + str(description)
		cmd = shlex.split(cmd)
		process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		process.wait()
		output = ''
		for line in process.stdout:
			output+=line.decode("utf-8").strip()
		return output
	except Exception as e:
		exp = ret_exception(e) 
		return exp


def create_artifact_cmd(uuid,short_id,filename,content_type,checksum,path,uri,label,openchain):
	cmd = "comp create " + uuid + " " + str(short_id) + " "  + str(filename) + " " + str(content_type) + " " + checksum + " " + str(path) + " " + str(uri) + " " + str(label) + " " + str(openchain)
	return cmd

#Create record for the artifact in the ledger  
@app.route('/api/sparts/ledger/envelopes', methods=['POST'])
def create_artifact():
	try:
		parent_envelope_uuid=''
		output = '' 
		for i in request.json["artifacts"]:
			if i['content_type'] == 'this':
				parent_envelope_uuid=i['uuid']
				uuid=i['uuid']
				short_id = i['short_id']
				short_id = format_str(short_id)
				checksum = i['checksum']
				filename = i['filename']
				filename = format_str(filename)
				content_type = i['content_type']
				content_type = format_str(content_type)
				path = i['path']
				path = format_str(path)
				uri = i['uri']
				uri = format_str(uri)
				label = i['label']
				label = format_str(label)
				openchain = i['openchain']
				cmd = create_artifact_cmd(uuid,short_id,filename,content_type,checksum,path,uri,label,openchain) 
				cmd = shlex.split(cmd)
				process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
				process.wait()
				for line in process.stdout:
					output+=line.decode("utf-8").strip()
			else:
				uuid=i['uuid']
				short_id = i['short_id']
				short_id = format_str(short_id)
				checksum = i['checksum']
				filename = i['filename']
				filename = format_str(filename)
				content_type = i['content_type']
				content_type = format_str(content_type)
				path = i['path']
				path = format_str(path)
				uri = i['uri']
				uri = format_str(uri)
				label = i['label']
				label = format_str(label)
				openchain = i['openchain']
				cmd = create_artifact_cmd(uuid,short_id,filename,content_type,checksum,path,uri,label,openchain)
				cmd = shlex.split(cmd)

				process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
				process.wait()
				for line in process.stdout:
					output+=line.decode("utf-8").strip()
			
			if len(parent_envelope_uuid) > 0 and i['content_type'] != 'this':
				uuid=i['uuid']
				cmd = "comp AddArtifact " + parent_envelope_uuid + " " + uuid
				process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
				process.wait()
				for line in process.stdout:
					output+=line.decode("utf-8").strip()	

		return output
	except Exception as e:
		exp = ret_exception(e)
		return exp
			
			
def not_found():
	status = "{'error':'Not found'}"
	return status
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="33")
