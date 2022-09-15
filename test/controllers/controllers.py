# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.custom.test.models.common import invalid_response, valid_response
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


class Test(http.Controller):
    @http.route('/test/test/', auth='public')
    def index(self, **kw):
        return "Hello, world"


class Login(http.Controller):
    @http.route("/api/login", methods=["GET"], type="http", auth="none", csrf=False)
    def api_login(self, **post):
        params = ["db", "login", "password"]
        params = {key: post.get(key) for key in params if post.get(key)}
        db, username, password = (
            params.get("db"),
            post.get("login"),
            post.get("password"),
        )
        _credentials_includes_in_body = all([db, username, password])
        # check if one of the params is missing #########################################################################
        if not _credentials_includes_in_body:
            headers = request.httprequest.headers
            db = headers.get("db")
            username = headers.get("login")
            password = headers.get("password")
            _credentials_includes_in_headers = all([db, username, password])
            if not _credentials_includes_in_headers:
                return invalid_response(
                    "missing error", "either of the following are missing [db, username,password]", 403,
                )
        # login to odoo to see if the params are correct ################################################################
        try:
            request.session.authenticate(db, username, password)
        except AccessError as aee:
            return invalid_response("Access error", "Error: %s" % aee.name)
        except AccessDenied as ade:
            return invalid_response("Access denied", "Login, password or db invalid")
        except Exception as e:
            # Invalid database:
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            return invalid_response("wrong database name", error, 403)

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)


class ReadContact(http.Controller):
    @http.route("/api/read", auth="public", website=False, csrf=False, type="json", methods=['GET', 'POST'])
    def return_contact(self, **post):
        requested_id = (int(post.get("id")),)
        contact = http.request.env['res.partner'].sudo().search([('id', '=', requested_id)])
        contact_list = [contact.name, contact.person_gender]
        if contact.name != False:
            # print(contact_list)
            # return valid_response([{"The Contact is": contact_list, "message": "succeed"}], status=200)
            return contact_list
        else:
            # print("not found")
            return invalid_response("ID is not found", "enter correct ID", status=401)


class CreateContact(http.Controller):
    @http.route("/api/create", auth="public", website=False, csrf=False, type="json", methods=['GET', 'POST'])
    def create_contact(self, **post):
        name, person_gender = (
            str(post.get("name")),
            str(post.get("person_gender")),
        )
        request.env['res.partner'].sudo().create({
            'name': name,
            'person_gender': person_gender
        })
        return valid_response([{"message": "New Contact successfully Created"}], status=200)