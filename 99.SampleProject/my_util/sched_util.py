from datetime import date
import db_sqlite.anniversary_dao as adao

# Generate schedule day
def gen_schday(d, session_month):
    schday = {}
    schday['day'] = d.day      # 1 ~ 31
    schday['webDate'] = (d.weekday() + 1) % 7
    anniv_list = adao.get_anniv_list(d.strftime('%Y%m%d'), d.strftime('%Y%m%d'))
    schday['isHoliday'] = 0
    #annivs = []
    for anniv in anniv_list:
        #annivs.append(anniv[1])
        if anniv[3] == 1:
            schday['isHoliday'] = 1
            break
    schday['isOtherMonth'] = 1 if d.month != session_month else 0
    schday['sdate'] = d.strftime('%Y%m%d')
    schday['annivList'] = anniv_list
    schday['schedList'] = None
    return schday
