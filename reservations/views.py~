# coding:utf-8
from django.http import HttpResponseRedirect
from django.contrib.auth import logout, authenticate
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError

from django.contrib.auth.models import User
from .models import Record

import sys
import sqlite3
import smtplib
import sched
import time
import datetime
import os
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def check_overlapping(time1, time2):
    # check whether the two time periods overlap
    if (time1[1] <= time2[0]) or (time2[1] <= time1[0]):
        return False
    else:
        return True


def check_reservation_time(start_time, end_time):
#########################################################################################################
#     rules:
#     - the start time should be prior to the end time
#     - the start time should be later than or equal to the time being
#     - only reservations for this week and the following week can be made
#     - the longest time for a single reservation is 3 hours
#     - reservations should lie within a day
#     - new reservation must not overlap with the existed 
#########################################################################################################
    now = datetime.datetime.now()
    if start_time >= end_time:
        #return (False, "start time should be prior to the end time")
        return (False, "开始时间必须早于结束时间！")
    if start_time < now:
        #return (False, "start time should be later than or same with the current time")
        return (False, "开始时间必须晚于当前时间！")
    if end_time >= datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days = (14 - now.weekday())):
        #return (False, "please make reservation for this week and the next week")
        return (False, "只能够预约这周和下周的时间！")
    if start_time.day != end_time.day:
        #return (False, "please make reservation within a single day")
        return (False, "请不要预约超过一天！")
    if end_time - start_time > datetime.timedelta(hours=3):
        #return (False, "the longest time is 3 hours")
        return (False, "一次性最长预约3小时！")
    
    records_of_same_day = Record.objects.filter(
        start_time__gte=datetime.datetime(start_time.year, start_time.month, start_time.day)).filter(
        start_time__lte=(datetime.datetime(start_time.year, start_time.month, start_time.day) +
        datetime.timedelta(days=1)))
    for record in records_of_same_day:
        # if your reservation period overlaps with any of the existed, it is invalid
        if check_overlapping((start_time, end_time), (record.start_time, record.end_time)):
            #return (False, "Your reservation overlaps the existed")
            return (False, "该时间段与已有预约重叠！")
    
    return (True,'you are good to go')
    
    
def welcome(request):
    this_week_past = []
    this_week_future = []
    next_week = []
    now = datetime.datetime.now()
    this_week_first_moment = datetime.datetime(now.year, now.month, now.day)
    this_week_first_moment -= datetime.timedelta(days=now.weekday())
    this_week_last_moment = datetime.datetime(now.year, now.month, now.day)
    this_week_last_moment += datetime.timedelta(days=(7-now.weekday()))
    
    if request.user.is_authenticated():
        status = True
        id_name = request.user.last_name
    else:
        status = False
        id_name = ''
    
    for record in Record.objects.all():
        time_stamp = record.start_time
        if time_stamp > this_week_last_moment:
            next_week.append(record)
        elif time_stamp < this_week_first_moment:
            continue
        elif time_stamp > now:
            this_week_future.append(record)
        elif time_stamp < now:
            this_week_past.append(record)
        else:
            raise RuntimeError("the time is weird in record: %s" % record.get_username())

    all_records = []
    filtered_records = []
    all_records.extend(this_week_past)
    all_records.extend(this_week_future)
    all_records.extend(next_week)
    id = 1
    for item in all_records:
        d = {
                "id":id,
                "start":item.start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                "end":item.end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                "title":item.user.last_name
            }
        filtered_records.append(d)
        id += 1
    if id == 1:
        filtered_records = ""
    
    context = {
        "this_week_past": this_week_past,
        "this_week_future": this_week_future,
        "next_week": next_week,
        "status": status,
        "id_name": id_name,
        "records": filtered_records,
    }
    
    return render(request, "reservations/welcome.html", context)


@login_required(login_url='reservations:auth_login')
def add_reservation(request):
    if request.user.is_authenticated():
        context = {
            'applicant_name': request.user.last_name,
        }
        return render(request, "reservations/add_reservation.html", context)
    else:
        raise Http404("You don't have the access, please log in.")


@login_required(login_url='reservations:auth_login')
def cancle_reservation(request):
    if request.user.is_authenticated():
        available_records_1 = Record.objects.filter(
            start_time__gte=datetime.datetime.now())
        available_records_2 = [
            record for record in available_records_1 if record.user.username == request.user.username]
        context = {
            "available_records": available_records_2
        }
        return render(request, "reservations/cancle_reservation.html", context)
    else:
        raise Http404("You don't have the access, please log in.")


@login_required(login_url='reservations:auth_login')
def add_reservation_submit(request):
    now = datetime.datetime.now()
    # applicant = request.POST['applicant']
    applicant = request.user.username

    reservation_date = request.POST['reservation_date']
    reservation_month = int(reservation_date.split('-')[1])
    reservation_day = int(reservation_date.split('-')[0])

    start_hour = int(request.POST['start_hour'])
    start_minute = int(request.POST['start_minute'])
    end_hour = int(request.POST['end_hour'])
    end_minute = int(request.POST['end_minute'])
    
    start_time_form = datetime.datetime(
        now.year, reservation_month, reservation_day, start_hour, start_minute)
    end_time_form = datetime.datetime(
        now.year, reservation_month, reservation_day, end_hour, end_minute)
    flag = check_reservation_time(start_time_form, end_time_form)
    if not (flag[0]):
        raise Http404(flag[1])
    
    user_list = User.objects.all()
    if applicant in [i.get_username() for i in user_list]:
        new_record = Record()
        new_record.start_time = start_time_form
        new_record.end_time = end_time_form
        new_record.user =  User.objects.filter(username=applicant)[0]
        new_record.save()
        return HttpResponseRedirect(reverse('reservations:index'))
    else:
        raise Http404("The applicant does not exits. Reservation denied !")


