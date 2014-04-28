import os
import urllib2
import datetime
import hashlib
import logging
from models import Local, Album
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

    def sync_from(self, sync_cls):
        logging.info('sync_from %s' % sync_cls)
        objs = sync_cls.sync_to_local()
        for obj in objs:
            logging.info('Local: save from %s' % obj)
            try:
                self.savefrom(obj)
            except IOError, e:
                logging.error('fetch error: %s with Exception: %s' % (obj, e))

    def sync_to(self, sync_cls):
        objs = []
        # traverse the dir
        for dirpath, folders, files in os.walk(self.folder):
            for fname in files:
                fpath = os.path.join(dirpath, fname)
                # get album, if have
                rel = os.path.relpath(dirpath, self.folder)
                if rel != '.':  # has sub dir
                    try:
                        album = Album.get(name=rel)
                    except Album.DoesNotExist:
                        album = Album.create(name=rel, folder=rel)
                else:
                    album = None
                # TODO: should a file extension filter here?
                md5 = hashlib.md5(open(fpath).read()).hexdigest()
                try:  # if file has been exists before
                    local = Local.get(md5=md5)
                    opath = local.path.encode('utf8')
                    if opath != fpath:
                        logging.debug('%s path change: %s --> %s' % (local, local.path, fpath))
                        # file was moved, rename filename or folder
                        local.title, ext = os.path.splitext(fname)
                        local.album = album
                        #local.fpath = fpath
                        local.last_modified = datetime.datetime.now()
                        local.save()
                        objs.append(local)  # objs: path modified.
                except Local.DoesNotExist:  # new file
                    try:
                        # file content modified
                        local = Local.get(path=fpath)
                        logging.debug('%s modified, path: %s' % (local, fpath))
                    except Local.DoesNotExist:
                        # brand new file
                        logging.debug('new file %s' % fpath)
                        local = Local()
                        local.title, ext = os.path.splitext(fname)
                        local.album = album
                        local.path = fpath
                    local.md5 = md5
                    local.last_modified = datetime.datetime.now()
                    local.save()
                    objs.append(local)

        # for those have not been upload
        for l in Local.select():
            sets = getattr(l, sync_cls.model.local.related_name)
            if sets.count() == 0 and l not in objs:
                objs.append(l)

        # pass objs that needs update to sync class
        logging.info('local: sync to %s, count %d' % (sync_cls, len(objs)))
        sync_cls.sync_from_local(objs)


if __name__ == '__main__':
    lsync = LocalSync()
    fsync = FlickrSync()
    lsync.sync_from(fsync)
    lsync.sync_to(fsync)
