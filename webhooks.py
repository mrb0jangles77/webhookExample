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
link = 'http://54.164.47.138/cgi-bin/webhooks/webhooks.py'
conn = MySQLdb.connect(host=host, user=user, passwd=passwrd, db=db)

def respond_404():
    print("Status: 404 Not Found")
    print()

def respond_405():
    print("Status: 405 Method Not Allowed")
    print()

def postHandler(inputData):
    real = json.loads(input_data)
    for elem in real.keys():
        body = real[elem]
        cursor = conn.cursor()
        cursor.execute("INSERT into webhooks(time, body) values(NOW(), %s)", (body,))
        #results = cursor.fetchall()
        conn.commit()
        cursor.close()
        limit()
    print("Status: 302 Redirect")
    print("Location: http://54.164.47.138/cgi-bin/webhooks/webhooks.py/receiver")
    print()

def limit():
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM webhooks ORDER BY time")
    #count = cursor.rowcount
    results = cursor.fetchall()
    #conn.close()
    if len(results) > 7:
        #cursor = conn.cursor()
        cursor.execute("DELETE FROM webhooks WHERE id = %s", (results[0],))
        conn.commit()
        cursor.close()        

def getHandler():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM webhooks")
    results = cursor.fetchall()
    cursor.close()
    print("Status: 200 OK")
    print("Content-Type: text/html")
    print()
    print("<html><body><table><tr><td>ID&nbsp&nbsp</td><td>Time&nbsp&nbsp</td><td>Text&nbsp&nbsp</td></tr>")
    for elem in results:
        print("""<tr><td>{}</td><td>{}</td>
        <td><div><pre>{}</pre></div></td></tr>""".format(elem[0],elem[1], elem[2]))
    print("</table></body></html>")



if "PATH_INFO" in os.environ:
    my_path = os.environ["PATH_INFO"]
    link += my_path
    request = os.environ["REQUEST_METHOD"]
    my_path = my_path.strip('/').split('/')
    if request == 'POST' and my_path[0] == 'receiver':
        input_data = sys.stdin.read()
        print("Status: 200 OK")
        print("Content-Type: text/html")
        print()
        postHandler(input_data)
    elif request == 'GET' and my_path[0] == 'reviewer':
        getHandler()
    else:
        print("Status: 302 Redirect")
        print("Location: http://54.164.47.138/cgi-bin/webhooks/webhooks.py/reviewer")
        print()

else:
    print("Status: 302 Redirect")
    print("Location: http://54.164.47.138/cgi-bin/webhooks/webhooks.py/reviewer")
    print()
    
