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

import os
import json
import uuid

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
#from nqgcs import NQGCS
from .settings import APP_FOLDER
#from .gcs_url import gcs_url

url_signer = URLSigner(session)

BUCKET = '/reportcard-bucket'
GCS_KEY_PATH = os.path.join(APP_FOLDER, 'private/gcs_keys.json')
with open(GCS_KEY_PATH) as gcs_key_f:
    GCS_KEYS = json.load(gcs_key_f)

#gcs = NQGCS(json_key_path=GCS_KEY_PATH)

@action('index')
@action.uses(db, auth, 'index.html')
def index():
    profile_page_link = ""
    if get_user_email() is not None:
        this_user_info = db(db.auth_user.email == get_user_email()).select().first()
        assert this_user_info is not None
        this_user_id = this_user_info.id
        profile_page_link = URL('profile', str(this_user_id))

    return dict(
        load_everything_url=URL('load_everything', signer=url_signer),
        url_signer=url_signer,
        profile_page_link=profile_page_link,
    )

@action('profile/<user_id:int>')
@action.uses(db, auth, session, 'profile.html')
def profile(user_id=None):
    assert user_id is not None
    logged_in = True if get_user_email() is not None else False

    user_info = db(db.auth_user.id == user_id).select().first()
    assert user_info is not None

    profile_page_link = ""
    if get_user_email() is not None:
        this_user_info = db(db.auth_user.email == get_user_email()).select().first()
        assert this_user_info is not None
        this_user_id = this_user_info.id
        profile_page_link = URL('profile', str(this_user_id))

    return dict(
        user_info=user_info,
        email=get_user_email(),
        load_user_reviews_url=URL('load_user_reviews', signer=url_signer),
        author_email=get_user_email(),
        logged_in=logged_in,
        delete_review_url=URL('delete_review', signer=url_signer),
        edit_review_url=URL('edit_review', signer=url_signer),
        add_like_url=URL('add_like', signer=url_signer),
        flip_like_url=URL('flip_like', signer=url_signer),
        delete_like_url=URL('delete_like', signer=url_signer),
        user_id=user_id,
        profile_page_link=profile_page_link,
    )

'''
@action('profile/<user_id:int>')
@action.uses(db, session, 'profile.html')
def profile(user_id=None):
    assert user_id is not None

    return dict(
        user=db(db.auth_user.id == user_id).select().first(),
        email=get_user_email(),
        has_pfp=False,
        notify_upload_pfp_url=URL('notify_upload_pfp', signer=url_signer),
        notify_delete_pfp_url=URL('notify_delete_pfp', signer=url_signer),
        access_pfp_url=URL('access_pfp', signer=url_signer),
        pfp_url="https://cdn.geekwire.com/wp-content/uploads/2018/01/L10309441.jpg",
    )'''

