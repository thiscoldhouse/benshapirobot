import time
import praw
import random

import secrets


QUOTES = [
    'Israelis like to build. Arabs like to bomb crap and live in open sewage. This is not a difficult issue.',
    "If you wear your pants below your butt, don't bend the brim of your cap, and have an EBT card, 0% chance you will ever be a success in life.",
    "Since nobody seems willing to state the obvious due to cultural sensitivity... I’ll say it: rap isn’t music",
    ' Palestinian Arabs have demonstrated their preference for suicide bombing over working toilets.',
    'The Palestinian people, who dress their toddlers in bomb belts and then take family snapshots.',
    'The Palestinian Arab population is rotten to the core.',
    'There is no doubt that law enforcement should be heavily scrutinizing the membership and administration of mosques.',
    'If you believe that the Jewish state has a right to exist, then you must allow Israel to transfer the Palestinians and the Israeli-Arabs from Judea, Samaria, Gaza and Israel proper. It’s an ugly solution, but it is the only solution… It’s time to stop being squeamish.'
]
FOOTNOTE = "^(I'm a bot. My purpose is to contextualize--and poke some light-hearted fun at--Ben Shapiro to counteract the social media pipeline that sends people his way. I'm part of a project that uses technology to better understand Ben and other right wing grifters. More at /r/AuthoritarianMoment)"

TEMPLATE = "I saw that you mentioned Ben Shapiro. In case you don't know, Ben Shapiro is a grifter and a hack. If you find anything he's said compelling, you should keep in mind he also says things like this:\n\n>{QUOTE}"

SHITPOST_THRESHOLD = 2
SHITPOSTS = [
    "Facts don't care about your feelings.",
    "America was built on values that the left is fighting every single day to tear down.",
    "Judeo-Christian values made The West great.",
    "If you're not scared, why won't you debate me?",
    "Another liberal DESTROYED.",
]

EXCLUDED_SUBS = [
    'benshapiro', 'conservative',
    # too frequent:
    'redscarepod',
    # karma requirements:
    'centrist', 'bravorealhousewives'
]


def should_shitpost(submission):
    i = 0
    for comment in submission.comments.replace_more(limit=None):
        if comment.author is None:
            # I don't understand this, whatever
            continue
        elif comment.author.name == secrets.USERNAME:
            i += 1
            if i >= SHITPOST_THRESHOLD:
                return True
    return False

def reply_if_appropriate(comment, message_type):
    comment.refresh()
    if (
            secrets.USERNAME.lower() in
            [
                r.author.name.lower() for r in comment.replies
                if r.author is not None
            ]
    ):
        return

    if comment.author is not None:
        if comment.author.name.lower() == 'automoderator':
            return

    message = None
    if message_type == 'GENERIC':
        if should_shitpost(comment.submission):
            return reply_if_appropriate(comment, 'SHITPOST')

        message = TEMPLATE.format(
            QUOTE=random.choice(QUOTES)
        )

    elif message_type == 'P-WORD':
        message = "My only real concern is that the women involved -- who apparently require a \"bucket and a mop\" -- get the medical care they require. My doctor wife's differential diagnosis: bacterial vaginosis, yeast infection, or trichomonis."
    elif message_type == 'DEBATE-ME':
        message = "Why won't you debate me?"
    elif message_type == 'SHITPOST':
        message = random.choice(SHITPOSTS)
    else:
        raise ValueError(f'Invalid message_type {message_type}')

    message = '\n\n'.join((message, FOOTNOTE))
    result = comment.reply(message)
    print(f'Made comment {result.permalink}')
    return result


def challenge_responders_to_debate(r):
    me = praw.models.Redditor(r, name=secrets.USERNAME)
    results = []
    for i, comment in enumerate(me.comments.new()):
        comment.refresh()
        if i > 5:
            break
        for reply in comment.replies:
            results.append(
                reply_if_appropriate(reply, 'DEBATE-ME')
            )

    return results


def main(subs='all'):
    r = praw.Reddit(
        client_id=secrets.CLIENT_ID,
        client_secret=secrets.SECRET,
        user_agent=f'{secrets.USERNAME} (by /u/headgasketidiot)',
        username=secrets.USERNAME,
        password=secrets.PASSWORD
    )

    for i, comment in enumerate(r.subreddit(subs).stream.comments()):
        if (
                comment.author.name.lower() == secrets.USERNAME or
                comment.subreddit.display_name.lower() in EXCLUDED_SUBS
        ):
            continue

        words = ' '.join(w.lower() for w in comment.body.split())
        result = None
        if 'ben shapiro' in words:
            result = reply_if_appropriate(comment, 'GENERIC')

        elif any([
                phrase in words
                for phrase in ['wet ass pussy', ' p-word', 'cardi b', 'megan three stallion']
        ]):
            result = reply_if_appropriate(comment, 'P-WORD')

        if result is not None:
            challenge_responders_to_debate(r)


if __name__ == '__main__':
    main()
