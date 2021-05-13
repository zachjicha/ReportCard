"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth, 'index.html')
def index():
    return dict()

@action('profile/<user_id:int>')
@action.uses(db, session, 'profile.html')
def profile(user_id=None):
    assert user_id is not None

    return dict(user=db(db.auth_user.id == user_id).select().first(), email=get_user_email())

@action('course/<course_id:int>')
@action.uses(db, session, 'course.html')
def course(course_id=None):
    assert course_id is not None

    course_info = db(db.courses.id == course_id).select().first()
    reviews = db(db.reviews.course == course_id).select().as_list()
    ratings = []

    for review in reviews:
        ratings.append(review["rating"])
        instructor = db(db.instructors.id == review["instructor"]).select().first()
        review["fname"] = instructor.first_name
        review["lname"] = instructor.last_name

    if ratings:
        avg_rating = sum(ratings)/len(ratings)
        rating_string = str(avg_rating) + "/5.0"
    else:
        rating_string = "No ratings yet..."

    return dict(course=course_info, reviews=reviews, rating=rating_string)

@action('instructor/<instr_id:int>')
@action.uses(db, session, 'instructor.html')
def course(instr_id=None):
    assert instr_id is not None

    instr_info = db(db.instructors.id == instr_id).select().first()
    reviews = db(db.reviews.instructor == instr_id).select().as_list()
    ratings = []
    school = db(db.schools.id == instr_info.school).select().first().name

    for review in reviews:
        ratings.append(review["rating"])
        course = db(db.courses.id == review["course"]).select().first()
        review["course_name"] = course.name

    if ratings:
        avg_rating = sum(ratings)/len(ratings)
        rating_string = str(avg_rating) + "/5.0"
    else:
        rating_string = "No ratings yet..."

    return dict(instr=instr_info, reviews=reviews, rating=rating_string, school=school)

