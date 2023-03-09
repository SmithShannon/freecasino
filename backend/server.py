from SlotMachine import SlotMachine
from flask import Flask, send_file, abort, jsonify, request, make_response
from flask_cors import CORS
from functools import wraps
from urllib.request import urlopen
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, Column, Integer, String, create_engine
from flask_migrate import Migrate
from dotenv import load_dotenv
import pandas as pd
import os, sys, json, jwt, requests

load_dotenv()

app = Flask(__name__)
cors = CORS(app, origins=['http://localhost:8000'],supports_credentials=True)

app.config.from_object('config')
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('database_uri')
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

#engine = create_engine(app.config['SQLALCHEMY_ENGINE'])
#with engine.connect() as conn:
#    conn.execute("commit")
#    conn.execute('CREATE DATABASE {database};'.format(database='slots'))

db = SQLAlchemy(app)

migrate = Migrate(app,db,compare_type=True)

class User (db.Model):
    __tablename__ = 'user'

    username = Column(String,primary_key=True)
    score = Column(Integer,default=0,nullable=False)
    credit = Column(Integer,default=0,nullable=False)

    def __init__(self,username):
        self.username = username

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def add_winnings(self,winning):
        self.score += winning
        db.session.commit()

    def subtract_winnings(self,amount):
        self.score += -amount
        db.session.commit()

    def add_credit(self,credits):
        self.credit += credits
        db.session.commit()

    def subtract_credit(self,amount):
        self.credit += -amount
        db.session.commit()

award_dict = {'/test/club.png':1,'/test/diamond.png':1,'/test/heart.png':1,'/test/spade.png':1,'/test/diamond-gem.png':1000}

slots = {
    'test':SlotMachine(
        num_reels=3,
        reel_array=['/test/club.png', '/test/club.png', '/test/club.png',
                    '/test/diamond.png', '/test/diamond.png', '/test/diamond.png',
                    '/test/heart.png', '/test/heart.png', '/test/heart.png',
                    '/test/spade.png', '/test/spade.png', '/test/spade.png',
                    '/test/diamond-gem.png'],
        award_dict=award_dict,
        window=3,
        center_only=False
    )
}

def requires_auth(permission=''):
    def decorator (f,*args,**kwargs):
        @wraps(f)
        def auth_wrap(*args,**kwargs):
            try:
                token = request.headers.get('Authorization',False).split(" ")
                if token[0].lower() != 'bearer':
                    abort(401)
                header = jwt.get_unverified_header(token[1])
                jwks_url = 'https://{AUTH0_DOMAIN}/.well-known/jwks.json'.format(AUTH0_DOMAIN=os.getenv('AUTH0_DOMAIN'))
                jwks = json.loads(urlopen(jwks_url).read())
                keys = {}
                for jwk in jwks['keys']:
                    keys[jwk['kid']] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                payload = jwt.decode(
                    token[1],
                    keys[header['kid']],
                    algorithms=os.getenv('ALGORITHM'),
                    audience=os.getenv('AUDIENCE'),
                    issuer='https://{AUTH0_DOMAIN}/'.format(AUTH0_DOMAIN=os.getenv('AUTH0_DOMAIN'))
                )
                if permission != "" and permission not in payload['permissions']:
                    abort(403)
                return f(payload,*args,**kwargs)
            except:
                print(sys.exc_info())
                abort(401)
        return auth_wrap
    return decorator

def getSuperToken():
    auth0_domain = os.getenv('AUTH0_DOMAIN')
    res = requests.post("https://{AUTH0_DOMAIN}/oauth/token".format(AUTH0_DOMAIN=auth0_domain), data={
        'grant_type':'client_credentials',
        'client_id':os.getenv('CLIENT_ID'),
        'client_secret':os.getenv('CLIENT_SECRET'),
        'audience':'https://{AUTH0_DOMAIN}/api/v2/'.format(AUTH0_DOMAIN=auth0_domain)
    })
    return res.json()['access_token']

def responseHeader(body):
    res = make_response(body)
    res.headers['Access-Control-Allow-Origin'] = 'http:localhost:8000'
    return res

@app.route('/<slot_id>/<image>',methods=['GET'])
def getPic(slot_id,image):
    try:
        return send_file('slot_images/{slot}/{pic}'.format(slot=slot_id,pic=image))
    except:
        print(sys.exc_info())
        abort(404)

@app.route('/slots/',methods=['GET'])
def get_slots():
    try:
        return responseHeader(
            jsonify({
                'success':True,
                'slots':list(slots.keys())
            })
        )
    except:
        print(sys.exc_info())
        abort(500)

@app.route('/slots/<slot_id>',methods=['POST'])
@requires_auth()
def spin (p,slot_id):
    try:
        user = User.query.filter_by(username=p['sub']).first()

        if user.credit < 1:
            return jsonify({
                'success': True,
                'canceled':True,
                'message':"You don't hava any credits."
        })

        slot = slots[slot_id]
        slot.spin()
        winnings = slot.dispense()
        matches = slot.matchesToJson()
        display = slot.windowToJson()
        reel_pos = slot.getReelPos()
        slot.visualize()

        user.add_winnings(winnings+1)

        return jsonify({
            'success':True,
            'window':display,
            'matches':matches,
            'winnings':winnings,
            'reel_pos':reel_pos
        })
    except:
        print(sys.exc_info())
        abort(404)

@app.route('/slots/<slot_id>',methods=['GET'])
def getMachine(slot_id):
    try:
        slot = slots[slot_id]
        display = slot.windowToJson()
        return jsonify({
            'success':True,
            'window':display,
            'reel':slot.getReel(),
            'window_size':slot.window,
            'reel_pos': slot.getReelPos()
        })
    except:
        print(sys.exc_info())
        abort(404)

@app.route('/top-up',methods=['GET'])
@requires_auth()
def top_up(p):
    try:
        print(request.headers)
        user = User.query.filter_by(username=p['sub']).first()
        user.add_credit(10)
        return jsonify({
            'success':True
        })
    except:
        print(sys.exc_info())
        abort(403)

@app.route('/user',methods=['POST'])
@requires_auth()
def getUser (p):
    print(request.headers)
    try:
        user0 = requests.get(
            'https://{AUTH0_DOMAIN}/api/v2/users?q=user_id:"{sub}"'.format(
                AUTH0_DOMAIN=os.getenv('AUTH0_DOMAIN'),sub=p['sub']),
            headers={"Authorization":"Bearer "+getSuperToken(),'Content-Type':'application/json'}
        )
        username = user0.json()[0]['nickname']
        user = User.query.filter_by(username=p['sub']).first()
        if user is None:
            user = User(username=p['sub'])
            user.insert()
        return jsonify({
            'success':True,
            'username':username,
            'credits':user.credit,
            'winnings':user.score
        })
    except:
        print(sys.exc_info())
        abort(401)

@app.route('/user',methods=['OPTIONS'])
def check():
    print('option')
    print(request)
    return {}

@app.errorhandler(401)
def err_401(error):
    return jsonify({
        'success':False,
        'error':401,
        'message':'Not authenticated'
    }), 401

@app.errorhandler(403)
def err_403(error):
    return jsonify({
        'success':False,
        'error':403,
        'message':'Forbidden'
    }), 403

@app.errorhandler(404)
def err_404(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':'Not found'
    }), 404

@app.errorhandler(500)
def err_500(error):
    return jsonify({
        'success':False,
        'error':500,
        'message':'Server Error'
    }), 500

if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)