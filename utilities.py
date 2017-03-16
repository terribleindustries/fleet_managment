import re
from settings import *
import MySQLdb
import hashlib
import getpass
import arrow
from twilio.rest import TwilioRestClient
import bcrypt

def Sanatize(str):
    return re.sub('[^a-zA-Z0-9 \']+', '',str) 


def check_db():
    try:
        myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='trucking')
        c = myDB.cursor()
        c.execute("SELECT * from payloads")
        result = c.fetchone()
        return True
    except:
        return False

def setup_db():
    root_pass = getpass.getpass("mysql root pass:")
    myDB = MySQLdb.connect(host='localhost', port=3306, user='root', passwd=root_pass)
    c = myDB.cursor()
    c.execute('CREATE DATABASE IF NOT EXISTS trucking;')
    myDB.commit()
    c.execute('USE trucking;')
    c.execute('CREATE TABLE IF NOT EXISTS `admin` (user varchar(25), password varchar(64));')
    myDB.commit()
    c.execute("""
    CREATE TABLE IF NOT EXISTS `payloads` (id MEDIUMINT NOT NULL AUTO_INCREMENT, payload varchar(255), src varchar(255), dst varchar(255), 
    weight INT, customer_name varchar(255), truck_id varchar(255), assigned_time varchar(255), delivered_time varchar(255), PRIMARY KEY (id));
    """)
    myDB.commit()
    c.execute("""
    CREATE TABLE IF NOT EXISTS `trucks` (id MEDIUMINT NOT NULL AUTO_INCREMENT, truck_id varchar(255), trucker_name varchar(255), PRIMARY KEY (id));
    """)
    myDB.commit()
    user = raw_input("admin's username:")
    password = getpass.getpass("password:")
    check_password = getpass.getpass("retype password:")
    while (password != check_password):
        print 'ERROR! passwords do not match:'
        password = getpass.getpass("password:")
        check_password = getpass.getpass("retype password:")
    if USE_BCRYPT:
        hashed_pass = bcrypt.hashpw(password, bcrypt.gensalt())
    else:
        m = hashlib.sha256()
        m.update(password)
        hashed_pass = m.digest().encode('hex')
    # print hashed_pass
    c.execute("INSERT INTO admin (user, password) VALUES (%s,%s)", (user, hashed_pass))
    try:
        c.execute("CREATE USER '{}'@'localhost' IDENTIFIED BY '{}';".format(DB_USER_USER, DB_USER_PASS))
        c.execute("CREATE USER '{}'@'%' IDENTIFIED BY '{}';".format(DB_USER_USER, DB_USER_PASS))
    except:
        pass
    c.execute("flush privileges;")
    c.execute("GRANT ALL on *.* to '{}'@'localhost';".format(DB_USER_USER))
    c.execute("GRANT ALL on *.* to '{}'@'%';".format(DB_USER_USER))
    c.execute("flush privileges;")
    myDB.commit()
    myDB.close()

def authenticate_user(user, password, lock):
    with lock:
        myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='trucking')
        cursor = myDB.cursor()
        cursor.execute("SELECT password FROM admin WHERE user=%s", (user,))
        result=cursor.fetchone()
        if result is not None and len(result) > 0:
            if USE_BCRYPT:
                entered_pass = password.encode('utf-8')
                hashed = result[0].encode('utf-8')
                return bcrypt.hashpw(entered_pass, hashed) == hashed
            else:
                m = hashlib.sha256()
                m.update(password)
                entered_pass = m.digest().encode('hex')
                return entered_pass == result[0]
        return False

def input_new_order(payload, src, dst, weight, customer_name, lock):
    with lock:
        myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='trucking')
        cursor = myDB.cursor()
        cursor.execute("INSERT INTO payloads (payload, src, dst, weight, customer_name) VALUES ('{}', '{}', '{}', '{}', '{}')".format(payload, src, dst, weight, customer_name))
        myDB.commit()

def assign_payload(truck_id, lock):
    cur_time = arrow.now().format(DATE_FORMAT)
    with lock:
        myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='trucking')
        cursor = myDB.cursor()
        cursor.execute("SELECT * FROM payloads WHERE truck_id IS NULL LIMIT 1;")
        cur_num = cursor.fetchone()
        if not cur_num:
            return None
        cursor.execute("UPDATE payloads SET truck_id='{}', assigned_time='{}' WHERE id={}".format(truck_id, cur_time, cur_num[0]))
        myDB.commit()
        return cur_num

def mark_complete(payload_id, lock):
    cur_time = arrow.now().format(DATE_FORMAT)
    with lock:
        myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='trucking')
        cursor = myDB.cursor()
        cursor.execute("UPDATE payloads SET delivered_time = '{}' WHERE id={};".format(cur_time,payload_id))
        myDB.commit()

