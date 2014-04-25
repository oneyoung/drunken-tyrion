from peewee import *


DB_NAME = "db.sqlite"
database = SqliteDatabase(DB_NAME)


class BaseModel(Model):
    class Meta:
        database = database


class Album(BaseModel):
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


class BasePhotoModel(BaseModel):
    title = CharField(null=True)
    album = ForeignKeyField(Album, null=True)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.title)


class Local(BasePhotoModel):
    path = CharField()
    md5 = CharField()  # MD5 checksum of file
    last_modified = DateField()


class Flickr(BasePhotoModel):
    photoid = CharField(primary_key=True)
    lastupdate = CharField()
    ispublic = BooleanField()
    # public members
    url = CharField()  # url of photo
    extension = CharField()  # file extension
    local = ForeignKeyField(Local, null=True)  # mapping to local file


class Misc(BaseModel):
    ''' a misc talbe to store config '''
    name = CharField(primary_key=True)
    value = CharField(null=True)

# create table if necessary
for m in [Album, Local, Flickr, Misc]:
    if not m.table_exists():
        m.create_table()
