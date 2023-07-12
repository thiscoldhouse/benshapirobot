import time
import sys
import json
from prawcore.exceptions import Forbidden
from praw.exceptions import RedditAPIException
import praw
import random
import re
import secrets

import logging
logging.basicConfig(filename="comments.log")

# ------------------------ content ----------------------------- #

QUOTES = [
    'Israelis like to build. Arabs like to bomb crap and live in open sewage. This is not a difficult issue.',
    "If you wear your pants below your butt, don't bend the brim of your cap, and have an EBT card, 0% chance you will ever be a success in life.",
    "Since nobody seems willing to state the obvious due to cultural sensitivity... I’ll say it: rap isn’t music",
    ' Palestinian Arabs have demonstrated their preference for suicide bombing over working toilets.',
    'The Palestinian people, who dress their toddlers in bomb belts and then take family snapshots.',
    'The Palestinian Arab population is rotten to the core.',
    'There is no doubt that law enforcement should be heavily scrutinizing the membership and administration of mosques.',
    'If you believe that the Jewish state has a right to exist, then you must allow Israel to transfer the Palestinians and the Israeli-Arabs from Judea, Samaria, Gaza and Israel proper. It’s an ugly solution, but it is the only solution... It’s time to stop being squeamish.',
    "Most Americans when they look around at their lives, they think: I'm not a racist, nobody I know is a racist, I wouldn't hang out with a racist, I don't like doing business with racists--so, where is all the racism in American society?",
    "When it comes to global warming, there are two issues: is there such a thing as the greenhouse gas effect, the answer is yes. Is that something that is going to dramatically reshape our world? There is no evidence to show that it will. Is that something that we can stop? There is no evidence to show that we can",
    "Even climatologists can't predict 10 years from now. They can't explain why there has been no warming over the last 15 years. There has been a static trend with regard to temperature for 15 years.",
    'If you believe that the Jewish state has a right to exist, then you must allow Israel to transfer the Palestinians and the Israeli-Arabs from Judea, Samaria, Gaza and Israel proper. It’s an ugly solution, but it is the only solution… It’s time to stop being squeamish.',
    "This is what the radical feminist movement was proposing, remember? Women need a man the way a fish needs a bicycle... unless it turns out that they're little fish, then you might need another fish around to help take care of things.",
        '''Let’s say your life depended on the following choice today: you must obtain either an affordable chair or an affordable X-ray. Which would you choose to obtain? Obviously, you’d choose the chair. That’s because there are many types of chair, produced by scores of different companies and widely distributed. You could buy a $15 folding chair or a $1,000 antique without the slightest difficulty. By contrast, to obtain an X-ray you’d have to work with your insurance company, wait for an appointment, and then haggle over price. Why? Because the medical market is far more regulated — thanks to the widespread perception that health care is a “right” — than the chair market. Does that sound soulless? True soullessness is depriving people of the choices they require because you’re more interested in patting yourself on the back by inventing rights than by incentivizing the creation of goods and services. In health care, we could use a lot less virtue signaling and a lot less government. Or we could just read Senator Sanders’s tweets while we wait in line for a government-sponsored surgery — dying, presumably, in a decrepit chair.''',
    'Pegging, of course, is an obscure sexual practice in which women perform the more aggressive sexual act on men.',
    "Heterosexual marriage is the cornerstone of society; homosexual marriage offers no benefits to society.",
]


TEMPLATE = "I saw that you mentioned Ben Shapiro. In case some of you don't know, Ben Shapiro is a grifter and a hack. If you find anything he's said compelling, you should keep in mind he also says things like this:\n\n>{QUOTE}"


GOOD_BOT_REPLIES = [
    "Take a bullet for ya babe.",
    "Thank you for your logic and reason.",
]

BAD_BOT_REPLIES = [
    "So much for the tolerant left.",
    "Straw men are easier to knock down than real arguments.",
    "Another millenial snowflake offended by logic and reason.",
]

GOOD_BOT_REPLY_REPLIES = [
    "You're a bear of a man.",
]

