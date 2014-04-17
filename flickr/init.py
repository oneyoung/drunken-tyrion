import os
import logging
import flickr_api as flickr


def auth_in_browser(perms):
    ''' OAuth in Browser and return auth object
    Implement:
        1. oauth support url redirect after auth done
        2. we can setup a HTTP server to get such token
    '''
    logging.info("auth in browser")
    port = 5678
    redirt_url = "http://localhost:%s/" % port

    # get auth url
    auth = flickr.auth.AuthHandler(callback=redirt_url)
    url = auth.get_authorization_url(perms)
    # open url in browser
    import webbrowser
    webbrowser.open_new(url)

    # setup a temporary http server to get oath_token
    import BaseHTTPServer

    class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
        def do_GET(self):
            # parse url to get auth_token
            import urlparse
            p = urlparse.urlparse(self.path)
            q = urlparse.parse_qs(p.query)
            try:
                auth_token = q['oauth_token'][0]
                auth_verifier = q['oauth_verifier'][0]
            except:
                logging.error("Auth Fail: %s" % q)
                raise Exception("Auth Failure")
            logging.info("Get auth_token %s" % auth_token)
            # save back to auth handler
            auth.set_verifier(auth_verifier)
            # send response to webpage
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("Auth OK. Please close this page.")
            self.wfile.close()

    logging.info("setup HTTP server at port: %d" % port)
    httpd = BaseHTTPServer.HTTPServer(("", port), Handler)

    httpd.handle_request()  # just handle on request

    return auth


def init_flickr():
    # logging config
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    API_KEY = ""
    API_SEC = ""

    AUTH_FILE = ".flickr_auth"
    try:
        # try to load old auth file first
        auth = flickr.auth.AuthHandler.load(AUTH_FILE)
        logging.info("load config from %s" % AUTH_FILE)
    except:
        flickr.set_keys(api_key=API_KEY, api_secret=API_SEC)
        auth = auth_in_browser('write')
        auth.save(AUTH_FILE, True)  # also include API keys

    flickr.set_auth_handler(auth)


def download_all_photos():
    # create saved dir
    savedir = "photos"
    try:
        os.mkdir(savedir)
    except:
        pass
    # get photos
    user = flickr.test.login()
    # flickr user.getPhotos only return 1 page of photos
    # to fetch all photos, need to retrieve page by page
    pages = user.getPhotos().info.pages
    for page in range(1, pages + 1):
        logging.info("Download photos of page %d" % page)
        # download specified page photos
        for photo in user.getPhotos(page=page):
            basename = (photo.title if photo.title else photo.id)
            filename = basename + ".jpg"
            fpath = os.path.join(savedir, filename)
            # make sure we found an available path
            index = 1
            base, ext = os.path.splitext(fpath)
            while 1:
                if os.path.exists(fpath):
                    fpath = base + str(index) + ext
                else:
                    break
                index += 1
            size = "Original"
            logging.info("%s ==> %s" % (photo.getPhotoUrl(size), fpath))
            photo.save(fpath, size_label=size)

if __name__ == "__main__":
    init_flickr()
    download_all_photos()
