from peewee import *


DB_NAME = "db.sqlite"
database = SqliteDatabase(DB_NAME)


class BaseModel(Model):
    class Meta:
        database = database


class Local(BaseModel):
    title = CharField()
    path = CharField()
    md5 = CharField()  # MD5 checksum of file
    last_modified = DateField()


class Flickr(BaseModel):
    photoid = CharField(unique=True)
    local = ForeignKeyField(Local, null=True)  # mapping to local file
    photoset = CharField(null=True)  # if photo belong to certain set
    lastupdate = CharField()
    ispublic = BooleanField()
