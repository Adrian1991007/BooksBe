from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Sequence

from extensions import db
from models import book_table_name


class Book(db.Model):
    __tablename__ = book_table_name

    id = db.Column(db.Integer, Sequence('book_id_seq'), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    authors = db.Column(db.String(100), nullable=False)
    imageUrl = db.Column(db.String,  nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age_start = db.Column(db.Integer,  nullable=False)
    age_end = db.Column(db.Integer,  nullable=False)

    def __repr__(self):
        return f"Book(id={self.id}, title='{self.title}', authors='{self.authors}', imageUrl='{self.imageUrl}', gender='{self.gender}', " \
               f"age_start={self.age_start}, age_end={self.age_end})"


class BookSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        include_relationships = True
        load_instance = True
