from flask import Flask, render_template, request, redirect, session, flash
from my_util.weather_util import get_weather, get_weather_by_coord
import my_util.crawl_util as cu
import my_util.map_util as mu
import my_util.image_util as iu
import os, random, json
from bp_chatbot.chatbot import chatbot_bp
from bp_user.user import user_bp
from bp_schedule.schedule import schdedule_bp

app = Flask(__name__)
app.secret_key = 'qwert12345'
app.config['SESSION_COOKIE_PATH'] = '/'

app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(schdedule_bp, url_prefix='/schedule')

# flask 2.3 에서는 이 코드만 사용 가능
""" with app.app_context():
    global quote, quotes            # quote, quotes 변수를 전역 변수로 만들어 줌
    global addr
    filename = os.path.join(app.static_folder, 'data/todayQuote.txt')
    with open(filename, encoding='utf-8') as f:
        quotes = f.readlines()
    quote = random.sample(quotes, 1)[0]
    addr = '수원시 장안구' """

@app.before_first_request
def before_first_request():
    global quote, quotes            # quote, quotes 변수를 전역 변수로 만들어 줌
    global addr
    filename = os.path.join(app.static_folder, 'data/todayQuote.txt')
    with open(filename, encoding='utf-8') as f:
        quotes = f.readlines()
    quote = random.sample(quotes, 1)[0]
    session['quote'] = quote
    addr = '수원시 장안구'
    session['addr'] = addr


# for AJAX  #############################
@app.route('/change_quote')
def change_quote():
    global quote
    quote = random.sample(quotes, 1)[0]
    session['quote'] = quote
    return quote

@app.route('/change_addr')
def change_addr():
    global addr
    addr = request.args.get('addr')
    session['addr'] = addr
    return addr

@ app.route('/weather')
def weather():
    addr = request.values['addr']
    lat, lng = mu.get_coord(addr + '청', app)
    html = get_weather_by_coord(app, lat, lng)
    return html

@app.route('/change_profile', methods=['POST'])
def change_profile():
    file_image = request.files['image']
    filename = os.path.join(app.static_folder, f'upload/{file_image.filename}')
    file_image.save(filename)
    mtime = iu.change_profile(app, filename)
    return str(mtime)
#########################################

@app.route('/')
def home():
    menu = {'ho':1, 'us':0, 'cr':0, 'cb':0, 'sc':0}
    return render_template('home.html', menu=menu, weather=get_weather(app),
                           quote=quote, addr=addr)

@app.route('/interpark')
def interpark():
    menu = {'ho':0, 'us':0, 'cr':1, 'cb':0, 'sc':0}
    book_list = cu.interpark()
    return render_template('crawling/interpark.html', book_list=book_list, 
                           menu=menu, weather=get_weather(app), quote=quote, addr=addr)

@app.route('/genie')
def genie():
    menu = {'ho':0, 'us':0, 'cr':1, 'cb':0, 'sc':0}
    song_list = cu.genie()
    return render_template('crawling/genie.html', song_list=song_list, 
                           menu=menu, weather=get_weather(app), quote=quote, addr=addr)

@app.route('/genie_jquery')
def genie_jquery():
    menu = {'ho':0, 'us':0, 'cr':1, 'cb':0, 'sc':0}
    song_list = cu.genie()
    return render_template('crawling/genie_jquery.html', song_list=song_list, 
                           menu=menu, weather=get_weather(app), quote=quote, addr=addr)

@app.route('/siksin', methods=['GET', 'POST'])
def siksin():
    menu = {'ho':0, 'us':0, 'cr':1, 'cb':0, 'sc':0}
    if request.method == 'GET':
        return render_template('crawling/siksin.html', menu=menu, weather=get_weather(app), 
                               quote=quote, addr=addr)
    else:
        place = request.form['place']
        food_list = cu.siksin(place)
        return render_template('crawling/siksin_res.html', food_list=food_list, 
                               menu=menu, weather=get_weather(app), place=place, 
                               quote=quote, addr=addr)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
