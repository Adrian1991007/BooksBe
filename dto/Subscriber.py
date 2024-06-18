from marshmallow import Schema,  fields, post_load

from models.subscriber import Subscriber


class SubscriberCreationSchema(Schema):
    email = fields.String(required=True)

    @post_load
    def make_subscriber(self, data, **kwargs):
        return Subscriber(**data)
