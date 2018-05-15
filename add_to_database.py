import sqlite3
import datetime
from enum import Enum
import random
import math


fish_database = "fish_database.db"  # just come up with name of database


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

    time_delta = datetime.datetime.now() - datetime.timedelta(hours=24)

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


try:
    db_create()
except:
    pass
# for x in range(100):  # pick a 100 datapoints
#     rand = random.randint(-10, 10)
#     y = 85 + 30*math.sin(x/30) + rand
#     y2 = random.randint(0, 100)
#     y3 = 30 + -1*x + rand/2
#     y4 = y2
#
#     db_insert(Tables(1), y)
#     db_insert(Tables(2), y2)
#     db_insert(Tables(3), y3)
#     db_insert(Tables(4), y4)