@action('add_course', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify(), 'add_course.html')
def add_course():
    form = Form(db.courses, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # Redirect back to index
        redirect(URL('index'))
    else:
        profile_page_link = ""
        if get_user_email() is not None:
            this_user_info = db(db.auth_user.email == get_user_email()).select().first()
            assert this_user_info is not None
            this_user_id = this_user_info.id
            profile_page_link = URL('profile', str(this_user_id))
        # GET or not accepted, so error
        return dict(form=form, profile_page_link=profile_page_link)

@action('add_instructor', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_instructor.html')
def add_instructor():
    form = Form(db.instructors, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # Redirect back to index
        redirect(URL('index'))
    else:
        profile_page_link = ""
        if get_user_email() is not None:
            this_user_info = db(db.auth_user.email == get_user_email()).select().first()
            assert this_user_info is not None
            this_user_id = this_user_info.id
            profile_page_link = URL('profile', str(this_user_id))
        # GET or not accepted, so error
        return dict(form=form, profile_page_link=profile_page_link)

@action('course/<course_id:int>')
@action.uses(db, session, auth, 'course.html')
def course(course_id=None):
    assert course_id is not None

    course_info = db(db.courses.id == course_id).select().first()
    reviews = db(db.reviews.course == course_id).select().as_list()

    assert course_info is not None
    assert reviews is not None

    logged_in = True if get_user_email() is not None else False

    ratings = []
    school = db(db.schools.id == course_info.school).select().first().name

    for review in reviews:
        ratings.append(review["rating"])
        instructor = db(db.instructors.id == review["instructor"]).select().first()
        review["instr_name"] = instructor.first_name + " " + instructor.last_name

    if ratings:
        avg_rating = sum(ratings)/len(ratings)
        rating_string = "{:.1f}/5.0".format(avg_rating)
    else:
        rating_string = "No ratings yet..."

    profile_page_link = ""
    if get_user_email() is not None:
        this_user_info = db(db.auth_user.email == get_user_email()).select().first()
        assert this_user_info is not None
        this_user_id = this_user_info.id
        profile_page_link = URL('profile', str(this_user_id))

    author_name = ""
    author_id = -1
    if logged_in:
        user_info = db(db.auth_user.email == get_user_email()).select().first()
        assert user_info is not None
        author_name = user_info.first_name + " " + user_info.last_name
        author_id = user_info.id

    return dict(
        course=course_info,
        reviews=reviews,
        rating_string=rating_string,
        logged_in=logged_in,
        school=school,
        author_name=author_name,
        author_email=get_user_email(),
        author_id=author_id,
        course_id=course_id,
        load_course_reviews_url=URL('load_course_reviews', signer=url_signer),
        add_review_url=URL('add_review', signer=url_signer),
        delete_review_url=URL('delete_review', signer=url_signer),
        edit_review_url=URL('edit_review', signer=url_signer),
        add_like_url=URL('add_like', signer=url_signer),
        flip_like_url=URL('flip_like', signer=url_signer),
        delete_like_url=URL('delete_like', signer=url_signer),
        profile_page_link=profile_page_link,
    )

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

    profile_page_link = ""
    if get_user_email() is not None:
        this_user_info = db(db.auth_user.email == get_user_email()).select().first()
        assert this_user_info is not None
        this_user_id = this_user_info.id
        profile_page_link = URL('profile', str(this_user_id))

    author_name = ""
    author_id = -1
    if logged_in:
        user_info = db(db.auth_user.email == get_user_email()).select().first()
        assert user_info is not None
        author_name = user_info.first_name + " " + user_info.last_name
        author_id = user_info.id

    return dict(
        instr=instr_info,
        reviews=reviews,
        rating_string=rating_string,
        school=school,
        author_name=author_name,
        author_email=get_user_email(),
        author_id=author_id,
        instr_id=instr_id,
        logged_in=logged_in,
        load_instructor_reviews_url=URL('load_instructor_reviews', signer=url_signer),
        add_review_url=URL('add_review', signer=url_signer),
        delete_review_url=URL('delete_review', signer=url_signer),
        edit_review_url=URL('edit_review', signer=url_signer),
        add_like_url=URL('add_like', signer=url_signer),
        flip_like_url=URL('flip_like', signer=url_signer),
        delete_like_url=URL('delete_like', signer=url_signer),
        profile_page_link=profile_page_link,
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

        user_info = db(db.auth_user.email == review["user"]).select().first()
        assert user_info is not None
        review["user_name"] = user_info.first_name + " " + user_info.last_name
        review["user_id"] = user_info.id

        review_likes = db(db.likes.review == review["id"]).select()
        review["likers"] = 0
        review["dislikers"] = 0
        for like in review_likes:
            if like["is_like"]:
                review["likers"] += 1
            else:
                review["dislikers"] += 1

    return dict(reviews=reviews, likes=likes, courses=courses, course_2_id=course_2_id)

@action('load_course_reviews', method="POST")
@action.uses(url_signer.verify(), db)
def load_course_reviews():

    course_id = request.json.get('course_id')
    assert course_id is not None

    course_info = db(db.courses.id == course_id).select().first()
    assert course_info is not None

    school_id = course_info.school
    instr_info = db(db.instructors.school == school_id).select()
    assert instr_info is not None

    instructors = []
    instr_2_id = {}

    for i in instr_info:
        name = i.first_name + " " + i.last_name
        instructors.append(name)
        instr_2_id[name] = i.id

    reviews = db(db.reviews.course == course_id).select().as_list()
    likes = db(db.likes.user_email == get_user_email()).select().as_list()
    assert reviews is not None
    assert likes is not None

    # Add all people who liked each post to each post and other info
    for review in reviews:
        instr_description = db(db.instructors.id == review["instructor"]).select().first()
        assert instr_description is not None
        review["instr_name"] = instr_description.first_name + " " + instr_description.last_name

        user_info = db(db.auth_user.email == review["user"]).select().first()
        assert user_info is not None
        review["user_name"] = user_info.first_name + " " + user_info.last_name
        review["user_id"] = user_info.id

        review_likes = db(db.likes.review == review["id"]).select()
        review["likers"] = 0
        review["dislikers"] = 0
        for like in review_likes:
            if like["is_like"]:
                review["likers"] += 1
            else:
                review["dislikers"] += 1

    return dict(reviews=reviews, likes=likes, instructors=instructors, instr_2_id=instr_2_id)

@action('load_user_reviews', method="POST")
@action.uses(url_signer.verify(), db)
def load_user_reviews():

    user_id = request.json.get('user_id')

    user_info = db(db.auth_user.id == user_id).select().first()
    assert user_info is not None
    user_email = user_info.email

    reviews = db(db.reviews.user == user_email).select().as_list()
    likes = db(db.likes.user_email == get_user_email()).select().as_list()
    assert reviews is not None
    assert likes is not None

    # Add all people who liked each post to each post and other info
    for review in reviews:
        instr_description = db(db.instructors.id == review["instructor"]).select().first()
        course_description = db(db.courses.id == review["course"]).select().first()
        assert instr_description is not None
        assert course_description is not None

        review["instr_name"] = instr_description.first_name + " " + instr_description.last_name
        review["course_name"] = course_description.name

        review_likes = db(db.likes.review == review["id"]).select()
        review["likers"] = 0
        review["dislikers"] = 0
        for like in review_likes:
            if like["is_like"]:
                review["likers"] += 1
            else:
                review["dislikers"] += 1

    return dict(reviews=reviews, likes=likes)

@action('load_everything', method="POST")
@action.uses(url_signer.verify(), db)
def load_everything():
    courses_info = db(db.courses).select()
    instrs_info = db(db.instructors).select()

    assert courses_info is not None
    assert instrs_info is not None

    courses = []
    instrs = []
    course_2_id = {}
    instr_2_id = {}

    for c in courses_info:
        courses.append(c.name)
        course_2_id[c.name] = c.id

    for i in instrs_info:
        name = i.first_name + " " + i.last_name
        instrs.append(name)
        instr_2_id[name] = i.id

    return dict(
        courses=courses,
        course_2_id=course_2_id,
        instrs=instrs,
        instr_2_id=instr_2_id,
    )

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


###########################################
#            PFP ENDPOINTS                #
###########################################
'''
@action('access_pfp', method="POST")
@action.uses(url_signer.verify(), db)
def access_pfp():
    """Returns the URL to do download / upload / delete for GCS."""
    verb = request.json.get("action")
    if verb == "PUT":
        mimetype = request.json.get("mimetype", "")
        file_name = request.json.get("file_name")
        extension = os.path.splitext(file_name)[1]
        # Use + and not join for Windows, thanks Blayke Larue
        file_path = BUCKET + "/" + str(uuid.uuid1()) + extension
        # Marks that the path may be used to upload a file.
        mark_possible_upload(file_path)
        upload_url = gcs_url(GCS_KEYS, file_path, verb='PUT',
                             content_type=mimetype)
        return dict(
            signed_url=upload_url,
            file_path=file_path
        )
    elif verb in ["GET", "DELETE"]:
        file_path = request.json.get("file_path")
        if file_path is not None:
            # We check that the file_path belongs to the user.
            r = db(db.pfp.file_path == file_path).select().first()
            if r is not None and r.owner == get_user_email():
                # Yes, we can let the deletion happen.
                delete_url = gcs_url(GCS_KEYS, file_path, verb='DELETE')
                return dict(signed_url=delete_url)
        # Otherwise, we return no URL, so we don't authorize the deletion.
        return dict(signer_url=None)

@action('notify_upload_pfp', method="POST")
@action.uses(url_signer.verify(), db)
def notify_upload_pfp():
    """We get the notification that the file has been uploaded."""
    file_name = request.json.get("file_name")
    file_path = request.json.get("file_path")
    # Deletes any previous file.
    rows = db(db.pfp.owner == get_user_email()).select()
    for r in rows:
        if r.file_path != file_path:
            delete_path(r.file_path)
    # Marks the upload as confirmed.
    db.pfp.update_or_insert(
        ((db.pfp.owner == get_user_email()) &
         (db.pfp.file_path == file_path)),
        owner=get_user_email(),
        file_path=file_path,
        file_name=file_name,
        confirmed=True,
    )
    # Returns the file information.
    return dict(
        download_url=gcs_url(GCS_KEYS, file_path, verb='GET')
    )

@action('notify_delete_pfp', method="POST")
@action.uses(url_signer.verify(), db)
def notify_delete_pfp():
    file_path = request.json.get("file_path")
    # We check that the owner matches to prevent DDOS.
    db((db.pfp.owner == get_user_email()) &
       (db.pfp.file_path == file_path)).delete()
    return dict()

def delete_path(file_path):
    """Deletes a file given the path, without giving error if the file
    is missing."""
    try:
        bucket, id = os.path.split(file_path)
        gcs.delete(bucket[1:], id)
    except:
        # Ignores errors due to missing file.
        pass

def delete_previous_uploads():
    """Deletes all previous uploads for a user, to be ready to upload a new file."""
    previous = db(db.pfp.owner == get_user_email()).select()
    for p in previous:
        # There should be only one, but let's delete them all.
        delete_path(p.file_path)
    db(db.pfp.owner == get_user_email()).delete()

def mark_possible_upload(file_path):
    """Marks that a file might be uploaded next."""
    delete_previous_uploads()
    db.pfp.insert(
        owner=get_user_email(),
        file_path=file_path,
        confirmed=False,
    )'''
