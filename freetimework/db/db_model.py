from freetimework.freetimework.db.base_db import database
from peewee import *
import datetime


class FreeTimeWorkModel(database):
    id = IntegerField(index=True, null=False)
    channel_id = CharField(index=True, null=False, default='0')
    channel_name = CharField(index=False, null=False, default='')
    publisher = CharField(null=False, default='')
    journal_id = CharField(index=True, null=False, default='0')
    journal_name = CharField(null=False, default='')
    journal_url = CharField(null=False, default='')
    article_id = CharField(null=False)
    article_title = CharField(null=False, default='')
    article_url = CharField(null=False, default='')
    article_pdf_url = CharField(null=False, default='')
    article_abstract = TextField(null=False, default='')
    author = CharField(null=False, default='')
    email = CharField(null=False, default='')
    company = CharField(null=False, default='')
    created_at = DateField(null=False, default=datetime.datetime.now())
    updated_at = DateField(null=False, default=datetime.datetime.now())
    status = IntegerField(default=1)
