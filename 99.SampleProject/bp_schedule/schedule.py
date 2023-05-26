from flask import Blueprint, request, render_template, session, current_app
from flask import redirect, flash
import json, os, calendar
from datetime import date, timedelta
import my_util.sched_util as su
import db_sqlite.anniversary_dao as adao

schdedule_bp = Blueprint('schdedule_bp', __name__)
menu = {'ho':0, 'us':0, 'cr':0, 'sc':1}

@schdedule_bp.route('/calendar/<arrow>')
def calendar_func(arrow):
    today = date.today()
    date_name = '월 화 수 목 금 토 일'.split()[today.weekday()]
    year = today.year
    month = today.month
    today = f'{year}-{month:02d}-{today.day:02d}({date_name})'
    try: 
        _ = session['year']
        year = int(session['year'])
        month = int(session['month'])
    except:
        pass

    if arrow == 'left':
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    elif arrow == 'right':
        month += 1
        if month == 13:
            year, month = year + 1, 1
    elif arrow == 'left2':
        year -= 1
    elif arrow == 'right2':
        year += 1
    session['year'] = str(year)
    session['month'] = str(month)

    first_day = date(year, month, 1)
    first_date = first_day.weekday()
    last_day = calendar.monthrange(year, month)[1]
    last_date = date(year, month, last_day).weekday()

    schedule_month = []
    number_of_weeks = 0
    # 첫번째 주
    week = []
    if first_date != 6:
        prev_sunday = first_day - timedelta(days=(first_date+1)%7)
        for i in range(first_date+1):
            oneday = prev_sunday + timedelta(days=i)
            week.append(su.gen_schday(oneday, month, session['uid']))
    for k, i in enumerate(range((first_date + 1) % 7, 7)):
        oneday = date(year, month, k+1)
        week.append(su.gen_schday(oneday, month, session['uid']))
    schedule_month.append(week)
    number_of_weeks += 1

    # 둘째 주 ~ 마지막 전 주
    day = 8 - (first_date+1) % 7
    duration = last_day - day + 1
    count = duration // 7
    for i in range(count):
        week = []
        for k in range(7):
            oneday = date(year, month, i*7+k+day)
            week.append(su.gen_schday(oneday, month, session['uid']))
        schedule_month.append(week)
    number_of_weeks += count

    # 마지막 주
    if count * 7 + day <= last_day:
        start_day = count * 7 + day
        week = []
        for i in range(7):
            oneday = date(year, month, start_day) + timedelta(days=i)
            week.append(su.gen_schday(oneday, month, session['uid']))
        schedule_month.append(week)
        number_of_weeks += 1

    time_list = su.gen_time()
    return render_template('schedule/calendar.html', menu=menu, 
                           today=today, year=year, month=f'{month:02d}', timeList=time_list,
                           schedule_month=schedule_month, number_of_weeks=number_of_weeks)

@schdedule_bp.route('/insertAnniv', methods=['POST'])
def insert_anniv():
    title = request.form['title']
    anniv_date = request.form['annivDate'].replace('-','')
    try:
        _ = request.form['holiday']
        is_holiday = 1
    except:
        is_holiday = 0

    adao.insert_anniv((title, anniv_date, is_holiday))
    return redirect('/schedule/calendar/this')
