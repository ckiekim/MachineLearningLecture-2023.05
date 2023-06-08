from flask import Blueprint, request, render_template, session, current_app
from flask import redirect, flash
from urllib.parse import unquote
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json, os, requests
from urllib.parse import quote
import openai

chatbot_bp = Blueprint('chatbot_bp', __name__)
menu = {'ho':0, 'us':0, 'cr':0, 'cb':1, 'sc':0}

@chatbot_bp.before_app_first_request
def before_app_first_request():
    global model, wdf
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    filename = os.path.join(current_app.static_folder, 'data/wellness_dataset.csv')
    wdf = pd.read_csv(filename)
    wdf.embedding = wdf.embedding.apply(json.loads)
    print('Wellness initialization is done.')

@chatbot_bp.route('/counsel', methods=['GET','POST']) 
def counsel():
    if request.method == 'GET':
        return render_template('chatbot/counsel.html', menu=menu)
    else:
        user_input = request.form['userInput']
        embedding = model.encode(user_input)
        wdf['유사도'] = wdf.embedding.map(lambda x: cosine_similarity([embedding], [x]).squeeze())
        answer = wdf.loc[wdf.유사도.idxmax()]
        result = {
            'category':answer.구분, 'user':user_input, 'chatbot':answer.챗봇, 'similarity':answer.유사도
        }
        return json.dumps(result)

@chatbot_bp.route('/bard', methods=['GET','POST']) 
def bard():
    if request.method == 'GET':
        return render_template('chatbot/bard.html', menu=menu)
    else:
        with open(os.path.join(current_app.static_folder, 'keys/bardapikey.txt')) as f:
            bard_key = f.read()
        headers = { 'Authorization': f'Bearer {bard_key}', 
                    'Content-Type': 'text/plain' }
        user_input = request.form['userInput']
        data = { "input": quote(user_input) }
        req = requests.post('https://api.bardapi.dev/chat', headers=headers, json=data)
        result = { 'user':user_input, 'chatbot':req.json()['output'] }
        return json.dumps(result)

@chatbot_bp.route('/genImg', methods=['GET','POST']) 
def gen_img():
    if request.method == 'GET':
        return render_template('chatbot/openai.html', menu=menu)
    else:
        with open(os.path.join(current_app.static_folder, 'keys/openAIapikey.txt')) as f:
            openai.api_key = f.read()
        user_input = request.form['userInput']  # 'a photo of a happy corgi puppy sitting and facing me'
        size = request.form['size']

        gpt_prompt = [
            {'role': 'system', 'content': 'Translate it in English'},
            {'role': 'user', 'content': user_input}      
        ]
        gpt_response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo', messages=gpt_prompt
        )
        prompt = gpt_response['choices'][0]['message']['content']
        dalle_response = openai.Image.create(
            prompt=prompt, size=size         # '1024x1024', '512x512', '256x256'
        )
        img_url = dalle_response['data'][0]['url']
        result = {'img_url':img_url, 'translated_text': prompt}

        return json.dumps(result)
