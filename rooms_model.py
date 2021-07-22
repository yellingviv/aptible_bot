from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# define rooms db model
# good news she be basic brah

class Rooms(db.Model):
    # rooms, not requests, due to using requests lib -- too much repeat!!

    __tablename__ = "room_requests"

    request_id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    requested_at = db.Column(db.String(25), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    url = db.Column(db.String(150), nullable=False)
    approver = db.Column(db.String(100))
    approved_at = db.Column(db.String(25), nullable)

    def __repr__(self):
        return f"<Room Request: {self.request_id} from {self.email} at {self.requested_at}. Status is {self.status}."


# helper function is a fren

def connect_to_db(app):
    # connect db to main flask app

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///rooms'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.app = app
    db.init_app(app)
    db.create_all()
    print('db is up and running yeehaw')
