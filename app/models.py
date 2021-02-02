from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from passlib.context import CryptContext

PASSLIB_CONTEXT = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
)

db = SQLAlchemy()

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    # Use for Oauth 2 authentication via Google
    email = db.Column(db.String(256), unique=True)
    # Generate with something like secrets.token_hex(32)
    api_key = db.Column(db.String(256))
    site_id = db.Column(db.Integer, db.ForeignKey(Site.id), nullable=False)
    site = db.relationship(Site)

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    info_hash = db.Column(db.Text, nullable=False)
    recruitment_date = db.Column(db.DateTime, nullable=False)
    recruited_by = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)
    
    def __init__(self, info=None, info_hash=None, **kwargs):
        if info_hash is None and info is not None:
            info_hash = self.generate_hash(info)
        super().__init__(info_hash=info_hash, **kwargs)
    
    @property
    def info(self):
        raise AttributeError("Participant.info is write-only")
    
    @info.setter
    def info(self, info):
        self.info_hash = self.generate_hash(info)
    
    def verify_info(self, info):
        return PASSLIB_CONTEXT.verify(info, self.info_hash)
    
    @staticmethod
    def generate_hash(info):
        """Generate secure hash of participant info"""
        return PASSLIB_CONTEXT.hash(info.encode('utf8'))


# setup login manager
login_manager = LoginManager()
login_manager.login_view = "google.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
