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
@action.uses(db, session, auth, 'instructor.html')
def course(instr_id=None):
    assert instr_id is not None

    instr_info = db(db.instructors.id == instr_id).select().first()
    reviews = db(db.reviews.instructor == instr_id).select().as_list()

    assert instr_info is not None
    assert reviews is not None

    logged_in = True if get_user_email() is not None else False

    ratings = []
    school = db(db.schools.id == instr_info.school).select().first().name

    for review in reviews:
        ratings.append(review["rating"])
        course = db(db.courses.id == review["course"]).select().first()
        review["course_name"] = course.name

    if ratings:
        avg_rating = sum(ratings)/len(ratings)
        rating_string = "{:.1f}/5.0".format(avg_rating)
    else:
        rating_string = "No ratings yet..."

    return dict(instr=instr_info,
                reviews=reviews,
                rating_string=rating_string,
                school=school,
                author=get_user_email(),
                instr_id=instr_id,
                logged_in=logged_in,
                load_instructor_reviews_url=URL('load_instructor_reviews', signer=url_signer),
                add_review_url=URL('add_review', signer=url_signer),
                delete_review_url=URL('delete_review', signer=url_signer),
                edit_review_url=URL('edit_review', signer=url_signer),
                add_like_url=URL('add_like', signer=url_signer),
                flip_like_url=URL('flip_like', signer=url_signer),
                delete_like_url=URL('delete_like', signer=url_signer),
    )

###########################################
#            API ENDPOINTS                #
###########################################
@action('load_instructor_reviews', method="POST")
@action.uses(url_signer.verify(), db)
def load_instructor_reviews():

    instr_id = request.json.get('instr_id')
    assert instr_id is not None

    instr_info = db(db.instructors.id == instr_id).select().first()
    assert instr_info is not None

    school_id = instr_info.school
    courses_info = db(db.courses.school == school_id).select()
    assert courses_info is not None
    courses = []
    course_2_id = {}

    for c in courses_info:
        courses.append(c.name)
        course_2_id[c.name] = c.id

    reviews = db(db.reviews.instructor == instr_id).select().as_list()
    likes = db(db.likes.user_email == get_user_email()).select().as_list()
    assert reviews is not None
    assert likes is not None

    # Add all people who liked each post to each post and other info
    for review in reviews:
        course_description = db(db.courses.id == review["course"]).select().first()
        assert course_description is not None
        review["course_name"] = course_description.name

        review_likes = db(db.likes.review == review["id"]).select()
        review["likers"] = 0
        review["dislikers"] = 0
        for like in review_likes:
            if like["is_like"]:
                review["likers"] += 1
            else:
                review["dislikers"] += 1

    return dict(reviews=reviews, likes=likes, courses=courses, course_2_id=course_2_id)

@action('add_review', method="POST")
@action.uses(url_signer.verify(), db)
def add_review():
    course = request.json.get('course')
    instructor = request.json.get('instructor')
    body = request.json.get('body')
    rating = request.json.get('rating')
    user = get_user_email()

    if get_user_email() is None:
        return dict(fail=True)

    assert course is not None
    assert instructor is not None
    assert body is not None
    assert rating is not None

    new_id = db.reviews.insert(
        course=course,
        instructor=instructor,
        body=body,
        rating=rating,
        user=get_user_email()
    )

    course_description = db(db.courses.id == course).select().first()
    assert course_description is not None

    return dict(id=new_id, fail=False, course_name=course_description.name)

@action('edit_review', method="POST")
@action.uses(url_signer.verify(), db)
def edit_review():
    review_id = request.json.get('id')
    new_body = request.json.get('body')
    new_rating = request.json.get('rating')
    assert review_id is not None
    assert new_body is not None
    assert new_rating is not None

    db(db.reviews.id == review_id).update(body=new_body, rating=new_rating)
    return "ok"

@action('delete_review', method="POST")
@action.uses(url_signer.verify(), db)
def delete_review():
    review_id = request.json.get('id')
    assert review_id is not None
    db(db.reviews.id == review_id).delete()
    return "ok"

@action('add_like', method="POST")
@action.uses(url_signer.verify(), db)
def add_like():
    new_id = db.likes.insert(
        is_like=request.json.get('is_like'),
        review=request.json.get('review'),
        user_email=get_user_email(),
    )
    return dict(id=new_id)

@action('flip_like', method="POST")
@action.uses(url_signer.verify(), db)
def flip_like():
    like_id = request.json.get('id')
    assert like_id is not None
    new_val = request.json.get('is_like')
    assert new_val is not None
    db(db.likes.id == like_id).update(is_like=new_val)
    return "ok"

@action('delete_like', method="POST")
@action.uses(url_signer.verify(), db)
def delete_like():
    like_id = request.json.get('id')
    assert like_id is not None
    db(db.likes.id == like_id).delete()
    return "ok"
