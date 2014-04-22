from peewee import *


DB_NAME = "db.sqlite"
database = SqliteDatabase(DB_NAME)


class BaseModel(Model):
    title = CharField(null=True)
    album = CharField(null=True)

    class Meta:
        database = database


class Local(BaseModel):
    path = CharField()
    md5 = CharField()  # MD5 checksum of file
    last_modified = DateField()


class Flickr(BaseModel):
    photoid = CharField(primary_key=True)
    photoset = CharField(null=True)  # if photo belong to certain set
    lastupdate = CharField()
    ispublic = BooleanField()
    # public members
    url = CharField()  # url of photo
    extension = CharField()  # file extension
    local = ForeignKeyField(Local, null=True)  # mapping to local file
