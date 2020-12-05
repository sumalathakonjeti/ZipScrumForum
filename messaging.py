from flask import *
from datetime import datetime
from collections import namedtuple

Message = namedtuple('Message', ['sender', 'message', 'date'])

app = Flask(__name__)
app.config['CSRF_ENABLED'] = True

MAX_MESSAGES = 3

messages = []  # list of Message(s)



@app.route('/lst')
def list_messages():
    """list all messages (TXT)"""
    return '%d messages: %s' % (len(messages), ",\n".join(messages))


@app.route('/latest')
def latest_message():
    """show latest message (JSON)"""
    import json
    latest = messages[-1] if len(messages) else None
    if latest:
        msg = latest.message
        if latest.sender:
            msg = ("%s: " % latest.sender) + msg
        if latest.date:
            now = datetime.now()
            delta = now - latest.date
            if delta.days == 0:
                dstr = "Today %s" % latest.date.strftime('%H:%M')
            elif delta.days == 1:
                dstr = "Yesterday %s" % latest.date.strftime('%H:%M')
            else:
                dstr = latest.date.strftime('%Y-%m-%d %H:%M')
            msg = msg + (" (%s)" % dstr)
    else:
        msg = "No Messages"

    output = {"frames": [{
        "index": 0,
        "text": msg,
        "icon": "i43"
    }]
    }
    return json.dumps(output)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


