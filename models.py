"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'schools',
    Field('name', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'courses',
    Field('name', requires=IS_NOT_EMPTY()),
    Field('school', 'reference schools'),
    Field('description', 'text'),
)

db.define_table(
    'instructors',
    Field('first_name', requires=IS_NOT_EMPTY()),
    Field('last_name', requires=IS_NOT_EMPTY()),
    Field('school', 'reference schools'),
)

db.define_table(
    'course_reviews',
    Field('course', 'reference courses'),
    Field('review', 'text'),
)

db.define_table(
    'instructor_reviews',
    Field('course', 'reference instructor'),
    Field('review', 'text'),
)

db.schools.id.readable            = db.schools.id.writable            = False
db.courses.id.readable            = db.courses.id.writable            = False
db.instructors.id.readable        = db.instructors.id.writable        = False
db.course_reviews.id.readable     = db.course_reviews.id.writable     = False
db.instructor_reviews.id.readable = db.instructor_reviews.id.writable = False

db.commit()
