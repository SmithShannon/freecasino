from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('database_uri')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

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

    def add_winning(self,winning):
        self.score += winning
        db.session.commit()

    def add_credit(self,credits):
        self.credit += credits
        db.session.commit()

