from flask import Blueprint, request, render_template, session, current_app
from flask import redirect, flash
import hashlib, base64, json, os
import db_sqlite.user_dao as udao

user_bp = Blueprint('user_bp', __name__)
menu = {'ho':0, 'us':1, 'cr':0, 'cb':0, 'sc':0}

@user_bp.route('/login', methods=['GET','POST'])    # localhost:5000/user/login 이 처리되는 곳
def login():
    if request.method == 'GET':
        return render_template('user/login.html')
    else:
        uid = request.form['uid']
        pwd = request.form['pwd']
        user_info = udao.get_user(uid)
        if user_info:
            db_pwd = user_info[1]
            pwd_sha256 = hashlib.sha256(pwd.encode())
            hashed_pwd = base64.b64encode(pwd_sha256.digest()).decode('utf-8')
            if hashed_pwd == db_pwd:
                flash(f'{user_info[2]}님 환영합니다.')        # 초기 화면으로 보내줌
                session['uid'] = uid        # 세션값을 설정함으로써 사용자가 로그인하였음을 알게 해줌
                session['uname'] = user_info[2]
                return redirect('/')
            else:
                flash('비밀번호가 틀립니다.')       # 로그인 화면을 다시 보내줌
                return redirect('/user/login')
        else:
            flash('사용자 ID가 잘못되었습니다.')    # 회원 가입 페이지로 안내
            return redirect('/user/register')

@user_bp.route('/logout')
def logout():
    session.pop('uid', None)       # 설정한 세션값을 삭제 
    session.pop('uname', None)
    session.pop('year', None)
    session.pop('month', None)
    return redirect('/')

@user_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('user/register.html')
    else:
        uid = request.form['uid']
        if udao.get_user(uid):
            flash('이미 사용자 ID가 있습니다. 다른 ID를 사용하세요.')
            return redirect('/user/register')
        pwd = request.form['pwd']
        pwd2 = request.form['pwd2']
        if pwd != pwd2:
            flash('패스워드가 일치하지 않습니다.')
            return redirect('/user/register')
        uname = request.form['uname']
        email = request.form['email']
        pwd_sha256 = hashlib.sha256(pwd.encode())
        hashed_pwd = base64.b64encode(pwd_sha256.digest()).decode('utf-8')
        udao.insert_user((uid, hashed_pwd, uname, email))
        session['uid'] = uid        # 세션값을 설정함으로써 사용자가 로그인하였음을 알게 해줌
        session['uname'] = uname
        return redirect('/')

@user_bp.route('/list')
def list():
    user_list = udao.get_user_list()
    return render_template('user/list.html', user_list=user_list, menu=menu)

@user_bp.route('/update/<uid>', methods=['GET','POST'])
def update(uid):
    user = udao.get_user(uid)
    if request.method == 'GET':
        return render_template('user/update.html', user=user, menu=menu)
    else:
        pwd = request.form['pwd']
        pwd2 = request.form['pwd2']
        if pwd != None and pwd == pwd2:
            pwd_sha256 = hashlib.sha256(pwd.encode())
            hashed_pwd = base64.b64encode(pwd_sha256.digest()).decode('utf-8')
        else:
            hashed_pwd = user[1]
        uname = request.form['uname']
        email = request.form['email']
        udao.update_user((hashed_pwd, uname, email, uid))
        return redirect('/user/list')

@user_bp.route('/delete/<uid>')
def delete(uid):
    return render_template('user/delete.html', uid=uid, menu=menu)

@user_bp.route('/delete_confirm/<uid>')
def delete_confirm(uid):
    udao.delete_user(uid)
    return redirect('/user/logout')