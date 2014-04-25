import os
import urllib
import datetime
import hashlib
import logging
from models import Local
from flickr import FlickrSync

LOCAL_FOLDER = 'photos/'


class LocalSync():
    def __init__(self):
        # make sure directory is exists
        self.folder = LOCAL_FOLDER
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

    def savefrom(self, model):
        title = model.title
        album = model.album
        # path consist of "album/title.ext"
        filename = '%s.%s' % (model.title, model.extension)
        folder = self.folder
        if album:
            album = model.album
            if not album.folder:
                album.folder = album.title
                album.save()
            folder = os.path.join(folder, album.folder)
            if not os.path.exists(folder):
                os.mkdir(folder)
        path = os.path.join(folder, filename)
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

    def update_from(self, sync_cls):
        logging.info('update_from %s' % sync_cls)
        objs = sync_cls.sync_to_local()
        for obj in objs:
            logging.info('Local: save from %s' % obj)
            self.savefrom(obj)


if __name__ == '__main__':
    lsync = LocalSync()
    fsync = FlickrSync()
    lsync.update_from(fsync)
