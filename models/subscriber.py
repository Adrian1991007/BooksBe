from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Sequence

from extensions import db
from models import subscribers_table_name


class Subscriber(db.Model):
    __tablename__ = subscribers_table_name

    id = db.Column(db.Integer, Sequence('subscriber_id_seq'), primary_key=True)
    email = db.Column(db.String(100), nullable=False)


    def __repr__(self):
        return f"Subscriber(id={self.id}, email='{self.email}')"


class SubscriberSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Subscriber
        include_relationships = True
        load_instance = True
