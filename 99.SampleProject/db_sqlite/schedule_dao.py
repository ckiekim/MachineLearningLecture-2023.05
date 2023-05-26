import sqlite3

def get_sched(sid):
    conn = sqlite3.connect('./db_sqlite/project.db')
    cur = conn.cursor()

    sql = 'select * from schedule where sid=?'
    cur.execute(sql, (sid,))
    row = cur.fetchall()

    cur.close()
    conn.close()
    return row

def get_sched_list(params):
    conn = sqlite3.connect('./db_sqlite/project.db')
    cur = conn.cursor()

    sql = 'select * from schedule where uid=? and sdate=? order by start_time'
    cur.execute(sql, params)        # (uid, sdate)
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows

def insert_sched(params):
    conn = sqlite3.connect('./db_sqlite/project.db')
    cur = conn.cursor()

    sql = 'insert into schedule(uid, sdate, title, place, start_time, end_time, is_important, memo) values(?, ?, ?, ?, ?, ?, ?, ?)'
    cur.execute(sql, params)
    conn.commit()

    cur.close()
    conn.close()
