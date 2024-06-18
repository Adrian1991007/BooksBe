from marshmallow import Schema, ValidationError, fields, post_load, validates

from models.book import Book


class UserCreationSchema(Schema):
    title = fields.String(required=True)
    authors = fields.String(required=True)
    imageUrl = fields.String(required=True)
    gender = fields.String(required=True)
    age_start = fields.String(required=True)
    age_end = fields.String(required=True)

    @validates("title")
    def validates_title(self, value):
        if len(value) < 4:
            raise ValidationError("Title must longer than 3")

    @post_load
    def make_book(self, data, **kwargs):
        return Book(**data)
