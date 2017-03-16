import sys
sys.path.append("/Library/Python/2.7/site-packages/")

import tornado.web
from tornado import httpclient

from jinja2 import Environment, FileSystemLoader
import tornado.web
import os, os.path
import wtforms
from wtforms_tornado import Form
import urllib
import random
import string
import re
import sys, inspect
import requests
import arrow
import time
import StringIO
import csv
import threading

from settings import *
from utilities import *

# Handler for main page
class MainHandler(tornado.web.RequestHandler):
    TEMPLATE_FILE = "index.jinja"

    def getContext(self, **kwargs):
        context = {}
        context.update(kwargs)
        context.update(JINJA2_SETTINGS)
        pages = []
        # import ipdb;ipdb.set_trace()
        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj):
                try:
                    new_page = {'name': obj.PAGE_NAME, 'desc': obj.PAGE_DESCRIPTION, 'url': obj.PAGE_URL, 'pos': obj.PAGE_POS}
                    if self.PAGE_NAME == obj.PAGE_NAME:
                        new_page.update({'navclass':'active'})
                    else:
                        new_page.update({'navclass':''})
                    pages.append(new_page)
                except AttributeError:
                    pass
        context.update({'pages': pages})
        return context

    def get(self, **kwargs):
        context = {}
        context.update(self.getContext(**kwargs))
        templateLoader = FileSystemLoader( searchpath=BASEDIR + "templates/" )
        templateEnv = Environment( loader=templateLoader )
        template = templateEnv.get_template(self.TEMPLATE_FILE)
        html_output = template.render(title="Truck Service", **context)
        # Returns rendered template string to the browser request
        self.write(html_output)

#---- PAGES ----

class REDIRECT(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.protocol == "http":
            self.redirect("https://%s" % self.request.full_url()[len("http://"):], permanent=True)

    def get(self):
        self.write("Hello, world")

class Index(MainHandler):
    TEMPLATE_FILE = "index.jinja"
    PAGE_NAME = "Home"
    PAGE_DESCRIPTION = ""
    PAGE_URL = '/'
    PAGE_POS = 0


class AdminLogin(MainHandler):
    TEMPLATE_FILE = "admin_login.jinja"

    def getContext(self, **kwargs):
        context = super(AdminLogin, self).getContext(**kwargs)
        context.update({'auth_fail':self.get_argument('auth_fail',False)})
        return context

    def get(self, **kwargs):
        if self.get_secure_cookie("auth_token")==ADMIN_KEY:
            return self.redirect('/admin')
        return super(AdminLogin, self).get(**kwargs)


class Admin(MainHandler):
    TEMPLATE_FILE = 'admin.jinja'

    def getContext(self, **kwargs):
        context = super(Admin, self).getContext(**kwargs)
        context.update({'api_key':API_KEY})
        num = get_current_number()
        if(HUMANIZE):
            date = arrow.get(num[1]).humanize()
        else:
            date = arrow.get(num[1]).to(TIMEZONE).format(DATE_FORMAT)
        context.update({'number':num[0], 'date':date})
        context.update({'users': get_all_users()})
        state = seeing_people()
        print state
        if(HUMANIZE):
            state_date = arrow.get(state[1]).humanize()
        else:
            state_date = arrow.get(state[1]).to(TIMEZONE).format(DATE_FORMAT)
        context.update({'seeing_people':state[0], 'seeing_people_date':state_date})
        return context

    def get(self, **kwargs):
        if self.get_secure_cookie("auth_token")!=ADMIN_KEY:
            return self.redirect('/admin_login')
        return super(Admin, self).get(**kwargs)

    def post(self, **kwargs):
        user_name = self.get_argument('user_name', '')
        password = self.get_argument('password', '')
        if authenticate_user(user_name, password):
            self.set_secure_cookie("auth_token", ADMIN_KEY)
            return super(Admin, self).get(**kwargs)
        else:
            time.sleep(5)
            return self.redirect('/admin_login?auth_fail=1')


#APIs
class GetNext(tornado.web.RequestHandler):
    def post(self):
        DBLOCK = threading.Lock()
        post_api_key = self.get_argument('api_key', '')
        if post_api_key != API_KEY:
            self.set_status(403)
            self.write({'error':"You're not authorized"})
            return
        truck_id = self.get_argument('truck_id', '')
        work = assign_payload(truck_id, DBLOCK)
        response = {'status': 'Error'}
        if (work):
            response ={'payload_id': work[0], 'payload':work[1], 'src':work[2], 'dst':work[3], 'weight':work[4], 'customer_name':work[5]}
        self.write(response)


class OrderWork(tornado.web.RequestHandler):
    def post(self):
        DBLOCK = threading.Lock()
        post_api_key = self.get_argument('api_key', '')
        if post_api_key != API_KEY:
            self.set_status(403)
            self.write({'error':"You're not authorized"})
            return
        payload = self.get_argument('payload', '')
        src = self.get_argument('src', '')
        dst = self.get_argument('dst', '')
        weight = self.get_argument('weight', '')
        customer_name = self.get_argument('customer_name', '')
        input_new_order(payload, src, dst, weight, customer_name, DBLOCK)
        response ={'status':'OK'}
        self.write(response)


class Delivered(tornado.web.RequestHandler):
    def post(self):
        DBLOCK = threading.Lock()
        post_api_key = self.get_argument('api_key', '')
        if post_api_key != API_KEY:
            self.set_status(403)
            self.write({'error':"You're not authorized"})
            return
        payload_id = self.get_argument('payload_id', '')
        mark_complete(payload_id, DBLOCK)
        response ={'status':'OK'}
        self.write(response)
