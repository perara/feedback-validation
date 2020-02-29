#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
from collections import namedtuple
from uuid import UUID

from Crypto.Hash import SHA256
from Crypto.PublicKey import DSA, RSA, ECC
from Crypto.Signature import DSS
from netaddr import IPAddress, IPNetwork
from sanic.response import json, text
from sanic.views import HTTPMethodView
from sanic import Sanic
from sanic_jinja2 import SanicJinja2
import tinydb
from datetime import datetime
from os.path import dirname, realpath, join

from tinydb import where

dp = dirname(realpath(__file__))
hash_dummy = namedtuple("Hash", ["oid"])
app = Sanic(name="feedback_validation")
db = tinydb.TinyDB(join(dp, "database.json"))
jinja = SanicJinja2(app)
access_control = ["127.0.0.1/24", "10.0.10.0/24", "10.0.0.0/24", "10.0.1.0/24"]

@app.route('/')
@jinja.template('index.html')  # decorator method is staticmethod
async def index(request):
    all_table_data = {tbl_name: db.table(tbl_name).all() for tbl_name in db.tables() if tbl_name != "_default"}
    print(all_table_data)
    return {'data': all_table_data}

@app.route('/course/<year:[0-9]{4}>/<course_id:string>/verify/<signature:string>')
async def course(request, year, course_id, signature):
    course_data = db.table(year).search(where("course") == course_id)[0]
    verify_ok = False
    for key, value in course_data["keys"].items():
        h = SHA256.new(value["pubkey"].encode("utf-8"))
        key = ECC.import_key(value["pubkey"])
        verifier = DSS.new(key, 'fips-186-3')

        try:
            verifier.verify(h, bytes.fromhex(signature))
            verify_ok = True
            continue
        except ValueError:
            pass

    return json({
        "message": verify_ok
    })


@app.route('/course/<year:[0-9]{4}>/<course_id:string>')
async def course(request, year, course_id):
    course_data = db.table(year).search(where("course") == course_id)[0]

    # Check if session exists
    session = request.cookies.get('session')

    if session is None:
        session = str(uuid.uuid4())

    request_new_key = "newkey" in request.args

    if request_new_key:

        if session not in course_data["keys"]:
            # Session has no existing keys
            key = ECC.generate(curve='P-256')
            pubkey = key.public_key().export_key(format='PEM')

            h = SHA256.new(pubkey.encode("utf-8"))

            signer = DSS.new(key, 'fips-186-3')
            signature = signer.sign(h)

            # Update table
            course_data["keys"][session] = {
                "pubkey": pubkey,
                "hash": h.hexdigest(),
                "signature": signature.hex()
            }

            db.table(year).update(course_data, where("course") == course_id)

    response = jinja.render(
        "course.html",
        request,
        course=course_data["course"],
        session=course_data["keys"][session]
    )
    response.cookies['session'] = session
    response.cookies["session"]["max-age"] = 60 * 60 * 24 * 30 * 12 * 50 # Cookie lives for 50 years
    return response

@app.route('/new-course/<course_id>')
async def new_course(request, course_id):
    # TODO - Ensure that request.ip is correct
    if not any([IPAddress(request.ip) in IPNetwork(cidr) for cidr in access_control]):
        return json({
            "message": "Not a valid ip"
        })

    table = db.table(str(datetime.now().year.real))
    if table.search(where("course") == course_id):
        return json({
            "message": f"Course {course_id} already exists."
        })

    table.insert({
        "course": course_id,
        "keys": {}
    })

    return json({
        "message": "Created!"
    })




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
