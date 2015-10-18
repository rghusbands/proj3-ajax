#! /usr/bin/env python3

""" For deployment on ix under CGI """

import site
site.addsitedir("/home/users/rgh/public_html/CIS399/htbin/proj3-ajax/env/lib/python3.4/site-packages")

from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)
