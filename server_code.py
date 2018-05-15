import sqlite3
import datetime
import requests
from bokeh.plotting import figure
from bokeh.models import HoverTool, LinearColorMapper
from bokeh.embed import components
import numpy as np
from math import factorial
from enum import Enum
import sys

sys.path.append('__HOME__/final_project/')  # changes the directory so that I can call other python scripts
import alerts

# fish_database = "fish_database.db"  # just come up with name of database
fish_database = "__HOME__/final_project/fish_database.db"

temperature_low = 72 # https://en.wikipedia.org/wiki/Serpae_tetra
temperature_high = 79 # https://en.wikipedia.org/wiki/Serpae_tetra
turbidy_low = 4.2 # Experimental
ph_low = 6.5  # https://www.fishlore.com/Profiles-SerpaeTetra.htm
ph_high = 6.8 # https://www.fishlore.com/Profiles-SerpaeTetra.htm
waterlevel = 2 # Experimental


class Tables(Enum):
    temperature = 1
    turbidity = 2
    waterlevel = 3
    ph = 4


def db_create():
    connection = sqlite3.connect(fish_database)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE temperature (temperature float, timing timestamp);')
    cursor.execute('CREATE TABLE turbidity (turbidity float, timing timestamp);')
    cursor.execute('CREATE TABLE waterlevel (waterlevel float, timing timestamp);')
    cursor.execute('CREATE TABLE ph (ph float, timing timestamp);')
    connection.commit()
    connection.close()


def db_insert(table, value):
    connection = sqlite3.connect(fish_database)
    cursor = connection.cursor()

    if table == Tables.ph:
        cursor.execute('''INSERT into ph VALUES (?,?);''', (value, datetime.datetime.now()))
    elif table == Tables.temperature:
        cursor.execute('''INSERT into temperature VALUES (?,?);''', (value, datetime.datetime.now()))
    elif table == Tables.waterlevel:
        cursor.execute('''INSERT into waterlevel VALUES (?,?);''', (value, datetime.datetime.now()))
    elif table == Tables.turbidity:
        cursor.execute('''INSERT into turbidity VALUES (?,?);''', (value, datetime.datetime.now()))

    connection.commit()
    connection.close()


def db_lookup(table):
    connection = sqlite3.connect(fish_database)
    cursor = connection.cursor()

    time_delta = datetime.datetime.now() - datetime.timedelta(days=24)  # change this to 24 hours in actual project

    things = []

    if table == Tables.ph:
        things = cursor.execute('''SELECT * FROM ph WHERE timing > ? ORDER BY timing ASC;''', (time_delta,)).fetchall()
    elif table == Tables.temperature:
        things = cursor.execute('''SELECT * FROM temperature WHERE timing > ? ORDER BY timing ASC;''', (time_delta,)).fetchall()
    elif table == Tables.waterlevel:
        things = cursor.execute('''SELECT * FROM waterlevel WHERE timing > ? ORDER BY timing ASC;''', (time_delta,)).fetchall()
    elif table == Tables.turbidity:
        things = cursor.execute('''SELECT * FROM turbidity WHERE timing > ? ORDER BY timing ASC;''', (time_delta,)).fetchall()

    connection.commit()
    connection.close()

    return things


def savgol_filter(y, window_size, order, deriv=0, rate=1):
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # pre-compute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window+1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


