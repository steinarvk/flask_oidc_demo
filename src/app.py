import flask
import flask_oidc
import binascii
import os
import functools
import jinja2
import urllib

app = flask.Flask(__name__)

# Set the redirect URI to /callback.
# APP_BASE_URL should be set to e.g. "https://myapp.example.com"
app.config["OVERWRITE_REDIRECT_URI"] = urllib.parse.urljoin(os.environ["APP_BASE_URL"], "/callback")

# Set the secret key used by Flask to encrypt session data.
# FLASK_SECRET_KEY should be a random hexadecimal string; the same for each iteration.
app.config["SECRET_KEY"] = binascii.unhexlify(os.environ["FLASK_SECRET_KEY"])

# Set the location of the client_secrets.json file.
app.config["OIDC_CLIENT_SECRETS"] = os.environ.get("CLIENT_SECRETS_FILE", "/app/client_secrets.json")

oidc = flask_oidc.OpenIDConnect(app)

TMPL = jinja2.Environment(autoescape=True).from_string("""
<html>
    <p>Hello, {{ term_of_address }}!</p>

    <p>{{ content }}</p>

    <ul>
        <li><a href="/secret">secret</a></li>
        <li><a href="/other-secret">other secret</a></li>
    </ul>
</html>
""")

@app.route("/callback")
@oidc.custom_callback
def callback(state):
    redirect_to = state.get("destination") or "/"
    return flask.redirect(redirect_to)

# oidc.require_login should not be used alongside oidc.custom_callback.
# require_login() performs a plain-destination redirect through the OIDC
# server; a custom callback expects a redirect with a customstate object.
# (Even if all that customstate object contains really is just a
# redirect destination. Using a custom callback leaves open the
# potential for passing more.)
oidc.require_login = None  # not compatible with custom callback

# Below is a replacement decorator.
# It should be used with a "target" argument:
#   @require_login(target="/secret")

class require_login(object):
    """A require_login decorator that works with a custom callback."""

    def __init__(self, **default_state):
        self.default_state = default_state

    def __call__(self, view_func):
        @functools.wraps(view_func)
        def decorated(*args, **kwargs):
            if flask.g.oidc_id_token is None:
                return oidc.redirect_to_auth_server(None, self.default_state)
            return view_func(*args, **kwargs)
        return decorated

def render_page(content=""):
    if oidc.user_loggedin:
        email = oidc.user_getfield("email")
        addressed_as = "logged-in user {}".format(oidc.user_getfield("sub"))
        if email:
            addressed_as += " (with email {})".format(email)
    else:
        addressed_as = "logged-out user"
    return TMPL.render(
        term_of_address=addressed_as,
        content=content,
    )

@app.route("/")
def index():
    return render_page()

@app.route("/secret")
@require_login(destination="/secret")
def secret():
    return render_page("soylent green is people")

@app.route("/other-secret")
@require_login(destination="/other-secret")
def other_secret():
    return render_page("Edelgard is the Flame Emperor")
