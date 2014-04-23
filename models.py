from peewee import *


DB_NAME = "db.sqlite"
database = SqliteDatabase(DB_NAME)


class Album(Model):
    name = CharField()
    folder = CharField(null=True)
    flickr_setid = CharField(null=True)  # flickr photoset id

    @classmethod
    def fetch_update(cls, name, **kwargs):
        ''' get or create object by name,
        update field from kwargs if provided
        '''
        # get or create obj first
        try:
            obj = cls.get(name=name)
        except cls.DoesNotExist:
            obj = cls.create(name=name)

        # update keys
        modified = False
        for k in kwargs.keys():
            if hasattr(obj, k) and getattr(obj, k) != kwargs[k]:
                modified = True
                setattr(obj, k, kwargs[k])
        if modified:
            obj.save()

        return obj


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

# create table if necessary
for m in [Album, Local, Flickr]:
    if not m.table_exists():
        m.create_table()
