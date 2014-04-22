import os
import urllib
import datetime
import hashlib
import logging
from models import Local

LOCAL_FOLDER = 'photos/'


class LocalSync():
    def __init__(self):
        # create table if necessary
        if not Local.table_exists():
            Local.create_table()
        # make sure directory is exists
        self.folder = LOCAL_FOLDER
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

    def savefrom(self, model):
        title = model.title
        album = model.album
        # path consist of "album/title.ext"
        filename = '%s.%s' % (model.title, model.extension)
        if model.album:
            path = os.path.join(self.folder, model.album, filename)
        else:
            path = os.path.join(self.folder, filename)
        logging.info('retrieve %s --> %s' % (model.url, path))
        urllib.urlretrieve(model.url, path)
        last_modified = datetime.datetime.now()
        md5 = hashlib.md5(open(path).read()).hexdigest()

        # save to Local model
        l = model.local if model.local else Local()
        l.title = title
        l.album = album
        l.path = path
        l.md5 = md5
        l.last_modified = last_modified
        l.save()
        model.local = l  # set back foreign key
