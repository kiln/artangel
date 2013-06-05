#!/usr/bin/python

import json
import optparse
import sys
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
parser.add_option("", "--channel",
                  action="store", default="artangel",
                  help="Redis channel to publish results on")
(options, keywords) = parser.parse_args()

# Create a Redis connection (It does not actu)
r = redis.StrictRedis()

# Perform the search
auth = tweepy.OAuthHandler(oauth_data["CONSUMER_KEY"], oauth_data["CONSUMER_SECRET"])
auth.set_access_token(oauth_data["ACCESS_TOKEN"], oauth_data["ACCESS_TOKEN_SECRET"])

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        r.publish(options.channel, _as_json(status))

listener = MyStreamListener()
tweepy.Stream(auth, listener).filter(track=keywords)
