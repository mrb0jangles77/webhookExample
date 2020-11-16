#! /usr/bin/python3

import os
import sys
import MySQLdb
import passwords
import json
import cgi
import cgitb
cgitb.enable()

credentials = passwords.Passwords()
host = credentials.getHost()
user = credentials.getUser()
passwrd = credentials.getPass()
db = credentials.getDB()
link = 'http://54.164.47.138/cgi-bin/my_pets/pets.py'
conn = MySQLdb.connect(host=host, user=user, passwd=passwrd, db=db)

def doGetAll(table, link):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM {}".format(table,))
    results = cursor.fetchall()
    cursor.close()
    toDump = []
    for elem in results:
        temp = {}
        temp['ID'] = elem[0]
        temp['First Name'] = elem[1]
        temp['Last Nane'] = elem[2]
        temp['City'] = elem[3]
        if link[-1] == '/':
            temp['Link'] = link + str(elem[0])
        else:
            temp['Link'] = link + '/' + str(elem[0])
        toDump.append(temp)
    print("Status: 200 OK")
    print("Content-Type: application/json")
    print()
    print(json.dumps(toDump, indent=4))

def doGet(table, link, key):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM {} WHERE id = %s".format(table,), (key,))
    results = cursor.fetchall()
    cursor.close()
    if len(results) < 1:
        respond_404()
    else:
        toDump = []
        for elem in results:
            temp = {}
            temp['ID'] = elem[0]
            temp['First Name'] = elem[1]
            temp['Last Nane'] = elem[2]
            temp['City'] = elem[3]
            temp['Link'] = link
            toDump.append(temp)
        print("Status: 200 OK")
        print("Content-Type: application/json")
        print()
        print(json.dumps(toDump, indent=4))

def respond_404():
    print("Status: 404 Not Found")
    print()

def respond_405():
    print("Status: 405 Method Not Allowed")
    print()

def delete(table, key):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM {} WHERE id = %s".format(table,), (key,))
    results = cursor.fetchall()
    cursor.close()
    if table != 'people':
        respond_404()
    else:        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pets WHERE peopleID = %s", (key,))
        cursor.close()
        cursor = conn.cursor()
        cursor.execute("Delete FROM people WHERE id = %s", (key,))
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        if int(count) < 1:
            respond_404()
            return
        print("Status: 302 Redirect")
        print("Location: http://54.164.47.138/cgi-bin/my_pets/pets.py/people")
        print()

def put(real):
    key = real['id']
    name = real['name']
    cursor = conn.cursor()
    cursor.execute("update pets set name=%s where id=%s", (name,key,))
    conn.commit()
    cursor.close()
    print("Status: 302 Redirect")
    print("Location: http://54.164.47.138/cgi-bin/my_pets/pets.py/pets")
    print()
    
def postPeople(real):
    actual = {}
    if 'first' in real.keys():
        actual['first'] = real['first']
    else:
        real['first'] = ''
    if 'last' in real.keys():
        actual['last'] = real['last']
    else:
        real['last'] = ''
    if 'city' in real.keys():
        actual['city'] = real['city']
    else:
        actual['city'] = ''
    cursor = conn.cursor()
    cursor.execute("INSERT INTO people(first,last,city) values(%s, %s, %s)", (actual['first'], actual['last'], actual['city']))
    conn.commit()
    cursor.close()
    print("Status: 302 Redirect")
    print("Location: http://54.164.47.138/cgi-bin/my_pets/pets.py/people")
    print()


def postPets(real):
    actual = {}
    if 'name' in real.keys():
        actual['name'] = real['name']
    else:
        real['name'] = ''
    if 'breed' in real.keys():
        actual['breed'] = real['breed']
    else:
        real['breed'] = ''
    if 'peopleID' in real.keys():
        actual['peopleID'] = real['peopleID']
    else:
        actual['peopleID'] = 1
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pets(name,breed,peopleID) values(%s, %s, %s)", (actual['name'], actual['breed'], actual['peopleID']))
    conn.commit()
    cursor.close()
    print("Status: 302 Redirect")
    print("Location: http://54.164.47.138/cgi-bin/my_pets/pets.py/pets")
    print()


if "PATH_INFO" in os.environ:
    my_path = os.environ["PATH_INFO"]
    link += my_path
    request = os.environ["REQUEST_METHOD"]
    my_path = my_path.strip('/').split('/')
    if request == 'GET':
        table = my_path[0]
        if len(my_path) < 2:
            doGetAll(table,link)
        else:
            key = int(my_path[1])
            doGet(table,link,key)
    elif request == 'POST':
        table = my_path[0]
        input_data = sys.stdin.read()
        real = json.loads(input_data)
        if table == 'people':
            putPeople(real)
        else:
            putPets(real)
    elif request == 'DELETE':
        table = my_path[0]
        key = int(my_path[1])
        delete(table, key)
    elif request == 'PUT':
        # Just in case a user uses POST operation with a path_info value
        # path_info value will be ignored.
        input_data = sys.stdin.read()
        real = json.loads(input_data)
        put(real)
    else:
        respond_405()
elif os.environ["REQUEST_METHOD"] == 'PUT':
    input_data = sys.stdin.read()
    real = json.loads(input_data)
    put(real)
else:
    respond_404()


