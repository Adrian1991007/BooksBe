from flask import request, jsonify, Blueprint
import logging

from sqlalchemy import select

from decorators import timed
from dto.Subscriber import SubscriberCreationSchema
from extensions import db
from models.subscriber import Subscriber, SubscriberSchema

subscribers_bp = Blueprint("subscribers", __name__, url_prefix="/subscribers")
subscribers_schema = SubscriberSchema()
logger = logging.getLogger(__name__)



@timed
@subscribers_bp.route("", methods=["GET"])
def get_all_subscribers():
    logger.info("Retrieved all subscribers")
    subscribers = db.session.scalars(select(Subscriber)).all()
    return jsonify(subscribers_schema.dump(subscribers, many=True))


@subscribers_bp.route("", methods=["POST"])
def add_subscriber():
    try:
        req = request.get_json()['data']
        new_subscriber = Subscriber(email=req['email'])
        print(new_subscriber)
        db.session.add(new_subscriber)
        db.session.commit()

        return jsonify({"message": "Subscriber added successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
