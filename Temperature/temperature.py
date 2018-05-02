from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.embed import components
from math import factorial
import sqlite3
import datetime
import numpy as np
import sys

sys.path.append('__HOME__/final_project/')  # changes the directory so that I can call other python scripts
import alerts

# example_db = "__HOME__/final_project/temperature.db"  # just come up with name of database
example_db = "temperature.db"  # just come up with name of database


def db_create():
    conn = sqlite3.connect(example_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute('''CREATE TABLE temp_table (temp float, timing timestamp);''')  # run a CREATE TABLE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database


def db_insert(temp):
    conn = sqlite3.connect(example_db)  # connect to that database
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute('''INSERT into temp_table VALUES (?,?);''', (temp, datetime.datetime.now()))  # with time
    conn.commit()  # commit commands
    conn.close()  # close connection to database


def db_lookup():
    conn = sqlite3.connect(example_db)
    c = conn.cursor()

    time_delta = datetime.datetime.now() - datetime.timedelta(
        hours=24)
    things = c.execute('''SELECT * FROM temp_table WHERE timing > ? ORDER BY timing ASC;''',
                       (time_delta,)).fetchall()

    conn.commit()
    conn.close()
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
    half_window = (window_size - 1) // 2
    # pre-compute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window+1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


temp_threshold = 78


def request_handler(request):

    if request["method"] == "GET":
        entries = db_lookup()
        x = []
        y = []
        for entry in entries:
            temp, time = entry
            x.append(datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f"))
            y.append(temp)
        y_prime = np.array(y)
        y_prime = savgol_filter(y_prime, 51, 3)

        p = figure(plot_width=800, plot_height=400, x_axis_type="datetime")

        p.line(x, y_prime, line_dash="4 4", line_width=1, color="gray")
        cr = p.circle(x, y, size=20, hover_fill_color="firebrick",
                      fill_alpha=0.05, hover_alpha=0.3,
                      line_color=None, hover_line_color="white")

        p.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='vline'))
        p.yaxis.axis_label = "Temperature (°F)"
        p.xaxis.axis_label = "Time"
        script, div = components(p)

        output = r"""<!DOCTYPE html>
        <html lang="en">
            <!-- <meta http-equiv="Refresh" content="5"> -->
            <head>
                <meta charset="utf-8">
                <title>Temperature Graphs</title>
                
                <link rel="stylesheet" href="http://cdn.pydata.org/bokeh/release/bokeh-0.12.13.min.css" type="text/css" />
                <script type="text/javascript" src="http://cdn.pydata.org/bokeh/release/bokeh-0.12.13.min.js"></script>
                {}
            </head>
            <body>
                {}
            </body>
        </html>""".format(script, div)
        return output
    else:
        temp = float(request["values"]["temp"])
        if temp >= temp_threshold:
            alert = True
            for entry in db_lookup()[-3:]:  # if any of the last 3 were also over, don't alert again.
                if entry[0] >= temp_threshold:
                    alert = False
            if alert:
                alerts.alert_all(temp_threshold)
        db_insert(temp)

    return None


# db_create()
db_insert(70)
print(db_lookup())
# request_handler({"method": "POST", "values": {"temp": 74}})
