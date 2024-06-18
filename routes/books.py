import io

import boto3
from botocore.exceptions import ClientError
from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
import logging

from sqlalchemy import select

from decorators import timed
from extensions import db
from models.book import Book, BookSchema

books_bp = Blueprint("books", __name__, url_prefix="/books")
book_schema = BookSchema()
logger = logging.getLogger(__name__)

# Initialize S3 client
s3 = boto3.client('s3',
                  aws_access_key_id='AKIAQ3EGVHPVTHSEBC3X',
                  aws_secret_access_key='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',
                  region_name='us-east-1')

# Initialize SNS client
sns = boto3.client('sns',
                   aws_access_key_id='AKIAQ3EGVHPVTHSEBC3X',
                   aws_secret_access_key='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',
                   region_name='us-east-1')

# Define the SNS topic ARN
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:471112624961:books'

@timed
@books_bp.route("", methods=["GET"])
def get_all_books():
    age_range = request.args.get("age")
    gender = request.args.get("gender")

    if age_range and gender:
        # Validate gender parameter
        if gender and gender not in ["Male", "Female"]:
            logger.error("Invalid gender parameter: %s", gender)
            return jsonify({"error": "Gender must be either 'Male' or 'Female'"}), 400

        # Extract age_start and age_end from the age_range parameter
        age_start, age_end = None, None
        if age_range:
            try:
                age_start, age_end = map(int, age_range.split("-"))
                if age_start < 0 or age_end < 0:
                    raise ValidationError("Age must be a positive integer")
            except ValueError:
                logger.error("Invalid age parameter: %s", age_range)
                return jsonify({"error": "Invalid age parameter"}), 400

        # Query books based on age and gender filters
        query = Book.query
        if age_start is not None and age_end is not None:
            query = query.filter(Book.age_start <= age_end, Book.age_end >= age_start)
        if gender:
            query = query.filter(Book.gender == gender)

        books = query.all()

        # Log the number of books retrieved
        logger.info("Retrieved %d books with age_range=%s and gender=%s", len(books), age_range, gender)

        return jsonify(BookSchema(many=True).dump(books))

    books = db.session.scalars(select(Book)).all()
    logger.info("Retrieved all books")
    return jsonify(book_schema.dump(books, many=True))


@books_bp.route("", methods=["POST"])
def add_book():
    try:
        # Handle form data
        title = request.form.get('title')
        author = request.form.get('author')
        gender = request.form.get('gender')
        age = request.form.get('age')

        # Handle image upload
        if 'image' in request.files:
            # Read image data from request
            image_data = request.files['image'].read()

            # Upload image to S3 bucket
            bucket_name = 'ccbooksimages'
            key = f'images/{title}.jpg'  # Define the key (path) for the image in the bucket
            s3.upload_fileobj(io.BytesIO(image_data), bucket_name, key, ExtraArgs={'ACL': 'public-read'})

            # Get the URL of the uploaded image
            image_url = f'https://{bucket_name}.s3.amazonaws.com/{key}'

        else:
            image_url = None

        # Extract age_start and age_end from the age field
        age_start_str, age_end_str = age.split('-')
        age_start = int(age_start_str[1:])
        age_end = int(age_end_str[:-1])

        # Create a new book instance (assuming your Book model is properly defined)
        new_book = Book(
            title=title,
            authors=author,
            imageUrl=image_url,
            gender=gender,
            age_start=age_start,
            age_end=age_end
        )

        # Add and commit the new book to the database
        db.session.add(new_book)
        db.session.commit()

        # Publish a message to the SNS topic
        message = f"A new book titled '{title}' by {author} has been added."
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="New Book Added"
        )

        return jsonify({"message": "Book added successfully"}), 200

    except ClientError as e:
        print(f"Error uploading image to S3: {e}")
        return jsonify({"error": "Error uploading image to S3"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
