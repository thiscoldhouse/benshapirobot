import time
import praw
import random

import secrets


# ------------------------ content ----------------------------- #
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


TEMPLATE = "I saw that you mentioned Ben Shapiro. In case some of you don't know, Ben Shapiro is a grifter and a hack. If you find anything he's said compelling, you should keep in mind he also says things like this:\n\n>{QUOTE}"

P_WORD_MESSAGE =  """
Remember when Ben Shapiro recited the lyrics to WAP on his show and was too uncomfortable to say "pussy" so he said "p-word?" Then, when everyone made fun of him, he doubled down and tweeted:


>My only real concern is that the women involved -- who apparently require a "bucket and a mop" -- get the medical care they require. My doctor wife's differential diagnosis: bacterial vaginosis, yeast infection, or trichomonis.

"""

GOOD_BOT_REPLIES = [
    "Take a bullet for ya babe.",
    "Thank you for your logic and reason.",
]

BAD_BOT_REPLIES = [
    "So much for the tolerant left.",
    "Straw men are easier to knock down than real arguments.",
    "Another millenial snowflake offended by logic and reason.",
]

SHITPOSTS = {
    'FEMINISM': [
        "This is what the radical feminist movement was proposing, remember? Women need a man the way a fish needs a bicycle... unless it turns out that they're little fish, then you might need another fish around to help take care of things.",
        "Women kind of like having babies. This notion that women don't want to have babies is so bizarre. Has anyone ever met a 35 year old single woman? The vast majority of women who are 35 and single are not supremely happy.",
    ],
    'PATRIOTISM': [
        "America was built on values that the left is fighting every single day to tear down.",
        "Judeo-Christian values made The West great.",
    ],
    'TAUNT': [
        "If you're not scared, why won't you debate me?",
        "Another liberal DESTROYED.",
    ]
}

FOOTNOTE = """
^(I'm a bot. My purpose is to contextualize--and poke some light-hearted fun at--Ben Shapiro to counteract the social media pipeline that sends people his way. I'm part of a project that uses technology to better understand Ben and other right wing grifters. More info and feedback at /r/AuthoritarianMoment)

^(You can also summon me by mentioning /u/thebenshapirobot and mentioning {options} )
"""

options = []
for i, option in enumerate(SHITPOSTS.keys()):
    option = option.lower()
    if i + 1 == len(SHITPOSTS.keys()):
        option = f'or {option}'
    options.append(option)
FOOTNOTE = FOOTNOTE.format(options=', '.join(options))

# --------------- reddit config ---------------------------- #

EXCLUDED_USERS = [
    'automoderator', 'sneakpeekbot',
]
EXCLUDED_SUBS = [
    'benshapiro', 'conservative',
    # banned
    'whatisthisbug', 'KUWTK', 'okbuddyretard',
    # too frequent:
    'redscarepod',
    # karma requirements:
    'centrist', 'bravorealhousewives', 'toiletpaperusa', 'librandu'
]

# ################################# actual code ########################################## #


# ---- helpers ----- #

def already_in_thread_helper(root_ancestor, depth=0):
    print('----')
    print('DEPTH', depth)
    if depth == 10:
        return False

    for reply in root_ancestor.replies:
        if reply.author is not None:
            if str(reply.author.name).lower() == secrets.USERNAME:
                return True

        if already_in_thread_helper(reply, depth+1):
            return True
    else:
        return False


def already_in_thread(comment):
    if type(comment) is not praw.models.Comment:
        return False

    # this excerpt adapted from
    # https://praw.readthedocs.io/en/latest/code_overview/models/comment.html
    ancestor = comment
    refresh_counter = 0
    while not ancestor.is_root:
        if ancestor.author is not None:
            if str(ancestor.author.name).lower() == secrets.USERNAME:
                return True
        ancestor = ancestor.parent()
        if refresh_counter % 9 == 0:
            ancestor.refresh()
        refresh_counter += 1

    return already_in_thread_helper(comment)


def should_shitpost(submission):
    # check immediate ancestors only
    i = 0
    for comment in submission.comments.replace_more(limit=None):
        if comment.author is not None:
            if comment.author.name == secrets.USERNAME:
                i += 1
                if i >= SHITPOST_THRESHOLD:
                    return True
    # traverse root comment's tree
    if already_in_thread(submission):
        return True
    return False


def clean_comment(comment):
    return ' '.join(w.lower() for w in comment.body.split())


