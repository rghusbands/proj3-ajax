"""
Very simple Flask web site, with one page
displaying a course schedule.

"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify # For AJAX transactions

import json
import logging

# Date handling
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
import math
from dateutil import tz  # For interpreting local times

# Our own module
# import acp_limits


###
# Globals
###
app = flask.Flask(__name__)
import CONFIG

import uuid
app.secret_key = str(uuid.uuid4())
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)


###
# Pages
###

@app.route("/")
@app.route("/index")
@app.route("/calc")
def index():
  app.logger.debug("Main page entry")
  return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("index")
    return flask.render_template('page_not_found.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############

@app.route("/_calc_times")
def calc_times():
  """
  Calculates open/close times from miles, using rules
  described at http://www.rusa.org/octime_alg.html.
  Expects one URL-encoded argument, the number of miles.
  """
  app.logger.debug("Got a JSON request");

#grabs the values from the javascript and html inputs
  miles = request.args.get('miles', 0, type=int)
  totaldistance = request.args.get('distance', 1,  type=int)
  currenttime = request.args.get('currenttime', 2, type=str)
  units = request.args.get('units', 3, type=str)
  count = request.args.get('count', 4, type=int)

#A lot of checks for things such as illegal dates/times and not plugging in values properly
  if (count == 0 and miles != 0):
      return jsonify(result = "Please start with Distance = 0.")
  if (miles < 0):
      return jsonify(result = "No negative inputs please.")
  if (units == '-choose-'):
      return jsonify(result = "Choose Units. Please refresh page")
  currentTimeArray = currenttime.split(' ')
  if len(currentTimeArray) <= 1:
      return jsonify(result = "Date Inputted Incorrectly. Please refresh page")
  dateArray = currentTimeArray[0].split('/')
  if (int(dateArray[0]) > 12 or int(dateArray[0]) < 1 or int(dateArray[1]) > 31 or int(dateArray[1]) < 1 or int(dateArray[2]) < 0):
      return jsonify(result = "Illegal Date/Time Entered. Please refresh page")
  timeArray = currentTimeArray[1].split(':')
  if (int(timeArray[0])<0 or int(timeArray[0])>24 or int(timeArray[1])<0 or int(timeArray[1])>60):
      return jsonify(result = "Illegal Date/Time Entered. Please refresh page")

#converts input miles to km if inputs are miles
  if (units == "Miles"):
      miles = miles*1.609

#use arrow to help format and keep track of the time and date
  try:
      startTime = arrow.get(currenttime, "MM/DD/YY HH:mm")
  except:
      startTime = arrow.get('01/01/15 00:00', "MM/DD/YY HH:mm")

#refreshes open and closetime to 0 everytime.
  opentime = 0;
  closetime = 0;

#Holds the different speeds to be accessed in the algorithm below
  speeds = {0:[15,34], 1:[15,32], 2:[15,30], 3:[11.428,28], 4:[13.333,26]}

#Calculates the checkpoints raw time in hours in decimal form. Anything over the distance will have a checkpoint at the same time as the
#total distance checkpoint because the race is supposed to be over.

#There also seems to be some weird thing that happens when the input is exact but I don't see anything about it in the rules so
#I don't know what it is. Therefore they are regretfully hardcoded in.

  if (totaldistance == 1000):
      if (miles >= 1000):
          opentime = 200/speeds[0][1] + 200/speeds[1][1] + 200/speeds[2][1] + 400/speeds[3][1]
          closetime = 75.0
      if (miles >= 600 and miles < 1000):
          opentime = 200/speeds[0][1] + 200/speeds[1][1] + 200/speeds[2][1] + (miles-600)/speeds[3][1]
          closetime = 200/speeds[0][0] + 200/speeds[1][0] + 200/speeds[2][0] + (miles-600)/speeds[3][0]
      if (miles >= 400 and miles < 600):
          opentime = 200/speeds[0][1] + 200/speeds[1][1] + (miles-400)/speeds[2][1]
          closetime = 200/speeds[0][0] + 200/speeds[1][0] + (miles-400)/speeds[2][0]
      if (miles >= 300 and miles < 400):
          opentime = 200/speeds[0][1] + (miles-200)/speeds[1][1]
          closetime = 200/speeds[0][0] + (miles-200)/speeds[1][0]
      if (miles >= 200 and miles < 300):
          opentime = 200/speeds[0][1] + (miles-200)/speeds[1][1]
          closetime = 200/speeds[0][0] + (miles-200)/speeds[1][0]
      if (miles < 200):
          opentime = miles/speeds[0][1]
          closetime = miles/speeds[0][0]
  elif (totaldistance == 600):
      if (miles >= 600):
          opentime = 200/speeds[0][1] + 200/speeds[1][1] + 200/speeds[2][1]
          closetime = 40.0
      if (miles >= 400 and miles < 600):
          opentime = 200/speeds[0][1] + 200/speeds[1][1] + (miles-400)/speeds[2][1]
          closetime = 200/speeds[0][0] + 200/speeds[1][0] + (miles-400)/speeds[2][0]
      if (miles >= 300 and miles < 400):
          opentime = 200/speeds[0][1] + (miles-200)/speeds[1][1]
          closetime = 200/speeds[0][0] + (miles-200)/speeds[1][0]
      if (miles >= 200 and miles < 300):
          opentime = 200/speeds[0][1] + (miles-200)/speeds[1][1]
          closetime = 200/speeds[0][0] + (miles-200)/speeds[1][0]
      if (miles < 200):
          opentime = miles/speeds[0][1]
          closetime = miles/speeds[0][0]
  elif (totaldistance == 400):
      if (miles >= 400):
          opentime = 200/speeds[0][1] + 200/speeds[1][1]
          closetime = 27.0
      if (miles >= 300 and miles < 400):
          opentime = 200/speeds[0][1] + (miles-200)/speeds[1][1]
          closetime = 200/speeds[0][0] + (miles-200)/speeds[1][0]
      if (miles >= 200 and miles < 300):
          opentime = 200/speeds[0][1] + (miles-200)/speeds[1][1]
          closetime = 200/speeds[0][0] + (miles-200)/speeds[1][0]
      if (miles < 200):
          opentime = miles/speeds[0][1]
          closetime = miles/speeds[0][0]
  elif (totaldistance == 300):
      if (miles >= 300):
          opentime = 200/speeds[0][1] + 100/speeds[1][1]
          closetime = 20.0
      if (miles >= 200 and miles < 300):
          opentime = 200/speeds[0][1] + (miles-200)/speeds[1][1]
          closetime = 200/speeds[0][0] + (miles-200)/speeds[1][0]
      if (miles < 200):
          opentime = miles/speeds[0][1]
          closetime = miles/speeds[0][0]
  elif (totaldistance == 200):
      if (miles >= 200):
          opentime = 200/speeds[0][1]
          closetime = 13.5
      if (miles < 200):
          opentime = miles/speeds[0][1]
          closetime = miles/speeds[0][0]

  #converts hours in decimals to integer hours and mintues with seperate variables
  openhours, openminutes = divmod(opentime, 1)
  closehours, closeminutes = divmod(closetime, 1)
  openhours = int(openhours)
  closehours = int(closehours)
  openminutes = round(openminutes * 60)
  closeminutes = round(closeminutes * 60)

#formats before being pushed back to the html
  if (miles == 0):
      result1 = startTime.format('MM/DD/YY HH:mm')
      result2 = startTime.replace(hours=+1).format('MM/DD/YY HH:mm')
  else:
      result1 = startTime.replace(hours=+openhours).replace(minutes=+openminutes).format('MM/DD/YY HH:mm')
      result2 = startTime.replace(hours=+closehours).replace(minutes=+closeminutes).format('MM/DD/YY HH:mm')

  return jsonify(result = "Open: " + result1 + " -  Close:  " + result2, count = count+1)

#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try:
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try:
        normal = arrow.get( date )
        return normal.format("hh:mm")
    except:
        return "(bad time)"



#############


if __name__ == "__main__":
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT)