def make_html(table):
    entries = db_lookup(Tables(table))
    x = []
    y = []
    for entry in entries:
        temp, time = entry
        x.append(datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f"))
        y.append(temp)
    if table == 3:  # does fix for water level being inverted
        y = [24 - x for x in y]
    y_prime = np.array(y)
    y_prime = savgol_filter(y_prime, 301, 3)

    p = figure(x_axis_type="datetime", plot_width=800, plot_height=300)

    blues = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#084594']
    color_mapper = LinearColorMapper(palette=blues, low=min(y), high=max(y))

    if table == 1:  # temperature
        p = figure(x_axis_type="datetime", plot_width=800, plot_height=300, y_range=(65, 85))
        color_mapper = LinearColorMapper(palette='Magma256', low=min(y), high=max(y))
    elif table == 3:
        p = figure(x_axis_type="datetime", plot_width=800, plot_height=300, y_range=(15, 24))
    elif table == 4:  # ph
        p = figure(x_axis_type="datetime", plot_width=800, plot_height=300, y_range=(0, 14))
    p.scatter(x, y, color={'field': 'y', 'transform': color_mapper}, size=12, line_color="#333333")
    p.line(x, y_prime, line_dash="5 7", line_width=2, color='gray')
    # cr = p.circle(x, y, size=20, hover_fill_color="firebrick",
    #               fill_alpha=0.2, hover_alpha=0.6,
    #               line_color=None, hover_line_color="white")

    # p.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='vline'))
    p.yaxis.axis_label = str(Tables(table)).split('.')[1]
    p.xaxis.axis_label = "Time"
    p.toolbar.logo = None
    p.toolbar_location = None
    p.sizing_mode = 'scale_both'

    script, div = components(p)

    with open("__HOME__/final_project/graphs.html") as output:
        output = output.read().format(Tables(table).name.title(), script, div)

    return output


def make_alert(l, low, high):
    if not (low <= float(l[-1][0]) <= high):  # if the most recent one is not in the range!!!
        for i in range(0, 3):  # if we've alerted for any of the past 3 entries
            if not (low <= float(l[i][0]) <= high):  # if something is not in the range, we've already alerted
                return False
        return True
    else:  # we're all good :)
        return False


def request_handler(request):
    if request["method"] == "GET":  # this means that the user is requesting the webpage
        table = request["values"].get("table", 1)
        return make_html(int(table))
    else:  # the user is posting some data about the fish tank
        value = float(request["values"]["value"])
        sensor = Tables(int(request["values"]["sensor"]))
        db_insert(sensor, value)

        ph_alert, temp_alert, level_alert, turbidity_alert = False, False, False, False

        if sensor == Tables.temperature:
            temps = db_lookup(Tables(1))[-4:]
            temp_alert = make_alert(temps, temperature_low, temperature_high)
            requests.get("http://blynk-cloud.com/e59f25208cd64dd78eb0e6b587bf978f/update/V0", {"value": value})
        elif sensor == Tables.turbidity:
            turbidity = db_lookup(Tables(2))[-4:]
            turbidity_alert = make_alert(turbidity, turbidy_low, float("inf"))
        elif sensor == Tables.waterlevel:
            levels = db_lookup(Tables(3))[-4:]
            level_alert = make_alert(levels, waterlevel, float("inf"))
        else:
            phs = db_lookup(Tables(4))[-4:]
            ph_alert = make_alert(phs, ph_low, ph_high)

        if any([ph_alert, temp_alert, level_alert, turbidity_alert]):
            # alerts.alert_all()
            return "ON"
        return "OFF"


# db_create()
# db_insert(Tables(1), 77.8)
# db_insert(Tables(1), 78.9)
# db_insert(Tables(1), 77.7)
# db_insert(Tables(1), 77.4)
# db_insert(Tables(1), 77.2)
# db_insert(Tables(2), 4.98)
# db_insert(Tables(2), 4.98)
# db_insert(Tables(2), 4.96)
# db_insert(Tables(2), 4.97)
# db_insert(Tables(2), 4.95)
# db_insert(Tables(3), 0.51)
# db_insert(Tables(3), 0.72)
# db_insert(Tables(3), 0.52)
# db_insert(Tables(3), 1.22)
# db_insert(Tables(3), 0.93)
# db_insert(Tables(4), 6.62)
# db_insert(Tables(4), 6.70)
# db_insert(Tables(4), 6.66)
# db_insert(Tables(4), 6.69)
# db_insert(Tables(4), 6.72)

# request_handler({"method": "POST", "values": {"temp": 74}})