@login_required(login_url='reservations:auth_login')
def cancle_reservation_submit(request):
    delete_id_list = request.POST.getlist("checkbox_list")
    for id in delete_id_list:
        record = Record.objects.filter(id=id)[0]
        record.delete()
    return HttpResponseRedirect(reverse('reservations:index'))


def user_logout(request):
    if request.user.is_authenticated():
        logout(request)
        return render(request, "registration/logout.html")
    else:
        return HttpResponseRedirect(reverse('reservations:index'))


def user_create_user(request):
    return render(request, 'registration/create_user.html')


def user_create_user_submit(request):
    username = request.POST['applicant']
    password = request.POST['password']
    email_address = request.POST['email_address']
    
    # nickname is stored as last_name
    nickname = request.POST['nickname']
    
    users = User.objects.all()
    if nickname in [i.last_name for i in users]:
        # forbidden because the nickname has been taken
        raise Http404("the nickname has been taken !")
    
    try:      
        user = User.objects.create_user(username, email_address, password, last_name=nickname)
    except IntegrityError:
        # error occurred because the user name has been taken
        raise Http404("the user name has been taken")
    
    user.is_active = False
    user.save()
    return render(request, 'registration/is_active_false.html')


@login_required(login_url='reservations:auth_login')
def password_change(request):
    context = {
        "id_name": request.user.last_name}
    return render(request, 'registration/password_change.html', context)


@login_required(login_url='reservations:auth_login')
def password_change_submit(request):
    u = User.objects.get(username__exact=request.user.username)
    u.set_password(request.POST["password"])
    u.save()
    return render(request, 'registration/password_change_success.html')


@login_required(login_url='reservations:index')
def clean_old_records(request):
    #if request.user.username == "admin":
    if request.user.username == "huweiming":
        return render(request, 'reservations/clean_old_records.html')
    else:
        return HttpResponseRedirect(reverse('reservations:index'))


@login_required(login_url='reservations:index')
def clean_old_records_submit(request):
    # format should be 2016-04-23 18:00:00
    now = datetime.datetime.now()
    format_time = "{year}-{month}-{day} {hour}:{minute}:{second}".format(
            year = now.year,
            month = request.POST["clean_month"],
            day = request.POST["clean_day"],
            hour = 0,
            minute = 0,
            second = 0)
    send_email(format_time)
    delete_records_older_than_one_month(format_time)
    return HttpResponseRedirect(reverse('reservations:index'))


@login_required(login_url='reservations:index')
def show_items_to_delete(request):
    format_time = "{year}-{month}-{day} {hour}:{minute}:{second}".format(
            year = datetime.datetime.now().year,
            month = int(request.GET['form_month']),
            day = int(request.GET['form_day']),
            hour = 0,
            minute = 0,
            second = 0)
    execute_result = Record.objects.filter(end_time__lte = format_time)
    return HttpResponse(len(execute_result))


def delete_records_older_than_one_month(format_time):
    execute_result = Record.objects.filter(end_time__lte = format_time)
    for item in execute_result:
        item.delete()
    

def prepare_attachment(format_time):
    execute_result = Record.objects.filter(end_time__lte = format_time)
    result = []
    for item in execute_result:
        l = ["Start time", "End time", "User name"]
        l[0] = item.start_time.strftime("%Y-%m-%d %H:%M:%S")
        l[1] = item.end_time.strftime("%Y-%m-%d %H:%M:%S")
        l[2] = item.user.get_username()
        result.append(l)
    
    # write attachment
    with open('attachment.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Start time", "End time", "User name"])
        for line in result:
            writer.writerow(line)
        return True


def send_email(format_time):
    sender = "reservation_rec@sina.com"
    password = "qingyinshe"
    receivers = ["409498637@qq.com"]
    smtp_server = "smtp.sina.com"
    
    # set email content
    message = MIMEMultipart()
    message['Subject'] = "过期预约信息"
    message['From'] = "<reservation_rec@sina.com>"
    message['To'] = ";".join(receivers)
    
    if prepare_attachment(format_time):
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

def check_exist_account(request):
    # check exist account
    # return false when the account or the nickname has already been used
    account = request.GET.get("account")
    nickname = request.GET.get("nickname")
    result = ['0', '0']
    for user in User.objects.all():
        if account == user.username:
            result[0] = '1'
        if nickname == user.last_name:
            result[1] = '1'
    return HttpResponse(','.join(result))


@login_required(login_url='reservations:auth_login')
def add_reservation_check(request):
    now = datetime.datetime.now()
    applicant = request.user.username

    reservation_date = request.GET['form_date']
    reservation_month = int(reservation_date.split('-')[1])
    reservation_day = int(reservation_date.split('-')[0])

    start_hour = int(request.GET['start_hour'])
    start_minute = int(request.GET['start_minute'])
    end_hour = int(request.GET['end_hour'])
    end_minute = int(request.GET['end_minute'])
    
    start_time_form = datetime.datetime(
        now.year, reservation_month, reservation_day, start_hour, start_minute)
    end_time_form = datetime.datetime(
        now.year, reservation_month, reservation_day, end_hour, end_minute)
    flag = check_reservation_time(start_time_form, end_time_form)
    if (flag[0]):
        return HttpResponse("OK")
    else:
        return HttpResponse(flag[1])
