import os
import urllib2
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
        folder = self.folder
        if album:  # has associated album
            album = model.album
            if not album.folder:
                album.folder = album.name
                album.save()
            folder = os.path.join(folder, album.folder)
            if not os.path.exists(folder):
                os.mkdir(folder)
        # if old photo exists, remove it first
        if model.local:
            os.unlink(model.local.path)
        # find a suitable path
        filename = '%s.%s' % (model.title, model.extension)
        path = os.path.join(folder, filename)
        # make sure we found an available path
        index = 1
        base, ext = os.path.splitext(path)
        while 1:
            if os.path.exists(path):
                path = base + str(index) + ext
            else:
                break
            index += 1

        # fetch & save to local file
        logging.info('retrieve %s --> %s' % (model.url, path))
        # urllib.urlretrieve does NOT support implicit http_proxy
        r = urllib2.urlopen(model.url)
        with open(path, 'wb') as f:
            f.write(r.read())
            f.close()

        # modified timestamp & md5 hash
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
        model.save()

    def update_from(self, sync_cls):
        logging.info('update_from %s' % sync_cls)
        objs = sync_cls.sync_to_local()
        for obj in objs:
            logging.info('Local: save from %s' % obj)
            try:
                self.savefrom(obj)
            except IOError, e:
                logging.error('fetch error: %s with Exception: %s' % (obj, e))


if __name__ == '__main__':
    lsync = LocalSync()
    fsync = FlickrSync()
    lsync.update_from(fsync)