def get_summons_message(comment):
    words = clean_comment(comment)
    for word in SHITPOSTS.keys():
        if word.lower() in words:
            return random.choice(SHITPOSTS[word])
    else:
        return random.choice(
            SHITPOSTS[
                random.choice(
                    list(SHITPOSTS.keys())
                )
            ]
        )


def should_reply(comment):
    if str(comment.subreddit).lower() in EXCLUDED_SUBS:
        print(comment.subreddit).lower()
        print('in exclued subs')
        return False

    try:
        comment.refresh()
    except praw.exceptions.ClientException:
        print('Failed to refresh comment, moving on')

    if (
            secrets.USERNAME.lower() in
            [
                r.author.name.lower() for r in comment.replies
                if r.author is not None
            ]
    ):
        print('already replied')
        return False
    if comment.author is not None:
        print('author is none')
        if comment.author.name.lower() in EXCLUDED_USERS:
            return False
    return True

# --------- end helpers ------------ #

# only place that actually replies
def reply_if_appropriate(comment, message_type):
    if should_reply(comment) is False:
        print(comment.body)
        print('SHOULD REPLY IS FALSE')
        return

    message = None
    if message_type == 'GENERIC':
        if should_shitpost(comment.submission):
            return reply_if_appropriate(comment, 'SHITPOST')
        message = TEMPLATE.format(
            QUOTE=random.choice(QUOTES)
        )

    elif message_type == 'P-WORD':
        message = P_WORD_MESSAGE
    elif message_type == 'DEBATE-ME':
        message = "Why won't you debate me?"
    elif message_type == 'SHITPOST':
        message = random.choice(SHITPOSTS)
    elif message_type == 'GOOD-BOT-REPLY':
        message = random.choice(GOOD_BOT_REPLIES)
    elif message_type == 'BAD-BOT-REPLY':
        message = random.choice(BAD_BOT_REPLIES)
    elif message_type == 'SUMMONS':
        message = get_summons_message(comment)
    else:
        raise ValueError(f'Invalid message_type {message_type}')

    message = '\n\n'.join((message, FOOTNOTE))
    result = comment.reply(message)
    print(f'Made comment {result.permalink}')
    return result


# -------- state functions --------- #


def respond_to_replies(r, subs):
    me = praw.models.Redditor(r, name=secrets.USERNAME)
    results = []
    for i, comment in enumerate(me.comments.new()):
        comment.refresh()
        if i > 5:
            break
        for reply in comment.replies:
            if 'good bot' in str(comment.body).lower():
                results.append(
                    reply_if_appropriate(reply, 'GOOD-BOT-REPLY')
                )
            elif 'bad bot' in str(comment.body).lower():
                results.append(
                    reply_if_appropriate(reply, 'BAD-BOT-REPLY')
                )

            else:
                results.append(
                    reply_if_appropriate(reply, 'DEBATE-ME')
                )
    return results

def respond_to_mentions(r, subs):
    for i, mention in enumerate(r.inbox.mentions(limit=5)):
        if not mention.new:
            continue
        mention.mark_read()
        reply_if_appropriate(mention, 'SUMMONS')


def respond_to_comments(comment, r, subs):
    print(comment)
    if (
            comment.author.name.lower() == secrets.USERNAME or
            comment.subreddit.display_name.lower() in EXCLUDED_SUBS
    ):
        return
    words = clean_comment(comment)
    result = None
    if 'ben shapiro' in words:
        result = reply_if_appropriate(comment, 'GENERIC')

    elif any([
            phrase in words
            for phrase in ['wet ass pussy', ' p-word', ' cardi b', 'megan three stallion']
    ]):
        yield reply_if_appropriate(comment, 'P-WORD')


def handle_polling(r, subs):
    while True:
        for action in (
                respond_to_mentions,
                respond_to_replies,
        ):
            action(r, subs)

# ---------- main loop ---------- #

def main(subs='all'):
    r = praw.Reddit(
        client_id=secrets.CLIENT_ID,
        client_secret=secrets.SECRET,
        user_agent=f'{secrets.USERNAME} (by /u/headgasketidiot)',
        username=secrets.USERNAME,
        password=secrets.PASSWORD
    )

    t = time.time()
    for i, comment in enumerate(r.subreddit(subs).stream.comments()):
        respond_to_comments(comment, r, subs)
        if time.time() - t >= 30:
            handle_polling(r, subs)
            t = time.time()

if __name__ == '__main__':
    main("authoritarianmoment")
    #main()