SHITPOSTS = {
    'HEALTHCARE': [
        '''Let’s say your life depended on the following choice today: you must obtain either an affordable chair or an affordable X-ray. Which would you choose to obtain? Obviously, you’d choose the chair. That’s because there are many types of chair, produced by scores of different companies and widely distributed. You could buy a $15 folding chair or a $1,000 antique without the slightest difficulty. By contrast, to obtain an X-ray you’d have to work with your insurance company, wait for an appointment, and then haggle over price. Why? Because the medical market is far more regulated — thanks to the widespread perception that health care is a “right” — than the chair market.*


*Does that sound soulless? True soullessness is depriving people of the choices they require because you’re more interested in patting yourself on the back by inventing rights than by incentivizing the creation of goods and services. In health care, we could use a lot less virtue signaling and a lot less government. Or we could just read Senator Sanders’s tweets while we wait in line for a government-sponsored surgery — dying, presumably, in a decrepit chair.''',
        '''New York Magazine’s Jesse Singal, wrote that “free markets are good at some things and terrible at others and it’s silly to view them as ends rather than means.” That’s untrue. Free markets are expressions of individual autonomy, and therefore ends to be pursued in themselves.''',
    ],
    'COVID':[
        "And then, there are people in the United States that are pushing for mask mandates on children. The data that they are using are extraordinarily skimpy--in fact, they are essentially nonexistent. You're hearing the CDC say things like 'maybe the delta variant does more damage to kids,' but no information they have presented publicly that there is more damage being done to kids... and the reason we are being told that they damage kids is because they can't scare the adults enough. If we cannot scare the adults enough, we're going to have to mask up the kids.",
        "We are being told that if we don't mask our children, that if we don't mask ourselves, that if we don't initiate social distancing measures again and shut down business again, that COVID is going to kill us all",
    ],
    "GAY MARRIAGE": [
        "Heterosexual marriage is the cornerstone of society; homosexual marriage offers no benefits to society.",
        "If you vote in favor of the idea that society has an obligation to recognize male-male or female-female dyads in the same way that society has an obligation to recognize male-female, you should not be in the Republican party.",
    ],
    'SEX': [
        "By objectification of women, do you mean that there are actual standards of beauty and that there are many people in popular culture who we have been told are supposed to be seen as beautiful who are not objectively beautiful? Obviously that's true. Obviously that's true. If you polled men on whether Lizzo is beautiful--and I say Lizzo is not by any classical definition a beautiful person--that does not mean that that is objectification of women, that just means that there is a standard called beauty and it has meaning.",
        "I've been an outspoken anti-porn advocate since I was like sixteen years old.",
        'Pegging, of course, is an obscure sexual practice in which women perform the more aggressive sexual act on men.',
        "My only real concern is that the women involved -- who apparently require a \"bucket and a mop\" -- get the medical care they require. My doctor wife's differential diagnosis: bacterial vaginosis, yeast infection, or trichomonis.",
    ],
    'CLIMATE': [
        'Renewable energy: dumbest phrase since climate change. See the first law of thermodynamics, dumbass.',
        "When it comes to global warming, there are two issues: is there such a thing as the greenhouse gas effect, the answer is yes. Is that something that is going to dramatically reshape our world? There is no evidence to show that it will. Is that something that we can stop? There is no evidence to show that we can",
        "Even climatologists can't predict 10 years from now. They can't explain why there has been no warming over the last 15 years. There has been a static trend with regard to temperature for 15 years.",
        "The weatherman can't even predict the weather a few days from now"
    ],
    'NOVEL': [
        """Hawthorne was a bear of a man, six three in his bare feet and two hundred fifteen pounds in his underwear, with a graying blond crew cut and a face carved of granite. But he had plenty of smile lines. He just didn’t like showing those to people unless he knew them.
        """,
        """ Standing above him, glaring at him, was a behemoth, a black kid named Yard. Nobody knew his real name—everybody just called him Yard because he played on the school football team, stood six foot five, clocked in at a solid two hundred eighty pounds, and looked like he was headed straight for a lifetime of prison workouts. The coach loved him. Everybody else feared him.
        """,
        """Brett didn’t care about that. He turned, irked—and found himself face-to-face with a beautiful young woman, about seventeen, staring aggressively at him.
        """,
        """Soledad Ramirez knew the value of good press, and she baked mean
chocolate chip cookies. “No oatmeal raisin here,” she said good-naturedly,
handing out the meltingly hot treats to the men wearing full military gear and
carrying M4s set to burst.
        """,
        """Then he heard the voice.

   “Hey, pig,” it said. The voice wasn’t deep. It was the voice of a child. And the
kid stood outside the door of the quick mart, legs spread, arms hanging down by
his sides. A cute black kid, wearing a Simpsons T-shirt and somebody’s old
Converse sneakers and baggy jeans.

   On his hip, stuck in those baggy jeans, was a pistol.

   It looked like a pistol, anyway. But O’Sullivan couldn’t see clearly. The light
wasn’t right. He could see the bulge, but not the object.

   O’Sullivan put his flashlight back in his belt and put his hand back on his
pistol, the greasy handle still warm to the touch.

   “Stop right there, pig,” the kid said. His hand began to creep down toward his
waistband.

   O’Sullivan pulled the gun out of its holster, leveling it at the kid. “Put your
hands above your head. Do it now!”

   “Fuck you, honky,” the kid shot back. “Get the fuck out of my neighborhood.”
Then he laughed, a cute kid’s laugh. O’Sullivan looked for sympathy behind
those eyes, found none.

   Oh, shit, O’Sullivan thought. Then he said, “Hands up. Right now.”

   The kid laughed again, a musical tinkling noise. “You ain’t gonna shoot me,
pig. What, you afraid of a kid?”

   O’Sullivan could feel every breath as it entered his lungs. “No, kid, I don’t
want to shoot you,” he said. “But I need you to cooperate. Put your hands above
your head. Right now.”

   The kid’s hand shifted to his waistband again. O’Sullivan’s hands began to
shake.

   “Get the fuck out of my neighborhood,” the kid repeated.

   O’Sullivan looked around stealthily. Still nobody on the street. Totally empty.
The sweat on his forehead felt cold in the night air. In the retraining sessions at
the station, they’d told officers to remember the nasty racial legacy of the
department, be aware of the community’s justified suspicion of police. Right
now, all O’Sullivan was thinking about was getting this kid with the empty eyes
to back the fuck off.

   “Go on home,” he said.

   “You go home, white boy,” said the kid. His hand moved lower.

   Suddenly, O’Sullivan’s head filled with a sudden clarity, his brain with a
preternatural energy. He recognized the feel of the adrenaline hitting. He wasn’t
going to get shot on the corner of Iowa and Van Dyke outside a shitty
convenience store in a shitty town by some eight-year-old, bleed out in the gutter
of some city the world left behind. He had a life, too.

   The gun felt alive in his hand. The gun was life.

   The muzzle was aimed dead at the kid’s chest. No way to miss, with the kid
this close, just ten feet away maybe. Still cloaked in the shadow of the gas
station overhang.

   “Kid, I’m not going to ask you again. I need you to put your hands on top of
your head and get on your knees.”

   “Fuck you, motherfucker.”

   “I’m serious.”

   The kid’s hand was nearly inside his waistband now.

   “Don’t do that,” O’Sullivan said.

   The kid smiled, almost gently.

   “Don’t.”

   The kid’s smile broadened, the hand moved down into the pants. “Get the
fuck out of my hood,” the kid cheerfully repeated. “I’ll cap your ass.”

   “Kid, I’m warning you,” O’Sullivan yelled. “Put your hands above your head!
Do it now…”

   The roar shattered the night air, a sonic boom in the blackness. The shot blew
the kid off his feet completely, knocked him onto his back.

   O’Sullivan reached for his radio, mechanically reported it: “Shots fired,
officer needs help at the gas station on Iowa and Van Dyke.”

   “Ohgodohgodohgodohgod,” O’Sullivan repeated as he moved toward the
body, the smoke rising from his Glock. He pointed it down at the kid again, but
the boy wasn’t moving. The blood seeped through Homer Simpson’s face,
pooled around the kid’s lifeless body. The grin had been replaced with a look of
instantaneous shock. His hand had fallen out of his waistband with the force of
the shooting.

   In it was a toy gun, the tip orange plastic.

   For a brief moment, O’Sullivan couldn’t breathe. When he looked up, he saw
them coming. Dozens of them. The citizens of Detroit, coming out of the
darkness, congregating. He could feel their eyes.

   Officer Ricky O’Sullivan sat down on the curb and began to cry.
        """
    ],
    'FEMINISM': [
        "This is what the radical feminist movement was proposing, remember? Women need a man the way a fish needs a bicycle... unless it turns out that they're little fish, then you might need another fish around to help take care of things.",
        "Women kind of like having babies. This notion that women don't want to have babies is so bizarre. Has anyone even met a 35 year old single woman? The vast majority of women who are 35 and single are not supremely happy.",
    ],
    'HISTORY': [
        "Freedom is an invention of the last couple of centuries. It really did not exist en masse until the last couple of centuries--and even then, really only since the end of the Soviet Union has it been sorta the broad movement of the public across the world.",
        "America was built on values that the left is fighting every single day to tear down.",
    ],
    'CIVIL RIGHTS': [
        "“Native American culture [being] inferior to Western culture…is a contention with which I generally agree.",
        "Most Americans when they look around at their lives, they think: I'm not a racist, nobody I know is a racist, I wouldn't hang out with a racist, I don't like doing business with racists--so, where is all the racism in American society?",
        'I don’t think the law has any role whatsoever in banning race-based discrimination by private actors',
    ],
    'DUMB TAKES': [
        "Frankly, the term 'sexual orientation' needs to go. According to Webster's Dictionary, it implies the possibility of change in response to external stimuli. It is deeply offensive. I call on Webster's to free itself of its intellectual heteronormativity.",
        "Let’s say, for the sake of argument, that all of the water levels around the world rise by, let’s say, five feet or ten feet over the next hundred years. It puts all the low-lying areas on the coast underwater. Let’s say all of that happens. You think that people aren’t just going to sell their homes and move?",
        "Trayvon Martin would have turned 21 today if he hadn't taken a man's head and beaten it on the pavement before being shot.",
    ],
    'TAUNT': [
        "If you like socialism so much why don't you go to Venezuela?",
        "Another liberal DESTROYED.",
    ]
}

