# coding: utf-8
#===============================================================================
# This module will send weekly the records of a month ago to designated email address,
# and then delete these records from the database.
# 
# Event time each week : Monday 4:00 am
# Event function: send email and delete old records of more than a month ago
#===============================================================================

import sqlite3
import smtplib
import sched
import time
import datetime
import os
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#===============================================================================
# debug:
# 1. fix next_monday_4_00_am as commented
#===============================================================================

s = sched.scheduler(time.time, time.sleep)

def delete_records_older_than_one_month(format_time):
    sql_server = sqlite3.connect("db.sqlite3")
    cur = sql_server.cursor()
    cur.execute("DELETE FROM reservations_record where end_time < '%s'" % format_time)
    sql_server.close()

def prepare_attachment(format_time):
    sql_server = sqlite3.connect("db.sqlite3")
    cur = sql_server.cursor()
    
    cur.execute("SELECT start_time, end_time, user_id FROM reservations_record WHERE end_time < '%s'" % format_time)
    execute_result = cur.fetchall()
    result = []
    for item in execute_result:
        l = list(item)
        cur.execute("SELECT username FROM auth_user WHERE id = %s" % str(item[2]))
        l[2] = cur.fetchall()[0][0]
        result.append(l)
    sql_server.close()
    
    # write attachment
    writer = csv.writer(file('attachment.csv', 'w'))
    writer.writerow(["Start time", "End time", "User name"])
     
    for line in result:
        writer.writerow(line)
    return True

def send_email():
    sender = "reservation_rec@sina.com"
    password = "qingyinshe"
    receivers = ["409498637@qq.com"]
    smtp_server = "smtp.sina.com"
    
    # set email content
    message = MIMEMultipart()
    message['Subject'] = "过期预约信息"
    message['From'] = "轻音社在线预约系统<reservation_rec@sina.com>"
    message['To'] = ";".join(receivers)
    
    if prepare_attachment():
        # create attachment
        att1 = MIMEText(open('attachment.csv', 'r').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = 'attachment; filename="records.csv"'
        message.attach(att1)
        os.remove('attachment.csv')
    
    # send email
    try:
        smtpObj = smtplib.SMTP(smtp_server)
        smtpObj.starttls()
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print ("succeed !")
    except smtplib.SMTPException:
        print ("Error: smtplib.SMTPException")
    finally:
        smtpObj.quit()

def event():
    # format should be 2016-04-23 18:00:00
    now = datetime.datetime.now()
    target_time = now + datetime.timedelta(days=-7)
    format_time = "{year}-{month}-{day} {hour}:{minute}:{second}".format(
        year = target_time.year,
        month = target_time.month,
        day = target_time.day,
        hour = target_time.hour,
        minute = target_time.minute,
        second = target_time.second)
    send_email(format_time)
    delete_records_older_than_one_month(format_time)

def perform():    
    global s
    now = datetime.datetime.now()
    # next_monday_4_00_am = datetime.datetime(now.year, now.month, now.day, 4, 0, 0) + datetime.timedelta(days = (7 - now.weekday()))
    # for test
    next_monday_4_00_am = datetime.datetime(now.year, now.month, now.day, 4, 0, 0) + datetime.timedelta(days =1)
    delta = next_monday_4_00_am - now
    sec_till_next_monday_4_00_am = int(delta.total_seconds())
    
    s.enter(sec_till_next_monday_4_00_am, 0, perform)
    event()

def my_main(inc=10):
    global s
    s.enter(0, 0, perform)
    s.run()

if __name__ == '__main__':
    my_main()
