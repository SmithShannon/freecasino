import sys

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
cors = CORS(app)

@app.route('/login',methods=['GET'])
def login ():
    return render_template('login.html')

@app.route('/user',methods=['POST'])
def getUser():
    r = requests.post(
        'http://localhost:5000/user',
        headers=request.headers,
    )
    return r.json()
    #return render_template('user.html')

@app.route('/menu',methods=['GET'])
def getMenu():
    return render_template('menu.html')

@app.route('/login/token',methods=['GET'])
def get_token():
    return redirect(url_for('slots'))

@app.route('/slots',methods=['GET'])
def slots():
    r = requests.get('http://localhost:5000/slots')
    #print(r.json()['slots'])
    return render_template('slot_directory.html',slots=r.json()['slots'])

@app.route('/slots/<slot_id>',methods=['GET'])
def get_slot(slot_id):
    r = requests.get('http://localhost:5000/slots/'+slot_id)
    slot = r.json()
    s = requests.get('http://localhost:5000/{slot_id}/style.css'.format(slot_id=slot_id))
    if slot['success']:
        return render_template(
            'slots.html',
            slot_id=slot_id,
            window=slot['window'],
            reel=slot['reel'],
            reel_pos=slot['reel_pos'],
            window_size=slot['window_size'],
            style=s.text
        )
    else:
        return redirect('/error/'+slot['error']+'/'+slot['message'])

@app.route('/slots/<slot_id>/spin',methods=['POST'])
def get_slot_spin(slot_id):
    try:
        r = requests.post(
            'http://localhost:5000/slots/'+slot_id,
            headers=request.headers,
        )
        return r.json()
    except:
        print(sys.exc_info())
        redirect('error'+404+'/'+'Not Found')

@app.route('/top-up',methods=['GET'])
def get_top_up():
    return render_template('ad_screen.html')

@app.route('/logout',methods=['GET'])
def logout():
    return render_template('logout.html')

@app.route('/error/<status_code>/<message>',methods=['GET'])
def error(status_code,message):
    return render_template('error.html',status_code=status_code,message=message)

@app.route('/<slot_id>/<file>',methods=['GET'])
def get_file(slot_id,file):
    try:
        r = requests.get(
            'http://localhost:5000/{slot_id}/{file}'.format(slot_id=slot_id,file=file),
            headers=request.headers)
        print(r.content)
        return r.content
    except:
        print(sys.exc_info())
        redirect('error/'+404+'/'+'Not Found')

@app.route('/sound_test',methods=['GET'])
def sound_test():
    return render_template('sound_test.html')

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)