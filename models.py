from peewee import *


DB_NAME = "db.sqlite"
database = SqliteDatabase(DB_NAME)


class Album(Model):
    name = CharField()
    folder = CharField(null=True)
    flickr_setid = CharField(null=True)  # flickr photoset id


class BaseModel(Model):
    title = CharField(null=True)
    album = ForeignKeyField(Album, null=True)

    class Meta:
        database = database


class Local(BaseModel):
    path = CharField()
    md5 = CharField()  # MD5 checksum of file
    last_modified = DateField()


class Flickr(BaseModel):
    photoid = CharField(primary_key=True)
    lastupdate = CharField()
    ispublic = BooleanField()
    # public members
    url = CharField()  # url of photo
    extension = CharField()  # file extension
    local = ForeignKeyField(Local, null=True)  # mapping to local file
