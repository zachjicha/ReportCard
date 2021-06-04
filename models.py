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
    Field('school', 'reference schools', default=1, requires=IS_NOT_EMPTY()),
    Field('description', 'text', default="", requires=IS_NOT_EMPTY()),
)

db.define_table(
    'instructors',
    Field('first_name', requires=IS_NOT_EMPTY()),
    Field('last_name', requires=IS_NOT_EMPTY()),
    Field('school', 'reference schools', default=1, requires=IS_NOT_EMPTY()),
    Field('department', 'text',  default="", requires=IS_NOT_EMPTY()),
)

db.define_table(
    'reviews',
    Field('course', 'reference courses', requires=IS_NOT_EMPTY()),
    Field('instructor', 'reference instructors', requires=IS_NOT_EMPTY()),
    Field('body', 'text', requires=IS_NOT_EMPTY()),
    Field('rating', 'double', requires=IS_FLOAT_IN_RANGE(0, 5)),
    Field('user', requires=IS_NOT_EMPTY())
)

db.define_table(
    'likes',
    Field('is_like', 'boolean', requires=IS_NOT_EMPTY()),
    Field('user_email', requires=IS_NOT_EMPTY()),
    Field('review', 'reference reviews', requires=IS_NOT_EMPTY()),
)
'''
db.define_table(
    'pfp',
    Field('owner', default=get_user_email()),
    Field('file_name'),
    Field('file_path'),
    Field('confirmed', 'boolean', default=False),
)'''

db.schools.id.readable     = db.schools.id.writable     = False
db.courses.id.readable     = db.courses.id.writable     = False
db.instructors.id.readable = db.instructors.id.writable = False
db.reviews.id.readable     = db.reviews.id.writable     = False

# Since this is only for UCSC, we will always write UCSC's id
db.courses.school.readable = db.courses.school.writable = False
db.instructors.school.readable = db.instructors.school.writable = False

db.commit()
