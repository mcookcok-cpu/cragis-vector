import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
D = os.path.dirname(os.path.abspath(__file__))
F = {"outline": ("cragis-outline.svg", "garis"), "abu": ("cragis-abu-garis.svg", "abu-garis"),
     "tipis": ("cragis-font-tipis.svg", "font-tipis"), "jiplak": ("cragis-putih-jiplak.svg", "putih-jiplak")}
class H(BaseHTTPRequestHandler):
    def do_GET(s):
        if s.path.startswith("/logo"):
            k = next((k for k in F if k in s.path), None)
            fn, nm = F[k] if k else ("cragis-font.svg", "font-nasalization")
            b, c = open(os.path.join(D, fn), "rb").read(), "image/svg+xml"
            dl = 'attachment; filename="cragis-%s.svg"' % nm
        else:
            b, c, dl = open(os.path.join(D, "index.html"), "rb").read(), "text/html; charset=utf-8", None
        s.send_response(200); s.send_header("Content-Type", c)
        if dl and "download=1" in s.path: s.send_header("Content-Disposition", dl)
        s.end_headers(); s.wfile.write(b)
    def log_message(s, *a): pass
ThreadingHTTPServer(("0.0.0.0", 4567), H).serve_forever()
