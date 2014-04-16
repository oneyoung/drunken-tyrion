import flickr_api as flickr
import logging


def auth_in_browser(perms):
    ''' OAuth in Browser and return auth object
    Implement:
        1. oauth support url redirect after auth done
        2. we can setup a HTTP server to get such token
    '''
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
    API_KEY = ""
    API_SEC = ""

    AUTH_FILE = ".flickr_auth"
    try:
        # try to load old auth file first
        auth = flickr.auth.AuthHandler.load(AUTH_FILE)
    except:
        flickr.set_keys(api_key=API_KEY, api_secret=API_SEC)
        auth = auth_in_browser('write')
        auth.save(AUTH_FILE, True)  # also include API keys

    flickr.set_auth_handler(auth)


init_flickr()
