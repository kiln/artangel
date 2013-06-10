#!/usr/bin/python

import json
import optparse
import re
import types

import redis
import tweepy

oauth_data = {
    "CONSUMER_KEY": "B0RgCrQ73LK5gWyRYPVLYA",
    "CONSUMER_SECRET": "bLpNaI7ziNUQFyVM0XLHDoqnaRLzlymiz2qY4Yes",
    "ACCESS_TOKEN": "34650516-UERO93A7gDvh11vHJvD1QPv6JvB3BHQgLPntudtni",
    "ACCESS_TOKEN_SECRET": "r9igzim5q4RmD9NMjRFmOQN4ayrTEgjKEZctWRlEBU",
}

BURMA_BOUNDING_BOX = [91.833, 6.000, 102.000, 28.350]

KEYWORDS = [
    "burma", "democracy", "rohingya", "human rights",
    "transparency", "election", "myanmar", "violence"
]

# Methods for converting Tweepy objects to JSON
def _as_json(o):
    return json.dumps(_as_dict(o))

def _as_dict(o):
    if isinstance(o, tweepy.models.Model):
        return dict((
            (x, _as_dict(getattr(o, x)))
            for x in dir(o)
            if not x.startswith('_')
            and not isinstance(getattr(o, x), types.MethodType)
        ))
    elif isinstance(o, int):
        return o
    elif o is None:
        return None
    else:
        return unicode(o)


# Parse the command-line options
parser = optparse.OptionParser()
(options, args) = parser.parse_args()

# Create a Redis connection (It does not actually connect till used)
r = redis.StrictRedis()

auth = tweepy.OAuthHandler(oauth_data["CONSUMER_KEY"], oauth_data["CONSUMER_SECRET"])
auth.set_access_token(oauth_data["ACCESS_TOKEN"], oauth_data["ACCESS_TOKEN_SECRET"])

# Create a Tweepy API object
api = tweepy.API(auth, secure=True)

# The current released version of Tweepy does not have the get_oembed function yet
api.get_oembed = types.MethodType(
    tweepy.binder.bind_api(
        path = '/statuses/oembed.json',
        payload_type = 'json',
        allowed_param = ['id', 'url', 'maxwidth', 'hide_media', 'omit_script', 'align', 'related', 'lang']
    ), api)

def text_to_html(text):
    return re.sub(r"[&<>\"']", lambda m: {
        '&': "&amp;",
        '<': "&lt;",
        '>': "&gt;",
        '"': "&quot;",
        "'": "&apos;",
    }[m.group(0)],text)

def fake_oembed_html(status):
    return u"""<blockquote class="twitter-tweet"><p>{tweet_text_html}</p>&mdash; {user_name} (@{user_screen_name}) <a href="https://twitter.com/{user_screen_name}/statuses/{tweet_id}">{date}</a></blockquote>""".format(
        tweet_text_html=text_to_html(status.text),
        user_name=status.user.name,
        user_screen_name=status.user.screen_name,
        tweet_id=status.id_str,
        date=status.created_at
    )

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        #print _as_json(status)
        
        # This is the best way to get the HTML embed code, but we quickly
        # fall foul of the rate limit if we do it this way.
        #
        # oembed_json = json.dumps(api.get_oembed(id=status.id_str))
        
        oembed_json = json.dumps({"html": fake_oembed_html(status)})
        for keyword in KEYWORDS:
            if re.search(r"\b" + keyword, status.text, re.I):
                print "MATCH " + keyword
                r.publish(keyword, oembed_json)

# Perform the search
listener = MyStreamListener()
tweepy.Stream(auth, listener).filter(track=KEYWORDS)
