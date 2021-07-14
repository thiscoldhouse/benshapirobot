import time
import praw
import random

import secrets


QUOTES = [
    'Israelis like to build. Arabs like to bomb crap and live in open sewage. This is not a difficult issue.',
    "If you wear your pants below your butt, don't bend the brim of your cap, and have an EBT card, 0% chance you will ever be a success in life.",
    "Since nobody seems willing to state the obvious due to cultural sensitivity... I’ll say it: rap isn’t music",
    'Rappers have the life expectancies of fruit flies: by the time they’re 40 – if they hit 40 – there’s a good shot they’ll have shot somebody, been shot, been busted for hard core drugs, or acquired an STD',
    ' Palestinian Arabs have demonstrated their preference for suicide bombing over working toilets.',
    'The Palestinian people, who dress their toddlers in bomb belts and then take family snapshots.',
    'The Palestinian Arab population is rotten to the core.',
    'There is no doubt that law enforcement should be heavily scrutinizing the membership and administration of mosques.',
    'If you believe that the Jewish state has a right to exist, then you must allow Israel to transfer the Palestinians and the Israeli-Arabs from Judea, Samaria, Gaza and Israel proper. It’s an ugly solution, but it is the only solution… It’s time to stop being squeamish.'
]


TEMPLATE = """
I saw that you mentioned Ben Shapiro. In case you don't know, Ben Shapiro is a grifter and a hack. If you find anything he's said compelling, you should keep in mind he also says things like this:\n\n\n\n
>{QUOTE}
\n\n\n\n^(I'm BensHapiRobot. My purpose is to contextualize Ben Shapiro to counteract the social media pipeline that sends people his way. I'm part of a project that uses technology to better understand Ben and other right wing grifters. More at /r/AuthoritarianMoment and https://theauthoritarianmoment.com)
"""

ALREADY_REPLIED = set()

def reply_if_appropriate(comment):
    if (
            'benshapirobot' in [r.author.name for r in comment.replies] or
            comment.link_id in ALREADY_REPLIED
    ):
        return
    message = TEMPLATE.format(
        QUOTE=random.choice(QUOTES)
    )
    ALREADY_REPLIED.add(comment.link_id)
    result = comment.reply(message)
    print(f'Made comment {result.permalink}')
    import pdb; pdb.set_trace()
    return result


def main(subs='all'):
    r = praw.Reddit(
        client_id=secrets.CLIENT_ID,
        client_secret=secrets.SECRET,
        user_agent='BenShapiroBot (by /u/headgasketidiot)',
        username="benshapirobot",
        password=secrets.PASSWORD
    )

    for i, comment in enumerate(r.subreddit(subs).stream.comments()):
        if comment.author.name.lower() == 'benshapirobot':
            continue

        words = ' '.join(w.lower() for w in comment.body.split())
        if 'ben shapiro' in words:
            result = reply_if_appropriate(comment)


if __name__ == '__main__':
    main()