SHITPOST_THRESHOLD = 4


################################## actual code #################################

class BSBot():

    opt_out_regex = r'i .* have read and agree to the above terms and the enforecment thereof.'

    def __init__(self):
        config = None
        with open('reddit_config.json') as f:
            config = json.loads(f.read())

        self.EXCLUDED_USERS, self.EXCLUDED_SUBS = config['EXCLUDED_USERS'], config['EXCLUDED_SUBS']
        self.EXCLUDED_USERS.append('thebenshapirobotbot')
        self.EXCLUDED_USERS.append('automoderator')

        self.r = praw.Reddit(
            # TODO: move these into kwargs or something
            client_id=secrets.CLIENT_ID,
            client_secret=secrets.SECRET,
            user_agent=f'{secrets.USERNAME} (by /u/headgasketidiot)',
            username=secrets.USERNAME,
            password=secrets.PASSWORD
        )
        self.opt_out_submission = praw.models.Submission(self.r, id='olk6r2')

    def generate_footnote(self):
        options = [o.lower() for o in SHITPOSTS.keys()]
        options.remove('taunt')
        options = sorted(options, key=lambda x: random.random())[:4]
        options = ', '.join(options)
        options = f'{options}, etc.'
        return f"""
*****

^(I'm a bot. My purpose is to counteract online radicalization. You can summon me by tagging thebenshapirobot. Options: {options})



[^Opt ^Out ](https://np.reddit.com/r/AuthoritarianMoment/comments/olk6r2/click_here_to_optout_of_uthebenshapirobot/)
"""


    def am_i_author(self, comment):
        try:
            if comment.author is not None:
                if comment.author.name.lower() == secrets.USERNAME:
                    return True
            return False
        except AttributeError as e:
                return True
        return False

    def did_already_reply(self, comment):
        for reply in comment.replies:
            if type(reply) is praw.models.MoreComments:
                for comment in rely.comments:
                    if self.did_already_reply(comment):
                        return True
            elif self.am_i_author(reply):
                return True
        return False

    def handle_opt_outs(self):
        replies = []
        for comment in self.opt_out_submission.comments:
            try:
                comment.refresh()
            except praw.exceptions.ClientException as e:
                sys.stderr.write(f'Could not refresh comment {comment}. Exception: {e}')
                continue

            if comment.author is None:
                continue
            elif comment.author.name.lower() in self.EXCLUDED_USERS:
                continue

            replies.append(
                self.reply_if_appropriate(comment, 'OPT-OUT')
            )

            self.EXCLUDED_USERS.append(comment.author.name.lower())
            self.save_reddit_config()

        return replies

    def save_reddit_config(self):
        config = {}
        config['EXCLUDED_USERS'] = list(set(self.EXCLUDED_USERS))
        config['EXCLUDED_SUBS'] = list(set(self.EXCLUDED_SUBS))
        with open('reddit_config.json', 'w+') as f:
            f.write(json.dumps(config))

    def clean_comment(self, comment):
        return ' '.join(w.lower() for w in comment.body.split())

    def extract_keyword_from_comment(self, comment):
        words = self.clean_comment(comment)
        for word in SHITPOSTS.keys():
            if word.lower() in words:
                return word
        return None

    def get_shitpost_message(self, comment):
        key = self.extract_keyword_from_comment(comment)
        if key is None:
            key = random.choice(list(SHITPOSTS.keys()))

        message = random.choice(SHITPOSTS[key])
        if key == 'NOVEL':
            message = f'**An excerpt from True Allegiance, by Ben Shapiro:**\n\n\n{message}'
        elif key == 'TAUNT':
            pass
        else:
            message = f'*{message}*\n\n\n -Ben Shapiro'

        return message

    def should_shitpost(self, submission):
        i = 0
        me = praw.models.Redditor(self.r, name=secrets.USERNAME)
        for i, my_comment in enumerate(me.comments.new(limit=50)):
            if my_comment.submission.id == submission.id:
                i += 1
                if i >= SHITPOST_THRESHOLD:
                    return True
        return False

    def reply_if_appropriate(self, comment, message_type, custom_message=None):
        try:
            comment.refresh()
        except (praw.exceptions.ClientException, AttributeError) as e:
            sys.stderr.write(f'Could not refresh comment {comment}. Exception: {e}')
            return

        if (
                secrets.USERNAME.lower() in
                [
                    r.author.name.lower() for r in comment.replies
                    if r.author is not None
                ]
        ):
            return

        if comment.author is not None:
            if comment.author.name.lower() in self.EXCLUDED_USERS:
                if message_type != 'OPT-OUT':
                    return

        message = None
        if message_type == 'GENERIC':
            if self.should_shitpost(comment.submission):
                return self.reply_if_appropriate(comment, 'SHITPOST')

            message = TEMPLATE.format(
                QUOTE=random.choice(QUOTES)
            )
        # elif message_type == 'P-WORD':
        #     message = P_WORD_MESSAGE
        elif message_type == 'DEBATE-ME':
            if self.should_shitpost(comment.submission):
                return self.reply_if_appropriate(comment, 'SHITPOST')
            message = "Why won't you debate me?"
        elif message_type in ('SHITPOST', 'SUMMONS'):
            message = self.get_shitpost_message(comment)
        elif message_type == 'GOOD-BOT-REPLY':
            message = random.choice(GOOD_BOT_REPLIES)
        elif message_type == 'GOOD-BOT-REPLY-REPLY':
            message = random.choice(GOOD_BOT_REPLY_REPLIES)
        elif message_type == 'BAD-BOT-REPLY':
            message = random.choice(BAD_BOT_REPLIES)
        elif message_type == 'OPT-OUT':
            message = random.choice(BAD_BOT_REPLIES)
        elif message_type == 'REAL':
            message = 'Yup, all of the quotes and excerpts this bot posts that are explicitly attributed to Ben Shapiro are real. It is hard to believe people take him seriously.'
        elif message_type == 'IS_GRIFTER':
            message = 'He is absolutely a grifter.'
        elif message_type == 'CUSTOM' and custom_message is not None:
            message = custom_message
        else:
            raise ValueError(f'Invalid message_type {message_type}')

        message = '\n\n'.join((message, self.generate_footnote()))
        result = None
        try:
            result = comment.reply(message)
            print(f'Made comment {result.permalink}')
        except Exception as e:
            if type(e) is Forbidden:
                self.EXCLUDED_SUBS.append(comment.subreddit.display_name)
                self.save_reddit_config()
                sys.stderr.write(
                    f'Found new banned subreddit {comment.subreddit.display_name}'
                )
            elif type(e) is RedditAPIException:
                # for now, probably handle differently later?
                sys.stderr.write(
                    f'Reply failed with exception {e}'
                )
            else:
                sys.stderr.write(
                    f'Reply failed with exception {e}'
                )

        return result

    def avoid_rate_limit(self):
        time.sleep(2)

    def respond(self):
        results = []
        for reply in self.r.inbox.unread():
            submission_id = None
            try:
                submission_id = reply.submission.id
            except AttributeError as e:
                # some kinds of messages arne't associated with
                # subreddits.
                pass


            text = self.clean_comment(reply)
            response = None
            if submission_id == self.opt_out_submission.id:
                self.EXCLUDED_USERS.append(reply.author.name.lower())
                self.save_reddit_config()
                response = self.reply_if_appropriate(reply, 'OPT-OUT')
            elif 'good bot' in text:
                response = self.reply_if_appropriate(reply, 'GOOD-BOT-REPLY')
            elif 'bad bot' in text:
                response = self.reply_if_appropriate(reply, 'BAD-BOT-REPLY')
            elif 'is this real' in text or "can't be real" in text or "did he actually" in text:
                response = self.reply_if_appropriate(reply, 'REAL')
            elif 'take a bullet for y' in text:
                response = self.reply_if_appropriate(reply, 'GOOD-BOT-REPLY-REPLY')
            elif (
                    (
                        'grifter' in text or
                        'grift' in text
                    ) and
                    (
                        'believe' in text or
                        'think' in text or
                        'know' in text or
                        'really' in text or
                        'actually' in text
                    ) and (
                        len(text) < 140
                    )
            ):
                response = self.reply_if_appropriate(reply, 'IS_GRIFTER')
            else:
                key = self.extract_keyword_from_comment(reply)
                if key is None:
                    response = self.reply_if_appropriate(reply, 'DEBATE-ME')
                else:
                    response = self.reply_if_appropriate(reply, 'SUMMONS')

            if response is not None:
                self.avoid_rate_limit()
                results.append(response)
                reply.mark_read()

        return results

    def main(self, subs='all'):
        #self.handle_opt_outs()
        reply_on_next_loop = True
        for i, comment in enumerate(self.r.subreddit(subs).stream.comments()):
            if reply_on_next_loop:
                # avoids edge case of replying twice to someone because
                # they mentioned "ben shapiro" in a reply
                self.respond()
                reply_on_next_loop = False
            if comment.author is None:
                continue
            if (
                    comment.author.name.lower() == secrets.USERNAME or
                    comment.subreddit.display_name.lower() in self.EXCLUDED_SUBS
            ):
                continue

            words = self.clean_comment(comment)
            result = None
            if 'ben shapiro' in words:
                result = self.reply_if_appropriate(comment, 'GENERIC')
                reply_on_next_loop = True

if __name__ == '__main__':
    BSBot().main()
