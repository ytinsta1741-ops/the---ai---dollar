#!/usr/bin/env python3
"""
The AI Dollar - Video Generator
Finance education Shorts with per-slide audio sync + zoom + crossfade + deep male TTS
"""

import os
import re
import gc
import base64
import subprocess
import asyncio
import requests
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"[OK] FFmpeg ready: {FFMPEG}")
except Exception as e:
    FFMPEG = "ffmpeg"
    print(f"[WARN] Using system ffmpeg: {e}")


def _run_ffmpeg_hard_timeout(cmd, timeout):
    """Like subprocess.run(..., timeout=timeout) but immune to the classic
    Python gotcha where a timed-out process leaves orphaned children holding
    the output pipe open, making the post-kill communicate() hang forever
    anyway. Runs the process in its own session and kills the whole group.
    Returns the completed process, or None on timeout."""
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            import signal
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            proc.kill()
        try:
            proc.communicate(timeout=10)
        except Exception:
            pass
        return None
    proc.stderr = stderr
    return proc

CONFIG = {"output_dir": "./videos"}

# Strip surrounding quotes: a key pasted as "abc123" (the .env convention)
# is sent verbatim in the Authorization header and Pexels answers 401, which
# silently disabled every photo lookup in this file.
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "").strip().strip('"').strip("'")

from topic_generator import generate_short_topic, generate_long_topic



CONTENT_TOPICS = [
    {
        "title": "A Janitor Died With $8 Million (His Secret Was Stupid Simple)",
        "slides": [
            {"text": "A janitor named\nRonald Read died\nat age 92", "speech": "A janitor named Ronald Read died at age ninety two. Nobody knew he was rich. He wore flannel shirts. Drove an old Toyota. Ate at the same diner every day.", "img": "humble elderly man in simple clothes smiling"},
            {"text": "When they read\nhis will...\neveryone was\nSHOCKED", "speech": "When they read his will, EVERYONE was shocked. This quiet janitor from Vermont had EIGHT MILLION DOLLARS.", "img": "shocked lawyer reading a will document"},
            {"text": "EIGHT MILLION\nDOLLARS\nFrom a janitor's\nsalary", "speech": "Eight. Million. Dollars. On a JANITOR'S salary. No inheritance. No lottery. No side business. Just a paycheck and a strategy.", "img": "eight million dollars in gold numbers glowing"},
            {"text": "His secret?\nHe bought stocks\nand NEVER sold\nthem. Ever.", "speech": "His secret was embarrassingly simple. He bought blue chip stocks. And he NEVER sold them. Not in crashes. Not in recessions. NEVER.", "img": "stock portfolio growing over decades steadily"},
            {"text": "He held them\nfor 40+ YEARS\nthrough every crash\nevery recession", "speech": "He held those stocks for over FORTY YEARS. Through the dot com crash. Through two thousand eight. Through everything. He just held.", "img": "timeline showing decades of patient investing"},
            {"text": "While everyone\npanicked and sold\nhe did NOTHING\nThat was his\nsuperpower", "speech": "While everyone PANICKED and sold their stocks at a loss, Ronald did NOTHING. And that NOTHING was his superpower.", "img": "calm person while others panic around them"},
            {"text": "Compound interest\ndid the rest\n$300 per month\nfor 40 years\n= $8 MILLION", "speech": "Compound interest did the rest. Three hundred dollars per month. Invested consistently for forty years. At ten percent average returns. EIGHT MILLION DOLLARS.", "img": "compound growth curve shooting upward dramatically"},
            {"text": "You don't need\na huge salary\nYou need TIME\nand PATIENCE", "speech": "You don't need a six figure salary. You don't need to be smart. You need TIME and PATIENCE. That's literally it.", "img": "clock and patience symbols with wealth growing"},
            {"text": "The stock market\naverages 10% per\nyear for 100+\nyears straight", "speech": "The stock market has averaged ten percent per year for over one hundred years. It's the most reliable wealth machine in human history.", "img": "hundred year stock market chart going up"},
            {"text": "Start with $50\nper month TODAY\nYour future self\nwill THANK you", "speech": "Start with fifty dollars per month TODAY. Set it on autopilot. Forget about it. In forty years, your future self will be a MILLIONAIRE thanking you for this moment.", "img": "person starting small investment journey with hope"},
        ],
        "keywords": ["Compound Interest", "Long Term Investing", "Wealth"],
    },
    {
        "title": "I Asked A Millionaire His #1 Money Rule (It Changed Everything)",
        "slides": [
            {"text": "I asked a\nmillionaire his\n#1 money rule", "speech": "I asked a real millionaire what his NUMBER ONE money rule was. His answer changed the way I think about money forever.", "img": "businessman in suit giving advice at coffee meeting"},
            {"text": "He said:\nPay yourself FIRST\nnot last\nNEVER last", "speech": "He said four words. PAY YOURSELF FIRST. Not last. NEVER last. Most people pay rent, bills, food, fun, and save whatever is LEFT. That's backwards.", "img": "paycheck being split with savings first priority"},
            {"text": "Most people:\nBills → Food →\nFun → Save\nwhatever's left\n(usually $0)", "speech": "Most people pay bills, then food, then fun, then save whatever's left. Which is usually NOTHING. Zero. Every single month.", "img": "empty wallet at end of month"},
            {"text": "Rich people:\nSave 20% FIRST →\nThen bills →\nThen food →\nThen fun", "speech": "Rich people flip it. Save twenty percent FIRST. Then pay bills. Then food. Then fun with what's left. The ORDER changes everything.", "img": "money flowing to savings first then expenses"},
            {"text": "The trick?\nAUTOMATE IT\nSet up auto\ntransfer on payday\nYou'll never\nmiss it", "speech": "The trick is to AUTOMATE it. Set up an automatic transfer on payday. Twenty percent goes to your investment account before you even SEE it. You'll never miss money you never saw.", "img": "automatic bank transfer setup on phone"},
            {"text": "After 1 month\nyou forget\nit's even gone\nYour lifestyle\nadjusts", "speech": "After one month you FORGET it's even happening. Your lifestyle adjusts automatically. You spend less without even trying. It's painless.", "img": "person living normally without noticing savings"},
            {"text": "After 1 year\nyou have\n$4,000-$10,000\nsaved without\neven trying", "speech": "After one year you have four to ten thousand dollars SAVED. Without even trying. Without any sacrifice. Without any pain. Just from flipping the order.", "img": "surprised person checking growing savings account"},
            {"text": "After 10 years\nthat money\nBECOMES\n$100,000+\nwith investing", "speech": "After ten years, with compound interest, that money becomes over ONE HUNDRED THOUSAND DOLLARS. From just paying yourself first.", "img": "hundred thousand dollar milestone celebration"},
            {"text": "Every millionaire\nI've studied\ndoes THIS one\nthing first", "speech": "Every single millionaire I've studied does this ONE thing. They pay themselves first. Before anything. Before anyone. THEMSELVES FIRST.", "img": "multiple successful people all sharing same habit"},
            {"text": "Open a free\naccount TODAY\nSet up auto\ntransfer for $50\nJust START", "speech": "Open a free brokerage account TODAY. Set up an automatic transfer for fifty dollars every paycheck. Just START. The amount doesn't matter. The HABIT matters. Do it NOW.", "img": "phone showing account setup with start button"},
        ],
        "keywords": ["Pay Yourself First", "Millionaire Habits", "Saving"],
    },
    {
        "title": "Your Parents Lied About Money (5 Myths Exposed)",
        "slides": [
            {"text": "Your parents\ntold you things\nabout money that\nare completely\nWRONG", "speech": "Your parents told you things about money that are completely WRONG. Not because they're bad people. Because THEIR parents told them the same lies.", "img": "family at dinner table discussing money"},
            {"text": "Myth 1:\nGet a good job\nand you'll be\nset for life\nNOPE", "speech": "Myth one. Get a good job and you'll be set for life. WRONG. No job is guaranteed. Layoffs happen. Companies close. Your salary alone will NEVER make you wealthy.", "img": "person at desk job looking stressed and uncertain"},
            {"text": "Reality:\nYour job is ONE\nincome stream\nYou need 3-7\nstreams minimum", "speech": "Reality check. Your job is just ONE income stream. Millionaires have THREE to SEVEN income streams. Side hustles. Investments. Rental income. Dividends.", "img": "multiple income streams flowing into one person"},
            {"text": "Myth 2:\nSave money in\nthe bank\nit's SAFE there\nIt's actually\nLOSING value", "speech": "Myth two. Save your money in the bank, it's safe there. Your bank pays you zero point zero one percent interest. Inflation is three percent. Your money LOSES value every single day in a bank.", "img": "money in bank shrinking from inflation"},
            {"text": "Myth 3:\nDebt is always bad\nWRONG\nSmart debt builds\nwealth FAST", "speech": "Myth three. All debt is bad. WRONG. Smart debt builds wealth FAST. A mortgage on a rental property that pays you monthly? That's GOOD debt. It makes you richer.", "img": "good debt building wealth versus bad debt"},
            {"text": "Myth 4:\nYou need a lot\nof money to\nstart investing\nYou need $1", "speech": "Myth four. You need a lot of money to start investing. You need ONE DOLLAR. Seriously. Apps let you buy fractional shares. One dollar gets you started TODAY.", "img": "one dollar coin becoming first investment"},
            {"text": "Myth 5:\nRich people are\ngreedy and evil\nMost are just\nDISCIPLINED", "speech": "Myth five. Rich people are greedy. Most wealthy people are just DISCIPLINED. They spend less than they earn. They invest consistently. They're not special. They're just disciplined.", "img": "disciplined person following financial routine"},
            {"text": "The #1 thing\nschools SHOULD\nteach but DON'T:\nHow money\nACTUALLY works", "speech": "The number one thing schools SHOULD teach but DON'T is how money actually works. Taxes. Investing. Compound interest. Credit. They teach you algebra you'll never use but not how to BUILD WEALTH.", "img": "school with no financial education being taught"},
            {"text": "Break the cycle\nLearn what your\nparents couldn't\nteach you", "speech": "Break the cycle. Learn what your parents couldn't teach you. Not because they didn't love you. Because nobody taught THEM either.", "img": "person breaking chains of financial ignorance"},
            {"text": "Follow for REAL\nmoney education\nyour school never\ngave you", "speech": "Follow The AI Dollar for REAL money education your school never gave you. New lessons every single day. Subscribe now. Your financial future depends on it.", "img": "student learning real financial education online"},
        ],
        "keywords": ["Money Myths", "Financial Education", "Parents"],
    },
    {
        "title": "I Lived On $20K And Still Invested $10K (Here's How)",
        "slides": [
            {"text": "I made $20,000\nlast year and\nstill invested\nTEN THOUSAND\nof it", "speech": "I made twenty thousand dollars last year. And I still managed to invest TEN THOUSAND of it. People think I'm crazy. But here's exactly how I did it.", "img": "simple apartment with person managing tight budget"},
            {"text": "Step 1:\nI tracked every\nsingle dollar\nfor 30 days\nand found the\nLEAKS", "speech": "Step one. I tracked every single dollar for thirty days. And I found the LEAKS. Subscriptions I forgot about. Doordash three times a week. Random Amazon purchases.", "img": "expense tracker app showing spending leaks"},
            {"text": "I was wasting\n$400 per month\nwithout even\nknowing it\nFOUR HUNDRED", "speech": "I was wasting FOUR HUNDRED dollars per month without even knowing it. That's almost FIVE THOUSAND per year. Going absolutely NOWHERE.", "img": "four hundred dollars per month wasted on nothing"},
            {"text": "Step 2:\nI meal prepped\nevery Sunday\nFood bill dropped\nfrom $500 to $150", "speech": "Step two. I started meal prepping every Sunday. My food bill dropped from five hundred to one hundred fifty per month. Same food. Just cooked at home.", "img": "meal prep containers lined up for the week"},
            {"text": "Step 3:\nI cancelled\nEVERYTHING\nexcept one\nstreaming service", "speech": "Step three. I cancelled EVERYTHING. Netflix, Spotify, gym I never went to, app subscriptions. Kept ONE streaming service. Saved two hundred per month.", "img": "cancelling multiple subscription services"},
            {"text": "Step 4:\nI got a roommate\nRent went from\n$1100 to $550\nInstantly", "speech": "Step four. I got a roommate. Rent went from eleven hundred to five fifty. INSTANTLY saved five hundred fifty per month. Was it comfortable? No. Was it worth it? Absolutely.", "img": "shared apartment with roommate splitting costs"},
            {"text": "Total saved:\n$1,150 per month\n$13,800 per year\nOn a $20K salary", "speech": "Total saved. Eleven hundred fifty per month. Thirteen thousand eight hundred per year. On a TWENTY THOUSAND dollar salary. More than half my income.", "img": "savings calculator showing impressive results"},
            {"text": "I put $850\nper month into\nindex funds\nAutomatically", "speech": "I put eight hundred fifty per month straight into index funds. Automatically. On payday. Before I could touch it. The rest went to emergency savings.", "img": "automatic investment deposits into index funds"},
            {"text": "Was it fun?\nNo.\nWas it worth it?\nI have $30K\nnow in 2 years", "speech": "Was it fun? Honestly, no. Was it worth it? I now have THIRTY THOUSAND dollars invested after just two years. At twenty three years old. Most people my age have zero.", "img": "young person checking growing investment portfolio"},
            {"text": "If I can do it\non $20K\nYOU can do it\non whatever\nyou make\nSTART", "speech": "If I can do it on twenty thousand, YOU can do it on whatever you make. The amount doesn't matter. The DISCIPLINE does. Start today. Future you is counting on it.", "img": "motivated person starting their investment journey"},
        ],
        "keywords": ["Budgeting", "Low Income Investing", "Frugal Living"],
    },
    {
        "title": "She Made $0 To $5K/Month In 90 Days (Copy Her Strategy)",
        "slides": [
            {"text": "She went from\n$0 to $5K\nper month\nin just 90 days", "speech": "She went from ZERO income to FIVE THOUSAND dollars per month in just ninety days. No degree. No connections. No startup money. Here's her exact strategy.", "img": "young woman celebrating financial success on laptop"},
            {"text": "Day 1-7:\nShe picked ONE\nskill to learn\nSocial media\nmanagement", "speech": "Days one through seven. She picked ONE skill. Social media management. Not three skills. Not five. ONE. She went all in on that one thing.", "img": "person focused on learning one skill deeply"},
            {"text": "Day 8-30:\nShe learned it\nFREE on YouTube\n2 hours per day\nwhile working her\njob", "speech": "Days eight through thirty. She learned it FREE on YouTube. Two hours per day. Before work. After work. While eating lunch. She was OBSESSED with learning.", "img": "watching tutorial videos to learn new skill"},
            {"text": "Day 31-45:\nShe managed 3\nfriends' accounts\nfor FREE\nto build a\nportfolio", "speech": "Days thirty one through forty five. She managed THREE friends' social media accounts for FREE. Not for money. For PROOF. She needed results to show future clients.", "img": "managing social media accounts for friends"},
            {"text": "Day 46-60:\nShe cold messaged\n100 small businesses\nper week on\nInstagram", "speech": "Days forty six through sixty. She cold messaged ONE HUNDRED small businesses per week on Instagram. Not spam. Personalized messages showing how she could help THEM specifically.", "img": "sending personalized messages to businesses"},
            {"text": "3 said yes\n$500 per client\nper month\nThat's $1,500\nin month 2", "speech": "Three said yes. Five hundred per client per month. That's fifteen hundred dollars in month TWO. From cold messages. No fancy website. No degree. Just hustle.", "img": "first three clients signing up for services"},
            {"text": "Day 61-90:\nShe raised prices\nto $1,000\nAdded 2 more\nclients", "speech": "Days sixty one through ninety. She raised her prices to one thousand per client. Added two more clients through REFERRALS. Happy clients told their friends.", "img": "raising prices and getting referral clients"},
            {"text": "Month 3:\n5 clients\n× $1,000 each\n= $5,000/month", "speech": "Month three. Five clients at one thousand each. Five thousand dollars per month. RECURRING income. Every month. Like clockwork.", "img": "five thousand monthly income dashboard"},
            {"text": "She kept her\nday job too\n$5K side income\n+ salary\n= WEALTH", "speech": "She kept her day job too. Five thousand in side income PLUS her salary. She invested the entire side income. In two years she'll have over one hundred thousand invested.", "img": "dual income streams building wealth fast"},
            {"text": "Pick YOUR skill:\nWriting Design\nVideo editing\nPick ONE\nGo ALL IN\nfor 90 days", "speech": "Pick YOUR skill. Writing. Design. Video editing. Pick ONE. Go ALL IN for ninety days. The hardest part is starting. Everything else is just momentum. START TODAY.", "img": "skills to choose from with go button"},
        ],
        "keywords": ["Side Hustle", "Freelancing", "Make Money"],
    },
    {
        "title": "The $3 Coffee That Costs You $1.2 Million (Do The Math)",
        "slides": [
            {"text": "That $3 coffee\nyou buy every\nmorning?\nIt's costing you\n$1.2 MILLION", "speech": "That three dollar coffee you buy every single morning? It's not costing you three dollars. It's costing you ONE POINT TWO MILLION DOLLARS. Let me show you the math.", "img": "morning coffee cup with dollar signs floating away"},
            {"text": "$3 per day\n× 365 days\n= $1,095\nper year", "speech": "Three dollars per day. Times three hundred sixty five days. That's one thousand ninety five dollars per year. On COFFEE.", "img": "calculator showing yearly coffee spending"},
            {"text": "That $1,095\ninvested at 10%\nfor 40 years\n= $604,817", "speech": "Now take that same one thousand ninety five dollars. Invest it in the stock market at ten percent average returns. Over forty years? SIX HUNDRED FOUR THOUSAND DOLLARS.", "img": "investment growth chart from coffee money"},
            {"text": "But WAIT\nmost people spend\n$5-7 on coffee\nnot $3", "speech": "But WAIT. Most people don't spend three dollars. They spend FIVE to SEVEN dollars at Starbucks. A venti latte with oat milk? That's SEVEN BUCKS.", "img": "starbucks receipt showing expensive coffee order"},
            {"text": "$7 per day\n= $2,555/year\nInvested for\n40 years\n= $1.2 MILLION", "speech": "Seven dollars per day is twenty five hundred per year. Invested for forty years at ten percent? ONE POINT TWO MILLION DOLLARS. From COFFEE.", "img": "one point two million dollars from coffee spending"},
            {"text": "I'm NOT saying\nnever buy coffee\nI'm saying KNOW\nwhat it costs", "speech": "I'm NOT saying never buy coffee. I love coffee. I'm saying KNOW what it actually costs you in opportunity. Make it at home for thirty cents. Buy it out SOMETIMES.", "img": "home coffee setup saving money daily"},
            {"text": "Make coffee at\nhome for $0.30\nSave $6.70 per day\nThat's $200/month", "speech": "Make coffee at home for thirty cents. Save six dollars seventy cents per day. That's TWO HUNDRED dollars per month you can INVEST instead.", "img": "home brewed coffee next to savings jar"},
            {"text": "This applies to\nEVERYTHING:\nLunch out\nSubscriptions\nImpulse buys", "speech": "This applies to EVERYTHING. Lunch out every day? Same math. Subscriptions you forgot about? Same math. Every small daily expense is a FORTUNE over time.", "img": "daily expenses adding up over lifetime"},
            {"text": "Small daily\nexpenses are the\n#1 reason\npeople stay broke", "speech": "Small daily expenses are the NUMBER ONE reason people stay broke. Not big purchases. Not emergencies. The three, five, seven dollar daily habits that add up to MILLIONS lost.", "img": "small expenses draining wealth slowly"},
            {"text": "Check your bank\nstatement RIGHT NOW\nFind your $3\ncoffee equivalent\nCut it. Invest it.", "speech": "Check your bank statement RIGHT NOW. Find YOUR three dollar coffee equivalent. Cut it. Invest the difference. In forty years you'll have over a MILLION DOLLARS. Or you'll have a lot of empty coffee cups.", "img": "person checking bank app finding wasted spending"},
        ],
        "keywords": ["Latte Factor", "Daily Spending", "Investing"],
    },
    {
        "title": "Warren Buffett's 3 Rules (Why 99% Ignore Them)",
        "slides": [
            {"text": "Warren Buffett is\nworth $120 BILLION\nHis 3 rules are\nembarrassingly\nsimple", "speech": "Warren Buffett is worth one hundred twenty BILLION dollars. He's the greatest investor alive. And his three rules are so simple that ninety nine percent of people ignore them.", "img": "Warren Buffett portrait looking wise and confident"},
            {"text": "Rule 1:\nNever lose money\nRule 2:\nNever forget\nRule 1", "speech": "Rule one. Never lose money. Rule two. Never forget rule one. Sounds obvious right? But most people GAMBLE with their money instead of PROTECTING it.", "img": "golden rules carved in stone monument"},
            {"text": "This means:\nDon't chase hype\nDon't gamble\nDon't YOLO\nProtect what\nyou have", "speech": "This means don't chase hype. Don't gamble on meme stocks. Don't YOLO your savings into crypto. PROTECT what you have first. Then grow it SAFELY.", "img": "shield protecting investments from risky choices"},
            {"text": "Rule 3:\nBe fearful when\nothers are greedy\nBe greedy when\nothers are fearful", "speech": "Rule three. Be fearful when others are greedy. Be greedy when others are fearful. When everyone is buying? Be careful. When everyone is PANICKING? That's when you BUY.", "img": "crowd panicking while smart investor buys stocks"},
            {"text": "In 2008 when\neveryone PANICKED\nBuffett invested\n$5 BILLION\ninto Goldman Sachs", "speech": "In two thousand eight when the whole world PANICKED and sold everything, Buffett invested FIVE BILLION into Goldman Sachs. Everyone called him crazy. He made THREE BILLION profit.", "img": "2008 crash with Buffett buying when others sold"},
            {"text": "In 2020 COVID\nmarket crashed 34%\nPeople who bought\nthe dip DOUBLED\ntheir money", "speech": "In twenty twenty COVID crashed the market thirty four percent. People who bought during that panic DOUBLED their money in just two years. The ones who sold? Still recovering.", "img": "COVID crash recovery showing doubled gains"},
            {"text": "His actual\nstrategy is boring:\nBuy good companies\nHold FOREVER\nThat's it", "speech": "His actual strategy is BORING. Buy good companies at fair prices. Hold them FOREVER. Collect dividends. Reinvest. That's literally it. No day trading. No crypto. No complexity.", "img": "simple boring investment strategy that works"},
            {"text": "He's owned\nCoca-Cola since 1988\n36 YEARS\nHe never sold\na single share", "speech": "He's owned Coca-Cola stock since nineteen eighty eight. THIRTY SIX YEARS. He's never sold a single share. It pays him seven hundred million per year in dividends alone.", "img": "Coca-Cola stock held for decades paying dividends"},
            {"text": "The lesson:\nStop overcomplicating\nmoney\nBuy index funds\nHold forever\nGet rich slowly", "speech": "The lesson? Stop overcomplicating money. Buy index funds. Hold forever. Get rich SLOWLY. It's boring. It's unsexy. But it WORKS. Every single time.", "img": "simple path to wealth through patience"},
            {"text": "Buffett says:\nBuy the S&P 500\nand go live\nyour life\nFollow his advice", "speech": "Buffett himself says most people should just buy an S and P five hundred index fund and go live their life. That's the advice of the greatest investor in history. FOLLOW IT.", "img": "S&P 500 index fund as Buffett's recommendation"},
        ],
        "keywords": ["Warren Buffett", "Investing Rules", "Value Investing"],
    },
    {
        "title": "The 72 Hour Rule That Saved Me $15,000 This Year",
        "slides": [
            {"text": "One simple rule\nsaved me $15,000\nthis year\nIt takes 3\nseconds to learn", "speech": "One stupid simple rule saved me FIFTEEN THOUSAND DOLLARS this year. It takes three seconds to learn and it works IMMEDIATELY.", "img": "person celebrating money saved with excitement"},
            {"text": "The 72 HOUR rule:\nWant something?\nWait 72 hours\nbefore buying it", "speech": "The seventy two hour rule. Want something? WAIT seventy two hours before buying it. If you still want it after three days, buy it. If you forgot about it? You never needed it.", "img": "clock showing 72 hours countdown before purchase"},
            {"text": "90% of impulse\npurchases you\nWON'T WANT\nafter 3 days\nGuaranteed", "speech": "NINETY PERCENT of impulse purchases you won't even REMEMBER after three days. That's not my opinion. That's psychology research. Your brain tricks you into wanting things you don't need.", "img": "brain being tricked by impulse purchase urges"},
            {"text": "That $200 jacket\nyou HAD to have?\nForgotten in\n72 hours", "speech": "That two hundred dollar jacket you HAD to have? Forgotten in seventy two hours. Those wireless earbuds on sale? Don't care anymore. That kitchen gadget? Never think about it again.", "img": "forgotten impulse purchases gathering dust"},
            {"text": "Amazon makes it\nWORSE with\none-click buy\nThey WANT you\nto buy impulsively", "speech": "Amazon makes it WORSE with one-click buying. They WANT you to buy impulsively. Remove your credit card from Amazon. Add items to your cart. Wait three days. Then decide.", "img": "amazon one click buy designed for impulse purchases"},
            {"text": "I used to spend\n$500-1000 per month\non random stuff\nI didn't need", "speech": "I used to spend five hundred to one thousand per month on random stuff I didn't need. Gadgets. Clothes. Things that gave me a dopamine hit for five minutes then sat in a drawer.", "img": "closet full of unused impulse purchases"},
            {"text": "After the 72\nhour rule:\nI spend $100-200\nThat's $800 saved\nper month", "speech": "After applying the seventy two hour rule? I spend one to two hundred on wants. That's EIGHT HUNDRED saved per month. Almost ten thousand per year. INVESTED.", "img": "dramatic spending reduction chart before and after"},
            {"text": "That $800/month\ninvested = $45K\nin 3 years\n$500K in 20 years", "speech": "That eight hundred per month invested becomes forty five thousand in three years. Five hundred thousand in twenty years. Half a MILLION dollars from just WAITING three days before buying stuff.", "img": "investment growth from saved impulse spending"},
            {"text": "The dopamine hit\nfrom buying fades\nin 5 minutes\nThe money is\ngone FOREVER", "speech": "The dopamine hit from buying something fades in five minutes. But the money is gone FOREVER. That five minute high costs you thousands.", "img": "dopamine spike fading quickly after purchase"},
            {"text": "Try it for\n30 days\nAdd to cart\nWait 72 hours\nWatch your savings\nEXPLODE", "speech": "Try it for thirty days. Add things to cart. Wait seventy two hours. Watch how much money you KEEP. Your savings will EXPLODE. This is the simplest wealth hack that exists.", "img": "thirty day challenge to save money starting now"},
        ],
        "keywords": ["Impulse Buying", "Saving Money", "72 Hour Rule"],
    },
    {
        "title": "Rich Dad vs Poor Dad (The Lesson That Changed My Life)",
        "slides": [
            {"text": "Rich dad said:\nThe poor work\nfor money\nThe rich make\nmoney work\nfor THEM", "speech": "Rich dad said something that changed my life forever. The poor work for money. The rich make money work for THEM. Same twenty four hours. Completely different results.", "img": "two paths diverging one to wealth one to poverty"},
            {"text": "Poor mindset:\nGet paycheck →\nPay bills →\nSpend rest →\nRepeat until 65", "speech": "Poor mindset. Get paycheck. Pay bills. Spend the rest. Repeat until you're sixty five. Then pray Social Security is enough. This is the TRAP most people live in.", "img": "hamster wheel of paycheck to paycheck living"},
            {"text": "Rich mindset:\nGet paycheck →\nInvest first →\nLet investments\npay your bills", "speech": "Rich mindset. Get paycheck. Invest FIRST. Build assets. Let your INVESTMENTS pay your bills. Eventually your money makes more than your job does.", "img": "money machine generating passive income"},
            {"text": "An ASSET puts\nmoney IN your\npocket every month\nRental property\nDividend stocks", "speech": "An ASSET puts money IN your pocket every month. Rental property. Dividend stocks. A business that runs without you. These are ASSETS.", "img": "assets generating monthly income automatically"},
            {"text": "A LIABILITY takes\nmoney OUT of\nyour pocket\nCar payments\nCredit card debt", "speech": "A LIABILITY takes money OUT of your pocket. Car payments. Credit card debt. That fancy watch. Anything that COSTS you money monthly is a liability.", "img": "liabilities draining money from wallet"},
            {"text": "Your house?\nIt's a LIABILITY\nuntil it makes\nyou money\n(controversial\nbut TRUE)", "speech": "Your house? Controversial truth. It's a LIABILITY until it makes you money. Mortgage, taxes, repairs, insurance. It COSTS you money every month unless you rent part of it out.", "img": "house with expenses flowing out monthly"},
            {"text": "The goal:\nBuy enough ASSETS\nthat they cover\nall your bills\nThat's FREEDOM", "speech": "The goal is simple. Buy enough ASSETS that the income they generate covers ALL your bills. When your assets pay your expenses? That's FINANCIAL FREEDOM. You never have to work again.", "img": "assets income exceeding monthly expenses"},
            {"text": "Start small:\n$50 into dividend\nETF this month\nThat's your\nfirst asset", "speech": "Start small. Put fifty dollars into a dividend ETF this month. That's your first ASSET. It will pay you dividends. Reinvest those dividends. Watch it compound.", "img": "first fifty dollar investment into dividend fund"},
            {"text": "In 5 years:\nYour assets pay\n$200 per month\nIn 15 years:\n$2,000 per month\nIn 30: $10,000", "speech": "In five years your assets pay two hundred per month. In fifteen years, two thousand. In thirty years, TEN THOUSAND per month. All passive. All automatic.", "img": "passive income growing decade by decade"},
            {"text": "Stop buying\nliabilities\nStart buying\nassets TODAY\nYour future self\nis watching", "speech": "Stop buying liabilities. Start buying assets TODAY. Your future self is either going to THANK you or BLAME you for what you do right now. Make the right choice.", "img": "choosing assets over liabilities for future wealth"},
        ],
        "keywords": ["Rich Dad Poor Dad", "Assets", "Financial Freedom"],
    },
    {
        "title": "Banks Pray You Never Learn This (High Yield Savings)",
        "slides": [
            {"text": "Your bank is\npaying you\n0.01% interest\nwhile making\n5% on YOUR money", "speech": "Your bank is paying you zero point zero one percent interest on YOUR money. Meanwhile they're lending it out at FIVE percent and keeping the difference. They're getting RICH off your savings.", "img": "bank building profiting from customer deposits"},
            {"text": "On $10,000 saved\nyour bank pays\nyou $1 per YEAR\nONE DOLLAR", "speech": "On ten thousand dollars saved, your bank pays you ONE DOLLAR per year. ONE. DOLLAR. That's not a typo. That's the biggest scam in banking.", "img": "one dollar annual interest on ten thousand savings"},
            {"text": "But a HIGH YIELD\nsavings account\npays you\n4.5 - 5%\nOn the SAME money", "speech": "But a HIGH YIELD savings account pays you FOUR POINT FIVE to FIVE percent. On the SAME money. Same safety. Same insurance. FDIC protected. Just a different bank.", "img": "high yield savings rate comparison glowing green"},
            {"text": "Same $10,000\nat 4.5% = $450\nper year\nVS $1 at your\nbank\nThat's 450x MORE", "speech": "Same ten thousand dollars at four point five percent earns you FOUR HUNDRED FIFTY per year. That's four hundred fifty times more than your regular bank. For doing NOTHING differently.", "img": "dramatic comparison 450 vs 1 dollar interest"},
            {"text": "It takes\n5 MINUTES\nto open one\nonline\nCompletely free", "speech": "It takes FIVE MINUTES to open one online. Completely free. No fees. No minimum balance. Transfer your money over. Start earning REAL interest tomorrow.", "img": "opening high yield account on phone in minutes"},
            {"text": "Best ones:\nMarcus by Goldman\nAlly Bank\nWealthfront\nAll pay 4%+", "speech": "Best ones right now. Marcus by Goldman Sachs. Ally Bank. Wealthfront. All paying four percent or higher. All FDIC insured. All completely free.", "img": "top high yield savings account options listed"},
            {"text": "Your money is\njust as SAFE\nFDIC insured\nup to $250,000\nSame as your\nbank", "speech": "Your money is just as SAFE. FDIC insured up to two hundred fifty thousand dollars. Exact same protection as your current bank. Zero additional risk.", "img": "FDIC insurance protection on high yield account"},
            {"text": "Why don't banks\ntell you this?\nBecause they PROFIT\nfrom your\nignorance", "speech": "Why doesn't your bank tell you about this? Because they PROFIT from your ignorance. Every dollar you leave in their zero interest account is a dollar THEY make money on.", "img": "bank profiting from customer ignorance"},
            {"text": "$50K at 0.01%\n= $5/year\n$50K at 4.5%\n= $2,250/year\nYou're leaving\n$2,245 on table", "speech": "Fifty thousand at zero point zero one percent earns five dollars. At four point five percent? Two thousand two hundred fifty. You're leaving over TWO THOUSAND on the table. Every single year.", "img": "money left on table from low interest accounts"},
            {"text": "Move your savings\nTODAY\nIt takes 5 min\nand earns you\nTHOUSANDS more\nper year", "speech": "Move your emergency fund and savings TODAY. Five minutes of work earns you THOUSANDS more per year. This is literally free money. Stop giving it to your bank.", "img": "transferring savings to high yield account now"},
        ],
        "keywords": ["High Yield Savings", "Banking", "Interest Rates"],
    },
    {
        "title": "He Retired At 35 With $1.2M (His Boring Strategy)",
        "slides": [
            {"text": "He retired at 35\nwith $1.2 million\nHis strategy was\nso BORING\npeople laughed", "speech": "He retired at thirty five with one point two million dollars. His strategy was so BORING that people literally laughed at him. But he got the last laugh.", "img": "young retiree enjoying life while others work"},
            {"text": "Age 22:\nGot a normal job\n$45K per year\nNothing special\nNo trust fund", "speech": "At twenty two he got a normal job making forty five thousand per year. Nothing special. No trust fund. No rich parents. No tech startup. Just a regular job.", "img": "young professional starting regular office job"},
            {"text": "He saved 50%\nof EVERYTHING\nLived on $22K\nInvested $22K", "speech": "He saved FIFTY PERCENT of everything he earned. Lived on twenty two thousand. Invested twenty two thousand. While his friends bought cars and clothes, he bought index funds.", "img": "splitting income fifty fifty savings and spending"},
            {"text": "His friends called\nhim cheap\nHe drove a\n2005 Honda Civic\nNo shame", "speech": "His friends called him cheap. He drove a two thousand five Honda Civic. Ate rice and beans. Had one pair of nice shoes. He didn't care what anyone thought.", "img": "old reliable honda civic as frugal transportation"},
            {"text": "Every single month\nfor 13 YEARS\n$1,800 into\nindex funds\nNever missed once", "speech": "Every single month for THIRTEEN YEARS he put eighteen hundred dollars into index funds. Never missed a month. Not once. Rain or shine. Bull market or crash.", "img": "thirteen years of consistent monthly investing"},
            {"text": "He didn't pick\nstocks or trade\ncrypto\nJust VOO and VTI\nSet and forget", "speech": "He didn't pick stocks. Didn't trade crypto. Didn't watch CNBC. Just VOO and VTI. Set it on autopilot. Forgot about it. Let compound interest do the work.", "img": "simple two fund portfolio on autopilot"},
            {"text": "At age 35:\n$1.2 MILLION\nin his portfolio\nHe quit his job\nForever", "speech": "At age thirty five. One point two MILLION dollars in his portfolio. He walked into his boss's office. And quit. Forever. He never has to work another day in his life.", "img": "person handing in resignation letter with smile"},
            {"text": "He now lives on\n4% per year\n= $48K annually\nFrom his portfolio\nFOREVER", "speech": "He now lives on four percent of his portfolio per year. Forty eight thousand annually. His money generates this FOREVER while the principal keeps growing.", "img": "living off investment returns forever"},
            {"text": "His friends who\nlaughed at him?\nStill working\nStill in debt\nStill broke", "speech": "His friends who laughed at him for being cheap? Still working. Still in debt. Still making car payments. They'll work until sixty five. He's FREE at thirty five.", "img": "comparison of early retiree vs still working friends"},
            {"text": "It wasn't talent\nIt wasn't luck\nIt was DISCIPLINE\nfor 13 years\nYou can do this", "speech": "It wasn't talent. It wasn't luck. It was DISCIPLINE for thirteen years. That's it. You can do this too. Start today. Your freedom countdown begins NOW.", "img": "motivated person beginning their FIRE journey"},
        ],
        "keywords": ["FIRE", "Early Retirement", "Index Funds"],
    },
    {
        "title": "Delete These 3 Apps To Save $500/Month (Seriously)",
        "slides": [
            {"text": "3 apps on your\nphone are STEALING\n$500 per month\nfrom you", "speech": "Three apps on your phone right now are STEALING five hundred dollars per month from you. And you don't even realize it. Check your bank statement. I dare you.", "img": "phone with money being drained from apps"},
            {"text": "App 1:\nDoorDash UberEats\nGrubhub\nAverage user spends\n$200+ per month", "speech": "App one. Food delivery. DoorDash, UberEats, Grubhub. The average user spends over TWO HUNDRED dollars per month. A fifteen dollar meal becomes twenty five after fees and tips.", "img": "food delivery app showing inflated prices"},
            {"text": "A $12 meal\nbecomes $25 after:\nDelivery fee $4\nService fee $3\nTip $5\nMarkup $1", "speech": "A twelve dollar meal becomes TWENTY FIVE dollars. Delivery fee four bucks. Service fee three. Tip five. Menu markup. You're paying DOUBLE for the same food.", "img": "receipt breakdown showing hidden delivery fees"},
            {"text": "App 2:\nAmazon\nAverage Prime\nmember spends\n$1,400 per year\non impulse buys", "speech": "App two. Amazon. The average Prime member spends fourteen hundred dollars per year on IMPULSE buys. Things they didn't need. Things they used once. Things still in the box.", "img": "amazon boxes piling up from impulse shopping"},
            {"text": "Remove your credit\ncard from Amazon\nThe extra steps\nstop 80% of\nimpulse buys", "speech": "Remove your credit card from Amazon. The extra step of entering it manually stops EIGHTY PERCENT of impulse purchases. Friction is your friend.", "img": "removing saved payment method from shopping app"},
            {"text": "App 3:\nAny shopping app\nSHEIN Temu Zara\nFast fashion is\na MONEY BONFIRE", "speech": "App three. Shopping apps. SHEIN, Temu, Zara. Fast fashion is a money BONFIRE. You buy clothes you wear twice then throw away. Repeat monthly.", "img": "fast fashion purchases worn once then discarded"},
            {"text": "These 3 apps\ncombined drain\n$300-500 per month\nfrom average users", "speech": "These three apps combined drain THREE to FIVE HUNDRED dollars per month from the average user. That's four to six thousand per year. Going to companies that don't care about you.", "img": "three apps draining thousands per year from users"},
            {"text": "Delete them\nfor 30 days\nI PROMISE you\nwon't die\nYou'll feel FREE", "speech": "Delete them for thirty days. I PROMISE you won't die. You'll cook more. You'll buy less junk. And you'll feel FREE knowing you're keeping your money instead of giving it away.", "img": "person deleting apps and feeling liberated"},
            {"text": "$500 saved\nper month\n= $6,000/year\nInvested for\n30 years\n= $1.1 MILLION", "speech": "Five hundred saved per month is six thousand per year. Invested for thirty years at ten percent? ONE POINT ONE MILLION DOLLARS. From deleting three apps.", "img": "million dollars from deleting wasteful apps"},
            {"text": "Your phone is\neither making\nyou RICH or\nkeeping you POOR\nChoose wisely", "speech": "Your phone is either making you RICH or keeping you POOR. Replace those three apps with a brokerage app. Start investing what you were wasting. Choose wisely.", "img": "phone choice between wealth apps and wasteful apps"},
        ],
        "keywords": ["Saving Money", "Apps", "Spending Habits"],
    },
    {
        "title": "The $100 Challenge That Builds Your First $10K",
        "slides": [
            {"text": "The $100 challenge\nthat builds your\nfirst $10,000\nAnyone can do it", "speech": "The hundred dollar challenge that builds your first TEN THOUSAND dollars. Anyone can do it. Any income level. Any age. No excuses.", "img": "hundred dollar bill transforming into ten thousand"},
            {"text": "Week 1:\nSave $100\nPut it in a\nhigh yield savings\naccount\nDONE", "speech": "Week one. Save one hundred dollars. Skip eating out twice. Cancel one subscription. Sell something you don't use. Put it in a high yield savings account. DONE.", "img": "first hundred dollars going into savings"},
            {"text": "Every month after:\nAdd $100 more\nAutomatically\nOn payday\nNon-negotiable", "speech": "Every month after, add one hundred more. Set up automatic transfer on payday. Non-negotiable. It happens whether you feel like it or not.", "img": "automatic monthly hundred dollar transfers"},
            {"text": "Month 3: $300\nMonth 6: $600\nMonth 12: $1,200\nYou're building\nMOMENTUM", "speech": "Month three, three hundred. Month six, six hundred. Month twelve, twelve hundred. You're building MOMENTUM. The habit is becoming automatic.", "img": "savings growing month by month steadily"},
            {"text": "At month 6:\nMove savings into\na brokerage\naccount\nBuy VOO\n(S&P 500 ETF)", "speech": "At month six, move your savings into a brokerage account. Buy VOO, the S and P five hundred ETF. Now your money isn't just sitting there. It's GROWING.", "img": "moving savings into investment account"},
            {"text": "Your $100/month\nat 10% returns\n= $10,000\nin just 6 years", "speech": "One hundred per month at ten percent average returns equals TEN THOUSAND dollars in just six years. Your first ten thousand. The hardest ten thousand. After that it snowballs.", "img": "six year journey to ten thousand dollars"},
            {"text": "After $10K\nsomething magical\nhappens\nYour money starts\nmaking money\nfor YOU", "speech": "After ten thousand something MAGICAL happens. Your investments generate real returns. Hundreds per year. Then thousands. Your money starts making money FOR you.", "img": "money generating its own returns automatically"},
            {"text": "Can you do more?\n$200/month\n= $10K in 3 years\n$500/month\n= $10K in 18 months", "speech": "Can you do more? Two hundred monthly hits ten thousand in three years. Five hundred monthly? Just eighteen months. The more you invest, the faster you win.", "img": "faster paths to ten thousand at higher amounts"},
            {"text": "The first $10K\nis the HARDEST\nThe next $10K\ncomes in HALF\nthe time", "speech": "The first ten thousand is the HARDEST. After that, the next ten thousand comes in HALF the time. Because compound interest is working FOR you now. It gets easier.", "img": "accelerating wealth after first milestone"},
            {"text": "Start YOUR\n$100 challenge\nTODAY\nSet up auto\ntransfer right now\nGO", "speech": "Start YOUR hundred dollar challenge TODAY. Right now. Open your banking app. Set up a hundred dollar automatic transfer. Do it before you close this video. GO.", "img": "person setting up automatic investment transfer"},
        ],
        "keywords": ["$100 Challenge", "Saving", "First 10K"],
    },
    {
        "title": "Why Your Salary Is A Trap (The Truth Nobody Tells You)",
        "slides": [
            {"text": "Your salary\nis a TRAP\ndesigned to keep\nyou working\nuntil you're 65", "speech": "Your salary is a TRAP. It's designed to give you JUST ENOUGH to survive but NEVER ENOUGH to escape. You're comfortable enough to stay but too broke to leave.", "img": "golden handcuffs on office worker at desk"},
            {"text": "You get a raise\nYou upgrade your\nlifestyle\nYou're back to\nbroke again\nEVERY TIME", "speech": "You get a raise. You upgrade your car. Better apartment. Nicer clothes. And suddenly you're back to broke again. This is called LIFESTYLE INFLATION and it's a TRAP.", "img": "salary going up but lifestyle eating all gains"},
            {"text": "Earning $30K?\nBroke\nEarning $50K?\nStill broke\nEarning $100K?\nSOMEHOW still broke", "speech": "Earning thirty thousand? Broke. Get a raise to fifty thousand? Still broke. Hit one hundred thousand? SOMEHOW still broke. The number doesn't matter if your SPENDING grows with it.", "img": "income growing but savings staying at zero"},
            {"text": "The escape plan:\nKeep your lifestyle\nthe SAME when\nyou get a raise\nInvest the\ndifference", "speech": "The escape plan. When you get a raise, keep your lifestyle EXACTLY the same. Invest the ENTIRE difference. Your future self just got a raise too.", "img": "investing salary increases instead of spending"},
            {"text": "Got a $5K raise?\nDon't upgrade\nanything\nInvest $416/month\nextra\nSilently build wealth", "speech": "Got a five thousand dollar raise? Don't upgrade ANYTHING. That's four hundred sixteen dollars per month invested. In ten years that single raise becomes over EIGHTY THOUSAND invested.", "img": "five thousand raise going straight to investments"},
            {"text": "Your REAL salary\nis what you KEEP\nnot what you EARN\nRemember that", "speech": "Your REAL salary is what you KEEP. Not what you earn. Someone earning fifty thousand who saves fifteen is wealthier than someone earning one hundred thousand who saves zero.", "img": "keeping versus earning as real salary metric"},
            {"text": "The golden\nhandcuffs:\nNice salary\nNice car\nNice apartment\nBut ZERO freedom", "speech": "The golden handcuffs. Nice salary. Nice car. Nice apartment. But ZERO freedom. Zero savings. Zero investments. Miss one paycheck and everything collapses.", "img": "comfortable life with no financial security"},
            {"text": "Freedom means:\nYour investments\npay your bills\nYou work because\nyou WANT to\nnot because\nyou HAVE to", "speech": "Freedom means your investments pay your bills. You work because you WANT to, not because you HAVE to. That's the difference between a job and a choice.", "img": "financially free person choosing to work or not"},
            {"text": "The math:\nSave 25% of income\nfor 20 years\n= you NEVER\nhave to work\nagain", "speech": "The math. Save twenty five percent of your income for twenty years. That's it. You'll never HAVE to work again. The math works on ANY salary.", "img": "twenty year path to financial independence"},
            {"text": "Next paycheck:\nDon't spend the\nraise\nInvest it\nBreak the trap\nBe FREE", "speech": "Your next paycheck, don't spend the raise. Invest it. Break the salary trap. The difference between retiring at forty five and retiring at sixty five is what you do RIGHT NOW.", "img": "person breaking free from salary trap"},
        ],
        "keywords": ["Salary Trap", "Lifestyle Inflation", "Financial Freedom"],
    },
    {
        "title": "I Tracked Every Dollar For 30 Days (The Results Shocked Me)",
        "slides": [
            {"text": "I tracked EVERY\nsingle dollar I\nspent for 30 days\nThe results\nSHOCKED me", "speech": "I tracked EVERY single dollar I spent for thirty days. Every coffee. Every subscription. Every impulse buy. The results absolutely SHOCKED me.", "img": "expense tracking notebook with detailed entries"},
            {"text": "I thought I\nspent $2,000\nper month\nThe real number?\n$3,400\nWHERE did\n$1,400 go?", "speech": "I THOUGHT I spent two thousand per month. The real number? Thirty four hundred. WHERE did fourteen hundred extra dollars go? I had no idea.", "img": "shocked reaction to actual spending amount"},
            {"text": "Hidden expense 1:\nSubscriptions\n$89 per month\nI was paying for\n7 things I\nnever used", "speech": "Hidden expense one. Subscriptions. EIGHTY NINE dollars per month for SEVEN things I never used. Two streaming services. A gym. Three apps. A magazine.", "img": "list of forgotten subscription charges"},
            {"text": "Hidden expense 2:\nConvenience fees\n$220 per month\nDoorDash ATM fees\nconvenience stores", "speech": "Hidden expense two. Convenience fees. TWO HUNDRED TWENTY per month. Doordash markups. ATM fees. Buying from convenience stores instead of grocery stores. Lazy tax.", "img": "convenience spending adding up dramatically"},
            {"text": "Hidden expense 3:\nSocial spending\n$380 per month\nDrinks dinners\n'hanging out'\ncosts a FORTUNE", "speech": "Hidden expense three. Social spending. THREE HUNDRED EIGHTY dollars per month. Drinks. Dinners. Hanging out costs a FORTUNE when you're not paying attention.", "img": "social outing receipts piling up"},
            {"text": "Hidden expense 4:\nRandom Amazon\n$310 per month\nI didn't even\nremember ordering\nhalf of it", "speech": "Hidden expense four. Random Amazon purchases. Three hundred ten per month. I didn't even REMEMBER ordering half of it. Stuff sitting in boxes unopened. WASTED.", "img": "unopened amazon packages piling up"},
            {"text": "Total waste:\n$1,000 per month\non things that\nadded ZERO value\nto my life", "speech": "Total waste. Over ONE THOUSAND per month on things that added ZERO value to my life. Zero happiness. Zero utility. Just gone.", "img": "thousand dollars wasted monthly on nothing"},
            {"text": "After tracking:\nI cut $700/month\nwithout suffering\nat all\nI didn't even\nnotice", "speech": "After tracking, I cut seven hundred per month. Without suffering at ALL. I didn't miss any of it. I literally didn't notice the difference in my daily life.", "img": "seven hundred monthly savings with no lifestyle change"},
            {"text": "$700 per month\ninvested\n= $127,000\nin 10 years\nFrom just KNOWING\nwhere money goes", "speech": "Seven hundred per month invested equals one hundred twenty seven thousand in ten years. From just KNOWING where your money goes. That's it. Just awareness.", "img": "awareness turning into massive investment gains"},
            {"text": "Download ANY\nfree expense app\nTrack for 30 days\nYou WILL find\n$500+ in waste\nGuaranteed", "speech": "Download ANY free expense tracking app. Track for thirty days. I GUARANTEE you will find five hundred or more in waste. Money you can invest instead. Start tracking TODAY.", "img": "free expense tracker app ready to download"},
        ],
        "keywords": ["Expense Tracking", "Budgeting", "Money Awareness"],
    },
    {
        "title": "The Savings Account Scam (Banks Hate This Video)",
        "slides": [
            {"text": "Your savings\naccount is the\nbiggest SCAM\nin banking\nHere's proof", "speech": "Your savings account is the biggest SCAM in banking. And banks are PRAYING you never figure this out. Here's the proof.", "img": "bank vault with scam warning sign"},
            {"text": "Bank pays you:\n0.01% interest\nInflation takes:\n3-4% per year\nYou LOSE 3%\nevery year", "speech": "Your bank pays you zero point zero one percent. Inflation runs at three to four percent. You're LOSING three percent of your purchasing power every single year. Your savings are SHRINKING.", "img": "savings account value shrinking from inflation"},
            {"text": "$20,000 in savings\nloses $600 in\npurchasing power\nEVERY YEAR\nThat's $50/month\nGONE", "speech": "Twenty thousand in a regular savings account loses SIX HUNDRED dollars in purchasing power every year. That's fifty bucks a month just EVAPORATING.", "img": "twenty thousand losing six hundred per year"},
            {"text": "In 10 years\nyour $20K buys\nwhat $14K buys\ntoday\nYou got ROBBED", "speech": "In ten years, your twenty thousand only buys what fourteen thousand buys today. You got ROBBED of six thousand dollars. Without moving a finger.", "img": "purchasing power declining over ten years"},
            {"text": "Meanwhile YOUR bank\nlends YOUR money\nat 7% for mortgages\nKeeps the profit", "speech": "Meanwhile, YOUR bank takes YOUR money and lends it out at SEVEN PERCENT for mortgages. They keep the entire profit. They get rich. You get one dollar per year.", "img": "bank lending customer deposits at huge profit"},
            {"text": "The FIX is\nridiculous easy:\nMove money to\nHigh Yield Savings\n4.5% right now", "speech": "The fix is ridiculously easy. Move your money to a high yield savings account. Paying four point five percent RIGHT NOW. Same safety. Same FDIC insurance. Four hundred times more interest.", "img": "switching to high yield savings instantly"},
            {"text": "For investing:\nPut long term\nmoney into\nindex funds\n10% average returns", "speech": "For money you don't need for five plus years, put it into index funds. Ten percent average returns. Your money GROWS instead of shrinks.", "img": "index fund returns beating inflation easily"},
            {"text": "Keep 3-6 months\nexpenses in\nhigh yield savings\nInvest EVERYTHING\nelse", "speech": "Keep three to six months of expenses in high yield savings as your emergency fund. Invest EVERYTHING else. Your emergency fund earns four percent while protecting you. Everything else earns ten percent.", "img": "splitting money between emergency fund and investments"},
            {"text": "Every day you\nleave money in a\nregular bank\nyou're getting\nPOORER", "speech": "Every day you leave money in a regular bank savings account, you are getting POORER. Not staying the same. Getting POORER. Inflation doesn't take days off.", "img": "clock ticking as regular savings lose value"},
            {"text": "Transfer to high\nyield TODAY\n5 minutes of work\n= thousands more\nper year\nDO IT NOW", "speech": "Transfer to a high yield account TODAY. Five minutes of work equals THOUSANDS more per year. This is the easiest money decision you will ever make. DO IT NOW.", "img": "person making the switch to high yield account"},
        ],
        "keywords": ["Savings Account", "High Yield", "Inflation"],
    },
    {
        "title": "How I Turned $1 Into $100 (Rule of 72 Explained)",
        "slides": [
            {"text": "I can tell you\nEXACTLY when your\nmoney will DOUBLE\nOne simple formula", "speech": "I can tell you EXACTLY when your money will double. Not approximately. EXACTLY. With one simple formula that takes three seconds.", "img": "money doubling with mathematical formula"},
            {"text": "The Rule of 72\nDivide 72 by\nyour interest rate\n= years to double\nThat's IT", "speech": "The Rule of seventy two. Divide seventy two by your interest rate. The answer is how many years until your money doubles. That's IT. Three seconds.", "img": "rule of 72 formula on chalkboard"},
            {"text": "Stock market\naverages 10%\n72 ÷ 10 = 7.2\nyears to DOUBLE", "speech": "Stock market averages ten percent per year. Seventy two divided by ten equals seven point two. Your money DOUBLES every seven point two years in the stock market.", "img": "stock market doubling money every seven years"},
            {"text": "$1,000 today\n= $2,000 in 7 years\n= $4,000 in 14\n= $8,000 in 21\n= $16,000 in 28", "speech": "One thousand today becomes two thousand in seven years. Four thousand in fourteen. Eight thousand in twenty one. Sixteen thousand in twenty eight. It keeps DOUBLING.", "img": "money doubling chain over decades"},
            {"text": "Your savings\naccount at 0.01%?\n72 ÷ 0.01\n= 7,200 YEARS\nto double\nYou'll be DEAD", "speech": "Your savings account at zero point zero one percent? Seventy two divided by zero point zero one equals SEVEN THOUSAND TWO HUNDRED YEARS to double. You'll be dead for seven thousand years.", "img": "seven thousand year timeline for bank doubling"},
            {"text": "High yield at 5%?\n72 ÷ 5\n= 14.4 years\nBetter but still\nSLOW", "speech": "High yield savings at five percent? Fourteen point four years to double. BETTER. But still slow compared to stocks.", "img": "high yield savings doubling in fourteen years"},
            {"text": "This is why\nSTOCKS win\n7 years to double\nvs 14 years\nvs 7,200 years", "speech": "This is why STOCKS win. Seven years to double versus fourteen versus SEVEN THOUSAND. The choice is obvious. Get your money into the stock market.", "img": "comparison of doubling speeds between options"},
            {"text": "At age 25 with\n$5,000 invested\nAge 32: $10K\nAge 39: $20K\nAge 46: $40K\nAge 53: $80K\nAge 60: $160K", "speech": "At age twenty five with five thousand invested. By thirty two, ten thousand. Thirty nine, twenty thousand. Forty six, forty thousand. Fifty three, eighty thousand. Sixty, one hundred sixty thousand.", "img": "life timeline showing money doubling each period"},
            {"text": "And that's without\nadding a SINGLE\nextra dollar\nJust compound\ninterest working", "speech": "And that's WITHOUT adding a single extra dollar. Just compound interest working. Now imagine adding one hundred per month on TOP of that. You'd have over a MILLION.", "img": "compound interest working on its own"},
            {"text": "72 ÷ your rate\n= years to double\nMemorize this\nUse it forever\nTeach it to\neveryone", "speech": "Seventy two divided by your rate equals years to double. Memorize this. Use it forever. Teach it to everyone you know. This one formula changes how you see money forever.", "img": "formula memorized and shared with everyone"},
        ],
        "keywords": ["Rule of 72", "Compound Interest", "Doubling Money"],
    },
    {
        "title": "Your Credit Score Controls Your Life (Fix It In 30 Days)",
        "slides": [
            {"text": "Your credit score\ncontrols WHERE\nyou live\nWHAT car you\ndrive and HOW\nmuch you pay", "speech": "Your credit score controls WHERE you live, WHAT car you drive, and HOW MUCH you pay for everything. A bad score costs you HUNDREDS OF THOUSANDS over your lifetime.", "img": "credit score gauge affecting all life decisions"},
            {"text": "Below 600?\nYou pay 24%\non credit cards\nAbove 750?\nYou pay 15%\nThat's THOUSANDS", "speech": "Below six hundred? You pay twenty four percent on credit cards. Above seven fifty? You pay fifteen percent. On a car loan that difference is THOUSANDS of dollars. Same car. Different price.", "img": "credit score comparison showing different interest rates"},
            {"text": "On a $300K\nmortgage:\nBad credit = $1,900/mo\nGood credit = $1,400/mo\n$500 per month\nDIFFERENCE", "speech": "On a three hundred thousand dollar mortgage, bad credit costs you nineteen hundred per month. Good credit? Fourteen hundred. That's FIVE HUNDRED dollars per month difference. For THIRTY YEARS.", "img": "mortgage payment comparison good versus bad credit"},
            {"text": "Step 1:\nCheck your score\nFREE at\nAnnualCreditReport\nKnow your number", "speech": "Step one. Check your score for FREE at Annual Credit Report dot com. You NEED to know your number. Most people have no idea. That's like driving without a speedometer.", "img": "checking credit score on free website"},
            {"text": "Step 2:\nPay ALL bills\non time\nPayment history\n= 35% of\nyour score", "speech": "Step two. Pay ALL bills on time. Payment history is THIRTY FIVE percent of your score. One missed payment can drop you fifty points. Set up autopay for EVERYTHING.", "img": "setting up autopay for all monthly bills"},
            {"text": "Step 3:\nKeep credit usage\nbelow 30%\nIf your limit\nis $1000\nnever owe\nmore than $300", "speech": "Step three. Keep your credit utilization below thirty percent. If your limit is one thousand, never owe more than three hundred. Below ten percent is even better.", "img": "credit utilization gauge showing below thirty percent"},
            {"text": "Step 4:\nDon't close old\ncards EVER\nAge of accounts\nmatters\nKeep them open", "speech": "Step four. Don't close old credit cards EVER. The age of your accounts matters. That card you got in college? Keep it open. Use it once a month for gas.", "img": "old credit cards being kept open for history"},
            {"text": "Step 5:\nDispute any errors\non your report\n79% of reports\nhave mistakes\nFREE to fix", "speech": "Step five. Dispute any errors on your report. SEVENTY NINE percent of credit reports have mistakes. Wrong addresses. Accounts that aren't yours. Dispute them online for FREE.", "img": "disputing errors on credit report for free"},
            {"text": "In 30 days you\ncan boost your\nscore 50-100\npoints with\nthese steps", "speech": "In just thirty days you can boost your score fifty to one hundred points with these steps. I've seen people go from five eighty to seven hundred in one month.", "img": "credit score jumping up dramatically in 30 days"},
            {"text": "A good credit\nscore saves you\n$100,000+ over\nyour lifetime\nFix it NOW", "speech": "A good credit score saves you over ONE HUNDRED THOUSAND DOLLARS over your lifetime. Lower rates on everything. Better apartments. Better insurance. Fix your score NOW.", "img": "lifetime savings from excellent credit score"},
        ],
        "keywords": ["Credit Score", "Credit Repair", "Financial Health"],
    },
    {
        "title": "5 Things Rich People Buy That Poor People Don't",
        "slides": [
            {"text": "Rich people buy\n5 things that\npoor people think\nare a waste\nof money", "speech": "Rich people buy FIVE things that poor people think are a complete waste of money. And it's THESE purchases that keep the rich getting richer.", "img": "wealthy person making smart purchase decisions"},
            {"text": "Thing 1:\nBOOKS\nThe average CEO\nreads 52 books\nper year\nThe average person\nreads 4", "speech": "Thing one. BOOKS. The average CEO reads fifty two books per year. The average person reads four. Rich people invest in their BRAIN first. Knowledge compounds faster than money.", "img": "stack of business and finance books"},
            {"text": "Thing 2:\nOnline courses\nand coaching\n$500 course that\nmakes you $50K\nis a 100x return", "speech": "Thing two. Online courses and coaching. A five hundred dollar course that teaches you to earn fifty thousand more is a ONE HUNDRED X return. No stock gives you that.", "img": "online course leading to career advancement"},
            {"text": "Thing 3:\nHealth and fitness\nGym food\nsupplements\nYour body is\nyour #1 asset", "speech": "Thing three. Health and fitness. Gym membership. Quality food. Supplements. Your body is your NUMBER ONE asset. Can't make money from a hospital bed.", "img": "person investing in health at gym"},
            {"text": "Thing 4:\nTIME back\nHouse cleaning\nMeal prep service\nBuying back hours\nfor higher value", "speech": "Thing four. They buy TIME back. House cleaning. Meal prep service. Lawn care. They buy back HOURS and use those hours to make MORE money. Time is the ultimate asset.", "img": "outsourcing tasks to free up valuable time"},
            {"text": "Thing 5:\nASSETS\nStocks ETFs\nreal estate\nThings that pay\nTHEM every month", "speech": "Thing five. ASSETS. Stocks. ETFs. Real estate. Things that pay THEM every month. While poor people buy depreciating stuff, rich people buy things that GROW.", "img": "portfolio of growing assets and investments"},
            {"text": "What poor people\nbuy instead:\nDesigner clothes\nNew phones\nFancy cars\nAll DEPRECIATE", "speech": "What do poor people buy instead? Designer clothes that lose value. New phones every year. Fancy cars that depreciate fifty percent in three years. All depreciating assets.", "img": "depreciating purchases losing value quickly"},
            {"text": "A $50,000 car\nis worth $25,000\nin 3 years\nA $50,000\ninvestment is worth\n$80,000 in 3 years", "speech": "A fifty thousand dollar car is worth twenty five thousand in three years. A fifty thousand dollar investment is worth eighty thousand in three years. THAT'S the difference.", "img": "car losing value while investment gains value"},
            {"text": "Rich don't spend\nmore money\nThey spend money\nDIFFERENTLY\nOn things that\nGROW", "speech": "Rich people don't spend MORE money. They spend money DIFFERENTLY. On things that grow. On things that pay them back. On things that make them MORE.", "img": "spending money on growth instead of status"},
            {"text": "Next purchase:\nAsk yourself:\nDoes this make\nme RICHER or\nPOORER?\nChoose RICHER", "speech": "Before your next purchase, ask yourself one question. Does this make me RICHER or POORER? Choose richer. Every time. Your future depends on it.", "img": "choosing between richer and poorer decisions"},
        ],
        "keywords": ["Rich vs Poor", "Spending Habits", "Wealth Building"],
    },
    {
        "title": "The Credit Card Trick That Pays YOU $1,000/Year",
        "slides": [
            {"text": "Credit card\ncompanies are\npaying ME\n$1,000 per year\nto use their\ncards", "speech": "Credit card companies are paying ME one thousand dollars per year to use their cards. Not the other way around. Here's the trick they don't want you to know.", "img": "credit card cash back rewards adding up"},
            {"text": "The trick:\nUse credit cards\nfor EVERYTHING\nBut pay the\nfull balance\nEVERY MONTH", "speech": "The trick. Use credit cards for EVERYTHING you buy. Groceries. Gas. Bills. But pay the FULL BALANCE every single month. Never carry a balance. EVER.", "img": "paying credit card balance in full monthly"},
            {"text": "Most cards give\n1-5% CASH BACK\non everything\nyou buy\nThat's FREE money", "speech": "Most cards give you one to five percent CASH BACK on everything you buy. Groceries, three percent. Gas, three percent. Restaurants, four percent. That's FREE money.", "img": "cash back percentages on different spending"},
            {"text": "Average person\nspends $5,000/month\n3% cash back\n= $150/month\n= $1,800/year\nFOR FREE", "speech": "The average person spends five thousand per month on regular expenses. At three percent cash back, that's one hundred fifty per month. Eighteen hundred per year. FOR FREE.", "img": "annual cash back earnings calculation"},
            {"text": "The KEY rule:\nNEVER carry a\nbalance\n20% interest\nwill DESTROY\nyour gains", "speech": "The KEY rule. NEVER carry a balance. Pay it off in FULL every month. If you carry a balance, they charge you twenty percent interest. That DESTROYS everything.", "img": "warning about credit card interest danger"},
            {"text": "Treat your card\nlike a DEBIT card\nOnly spend what\nyou ALREADY have\nin your bank", "speech": "Treat your credit card like a DEBIT card. Only spend what you ALREADY have in your checking account. If you don't have the cash, don't swipe the card.", "img": "credit card used as debit card discipline"},
            {"text": "Sign up bonuses:\nSpend $3K in\n3 months\nGet $200 bonus\nOn spending you'd\ndo ANYWAY", "speech": "Sign up bonuses are even better. Spend three thousand in three months and get a two hundred dollar bonus. On spending you'd do ANYWAY. Rent. Utilities. Groceries.", "img": "credit card sign up bonus free money"},
            {"text": "Best cards:\n2% on everything\n3-5% on groceries\n3% on dining\nStack them\nstrategically", "speech": "Best strategy. One card with two percent on everything. Another with five percent on groceries. Another with three percent on dining. Stack them strategically.", "img": "multiple credit cards stacked for maximum rewards"},
            {"text": "I invest ALL my\ncash back\n$150/month\ninvested for\n30 years\n= $340,000", "speech": "I invest ALL my cash back. One hundred fifty per month invested for thirty years at ten percent? Three hundred forty thousand dollars. From FREE credit card rewards.", "img": "cash back invested turning into retirement fund"},
            {"text": "The banks make\nmoney from people\nwho DON'T pay\non time\nDon't be that\nperson", "speech": "Banks make money from people who DON'T pay on time. Be the person who gets PAID by the bank. Pay your balance in full. Collect your free money. Be smart.", "img": "being the smart credit card user who profits"},
        ],
        "keywords": ["Credit Card Rewards", "Cash Back", "Free Money"],
    },
    {
        "title": "My First $1,000 In Dividends (How Long It Took)",
        "slides": [
            {"text": "I just got my\nfirst $1,000 in\ndividends\nMoney I earned\nwhile SLEEPING", "speech": "I just hit my first one thousand dollars in dividend income. Money I earned while SLEEPING. While eating. While doing absolutely NOTHING. Here's how long it took.", "img": "dividend payment notification on phone screen"},
            {"text": "What are\ndividends?\nCompanies PAY YOU\njust for owning\ntheir stock\nEvery 3 months", "speech": "What are dividends? Companies PAY YOU just for owning their stock. Every three months, money shows up in your account. You don't have to do ANYTHING.", "img": "dividends deposited automatically every quarter"},
            {"text": "I started with\n$0 invested\n3 years ago\nPut in $300\nper month into\ndividend ETFs", "speech": "I started with zero invested three years ago. Put three hundred per month into dividend ETFs like SCHD and VYM. Automatically. Every payday.", "img": "starting dividend journey from zero balance"},
            {"text": "Month 1:\n$0.47 in dividends\nI laughed\nThat's less than\na pack of gum", "speech": "Month one. Forty seven CENTS in dividends. I laughed. That's less than a pack of gum. Most people quit here because it feels pointless. I didn't.", "img": "tiny first dividend payment of 47 cents"},
            {"text": "Month 6:\n$4.80/month\nStill pathetic\nBut I kept going\nBecause MATH\nworks", "speech": "Month six. Four dollars eighty cents per month. Still pathetic. But I kept going. Because I understood the MATH. Compound interest starts slow then EXPLODES.", "img": "small but growing dividend income chart"},
            {"text": "Year 1:\n$15/month\nYear 2:\n$45/month\nYear 3:\n$83/month\n= $1,000/year", "speech": "Year one, fifteen dollars per month. Year two, forty five. Year three, eighty three per month. That's one thousand per year. From doing NOTHING.", "img": "dividend income growing year over year"},
            {"text": "I reinvested\nEVERY dividend\nDividends buying\nmore shares\nthat pay MORE\ndividends", "speech": "I reinvested EVERY single dividend. Dividends bought more shares. More shares paid more dividends. More dividends bought even MORE shares. It's a snowball.", "img": "dividend reinvestment creating snowball effect"},
            {"text": "At this rate:\nYear 5: $250/month\nYear 10: $1,200/month\nYear 20: $8,000/month", "speech": "At this rate, year five is two fifty per month. Year ten is twelve hundred per month. Year twenty is EIGHT THOUSAND per month. All passive. All automatic.", "img": "projected dividend income growth long term"},
            {"text": "Imagine $8,000\nper month\nhitting your\naccount while\nyou SLEEP\nThat's freedom", "speech": "Imagine EIGHT THOUSAND dollars per month hitting your bank account while you sleep. That's more than most people's salary. And you did NOTHING to earn it that month.", "img": "passive dividend income exceeding most salaries"},
            {"text": "Start with $50\nper month into\nSCHD or VYM\nReinvest dividends\nWait 10 years\nThank me later", "speech": "Start with fifty dollars per month into SCHD or VYM. Turn on dividend reinvestment. Wait ten years. You'll have a money machine that pays you while you sleep. Thank me later.", "img": "starting fifty dollar monthly dividend investment"},
        ],
        "keywords": ["Dividends", "Passive Income", "Dividend Investing"],
    },
    {
        "title": "The 50/30/20 Rule Made Me Rich (Budgeting Is Easy)",
        "slides": [
            {"text": "The 50/30/20 rule\nis the EASIEST\nbudget ever created\nand it actually\nWORKS", "speech": "The fifty thirty twenty rule is the EASIEST budget ever created. And it actually WORKS. No spreadsheets. No complicated apps. Just three numbers.", "img": "simple pie chart showing 50 30 20 budget split"},
            {"text": "50% of income:\nNEEDS\nRent utilities\ngroceries insurance\ntransportation", "speech": "Fifty percent of your income goes to NEEDS. Rent. Utilities. Groceries. Insurance. Transportation. The stuff you literally cannot live without.", "img": "essential needs taking fifty percent of income"},
            {"text": "If you make\n$4,000/month:\n$2,000 for needs\nIf your needs\ncost MORE than\n50% you need\nto cut", "speech": "If you make four thousand per month, that's two thousand for needs. If your needs cost MORE than fifty percent, something needs to change. Cheaper apartment. Cheaper car.", "img": "calculating fifty percent needs budget"},
            {"text": "30% of income:\nWANTS\nDining out\nentertainment\nshopping streaming\nHave FUN", "speech": "Thirty percent goes to WANTS. Dining out. Entertainment. Shopping. Streaming. This is your FUN money. Yes, you're ALLOWED to have fun. That's the whole point.", "img": "thirty percent wants budget for fun spending"},
            {"text": "This is why\nmost budgets FAIL:\nThey cut ALL fun\nThat's not\nsustainable\nYou NEED wants", "speech": "This is why most budgets FAIL. They cut ALL the fun. That's not sustainable. You'll last two weeks then binge spend. The fifty thirty twenty gives you PERMISSION to enjoy life.", "img": "failed strict budgets versus balanced approach"},
            {"text": "20% of income:\nSAVINGS and\nINVESTMENTS\nThis is your\nFUTURE SELF\nmoney", "speech": "Twenty percent goes to savings and investments. This is your FUTURE SELF money. Emergency fund first. Then index funds. Then whatever investments you choose.", "img": "twenty percent savings and investment allocation"},
            {"text": "$4,000/month:\n$2,000 needs\n$1,200 wants\n$800 investing\nDone. That's\nyour budget.", "speech": "Four thousand per month? Two thousand needs. Twelve hundred wants. Eight hundred investing. DONE. That's your entire budget. Three categories. That's it.", "img": "complete 50/30/20 budget example breakdown"},
            {"text": "$800/month invested\nfor 30 years at\n10% returns\n= $1.8 MILLION\nFrom a simple\nbudget", "speech": "Eight hundred per month invested for thirty years at ten percent? ONE POINT EIGHT MILLION dollars. From a budget so simple a twelve year old could follow it.", "img": "1.8 million from simple 50/30/20 budget"},
            {"text": "The secret:\nAUTOMATE it\nPayday hits →\n20% auto invests\nYou never\ntouch it", "speech": "The secret is AUTOMATION. Payday hits, twenty percent auto-invests before you see it. Needs auto-pay from your account. Whatever's left is your wants. Zero thinking required.", "img": "automating budget with automatic transfers"},
            {"text": "Do this ONE thing\ntoday:\nSet up 20%\nauto transfer\nfrom checking to\ninvestment account", "speech": "Do ONE thing today. Set up a twenty percent auto transfer from your checking to your investment account on payday. That single action changes your entire financial future. Do it NOW.", "img": "setting up automated twenty percent investment"},
        ],
        "keywords": ["50/30/20 Rule", "Budgeting", "Simple Budget"],
    },
    {
        "title": "7 Passive Income Ideas That Actually Work (Not Fake Gurus)",
        "slides": [
            {"text": "7 passive income\nstreams that\nACTUALLY work\nNo fake gurus\nNo get rich\nquick schemes", "speech": "Seven passive income streams that ACTUALLY work. No fake gurus selling courses. No get rich quick schemes. Just real methods real people use to make money while they sleep.", "img": "seven real passive income streams listed"},
            {"text": "1. Dividend stocks\nBuy SCHD ETF\nGet paid every\n3 months\nAutomatic income\nforever", "speech": "One. Dividend stocks. Buy SCHD or VYM ETF. Get paid every three months automatically. The more you own, the more you earn. Forever.", "img": "dividend stocks paying quarterly income"},
            {"text": "2. High yield\nsavings\nPark emergency fund\nEarn 4-5% yearly\nFREE money for\ndoing nothing", "speech": "Two. High yield savings account. Park your emergency fund there. Earn four to five percent per year. Free money for literally doing nothing. Better than zero at your regular bank.", "img": "high yield savings earning passive interest"},
            {"text": "3. Index funds\nBuy VOO or VTI\n10% average returns\nSet and forget\nfor decades", "speech": "Three. Index fund investing. Buy VOO or VTI. Ten percent average returns over decades. Set it on autopilot. Forget about it. Let compound interest work.", "img": "index funds growing automatically over time"},
            {"text": "4. Digital products\nCreate an ebook\nor template ONCE\nSell it forever\non Gumroad", "speech": "Four. Digital products. Create an ebook, template, or guide ONCE. Sell it forever on Gumroad or Etsy. No inventory. No shipping. One hundred percent profit margins.", "img": "digital product selling online automatically"},
            {"text": "5. YouTube channel\nOld videos keep\nearning ad revenue\nFOREVER\nContent = passive\nincome machine", "speech": "Five. YouTube channel. Old videos keep earning ad revenue FOREVER. A video you made two years ago still makes money today. Content is a passive income MACHINE.", "img": "youtube video earning money months later"},
            {"text": "6. Rent out a room\non Airbnb\nOne spare room\n= $500-2000\nper month EXTRA", "speech": "Six. Rent out a spare room on Airbnb. One spare room can earn five hundred to two thousand per month. That's twenty four thousand per year from a room you're not using.", "img": "spare room earning income on airbnb"},
            {"text": "7. REITs\nReal estate\nwithout buying\nproperty\nBuy shares → earn\nrent income", "speech": "Seven. REITs. Real estate investment trusts. Own real estate WITHOUT buying property. Buy shares like stocks. Earn rent income as dividends. Easy and accessible.", "img": "REITs paying rental income without owning property"},
            {"text": "Start with ONE\nMaster it\nThen add another\nMillionaires average\n7 income streams", "speech": "Start with ONE. Master it. Then add another. Then another. Millionaires have an average of SEVEN income streams. You can build this over time.", "img": "building multiple income streams one by one"},
            {"text": "The best time to\nstart was 10\nyears ago\nThe second best\ntime is RIGHT NOW\nStart today", "speech": "The best time to start was ten years ago. The second best time is RIGHT NOW. Pick one from this list. Start today. Your future passive income depends on what you do THIS moment.", "img": "starting passive income journey today"},
        ],
        "keywords": ["Passive Income", "Income Streams", "Make Money"],
    },
    {
        "title": "Jeff Bezos Was Broke At 30 (Then He Did THIS)",
        "slides": [
            {"text": "Jeff Bezos was\nworking a normal\njob at age 30\nNo billions\nNo fame\nJust a guy", "speech": "Jeff Bezos was working a normal office job on Wall Street at age thirty. No billions. No fame. No Amazon. Just a regular guy with a regular paycheck.", "img": "young professional working in office building"},
            {"text": "He noticed ONE\nthing that changed\neverything:\nInternet usage was\ngrowing 2,300%\nper year", "speech": "He noticed ONE thing. Internet usage was growing twenty three hundred percent per year. He didn't know exactly what to do with that information. But he knew it was MASSIVE.", "img": "internet growth chart skyrocketing in 1990s"},
            {"text": "He made a list\nof 20 products\nto sell online\nBooks won\nbecause they were\ncheap to ship", "speech": "He made a list of twenty products he could sell online. Books won. Not because he loved books. Because they were CHEAP to ship, hard to damage, and millions of titles existed.", "img": "brainstorming list of products to sell online"},
            {"text": "He quit his\nWall Street job\nEveryone said\nhe was CRAZY\nHis boss begged\nhim to stay", "speech": "He quit his Wall Street job. His boss took him on a walk and begged him to stay. His parents worried. Friends thought he was insane. He did it anyway.", "img": "person leaving comfortable job for risky venture"},
            {"text": "He started Amazon\nin his GARAGE\nwith $10,000 of\nhis own savings\nPlus loans from\nhis parents", "speech": "He started Amazon in his GARAGE. Ten thousand of his own savings. Plus loans from his parents who told him they believed there was a seventy percent chance they'd lose everything.", "img": "garage startup humble beginnings"},
            {"text": "The first year\nhe packed boxes\nhimself on the\nfloor and said:\nwe need\nkneeling pads", "speech": "The first year he packed boxes himself. On the floor. On his knees. He told a friend they needed kneeling pads. His friend said they needed TABLES. Bezos said he'd never thought of that.", "img": "entrepreneur packing boxes in early startup"},
            {"text": "It took 6 YEARS\nbefore Amazon\nmade a single\ndollar of profit\nSIX YEARS of\nlosses", "speech": "It took SIX YEARS before Amazon made a single dollar of profit. Six years of losses. Six years of people calling him a failure. He kept going.", "img": "years of losses before first profitable quarter"},
            {"text": "The lesson:\nEvery billionaire\nstarted with\nNOTHING and an\nIDEA they wouldn't\nlet go of", "speech": "The lesson? Every billionaire started with NOTHING and an idea they wouldn't let go of. Bezos. Musk. Zuckerberg. They were all broke nobodies before they were somebodies.", "img": "from nothing to billions with persistence"},
            {"text": "You don't need\nbillions to\nget started\nYou need ONE idea\nand the courage\nto START", "speech": "You don't need billions to get started. You need ONE idea and the courage to START. Your garage. Your laptop. Your phone. You have everything you need RIGHT NOW.", "img": "starting a business with just a laptop today"},
            {"text": "The difference\nbetween dreamers\nand doers?\nDoers START\nbefore they're ready\nStart NOW", "speech": "The difference between dreamers and doers? Doers START before they're ready. They figure it out along the way. Stop waiting for perfect conditions. Start NOW.", "img": "taking action instead of just dreaming"},
        ],
        "keywords": ["Jeff Bezos", "Amazon", "Entrepreneurship"],
    },
    {
        "title": "The Debt Snowball That Erased My $30K Debt In 18 Months",
        "slides": [
            {"text": "I had $30,000\nin debt and\nno idea how to\nescape\nThen I found the\nDEBT SNOWBALL", "speech": "I had thirty thousand dollars in debt. Credit cards. Car loan. Student loans. I felt trapped. Then I found the DEBT SNOWBALL and everything changed.", "img": "person drowning in thirty thousand dollars of debt"},
            {"text": "The debt snowball:\nList ALL debts\nsmallest to largest\nIgnore interest\nrates completely", "speech": "The debt snowball. List ALL your debts from smallest to largest balance. Ignore interest rates completely. I know that sounds crazy. Trust the process.", "img": "list of debts organized smallest to largest"},
            {"text": "My debts:\n$800 medical bill\n$2,500 credit card\n$7,700 credit card\n$19,000 car loan\nTotal: $30,000", "speech": "My debts. Eight hundred dollar medical bill. Twenty five hundred credit card. Seventy seven hundred credit card. Nineteen thousand car loan. Total? Thirty thousand.", "img": "four debts totaling thirty thousand dollars"},
            {"text": "Step 1:\nPay MINIMUM on\neverything EXCEPT\nthe smallest debt\nAttack that one\nwith EVERYTHING", "speech": "Step one. Pay the MINIMUM on everything except the smallest debt. Attack the smallest one with EVERYTHING extra. Every spare dollar. Every side hustle dollar. Destroy it.", "img": "attacking smallest debt with intense focus"},
            {"text": "Month 1-2:\n$800 medical bill\nGONE\nFirst debt\nDESTROYED\nMomentum started", "speech": "Month one and two. Eight hundred dollar medical bill GONE. First debt DESTROYED. The feeling was incredible. Like knocking down the first domino. Momentum STARTED.", "img": "first debt crossed off the list celebration"},
            {"text": "Month 3-6:\n$2,500 credit card\nGONE\nNow I had MORE\nmoney to throw\nat the next one", "speech": "Months three through six. Twenty five hundred credit card GONE. Now I had even MORE money to throw at the next debt. The snowball was GROWING.", "img": "second debt eliminated snowball growing"},
            {"text": "Month 7-12:\n$7,700 credit card\nGONE\nI could see the\nfinish line\nI was OBSESSED", "speech": "Months seven through twelve. Seventy seven hundred credit card GONE. I could see the finish line. I was OBSESSED. Working overtime. Selling stuff. Every dollar went to debt.", "img": "third debt gone finish line in sight"},
            {"text": "Month 13-18:\n$19,000 car loan\nGONE\n$30,000 in debt\nDESTROYED\nin 18 months", "speech": "Months thirteen through eighteen. Nineteen thousand dollar car loan GONE. Thirty thousand in debt completely DESTROYED in eighteen months. I was DEBT FREE.", "img": "all debt eliminated person celebrating freedom"},
            {"text": "Why it works:\nSmall wins create\nMOMENTUM\nYou feel\nprogress FAST\nand you don't quit", "speech": "Why does the snowball work? Small wins create MOMENTUM. You feel progress FAST. You see results QUICKLY. And because of that, you DON'T QUIT.", "img": "momentum and motivation from small debt wins"},
            {"text": "List YOUR debts\nright now\nSmallest first\nAttack it TODAY\nYou CAN be\ndebt free", "speech": "List YOUR debts right now. Smallest to largest. Attack the smallest one TODAY. With everything you've got. You CAN be debt free. I'm living proof.", "img": "starting debt snowball journey with determination"},
        ],
        "keywords": ["Debt Snowball", "Debt Free", "Pay Off Debt"],
    },
    {
        "title": "This 19 Year Old Makes $10K/Month (Her Secret Is Boring)",
        "slides": [
            {"text": "She's 19\nMakes $10K\nper month\nHer secret?\nIt's the most\nBORING business\never", "speech": "She's nineteen years old. Makes ten thousand dollars per month. Her secret? It's the most BORING business you've ever heard of. And that's exactly why it works.", "img": "teenage entrepreneur working on laptop at home"},
            {"text": "She started a\nbookkeeping\nbusiness\nYes BOOKKEEPING\nThe most boring\nthing ever", "speech": "She started a bookkeeping business. Yes. BOOKKEEPING. Numbers. Spreadsheets. The most boring thing on the planet. But boring businesses make BANK.", "img": "bookkeeping spreadsheet on computer screen"},
            {"text": "She learned it\nin 3 weeks\non YouTube\nFREE\nNo degree needed\nNo certification\nrequired", "speech": "She learned bookkeeping in THREE WEEKS on YouTube. Completely FREE. No degree needed. No certification required. Just QuickBooks and basic math.", "img": "learning bookkeeping free on youtube tutorials"},
            {"text": "Her first client:\nA local bakery\n$400 per month\n5 hours of work\nThat's $80 per\nhour", "speech": "Her first client was a local bakery. Four hundred per month. Five hours of actual work. That's EIGHTY DOLLARS per hour. At NINETEEN. While her friends made minimum wage.", "img": "first bookkeeping client local small business"},
            {"text": "She found clients\nby messaging\nsmall businesses\non Instagram\n'Hey do you need\nhelp with books?'", "speech": "She found clients by messaging small businesses on Instagram. Simple message. Hey, do you need help with your books? Most said no. Some said YES. That's all you need.", "img": "direct messaging businesses on social media"},
            {"text": "By month 3:\n6 clients\n$400-600 each\n$3,000 per month\nAt NINETEEN", "speech": "By month three, six clients. Four to six hundred each. Three thousand per month. At NINETEEN years old. While her classmates debated what to major in.", "img": "six clients totaling three thousand monthly"},
            {"text": "By month 8:\n15 clients\n$600-800 each\n$10,000 per month\nShe hired a helper", "speech": "By month eight, fifteen clients. Six to eight hundred each. Ten thousand per month. She hired a helper for twenty dollars per hour. Kept EVERYTHING else.", "img": "growing to fifteen clients and hiring help"},
            {"text": "Why bookkeeping?\nEvery business\nNEEDS it\nMost business owners\nHATE doing it\nRecession proof", "speech": "Why bookkeeping? EVERY business needs it. Most business owners HATE doing it. It's recession proof. People always need their books done. Always.", "img": "every business needing bookkeeping services"},
            {"text": "Boring businesses\nthat print money:\nBookkeeping\nCleaning\nLawn care\nPressure washing\nLaundry service", "speech": "Boring businesses that print money. Bookkeeping. Cleaning. Lawn care. Pressure washing. Laundry service. Nobody talks about these because they're not sexy. But they WORK.", "img": "boring but profitable service businesses"},
            {"text": "Stop chasing\nsexy businesses\nStart a BORING\none that pays\n$10K per month\nStart this WEEK", "speech": "Stop chasing sexy businesses. Start a BORING one that pays ten thousand per month. Pick one from this list. Learn it on YouTube. Start reaching out to clients THIS WEEK.", "img": "choosing boring profitable business to start"},
        ],
        "keywords": ["Side Hustle", "Bookkeeping Business", "Young Entrepreneur"],
    },
    {
        "title": "Gold vs Stocks vs Real Estate (The REAL Winner)",
        "slides": [
            {"text": "Gold vs Stocks\nvs Real Estate\nWhich one\nACTUALLY makes\nyou the richest?", "speech": "Gold versus stocks versus real estate. Everyone has an opinion. But which one ACTUALLY makes you the richest? I ran the numbers. The answer surprised me.", "img": "gold bars stocks and house side by side"},
            {"text": "GOLD:\n$10,000 invested\nin 1980\n= $32,000 today\nThat's 2.7% per year\nBARE minimum", "speech": "GOLD. Ten thousand invested in nineteen eighty is worth about thirty two thousand today. That's two point seven percent per year. Barely beating inflation. TERRIBLE.", "img": "gold investment returns over forty years"},
            {"text": "Real Estate:\n$10,000 invested\nin 1980\n= $110,000 today\nThat's 5.8% per year\nDecent", "speech": "Real estate. Ten thousand invested in nineteen eighty in the average US home is worth about one hundred ten thousand today. Five point eight percent per year. DECENT but not amazing.", "img": "real estate appreciation over four decades"},
            {"text": "STOCKS:\n$10,000 invested\nin 1980 in S&P 500\n= $1,100,000 today\nThat's 11.5% per year\nWINNER", "speech": "STOCKS. Ten thousand in the S and P five hundred in nineteen eighty? ONE POINT ONE MILLION today. Eleven point five percent per year. The CLEAR winner. By a MILE.", "img": "stock market returns crushing other investments"},
            {"text": "$10K in Gold = $32K\n$10K in Real\nEstate = $110K\n$10K in Stocks\n= $1,100,000\nNot even CLOSE", "speech": "Ten thousand in gold? Thirty two thousand. Real estate? One hundred ten thousand. Stocks? ONE POINT ONE MILLION. It's not even close. Stocks win by TEN TIMES over real estate.", "img": "side by side comparison of all three returns"},
            {"text": "BUT real estate\nhas ONE advantage:\nLEVERAGE\n$50K down payment\ncontrols $300K\nproperty", "speech": "BUT real estate has ONE advantage. Leverage. A fifty thousand down payment controls a three hundred thousand property. If it goes up ten percent, you made sixty percent on YOUR money.", "img": "real estate leverage amplifying returns"},
            {"text": "Gold's only use:\nHedge against\nchaos\nWar inflation\ncurrency collapse\nNOT for getting\nrich", "speech": "Gold's only use is hedging against chaos. War. Hyperinflation. Currency collapse. It's insurance, not an investment. Don't buy gold to get rich. Buy it to not go broke.", "img": "gold as insurance against economic chaos"},
            {"text": "The BEST strategy:\n80% stocks\n10% real estate\n(through REITs)\n10% bonds or gold", "speech": "The BEST strategy for most people. Eighty percent stocks. Ten percent real estate through REITs. Ten percent bonds or gold. Simple. Diversified. Proven.", "img": "optimal portfolio allocation pie chart"},
            {"text": "Don't overthink it\nJust buy VOO\nS&P 500 ETF\nHold for 20+ years\nYou'll beat 90%\nof investors", "speech": "Don't overthink it. Buy VOO, the S and P five hundred ETF. Hold it for twenty plus years. You'll beat NINETY PERCENT of professional fund managers. Seriously.", "img": "simple VOO investment beating professionals"},
            {"text": "The winner is\nSTOCKS by far\nStart investing\nTODAY\nEven $50/month\nchanges everything", "speech": "The winner is STOCKS by far. Not even a competition. Start investing TODAY. Even fifty dollars per month changes everything over twenty years. Your future millionaire self starts now.", "img": "stocks winning the investment comparison clearly"},
        ],
        "keywords": ["Gold vs Stocks", "Real Estate", "Investing Comparison"],
    },
    {
        "title": "I Read 50 Money Books (Only 3 Were Worth It)",
        "slides": [
            {"text": "I read 50 money\nbooks in 2 years\nOnly 3 were\nactually worth\nyour time", "speech": "I read FIFTY money books in two years. Most were garbage. Recycled advice. Fluff. Only THREE were actually worth your time. Here they are.", "img": "stack of fifty finance books read over two years"},
            {"text": "Book 1:\nThe Psychology\nof Money by\nMorgan Housel\nThis book changes\nhow you THINK", "speech": "Book one. The Psychology of Money by Morgan Housel. This book doesn't teach you what to invest in. It changes HOW YOU THINK about money. And thinking is everything.", "img": "psychology of money book cover displayed"},
            {"text": "Key lesson:\nWealth is what\nyou DON'T see\nThe money NOT\nspent\nThe car NOT bought\nThe flex NOT made", "speech": "Key lesson. Wealth is what you DON'T see. The money NOT spent. The car NOT bought. The flex NOT made. Real wealth is invisible. The flashy people are usually the brokest.", "img": "invisible wealth concept versus flashy spending"},
            {"text": "Book 2:\nThe Simple Path\nTo Wealth by\nJL Collins\nThe only investing\nbook you'll\nEVER need", "speech": "Book two. The Simple Path to Wealth by JL Collins. This is the ONLY investing book you'll ever need. He explains everything in plain English. Buy VTSAX. That's basically it.", "img": "simple path to wealth book recommendation"},
            {"text": "Key lesson:\nBuy VTSAX\n(total stock market)\nHold forever\nDon't sell in\ncrashes\nGet rich slowly", "speech": "Key lesson. Buy VTSAX, the total stock market index fund. Hold it forever. Don't sell during crashes. Get rich slowly. That's the entire book in three sentences.", "img": "VTSAX buy and hold forever strategy"},
            {"text": "Book 3:\nI Will Teach You\nTo Be Rich by\nRamit Sethi\nThe how-to guide\nfor your 20s-30s", "speech": "Book three. I Will Teach You To Be Rich by Ramit Sethi. This is the HOW-TO guide. He gives you scripts for negotiating bills. Exact account recommendations. Step by step.", "img": "I will teach you to be rich practical guide"},
            {"text": "Key lesson:\nAutomate your\nfinances completely\nPayday → auto\ninvest → auto\nbills → spend\nwhat's left guilt\nfree", "speech": "Key lesson. AUTOMATE your finances completely. Payday triggers auto investing. Then auto bill pay. Whatever's left? Spend it GUILT FREE. You already saved and invested.", "img": "fully automated financial system setup"},
            {"text": "Why the other\n47 books failed:\nThey say the\nSAME THINGS\njust with more\nwords and fluff", "speech": "Why did the other forty seven books fail? They all say the SAME THINGS. Just with more words, more stories, and more fluff. These three cover EVERYTHING.", "img": "repetitive finance books saying same advice"},
            {"text": "You don't need\n50 books\nYou need 3 books\nand the discipline\nto ACTUALLY\nfollow them", "speech": "You don't need fifty books. You need three books and the discipline to ACTUALLY follow them. Information without action is useless. APPLY what you learn.", "img": "three books plus action equals financial success"},
            {"text": "Read these 3\nbooks this month\nYour money IQ\nwill triple\nYour bank account\nwill follow", "speech": "Read these three books this month. Your money IQ will triple. And your bank account will follow. The library has them for FREE. Zero excuses.", "img": "three must read finance books changing lives"},
        ],
        "keywords": ["Money Books", "Financial Education", "Book Recommendations"],
    },
    {
        "title": "The Roth IRA Cheat Code (Tax Free Millions)",
        "slides": [
            {"text": "The Roth IRA is\na LEGAL cheat code\nthat makes your\nmoney grow\n100% TAX FREE", "speech": "The Roth IRA is a LEGAL cheat code for building wealth. Your money grows one hundred percent TAX FREE. The government will NEVER touch it. Here's how it works.", "img": "Roth IRA glowing as a cheat code for wealth"},
            {"text": "How it works:\nYou invest\nAFTER-TAX money\nIt grows tax free\nYou withdraw\nTAX FREE in\nretirement", "speech": "How it works. You invest after-tax money now. It grows tax free for decades. Then you withdraw it TAX FREE in retirement. No taxes on any of the gains. EVER.", "img": "Roth IRA money growing completely tax free"},
            {"text": "Regular account:\nInvest $500K →\nGrows to $2M →\nPay $300K in\ntaxes on gains\nOuch", "speech": "In a regular account, invest five hundred thousand, it grows to two million, you pay THREE HUNDRED THOUSAND in taxes on the gains. Three hundred thousand. To the government.", "img": "regular account losing huge amount to taxes"},
            {"text": "Roth IRA:\nInvest $500K →\nGrows to $2M →\nPay $0 in taxes\nZERO. NADA.\nAll yours.", "speech": "Roth IRA. Same five hundred thousand. Grows to two million. Pay ZERO in taxes. Nothing. Nada. All two million is YOURS. That's THREE HUNDRED THOUSAND more in your pocket.", "img": "Roth IRA keeping all gains tax free"},
            {"text": "You can invest\nup to $7,000\nper year (2024)\nThat's $583\nper month", "speech": "You can invest up to seven thousand per year. That's five hundred eighty three per month. Max it out if you can. Every dollar in a Roth grows tax free FOREVER.", "img": "seven thousand per year Roth IRA contribution"},
            {"text": "$583/month from\nage 25 to 65\nat 10% returns\n= $3.2 MILLION\nALL TAX FREE", "speech": "Five eighty three per month from age twenty five to sixty five at ten percent? THREE POINT TWO MILLION DOLLARS. All tax free. Not a penny to the IRS.", "img": "3.2 million tax free in Roth IRA at 65"},
            {"text": "Where to open one:\nFidelity\nCharles Schwab\nVanguard\nAll FREE\nTakes 10 minutes", "speech": "Where to open one. Fidelity. Charles Schwab. Vanguard. All completely FREE. No fees. No minimum to start. Takes ten minutes online.", "img": "opening Roth IRA at top brokerage firms"},
            {"text": "What to invest in:\nVOO or VTI\nIndex funds\nSet and forget\nLet it compound\nfor 30 years", "speech": "What to invest in? VOO or VTI. Index funds. Set it on autopilot. Let compound interest work its magic for thirty years. Don't touch it. Don't look at it during crashes.", "img": "investing Roth IRA in simple index funds"},
            {"text": "The BIGGEST mistake:\nNot starting\nat age 20-25\nEvery year you\nwait costs you\n$100K+", "speech": "The BIGGEST mistake is not starting at age twenty to twenty five. Every year you wait costs you over ONE HUNDRED THOUSAND in potential tax-free gains. TIME is the key ingredient.", "img": "cost of waiting to start Roth IRA"},
            {"text": "If you're under 50\nopen a Roth IRA\nTODAY\nFuture you will\nCRY tears of joy\nat age 65", "speech": "If you're under fifty, open a Roth IRA TODAY. Put in whatever you can. Even fifty dollars. Future you will CRY tears of joy at sixty five when you have MILLIONS tax free.", "img": "starting Roth IRA today for tax free future"},
        ],
        "keywords": ["Roth IRA", "Tax Free", "Retirement Investing"],
    },
    {
        "title": "Stop Renting! House Hack Your Way To Free Housing",
        "slides": [
            {"text": "What if your\nhousing was\ncompletely FREE?\nHouse hacking\nmakes it possible\nHere's how", "speech": "What if your housing was completely FREE? No rent. No mortgage payment. House hacking makes it possible. People do this every day. Here's EXACTLY how.", "img": "free housing through house hacking strategy"},
            {"text": "House hacking:\nBuy a small\nmulti-family\nproperty\nLive in one unit\nRent out the rest", "speech": "House hacking. Buy a small multi-family property. A duplex, triplex, or fourplex. Live in one unit. Rent out the other units. Their rent pays YOUR mortgage.", "img": "duplex with owner living in one unit"},
            {"text": "Example:\nBuy a duplex\nfor $250,000\nMortgage: $1,800/mo\nTenant pays:\n$1,900/mo\nYou live FREE\n+ $100 profit", "speech": "Example. Buy a duplex for two hundred fifty thousand. Your mortgage is eighteen hundred per month. Your tenant pays nineteen hundred. You live completely FREE plus one hundred profit.", "img": "duplex math showing free housing plus profit"},
            {"text": "FHA loan:\nOnly 3.5% down\n$250K house\n= $8,750 down\nThat's IT\nYou're a homeowner", "speech": "FHA loan. Only three point five percent down. On a two fifty thousand house, that's eight thousand seven fifty down. That's IT. You're a homeowner with almost no money down.", "img": "FHA loan low down payment for house hack"},
            {"text": "Your tenant builds\nYOUR equity\nYOUR wealth\nYOUR net worth\nWhile paying\nYOUR mortgage", "speech": "Your tenant builds YOUR equity. YOUR wealth. YOUR net worth. They're paying YOUR mortgage. Every month, you get richer because someone else pays for your house.", "img": "tenant payments building owner equity wealth"},
            {"text": "After 1-2 years:\nMove out\nRent BOTH units\nBuy another\nduplex\nRepeat", "speech": "After one to two years, move out. Rent BOTH units. Now you have positive cash flow. Buy another duplex. Live in it. Repeat. This is how real estate empires start.", "img": "moving out and repeating house hack strategy"},
            {"text": "By age 30 you\ncould own:\n4 properties\n8 rental units\n$3,000+ monthly\ncash flow", "speech": "By age thirty you could own four properties. Eight rental units. Three thousand plus in monthly cash flow. All because you house hacked instead of renting.", "img": "growing real estate portfolio from house hacking"},
            {"text": "Compare to renting:\nRent = $1,500/mo\n$18,000/year\n$180,000 in 10 years\nto your LANDLORD'S\nwealth", "speech": "Compare that to renting. Fifteen hundred per month. Eighteen thousand per year. One hundred eighty thousand in TEN YEARS going straight to your LANDLORD'S wealth. Not yours.", "img": "rent money building landlord wealth not yours"},
            {"text": "Yes it's more work\nYes tenants can\nbe difficult\nBut FREE housing\nis worth the\neffort", "speech": "Yes it's more work. Yes tenants can be difficult. But FREE housing is worth the effort. You're being paid to live somewhere. That's the best deal in real estate.", "img": "effort worth it for free housing benefit"},
            {"text": "Talk to a lender\nthis week about\nFHA loans\nFind duplexes\nin your area\nStop paying\nsomeone else's\nmortgage", "speech": "Talk to a lender THIS WEEK about FHA loans. Search for duplexes in your area. Stop paying someone else's mortgage. Start building YOUR wealth. House hack your way to freedom.", "img": "searching for duplex to start house hacking"},
        ],
        "keywords": ["House Hacking", "Real Estate", "Free Housing"],
    },
    {
        "title": "One Number Predicts If You'll Be Rich Or Broke",
        "slides": [
            {"text": "There's ONE number\nthat predicts\nwhether you'll be\nRICH or BROKE\nMost people have\nno idea what it is", "speech": "There's ONE number that predicts whether you'll be rich or broke. And most people have absolutely no idea what it is. Or what theirs is.", "img": "mysterious number predicting financial future"},
            {"text": "It's not your\nsalary\nIt's not your\ncredit score\nIt's not your\nnet worth\nIt's your\nSAVINGS RATE", "speech": "It's not your salary. It's not your credit score. It's not your net worth. It's your SAVINGS RATE. The percentage of your income that you save and invest.", "img": "savings rate as the key financial number"},
            {"text": "Someone earning\n$200K who saves\n0% will NEVER\nbe wealthy\nSomeone earning\n$40K who saves\n25% WILL BE", "speech": "Someone earning two hundred thousand who saves zero percent will NEVER be wealthy. Someone earning forty thousand who saves twenty five percent WILL BE. The rate matters more than the income.", "img": "high income zero savings versus low income high savings"},
            {"text": "Savings rate 0%:\nYou work until\nyou die\nNo retirement\nNo freedom\nEver", "speech": "Savings rate zero percent? You work until you DIE. No retirement. No freedom. No escape. EVER. This is most people. This is the default path.", "img": "working forever with zero savings rate"},
            {"text": "Savings rate 10%:\nYou can retire\nin about 40 years\nSo if you start\nat 25 you retire\nat 65", "speech": "Savings rate ten percent? You can retire in about forty years. Start at twenty five, retire at sixty five. Normal. Average. Nothing special.", "img": "ten percent savings rate forty year timeline"},
            {"text": "Savings rate 25%:\nRetire in 32 years\nStart at 25\nRetire at 57\nEIGHT years early", "speech": "Savings rate twenty five percent? Retire in thirty two years. Start at twenty five, retire at FIFTY SEVEN. Eight years early. That's eight YEARS of freedom.", "img": "25 percent savings rate retiring eight years early"},
            {"text": "Savings rate 50%:\nRetire in 17 years\nStart at 25\nRetire at 42\nThat's FIRE", "speech": "Savings rate FIFTY percent? Retire in SEVENTEEN years. Start at twenty five, retire at FORTY TWO. That's the FIRE movement. Financial Independence, Retire Early.", "img": "50 percent savings rate retiring at 42"},
            {"text": "Savings rate 75%:\nRetire in 7 years\nStart at 25\nRetire at 32\nExtreme but\nPOSSIBLE", "speech": "Savings rate seventy five percent? Retire in SEVEN years. Start at twenty five, retire at THIRTY TWO. Extreme? Yes. Possible? Absolutely. People do it.", "img": "extreme savings rate seven year retirement"},
            {"text": "What's YOUR\nsavings rate?\nCalculate it:\n(money saved ÷\ntotal income)\n× 100", "speech": "What's YOUR savings rate? Calculate it right now. Money saved and invested divided by total income times one hundred. That number tells you your financial future.", "img": "calculating personal savings rate formula"},
            {"text": "Increase it by\njust 5% this month\nThat alone could\ngive you 5 MORE\nyears of freedom\nDo it TODAY", "speech": "Increase your savings rate by just FIVE percent this month. That alone could give you FIVE MORE YEARS of freedom. Spend a little less. Invest a little more. Start TODAY.", "img": "increasing savings rate for earlier financial freedom"},
        ],
        "keywords": ["Savings Rate", "Financial Independence", "FIRE Movement"],
    },
    {
        "title": "The Envelope Method That Stopped My Overspending INSTANTLY",
        "slides": [
            {"text": "I used to\noverspend by\n$800 every\nsingle month\nThis method\nstopped it\nOVERNIGHT", "speech": "I used to overspend by EIGHT HUNDRED dollars every single month. Swiping my card without thinking. This one method stopped it OVERNIGHT. Literally overnight.", "img": "overspending eight hundred per month every month"},
            {"text": "The CASH\nenvelope method:\nWithdraw your\nbudget in CASH\nPut it in\nenvelopes\nWhen it's gone\nIT'S GONE", "speech": "The cash envelope method. Withdraw your monthly budget in CASH. Put it in labeled envelopes. When the envelope is empty, you're DONE spending in that category. Period.", "img": "labeled cash envelopes for budget categories"},
            {"text": "Groceries: $400\nDining out: $200\nFun money: $150\nGas: $150\nEach gets its\nown envelope", "speech": "Groceries, four hundred. Dining out, two hundred. Fun money, one fifty. Gas, one fifty. Each category gets its own envelope with EXACT cash inside.", "img": "budget envelopes labeled with exact amounts"},
            {"text": "Why it works:\nSwiping a card\nfeels like NOTHING\nHanding over $20\nFEELS like losing\nsomething", "speech": "Why does this work? Swiping a card feels like NOTHING. It's invisible money. But handing over a twenty dollar bill FEELS like losing something. You physically FEEL the money leaving.", "img": "pain of paying cash versus painless card swipe"},
            {"text": "Studies show:\nPeople spend\n12-18% MORE\nwith cards than\ncash\nThat's THOUSANDS\nper year", "speech": "Studies show people spend twelve to eighteen percent MORE with cards than cash. On a three thousand monthly budget, that's FOUR HUNDRED wasted. Thousands per year.", "img": "research showing cards cause more spending"},
            {"text": "Week 1 was HARD\nI ran out of\ndining money\nby Wednesday\nI realized how\nmuch I was\nwasting", "speech": "Week one was HARD. I ran out of dining money by Wednesday. And I realized just how much I'd been wasting. Three days into the week and my dining budget was GONE.", "img": "running out of dining budget early in the week"},
            {"text": "By week 3:\nI naturally spent\nless\nI thought twice\nbefore EVERY\npurchase\nAutomatic control", "speech": "By week three, I naturally spent less. I thought twice before EVERY purchase. Do I really need this? Can I make this at home? The control became automatic.", "img": "thinking twice before every purchase decision"},
            {"text": "Month 1 result:\nI saved $600\nthat I normally\nwould have wasted\nWith ZERO effort", "speech": "Month one result. I saved SIX HUNDRED dollars that I normally would have wasted. With zero effort. Zero willpower. Just the physical constraint of finite cash.", "img": "six hundred dollars saved in first month"},
            {"text": "Digital version:\nUse separate\nbank accounts\nfor each category\nSame concept\nModern twist", "speech": "Don't like cash? Digital version. Use separate bank accounts for each category. Same concept. Modern twist. Many banks let you create free sub-accounts.", "img": "digital envelope system with bank sub-accounts"},
            {"text": "Try it for\nONE month\nWithdraw your\nbudget in cash\nWatch how fast\nyour spending\ndrops", "speech": "Try it for ONE month. Withdraw your budget in cash. Divide it into envelopes. Watch how FAST your spending drops. This is the simplest budgeting hack that exists.", "img": "starting cash envelope method this month"},
        ],
        "keywords": ["Cash Envelope", "Budgeting", "Stop Overspending"],
    },
    {
        "title": "Emergency Fund: $1,000 In 30 Days (Starter Guide)",
        "slides": [
            {"text": "63% of Americans\ncan't cover a\n$500 emergency\nDon't be one\nof them\nBuild $1,000 in\n30 days", "speech": "Sixty three percent of Americans can't cover a five hundred dollar emergency. ONE flat tire away from disaster. Don't be one of them. Build a thousand dollar emergency fund in thirty days.", "img": "emergency fund protecting against financial disaster"},
            {"text": "Why $1,000?\nCovers most\nemergencies:\nCar repair $600\nER visit $300\nBroken phone $200", "speech": "Why one thousand? It covers MOST emergencies. Car repair, six hundred. ER co-pay, three hundred. Broken phone, two hundred. This money keeps you from going into DEBT over surprises.", "img": "common emergency expenses under one thousand"},
            {"text": "Day 1-3:\nSell stuff you\ndon't use\nOld clothes\nelectronics games\nTarget: $200-400", "speech": "Days one through three. Sell stuff you don't use. Old clothes. Electronics. Games. Books. Shoes. Facebook Marketplace. Poshmark. Target two hundred to four hundred dollars. You have more than you think.", "img": "selling unused items for emergency fund cash"},
            {"text": "Day 4-10:\nCut 3 expenses\nYou won't miss:\nSubscription $15\nEating out $50\nCoffee $25\n= $90 saved", "speech": "Days four through ten. Cut three expenses you won't miss. One subscription, fifteen. Eating out twice less, fifty. Coffee at home, twenty five. Ninety dollars saved. Easy.", "img": "cutting three easy expenses for savings"},
            {"text": "Day 11-20:\nPick up ONE\nside gig:\nDoorDash for\n2 hours/day\n= $300-400\nin 10 days", "speech": "Days eleven through twenty. Pick up ONE side gig. DoorDash, Instacart, or TaskRabbit for two hours per day. Three hundred to four hundred in ten days. Temporary hustle, permanent benefit.", "img": "side gig earning extra money for emergency fund"},
            {"text": "Day 21-30:\nRedirect ALL\nextra money\nto your fund\nEvery dollar\ncounts\nAlmost there!", "speech": "Days twenty one through thirty. Redirect ALL extra money to your emergency fund. Skip one night out. Return that Amazon order you don't need. Every dollar counts. You're almost there.", "img": "pushing to finish emergency fund goal"},
            {"text": "Where to keep it:\nHigh yield savings\naccount\n4-5% interest\nNot your checking\nNot under your\nmattress", "speech": "Where to keep it. A high yield savings account earning four to five percent. NOT your checking account where you'll spend it. Not under your mattress. Accessible but separate.", "img": "emergency fund in high yield savings account"},
            {"text": "RULES:\n1. Only for REAL\nemergencies\n2. A sale is NOT\nan emergency\n3. Replenish\nimmediately\nafter using it", "speech": "The rules. Only for REAL emergencies. A sale is NOT an emergency. Wanting new shoes is NOT an emergency. And if you use it, replenish it IMMEDIATELY.", "img": "emergency fund rules clearly defined"},
            {"text": "After $1,000:\nBuild to $5,000\nThen 3 months\nof expenses\nThen 6 months\nThat's REAL safety", "speech": "After one thousand, build to five thousand. Then three months of expenses. Then six months. THAT'S real safety. One thousand is just the start. The beginning of financial peace.", "img": "growing emergency fund from 1K to 6 months"},
            {"text": "Start TODAY\nnot Monday\nnot next month\nTODAY\nSell one thing\nright now\nGet to $1,000\nthis month", "speech": "Start TODAY. Not Monday. Not next month. TODAY. Sell one thing right now. Set up that high yield account. Get to one thousand this month. Your financial safety depends on it.", "img": "starting emergency fund challenge today"},
        ],
        "keywords": ["Emergency Fund", "Financial Safety", "Saving $1000"],
    },
    {
        "title": "Never Buy A New Car (The Math Will Make You Sick)",
        "slides": [
            {"text": "Buying a new car\nis the DUMBEST\nfinancial decision\nmost people make\nHere's the math", "speech": "Buying a new car is the DUMBEST financial decision most people make. And I can prove it with simple math that will make you SICK.", "img": "new car in dealership with price tag"},
            {"text": "A new car loses\n20% of its value\nthe SECOND you\ndrive it off\nthe lot", "speech": "A new car loses TWENTY PERCENT of its value the SECOND you drive it off the lot. You haven't even parked it at home yet and you've LOST thousands.", "img": "new car value dropping as it leaves dealership"},
            {"text": "$40,000 new car\n= $32,000 the\nmoment you\nleave the dealer\nYou just LOST\n$8,000 in\n5 minutes", "speech": "A forty thousand dollar new car is worth thirty two thousand the moment you leave the dealer. You just LOST eight thousand dollars in five minutes. That's sixteen hundred per minute.", "img": "eight thousand dollars lost in five minutes"},
            {"text": "After 3 years:\nWorth $22,000\nYou LOST $18,000\nThats $500 per\nMONTH in\ndepreciation", "speech": "After three years that same car is worth twenty two thousand. You LOST eighteen thousand. That's five hundred per MONTH in depreciation alone. PLUS your car payment. PLUS insurance.", "img": "car depreciation chart over three years"},
            {"text": "The smart move:\nBuy a 2-3 year\nold car\nSomeone ELSE paid\nthe $18,000\ndepreciation\nfor you", "speech": "The smart move. Buy a two to three year old car. Someone ELSE already paid the eighteen thousand in depreciation. You get the same car for forty percent less.", "img": "buying used car that someone else depreciated"},
            {"text": "A 3-year-old car\nfor $22,000\nvs same car\nnew for $40,000\nSave $18,000\nSAME CAR", "speech": "A three year old version of that same car costs twenty two thousand. The SAME car. Same features. Same reliability. Eighteen thousand LESS. For a car with most of its life ahead.", "img": "same car model new versus three years old"},
            {"text": "That $18,000 saved\ninvested for\n30 years at 10%\n= $314,000\nFrom ONE car\ndecision", "speech": "That eighteen thousand saved, invested for thirty years at ten percent? THREE HUNDRED FOURTEEN THOUSAND DOLLARS. From ONE car decision. Imagine making this choice every time.", "img": "car savings invested growing to six figures"},
            {"text": "Average person\nbuys 9 cars\nin their lifetime\n9 × $18K saved\n= $162,000\nINVESTED", "speech": "The average person buys nine cars in their lifetime. Nine times eighteen thousand saved equals one hundred sixty two thousand dollars INVESTED. That grows to over TWO MILLION.", "img": "lifetime car savings totaling millions invested"},
            {"text": "Rich people\nknow this:\nWarren Buffett\ndrove a 2006\nCadillac until 2014\nHe's worth\n$120 BILLION", "speech": "Rich people know this. Warren Buffett drove a two thousand six Cadillac until twenty fourteen. He's worth one hundred twenty BILLION. Rich people don't waste money on depreciating assets.", "img": "Warren Buffett with his old modest car"},
            {"text": "Next car:\nBuy 2-3 years old\nSave $15-20K\nInvest the\ndifference\nYour future self\nwill thank you", "speech": "Next time you need a car, buy two to three years old. Save fifteen to twenty thousand. Invest the difference. Drive the same car. Build wealth instead of losing it. Your future self will thank you.", "img": "choosing used car and investing the savings"},
        ],
        "keywords": ["New Car", "Depreciation", "Smart Spending"],
    },
    {
        "title": "How To Make $500 This Weekend (5 Easy Side Hustles)",
        "slides": [
            {"text": "5 ways to make\n$500 THIS weekend\nNo skills needed\nNo investment\nneeded\nJust hustle", "speech": "Five ways to make FIVE HUNDRED dollars THIS weekend. No skills needed. No investment needed. Just hustle and a willingness to work for two days.", "img": "making five hundred dollars in one weekend"},
            {"text": "Side hustle 1:\nFlip furniture\nBuy cheap on FB\nMarketplace\nClean it up\nResell for 2-3x", "speech": "Side hustle one. Flip furniture. Buy cheap dressers and tables on Facebook Marketplace for twenty to fifty bucks. Clean them up. Sand. Paint. Resell for two to three times the price.", "img": "flipping furniture bought cheap sold for profit"},
            {"text": "Example:\nBuy dresser: $30\nPaint and handles: $20\nSell for: $150\nProfit: $100\nDo 5 = $500", "speech": "Example. Buy a dresser for thirty dollars. Twenty bucks in paint and new handles. Sell for one fifty. That's one hundred profit. Do five of these. Five hundred bucks in a weekend.", "img": "furniture flip profit calculation example"},
            {"text": "Side hustle 2:\nPressure washing\nRent a washer\nfor $50/day\nCharge $100-300\nper driveway", "speech": "Side hustle two. Pressure washing. Rent a pressure washer for fifty bucks a day. Charge one hundred to three hundred per driveway. Two or three driveways and you're at five hundred.", "img": "pressure washing driveway earning money"},
            {"text": "Side hustle 3:\nYard sale +\nresell leftovers\non eBay/Mercari\nYour junk is\nsomeone's treasure", "speech": "Side hustle three. Yard sale Saturday. Everything you don't use or need. Resell leftovers on eBay or Mercari. Your junk is someone else's treasure. Clean out and cash in.", "img": "yard sale and online reselling for cash"},
            {"text": "Side hustle 4:\nTaskRabbit\nHelp people:\nMove furniture\nAssemble IKEA\nMount TVs\n$25-50 per hour", "speech": "Side hustle four. TaskRabbit. Help people move furniture. Assemble IKEA. Mount TVs. Clean garages. Twenty five to fifty per hour. Ten hours over a weekend, that's five hundred.", "img": "helping people with tasks on TaskRabbit"},
            {"text": "Side hustle 5:\nDog walking\nand pet sitting\n$20-40 per walk\nBook 15 walks\n= $500 weekend", "speech": "Side hustle five. Dog walking and pet sitting. Twenty to forty per walk on Rover or Wag. Book fifteen walks over the weekend. Five hundred bucks for hanging out with dogs.", "img": "walking dogs for money on weekends"},
            {"text": "The goal:\nMake $500 extra\nDon't SPEND it\nINVEST every\nsingle dollar\nThat $500 matters", "speech": "The goal isn't just to make five hundred. It's to INVEST every single dollar. Don't spend it. That five hundred invested monthly becomes over a MILLION in thirty years.", "img": "investing every side hustle dollar earned"},
            {"text": "$500 per weekend\n= $2,000/month\n= $24,000/year\nInvested for\n20 years\n= $1.5 MILLION", "speech": "Five hundred per weekend is two thousand per month. Twenty four thousand per year. Invested for twenty years at ten percent? ONE POINT FIVE MILLION DOLLARS. From weekend hustle.", "img": "weekend hustle money growing into millions"},
            {"text": "Pick ONE from\nthis list\nDo it THIS\nweekend\nYour first $500\nis waiting\nSTOP scrolling\nSTART hustling", "speech": "Pick ONE from this list. Do it THIS weekend. Your first five hundred is waiting. Stop scrolling. Start hustling. The money won't make itself. But YOU can.", "img": "choosing a side hustle and starting immediately"},
        ],
        "keywords": ["Side Hustle", "Make Money Fast", "Weekend Income"],
    },
]



LONG_FORM_TOPICS = [
    {
        "title": "How To Build Wealth From $0 (Complete Step-By-Step Blueprint)",
        "slides": [
            {"text": "You have ZERO\ndollars right now\nHere's your\nBLUEPRINT to wealth", "speech": "You have ZERO dollars right now. No savings. No investments. No clue where to start. THIS is your complete BLUEPRINT to building REAL WEALTH from NOTHING.", "img": "empty wallet on table with blueprint plans beside it"},
            {"text": "Step 1:\nSTOP the bleeding\nTrack every\nDOLLAR you spend", "speech": "Step ONE. STOP the bleeding. For the next thirty days, track EVERY SINGLE DOLLAR you spend. You will be SHOCKED where your money is going.", "img": "hand tracking expenses in notebook with calculator"},
            {"text": "The average person\nwastes $500/month\non stuff they\nDON'T NEED", "speech": "The average person wastes FIVE HUNDRED DOLLARS per month on subscriptions they forgot about, impulse buys, and overpriced coffee. FIVE HUNDRED. That's your SEED MONEY.", "img": "money flying out of wallet into unnecessary purchases"},
            {"text": "Step 2:\nBuild a $1000\nemergency fund\nBEFORE anything else", "speech": "Step TWO. Build a ONE THOUSAND DOLLAR emergency fund BEFORE you do ANYTHING else. This is your financial SAFETY NET. Without it, one car repair destroys you.", "img": "glass jar filling up with emergency savings cash"},
            {"text": "Put it in a\nHigh Yield Savings\naccount earning\n4-5% APY", "speech": "Put that emergency fund in a HIGH YIELD SAVINGS ACCOUNT earning FOUR TO FIVE PERCENT annually. Your money works while it sits there. Not a regular bank paying ZERO POINT ZERO ONE PERCENT.", "img": "online banking showing high yield savings interest rate"},
            {"text": "Step 3:\nDESTROY high\ninterest debt\nCredit cards FIRST", "speech": "Step THREE. DESTROY your high interest debt. Credit cards charging TWENTY FIVE PERCENT interest are EMERGENCY LEVEL. Pay minimums on everything else and ATTACK the highest rate first.", "img": "scissors cutting credit card with debt chains breaking"},
            {"text": "Every $1000 in\ncredit card debt\ncosts you $250\nPER YEAR", "speech": "Every THOUSAND DOLLARS in credit card debt costs you TWO HUNDRED FIFTY DOLLARS per year in PURE INTEREST. That's money BURNED. Lighting cash on FIRE.", "img": "hundred dollar bills burning in flames of interest"},
            {"text": "Step 4:\nThe 50/30/20 rule\n50% needs\n30% wants\n20% savings", "speech": "Step FOUR. Follow the FIFTY THIRTY TWENTY rule. FIFTY percent of income goes to NEEDS like rent and food. THIRTY percent to WANTS. TWENTY percent STRAIGHT to savings and investing.", "img": "pie chart showing fifty thirty twenty budget split"},
            {"text": "On $4000/month\nthat's $800/month\ninvested\n$9,600 per year", "speech": "On FOUR THOUSAND dollars a month income, that's EIGHT HUNDRED DOLLARS per month going to investments. That's NINE THOUSAND SIX HUNDRED dollars per year BUILDING YOUR FUTURE.", "img": "monthly paycheck being split into savings and investment"},
            {"text": "Step 5:\nOpen a ROTH IRA\nTax FREE growth\nfor LIFE", "speech": "Step FIVE. Open a ROTH IRA immediately. You put in money you ALREADY paid taxes on, and it grows COMPLETELY TAX FREE. When you retire, you pay ZERO taxes on withdrawals.", "img": "roth ira account growing with tax free stamp"},
            {"text": "Max contribution\n$7000 per year\nThat's $583\nper month", "speech": "Max contribution is SEVEN THOUSAND DOLLARS per year. That's FIVE HUNDRED EIGHTY THREE dollars per month. If you can't max it out yet, put in WHATEVER you can. Start with FIFTY DOLLARS.", "img": "contribution meter filling up to seven thousand"},
            {"text": "Step 6:\nInvest in INDEX\nFUNDS not\nindividual stocks", "speech": "Step SIX. Invest in INDEX FUNDS, not individual stocks. An S and P FIVE HUNDRED index fund gives you ownership in the FIVE HUNDRED BIGGEST companies in America. INSTANT diversification.", "img": "index fund chart showing diversified portfolio growth"},
            {"text": "S&P 500 returns\n10% average\nper year for\nthe last 50 YEARS", "speech": "The S and P FIVE HUNDRED has returned an average of TEN PERCENT per year for the last FIFTY YEARS. Through recessions, wars, pandemics. TEN PERCENT. CONSISTENTLY.", "img": "fifty year stock market chart trending upward"},
            {"text": "$500/month at 10%\nfor 30 years\n= $1.1 MILLION\ndollars", "speech": "Invest FIVE HUNDRED dollars per month at TEN PERCENT for THIRTY YEARS and you'll have ONE POINT ONE MILLION DOLLARS. That's the power of COMPOUND INTEREST doing the heavy lifting.", "img": "compound growth curve reaching one million dollars"},
            {"text": "Step 7:\nIncrease your\nINCOME not just\ncut expenses", "speech": "Step SEVEN. Increase your INCOME. Cutting expenses has a FLOOR. You can only cut so much. But your income has NO CEILING. Learn skills that pay MORE.", "img": "salary ladder climbing upward with skill badges"},
            {"text": "Learn high income\nskills: coding\nsales, marketing\nfinance", "speech": "Learn HIGH INCOME SKILLS. Coding, sales, digital marketing, finance, data analysis. These skills can DOUBLE or TRIPLE your income within TWO YEARS.", "img": "laptop showing high income skill courses online"},
            {"text": "Step 8:\nAutomate EVERYTHING\nSet up auto\ntransfers on payday", "speech": "Step EIGHT. AUTOMATE EVERYTHING. Set up automatic transfers on PAYDAY. Money moves to savings and investments BEFORE you can spend it. You can't spend what you don't SEE.", "img": "automated bank transfers flowing on payday"},
            {"text": "Pay yourself FIRST\nbefore rent\nbefore food\nbefore ANYTHING", "speech": "Pay yourself FIRST. Before rent. Before food. Before ANYTHING. The money goes to your future self AUTOMATICALLY. This is the number ONE habit of EVERY millionaire.", "img": "person paying themselves first with priority arrow"},
            {"text": "Step 9:\nNEVER upgrade\nyour lifestyle\nwhen income rises", "speech": "Step NINE. NEVER upgrade your lifestyle when your income goes up. Got a raise? INVEST the difference. This is called LIFESTYLE CREEP and it DESTROYS wealth builders.", "img": "person resisting luxury upgrade and investing instead"},
            {"text": "The gap between\nwhat you EARN\nand SPEND is\nyour WEALTH engine", "speech": "The GAP between what you EARN and what you SPEND is your WEALTH ENGINE. The BIGGER the gap, the FASTER you get rich. Protect that gap with your LIFE.", "img": "growing gap between earnings and spending chart"},
            {"text": "START TODAY\nnot tomorrow\nnot Monday\nnot next month\nTODAY", "speech": "START TODAY. Not tomorrow. Not Monday. Not next month. TODAY. Every day you wait costs you THOUSANDS in lost compound growth. Open that account RIGHT NOW. Your future self will THANK YOU.", "img": "person taking action now with clock showing today"},
        ],
        "keywords": ["Build Wealth", "Money Blueprint", "Financial Freedom"],
    },
    {
        "title": "Why Smart People Stay Broke (5 Money Psychology Traps)",
        "slides": [
            {"text": "Why do SMART\npeople stay\nBROKE?\nIt's not about IQ", "speech": "Why do incredibly SMART people stay BROKE their entire lives while high school dropouts become MILLIONAIRES? It has NOTHING to do with intelligence.", "img": "smart person with degree next to wealthy entrepreneur"},
            {"text": "Money is 80%\nBEHAVIOR and\nonly 20%\nknowledge", "speech": "Money is EIGHTY PERCENT BEHAVIOR and only TWENTY PERCENT knowledge. You can know EVERYTHING about finance and still be broke because of your HABITS.", "img": "brain split between behavior and knowledge percentages"},
            {"text": "Bias #1:\nInstant Gratification\nWe want it NOW\nnot in 30 years", "speech": "Bias number ONE. INSTANT GRATIFICATION. Our brains are WIRED to want rewards NOW, not in thirty years. That new phone feels AMAZING today but DESTROYS your retirement.", "img": "person choosing instant reward over long term wealth"},
            {"text": "A $1200 phone\nevery 2 years\ncosts you $85,000\nin retirement", "speech": "Buying a TWELVE HUNDRED DOLLAR phone every two years instead of investing that money costs you EIGHTY FIVE THOUSAND DOLLARS in retirement savings over thirty years. ONE ITEM.", "img": "phone purchase compared to retirement savings growth"},
            {"text": "Bias #2:\nSocial Comparison\nKeeping up with\npeople who are BROKE", "speech": "Bias number TWO. SOCIAL COMPARISON. You're trying to keep up with people who are ALSO BROKE. That neighbor with the BMW? Drowning in DEBT. That coworker with designer clothes? ZERO savings.", "img": "neighbors competing with luxury items both in debt"},
            {"text": "80% of luxury\ncar drivers are\nNOT millionaires\nthey're in DEBT", "speech": "EIGHTY PERCENT of luxury car drivers are NOT millionaires. They're regular people drowning in FIVE to SEVEN YEAR car loans. Real millionaires drive USED CARS.", "img": "luxury car with hidden debt chains underneath"},
            {"text": "Bias #3:\nLoss Aversion\nWe fear losing $100\nmore than gaining $200", "speech": "Bias number THREE. LOSS AVERSION. We fear LOSING one hundred dollars MORE than we enjoy GAINING two hundred. This makes us TERRIBLE investors who sell at the WORST time.", "img": "scale showing loss feeling heavier than equal gain"},
            {"text": "People who PANIC\nSOLD in March 2020\nmissed a 100%\nrecovery in 1 year", "speech": "People who PANIC SOLD their stocks in March twenty twenty MISSED a ONE HUNDRED PERCENT recovery in just ONE YEAR. Fear cost them HALF their retirement.", "img": "stock market crash and recovery chart twenty twenty"},
            {"text": "Bias #4:\nAnchoring\nA $200 shirt on\nSALE for $100\nis NOT a deal", "speech": "Bias number FOUR. ANCHORING. A two hundred dollar shirt on SALE for one hundred is NOT a deal. It's a one hundred dollar shirt. The anchor price TRICKS your brain into thinking you SAVED money.", "img": "sale tag with fake original price marketing trick"},
            {"text": "Stores mark UP\nprices 40% before\nSALES so you\nfeel like a genius", "speech": "Stores MARK UP prices FORTY PERCENT before putting items on SALE so you feel like a GENIUS for getting a deal. You're spending money you WOULDN'T HAVE SPENT.", "img": "retail store with marked up prices before sale event"},
            {"text": "Bias #5:\nLifestyle Inflation\nEarn more\nspend more\nstay BROKE", "speech": "Bias number FIVE. LIFESTYLE INFLATION. Every time you earn more, you spend more. New salary, new car. Bonus check, new wardrobe. You UPGRADE everything and save NOTHING.", "img": "salary increasing but spending growing equally fast"},
            {"text": "Someone earning\n$200K in debt is\nWORSE OFF than\n$50K with savings", "speech": "Someone earning TWO HUNDRED THOUSAND with maxed out credit cards is WORSE OFF financially than someone earning FIFTY THOUSAND with six months of savings. INCOME is not WEALTH.", "img": "high earner in debt versus modest earner with savings"},
            {"text": "Bias #6:\nOverconfidence\nI'll start investing\nNEXT YEAR", "speech": "Bias number SIX. OVERCONFIDENCE. Telling yourself you'll start investing NEXT YEAR. Next year you say the SAME THING. Overconfidence in your future discipline is a TRAP.", "img": "calendar pages flipping with next year repeated"},
            {"text": "Starting 10 years\nlate costs you\n65% of your\ntotal wealth", "speech": "Starting investing just TEN YEARS late costs you SIXTY FIVE PERCENT of your total potential wealth. TEN YEARS of procrastination destroys TWO THIRDS of your retirement.", "img": "two growth curves showing early versus late investor"},
            {"text": "Bias #7:\nSunk Cost Fallacy\nStaying in bad\ninvestments too long", "speech": "Bias number SEVEN. SUNK COST FALLACY. Staying in a TERRIBLE investment because you already put money in. The money is GONE. Holding won't bring it BACK.", "img": "person holding sinking stock refusing to let go"},
            {"text": "The FIX:\nAutomate investing\nso emotions\nCAN'T interfere", "speech": "The FIX for ALL these biases? AUTOMATE your investing so your emotions CANNOT INTERFERE. Set it and forget it. Remove the human element from the equation.", "img": "automated investment system running without emotions"},
            {"text": "Set up auto\ninvest $500/month\ninto index funds\nDON'T TOUCH IT", "speech": "Set up AUTO INVEST. Five hundred dollars per month into index funds. DON'T LOOK AT IT. DON'T TOUCH IT. Let compound interest work while you LIVE YOUR LIFE.", "img": "automated monthly investment transfer running smoothly"},
            {"text": "Delete shopping\napps and unfollow\ninfluencers selling\nyou JUNK", "speech": "DELETE shopping apps from your phone. UNFOLLOW influencers who make you feel like you need to BUY things. Protect your mind from SPENDING TRIGGERS.", "img": "phone deleting shopping apps and unfollowing accounts"},
            {"text": "Surround yourself\nwith people who\nBUILD wealth not\nFLAUNT it", "speech": "SURROUND yourself with people who BUILD wealth, not FLAUNT it. Your circle determines your financial future. If your friends are broke spenders, YOU WILL BE TOO.", "img": "group of wealth builders discussing financial strategies"},
            {"text": "Your BEHAVIOR\nwith money matters\nmore than how\nMUCH you make", "speech": "Your BEHAVIOR with money matters INFINITELY MORE than how MUCH you make. Fix your psychology FIRST. The money will follow. Start TODAY. Change your MIND, change your WEALTH.", "img": "mindset shift from broke thinking to wealth thinking"},
        ],
        "keywords": ["Money Psychology", "Financial Behavior", "Wealth Mindset"],
    },
    {
        "title": "Credit Score Secrets - How to Hit 800+ and Unlock Everything",
        "slides": [
            {"text": "Your credit score\nis your FINANCIAL\nREPUTATION\nin one number", "speech": "Your credit score is your FINANCIAL REPUTATION compressed into ONE NUMBER. It determines whether you get approved, how much you pay, and what doors OPEN or CLOSE for you.", "img": "credit score meter showing range from poor to excellent"},
            {"text": "800+ credit score\nsaves you over\n$100,000 in\nyour LIFETIME", "speech": "An EIGHT HUNDRED PLUS credit score saves you over ONE HUNDRED THOUSAND DOLLARS in your lifetime through lower interest rates on mortgages, cars, and credit cards.", "img": "person with excellent credit saving thousands on loans"},
            {"text": "35% of your score\nis PAYMENT HISTORY\nNever miss\na single payment", "speech": "THIRTY FIVE PERCENT of your score is PAYMENT HISTORY. This is the BIGGEST factor. ONE missed payment can drop your score FIFTY to ONE HUNDRED POINTS instantly.", "img": "payment history calendar showing all green checkmarks"},
            {"text": "Set up AUTOPAY\non every single\nbill you have\nNO EXCEPTIONS", "speech": "Set up AUTOPAY on EVERY SINGLE BILL. No exceptions. Even if it's just the minimum payment. A missed payment stays on your report for SEVEN YEARS.", "img": "all bills on autopay with automatic payment icons"},
            {"text": "30% is credit\nUTILIZATION\nHow much of your\nlimit you USE", "speech": "THIRTY PERCENT is credit UTILIZATION. This is how much of your available credit you're USING. If you have a ten thousand dollar limit and use five thousand, that's FIFTY PERCENT utilization.", "img": "credit card utilization bar showing percentage used"},
            {"text": "Keep utilization\nBELOW 10%\nfor the BEST\nscore boost", "speech": "Keep your utilization BELOW TEN PERCENT for the BEST score boost. Below THIRTY is okay. But below TEN is where your score REALLY starts to CLIMB.", "img": "utilization dropping below ten percent with score rising"},
            {"text": "PRO TIP: Pay your\nbalance BEFORE\nthe statement\ncloses not due date", "speech": "PRO TIP. Pay your balance BEFORE the statement closing date, not just the due date. The statement balance is what gets REPORTED to the credit bureaus.", "img": "calendar showing statement date versus due date"},
            {"text": "15% is LENGTH\nof credit history\nDon't close your\nOLDEST cards", "speech": "FIFTEEN PERCENT is LENGTH of credit history. Your oldest account matters. NEVER close your oldest credit card even if you don't use it. Just buy something small once a year.", "img": "timeline showing long credit history boosting score"},
            {"text": "10% is CREDIT MIX\nHave credit cards\nAND installment\nloans for best score", "speech": "TEN PERCENT is CREDIT MIX. Having DIFFERENT types of credit helps. Credit cards, a car loan, student loans, a mortgage. Variety shows you can handle MULTIPLE types of debt.", "img": "different credit types mixed together in portfolio"},
            {"text": "10% is NEW CREDIT\nEvery application\nis a HARD INQUIRY\nthat hurts your score", "speech": "The last TEN PERCENT is NEW CREDIT. Every time you APPLY for credit, it's a HARD INQUIRY that drops your score TWO to FIVE POINTS. Don't apply for five cards in one month.", "img": "hard inquiry marks on credit report from applications"},
            {"text": "Secret #1:\nBecome an\nAUTHORIZED USER\non someone's old card", "speech": "Secret number ONE. Become an AUTHORIZED USER on a family member's OLD credit card with perfect payment history. Their ENTIRE history gets added to YOUR report instantly.", "img": "authorized user being added to parent credit card"},
            {"text": "This can add\n10+ years of\nperfect history\nOVERNIGHT", "speech": "This can add TEN PLUS YEARS of perfect credit history to your report OVERNIGHT. It's completely LEGAL and one of the fastest ways to boost a thin credit file.", "img": "credit history jumping from new to ten years overnight"},
            {"text": "Secret #2:\nRequest credit\nlimit INCREASES\nevery 6 months", "speech": "Secret number TWO. Call your credit card company and request a CREDIT LIMIT INCREASE every SIX MONTHS. Higher limit plus same spending equals LOWER utilization. Score goes UP.", "img": "phone call requesting credit limit increase approved"},
            {"text": "Secret #3:\nDispute ANY errors\non your credit\nreport for FREE", "speech": "Secret number THREE. Pull your credit report from annual credit report dot com for FREE. Dispute ANY errors you find. THIRTY PERCENT of reports have mistakes that HURT your score.", "img": "magnifying glass finding errors on credit report"},
            {"text": "Errors can include\nwrong balances\naccounts not yours\nlate payments wrong", "speech": "Common errors include WRONG BALANCES, accounts that AREN'T YOURS, late payments that were actually ON TIME, and debts listed TWICE. Each one is dragging your score DOWN.", "img": "list of common credit report errors highlighted red"},
            {"text": "Secret #4:\nThe 48 hour\nrapid rescore\ntrick for mortgages", "speech": "Secret number FOUR. The FORTY EIGHT HOUR rapid rescore. When applying for a mortgage, your lender can request an EXPEDITED update to your credit score reflecting recent payments.", "img": "rapid rescore request form for mortgage application"},
            {"text": "Secret #5:\nNEVER carry a\nbalance thinking\nit helps your score", "speech": "Secret number FIVE. NEVER carry a balance thinking it HELPS your score. This is the BIGGEST MYTH in personal finance. Paying interest does NOTHING for your credit score. Pay in FULL.", "img": "myth busted stamp over carry balance advice"},
            {"text": "The IDEAL strategy:\nUse card for\neverything\npay in FULL\nevery month", "speech": "The IDEAL strategy. Use your credit card for EVERYTHING you'd normally buy. Earn rewards and cashback. Then pay the balance IN FULL every single month. ZERO interest paid.", "img": "credit card rewards being earned with full payment"},
            {"text": "Bad score right now?\n6-12 months of\nperfect habits\ncan FIX it", "speech": "Have a BAD score right now? SIX to TWELVE MONTHS of perfect payment habits, low utilization, and disputing errors can raise your score ONE HUNDRED to TWO HUNDRED POINTS.", "img": "credit score climbing rapidly over twelve month period"},
            {"text": "Your credit score\nis a GAME\nLearn the rules\nand WIN", "speech": "Your credit score is a GAME with clear rules. Learn them. Play them. WIN. An eight hundred plus score unlocks the LOWEST rates, the BEST cards, and saves you a FORTUNE. Start TODAY.", "img": "winner podium with excellent credit score trophy"},
        ],
        "keywords": ["Credit Score", "800 Credit", "Credit Secrets"],
    },
    {
        "title": "Stock Market For Beginners: Turn $1000 Into $50K (Full Guide)",
        "slides": [
            {"text": "You want to\ninvest in STOCKS\nbut have NO IDEA\nwhere to start", "speech": "You want to invest in the STOCK MARKET but you have absolutely NO IDEA where to start. You've heard people make MILLIONS but also LOSE EVERYTHING. Let me break it down.", "img": "beginner looking at stock market charts confused"},
            {"text": "A STOCK is\nownership in a\nREAL company\nYou own a PIECE", "speech": "A STOCK is OWNERSHIP in a REAL company. When you buy one share of Apple, you literally OWN a tiny piece of Apple. Their profits? YOURS. Their growth? YOURS.", "img": "stock certificate showing ownership piece of company"},
            {"text": "The stock market\nhas returned 10%\nper year on\naverage since 1926", "speech": "The stock market has returned an average of TEN PERCENT per year since NINETEEN TWENTY SIX. Through world wars, recessions, pandemics. It ALWAYS recovers and goes HIGHER.", "img": "hundred year stock market chart always trending up"},
            {"text": "$1000 invested\nin 1980 in S&P 500\nis worth $140,000\nTODAY", "speech": "ONE THOUSAND DOLLARS invested in the S and P FIVE HUNDRED in nineteen eighty is worth over ONE HUNDRED FORTY THOUSAND DOLLARS today. That's the power of STAYING INVESTED.", "img": "one thousand dollars growing to one hundred forty thousand"},
            {"text": "DON'T buy\nindividual stocks\nwhen starting\nBuy INDEX FUNDS", "speech": "When you're starting out, DO NOT buy individual stocks. One company can go to ZERO. Instead, buy INDEX FUNDS. You own HUNDREDS of companies at once. If one fails, the rest carry you.", "img": "single stock risk versus diversified index fund safety"},
            {"text": "S&P 500 index fund\n= 500 biggest\nUS companies\nin ONE purchase", "speech": "An S and P FIVE HUNDRED index fund gives you the FIVE HUNDRED BIGGEST companies in America in ONE single purchase. Apple, Google, Amazon, Microsoft. ALL OF THEM. One click.", "img": "top five hundred companies logos in one fund basket"},
            {"text": "Best beginner\nindex funds:\nVOO, SPY, or\nFXAIX", "speech": "The best beginner index funds are V O O from Vanguard, S P Y from State Street, or F X A I X from Fidelity. They all track the S and P FIVE HUNDRED. Pick ANY of them.", "img": "three index fund options displayed for beginners"},
            {"text": "Step 1: Open a\nbrokerage account\nFidelity or Schwab\nBOTH are FREE", "speech": "Step ONE. Open a brokerage account. Fidelity and Schwab are both COMPLETELY FREE. No fees. No minimums. Takes TEN MINUTES online. You can start with literally ONE DOLLAR.", "img": "brokerage account signup screen simple and free"},
            {"text": "Step 2: Set up\nautomatic investing\n$100/month minimum\nDON'T SKIP months", "speech": "Step TWO. Set up AUTOMATIC investing. At minimum ONE HUNDRED DOLLARS per month going into your index fund. Set the date for right after payday and DON'T SKIP MONTHS.", "img": "automatic monthly investment schedule calendar"},
            {"text": "This strategy is\ncalled DOLLAR COST\nAVERAGING and it's\nBULLETPROOF", "speech": "This strategy is called DOLLAR COST AVERAGING. You buy at HIGH prices AND LOW prices automatically. Over time, you get a GREAT average price without TIMING the market.", "img": "dollar cost averaging chart showing consistent buying"},
            {"text": "NEVER try to\nTIME the market\nEven PROS get\nit wrong 90%", "speech": "NEVER try to TIME the market. Even professional fund managers get it wrong NINETY PERCENT of the time over ten years. Just buy CONSISTENTLY and let TIME do the work.", "img": "failed market timing versus consistent investing results"},
            {"text": "What about\nmarket CRASHES?\nThey're actually\nSALES for investors", "speech": "What about market CRASHES? Here's the secret. Crashes are actually SALES for long-term investors. Stocks go on DISCOUNT. Your automatic investments buy MORE shares for LESS money.", "img": "stock market crash with sale signs for investors"},
            {"text": "If you invested\n$500/month through\n2008 crash\nyou'd be UP 400%", "speech": "If you invested FIVE HUNDRED dollars per month through the two thousand eight crash and KEPT GOING, you'd be up over FOUR HUNDRED PERCENT today. The crash was a GIFT.", "img": "investor who kept buying through crash now wealthy"},
            {"text": "The ONLY way to\nlose in stocks:\nSELL during a crash\nor STOP investing", "speech": "The ONLY way to LOSE money in the stock market long-term is to SELL during a crash or STOP investing. If you hold and keep buying, history says you WIN. Every. Single. Time.", "img": "two paths sell in panic lose versus hold and win"},
            {"text": "How about\nDIVIDENDS?\nCompanies PAY YOU\njust for owning", "speech": "How about DIVIDENDS? Many companies PAY YOU cash just for OWNING their stock. The S and P five hundred pays about one and a half percent in dividends per year ON TOP of growth.", "img": "dividend payments flowing into investor bank account"},
            {"text": "REINVEST dividends\nautomatically\nThis creates a\nSNOWBALL effect", "speech": "REINVEST your dividends automatically. This creates a SNOWBALL effect. Dividends buy more shares. More shares earn more dividends. More dividends buy MORE shares. EXPONENTIAL growth.", "img": "snowball rolling downhill getting bigger with dividends"},
            {"text": "With $1000 to\nstart here's your\nEXACT first move\nright now", "speech": "You have ONE THOUSAND DOLLARS to start. Here is your EXACT first move RIGHT NOW. Open a Fidelity or Schwab account. Buy one thousand dollars of V O O or equivalent index fund.", "img": "step by step first investment one thousand dollars"},
            {"text": "Then set up\n$200/month auto\ninvest and\nDON'T TOUCH IT\nfor 20 years", "speech": "Then set up TWO HUNDRED DOLLARS per month automatic investment. And DON'T TOUCH IT for TWENTY YEARS minimum. Check it once a year MAX. Let compound interest WORK.", "img": "twenty year hands off investment growing massively"},
            {"text": "$200/month for\n20 years at 10%\n= $153,000\nfrom just $48K put in", "speech": "TWO HUNDRED dollars per month for TWENTY YEARS at ten percent average returns equals ONE HUNDRED FIFTY THREE THOUSAND DOLLARS. You only put in FORTY EIGHT THOUSAND. The market gave you ONE HUNDRED FIVE THOUSAND for FREE.", "img": "investment calculator showing contributions versus growth"},
            {"text": "The stock market\nis the greatest\nwealth building\ntool EVER CREATED\nUSE IT", "speech": "The stock market is the greatest wealth building tool EVER CREATED. It's not for Wall Street elites. It's for YOU. Open that account TODAY. Start with whatever you have. Your future self will THANK you.", "img": "ordinary person building wealth with stock market"},
        ],
        "keywords": ["Stock Market", "Beginner Investing", "Index Funds"],
    },
    {
        "title": "7 Income Streams of Millionaires - Build Multiple Cash Flows",
        "slides": [
            {"text": "The average\nmillionaire has\n7 income streams\nYou have ONE", "speech": "The average MILLIONAIRE has SEVEN income streams. You probably have ONE. Your job. That's it. If you lose it, you lose EVERYTHING. That's not wealth, that's a TIGHTROPE.", "img": "millionaire with seven flowing income rivers"},
            {"text": "Stream #1:\nEARNED INCOME\nYour salary\nor hourly wage", "speech": "Stream number ONE. EARNED INCOME. Your salary or hourly wage. This is where EVERYONE starts. But if this is your ONLY stream, you're building on a HOUSE OF CARDS.", "img": "paycheck from employer as single income source"},
            {"text": "Maximize this FIRST\nNegotiate raises\nSwitch jobs every\n2-3 years", "speech": "MAXIMIZE this first. Negotiate raises AGGRESSIVELY. Switch jobs every TWO to THREE years for a TEN to TWENTY PERCENT pay bump. Loyalty to one company is EXPENSIVE.", "img": "salary jumping higher with each job switch"},
            {"text": "Stream #2:\nPROFIT INCOME\nStart a side\nbusiness for $0-500", "speech": "Stream number TWO. PROFIT INCOME from a business. You don't need a million dollars to start. Freelancing, consulting, dropshipping, tutoring. Start for ZERO to FIVE HUNDRED dollars.", "img": "small business growing from side hustle to profit"},
            {"text": "Even $500/month\nextra is $6000/year\nthat goes STRAIGHT\nto investments", "speech": "Even FIVE HUNDRED extra dollars per month is SIX THOUSAND per year that goes STRAIGHT to investments. That side income invested for twenty years becomes over THREE HUNDRED THOUSAND.", "img": "side hustle income flowing into investment account"},
            {"text": "Stream #3:\nINTEREST INCOME\nHigh yield savings\nand bonds pay YOU", "speech": "Stream number THREE. INTEREST INCOME. Your high yield savings account and bonds PAY YOU interest. Five percent on fifty thousand dollars is TWO THOUSAND FIVE HUNDRED per year for doing NOTHING.", "img": "interest payments accumulating from savings and bonds"},
            {"text": "Stream #4:\nDIVIDEND INCOME\nOwn stocks that\npay you quarterly", "speech": "Stream number FOUR. DIVIDEND INCOME. Own stocks and funds that pay you cash EVERY QUARTER just for holding them. Build a large enough portfolio and dividends cover your BILLS.", "img": "quarterly dividend payments landing in account"},
            {"text": "$500K in dividend\nstocks at 3%\npays $15,000/year\nWITHOUT selling", "speech": "FIVE HUNDRED THOUSAND in dividend stocks paying THREE PERCENT gives you FIFTEEN THOUSAND dollars per year WITHOUT selling a SINGLE SHARE. The shares KEEP growing too.", "img": "dividend income flowing while portfolio keeps growing"},
            {"text": "Stream #5:\nRENTAL INCOME\nOwn property\nthat pays you\nmonthly", "speech": "Stream number FIVE. RENTAL INCOME. Own property that pays you MONTHLY rent. A single rental property can generate FIVE HUNDRED to TWO THOUSAND per month in PASSIVE CASH FLOW.", "img": "rental property with monthly rent payments coming in"},
            {"text": "Can't afford a\nwhole property?\nREITs let you\ninvest with $100", "speech": "Can't afford a whole property? REITs, Real Estate Investment Trusts, let you invest in real estate with as little as ONE HUNDRED DOLLARS. You earn rental income WITHOUT being a landlord.", "img": "reit investment giving real estate exposure affordably"},
            {"text": "Stream #6:\nCAPITAL GAINS\nBuy assets LOW\nsell them HIGH", "speech": "Stream number SIX. CAPITAL GAINS. Buy assets LOW and sell them HIGHER. Stocks, real estate, businesses. The value goes UP over time and when you sell, you POCKET the difference.", "img": "buying low and selling high with profit arrow"},
            {"text": "Long-term capital\ngains are taxed\nat only 15%\nnot 37% income tax", "speech": "Long-term capital gains held over ONE YEAR are taxed at only FIFTEEN PERCENT. Compare that to your regular income tax rate of up to THIRTY SEVEN PERCENT. The tax code REWARDS investors.", "img": "tax comparison showing capital gains advantage"},
            {"text": "Stream #7:\nROYALTY INCOME\nCreate ONCE\nget paid FOREVER", "speech": "Stream number SEVEN. ROYALTY INCOME. Create something ONCE and get paid FOREVER. A book, an online course, music, a YouTube channel, software. ONE effort, LIFETIME earnings.", "img": "creative work generating ongoing royalty payments"},
            {"text": "A $50 online\ncourse selling\n10 copies/day\n= $182,000/year", "speech": "A FIFTY DOLLAR online course selling just TEN copies per day generates ONE HUNDRED EIGHTY TWO THOUSAND DOLLARS per year. You built it ONCE. It sells while you SLEEP.", "img": "online course sales notification pinging overnight"},
            {"text": "You don't need\nall 7 at ONCE\nBuild them ONE\nat a TIME", "speech": "You don't need all SEVEN income streams at ONCE. Build them ONE at a time. Start with your job. Add a side business. Start investing for dividends and interest. Layer them UP.", "img": "building blocks stacking income streams one by one"},
            {"text": "Year 1: Job +\nSide hustle\nYear 2: Add\ninvesting income", "speech": "Year ONE: maximize your job and start a side hustle. Year TWO: start investing for dividend and interest income. Year THREE: explore real estate or royalties. LAYER by LAYER.", "img": "three year timeline adding income streams gradually"},
            {"text": "Year 3: Add\nrental or\nroyalty income\nNow you're\nUNSTOPPABLE", "speech": "By year THREE you have FOUR to FIVE income streams. Lose your job? You still have FOUR others. THAT'S financial security. THAT'S freedom. You become UNSTOPPABLE.", "img": "person with multiple income streams feeling secure"},
            {"text": "The KEY is\nevery extra dollar\ngoes to building\nthe NEXT stream", "speech": "The KEY is every EXTRA DOLLAR from one stream goes to BUILDING the next stream. Side hustle profits buy dividend stocks. Dividend income funds your course creation. It COMPOUNDS.", "img": "income streams feeding into each other growing"},
            {"text": "Most people will\nREAD this and\ndo NOTHING\nDon't be MOST\npeople", "speech": "Most people will watch this and do NOTHING. They'll say interesting and scroll to the next video. Don't be MOST people. Pick ONE stream to start building THIS WEEK.", "img": "person taking action while others scroll past"},
            {"text": "ONE year from now\nyou'll wish you\nstarted TODAY\nSo START TODAY", "speech": "ONE YEAR from now, you will WISH you had started TODAY. So START TODAY. Pick your first extra income stream. Take the first step. Your seven-figure future is waiting.", "img": "future wealthy self looking back thankfully at today"},
        ],
        "keywords": ["Multiple Income", "7 Income Streams", "Passive Income"],
    },
    {
        "title": "Taxes Explained Simply - How to Legally Keep More Money",
        "slides": [
            {"text": "The government\ntakes 20-37% of\nyour money\nBut LEGALLY you\ncan pay LESS", "speech": "The government takes TWENTY to THIRTY SEVEN PERCENT of your money in taxes. But there are LEGAL strategies to keep MORE of what you earn. The rich use ALL of them.", "img": "government taking large percentage of income pie"},
            {"text": "Tax BRACKETS\ndon't work how\nyou THINK\nLet me explain", "speech": "Tax BRACKETS don't work how most people think. This MISUNDERSTANDING costs people THOUSANDS. Let me explain how they ACTUALLY work.", "img": "tax bracket chart with common misconception highlighted"},
            {"text": "You DON'T pay\n32% on ALL income\nif in 32% bracket\nOnly on income\nABOVE the line", "speech": "If you're in the THIRTY TWO percent bracket, you DON'T pay thirty two percent on ALL your income. You only pay thirty two percent on the income ABOVE that bracket's threshold. Everything below is taxed at LOWER rates.", "img": "stacked tax brackets showing marginal rate system"},
            {"text": "First $11,600\ntaxed at 10%\nnot 32%\nEveryone gets this", "speech": "The first ELEVEN THOUSAND SIX HUNDRED of your income is taxed at only TEN PERCENT. EVERYONE gets this low rate on their first chunk of income. Then the next chunk is at TWELVE percent. And so on UP.", "img": "income layers each taxed at different lower rate"},
            {"text": "Strategy #1:\n401K contributions\nreduce taxable\nincome IMMEDIATELY", "speech": "Strategy number ONE. Contribute to your FOUR OH ONE K. Every dollar you contribute reduces your TAXABLE INCOME immediately. Put in twenty thousand, your taxable income DROPS by twenty thousand.", "img": "four oh one k contribution reducing taxable income"},
            {"text": "$23,500 max in 2025\nAt 24% bracket\nthat saves you\n$5,640 in taxes", "speech": "The max contribution is TWENTY THREE THOUSAND FIVE HUNDRED in twenty twenty five. If you're in the TWENTY FOUR percent bracket, that saves you FIVE THOUSAND SIX HUNDRED FORTY in taxes RIGHT NOW.", "img": "tax savings calculation from max retirement contribution"},
            {"text": "Strategy #2:\nSTANDARD DEDUCTION\n$14,600 single\n$29,200 married", "speech": "Strategy number TWO. The STANDARD DEDUCTION. FOURTEEN THOUSAND SIX HUNDRED for single filers. TWENTY NINE THOUSAND TWO HUNDRED for married. This income is TAX FREE. Everyone gets it.", "img": "standard deduction amounts reducing taxable income"},
            {"text": "Strategy #3:\nHSA is the\nTRIPLE TAX FREE\naccount nobody uses", "speech": "Strategy number THREE. The HSA, Health Savings Account. It's the only TRIPLE TAX FREE account in existence. Tax free going IN, tax free GROWTH, and tax free coming OUT for medical expenses.", "img": "hsa account with triple tax advantage highlighted"},
            {"text": "$4,150 single\n$8,300 family\nmax contribution\nINVEST IT in stocks", "speech": "You can contribute FOUR THOUSAND ONE HUNDRED FIFTY as a single or EIGHT THOUSAND THREE HUNDRED as a family. Most people don't know you can INVEST your HSA in stocks for TAX FREE GROWTH.", "img": "hsa investment growing tax free in stock market"},
            {"text": "Strategy #4:\nTax Loss Harvesting\nSell LOSING stocks\nto offset GAINS", "speech": "Strategy number FOUR. TAX LOSS HARVESTING. If you have investments that lost money, SELL THEM to offset your capital gains. This reduces your tax bill on WINNING investments.", "img": "losing stock sold to offset winning stock taxes"},
            {"text": "You can deduct\n$3000 in losses\nagainst regular\nincome EVERY YEAR", "speech": "Even if you have no gains, you can deduct up to THREE THOUSAND DOLLARS in investment losses against your REGULAR INCOME every year. Carry unused losses into FUTURE years.", "img": "three thousand deduction applied against salary income"},
            {"text": "Strategy #5:\nROTH conversions\nin LOW income\nyears save HUGE", "speech": "Strategy number FIVE. ROTH CONVERSIONS during low income years. If you have a year with lower income, convert traditional retirement money to ROTH. Pay taxes now at a LOW rate, never pay again.", "img": "roth conversion in low income year saving taxes"},
            {"text": "Strategy #6:\nCharitable giving\nDonate appreciated\nstock not CASH", "speech": "Strategy number SIX. If you donate to charity, donate APPRECIATED STOCK instead of cash. You get the full deduction AND avoid paying capital gains tax on the growth. DOUBLE benefit.", "img": "donating stock instead of cash for tax advantage"},
            {"text": "Strategy #7:\nLong-term capital\ngains rate is\nonly 0-20%", "speech": "Strategy number SEVEN. Hold investments for MORE than one year to qualify for long-term capital gains rates. ZERO to TWENTY PERCENT instead of your regular income tax rate of up to THIRTY SEVEN.", "img": "holding period calendar crossing one year mark"},
            {"text": "If income under\n$47,025 single\nyour capital gains\ntax is ZERO", "speech": "If your taxable income is under FORTY SEVEN THOUSAND as a single filer, your long-term capital gains tax rate is ZERO PERCENT. You pay NO TAX on your investment profits.", "img": "zero percent capital gains rate for low income investors"},
            {"text": "Strategy #8:\nBusiness deductions\nHome office\ncar and equipment", "speech": "Strategy number EIGHT. If you have a side business, you can deduct your HOME OFFICE, car mileage, equipment, software, and business expenses. These reduce your taxable income SIGNIFICANTLY.", "img": "home office deductions reducing business tax bill"},
            {"text": "The IRS gives\nFREE tax filing\nif income under\n$84,000", "speech": "Don't pay for tax preparation if you don't need to. The IRS offers FREE tax filing through Free File if your income is under EIGHTY FOUR THOUSAND. Save that two hundred dollar filing fee.", "img": "free tax filing options from irs website"},
            {"text": "The wealthy pay\nLESS tax rate\nthan you because\nthey know THE RULES", "speech": "The wealthy don't pay less taxes because they CHEAT. They pay less because they KNOW THE RULES and use EVERY legal strategy available. These SAME strategies are available to YOU.", "img": "tax code book with legal strategies highlighted"},
            {"text": "Biggest mistake:\nNOT adjusting\nW4 withholding\nBig refund = loan\nto government", "speech": "The BIGGEST mistake. Getting a huge tax REFUND and celebrating. A big refund means you gave the government an INTEREST FREE LOAN all year. Adjust your W FOUR so you keep MORE in each paycheck.", "img": "tax refund explained as interest free government loan"},
            {"text": "Every dollar saved\non taxes is a\ndollar that can\nBUILD YOUR WEALTH", "speech": "Every dollar you LEGALLY save on taxes is a dollar that can go into INVESTMENTS building YOUR wealth instead of the government's budget. Learn the rules. PLAY THE GAME. Keep your money.", "img": "tax savings redirected into wealth building investments"},
        ],
        "keywords": ["Tax Strategies", "Save On Taxes", "Tax Planning"],
    },
    {
        "title": "Emergency Fund Masterclass - Your Financial Bulletproof Vest",
        "slides": [
            {"text": "78% of Americans\nlive paycheck\nto paycheck\nONE emergency\naway from disaster", "speech": "SEVENTY EIGHT PERCENT of Americans live paycheck to paycheck. ONE unexpected expense, ONE medical bill, ONE car repair away from COMPLETE FINANCIAL DISASTER.", "img": "person on financial tightrope with no safety net"},
            {"text": "An emergency fund\nis your FINANCIAL\nBULLETPROOF VEST\nNothing gets through", "speech": "An emergency fund is your FINANCIAL BULLETPROOF VEST. Job loss, medical emergency, car breakdown. NOTHING can take you down when you have cash reserves ready.", "img": "shield protecting person from financial emergencies"},
            {"text": "How much?\n3-6 months of\nESSENTIAL expenses\nNot income EXPENSES", "speech": "How much do you need? THREE to SIX months of ESSENTIAL living expenses. Not income. EXPENSES. Rent, food, utilities, insurance. Calculate your BARE MINIMUM monthly cost to survive.", "img": "calculator adding up essential monthly expenses"},
            {"text": "If monthly expenses\nare $3000\nYour target is\n$9,000 to $18,000", "speech": "If your essential monthly expenses are THREE THOUSAND dollars, your target emergency fund is NINE THOUSAND to EIGHTEEN THOUSAND dollars. That's your SAFETY ZONE.", "img": "emergency fund target range nine to eighteen thousand"},
            {"text": "Start with\n$1000 mini fund\nGet there in\n30 days MAX", "speech": "Don't get overwhelmed by the big number. Start with a ONE THOUSAND DOLLAR mini emergency fund. Get there in THIRTY DAYS maximum. Sell stuff, cut subscriptions, skip eating out.", "img": "first one thousand dollar milestone in savings jar"},
            {"text": "Where to keep it?\nHigh Yield Savings\n4-5% APY\nNOT under your\nmattress", "speech": "Where do you keep it? HIGH YIELD SAVINGS account earning FOUR to FIVE PERCENT annually. NOT under your mattress. NOT in a regular savings account earning nothing. Your emergency fund should EARN money.", "img": "high yield savings account earning four percent interest"},
            {"text": "Best HYSA options:\nMarcus, Ally,\nDiscover, Capital One\nAll FREE no fees", "speech": "Best high yield savings accounts right now: Marcus by Goldman Sachs, Ally Bank, Discover, Capital One. ALL completely FREE. No fees. No minimums. Open one in TEN MINUTES.", "img": "top high yield savings account options compared"},
            {"text": "Rule #1:\nThis money is\nfor EMERGENCIES ONLY\nA sale is NOT\nan emergency", "speech": "Rule number ONE. This money is for EMERGENCIES ONLY. A sale at your favorite store is NOT an emergency. A vacation is NOT an emergency. ACTUAL unexpected expenses that threaten your stability.", "img": "emergency definition real emergencies versus wants"},
            {"text": "Real emergencies:\nJob loss\nMedical bills\nCar repairs\nHome repairs", "speech": "Real emergencies include JOB LOSS, unexpected MEDICAL BILLS, essential CAR REPAIRS, and critical HOME REPAIRS. That's IT. Everything else, you save up for SEPARATELY.", "img": "list of real financial emergencies categorized"},
            {"text": "Rule #2:\nAutomate $200-500\nper month to\nyour emergency fund", "speech": "Rule number TWO. AUTOMATE it. Set up an automatic transfer of TWO HUNDRED to FIVE HUNDRED dollars per month to your high yield savings. Treat it like a BILL. Non-negotiable.", "img": "automatic monthly transfer to emergency savings"},
            {"text": "At $300/month\nyou hit $9000\nin just 2.5 years\nThat's LIFE CHANGING", "speech": "At THREE HUNDRED dollars per month, you hit NINE THOUSAND in just TWO AND A HALF YEARS. That's a FULL three-month emergency fund. That level of security is LIFE CHANGING.", "img": "progress bar filling up emergency fund over months"},
            {"text": "Rule #3:\nIf you USE it\nreplenish it\nIMMEDIATELY\nPriority ONE", "speech": "Rule number THREE. If you USE your emergency fund, replenishing it becomes PRIORITY ONE. Pause investing, pause fun spending. Get that safety net back to full as FAST as possible.", "img": "emergency fund being replenished after use priority"},
            {"text": "What if you\ncan't save $300?\nStart with $50\nEvery dollar counts", "speech": "What if you can't save three hundred a month? START WITH FIFTY. Even TWENTY FIVE. It doesn't matter HOW SMALL. What matters is that you START and stay CONSISTENT. Every dollar builds the wall.", "img": "small amounts adding up over time to big savings"},
            {"text": "Cut these NOW:\nSubscriptions $50\nEating out $200\nImpulse buys $100\n= $350 FOUND", "speech": "Cut these RIGHT NOW. Unused subscriptions, FIFTY dollars. Eating out less, TWO HUNDRED. Impulse purchases, ONE HUNDRED. That's THREE HUNDRED FIFTY dollars you just FOUND. Redirect to savings.", "img": "cutting unnecessary expenses freeing up cash"},
            {"text": "Single income?\nAim for 6 months\nDual income?\n3 months minimum", "speech": "SINGLE income household? Aim for SIX months because you have NO backup. DUAL income? THREE months minimum because one person can cover basics if the other loses their job.", "img": "single versus dual income emergency fund targets"},
            {"text": "Self-employed?\nAIM for 9-12\nmonths because\nincome is UNPREDICTABLE", "speech": "Self-employed or freelancer? Aim for NINE to TWELVE MONTHS because your income is UNPREDICTABLE. One dry spell without savings can END your business and force you back to a job.", "img": "freelancer with larger emergency fund for safety"},
            {"text": "Emergency fund\nBEFORE investing\nBEFORE debt payoff\nBEFORE everything", "speech": "Build your emergency fund BEFORE investing. BEFORE aggressive debt payoff. BEFORE everything else. Without this safety net, ONE bad month can undo YEARS of financial progress.", "img": "emergency fund as foundation before everything else"},
            {"text": "People without\nemergency funds\nuse CREDIT CARDS\nmaking crises WORSE", "speech": "People without emergency funds use CREDIT CARDS during crises. Then they owe the emergency cost PLUS twenty five percent interest. The emergency becomes a DEBT SPIRAL that takes YEARS to escape.", "img": "credit card debt spiral from emergency spending"},
            {"text": "With an emergency\nfund you sleep\nBETTER knowing\nnothing can break you", "speech": "With a fully funded emergency fund, you sleep BETTER at night. You negotiate HARDER at work. You take SMARTER risks. Because you know that NOTHING can financially BREAK you.", "img": "person sleeping peacefully with financial security"},
            {"text": "Open a HYSA\nTODAY and set up\nyour first auto\ntransfer RIGHT NOW", "speech": "Open a high yield savings account TODAY. Set up your first automatic transfer RIGHT NOW. Even if it's just fifty dollars. Future you will look back at this moment and say THANK YOU.", "img": "person opening savings account taking first step"},
        ],
        "keywords": ["Emergency Fund", "Financial Safety", "Savings Strategy"],
    },
    {
        "title": "How Inflation Secretly Steals Your Money Every Single Day",
        "slides": [
            {"text": "Your money is\nLOSING value\nRIGHT NOW\nwhile you watch\nthis video", "speech": "Your money is LOSING VALUE right now. While you watch this video, inflation is silently EATING your purchasing power. Every dollar you have is worth LESS tomorrow than it is today.", "img": "dollar bill slowly dissolving and fading away"},
            {"text": "Inflation means\nprices go UP\nand your dollars\nbuy LESS stuff", "speech": "Inflation means prices go UP and each of your dollars buys LESS stuff than before. That grocery bill that used to be two hundred? Now it's two hundred eighty. SAME groceries.", "img": "grocery cart same items but higher price tag"},
            {"text": "$100 in 2000\nonly buys $55\nworth of stuff\ntoday in 2025", "speech": "ONE HUNDRED DOLLARS from the year two thousand only buys FIFTY FIVE DOLLARS worth of stuff today. Your money lost FORTY FIVE PERCENT of its purchasing power in just twenty five years.", "img": "hundred dollar bill shrinking in purchasing power"},
            {"text": "The Federal Reserve\nTARGETS 2% inflation\nper year\nThat's BY DESIGN", "speech": "The Federal Reserve TARGETS two percent inflation per year. This isn't an accident. It's BY DESIGN. They WANT your money to lose value slowly to encourage spending and borrowing.", "img": "federal reserve building with two percent target sign"},
            {"text": "2% sounds small\nbut in 30 years\nyour money loses\n45% of its value", "speech": "Two percent sounds harmless. But over THIRTY YEARS, your money loses FORTY FIVE PERCENT of its value. That million dollar retirement actually has the buying power of FIVE HUNDRED FIFTY THOUSAND.", "img": "thirty year timeline showing money value declining"},
            {"text": "Your bank savings\naccount pays 0.01%\nInflation is 3%\nYou LOSE 2.99%\nper year", "speech": "Your regular bank savings account pays ZERO POINT ZERO ONE PERCENT. Inflation is running at THREE PERCENT. You are LOSING TWO POINT NINE NINE PERCENT per year. Your savings are SHRINKING.", "img": "bank interest versus inflation gap losing money"},
            {"text": "$50,000 in a bank\nloses $1,500 in\npurchasing power\nEVERY YEAR", "speech": "FIFTY THOUSAND DOLLARS sitting in a regular bank account loses FIFTEEN HUNDRED DOLLARS in purchasing power EVERY SINGLE YEAR. Over ten years, that's FIFTEEN THOUSAND DOLLARS of value GONE.", "img": "fifty thousand in bank losing value year after year"},
            {"text": "This is called\nthe INVISIBLE TAX\nYou never see\nit leave but\nit's GONE", "speech": "This is called the INVISIBLE TAX. You never see the money leave your account. The number stays the same. But what it can BUY gets smaller and smaller every single year.", "img": "invisible hand slowly taking value from savings"},
            {"text": "Solution #1:\nInvest in the\nSTOCK MARKET\n10% returns\nBEAT inflation", "speech": "Solution number ONE. Invest in the STOCK MARKET. Historical returns of TEN PERCENT per year CRUSH inflation. After inflation, you're still growing your wealth at SEVEN PERCENT per year.", "img": "stock market returns outpacing inflation line chart"},
            {"text": "Solution #2:\nHigh Yield Savings\n4-5% at least\nKEEPS PACE with\ninflation", "speech": "Solution number TWO. Move your cash to HIGH YIELD SAVINGS earning FOUR to FIVE PERCENT. It won't make you rich but it KEEPS PACE with inflation instead of losing ground.", "img": "high yield savings rate matching inflation rate"},
            {"text": "Solution #3:\nREAL ESTATE\nProperty values\nrise WITH inflation", "speech": "Solution number THREE. REAL ESTATE. Property values typically rise WITH inflation or FASTER. Plus your tenants pay MORE rent as prices go up. Real estate is an INFLATION HEDGE.", "img": "real estate value rising alongside inflation chart"},
            {"text": "Solution #4:\nI-BONDS from\nthe government\nGUARANTEED to\nmatch inflation", "speech": "Solution number FOUR. SERIES I BONDS from the US Treasury. They're GUARANTEED to match inflation. You can buy up to TEN THOUSAND per year. Your money NEVER loses purchasing power.", "img": "series i bond guaranteed to match inflation rate"},
            {"text": "Solution #5:\nInvest in YOURSELF\nHigher skills =\nhigher income that\nOUTRUNS inflation", "speech": "Solution number FIVE. Invest in YOURSELF. Higher skills equal higher income. If your income grows FASTER than inflation, you WIN. This is the most RELIABLE inflation hedge of all.", "img": "person upgrading skills to earn more than inflation"},
            {"text": "What NOT to do:\nKeep large amounts\nof CASH sitting\naround LOSING value", "speech": "What NOT to do. NEVER keep large amounts of cash just sitting in a regular checking or savings account. Anything beyond your emergency fund should be INVESTED and WORKING for you.", "img": "large cash pile with warning sign losing value daily"},
            {"text": "In the 1970s\ninflation hit 14%\nPeople who held\ncash lost HALF\nin 5 years", "speech": "In the nineteen seventies, inflation hit FOURTEEN PERCENT. People who held cash lost nearly HALF their purchasing power in just FIVE YEARS. Those who owned stocks and real estate THRIVED.", "img": "nineteen seventies inflation crisis with fourteen percent"},
            {"text": "Your SALARY needs\nto grow 3%+\nevery year or\nyou're getting a\nPAY CUT", "speech": "Your SALARY needs to grow at LEAST THREE PERCENT every year just to BREAK EVEN with inflation. If you got a two percent raise, congratulations, you actually got a ONE PERCENT PAY CUT.", "img": "raise below inflation is actually a pay cut chart"},
            {"text": "Negotiate raises\nbased on INFLATION\nnot just\nperformance", "speech": "When negotiating raises, bring up INFLATION. Tell your employer that a three percent raise isn't a raise, it's maintaining your current salary. You need ABOVE inflation for a REAL raise.", "img": "employee negotiating raise with inflation data"},
            {"text": "The RICH get richer\nduring inflation\nbecause they own\nASSETS not CASH", "speech": "The RICH get RICHER during inflation because they own ASSETS that rise in value. Stocks, real estate, businesses. The POOR get POORER because they hold CASH that loses value.", "img": "wealthy owning assets versus poor holding cash"},
            {"text": "Every dollar you\ndon't INVEST today\nis worth LESS\ntomorrow", "speech": "Every dollar you DON'T invest today is worth LESS tomorrow. Time plus inflation equals GUARANTEED LOSS on uninvested cash. The clock is TICKING on every dollar in your wallet.", "img": "clock ticking as uninvested cash loses value"},
            {"text": "Beat inflation:\nINVEST don't SAVE\nOwn ASSETS\nnot just currency\nSTART NOW", "speech": "Beat inflation by INVESTING, not just SAVING. Own ASSETS, not just currency. Start NOW because every day you wait, inflation steals MORE. Put your money to WORK. It's the only way to WIN.", "img": "person putting money to work investing against inflation"},
        ],
        "keywords": ["Inflation", "Purchasing Power", "Beat Inflation"],
    },
    {
        "title": "6 Side Hustles That Actually Pay $5000/Month (Tested 2025)",
        "slides": [
            {"text": "Your 9-5 salary\nwill NEVER make\nyou wealthy\nYou need a\nSIDE HUSTLE", "speech": "Your nine to five salary will NEVER make you wealthy on its own. You need a SIDE HUSTLE. An extra income stream that can grow from zero to FIVE THOUSAND dollars per month or MORE.", "img": "person working day job then building side hustle"},
            {"text": "I'm not talking\nabout MLMs or\nget rich schemes\nREAL businesses", "speech": "I'm not talking about pyramid schemes, MLMs, or get rich quick scams. I'm talking about REAL businesses that provide REAL value and generate REAL income. No gimmicks.", "img": "crossing out scams and highlighting real businesses"},
            {"text": "Hustle #1:\nFreelance Writing\n$50-200 per article\nStart TODAY", "speech": "Hustle number ONE. Freelance WRITING. Businesses need blog posts, emails, and web content. Charge FIFTY to TWO HUNDRED per article. Find clients on Upwork, Fiverr, or cold email businesses directly.", "img": "freelance writer working on laptop earning per article"},
            {"text": "Scale to $3000+/mo\nwith just\n3-4 regular clients\nwriting weekly", "speech": "Scale to THREE THOUSAND plus per month with just THREE to FOUR regular clients who need weekly content. That's TWELVE to SIXTEEN articles per month. Very DOABLE part-time.", "img": "freelance income scaling with regular client base"},
            {"text": "Hustle #2:\nSocial Media\nManagement\n$500-2000 per\nclient per month", "speech": "Hustle number TWO. Social media management. Small businesses NEED someone to handle their Instagram, TikTok, and Facebook. Charge FIVE HUNDRED to TWO THOUSAND per client per month.", "img": "social media manager handling multiple business accounts"},
            {"text": "3 clients at\n$1000/month each\n= $3000/month\nfor 1-2 hrs/day", "speech": "THREE clients at ONE THOUSAND per month each equals THREE THOUSAND per month for just ONE to TWO HOURS of work per day. Schedule posts in batches. Work SMART, not hard.", "img": "three clients generating three thousand monthly income"},
            {"text": "Hustle #3:\nOnline Tutoring\n$30-80 per hour\nTeach what you\nALREADY know", "speech": "Hustle number THREE. Online TUTORING. You don't need to be a professor. Teach what you ALREADY know. Math, English, test prep, coding. THIRTY to EIGHTY DOLLARS per hour on platforms like Wyzant.", "img": "online tutor teaching student through video call"},
            {"text": "Hustle #4:\nPrint on Demand\nDesign once\nsell forever\nNO inventory", "speech": "Hustle number FOUR. PRINT ON DEMAND. Design t-shirts, mugs, and posters. Upload to platforms like Redbubble or Merch by Amazon. They print and ship when someone buys. ZERO inventory risk.", "img": "print on demand products being created and shipped"},
            {"text": "One viral design\ncan make $500+\nper month on\nAUTOPILOT", "speech": "ONE viral design can generate FIVE HUNDRED or more per month on complete AUTOPILOT. You designed it ONCE and it sells while you sleep. Some designers have THOUSANDS of designs earning passively.", "img": "single design generating ongoing passive sales"},
            {"text": "Hustle #5:\nBookkeeping\n$40-60 per hour\nSmall businesses\nDESPERATELY need this", "speech": "Hustle number FIVE. BOOKKEEPING for small businesses. Charge FORTY to SIXTY dollars per hour. Small business owners HATE doing their books and will happily PAY someone to handle it.", "img": "bookkeeper organizing small business finances"},
            {"text": "Learn QuickBooks\nin 2 weeks on\nYouTube for FREE\nThen start charging", "speech": "Learn QuickBooks in TWO WEEKS watching FREE YouTube tutorials. Then start offering services to local businesses. There's a MASSIVE shortage of bookkeepers right now.", "img": "learning quickbooks from youtube free tutorials"},
            {"text": "Hustle #6:\nVirtual Assistant\n$20-50 per hour\nManage emails\ncalendars and tasks", "speech": "Hustle number SIX. VIRTUAL ASSISTANT. Twenty to fifty dollars per hour managing emails, calendars, scheduling, and administrative tasks for busy entrepreneurs. Work from ANYWHERE.", "img": "virtual assistant managing tasks from home computer"},
            {"text": "Hustle #7:\nFlipping items\nBuy LOW at thrift\nstores sell HIGH\nonline", "speech": "Hustle number SEVEN. FLIPPING items. Buy things cheap at thrift stores, garage sales, and clearance racks. Sell them for PROFIT on eBay, Facebook Marketplace, or Poshmark.", "img": "thrift store finds being sold for profit online"},
            {"text": "People make\n$2000-5000/month\nflipping furniture\nelectronics and\nvintage items", "speech": "People consistently make TWO THOUSAND to FIVE THOUSAND per month flipping furniture, electronics, vintage items, and brand name clothing. It's a REAL business with REAL money.", "img": "flipped furniture before and after with profit margin"},
            {"text": "Hustle #8:\nYouTube or TikTok\ncreator\nAd revenue +\nsponsors + affiliate", "speech": "Hustle number EIGHT. Content creation on YouTube or TikTok. Ad revenue, sponsorship deals, and affiliate marketing can generate THOUSANDS once you build an audience.", "img": "content creator earning from multiple revenue streams"},
            {"text": "The KEY to\nany side hustle:\nSTART before\nyou're ready\nFigure it out\nas you GO", "speech": "The KEY to any side hustle. START before you feel ready. You will NEVER feel ready. Figure it out AS YOU GO. Your first attempt will be bad. Your tenth will be GOOD. Your hundredth will be GREAT.", "img": "person taking imperfect first step toward side hustle"},
            {"text": "Dedicate 1-2 hours\nBEFORE work or\nAFTER work\nConsistency BEATS\ntalent", "speech": "Dedicate ONE to TWO HOURS before work or after work. Every single day. CONSISTENCY beats talent every time. The people who show up daily WIN over the talented ones who show up randomly.", "img": "daily schedule blocking time for side hustle work"},
            {"text": "Month 1-3:\n$0-500 learning\nMonth 4-6:\n$500-2000 growing\nMonth 7-12:\n$2000-5000 scaling", "speech": "Realistic timeline. Months one through three: zero to five hundred while LEARNING. Months four through six: five hundred to two thousand while GROWING. Months seven through twelve: two to five thousand while SCALING.", "img": "twelve month side hustle income growth timeline"},
            {"text": "Every dollar from\nyour side hustle\ngoes to INVESTING\nnot lifestyle upgrades", "speech": "Every DOLLAR from your side hustle goes straight to INVESTING. Not lifestyle upgrades. Not new clothes. INVESTMENTS. Your side hustle is your WEALTH ACCELERATOR.", "img": "side hustle income flowing directly into investments"},
            {"text": "Pick ONE hustle\nfrom this list\nand START\nthis WEEK\nno excuses", "speech": "Pick ONE hustle from this list and START this WEEK. No excuses. No waiting for the perfect moment. The perfect moment is RIGHT NOW. One year from now you'll have a second income stream changing your LIFE.", "img": "person choosing one hustle and starting immediately"},
        ],
        "keywords": ["Side Hustle", "Extra Income", "Make Money Online"],
    },
    {
        "title": "Retire By 50: The Early Retirement Plan That Actually Works",
        "slides": [
            {"text": "What if you could\nRETIRE in 15 years\ninstead of 40?\nHere's HOW", "speech": "What if you could RETIRE in FIFTEEN YEARS instead of FORTY? What if you never HAD to work again by age FORTY FIVE? This isn't fantasy. Real people do this. Here's EXACTLY how.", "img": "young person retiring early on beach while others work"},
            {"text": "Traditional retirement\nat 65 means working\n40+ YEARS\nThat's INSANE", "speech": "Traditional retirement at SIXTY FIVE means working FORTY PLUS YEARS of your life away. FORTY YEARS of alarm clocks, commutes, and doing what someone else tells you. That's INSANE.", "img": "forty year work timeline stretching into old age"},
            {"text": "The FIRE movement:\nFinancial Independence\nRetire Early\nSave 50-70%\nof income", "speech": "The FIRE movement. Financial Independence Retire Early. The concept is simple. Save FIFTY to SEVENTY percent of your income. Invest aggressively. Retire in TEN to FIFTEEN years.", "img": "fire movement acronym with early retirement path"},
            {"text": "The magic number:\n25x your annual\nexpenses\nThat's your\nretirement target", "speech": "The MAGIC NUMBER. Multiply your annual expenses by TWENTY FIVE. That's your retirement target. If you spend forty thousand per year, you need ONE MILLION DOLLARS invested.", "img": "twenty five times expenses calculation equals freedom"},
            {"text": "Why 25x?\nThe 4% RULE\nWithdraw 4% per year\nand your money\nLASTS forever", "speech": "Why twenty five times? The FOUR PERCENT RULE. Withdraw four percent of your portfolio per year and historically your money LASTS FOREVER. The investments GROW faster than you withdraw.", "img": "four percent withdrawal rate with portfolio lasting"},
            {"text": "$1 million at 4%\n= $40,000 per year\n= $3,333 per month\nFOREVER", "speech": "ONE MILLION DOLLARS at four percent equals FORTY THOUSAND per year. That's THREE THOUSAND THREE HUNDRED THIRTY THREE per month FOREVER. The million stays invested and keeps GROWING.", "img": "million dollar portfolio generating monthly income forever"},
            {"text": "Step 1:\nCut expenses\nDRASTICALLY\nEvery $100 cut\n= $30,000 less\nneeded to retire", "speech": "Step ONE. Cut your expenses DRASTICALLY. Every ONE HUNDRED DOLLARS per month you cut from expenses means you need THIRTY THOUSAND LESS to retire. Small cuts have MASSIVE impact.", "img": "expense cutting reducing retirement number dramatically"},
            {"text": "Step 2:\nMax out 401K\n$23,500 per year\nEmployer match is\nFREE MONEY", "speech": "Step TWO. Max out your FOUR OH ONE K at TWENTY THREE THOUSAND FIVE HUNDRED per year. If your employer matches, that's FREE MONEY. Never leave matching money on the table.", "img": "four oh one k maxed out with employer match stacking"},
            {"text": "Step 3:\nMax out Roth IRA\n$7,000 per year\nTax FREE growth\nand withdrawals", "speech": "Step THREE. Max out your ROTH IRA at SEVEN THOUSAND per year. Tax FREE growth. Tax FREE withdrawals in retirement. This account is your TAX FREE INCOME MACHINE.", "img": "roth ira growing tax free for early retirement"},
            {"text": "Step 4:\nInvest the rest\nin taxable brokerage\naccount\nNO contribution limits", "speech": "Step FOUR. Everything left over goes into a regular TAXABLE BROKERAGE account. No contribution limits. This is your BRIDGE money that gets you from early retirement to age fifty nine and a half.", "img": "taxable brokerage filling gap to retirement accounts"},
            {"text": "All money goes\ninto LOW COST\nindex funds\nVTSAX or VTI\nDON'T overthink it", "speech": "ALL the money goes into LOW COST total market index funds. V T S A X or V T I. Don't overthink it. Don't pick stocks. Don't time the market. Just buy INDEX FUNDS consistently.", "img": "simple index fund investment strategy for retirement"},
            {"text": "Example: $80K income\nSave 50% = $40K/yr\nInvested at 10%\n= $1M in 12 years", "speech": "Example. EIGHTY THOUSAND income. Save FIFTY PERCENT which is FORTY THOUSAND per year. Invested at TEN PERCENT average returns. You hit ONE MILLION in just TWELVE YEARS.", "img": "savings rate calculation reaching million in twelve years"},
            {"text": "The higher your\nsavings RATE the\nFASTER you retire\n70% = 8 years\n80% = 5 years", "speech": "The higher your savings RATE, the FASTER you retire. Save FIFTY percent, retire in about fifteen years. SEVENTY percent, EIGHT years. EIGHTY percent, retire in just FIVE YEARS.", "img": "savings rate chart showing years to retirement"},
            {"text": "But I can't save\n50% on my salary!\nThen INCREASE\nyour income\nside hustles MATTER", "speech": "But you can't save fifty percent on your current salary? Then INCREASE YOUR INCOME. Side hustles MATTER. Every extra dollar earned and invested ACCELERATES your retirement date.", "img": "increasing income with side hustles to boost savings rate"},
            {"text": "Housing is the\nBIGGEST expense\nHouse hack: rent\nrooms or buy duplex", "speech": "Housing is your BIGGEST expense. House HACK it. Rent out spare rooms. Buy a DUPLEX and live in one unit while tenants pay your mortgage. Cut your biggest expense by FIFTY PERCENT or more.", "img": "house hacking duplex with rental income covering mortgage"},
            {"text": "Healthcare in\nearly retirement:\nACA marketplace\nsubsidies if income\nis low enough", "speech": "Worried about healthcare? In early retirement, your OFFICIAL income is low from strategic withdrawals. You qualify for ACA marketplace SUBSIDIES. Health insurance for a fraction of the normal cost.", "img": "aca healthcare marketplace affordable coverage options"},
            {"text": "The HARDEST part\nis not the math\nIt's saying NO to\nlifestyle inflation", "speech": "The HARDEST part of early retirement is not the math. It's saying NO to lifestyle inflation. Your friends upgrade cars. You INVEST. They buy bigger houses. You INVEST. Discipline is EVERYTHING.", "img": "person saying no to upgrades and yes to investing"},
            {"text": "Once you hit\nyour number\nyou NEVER have\nto work for\nmoney AGAIN", "speech": "Once you hit your number, you NEVER have to work for money AGAIN. You can still work if you WANT to. But you work because you CHOOSE to, not because your bills FORCE you to.", "img": "person choosing work they love not forced employment"},
            {"text": "Even if full FIRE\nis too extreme\nsaving 30% gets\nyou to retirement\n10 years EARLY", "speech": "Even if full FIRE is too extreme for you, saving THIRTY PERCENT instead of the typical ten gets you to retirement TEN YEARS early. That's a DECADE of freedom you wouldn't have had.", "img": "moderate savings still reaching retirement decade early"},
            {"text": "Calculate YOUR\nnumber today\n25x annual expenses\nThen BUILD\nyour plan to\nget there", "speech": "Calculate YOUR number today. Twenty five times your annual expenses. Then BUILD your plan to get there. Every month you save and invest brings you closer to FREEDOM. Start RIGHT NOW.", "img": "person calculating their personal retirement number"},
        ],
        "keywords": ["Early Retirement", "FIRE Movement", "Financial Independence"],
    },
    {
        "title": "Buy Your First Property With $0 Down (Real Estate Beginner Guide)",
        "slides": [
            {"text": "90% of millionaires\nbuild wealth through\nREAL ESTATE\nHere's how to START", "speech": "NINETY PERCENT of millionaires built their wealth through REAL ESTATE. Not stocks. Not crypto. Not startups. REAL ESTATE. And you can start with way LESS money than you think.", "img": "millionaire next to real estate properties portfolio"},
            {"text": "Real estate builds\nwealth 4 WAYS\nat the same time\nNo other asset\ndoes this", "speech": "Real estate builds wealth FOUR WAYS simultaneously. No other investment gives you ALL FOUR at once. This is why it creates MORE millionaires than anything else.", "img": "four pillars of real estate wealth building"},
            {"text": "Way #1:\nCASH FLOW\nRent minus expenses\n= money in your\npocket MONTHLY", "speech": "Way number ONE. CASH FLOW. Your tenant pays rent. You subtract mortgage, taxes, insurance, and maintenance. What's LEFT goes in your pocket EVERY SINGLE MONTH.", "img": "rent payments flowing into landlord bank account"},
            {"text": "Way #2:\nAPPRECIATION\nProperty values\ngo UP 3-5%\nper year on average", "speech": "Way number TWO. APPRECIATION. Property values historically increase THREE to FIVE PERCENT per year. A three hundred thousand dollar home becomes FOUR HUNDRED THOUSAND in about eight years.", "img": "home value appreciation chart rising over years"},
            {"text": "Way #3:\nLOAN PAYDOWN\nYour tenant pays\nYOUR mortgage\nYOU build equity", "speech": "Way number THREE. LOAN PAYDOWN. Your TENANT is paying YOUR mortgage every month. Every payment builds YOUR equity. Someone else is literally buying the property FOR YOU.", "img": "tenant rent payments building landlord equity"},
            {"text": "Way #4:\nTAX BENEFITS\nDepreciation and\ndeductions save\nTHOUSANDS per year", "speech": "Way number FOUR. TAX BENEFITS. You can deduct mortgage interest, property taxes, insurance, repairs, and DEPRECIATION. Real estate investors often pay LESS tax than salaried employees.", "img": "tax deductions reducing real estate investor tax bill"},
            {"text": "How much money\ndo you NEED?\n3.5% down with\nFHA loan = $10,500\non $300K property", "speech": "How much money do you actually NEED? With an FHA loan, just THREE AND A HALF PERCENT down. On a three hundred thousand dollar property, that's only TEN THOUSAND FIVE HUNDRED dollars.", "img": "fha loan low down payment on first property"},
            {"text": "Strategy #1:\nHOUSE HACKING\nBuy a duplex\nLive in one unit\nRent the other", "speech": "Strategy number ONE for beginners. HOUSE HACKING. Buy a duplex or triplex. Live in one unit and rent out the others. The rental income covers your mortgage. You live for FREE.", "img": "duplex with owner in one unit tenant in other"},
            {"text": "Your tenant pays\nyour $2000 mortgage\nYou live for FREE\nand BUILD equity", "speech": "Your TENANT pays your two thousand dollar mortgage. You live for FREE and BUILD EQUITY every month. After a year, buy ANOTHER property and repeat. This is how empires start.", "img": "mortgage being paid by tenant while equity grows"},
            {"text": "Strategy #2:\nBRRRR method\nBuy Rehab Rent\nRefinance Repeat", "speech": "Strategy number TWO. The BRRRR method. Buy a undervalued property. REHAB it to increase value. RENT it out. REFINANCE to pull your money back out. REPEAT with the same money.", "img": "brrrr method cycle buy rehab rent refinance repeat"},
            {"text": "Buy for $150K\nRehab for $30K\nNow worth $250K\nRefinance and\npull cash OUT", "speech": "Buy a property for ONE FIFTY. Put THIRTY THOUSAND into renovations. Now it's worth TWO FIFTY. Refinance at eighty percent, pull TWO HUNDRED THOUSAND out. You get your money BACK plus a cash flowing rental.", "img": "property value increasing through rehab and refinance"},
            {"text": "The 1% Rule:\nMonthly rent should\nbe 1% of purchase\nprice minimum", "speech": "The ONE PERCENT RULE for evaluating deals. Monthly rent should be AT LEAST one percent of the purchase price. Three hundred thousand dollar property? Should rent for at least THREE THOUSAND per month.", "img": "one percent rule calculation for rental properties"},
            {"text": "Where to find\ndeals: Zillow\nRealtor.com\nForeclosures\nDriving for dollars", "speech": "Where to find deals. ZILLOW and REALTOR DOT COM for listed properties. FORECLOSURE auctions for deep discounts. DRIVING FOR DOLLARS, looking for distressed properties with motivated sellers.", "img": "property search on multiple platforms and methods"},
            {"text": "GET A GOOD\nreal estate agent\nwho INVESTS\nthemselves\nThey know the game", "speech": "Get a GOOD real estate agent who INVESTS themselves. They understand cash flow, cap rates, and deal analysis. An investor-friendly agent is worth their weight in GOLD.", "img": "investor friendly real estate agent analyzing deals"},
            {"text": "Run the NUMBERS\nbefore you buy\nRent minus ALL\nexpenses must be\nPOSITIVE", "speech": "ALWAYS run the numbers before buying. Rent minus mortgage minus taxes minus insurance minus maintenance minus vacancy must be POSITIVE. If the numbers don't work, WALK AWAY. No emotion.", "img": "spreadsheet analyzing rental property cash flow"},
            {"text": "Budget 1% of\nproperty value\nper year for\nrepairs and\nmaintenance", "speech": "Budget ONE PERCENT of the property value per year for repairs and maintenance. Three hundred thousand dollar property means THREE THOUSAND per year set aside. Things WILL break.", "img": "maintenance budget set aside for property repairs"},
            {"text": "Property management\ncosts 8-10% of rent\nWorth it once you\nhave 3+ properties", "speech": "Property management costs EIGHT to TEN PERCENT of rent. Handle it yourself at first to save money. Once you have THREE or more properties, hire a manager and make it truly PASSIVE.", "img": "property manager handling multiple rental properties"},
            {"text": "One property =\ncash flow\n5 properties =\nfinancial freedom\n10 = WEALTHY", "speech": "ONE property gives you extra cash flow. FIVE properties give you financial FREEDOM. TEN properties make you WEALTHY. Each property is a building block toward your empire.", "img": "real estate portfolio growing from one to ten properties"},
            {"text": "Start by getting\nPRE-APPROVED\nfor a mortgage\nKnow your budget\nBEFORE you shop", "speech": "Start by getting PRE-APPROVED for a mortgage. Know EXACTLY what you can afford before you start shopping. Talk to THREE lenders and compare rates. This costs you NOTHING.", "img": "mortgage pre-approval letter with budget range"},
            {"text": "Your first property\nis the HARDEST\nAfter that each\none gets EASIER\nStart THIS year", "speech": "Your first property is the HARDEST one to buy. After that, each one gets EASIER because you have experience, equity, and cash flow. Start THIS YEAR. Your real estate empire begins with property number ONE.", "img": "first property as foundation of growing real estate empire"},
        ],
        "keywords": ["Real Estate", "Rental Property", "Property Investing"],
    },
    {
        "title": "7 Money Rules That Changed My Life Forever",
        "slides": [
            {"text": "7 money rules\nthat changed\nEVERYTHING for me\nforever", "speech": "These SEVEN money rules changed everything for me. I went from broke to building real wealth. And they will work for YOU too.", "img": "golden rulebook with seven glowing chapters"},
            {"text": "Rule 1:\nPay yourself FIRST\nnot last\nThis is NON\nnegotiable", "speech": "Rule ONE. Pay yourself FIRST. Before rent. Before bills. Before fun. Take twenty percent of every paycheck and INVEST it immediately. This is NON NEGOTIABLE.", "img": "paycheck with first portion going to savings"},
            {"text": "The moment your\npaycheck hits\nmove 20% to\ninvestments\nAUTOMATICALLY", "speech": "Set up AUTOMATIC transfers. The moment your paycheck hits, twenty percent vanishes into your investment account. You never see it. You never miss it. But it GROWS.", "img": "automatic transfer from checking to investing"},
            {"text": "Rule 2:\nNever buy\ndepreciating assets\non credit\nEVER", "speech": "Rule TWO. NEVER buy depreciating assets on credit. Cars, electronics, furniture. If it loses value, pay CASH or don't buy it. Credit cards on depreciating stuff is financial SUICIDE.", "img": "car losing value with credit card interest adding up"},
            {"text": "Your brand new car\nloses 20% value\nthe second you\ndrive off the lot", "speech": "Your brand new car loses TWENTY PERCENT of its value the SECOND you drive off the lot. Twenty percent. GONE. That's not an investment. That's a DONATION to the dealership.", "img": "new car driving off lot with value dropping instantly"},
            {"text": "Rule 3:\nLive on last\nmonth's income\nnot this month's", "speech": "Rule THREE. Live on LAST month's income, not this month's. This creates a one month BUFFER that makes you financially bulletproof. No more paycheck to paycheck.", "img": "calendar showing living one month behind income"},
            {"text": "This one month\nbuffer means you\nNEVER stress about\nmoney again", "speech": "When you live on last month's income, you always know exactly how much you have. No surprises. No stress. No overdrafts. FREEDOM.", "img": "stress-free person with comfortable financial buffer"},
            {"text": "Rule 4:\nEvery dollar needs\na JOB before\nyou spend it", "speech": "Rule FOUR. Every dollar needs a JOB before you spend it. Assign every dollar a purpose. Rent. Food. Investing. Fun. When dollars have jobs, they don't disappear.", "img": "dollars lined up with assigned job titles"},
            {"text": "Unassigned dollars\nget WASTED on\nimpulse purchases\nyou don't need", "speech": "Unassigned dollars get WASTED on things you don't need. That random Amazon purchase. That extra takeout meal. Gone. ASSIGN every dollar a purpose.", "img": "impulse purchases eating unassigned cash"},
            {"text": "Rule 5:\nMultiple income\nstreams or you're\nONE layoff from\nbroke", "speech": "Rule FIVE. Build MULTIPLE income streams. Your job is ONE stream. Add side hustles, investments, rentals. If one stream dies, others keep you alive.", "img": "multiple streams of income flowing into one person"},
            {"text": "The average\nmillionaire has\nSEVEN income streams\nnot one", "speech": "The average millionaire has SEVEN income streams. Not one. SEVEN. That's job income, dividends, rental income, business income, interest, royalties, capital gains.", "img": "seven golden streams flowing into wealth pool"},
            {"text": "Rule 6:\nTrack your\nnet worth monthly\nNot your salary\nNET WORTH", "speech": "Rule SIX. Track your NET WORTH monthly. Not your salary. Your salary is what you EARN. Your net worth is what you KEEP. Assets minus debts. Track it monthly. Watch it grow.", "img": "net worth tracker showing monthly growth"},
            {"text": "Assets minus debts\nequals your real\nfinancial score\nTrack it", "speech": "Assets minus debts. That's your REAL financial score. Not your credit score. Not your salary. Your NET WORTH. This is the number that determines if you're actually wealthy.", "img": "balance sheet showing assets versus debts"},
            {"text": "Rule 7:\nInvest in what\nyou UNDERSTAND\nnever follow\nhype", "speech": "Rule SEVEN. ONLY invest in what you UNDERSTAND. Never follow hype. Never YOLO into crypto because your friend said so. If you can't explain it in one sentence, don't invest.", "img": "person studying investment before buying"},
            {"text": "Warren Buffett has\nNEVER invested in\nsomething he didn't\nunderstand\nFOLLOW HIS LEAD", "speech": "Warren Buffett has NEVER invested in something he didn't understand. He passed on tech stocks for DECADES because he didn't understand them. And he's still worth over ONE HUNDRED BILLION.", "img": "Warren Buffett wisdom about understanding investments"},
            {"text": "BONUS: Teach your\nkids about money\nSchools WON'T do it\nYOU must", "speech": "BONUS RULE. Teach your kids about money. Schools won't do it. The system is designed to keep people financially illiterate. Break the cycle. Teach them YOUNG.", "img": "parent teaching child about saving and investing"},
            {"text": "These 7 rules\nare SIMPLE but\n99% of people\nignore them", "speech": "These seven rules are SIMPLE. But ninety nine percent of people IGNORE them. That's why ninety nine percent of people retire broke. Don't be in that group.", "img": "99 percent ignoring rules versus 1 percent following"},
            {"text": "Pick ONE rule\nimplement it TODAY\nadd another next\nmonth", "speech": "Pick ONE rule. Implement it TODAY. Add another next month. In seven months you'll have ALL SEVEN working for you. Your financial life will be TRANSFORMED.", "img": "step by step implementing rules one by one"},
            {"text": "The difference between\nbroke and wealthy\nis HABITS not\nluck never luck", "speech": "The difference between broke and wealthy is HABITS. Not luck. Not inheritance. Not talent. HABITS. These seven rules ARE those habits. BUILD THEM.", "img": "habits building blocks creating wealth tower"},
            {"text": "SUBSCRIBE for more\nmoney rules\nComment which rule\nyou'll start with\nTODAY", "speech": "SUBSCRIBE to The AI Dollar for more money rules every single day. Comment below which rule you're going to start with TODAY. Share this with someone who needs to hear it. Your wealth journey starts NOW.", "img": "community of people building wealth together"},
        ],
        "keywords": ["Money Rules", "Financial Habits", "Wealth Building"],
    },
    {
        "title": "How To Make Your First $10,000 (Step By Step Blueprint)",
        "slides": [
            {"text": "How to make your\nfirst $10,000\nStep by step\nblueprint", "speech": "How to make your first TEN THOUSAND DOLLARS. Not theory. Not motivation. A step by step BLUEPRINT you can follow starting TODAY.", "img": "ten thousand dollars in cash with blueprint beside it"},
            {"text": "Step 1: Pick a\nhigh-demand skill\nthe market NEEDS\nnot wants NEEDS", "speech": "Step ONE. Pick a HIGH-DEMAND skill that the market NEEDS. Not something cool. Something NEEDED. Writing. Design. Marketing. Coding. Sales.", "img": "high demand skills listed with dollar signs"},
            {"text": "The fastest skills\nto monetize:\nCopywriting\nGraphic Design\nVideo Editing", "speech": "The fastest skills to monetize? COPYWRITING, GRAPHIC DESIGN, and VIDEO EDITING. You can learn basics in 30 days and start earning in 60.", "img": "three fast-to-learn profitable skills"},
            {"text": "Step 2: Learn it\nFREE on YouTube\nfor 30 days\n2 hours per day", "speech": "Step TWO. Learn it FREE on YouTube. Two hours per day for 30 days. That's 60 hours of focused learning. Enough to be DANGEROUS.", "img": "person learning new skill on YouTube laptop"},
            {"text": "Don't buy expensive\ncourses yet\nFree content is\nENOUGH to start", "speech": "Don't buy expensive courses yet. FREE content on YouTube is ENOUGH to start earning. Save courses for when you're already making money and want to level up.", "img": "free vs paid learning path comparison"},
            {"text": "Step 3: Build\n3 portfolio pieces\nEven if they're\nFAKE clients", "speech": "Step THREE. Build THREE portfolio pieces. Create sample work. Make up fake clients if you need to. Nobody cares if your first portfolio is practice work. They care about QUALITY.", "img": "portfolio website with three sample projects"},
            {"text": "Step 4: Sign up\non Fiverr Upwork\nand LinkedIn\nALL three", "speech": "Step FOUR. Sign up on Fiverr, Upwork, AND LinkedIn. ALL THREE. Cast a WIDE net. Your first client can come from anywhere.", "img": "three freelance platforms logos glowing"},
            {"text": "Price your first\ngig at $50-100\nYes that's low\nYou need REVIEWS", "speech": "Price your first gig at FIFTY to ONE HUNDRED dollars. Yes that's low. You need REVIEWS. First three clients are about building your REPUTATION. Money comes AFTER trust.", "img": "first gig pricing strategy for reviews"},
            {"text": "Step 5: Deliver\n10x more value\nthan they paid for\nOVERDELIVER always", "speech": "Step FIVE. OVERDELIVER on every project. Give TEN TIMES more value than they paid for. This gets you five-star reviews AND repeat clients. Reviews are your GROWTH ENGINE.", "img": "five star reviews stacking up from overdelivering"},
            {"text": "After 5 reviews\nRAISE your prices\n$200 then $500\nthen $1000", "speech": "After FIVE solid reviews, RAISE your prices. Two hundred. Then five hundred. Then one thousand per project. Your reviews justify the price increases.", "img": "price ladder climbing with each review milestone"},
            {"text": "Step 6: Cold email\n50 businesses per\nweek offering\nyour service", "speech": "Step SIX. Cold email FIFTY businesses per week offering your service. Not spam. PERSONALIZED emails showing how you can solve THEIR specific problem.", "img": "cold email outreach to fifty businesses weekly"},
            {"text": "Even a 2% response\nrate = 1 new\nclient per week\nThat's $2000/month", "speech": "Even a TWO PERCENT response rate means ONE new client per week. At five hundred per project, that's TWO THOUSAND per month. From just emails.", "img": "email response rate converting to monthly income"},
            {"text": "Step 7: Ask every\nclient for referrals\nThis is FREE\nmarketing", "speech": "Step SEVEN. Ask EVERY happy client for referrals. Do you know anyone else who needs this? This is FREE marketing that converts at INSANE rates.", "img": "referral chain growing from happy clients"},
            {"text": "Referral clients\nconvert 4x better\nthan cold leads\nFree and powerful", "speech": "Referral clients convert FOUR TIMES better than cold leads. They already trust you because someone they trust recommended you. FREE and POWERFUL.", "img": "referral conversion rate versus cold lead"},
            {"text": "Month 1: Learn skill\nMonth 2: First client\nMonth 3: $500-1000\nMonth 6: $3000+", "speech": "Timeline. Month one, learn the skill. Month two, first client. Month three, five hundred to one thousand. Month six, three thousand plus. Month twelve, FIVE THOUSAND or more.", "img": "income timeline growing month by month"},
            {"text": "By month 8-10\nyou hit $10,000\nTOTAL earned\nThat's your first\nmilestone", "speech": "By month EIGHT to TEN, you'll hit TEN THOUSAND DOLLARS TOTAL earned. That's your FIRST milestone. But here's the thing. The skills you built? Those earn forever.", "img": "ten thousand dollar milestone celebration"},
            {"text": "Most people quit\nat month 2\nwhen results are\nslow DON'T QUIT", "speech": "Most people QUIT at month two when results are slow. DON'T QUIT. Month two is the HARDEST. Month three is when momentum kicks in. Push through.", "img": "person pushing through difficulty to success"},
            {"text": "The skill you\nbuilt is now worth\n$50K-100K per year\nFOREVER", "speech": "The skill you built in thirty days is now worth FIFTY to ONE HUNDRED THOUSAND per year FOREVER. That's the real prize. Not the ten thousand. The SKILL.", "img": "skill as lifelong asset generating income"},
            {"text": "Scale it:\nHire helpers\nBuild an agency\n$10K becomes $100K\nper year", "speech": "Scale it. Hire helpers. Build an agency. That ten thousand becomes one hundred thousand per year. Then you hire more people. Then it becomes a BUSINESS that runs without you.", "img": "solo freelancer scaling to agency business"},
            {"text": "Start TODAY\nnot Monday\nnot next month\nTODAY\nPick your skill\nGO", "speech": "Start TODAY. Not Monday. Not next month. TODAY. Pick your skill. Watch one YouTube tutorial. Create one sample. Message one potential client. Your ten thousand dollar journey starts with ONE ACTION. GO.", "img": "person taking first step on path to ten thousand"},
        ],
        "keywords": ["Make Money", "First 10K", "Freelancing"],
    },
    {
        "title": "The Complete Crypto Guide For Beginners (2025 Edition)",
        "slides": [
            {"text": "Crypto explained\nfor COMPLETE\nbeginners\nNo jargon\njust FACTS", "speech": "Cryptocurrency explained for COMPLETE beginners. No confusing jargon. No hype. Just the FACTS you need to understand this technology and whether you should invest.", "img": "bitcoin and ethereum symbols with beginner friendly design"},
            {"text": "What IS crypto?\nDigital money that\nno government or\nbank controls", "speech": "What IS cryptocurrency? It's DIGITAL MONEY that no government or bank controls. It lives on a network of computers called a blockchain. No middlemen. No banks. Just math.", "img": "decentralized network of computers processing transactions"},
            {"text": "Bitcoin was the\nFIRST crypto\ncreated in 2009\nby mystery person\nSatoshi Nakamoto", "speech": "BITCOIN was the first cryptocurrency. Created in 2009 by a mystery person called Satoshi Nakamoto. Nobody knows who they are. The code is open source. Anyone can verify it.", "img": "bitcoin origin story with Satoshi mystery silhouette"},
            {"text": "There are now\nOVER 20,000\ndifferent cryptos\n99% are garbage\n1% might survive", "speech": "There are now OVER twenty thousand different cryptocurrencies. But here's the truth. Ninety nine percent are garbage. Scams. Meme coins. Pump and dumps. Only about ONE percent have real value.", "img": "thousands of crypto coins with most fading away"},
            {"text": "Bitcoin and Ethereum\nare the TWO\nyou should know\nEverything else\nis RISKY", "speech": "BITCOIN and ETHEREUM are the two you need to know. Bitcoin is digital gold. Ethereum is the platform that runs decentralized apps. Everything else is EXTREMELY risky.", "img": "bitcoin and ethereum as two pillars of crypto"},
            {"text": "Bitcoin: Digital gold\nStore of value\nOnly 21 million\nwill EVER exist\nScarce", "speech": "Bitcoin is DIGITAL GOLD. A store of value. Only TWENTY ONE MILLION will ever exist. That scarcity is what gives it value. You can't print more. Ever.", "img": "bitcoin as digital gold with limited supply counter"},
            {"text": "Ethereum: Digital\ncomputer\nRuns apps and\ncontracts without\nmiddlemen", "speech": "Ethereum is like a DIGITAL COMPUTER that the whole world shares. It runs applications and contracts without middlemen. DeFi, NFTs, and smart contracts all run on Ethereum.", "img": "ethereum running decentralized applications"},
            {"text": "How to buy:\nCoinbase or Kraken\nSign up verify ID\nDeposit dollars\nBuy crypto", "speech": "How to buy. Sign up on COINBASE or KRAKEN. Verify your identity. Deposit dollars from your bank. Buy Bitcoin or Ethereum. Takes about ten minutes.", "img": "step by step buying crypto on exchange"},
            {"text": "NEVER invest more\nthan you can\nafford to LOSE\nCrypto can drop\n80% overnight", "speech": "CRITICAL RULE. NEVER invest more than you can afford to LOSE completely. Crypto can drop EIGHTY PERCENT overnight. This is NOT a savings account. This is SPECULATION.", "img": "crypto volatility chart showing massive drops"},
            {"text": "The 5% rule:\nOnly put 5%\nof your portfolio\nin crypto\nmax 10%", "speech": "The FIVE PERCENT RULE. Only put five percent of your total investment portfolio in crypto. Maximum ten percent. The other ninety percent should be in stocks, bonds, and real assets.", "img": "portfolio pie chart with crypto as small slice"},
            {"text": "Dollar cost average\nBuy small amounts\nweekly or monthly\nDon't go all in", "speech": "DOLLAR COST AVERAGE. Buy small amounts weekly or monthly. Don't go ALL IN at once. This smooths out the wild price swings and reduces your risk.", "img": "dollar cost averaging into crypto over time"},
            {"text": "NEVER store crypto\non an exchange\nMove it to a\nhardware wallet\nYOUR keys YOUR coins", "speech": "NEVER store large amounts on an exchange. Exchanges get HACKED. Move your crypto to a hardware wallet like Ledger or Trezor. YOUR keys, YOUR coins. Not your keys, NOT your coins.", "img": "hardware wallet securing crypto versus exchange hack"},
            {"text": "Common SCAMS:\nAnyone promising\nguaranteed returns\nis LYING to you", "speech": "Common SCAMS. Anyone promising GUARANTEED returns in crypto is LYING. Anyone asking you to send crypto to double it is a SCAMMER. There are no guaranteed returns. EVER.", "img": "scam warning signs in crypto space"},
            {"text": "Never share your\nseed phrase or\nprivate keys\nwith ANYONE\nNot even support", "speech": "NEVER share your seed phrase or private keys with ANYONE. Not customer support. Not your friend. Not someone on Twitter. NOBODY. If they have your keys, they have your money.", "img": "seed phrase protection locked in vault"},
            {"text": "Crypto taxes:\nYES you owe taxes\non gains\nTrack EVERYTHING\nuse CoinTracker", "speech": "Yes, you OWE TAXES on crypto gains. The IRS treats it as property. Track EVERYTHING. Use CoinTracker or similar tools. Report your gains. Don't mess with the IRS.", "img": "crypto tax reporting requirements"},
            {"text": "Crypto is NOT\na get rich quick\nscheme\nIt's a long term\nspeculative bet", "speech": "Cryptocurrency is NOT a get rich quick scheme. It's a long-term SPECULATIVE bet on future technology. Some people made millions. Many more lost everything. Be SMART about it.", "img": "long term perspective on crypto investment"},
            {"text": "My honest opinion:\nBitcoin has VALUE\nas digital gold\nMost altcoins will\ngo to ZERO", "speech": "My honest opinion. Bitcoin has REAL value as digital gold and a hedge against monetary policy. Most altcoins will eventually go to ZERO. Be extremely selective.", "img": "bitcoin surviving while altcoins fade away"},
            {"text": "If you invest:\nBitcoin 70%\nEthereum 20%\nEverything else 10%\nmax", "speech": "If you decide to invest in crypto, split it. Seventy percent Bitcoin. Twenty percent Ethereum. Ten percent maximum in everything else combined. This is the safest approach.", "img": "crypto allocation strategy pie chart"},
            {"text": "Remember:\nStocks bonds and\nreal estate should\nbe your CORE\nCrypto is a\nSATELLITE", "speech": "Remember. Stocks, bonds, and real estate should be your CORE portfolio. Crypto is a SATELLITE position. A small speculative bet. Not your retirement plan.", "img": "core portfolio with crypto as small addition"},
            {"text": "Educate yourself\nbefore investing\nDon't follow hype\nFollow FUNDAMENTALS\nand facts", "speech": "EDUCATE yourself before investing a single dollar. Don't follow hype. Don't follow influencers. Follow FUNDAMENTALS and facts. Subscribe for more financial education every day.", "img": "education and research before crypto investing"},
        ],
        "keywords": ["Cryptocurrency", "Bitcoin", "Ethereum", "Crypto Investing"],
    },
    {
        "title": "10 Habits That Keep You Poor (Stop These NOW)",
        "slides": [
            {"text": "10 habits that\nare keeping you\nPOOR right now\nStop them TODAY", "speech": "TEN habits that are keeping you POOR right now. Most people do ALL of these without realizing it. Stop them TODAY and watch your finances transform.", "img": "chain of bad habits keeping person poor"},
            {"text": "Habit 1:\nBuying stuff to\nimpress people you\ndon't even LIKE", "speech": "Habit ONE. Buying stuff to impress people you don't even LIKE. That designer bag. That fancy car. That expensive dinner. All to show off to people who DON'T CARE about you.", "img": "luxury items bought to impress strangers"},
            {"text": "The rich don't\nflex with stuff\nThey flex with\nFREEDOM and TIME", "speech": "The truly rich don't flex with STUFF. They flex with FREEDOM and TIME. They drive regular cars. They wear simple clothes. But they can retire WHENEVER THEY WANT.", "img": "wealthy person enjoying freedom and time"},
            {"text": "Habit 2:\nSubscriptions you\nforgot about\n$50-200 per month\nWASTED", "speech": "Habit TWO. Subscriptions you FORGOT about. Check your bank statement RIGHT NOW. I guarantee you're paying for things you haven't used in MONTHS. Fifty to two hundred wasted every month.", "img": "bank statement full of forgotten subscriptions"},
            {"text": "Habit 3:\nEating out 5x\nper week\n$15 per meal\n= $300 per month\nGONE", "speech": "Habit THREE. Eating out five times per week. Fifteen dollars per meal. That's THREE HUNDRED per month. Three THOUSAND six hundred per year. Invested that would be FIFTY THOUSAND in ten years.", "img": "restaurant spending versus cooking at home"},
            {"text": "Habit 4:\nNot negotiating\nyour salary\nLeaving $5K-20K\non the table\nEVERY YEAR", "speech": "Habit FOUR. Not negotiating your salary. You're leaving FIVE to TWENTY THOUSAND dollars on the table EVERY YEAR. Companies EXPECT negotiation. They budget for it. ASK.", "img": "money left on table from not negotiating"},
            {"text": "Habit 5:\nPaying only minimum\non credit cards\n$5000 debt becomes\n$15000", "speech": "Habit FIVE. Paying only the MINIMUM on credit cards. That five thousand dollar balance? At minimum payments and twenty five percent interest, you'll pay FIFTEEN THOUSAND before it's gone.", "img": "minimum payment trap growing debt exponentially"},
            {"text": "Habit 6:\nNo budget\nNo plan\nJust spend and\nhope for the best\nThat's GAMBLING", "speech": "Habit SIX. No budget. No financial plan. Just spend and HOPE there's money left at the end of the month. That's not a strategy. That's GAMBLING with your future.", "img": "gambling with finances hoping money lasts"},
            {"text": "Habit 7:\nKeeping up with\nthe Joneses\nThe Joneses are\nBROKE", "speech": "Habit SEVEN. Keeping up with the Joneses. Fun fact. The Joneses are BROKE. They're in debt up to their eyeballs trying to keep up with someone ELSE. It's a TRAP.", "img": "neighbors competing in debt for appearances"},
            {"text": "Habit 8:\nNot investing\nbecause you think\nyou need $10K\nto start\nYou need $50", "speech": "Habit EIGHT. Not investing because you think you need TEN THOUSAND dollars to start. You DON'T. You need FIFTY. Apps like Fidelity let you start with basically NOTHING.", "img": "small amount growing into big investment"},
            {"text": "Habit 9:\nBlaming the economy\nyour boss your\nparents instead of\ntaking ACTION", "speech": "Habit NINE. Blaming everything EXCEPT yourself. The economy. Your boss. Your parents. Your background. Blaming keeps you STUCK. Taking ACTION moves you FORWARD.", "img": "person breaking free from blame cycle"},
            {"text": "Habit 10:\nWaiting for the\nPERFECT time\nto start\nThere IS no\nperfect time", "speech": "Habit TEN. Waiting for the PERFECT time. The perfect time to invest was TEN YEARS AGO. The second best time is RIGHT NOW. There is no perfect moment. JUST START.", "img": "clock showing now is the perfect time"},
            {"text": "These habits\ncost the average\nperson $500K+\nover their lifetime", "speech": "These ten habits cost the average person over FIVE HUNDRED THOUSAND DOLLARS over their lifetime. Half a million. GONE. To habits you can change TODAY.", "img": "lifetime cost of bad financial habits"},
            {"text": "Replace bad habits\nwith WEALTH habits:\nBudget Track Invest\nRepeat forever", "speech": "Replace bad habits with WEALTH habits. Budget. Track spending. Invest consistently. Learn about money. Repeat FOREVER. That's the formula.", "img": "replacing bad habits with wealth building habits"},
            {"text": "The rich automate\ntheir wealth habits\nAuto-invest\nAuto-save\nAuto-budget", "speech": "The rich AUTOMATE their wealth habits. Automatic investments. Automatic savings. Automatic bill payments. Remove willpower from the equation. Let SYSTEMS build your wealth.", "img": "automated systems building wealth passively"},
            {"text": "Warren Buffett reads\n5 hours per day\nBill Gates reads\n1 book per week\nEducation matters", "speech": "Warren Buffett reads FIVE HOURS per day. Bill Gates reads one book per week. The richest people on earth NEVER stop learning. Education about money is your most valuable investment.", "img": "successful people reading and learning about money"},
            {"text": "Challenge:\nPick THREE habits\nfrom this list\nEliminate them\nfor 30 days", "speech": "Here's your CHALLENGE. Pick THREE habits from this list. Eliminate them for THIRTY DAYS. Track how much money you save. I GUARANTEE it will shock you.", "img": "thirty day challenge to eliminate bad habits"},
            {"text": "30 days of better\nhabits = $500-1000\nsaved per month\nThat changes your\nLIFE", "speech": "Thirty days of better habits equals FIVE HUNDRED to ONE THOUSAND dollars saved per month. That's six to twelve thousand per year. INVESTED, that becomes ONE HUNDRED THOUSAND in ten years.", "img": "thirty day savings transforming into wealth"},
            {"text": "Your financial future\nis decided by\nyour DAILY HABITS\nnot your salary", "speech": "Your financial future is decided by your DAILY HABITS. Not your salary. People earning two hundred thousand go broke. People earning fifty thousand build wealth. The difference is HABITS.", "img": "daily habits determining financial destiny"},
            {"text": "SUBSCRIBE for daily\nfinance tips\nComment which habit\nyou'll BREAK today\nLet's GO", "speech": "SUBSCRIBE to The AI Dollar for daily finance education. Comment below which habit you're going to BREAK today. Share this with a friend who needs to hear this. Let's build WEALTH together.", "img": "community building wealth with better habits"},
        ],
        "keywords": ["Bad Habits", "Financial Mistakes", "Wealth Building"],
    },
    {
        "title": "ETFs Explained: Build A $500K Portfolio With Zero Effort",
        "slides": [
            {"text": "ETFs explained\nBuild a $500K\nportfolio with\nZERO effort", "speech": "ETFs. The SIMPLEST way to build a FIVE HUNDRED THOUSAND dollar portfolio with ZERO effort. This is how lazy investors get RICH.", "img": "ETF portfolio growing automatically to 500K"},
            {"text": "ETF stands for\nExchange Traded Fund\nIt's a basket of\nstocks in ONE\npurchase", "speech": "ETF stands for Exchange Traded Fund. It's a BASKET of stocks you can buy in ONE single purchase. Instead of buying Apple AND Amazon AND Google separately, you buy ONE ETF that holds ALL of them.", "img": "basket of stocks combined into one ETF"},
            {"text": "Think of it like\na variety pack\nof investments\nInstant diversity\nless risk", "speech": "Think of it like a variety pack. Instead of betting on ONE company, you bet on HUNDREDS. If one fails, the others carry you. INSTANT diversification.", "img": "variety pack of investments reducing risk"},
            {"text": "The most popular\nETF: VOO\nTracks the S&P 500\n500 biggest US\ncompanies", "speech": "The most popular ETF is VOO from Vanguard. It tracks the S and P Five Hundred. The FIVE HUNDRED biggest US companies. Apple. Amazon. Google. Microsoft. All of them in ONE fund.", "img": "VOO ETF containing top 500 companies"},
            {"text": "VOO costs just\n0.03% per year\nThat's 30 cents\nper $1000 invested\nALMOST FREE", "speech": "VOO costs just ZERO POINT ZERO THREE percent per year. That's THIRTY CENTS for every THOUSAND dollars invested. ALMOST FREE. Compare that to financial advisors charging ONE to TWO percent.", "img": "VOO ultra low cost versus advisor fees"},
            {"text": "Other great ETFs:\nVTI total market\nVXUS international\nBND bonds", "speech": "Other great ETFs. VTI gives you the TOTAL US stock market. VXUS gives you international stocks. BND gives you bonds. With just THREE ETFs you own the entire WORLD economy.", "img": "three ETFs covering global economy"},
            {"text": "The 3-fund\nportfolio strategy:\n60% VTI\n30% VXUS\n10% BND\nDONE", "speech": "The three fund portfolio. SIXTY percent VTI. THIRTY percent VXUS. TEN percent BND. That's it. You're DONE. This portfolio has beaten NINETY percent of professional fund managers.", "img": "three fund portfolio allocation pie chart"},
            {"text": "This beats 90%\nof professional\nfund managers\nSeriously. NINETY\nPERCENT", "speech": "I'm not exaggerating. This simple three fund portfolio beats NINETY PERCENT of professional fund managers who charge thousands in fees. SIMPLICITY WINS.", "img": "ETF portfolio beating professional fund managers"},
            {"text": "How to start:\nOpen account at\nFidelity or Vanguard\nTakes 5 minutes\nFREE", "speech": "How to start. Open a FREE account at Fidelity or Vanguard. Takes five minutes. No minimum balance required. Deposit as little as ONE dollar.", "img": "opening brokerage account on phone quickly"},
            {"text": "Buy $50 of VOO\nevery single week\nSet it on\nAUTOPILOT\nforget about it", "speech": "Buy FIFTY dollars of VOO every single week. Set it on AUTOPILOT. Then FORGET about it. Don't check it daily. Don't panic when it drops. Just keep buying.", "img": "automatic weekly purchase of VOO ETF"},
            {"text": "$50 per week\n= $2600 per year\nIn 30 years at 10%\n= $471,000", "speech": "FIFTY dollars per week is twenty six hundred per year. At ten percent average returns over thirty years, that grows to FOUR HUNDRED SEVENTY ONE THOUSAND DOLLARS. From fifty bucks a week.", "img": "fifty weekly growing to 471K in thirty years"},
            {"text": "Increase to $100\nper week?\n$942,000 in 30 years\nAlmost a MILLION", "speech": "Increase to ONE HUNDRED per week? NINE HUNDRED FORTY TWO THOUSAND in thirty years. Almost a MILLION DOLLARS. From a hundred bucks a week.", "img": "doubling contribution approaching million dollars"},
            {"text": "The KEY is\nCONSISTENCY\nNot timing\nNot picking stocks\nJust KEEP BUYING", "speech": "The KEY is CONSISTENCY. Not timing the market. Not picking individual stocks. Not reading charts. Just KEEP BUYING. Week after week. Month after month. CONSISTENCY wins.", "img": "consistent buying through market ups and downs"},
            {"text": "When the market\nDROPS don't panic\nYou're buying\nstocks ON SALE\nCelebrate dips", "speech": "When the market DROPS, don't panic. You're buying stocks ON SALE. Lower prices mean MORE shares for the same money. CELEBRATE dips. They make you RICHER long term.", "img": "market dip as buying opportunity celebration"},
            {"text": "Time IN the market\nbeats timing\nTHE market\nEvery single time\nProven by data", "speech": "Time IN the market beats timing THE market. Every single time. This is proven by DECADES of data. The best investors are the ones who STAYED IN longest.", "img": "time in market versus timing comparison"},
            {"text": "Mistakes to avoid:\nDon't day trade\nDon't follow hype\nDon't panic sell\nDon't check daily", "speech": "Mistakes to AVOID. Don't day trade. Don't follow hype. Don't panic sell during crashes. Don't check your portfolio every day. Set it and FORGET it.", "img": "common mistakes to avoid with ETF investing"},
            {"text": "ETFs vs mutual funds:\nETFs are CHEAPER\ntrade like stocks\nmore tax efficient", "speech": "ETFs versus mutual funds. ETFs are CHEAPER. They trade like stocks throughout the day. They're more TAX EFFICIENT. In almost every way, ETFs are BETTER for individual investors.", "img": "ETF advantages over mutual funds comparison"},
            {"text": "At retirement:\n$500K portfolio\npaying 4% per year\n= $20K passive\nincome FOREVER", "speech": "At retirement, your five hundred thousand dollar portfolio can pay you FOUR PERCENT per year. That's TWENTY THOUSAND dollars of passive income FOREVER while your principal stays intact.", "img": "retirement income from ETF portfolio forever"},
            {"text": "Add Social Security\nplus portfolio income\n= comfortable\nretirement WITHOUT\nworrying about money", "speech": "Add Social Security on top of your portfolio income and you have a COMFORTABLE retirement without EVER worrying about money again. This is FINANCIAL FREEDOM.", "img": "comfortable retirement with multiple income sources"},
            {"text": "Start THIS WEEK\nOpen account Monday\nBuy first ETF\nTuesday\nYour future self\nwill THANK you", "speech": "Start THIS WEEK. Open an account Monday. Buy your first ETF Tuesday. Your future self will THANK YOU for this decision. This is the most important financial step you'll ever take. DO IT NOW.", "img": "calendar with action steps for this week"},
        ],
        "keywords": ["ETF", "Index Fund", "Portfolio", "Investing"],
    },
    {
        "title": "Financial Freedom By 40 (The FIRE Movement Explained)",
        "slides": [
            {"text": "Retire by 40?\nThe FIRE movement\nexplained\nIt's REAL and\npeople DO it", "speech": "Retire by FORTY? It's not a fantasy. The FIRE movement is REAL and thousands of people are doing it RIGHT NOW. Financial Independence Retire Early. Let me show you HOW.", "img": "young person retiring at 40 on beach"},
            {"text": "FIRE stands for\nFinancial Independence\nRetire Early\nSave 50-70% of\nyour income", "speech": "FIRE stands for Financial Independence Retire Early. The core idea? Save FIFTY to SEVENTY percent of your income instead of the normal ten to twenty percent. Live lean now, retire DECADES early.", "img": "FIRE acronym with savings rate highlighted"},
            {"text": "The math is\nshockingly simple:\nSave 50% = retire\nin 17 years\nSave 70% = 8.5 years", "speech": "The math is SHOCKINGLY simple. If you save FIFTY percent of your income, you can retire in seventeen years. Save SEVENTY percent? EIGHT AND A HALF years. The math doesn't lie.", "img": "savings rate versus years to retirement chart"},
            {"text": "The 25x rule:\nYou need 25 times\nyour yearly expenses\nsaved to retire", "speech": "The TWENTY FIVE TIMES rule. You need twenty five times your yearly expenses saved and invested to retire. If you spend forty thousand per year, you need ONE MILLION invested.", "img": "25x rule calculation for retirement"},
            {"text": "The 4% rule:\nWithdraw 4% per\nyear from your\nportfolio\nIt lasts FOREVER", "speech": "The FOUR PERCENT rule. Once you hit your number, withdraw four percent per year. Studies show your money lasts THIRTY PLUS years. Basically FOREVER if invested properly.", "img": "4 percent withdrawal sustaining retirement"},
            {"text": "Step 1:\nTrack EVERY expense\nEliminate the waste\nFind your real\ncost of living", "speech": "Step ONE. Track EVERY expense for three months. Find your REAL cost of living. Most people are SHOCKED at how much they waste. Eliminate the fat.", "img": "expense tracking revealing waste"},
            {"text": "Step 2:\nIncrease income\nSide hustles raises\njob hopping\nEvery dollar counts", "speech": "Step TWO. INCREASE your income aggressively. Side hustles. Negotiate raises. Job hop for bigger salary. In FIRE, every extra dollar is MORE fuel for early retirement.", "img": "multiple income sources accelerating FIRE"},
            {"text": "Step 3:\nInvest EVERYTHING\nextra into\nlow-cost index funds\nVOO VTI VXUS", "speech": "Step THREE. Invest EVERYTHING extra into low-cost index funds. VOO, VTI, VXUS. Automatic weekly purchases. Don't try to pick stocks. Don't try to time markets. Just INVEST consistently.", "img": "consistent investing into index funds"},
            {"text": "Housing hack:\nHouse hack your\nfirst property\nRoommates pay YOUR\nmortgage", "speech": "Housing HACK. Buy a property. Live in one room. Rent out the others. Your roommates PAY your mortgage. Your housing cost drops to nearly ZERO. This alone can save you HUNDREDS OF THOUSANDS.", "img": "house hacking roommates paying mortgage"},
            {"text": "Transportation hack:\nDrive a reliable\nused car\nSave $500 per\nmonth instantly", "speech": "Transportation HACK. Drive a reliable used car. Not a new BMW. A reliable Honda or Toyota. Save FIVE HUNDRED per month on car payments alone.", "img": "used reliable car versus expensive new car"},
            {"text": "Food hack:\nMeal prep Sundays\n$200 per month\ninstead of $600\nSaves $4800 yearly", "speech": "Food HACK. Meal prep on Sundays. Cook in bulk. Eat leftovers. Your food bill drops from six hundred to TWO HUNDRED per month. That's FORTY EIGHT HUNDRED dollars saved per year.", "img": "meal prep saving thousands per year"},
            {"text": "Example:\n$60K salary\nSave $30K per year\nInvest at 10%\nFIRE in 15 years", "speech": "Real example. Sixty thousand salary. Save THIRTY THOUSAND per year. Invest at ten percent returns. You hit FINANCIAL INDEPENDENCE in FIFTEEN YEARS. That's retiring at FORTY if you start at twenty five.", "img": "real example path to FIRE at 40"},
            {"text": "Your FIRE number:\nMonthly expenses\nx 12 x 25\nThat's your\nFREEDOM number", "speech": "Calculate YOUR FIRE number. Monthly expenses times twelve times twenty five. If you spend three thousand per month, your FIRE number is NINE HUNDRED THOUSAND. That's your FREEDOM number.", "img": "calculating personal FIRE number"},
            {"text": "Lean FIRE:\nMinimalist lifestyle\n$600K-800K needed\nSimple but FREE", "speech": "There's LEAN FIRE. Minimalist lifestyle. You need about six to eight hundred thousand. Simple living but complete FREEDOM.", "img": "lean fire minimalist lifestyle"},
            {"text": "Fat FIRE:\nLuxury lifestyle\n$2M-3M needed\nRetire in STYLE", "speech": "And there's FAT FIRE. Luxury lifestyle in retirement. You need two to three million. Takes longer but you retire in STYLE.", "img": "fat fire luxury retirement lifestyle"},
            {"text": "Coast FIRE:\nSave aggressively\nearly then STOP\nLet compound interest\nfinish the job", "speech": "And COAST FIRE. Save aggressively in your twenties and thirties. Then STOP saving and just let compound interest finish the job. You coast to retirement.", "img": "coast fire letting investments grow passively"},
            {"text": "The hardest part?\nNot the saving\nIt's ignoring what\nEVERYONE else\nis doing", "speech": "The hardest part isn't the saving. It's ignoring what everyone ELSE is doing. While they buy new cars and designer clothes, you're building your FREEDOM MACHINE.", "img": "ignoring social pressure to spend"},
            {"text": "But when you're\n40 and RETIRED\nand they're working\ntill 65\nWho wins?", "speech": "But when you're FORTY and RETIRED. Traveling. Pursuing passions. Living life on YOUR terms. And they're working until SIXTY FIVE. WHO WINS? You know the answer.", "img": "retired at 40 versus working until 65"},
            {"text": "You don't have\nto go extreme\nEven saving 30-40%\ngets you retired\nby 50-55", "speech": "You don't have to go extreme. Even saving THIRTY to FORTY percent gets you retired by FIFTY to FIFTY FIVE. That's still TEN to FIFTEEN years early. That's TEN to FIFTEEN years of FREEDOM.", "img": "moderate FIRE path retiring 10-15 years early"},
            {"text": "Start calculating\nyour FIRE number\nTODAY\nEvery dollar saved\nis a step toward\nFREEDOM", "speech": "Start calculating your FIRE number TODAY. Every dollar saved is a step toward FREEDOM. Subscribe for more financial education every day. Comment your FIRE number below. Let's build FREEDOM together.", "img": "community building toward financial freedom"},
        ],
        "keywords": ["FIRE Movement", "Early Retirement", "Financial Independence"],
    },
]


def enhance_image(img_path, landscape=False):
    """Bring a generated image up to frame size and sharpen it.

    Scales to COVER the target and centre-crops the overflow. The previous
    version resized straight to the target dimensions, which stretched any
    source that wasn't already 9:16 — a square 1024x1024 render pulled to
    1080x1920 is squashed almost 2x horizontally, which on its own reads as
    'melted'. Generators return square or near-square images often enough
    that cropping rather than stretching is the only safe fit."""
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        img = Image.open(img_path).convert("RGB")
        w, h = img.size
        target_w, target_h = (1920, 1080) if landscape else (1080, 1920)

        scale = max(target_w / w, target_h / h)
        new_w, new_h = max(target_w, int(round(w * scale))), max(target_h, int(round(h * scale)))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left, top = (new_w - target_w) // 2, (new_h - target_h) // 2
        img = img.crop((left, top, left + target_w, top + target_h))

        # Sharpen in proportion to how much we had to enlarge: an image that
        # was already near frame size only needs a light pass, while a small
        # source upscaled 2x needs a strong one to stop looking soft.
        percent = 120 if scale <= 1.2 else (165 if scale <= 1.8 else 200)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=percent,
                                                 threshold=3))
        img = ImageEnhance.Contrast(img).enhance(1.12)
        img = ImageEnhance.Color(img).enhance(1.08)
        img = ImageEnhance.Sharpness(img).enhance(1.15)
        img.save(img_path, "JPEG", quality=95)
    except Exception as e:
        print(f"  [WARN] Image enhance failed: {e}")


def _extract_search_keywords(desc, text=""):
    """Pull search keywords from slide TEXT first, then img desc as fallback."""
    stop = {'a', 'an', 'the', 'of', 'on', 'in', 'at', 'to', 'and', 'or',
            'with', 'its', 'from', 'into', 'for', 'by', 'is', 'are', 'was',
            'being', 'their', 'that', 'this', 'no', 'not', 'showing',
            'looking', 'getting', 'labeled', 'versus', 'vs', 'next',
            'glowing', 'dramatic', 'golden', 'massive', 'tiny', 'large',
            'behind', 'beside', 'above', 'below', 'under', 'over',
            'dark', 'bright', 'single', 'each', 'every', 'slowly',
            'against', 'through', 'between', 'along', 'across', 'displayed',
            'floating', 'shooting', 'person', 'moment', 'reaction',
            'watch', 'follow', 'comment', 'subscribe', 'share',
            'ever', 'never', 'just', 'your', 'you', 'did', 'don',
            'why', 'how', 'what', 'when', 'who', 'which', 'step',
            'rule', 'tip', 'try', 'hit', 'now', 'today', 'right',
            'still', 'til', 'end', 'new', 'daily', 'tips', 'more'}

    combined = (text + ' ' + desc).lower().replace('\n', ' ').replace(',', ' ')
    combined = combined.replace('$', '').replace('#', '').replace('%', ' percent ')
    words = combined.split()
    good = [w for w in words if w not in stop and len(w) > 2 and w.isalpha()]

    seen = set()
    result = []
    for w in good:
        if w not in seen:
            seen.add(w)
            result.append(w)

    kw = ' '.join(result[:4]) if result else ''
    return f"business finance {kw}".strip() if kw else 'business finance money professional'


# Well-known finance/business figures the AI is allowed to reference by
# name. Fetched from Wikipedia, which only hosts openly-licensed
# (public domain / Creative Commons) images — much lower legal risk than
# pulling a random photo of a real person from general web search.
WELL_KNOWN_FIGURES = {
    "warren buffett", "jerome powell", "elon musk", "jeff bezos",
    "bill gates", "mark cuban", "janet yellen", "ray dalio", "charlie munger",
}


def _fetch_wikipedia_thumbnail(name, img_path):
    """Fetch an openly-licensed photo of a known public figure via
    Wikipedia's REST summary API. Returns True on success."""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(name)}"
        resp = requests.get(url, timeout=15, headers={"User-Agent": "TheAIDollar/1.0"})
        if resp.status_code != 200:
            return False
        data = resp.json()
        img_url = (data.get("originalimage") or data.get("thumbnail") or {}).get("source")
        if not img_url:
            return False
        img_resp = requests.get(img_url, timeout=20)
        if img_resp.status_code == 200 and len(img_resp.content) > 10000:
            with open(img_path, 'wb') as f:
                f.write(img_resp.content)
            return True
    except Exception as e:
        print(f"  [WARN] Wikipedia fetch failed for {name}: {e}")
    return False


CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "").strip().strip('"').strip("'")
CF_API_TOKEN = os.getenv("CF_API_TOKEN", "").strip().strip('"').strip("'")
# SDXL is the default over flux-1-schnell because it renders NATIVE 9:16.
# flux-schnell only returns a square, so a portrait frame has to be cut from
# the middle and blown up ~1.9x, and that upscale is where most of the
# softness comes from. SDXL at 896x1568 needs only ~1.2x. Override with
# CF_IMAGE_MODEL to compare.
CF_IMAGE_MODEL = os.getenv("CF_IMAGE_MODEL",
                           "@cf/stabilityai/stable-diffusion-xl-base-1.0")

# Appended to every generated prompt. Kept separate from the subject so the
# subject stays the dominant part of the prompt.
_GEN_STYLE = ("professional editorial photograph, 50mm lens, natural soft "
              "lighting, shallow depth of field, sharp focus, crisp fine "
              "detail, high resolution, clean composition, commercial stock "
              "photography quality")
# flux-1-schnell takes no negative_prompt, so exclusions have to be worded
# as part of the prompt itself.
_GEN_NEGATIVE = (
    "people, person, human, man, woman, face, portrait, hands, hand, "
    "fingers, arms, body, crowd, "
    "extra fingers, fused hands, merged limbs, deformed hands, mutated, "
    "disfigured, distorted, melted, warped, blurry, low detail, "
    "text, words, letters, watermark, signature, logo"
)

# Words that pull a person into frame. Generated hands and faces come out
# fused and melted often enough that the only reliable fix is to keep them
# out of the picture entirely, so any subject mentioning one is rewritten
# into the equivalent object-only scene before it reaches the generator.
_PEOPLE_WORDS = (
    "hand", "hands", "finger", "fingers", "palm", "arm", "arms",
    "person", "people", "man", "men", "woman", "women", "guy", "lady",
    "someone", "worker", "owner", "boss", "employee", "customer",
    "shopper", "investor", "trader", "banker", "broker", "client",
    "face", "faces", "portrait", "crowd", "team", "family", "couple",
    "he", "she", "his", "her", "their", "holding", "signing", "counting",
    "shaking", "pointing", "wearing", "smiling", "walking", "sitting",
)


def _deperson_subject(subject):
    """Strip a human out of a described scene, keeping the objects.

    Returns (subject, changed). The rewrite is deliberately blunt: it drops
    the clause naming the person and appends an explicit empty-scene
    instruction, which reads better than any attempt to describe a person
    the generator cannot render correctly."""
    words = re.findall(r"[a-zA-Z]+", subject.lower())
    if not any(w in _PEOPLE_WORDS for w in words):
        return subject, False

    # Drop the person words themselves rather than truncating at the first
    # one — truncating threw away the objects that came after it, turning
    # "a restaurant owner counting cash at the till" into "a restaurant".
    kept = [w for w in re.findall(r"[a-zA-Z]+", subject)
            if w.lower() not in _PEOPLE_WORDS]

    # Removing a word usually leaves a dangling article or preposition
    # ("...into an open", "a a smartphone"), so collapse repeats and trim
    # any trailing connective left pointing at nothing.
    dangling = {"a", "an", "the", "of", "with", "into", "on", "in", "at",
                "to", "for", "and", "by", "from", "open", "empty", "beside"}
    cleaned = []
    for w in kept:
        if cleaned and w.lower() == cleaned[-1].lower():
            continue
        if cleaned and w.lower() in {"a", "an", "the"} \
                and cleaned[-1].lower() in {"a", "an", "the"}:
            cleaned[-1] = w
            continue
        cleaned.append(w)
    while cleaned and cleaned[-1].lower() in dangling:
        cleaned.pop()

    base = " ".join(cleaned).strip(" ,.;:-")
    if len(base.split()) < 2:
        # Nothing usable survived — fall back to a neutral finance still
        # life rather than sending a prompt that still names a person.
        base = "banknotes, coins and a ledger on a desk"
    return (f"{base}, empty scene with nobody present, "
            f"no people, no hands visible"), True


def _generate_cloudflare(prompt, img_path, width=768, height=1024, seed=13):
    """Generate one image with FLUX-1-schnell on Cloudflare Workers AI.

    This is the primary generator. Pollinations, the previous one, retired
    its FLUX endpoint and now serves only `sana` regardless of the `model`
    parameter sent — a small distilled model whose output is consistently
    soft and melted-looking. No amount of prompt wording fixed it, so the
    fix had to be a different model. Cloudflare's free tier covers roughly
    2,000 images a day against the ~14 this channel needs, with no card.

    The two models take different inputs and return different shapes, so
    both are handled: SDXL accepts width/height/negative_prompt/num_steps
    and streams raw image bytes, while flux-1-schnell accepts only
    prompt/steps/seed and returns base64 JSON."""
    if not (CF_ACCOUNT_ID and CF_API_TOKEN):
        return False
    url = (f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}"
           f"/ai/run/{CF_IMAGE_MODEL}")
    is_flux = "flux" in CF_IMAGE_MODEL

    if is_flux:
        # No seed: this endpoint rejects unknown properties outright, and
        # sending one made every flux call 400 and silently fall through to
        # the low-quality fallback generator.
        payload = {
            "prompt": f"{prompt}. {_GEN_STYLE}. {_GEN_NEGATIVE}"[:2048],
            "steps": 8,
        }
    else:
        payload = {
            "prompt": f"{prompt}. {_GEN_STYLE}"[:2048],
            "negative_prompt": _GEN_NEGATIVE,
            # Multiples of 64 near the frame's 9:16. SDXL drifts into
            # duplicated subjects well above its training size, so this
            # stays close to 1024-equivalent area rather than maxing out.
            "width": width,
            "height": height,
            "num_steps": 20,
            "guidance": 7.5,
            "seed": seed,
        }

    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
            json=payload,
            timeout=180,
        )
        if resp.status_code != 200:
            print(f"  [WARN] Cloudflare image {resp.status_code}: "
                  f"{resp.text[:200]}")
            return False

        ctype = resp.headers.get("Content-Type", "")
        if "image" in ctype:
            raw = resp.content
        else:
            b64 = (resp.json().get("result") or {}).get("image")
            if not b64:
                print(f"  [WARN] Cloudflare returned no image: "
                      f"{resp.text[:200]}")
                return False
            raw = base64.b64decode(b64)

        if len(raw) < 5000:
            return False
        with open(img_path, "wb") as f:
            f.write(raw)
        return True
    except Exception as e:
        print(f"  [WARN] Cloudflare image generation failed: {e}")
        return False


def _generate_pollinations(prompt, img_path, width=768, height=1024, seed=13):
    """Last-resort generator. Quality is poor (see _generate_cloudflare) but
    it needs no credentials, so it keeps the pipeline producing something if
    the Cloudflare token is missing or its daily quota runs out."""
    full = f"{_GEN_STYLE}, {prompt}, no text, no words, no watermark"
    url = ("https://image.pollinations.ai/prompt/"
           f"{urllib.parse.quote(full)}"
           f"?width={width}&height={height}&nologo=true&seed={seed}")
    try:
        resp = requests.get(url, timeout=90)
        if resp.status_code == 200 and len(resp.content) > 5000:
            with open(img_path, "wb") as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"  [WARN] Pollinations generation failed: {e}")
    return False


# Native 9:16 at close to SDXL's trained pixel budget. Bigger drifts into
# duplicated subjects; smaller needs more upscaling and goes soft.
GEN_PORTRAIT = (896, 1568)
GEN_LANDSCAPE = (1568, 896)


def generate_image(prompt, img_path, width=None, height=None, seed=13,
                   landscape=False):
    """Generate one image for `prompt`, best available generator first,
    then scale-and-sharpen it to frame size."""
    if width is None or height is None:
        width, height = GEN_LANDSCAPE if landscape else GEN_PORTRAIT
    prompt, changed = _deperson_subject(prompt)
    if changed:
        print(f"  [IMG] removed people from subject -> {prompt[:60]}")
    ok = _generate_cloudflare(prompt, img_path, width, height, seed)
    if not ok:
        ok = _generate_pollinations(prompt, img_path, width, height, seed)
    if ok:
        enhance_image(img_path, landscape=landscape)
    return ok


def fetch_term_hero_images(term_a, term_b, save_dir, icon_a=None, icon_b=None):
    """One clean, purpose-drawn ILLUSTRATION per confusable term for the
    side-by-side panels.

    These are generated as flat vector-style graphics rather than pulled
    from stock photography. A Pexels search for "business finance markup"
    returns an interchangeable office/laptop photo that doesn't depict the
    concept at all — the two panels ended up looking near-identical and
    taught the viewer nothing. A generated illustration of the specific
    idea reads instantly and keeps the two sides visually distinct.
    Stock photo search remains the fallback if generation is unavailable."""
    os.makedirs(save_dir, exist_ok=True)
    headers = {"Authorization": PEXELS_API_KEY} if PEXELS_API_KEY else {}
    results = []
    used_photo_ids = set()
    icons = (icon_a, icon_b)
    for idx, term in enumerate((term_a, term_b)):
        img_path = os.path.join(save_dir, f"hero_{idx}.jpg")
        got = False

        # Real people stay as real photographs.
        if term.strip().lower() in WELL_KNOWN_FIGURES:
            got = _fetch_wikipedia_thumbnail(term.strip(), img_path)

        if not got:
            # The subject must be a CONCRETE object supplied by the script
            # writer. Prompting the generator with the bare finance term
            # produced abstract grey blobs — it can't draw "revenue", but it
            # can draw "a cash register overflowing with banknotes".
            subject = (icons[idx] or "").strip()
            if not subject:
                subject = f"a bank building and coins representing {term}"
            if generate_image(subject, img_path, seed=idx * 977 + 13):
                got = True
                print(f"  [ILLUS] {term}")

        if not got and PEXELS_API_KEY:
            try:
                query = f"business finance {term}"
                purl = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&orientation=portrait&per_page=15"
                resp = requests.get(purl, headers=headers, timeout=15)
                if resp.status_code == 200:
                    photos = resp.json().get("photos", [])
                    photo = next((p for p in photos if p.get("id") not in used_photo_ids), None)
                    if photo:
                        img_url = photo["src"].get("large2x") or photo["src"]["large"]
                        img_resp = requests.get(img_url, timeout=20)
                        if img_resp.status_code == 200 and len(img_resp.content) > 20000:
                            with open(img_path, 'wb') as f:
                                f.write(img_resp.content)
                            used_photo_ids.add(photo.get("id"))
                            got = True
            except Exception as e:
                print(f"  [WARN] Hero image fetch failed for {term}: {e}")
        results.append(img_path if got else None)
    return tuple(results)


def fetch_hd_images(slides, save_dir, landscape=False):
    """Per-slide artwork: Wikipedia photos for named public figures, and
    generated illustrations of the slide's own described scene for
    everything else.

    Generation is preferred over stock photo search because the search
    query is derived from the slide text, so it returned generic office
    imagery that matched the words but not the idea. The slide's "img"
    field already describes the exact scene the script wants, which an
    illustrator can draw directly. Stock search stays as the fallback."""
    os.makedirs(save_dir, exist_ok=True)
    images = []
    headers = {"Authorization": PEXELS_API_KEY} if PEXELS_API_KEY else {}
    orientation = "landscape" if landscape else "portrait"

    for i, slide in enumerate(slides):
        img_path = os.path.join(save_dir, f"slide_{i}.jpg")

        if os.path.exists(img_path) and os.path.getsize(img_path) > 50000:
            images.append(img_path)
            continue

        desc = slide.get('img', 'finance money')
        text = slide.get('text', '')
        query = _extract_search_keywords(desc, text)
        got = False

        if desc.strip().lower() in WELL_KNOWN_FIGURES:
            if _fetch_wikipedia_thumbnail(desc.strip(), img_path):
                images.append(img_path)
                print(f"  [WIKI] Slide {i+1}: {desc.strip()}")
                got = True

        if not got:
            # Same illustration style as the comparison panels so the whole
            # video looks like one designed piece rather than a mix of
            # stock photography and graphics.
            if generate_image(desc, img_path, seed=i * 131 + 7,
                              landscape=landscape):
                images.append(img_path)
                print(f"  [ILLUS] Slide {i+1}: {desc[:44]}")
                got = True

        if not got and PEXELS_API_KEY:
            try:
                purl = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&orientation={orientation}&per_page=15"
                resp = requests.get(purl, headers=headers, timeout=15)
                if resp.status_code == 200:
                    photos = resp.json().get("photos", [])
                    if photos:
                        photo = photos[i % len(photos)]
                        if landscape:
                            img_url = photo["src"].get("original") or photo["src"].get("large2x") or photo["src"].get("landscape") or photo["src"]["large"]
                        else:
                            img_url = photo["src"].get("original") or photo["src"].get("large2x") or photo["src"].get("portrait") or photo["src"]["large"]
                        img_resp = requests.get(img_url, timeout=20)
                        if img_resp.status_code == 200 and len(img_resp.content) > 20000:
                            with open(img_path, 'wb') as f:
                                f.write(img_resp.content)
                            images.append(img_path)
                            print(f"  [HD] Slide {i+1}: {query} (photo fallback)")
                            got = True
            except Exception as e:
                print(f"  [WARN] Pexels failed slide {i+1}: {e}")

        if not got:
            images.append(None)

    return images


PIPER_VOICE_NAME = os.getenv("PIPER_VOICE_NAME", "en_US-ryan-medium")
PIPER_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "piper_models")
PIPER_VOICE_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium"
_piper_voice = None


def _get_piper_voice():
    """Lazily download (once) and load the Piper TTS voice model.
    Fully open-source, runs locally — no API key, no billing, ever."""
    global _piper_voice
    if _piper_voice is not None:
        return _piper_voice

    os.makedirs(PIPER_MODEL_DIR, exist_ok=True)
    onnx_path = os.path.join(PIPER_MODEL_DIR, f"{PIPER_VOICE_NAME}.onnx")
    json_path = os.path.join(PIPER_MODEL_DIR, f"{PIPER_VOICE_NAME}.onnx.json")

    try:
        if not os.path.exists(onnx_path):
            print(f"[Piper] Downloading voice model {PIPER_VOICE_NAME}...")
            r = requests.get(f"{PIPER_VOICE_BASE_URL}/{PIPER_VOICE_NAME}.onnx", timeout=600)
            r.raise_for_status()
            with open(onnx_path, "wb") as f:
                f.write(r.content)
        if not os.path.exists(json_path):
            r = requests.get(f"{PIPER_VOICE_BASE_URL}/{PIPER_VOICE_NAME}.onnx.json", timeout=120)
            r.raise_for_status()
            with open(json_path, "wb") as f:
                f.write(r.content)

        from piper import PiperVoice
        _piper_voice = PiperVoice.load(onnx_path, config_path=json_path)
        print(f"[OK] Piper voice loaded: {PIPER_VOICE_NAME}")
        return _piper_voice
    except Exception as e:
        print(f"[WARN] Could not load Piper voice: {e}")
        return None


def _run_piper_tts(text, output_path, length_scale=1.15):
    """Synthesize speech with Piper (open-source, local, free forever)."""
    voice = _get_piper_voice()
    if voice is None:
        return False
    try:
        import wave
        from piper import SynthesisConfig
        # length_scale > 1.0 slows speech down for clarity (1.0 = normal speed)
        syn_config = SynthesisConfig(length_scale=length_scale)
        wav_path = output_path.rsplit(".", 1)[0] + "_piper.wav"
        with wave.open(wav_path, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file, syn_config=syn_config)

        cmd = [FFMPEG, '-y', '-i', wav_path, '-c:a', 'libmp3lame', '-b:a', '128k', output_path]
        proc = subprocess.run(cmd, capture_output=True, timeout=30)
        try:
            os.remove(wav_path)
        except Exception:
            pass
        return proc.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 500
    except Exception as e:
        print(f"  [WARN] Piper TTS failed: {e}")
        return False


GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY", "")
GOOGLE_TTS_VOICE = os.getenv("GOOGLE_TTS_VOICE", "en-US-Neural2-D")


def _run_google_tts(text, output_path, speaking_rate=0.9, pitch=-1.0):
    """Synthesize speech with Google Cloud TTS Neural2 (free up to 1M chars/mo).
    Falls back to edge-tts automatically if this fails or no key is set."""
    if not GOOGLE_TTS_API_KEY:
        return False
    import base64
    try:
        resp = requests.post(
            f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_API_KEY}",
            json={
                "input": {"text": text},
                "voice": {"languageCode": "en-US", "name": GOOGLE_TTS_VOICE},
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "speakingRate": speaking_rate,
                    "pitch": pitch,
                },
            },
            timeout=20,
        )
        if resp.status_code != 200:
            print(f"  [WARN] Google TTS error {resp.status_code}: {resp.text[:200]}")
            return False
        audio_b64 = resp.json().get("audioContent")
        if not audio_b64:
            return False
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(audio_b64))
        return os.path.exists(output_path) and os.path.getsize(output_path) > 500
    except Exception as e:
        print(f"  [WARN] Google TTS failed: {e}")
        return False


FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY", "")
# "ALEX_CHIKNA" — picked by ear from a side-by-side sample test: a
# confident, fast-paced young male voice. Chosen over the deeper narrator
# options because a lighter, brighter delivery reads as more human and
# energetic in short-form than a bass documentary voice.
FISH_AUDIO_VOICE_ID = os.getenv("FISH_AUDIO_VOICE_ID", "52e0660e03fe4f9a8d2336f67cab5440")


def _run_fish_audio_tts(text, output_path, speed=1.0):
    """Synthesize speech with Fish Audio's S2.1 Pro model — free (no card,
    no billing) under Fair Use as of 2026, noticeably more natural/HD than
    edge-tts or Piper. No official SLA, so any failure falls back to the
    existing edge-tts chain automatically."""
    if not FISH_AUDIO_API_KEY:
        return False
    try:
        resp = requests.post(
            "https://api.fish.audio/v1/tts",
            headers={
                "Authorization": f"Bearer {FISH_AUDIO_API_KEY}",
                "Content-Type": "application/json",
                "model": "s2.1-pro-free",
            },
            json={
                "text": text,
                "reference_id": FISH_AUDIO_VOICE_ID,
                "format": "mp3",
                "mp3_bitrate": 128,
                "prosody": {"speed": speed, "normalize_loudness": True},
            },
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"  [WARN] Fish Audio TTS error {resp.status_code}: {resp.text[:200]}")
            return False
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 500
    except Exception as e:
        print(f"  [WARN] Fish Audio TTS failed: {e}")
        return False


def _run_edge_tts(text, output_path, voice, rate, pitch):
    """Run edge-tts in a clean asyncio context with retry"""
    import edge_tts
    import time as _time

    async def _generate():
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_path)

    for attempt in range(3):
        try:
            asyncio.run(_generate())
            if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                return True
        except Exception as e:
            print(f"  [WARN] edge-tts attempt {attempt+1}/3 ({voice}): {e}")
            _time.sleep(2)
    return False


VOICE_LIST = [
    ("en-US-ChristopherNeural", "+6%", "-2Hz"),
    ("en-US-GuyNeural", "+6%", "-2Hz"),
    ("en-US-AndrewMultilingualNeural", "+6%", "-2Hz"),
    ("en-GB-RyanNeural", "+6%", "-2Hz"),
    ("en-US-DavisNeural", "+6%", "-2Hz"),
]


def create_slide_audios(slides, work_dir):
    """Generate audio for each slide's speech separately, measure exact duration per slide.
    Priority: Fish Audio S2.1 Pro (free, HD, no billing) -> Piper (opt-in,
    local) -> Google Cloud TTS (if a key is configured) -> edge-tts (free,
    no billing, final fallback)."""
    os.makedirs(work_dir, exist_ok=True)

    use_fish = False
    test_path = os.path.join(work_dir, "test_voice.mp3")
    if FISH_AUDIO_API_KEY:
        if _run_fish_audio_tts("Testing voice.", test_path):
            use_fish = True
            try:
                os.remove(test_path)
            except Exception:
                pass
            print("[OK] Using Fish Audio S2.1 Pro (Alex Chikna - energetic)")
        else:
            print("[WARN] Fish Audio unavailable, trying Piper / Google TTS / edge-tts")

    use_piper = False
    if not use_fish and os.getenv("USE_PIPER_TTS", "false").lower() == "true":
        if _run_piper_tts("Testing voice.", test_path):
            use_piper = True
            try:
                os.remove(test_path)
            except Exception:
                pass
            print(f"[OK] Using Piper voice: {PIPER_VOICE_NAME}")
        else:
            print("[WARN] Piper unavailable, trying Google TTS / edge-tts")

    use_google = False
    if not use_fish and not use_piper and GOOGLE_TTS_API_KEY:
        if _run_google_tts("Testing voice.", test_path):
            use_google = True
            try:
                os.remove(test_path)
            except Exception:
                pass
            print(f"[OK] Using Google Cloud TTS voice: {GOOGLE_TTS_VOICE}")
        else:
            print("[WARN] Google TTS test failed, falling back to edge-tts")

    working_voice = None
    if not use_fish and not use_piper and not use_google:
        try:
            import edge_tts
        except ImportError:
            print("[ERR] edge-tts not installed")
            return None

        for voice, rate, pitch in VOICE_LIST:
            if _run_edge_tts("Testing voice.", test_path, voice, rate, pitch):
                working_voice = (voice, rate, pitch)
                try:
                    os.remove(test_path)
                except Exception:
                    pass
                print(f"[OK] Using voice: {voice}")
                break

        if not working_voice:
            print("[ERR] All edge-tts voices failed in create_slide_audios")
            return None

    def _adjust_rate(rate_str, delta):
        """Shift a percentage string like '-6%' by delta points."""
        try:
            val = int(rate_str.strip('%').replace('+', ''))
        except ValueError:
            val = 0
        new_val = val + delta
        return f"{'+' if new_val >= 0 else ''}{new_val}%"

    def _adjust_pitch(pitch_str, delta):
        """Shift a Hz string like '-2Hz' by delta points."""
        try:
            val = int(pitch_str.replace('Hz', '').replace('+', ''))
        except ValueError:
            val = 0
        new_val = val + delta
        return f"{'+' if new_val >= 0 else ''}{new_val}Hz"

    audio_paths = []
    durations = []
    total_slides = len(slides)

    for idx, slide in enumerate(slides):
        audio_path = os.path.join(work_dir, f"speech_{idx}.mp3")
        ok = False
        # Vary energy across the video instead of one flat pace throughout:
        # punchier on the hook and the closing call-to-action, calmer and
        # clearer through the explanation slides in between.
        is_energetic_beat = idx == 0 or idx == total_slides - 1
        energy_delta = 13 if is_energetic_beat else 0
        pitch_delta = 5 if is_energetic_beat else 0

        if use_fish:
            ok = _run_fish_audio_tts(slide['speech'], audio_path, speed=1.1)
            if not ok:
                print(f"  [WARN] Fish Audio failed for slide {idx}, trying fallback")
        if not ok and use_piper:
            ok = _run_piper_tts(slide['speech'], audio_path, length_scale=(1.0 if is_energetic_beat else 1.15))
            if not ok:
                print(f"  [WARN] Piper failed for slide {idx}, trying fallback")
        if not ok and use_google:
            ok = _run_google_tts(
                slide['speech'], audio_path,
                speaking_rate=(1.0 if is_energetic_beat else 0.9),
            )
            if not ok:
                print(f"  [WARN] Google TTS failed for slide {idx}, trying edge-tts fallback")
        if not ok:
            # edge-tts is the true last resort regardless of which primary
            # engine was in use — without this, a mid-run failure on the
            # primary engine (Fish Audio has no SLA) would silently fall
            # through to a silent slide instead of a working fallback.
            try:
                import edge_tts  # noqa: F401
                voice, rate, pitch = working_voice or VOICE_LIST[0]
                ok = _run_edge_tts(
                    slide['speech'], audio_path, voice,
                    _adjust_rate(rate, energy_delta), _adjust_pitch(pitch, pitch_delta),
                )
            except ImportError:
                pass
        if not ok:
            print(f"  [WARN] TTS failed for slide {idx}, using silence")
            silence_cmd = [FFMPEG, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '3', '-c:a', 'aac', audio_path]
            subprocess.run(silence_cmd, capture_output=True, timeout=10)

        dur = get_audio_duration(audio_path)
        dur = max(dur, 1.5)
        audio_paths.append(audio_path)
        durations.append(dur)
        print(f"  [TTS] Slide {idx+1}: {dur:.1f}s")

    concat_list = os.path.join(work_dir, "audio_concat.txt")
    with open(concat_list, 'w') as f:
        for ap in audio_paths:
            f.write(f"file '{os.path.basename(ap)}'\n")

    combined = os.path.join(work_dir, "combined_audio.mp3")
    cmd = [FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', concat_list, '-c:a', 'copy', combined]
    subprocess.run(cmd, capture_output=True, timeout=30)

    if not os.path.exists(combined) or os.path.getsize(combined) < 1000:
        return None

    return combined, durations


def create_audio(text, output_path):
    try:
        import edge_tts
        for voice, rate, pitch in VOICE_LIST:
            if _run_edge_tts(text, output_path, voice, rate, pitch):
                print(f"[OK] Audio ready (deep voice: {voice})")
                return True
        raise Exception("All edge-tts voices failed after retries")
    except Exception as e:
        print(f"[WARN] edge-tts failed ({e}), using gTTS...")

    import time as _time
    from gtts import gTTS
    for attempt in range(3):
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            print("[OK] Audio ready (gTTS fallback)")
            return True
        except Exception as e:
            print(f"  [WARN] gTTS attempt {attempt+1}/3: {e}")
            _time.sleep(5)

    raise Exception("All TTS methods failed")


def generate_bg_music(output_path, duration):
    """Write an original, gentle background music bed: a soft four-chord pad
    progression that moves every couple of bars so the track breathes with
    the video instead of sitting on one flat drone.

    Synthesised sample-by-sample with the stdlib (wave/array/math) rather
    than a big ffmpeg lavfi filter graph — an earlier amix-based version was
    the suspected cause of ffmpeg hangs on Render, and this needs no extra
    dependencies and cannot hang. Fully original audio, so there are no
    music-licensing or Content-ID problems on YouTube/TikTok/Instagram."""
    import wave
    import array as _array
    import math as _math

    try:
        sr = 44100
        total = int(sr * duration)
        # Am - F - C - G: a warm, neutral loop that suits explainer content.
        chords = [
            (110.00, 130.81, 164.81),   # Am
            (87.31, 110.00, 130.81),    # F
            (130.81, 164.81, 196.00),   # C
            (98.00, 123.47, 146.83),    # G
        ]
        bar = max(1.0, duration / 8.0)   # chord change roughly every bar
        samples = _array.array("h", bytes(total * 2))

        fade = int(sr * 1.5)
        for i in range(total):
            t = i / sr
            ci = int(t / bar) % len(chords)
            # crossfade between chords so changes are smooth, not clicky
            local = (t % bar) / bar
            nxt = chords[(ci + 1) % len(chords)]
            cur = chords[ci]
            blend = max(0.0, (local - 0.85) / 0.15)   # last 15% of the bar

            v = 0.0
            for f_cur, f_nxt in zip(cur, nxt):
                f = f_cur * (1 - blend) + f_nxt * blend
                v += _math.sin(2 * _math.pi * f * t)
            v /= len(cur)
            # slow tremolo gives it a little life
            v *= 0.85 + 0.15 * _math.sin(2 * _math.pi * 0.15 * t)

            amp = 0.30                      # bed level; ducked under narration at mix
            if i < fade:
                amp *= i / fade
            if i > total - fade:
                amp *= max(0.0, (total - i) / fade)

            samples[i] = int(max(-1.0, min(1.0, v * amp)) * 32767)

        wav_path = output_path + ".wav"
        with wave.open(wav_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(samples.tobytes())

        cmd = [FFMPEG, "-y", "-i", wav_path,
               "-af", "lowpass=f=1200,highpass=f=55",
               "-c:a", "aac", "-b:a", "96k", output_path]
        proc = _run_ffmpeg_hard_timeout(cmd, timeout=60)
        try:
            os.remove(wav_path)
        except Exception:
            pass
        if proc is None or proc.returncode != 0:
            print("[WARN] generate_bg_music: encode failed, skipping background music")
            return False
        return os.path.exists(output_path)
    except Exception as e:
        print(f"[WARN] generate_bg_music failed ({e}), skipping background music")
        return False


def get_audio_duration(audio_path):
    cmd = [FFMPEG, '-i', audio_path, '-f', 'null', '-']
    proc = _run_ffmpeg_hard_timeout(cmd, timeout=30)
    if proc is None:
        print("[WARN] get_audio_duration: ffmpeg timed out, using fallback duration")
        return 4
    output = proc.stderr.decode('utf-8', errors='replace')
    for line in output.split('\n'):
        if 'Duration' in line:
            time_str = line.split('Duration:')[1].split(',')[0].strip()
            parts = time_str.split(':')
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 4


def prep_slides(images, slides, durations, work_dir, landscape=False):
    """Create professional cinematic slides — full HD, clean design, readable text."""
    os.makedirs(work_dir, exist_ok=True)

    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    def get_font(size):
        font_search = [
            "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf",
        ]
        for path in font_search:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    if landscape:
        W, H = 1920, 1080
    else:
        W, H = 1080, 1920
    PAD = 50
    MAX_TW = W - PAD * 2

    font_brand = get_font(28)
    font_cta = get_font(44)
    font_sub = get_font(24)
    font_counter = get_font(22)

    WHITE = (255, 255, 255)
    LIGHT_GRAY = (200, 200, 210)
    ACCENT = (220, 220, 230)

    def wrap_line(text_line, font, draw_ctx, max_w):
        words = text_line.split()
        if not words:
            return [text_line]
        out = []
        cur = words[0]
        for word in words[1:]:
            test = cur + " " + word
            bb = draw_ctx.textbbox((0, 0), test, font=font)
            if (bb[2] - bb[0]) <= max_w:
                cur = test
            else:
                out.append(cur)
                cur = word
        out.append(cur)
        return out

    def draw_text_shadow(draw_ctx, pos, text, font, fill):
        """Clean drop shadow + thin outline for readability on any background."""
        x, y = pos
        # Drop shadow
        draw_ctx.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0))
        draw_ctx.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
        # Thin outline
        for ox in range(-2, 3):
            for oy in range(-2, 3):
                if ox * ox + oy * oy <= 4:
                    draw_ctx.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0))
        draw_ctx.text((x, y), text, font=font, fill=fill)

    total_slides = len(slides)

    for idx, slide in enumerate(slides):
        img_src = images[idx] if idx < len(images) else None
        out = os.path.join(work_dir, f"s_{idx}.jpg")

        # Load and fit image to full frame
        if img_src and os.path.exists(img_src):
            bg = Image.open(img_src).convert("RGB")
            iw, ih = bg.size
            ratio = max(W / iw, H / ih)
            bg = bg.resize((int(iw * ratio), int(ih * ratio)), Image.LANCZOS)
            left = (bg.width - W) // 2
            top = (bg.height - H) // 2
            bg = bg.crop((left, top, left + W, top + H))
        else:
            bg = Image.new("RGB", (W, H), (12, 12, 40))

        # Cinematic gradient overlay — image visible everywhere, darker at bottom for text
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        # Light top vignette
        for gy in range(0, int(H * 0.12)):
            a = int(60 * (1 - gy / (H * 0.12)))
            ov_draw.rectangle([0, gy, W, gy + 1], fill=(0, 0, 0, a))
        # Bottom gradient for text readability
        grad_start = int(H * 0.38)
        for gy in range(grad_start, H):
            frac = (gy - grad_start) / (H - grad_start)
            a = int(220 * (frac ** 1.3))
            ov_draw.rectangle([0, gy, W, gy + 1], fill=(0, 0, 0, min(a, 220)))
        bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

        draw = ImageDraw.Draw(bg)

        # Brand name — top left, subtle white
        brand = "THE AI DOLLAR"
        draw_text_shadow(draw, (PAD, 28), brand, font_brand, LIGHT_GRAY)

        # Slide counter — top right
        counter = f"{idx + 1}/{total_slides}"
        cb = draw.textbbox((0, 0), counter, font=font_counter)
        cw = cb[2] - cb[0]
        draw_text_shadow(draw, (W - cw - PAD, 30), counter, font_counter, LIGHT_GRAY)

        # Text rendering with auto-wrap and auto-scale
        text = slide['text'].upper()
        raw_lines = text.split('\n')

        for font_size in [62, 54, 48, 42, 36, 30]:
            ft_title = get_font(font_size)
            ft_body = get_font(max(font_size - 10, 24))
            wrapped = []
            for li, raw in enumerate(raw_lines):
                f = ft_title if li == 0 else ft_body
                wrapped.extend([(w, li == 0) for w in wrap_line(raw, f, draw, MAX_TW)])
            line_h = font_size + 30
            total_h = len(wrapped) * line_h
            if total_h < (H * 0.50):
                break

        start_y = H - total_h - 130

        for li, (line, is_title) in enumerate(wrapped):
            font = ft_title if is_title else ft_body
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = max((W - tw) // 2, PAD)
            y = start_y + li * line_h
            color = WHITE if is_title else ACCENT
            draw_text_shadow(draw, (x, y), line, font, color)

        is_first = (idx == 0)
        is_last = (idx == len(slides) - 1)

        if is_first:
            hook = "WATCH TIL THE END"
            hb = draw.textbbox((0, 0), hook, font=font_sub)
            hw = hb[2] - hb[0]
            hx = (W - hw) // 2
            hy = H - 80
            draw.rounded_rectangle(
                [hx - 20, hy - 8, hx + hw + 20, hy + 30],
                radius=12, fill=(220, 40, 40)
            )
            draw.text((hx, hy), hook, font=font_sub, fill=WHITE)

        if is_last:
            # Subscribe button
            cta = "SUBSCRIBE"
            cb = draw.textbbox((0, 0), cta, font=font_cta)
            cw_btn = cb[2] - cb[0]
            ch_btn = cb[3] - cb[1]
            cx = (W - cw_btn) // 2
            cy = 100
            draw.rounded_rectangle(
                [cx - 30, cy - 14, cx + cw_btn + 30, cy + ch_btn + 14],
                radius=14, fill=(220, 20, 20)
            )
            draw.text((cx, cy), cta, font=font_cta, fill=WHITE)

            # Engagement prompt
            cta2 = "COMMENT YOUR #1 MONEY GOAL"
            cb2 = draw.textbbox((0, 0), cta2, font=font_sub)
            cw2 = cb2[2] - cb2[0]
            cx2 = (W - cw2) // 2
            cy2 = H - 75
            draw.rounded_rectangle(
                [cx2 - 16, cy2 - 6, cx2 + cw2 + 16, cy2 + 28],
                radius=10, fill=(30, 30, 60, 200)
            )
            draw.text((cx2, cy2), cta2, font=font_sub, fill=WHITE)

        bg.save(out, "JPEG", quality=98)
        del draw, bg
        gc.collect()
        print(f"  slide {idx+1}/{len(slides)} ready")


def prep_kenburns_backgrounds(images, work_dir, landscape=False):
    """Crop/grade each source image to full frame (same look as prep_slides)
    but WITHOUT burning text on it — text is animated separately so it can
    stay fixed while only the photo moves underneath it."""
    os.makedirs(work_dir, exist_ok=True)
    from PIL import Image, ImageDraw

    W, H = (1920, 1080) if landscape else (1080, 1920)
    paths = []

    for idx, img_src in enumerate(images):
        out = os.path.join(work_dir, f"bg_{idx}.jpg")

        if img_src and os.path.exists(img_src):
            bg = Image.open(img_src).convert("RGB")
            iw, ih = bg.size
            ratio = max(W / iw, H / ih)
            bg = bg.resize((int(iw * ratio), int(ih * ratio)), Image.LANCZOS)
            left = (bg.width - W) // 2
            top = (bg.height - H) // 2
            bg = bg.crop((left, top, left + W, top + H))
        else:
            bg = Image.new("RGB", (W, H), (12, 12, 40))

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        for gy in range(0, int(H * 0.12)):
            a = int(60 * (1 - gy / (H * 0.12)))
            ov_draw.rectangle([0, gy, W, gy + 1], fill=(0, 0, 0, a))
        grad_start = int(H * 0.38)
        for gy in range(grad_start, H):
            frac = (gy - grad_start) / (H - grad_start)
            a = int(220 * (frac ** 1.3))
            ov_draw.rectangle([0, gy, W, gy + 1], fill=(0, 0, 0, min(a, 220)))
        bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

        bg.save(out, "JPEG", quality=95)
        paths.append(out)
        del bg, overlay
        gc.collect()

    return paths


def prep_text_overlays(slides, work_dir, landscape=False):
    """Render brand/counter/text/CTA onto a transparent PNG so it can sit,
    perfectly still, on top of the moving Ken Burns background."""
    os.makedirs(work_dir, exist_ok=True)
    from PIL import Image, ImageDraw, ImageFont

    def get_font(size):
        font_search = [
            "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf",
        ]
        for path in font_search:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    def wrap_line(text_line, font, draw_ctx, max_w):
        words = text_line.split()
        if not words:
            return [text_line]
        out = []
        cur = words[0]
        for word in words[1:]:
            test = cur + " " + word
            bb = draw_ctx.textbbox((0, 0), test, font=font)
            if (bb[2] - bb[0]) <= max_w:
                cur = test
            else:
                out.append(cur)
                cur = word
        out.append(cur)
        return out

    def draw_text_shadow(draw_ctx, pos, text, font, fill):
        x, y = pos
        draw_ctx.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0))
        draw_ctx.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
        for ox in range(-2, 3):
            for oy in range(-2, 3):
                if ox * ox + oy * oy <= 4:
                    draw_ctx.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0))
        draw_ctx.text((x, y), text, font=font, fill=fill)

    W, H = (1920, 1080) if landscape else (1080, 1920)
    PAD = 50
    MAX_TW = W - PAD * 2

    font_brand = get_font(28)
    font_cta = get_font(44)
    font_sub = get_font(24)
    font_counter = get_font(22)

    WHITE = (255, 255, 255)
    LIGHT_GRAY = (200, 200, 210)
    ACCENT = (220, 220, 230)

    total_slides = len(slides)
    paths = []

    for idx, slide in enumerate(slides):
        out = os.path.join(work_dir, f"ov_{idx}.png")
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        brand = "THE AI DOLLAR"
        draw_text_shadow(draw, (PAD, 28), brand, font_brand, LIGHT_GRAY)

        counter = f"{idx + 1}/{total_slides}"
        cb = draw.textbbox((0, 0), counter, font=font_counter)
        cw = cb[2] - cb[0]
        draw_text_shadow(draw, (W - cw - PAD, 30), counter, font_counter, LIGHT_GRAY)

        text = slide['text'].upper()
        raw_lines = text.split('\n')

        wrapped, total_h, ft_title, ft_body, line_h = [], 0, None, None, 0
        for font_size in [62, 54, 48, 42, 36, 30]:
            ft_title = get_font(font_size)
            ft_body = get_font(max(font_size - 10, 24))
            wrapped = []
            for li, raw in enumerate(raw_lines):
                f = ft_title if li == 0 else ft_body
                wrapped.extend([(w, li == 0) for w in wrap_line(raw, f, draw, MAX_TW)])
            line_h = font_size + 30
            total_h = len(wrapped) * line_h
            if total_h < (H * 0.50):
                break

        start_y = H - total_h - 130
        for li, (line, is_title) in enumerate(wrapped):
            font = ft_title if is_title else ft_body
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = max((W - tw) // 2, PAD)
            y = start_y + li * line_h
            color = WHITE if is_title else ACCENT
            draw_text_shadow(draw, (x, y), line, font, color)

        is_first = (idx == 0)
        is_last = (idx == len(slides) - 1)

        if is_first:
            hook = "WATCH TIL THE END"
            hb = draw.textbbox((0, 0), hook, font=font_sub)
            hw = hb[2] - hb[0]
            hx = (W - hw) // 2
            hy = H - 80
            draw.rounded_rectangle([hx - 20, hy - 8, hx + hw + 20, hy + 30], radius=12, fill=(220, 40, 40))
            draw.text((hx, hy), hook, font=font_sub, fill=WHITE)

        if is_last:
            cta = "SUBSCRIBE"
            cb = draw.textbbox((0, 0), cta, font=font_cta)
            cw_btn = cb[2] - cb[0]
            ch_btn = cb[3] - cb[1]
            cx = (W - cw_btn) // 2
            cy = 100
            draw.rounded_rectangle([cx - 30, cy - 14, cx + cw_btn + 30, cy + ch_btn + 14], radius=14, fill=(220, 20, 20))
            draw.text((cx, cy), cta, font=font_cta, fill=WHITE)

            cta2 = "COMMENT YOUR #1 MONEY GOAL"
            cb2 = draw.textbbox((0, 0), cta2, font=font_sub)
            cw2 = cb2[2] - cb2[0]
            cx2 = (W - cw2) // 2
            cy2 = H - 75
            draw.rounded_rectangle([cx2 - 16, cy2 - 6, cx2 + cw2 + 16, cy2 + 28], radius=10, fill=(30, 30, 60, 200))
            draw.text((cx2, cy2), cta2, font=font_sub, fill=WHITE)

        canvas.save(out, "PNG")
        paths.append(out)
        del draw, canvas
        gc.collect()
        print(f"  overlay {idx+1}/{len(slides)} ready")

    return paths


def _build_kenburns_segment(bg_path, overlay_path, duration, output_path, landscape, effect):
    """Animate a still background with a slow zoom/pan (Ken Burns), then
    burn the fixed text overlay on top so only the photo moves."""
    W, H = (1920, 1080) if landscape else (1080, 1920)
    frames = max(2, round(duration * 30))

    if effect == 0:
        z_expr = "min(zoom+0.0010,1.15)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif effect == 1:
        z_expr = "1.12"
        x_expr = f"(iw-iw/zoom)*(on/{frames})"
        y_expr = "ih/2-(ih/zoom/2)"
    else:
        z_expr = "1.12"
        x_expr = f"(iw-iw/zoom)*(1-on/{frames})"
        y_expr = "ih/2-(ih/zoom/2)"

    # Supersample before zoompan — cropping from a same-size source leaves too
    # little pixel data per frame, which reads as visible shaking/stepping.
    presc = f"scale={W*2}:{H*2}:flags=lanczos"
    zoompan = f"zoompan=z='{z_expr}':d={frames}:x='{x_expr}':y='{y_expr}':s={W}x{H}:fps=30"
    filter_complex = f"[0:v]{presc},{zoompan}[zoomed];[zoomed][1:v]overlay=0:0[v]"

    cmd = [
        FFMPEG, '-y',
        '-framerate', '30', '-loop', '1', '-i', bg_path,
        '-i', overlay_path,
        '-filter_complex', filter_complex,
        '-map', '[v]',
        '-t', f'{duration:.2f}',
        '-an',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '26',
        '-pix_fmt', 'yuv420p',
        output_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, timeout=120)
    return proc.returncode == 0 and os.path.exists(output_path)


def create_video_kenburns(slides, images, audio_file, durations, output_file, landscape=False):
    """Build the video with slow zoom/pan motion on each image instead of
    static slides — free forever, ffmpeg-only, no external APIs."""
    work_dir = output_file + "_kbwork"
    os.makedirs(work_dir, exist_ok=True)

    print("[BUILD] Preparing Ken Burns backgrounds...")
    backgrounds = prep_kenburns_backgrounds(images, work_dir, landscape=landscape)

    print("[BUILD] Preparing text overlays...")
    overlays = prep_text_overlays(slides, work_dir, landscape=landscape)

    print("[BUILD] Rendering per-slide motion segments...")
    segments = []
    for idx in range(len(slides)):
        seg_path = os.path.join(work_dir, f"seg_{idx}.mp4")
        effect = idx % 3
        ok = _build_kenburns_segment(backgrounds[idx], overlays[idx], durations[idx], seg_path, landscape, effect)
        if ok:
            segments.append(seg_path)
        gc.collect()
        print(f"  segment {idx+1}/{len(slides)} ready")

    if len(segments) != len(slides):
        import shutil
        shutil.rmtree(work_dir, ignore_errors=True)
        return False

    concat_file = os.path.join(work_dir, "concat.txt")
    with open(concat_file, 'w') as f:
        for seg in segments:
            f.write(f"file '{os.path.basename(seg)}'\n")
    concat_video = os.path.join(work_dir, "concat_video.mp4")
    proc = subprocess.run(
        [FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', concat_file, '-c', 'copy', concat_video],
        capture_output=True, timeout=120,
    )
    if proc.returncode != 0 or not os.path.exists(concat_video):
        import shutil
        shutil.rmtree(work_dir, ignore_errors=True)
        return False

    print("[BUILD] Muxing narration + music...")
    audio_duration = get_audio_duration(audio_file)
    bg_music_path = os.path.join(work_dir, "bgmusic.m4a")
    has_music = generate_bg_music(bg_music_path, audio_duration + 2)

    if has_music:
        cmd = [
            FFMPEG, '-y',
            '-i', concat_video,
            '-i', audio_file,
            '-i', bg_music_path,
            '-filter_complex', '[2:a]volume=0.10[bg];[1:a][bg]amix=inputs=2:duration=first[aout]',
            '-map', '0:v', '-map', '[aout]',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '128k',
            '-shortest',
                        '-movflags', '+faststart',
            output_file,
        ]
    else:
        cmd = [
            FFMPEG, '-y',
            '-i', concat_video,
            '-i', audio_file,
            '-map', '0:v', '-map', '1:a',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '128k',
            '-shortest',
                        '-movflags', '+faststart',
            output_file,
        ]

    proc = subprocess.run(cmd, capture_output=True, timeout=180)
    import shutil
    shutil.rmtree(work_dir, ignore_errors=True)

    if proc.returncode != 0:
        stderr = proc.stderr.decode('utf-8', errors='replace')[-500:]
        print(f"[WARN] Ken Burns mux failed: {stderr}")
        return False

    print("[OK] Video created (Ken Burns motion)!")
    return True


# Caption colour coding. Meaning is carried by colour so a viewer grasps
# the sentiment of a word before they've finished reading it. Classified
# here in code rather than asking the model to tag words, because a
# keyword table is deterministic and can't drift or return bad markup.
CAP_GREEN = (0, 220, 90)     # assets, profit, income, structural wins
CAP_RED = (255, 45, 45)      # liabilities, taxes, debt, traps, losses
CAP_YELLOW = (255, 214, 0)   # shocks, hooks, and any number
CAP_WHITE = (255, 255, 255)  # ordinary narrative words

_CAP_GREEN_WORDS = {
    "profit", "profits", "asset", "assets", "income", "gain", "gains",
    "wealth", "wealthy", "rich", "keeps", "keep", "kept", "saved", "saves",
    "savings", "earns", "earn", "growth", "grows", "compound", "equity",
    "credit", "surplus", "net", "return", "returns", "yield", "free",
    "owns", "own", "builds", "building", "stays", "up",
}
_CAP_RED_WORDS = {
    "debt", "debts", "loss", "losses", "lost", "liability", "liabilities",
    "tax", "taxes", "trap", "trapped", "broke", "bankrupt", "drained",
    "drain", "drains", "bleeding", "bleed", "owe", "owes", "owed", "cost",
    "costs", "expense", "expenses", "fees", "fee", "interest", "gone",
    "vanishes", "vanish", "collapse", "risk", "wrong", "mistake", "down",
    "negative", "minus", "spent", "spend", "spends", "illusion", "hidden",
    "quietly", "poor",
}
_CAP_YELLOW_WORDS = {
    "never", "always", "shocking", "secret", "nobody", "everyone", "most",
    "why", "how", "truth", "actually", "really", "difference", "versus",
    "vs", "but", "until", "because", "warning", "stop", "watch",
}


def _word_colour(word):
    """Colour for one caption word: numbers and shock words pop yellow,
    money-in words green, money-out words red, everything else white."""
    w = word.strip().lower().strip(".,!?:;\"'()-")
    if any(ch.isdigit() for ch in w) or w.startswith("$") or "%" in word:
        return CAP_YELLOW
    if w in _CAP_GREEN_WORDS:
        return CAP_GREEN
    if w in _CAP_RED_WORDS:
        return CAP_RED
    if w in _CAP_YELLOW_WORDS:
        return CAP_YELLOW
    return CAP_WHITE


CHAR_OUTLINE = (38, 38, 42)
CHAR_SKIN    = (248, 248, 248)
CHAR_SHIRT   = (168, 168, 172)
CHAR_PANTS   = (92, 92, 96)
CHAR_SHOE    = (58, 58, 62)


def _seg_quad(p0, p1, w0, w1):
    """Quad for a limb segment that tapers from width w0 at p0 to w1 at p1."""
    import math
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    return [
        (x0 + nx * w0 / 2, y0 + ny * w0 / 2),
        (x1 + nx * w1 / 2, y1 + ny * w1 / 2),
        (x1 - nx * w1 / 2, y1 - ny * w1 / 2),
        (x0 - nx * w0 / 2, y0 - ny * w0 / 2),
    ]


def _limb(draw, pts, widths, fill, ow):
    """A tapered, rounded, outlined limb through a chain of points — the
    look of the reference sketch (solid shapes with a clean dark outline)
    rather than thin sticks. Drawn as an oversized outline pass followed by
    the fill pass so joints merge seamlessly with no internal seams."""
    for colour, pad in ((CHAR_OUTLINE, ow), (fill, 0)):
        for i in range(len(pts) - 1):
            draw.polygon(_seg_quad(pts[i], pts[i + 1],
                                   widths[i] + pad * 2, widths[i + 1] + pad * 2),
                         fill=colour)
        for p, w in zip(pts, widths):
            r = (w + pad * 2) / 2
            draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=colour)


def _draw_character(img, cx, top_y, scale=1.0, pose='calm', phase=0.0,
                    point_left=True):
    """The AI Dollar host: a friendly cartoon presenter (round head, grey
    tee, dark trousers and shoes) drawn entirely from primitives so EVERY
    limb can be posed and animated — a flat PNG of the character can't move
    its arms or legs, which is why this is redrawn rather than pasted.

    poses: calm | walk | point_left | point_right | point_both | confused
    phase: 0..1 position within the walk cycle.
    Returns the character's bottom y so callers can lay out below it."""
    import math
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    s = scale

    ow = max(2, int(4 * s))     # outline thickness

    # --- proportions (matched to the reference sketch) ---
    head_r = int(44 * s)
    head_cx = cx
    head_cy = top_y + head_r

    neck_top = head_cy + head_r - int(6 * s)
    neck_y = neck_top + int(16 * s)          # where the collar sits

    shoulder_y = neck_y + int(6 * s)
    torso_w = int(78 * s)        # slim tee, not a barrel chest
    torso_h = int(128 * s)
    hip_y = shoulder_y + torso_h

    leg_len = int(150 * s)
    foot_y = hip_y + leg_len

    swing = math.sin(phase * 2 * math.pi) if pose == 'walk' else 0.0

    # --- ground shadow ---
    sh_w, sh_h = int(74 * s), int(13 * s)
    d.ellipse([cx - sh_w, foot_y + int(10 * s) - sh_h // 2,
               cx + sh_w, foot_y + int(10 * s) + sh_h // 2],
              fill=(230, 230, 228))

    # --- legs: solid tapered trousers from a shared hip. Each leg stays on
    # its own side (the sway is deliberately smaller than the stance width
    # so they can never scissor past each other, which looked broken from
    # this front-on view); the gait reads through alternating knee-lift. ---
    hip_dx = int(20 * s)
    stance = int(32 * s)     # wide enough that the trouser legs read as two
    sway = int(14 * s)
    thigh_w, calf_w, ankle_w = int(34 * s), int(28 * s), int(22 * s)

    feet = []
    for sign, ph in ((-1, swing), (1, -swing)):
        lift = max(0.0, ph)                      # this leg is mid-step
        footx = cx + sign * stance + int(sway * ph)
        footy = foot_y - int(30 * s) * lift
        kneex = cx + sign * stance + int(sway * ph * 0.6)
        kneey = hip_y + int(leg_len * 0.52) - int(20 * s) * lift
        _limb(d, [(cx + sign * hip_dx, hip_y - int(6 * s)), (kneex, kneey), (footx, footy)],
              [thigh_w, calf_w, ankle_w], CHAR_PANTS, ow)
        feet.append((sign, footx, footy))

    # --- shoes ---
    shoe_w, shoe_h = int(38 * s), int(17 * s)
    for sign, footx, footy in feet:
        toe = int(12 * s) * sign
        d.rounded_rectangle(
            [min(footx - shoe_w // 2, footx - shoe_w // 2 + toe), footy - shoe_h // 2,
             max(footx + shoe_w // 2, footx + shoe_w // 2 + toe), footy + shoe_h],
            radius=int(8 * s), fill=CHAR_SHOE, outline=CHAR_OUTLINE, width=ow)

    # --- neck (tucks under both head and collar) ---
    _limb(d, [(cx, neck_top), (cx, neck_y + int(10 * s))],
          [int(26 * s), int(26 * s)], CHAR_SKIN, ow)

    # --- torso / t-shirt ---
    d.rounded_rectangle(
        [cx - torso_w // 2, shoulder_y, cx + torso_w // 2, hip_y + int(4 * s)],
        radius=int(20 * s), fill=CHAR_SHIRT, outline=CHAR_OUTLINE, width=ow)

    # --- arms: upper arm + forearm, tapering to a wrist, ending in a hand
    # with an extended index finger when pointing ---
    def _arm(sign, mode, sw):
        sx = cx + sign * (torso_w // 2 - int(10 * s))
        sy = shoulder_y + int(20 * s)
        upper_w, fore_w, wrist_w = int(30 * s), int(24 * s), int(18 * s)

        if mode == 'point':
            # Angled UP-and-out so the gesture actually lands on the photo
            # panel above the character, instead of pointing horizontally
            # into empty space beside it.
            elbow = (cx + sign * int(66 * s), sy - int(26 * s))
            wrist = (cx + sign * int(104 * s), sy - int(74 * s))
            hand_dir = (sign * 0.55, -0.84)
        elif mode == 'up':
            elbow = (cx + sign * int(74 * s), sy - int(30 * s))
            wrist = (cx + sign * int(96 * s), sy - int(88 * s))
            hand_dir = (sign * 0.4, -1)
        else:  # relaxed at the side, swinging with the gait
            elbow = (cx + sign * int(62 * s), sy + int(56 * s))
            wrist = (cx + sign * int(70 * s), sy + int(112 * s) + int(24 * s) * sw)
            hand_dir = (0, 1)

        _limb(d, [(sx, sy), elbow, wrist],
              [upper_w, fore_w, wrist_w], CHAR_SKIN, ow)

        # --- hand: a palm noticeably wider than the wrist so it actually
        # reads as a hand rather than the arm just stopping, plus a clearly
        # separated index finger on the pointing poses.
        hx, hy = wrist
        dx, dy = hand_dir
        norm = math.hypot(dx, dy) or 1.0
        dx, dy = dx / norm, dy / norm
        palm_c = (hx + dx * int(10 * s), hy + dy * int(10 * s))
        palm_w = int(30 * s)
        _limb(d, [wrist, palm_c], [wrist_w, palm_w], CHAR_SKIN, ow)
        if mode == 'point':
            f0 = (palm_c[0] + dx * int(12 * s), palm_c[1] + dy * int(12 * s))
            f1 = (palm_c[0] + dx * int(42 * s), palm_c[1] + dy * int(42 * s))
            _limb(d, [f0, f1], [int(15 * s), int(11 * s)], CHAR_SKIN, ow)

    if pose == 'point_both':
        _arm(-1, 'point', 0); _arm(1, 'point', 0)
    elif pose == 'point_left':
        _arm(-1, 'point', 0); _arm(1, 'down', 0)
    elif pose == 'point_right':
        _arm(-1, 'down', 0); _arm(1, 'point', 0)
    elif pose == 'confused':
        _arm(-1, 'up', 0); _arm(1, 'up', 0)
    else:  # calm / walk — arms swing opposite their same-side leg
        _arm(-1, 'down', swing); _arm(1, 'down', -swing)

    # --- head ---
    d.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r],
              fill=CHAR_SKIN, outline=CHAR_OUTLINE, width=ow)
    eye_dx, eye_dy, eye_r = int(16 * s), int(6 * s), int(5 * s)
    for ex in (head_cx - eye_dx, head_cx + eye_dx):
        d.ellipse([ex - eye_r, head_cy - eye_dy - eye_r, ex + eye_r, head_cy - eye_dy + eye_r],
                  fill=CHAR_OUTLINE)
    if pose == 'confused':
        mo = int(9 * s)
        d.ellipse([head_cx - mo, head_cy + int(15 * s) - mo, head_cx + mo, head_cy + int(15 * s) + mo],
                  outline=CHAR_OUTLINE, width=ow)
    else:
        sm = int(20 * s)
        d.arc([head_cx - sm, head_cy - int(2 * s), head_cx + sm, head_cy + sm + int(8 * s)],
              start=20, end=160, fill=CHAR_OUTLINE, width=ow)

    return foot_y + shoe_h + int(12 * s)


def _draw_mascot(draw, cx, top_y, scale=1.0, color=(25, 25, 30), pointing=True, point_left=True, confused=False):
    """An original simple line-art stick-figure host character — hand-drawn
    with primitives, not traced from any existing meme/character."""
    import math
    s = scale
    head_r = int(48 * s)
    head_cy = top_y + head_r
    lw = max(2, int(6 * s))

    # Head
    draw.ellipse(
        [cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
        outline=color, width=lw
    )
    # Eyes
    eye_dx, eye_dy, eye_r = int(16 * s), int(6 * s), int(4 * s)
    for ex in (cx - eye_dx, cx + eye_dx):
        draw.ellipse([ex - eye_r, head_cy - eye_dy - eye_r, ex + eye_r, head_cy - eye_dy + eye_r], fill=color)
    # Mouth — small "o" if confused, smile otherwise
    if confused:
        mo_r = int(8 * s)
        draw.ellipse([cx - mo_r, head_cy + int(6 * s) - mo_r, cx + mo_r, head_cy + int(6 * s) + mo_r], outline=color, width=max(2, int(4 * s)))
    else:
        sm_r = int(20 * s)
        draw.arc(
            [cx - sm_r, head_cy - int(4 * s), cx + sm_r, head_cy + sm_r],
            start=20, end=160, fill=color, width=lw
        )

    neck_y = head_cy + head_r
    torso_len = int(90 * s)
    hip_y = neck_y + torso_len
    draw.line([cx, neck_y, cx, hip_y], fill=color, width=lw)

    leg_len = int(70 * s)
    foot_y = hip_y + leg_len
    draw.line([cx, hip_y, cx - int(30 * s), foot_y], fill=color, width=lw)
    draw.line([cx, hip_y, cx + int(30 * s), foot_y], fill=color, width=lw)

    arm_y = neck_y + int(15 * s)
    point_dx, point_dy = 0, 0
    top_bound = top_y

    if confused:
        # Both arms raised in a shrug, plus a hand-drawn "?" above the head.
        for side in (-1, 1):
            draw.line([cx, arm_y, cx + side * int(50 * s), arm_y - int(50 * s)], fill=color, width=lw)
        q_cx = cx
        q_top = top_y - int(70 * s)
        q_r = int(16 * s)
        draw.arc([q_cx - q_r, q_top, q_cx + q_r, q_top + int(28 * s)], start=200, end=430, fill=color, width=max(2, int(5 * s)))
        draw.line([q_cx, q_top + int(24 * s), q_cx, q_top + int(36 * s)], fill=color, width=max(2, int(5 * s)))
        draw.ellipse([q_cx - int(3 * s), q_top + int(42 * s), q_cx + int(3 * s), q_top + int(48 * s)], fill=color)
        top_bound = q_top
    elif pointing:
        # Raised arm at a realistic length (comparable to the torso, not a
        # gangly overreach) and a natural ~65deg angle, aimed up toward
        # whatever sits above the mascot (the photo card). Alternates side.
        arm_len = int(75 * s)
        angle = math.radians(42)
        direction = -1 if point_left else 1
        point_dx = int(direction * arm_len * math.cos(angle))
        point_dy = -int(arm_len * math.sin(angle))
        draw.line([cx, arm_y, cx + point_dx, arm_y + point_dy], fill=color, width=lw)
        # A small solid dot marks the hand — just the line direction does
        # the pointing, no arrowhead needed.
        hand_x, hand_y = cx + point_dx, arm_y + point_dy
        hand_r = max(3, int(7 * s))
        draw.ellipse([hand_x - hand_r, hand_y - hand_r, hand_x + hand_r, hand_y + hand_r], fill=color)
        # Other arm rests on hip, realistic length
        other_dx = int(38 * s) if point_left else -int(38 * s)
        draw.line([cx, arm_y, cx + other_dx, arm_y + int(32 * s)], fill=color, width=lw)
        top_bound = min(top_y, arm_y + point_dy)
    else:
        draw.line([cx, arm_y, cx - int(45 * s), arm_y + int(35 * s)], fill=color, width=lw)
        draw.line([cx, arm_y, cx + int(45 * s), arm_y + int(35 * s)], fill=color, width=lw)

    left_bound = min(cx - int(55 * s), cx + point_dx if pointing else cx)
    right_bound = max(cx + int(55 * s), cx + point_dx if pointing else cx)
    return (left_bound, top_bound, right_bound, foot_y)


def _draw_mascot_walk_frame(img, cx, top_y, scale, color, phase):
    """One frame of a walking/running gait: legs stride opposite each other,
    arms swing opposite their same-side leg (natural walk), plus a small
    vertical bob — phase is 0..1, one full cycle. Same head/face as
    _draw_mascot so it's the same character, just animated."""
    import math
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    s = scale
    bob = int(6 * s * abs(math.sin(phase * 2 * math.pi)))
    top_y = top_y - bob

    head_r = int(48 * s)
    head_cy = top_y + head_r
    lw = max(2, int(6 * s))

    draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], outline=color, width=lw)
    eye_dx, eye_dy, eye_r = int(16 * s), int(6 * s), int(4 * s)
    for ex in (cx - eye_dx, cx + eye_dx):
        draw.ellipse([ex - eye_r, head_cy - eye_dy - eye_r, ex + eye_r, head_cy - eye_dy + eye_r], fill=color)
    sm_r = int(20 * s)
    draw.arc([cx - sm_r, head_cy - int(4 * s), cx + sm_r, head_cy + sm_r], start=20, end=160, fill=color, width=lw)

    neck_y = head_cy + head_r
    torso_len = int(90 * s)
    hip_y = neck_y + torso_len
    draw.line([cx, neck_y, cx, hip_y], fill=color, width=lw)

    # Legs: base outward stance (so they're ALWAYS visibly apart, not
    # overlapping at any point in the cycle) plus a stride swing that
    # alternates left/right. A running gait — one leg forward, one back.
    leg_len = int(70 * s)
    base_leg_spread = int(18 * s)
    stride = int(40 * s)
    swing = math.sin(phase * 2 * math.pi)
    left_foot_x = cx - base_leg_spread - int(stride * swing)
    right_foot_x = cx + base_leg_spread + int(stride * swing)
    draw.line([cx, hip_y, left_foot_x, hip_y + leg_len], fill=color, width=lw)
    draw.line([cx, hip_y, right_foot_x, hip_y + leg_len], fill=color, width=lw)
    foot_y = hip_y + leg_len

    # Arms: base spread so both are always visible off the torso, plus a
    # real swing angle (opposite to same-side leg). Both hands are always
    # off-body — never a "no arms" frame.
    arm_y = neck_y + int(15 * s)
    arm_len = int(50 * s)
    arm_swing = math.sin(phase * 2 * math.pi)
    left_hand_x = cx - int(arm_len * 0.55) - int(arm_len * 0.35 * arm_swing)
    right_hand_x = cx + int(arm_len * 0.55) + int(arm_len * 0.35 * arm_swing)
    left_hand_y = arm_y + int(arm_len * 0.6) + int(arm_len * 0.25 * arm_swing)
    right_hand_y = arm_y + int(arm_len * 0.6) - int(arm_len * 0.25 * arm_swing)
    draw.line([cx, arm_y, left_hand_x, left_hand_y], fill=color, width=lw)
    draw.line([cx, arm_y, right_hand_x, right_hand_y], fill=color, width=lw)

    return foot_y


def prep_infographic_slides(images, slides, work_dir, landscape=False,
                             term_a=None, term_b=None, hero_images=(None, None),
                             durations=None):
    """Clean white-background infographic style: bold headline, a boxed
    photo card, and a recurring original mascot character for brand
    identity — inspired by high-performing comparison-style Shorts.

    The mascot is animated by drawing it DIRECTLY with PIL onto multiple
    frames per slide (running while it travels between panels, pointing at
    a term once it arrives, bouncing on the hook) — deliberately not an
    ffmpeg overlay/alpha trick, because two different ffmpeg-side attempts
    (WebM/VP9 alpha, then a multi-input overlay+enable filter chain) both
    silently failed on Render's ffmpeg build and fell back to a motionless
    mascot in production despite working locally. Direct PIL drawing is the
    same method already proven reliable for the rest of the slide (photos,
    text, badges), so it can't have that class of failure.

    Returns (frame_paths, frame_durations) — more entries than len(slides)
    when a slide has multiple animation sub-frames; durations sum to match
    the original per-slide audio durations exactly."""
    os.makedirs(work_dir, exist_ok=True)
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    def _rounded_mask(size, radius):
        m = Image.new("L", size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
        return m

    def get_font(size, bold=True):
        names = (
            ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf"]
            if bold else
            ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf"]
        )
        for path in names:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    def wrap_line(text_line, font, draw_ctx, max_w):
        words = text_line.split()
        if not words:
            return [text_line]
        out, cur = [], words[0]
        for word in words[1:]:
            test = cur + " " + word
            bb = draw_ctx.textbbox((0, 0), test, font=font)
            if (bb[2] - bb[0]) <= max_w:
                cur = test
            else:
                out.append(cur)
                cur = word
        out.append(cur)
        return out

    W, H = (1920, 1080) if landscape else (1080, 1920)
    PAD = 60
    MAX_TW = W - PAD * 2

    BG = (250, 249, 246)
    INK = (20, 20, 24)
    MUTED = (110, 110, 118)
    ACCENT = (21, 87, 61)  # deep money-green
    CARD_BORDER = (225, 223, 216)

    font_brand = get_font(34)
    font_counter = get_font(24, bold=False)
    font_headline = get_font(58)
    font_sub = get_font(30, bold=False)
    font_cta = get_font(42)
    font_label = get_font(30)

    total_slides = len(slides)
    if durations is None:
        durations = [4.0] * total_slides
    frame_paths, frame_durations = [], []

    CHAR_SCALE = 1.35

    def _stamp_mascot(img, pose, cx_frame, top_y, phase=0.0, idle_t=None):
        import math
        if pose == 'bounce':
            bounce_amt = int(55 * abs(math.sin(phase * 2 * math.pi * 2.5)))
            return _draw_character(img, cx_frame, top_y - bounce_amt,
                                   scale=CHAR_SCALE, pose='point_both')
        # Idle breathing: a slow 1-2px rise and fall while the character is
        # holding a pose. Without it a static slide renders 60 identical
        # frames a second, so a correctly-encoded 60fps video still looks
        # frozen. This makes every frame genuinely different.
        off = 0
        if idle_t is not None:
            off = int(round(4.0 * math.sin(idle_t * 2 * math.pi * 0.5)))
        return _draw_character(img, cx_frame, top_y - off, scale=CHAR_SCALE,
                               pose=pose, phase=phase)

    prev_cx = None
    slide_start_t = 0.0    # absolute video time, so idle motion is continuous

    # Every slide shows both terms side by side with individual labels,
    # like the reference channel's comparison style — only when we
    # actually have both hero images to show. The SYSTEM_PROMPT's 7-slide
    # arc puts Term A's own explanation at index 1 and Term B's at index
    # 2, so those slides swap in that slide's own fetched image on their
    # side while the other side keeps showing its most recent photo.
    have_heroes = bool(term_a and term_b and hero_images[0] and hero_images[1])
    left_by_idx, right_by_idx, side_by_idx = [], [], []
    if have_heroes:
        cur_left, cur_right = hero_images[0], hero_images[1]
        for i in range(total_slides):
            if i == 1 and i < len(images) and images[i]:
                cur_left = images[i]
                side = 'A'
            elif i == 2 and i < len(images) and images[i]:
                cur_right = images[i]
                side = 'B'
            else:
                side = 'both'
            left_by_idx.append(cur_left)
            right_by_idx.append(cur_right)
            side_by_idx.append(side)

    for idx, slide in enumerate(slides):
        bg = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(bg)

        # Brand header
        brand = "THE AI DOLLAR"
        bb = draw.textbbox((0, 0), brand, font=font_brand)
        draw.text(((W - (bb[2] - bb[0])) // 2, 50), brand, font=font_brand, fill=INK)

        counter = f"{idx + 1}/{total_slides}"
        cb = draw.textbbox((0, 0), counter, font=font_counter)
        draw.text((W - (cb[2] - cb[0]) - PAD, 58), counter, font=font_counter, fill=MUTED)

        # Progress bar
        bar_y = 105
        progress = (idx + 1) / total_slides
        draw.rectangle([PAD, bar_y, W - PAD, bar_y + 4], fill=(230, 228, 222))
        draw.rectangle([PAD, bar_y, PAD + int((W - PAD * 2) * progress), bar_y + 4], fill=ACCENT)

        is_dual = have_heroes
        is_diff_slide = (idx == 3 and is_dual)
        side = side_by_idx[idx] if is_dual else 'both'

        def _paste_card(cx0, ctop, cw, ch, src):
            radius = 26
            # Soft drop-shadow so the panels read as floating cards (premium
            # depth). Drawn on a padded RGBA layer, blurred once, then
            # composited slightly below the card.
            pad = 34
            shadow = Image.new("RGBA", (cw + pad * 2, ch + pad * 2), (0, 0, 0, 0))
            ImageDraw.Draw(shadow).rounded_rectangle(
                [pad, pad, pad + cw, pad + ch], radius=radius, fill=(18, 20, 28, 95)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(15))
            bg.paste(shadow, (cx0 - pad, ctop - pad + 12), shadow)

            if src and os.path.exists(src):
                photo = Image.open(src).convert("RGB")
                iw, ih = photo.size
                ratio = max(cw / iw, ch / ih)
                photo = photo.resize((int(iw * ratio), int(ih * ratio)), Image.LANCZOS)
                left = (photo.width - cw) // 2
                top = (photo.height - ch) // 2
                photo = photo.crop((left, top, left + cw, top + ch))
                bg.paste(photo, (cx0, ctop), _rounded_mask((cw, ch), radius))
            else:
                draw.rounded_rectangle([cx0, ctop, cx0 + cw, ctop + ch], radius=radius, fill=(240, 239, 234))

        panel_left_cx = panel_right_cx = None
        if is_dual:
            label_h = 46
            card_top = 150 + label_h
            card_h = int(H * 0.30)
            gap = 44
            card_w = (int(W * 0.82) - gap) // 2
            left_x = (W - (card_w * 2 + gap)) // 2
            right_x = left_x + card_w + gap
            panel_left_cx = left_x + card_w // 2
            panel_right_cx = right_x + card_w // 2

            for label, cx0 in ((term_a, left_x), (term_b, right_x)):
                lb = draw.textbbox((0, 0), label.upper(), font=font_label)
                lw_ = lb[2] - lb[0]
                draw.text((cx0 + (card_w - lw_) // 2, 150), label.upper(), font=font_label, fill=INK)

            _paste_card(left_x, card_top, card_w, card_h, left_by_idx[idx])
            _paste_card(right_x, card_top, card_w, card_h, right_by_idx[idx])

            # "VS" badge straddling the gap between the two panels — the
            # visual signature of the comparison format. Drawn last so it
            # sits on top of both cards' inner edges.
            vs_cx, vs_cy = W // 2, card_top + card_h // 2
            r = 46
            draw.ellipse([vs_cx - r - 6, vs_cy - r - 6, vs_cx + r + 6, vs_cy + r + 6], fill=BG)
            draw.ellipse([vs_cx - r, vs_cy - r, vs_cx + r, vs_cy + r], fill=ACCENT)
            vs_font = get_font(40)
            vsb = draw.textbbox((0, 0), "VS", font=vs_font)
            draw.text(
                (vs_cx - (vsb[2] - vsb[0]) // 2, vs_cy - (vsb[3] - vsb[1]) // 2 - vsb[1]),
                "VS", font=vs_font, fill=(255, 255, 255),
            )
        else:
            img_src = images[idx] if idx < len(images) else None
            card_top = 150
            card_h = int(H * 0.34)
            card_w = int(W * 0.78)
            card_x = (W - card_w) // 2
            _paste_card(card_x, card_top, card_w, card_h, img_src)

        # Mascot — right below the card(s). Not drawn into `bg` yet: it's
        # stamped per-animation-sub-frame further down (running while it
        # travels to whichever term is being explained, pointing once it
        # arrives) so the SAME background is reused for every sub-frame of
        # this slide instead of re-rendering photos/text repeatedly.
        mascot_top = card_top + card_h + 70
        is_last = (idx == len(slides) - 1)
        is_first = (idx == 0)

        # Where the character stands is driven by the SCRIPT ARC, not by
        # which images happened to load. The 7-slide structure is:
        #   0 hook | 1-2 Person A / Term A | 3-4 Person B / Term B
        #   5 verdict | 6 loop closer
        # Deriving it from image indices meant the character wandered and
        # pointed at panels that had nothing to do with the line being
        # spoken, which read as random movement.
        n_sl = len(slides)
        if n_sl >= 7:
            if idx in (1, 2):
                arc_side = 'A'
            elif idx in (3, 4):
                arc_side = 'B'
            else:
                arc_side = 'both'
        else:
            arc_side = side

        if arc_side == 'A' and panel_left_cx is not None:
            target_cx = panel_left_cx
        elif arc_side == 'B' and panel_right_cx is not None:
            target_cx = panel_right_cx
        else:
            target_cx = W // 2
        # Keep the whole character comfortably on screen: a pointing arm
        # reaches ~180px (at scale 1.0) from the body centre, so standing
        # directly under a side panel could push the hand off the frame.
        reach = int(180 * CHAR_SCALE) + 45
        target_cx = max(reach, min(W - reach, target_cx))

        # Fixed bottom-bound estimate (dry-run on a scratch canvas) so the
        # headline position below the mascot stays stable across every pose
        # this slide might use, instead of jittering per sub-frame.
        _scratch = Image.new("RGB", (4, 4))
        mascot_bottom = _draw_character(_scratch, -9999, mascot_top,
                                        scale=CHAR_SCALE, pose='calm')
        del _scratch

        # Caption — SHORT and BIG: at most 2 lines so it's readable in a
        # single glance (long paragraphs killed readability). Flatten any
        # line breaks, then pick the largest font that fits in <=2 lines.
        # Caption words come from the SPOKEN line, not the separate "text"
        # field — those were written independently by the model, so the
        # words on screen never matched what the narrator was saying. Using
        # the speech verbatim and pacing the chunks across the slide's own
        # audio duration keeps screen and voice in step.
        text = " ".join(slide['speech'].split()).upper()
        bottom_zone_top = mascot_bottom + 40
        available_h = H - bottom_zone_top - 140
        size = 96
        cap_y0 = bottom_zone_top + max(0, (available_h - size) // 2)

        # AUTO-HIGHLIGHT (karaoke) SUBTITLES: the whole spoken line stays on
        # screen and the word currently being said is highlighted in a
        # coloured pill, the highlight stepping along in time with the
        # narration. Chunk-replacement (only 1-3 words visible at a time)
        # was tried first, but it hides the sentence, so the viewer can't
        # read ahead and the line never reads as a sentence at all.
        cap_words = text.split()
        if not cap_words:
            cap_words = [""]

        # Pick the largest size at which the line wraps to at most 3 rows.
        _cap_fs, _cap_rows = 62, None
        for _try in (72, 66, 60, 54, 48, 42):
            _f = get_font(_try)
            rows, cur = [], []
            for w in cap_words:
                trial = cur + [w]
                bb = draw.textbbox((0, 0), " ".join(trial), font=_f)
                if (bb[2] - bb[0]) <= MAX_TW or not cur:
                    cur = trial
                else:
                    rows.append(cur)
                    cur = [w]
            if cur:
                rows.append(cur)
            if len(rows) <= 3:
                _cap_fs, _cap_rows = _try, rows
                break
        if _cap_rows is None:
            _f = get_font(42)
            _cap_rows = [cap_words[i:i + 4] for i in range(0, len(cap_words), 4)][:3]
            _cap_fs = 42

        # index of the first word on each row, so the active word can be found
        _row_starts, _n = [], 0
        for r in _cap_rows:
            _row_starts.append(_n)
            _n += len(r)

        def _draw_caption(img, word_idx, tscale=1.0, dx=0, dy=0):
            """Draw the full line with the active word highlighted. tscale
            scales only the active word, giving it a small pop as it lands."""
            dd = ImageDraw.Draw(img)
            ff = get_font(_cap_fs)
            stroke = max(3, int(_cap_fs * 0.13))
            space = int(_cap_fs * 0.30)
            line_h = int(_cap_fs * 1.28)
            total_h = line_h * len(_cap_rows)
            yy = cap_y0 - total_h // 2 + dy

            for ri, row in enumerate(_cap_rows):
                widths = []
                for w in row:
                    b = dd.textbbox((0, 0), w, font=ff, stroke_width=stroke)
                    widths.append(b[2] - b[0])
                total_w = sum(widths) + space * (len(row) - 1)
                xx = (W - total_w) // 2 + dx
                for wi, (w, wd) in enumerate(zip(row, widths)):
                    gi = _row_starts[ri] + wi
                    if gi == word_idx:
                        # highlight pill behind the word being spoken
                        pad_x, pad_y = int(_cap_fs * 0.16), int(_cap_fs * 0.10)
                        dd.rounded_rectangle(
                            [xx - pad_x, yy - pad_y,
                             xx + wd + pad_x, yy + _cap_fs + pad_y],
                            radius=int(_cap_fs * 0.22),
                            fill=_word_colour(w) if _word_colour(w) != CAP_WHITE else ACCENT)
                        dd.text((xx, yy), w, font=ff, fill=(255, 255, 255),
                                stroke_width=stroke, stroke_fill=INK)
                    else:
                        dd.text((xx, yy), w, font=ff, fill=CAP_WHITE,
                                stroke_width=stroke, stroke_fill=INK)
                    xx += wd + space
                yy += line_h

        if is_first:
            hook = "WATCH TIL THE END"
            hb = draw.textbbox((0, 0), hook, font=font_sub)
            hw = hb[2] - hb[0]
            hx = (W - hw) // 2
            hy = H - 90
            draw.rounded_rectangle([hx - 24, hy - 10, hx + hw + 24, hy + 36], radius=14, fill=ACCENT)
            draw.text((hx, hy), hook, font=font_sub, fill=(255, 255, 255))

        if is_last:
            cta = "FOLLOW FOR MORE"
            cb2 = draw.textbbox((0, 0), cta, font=font_cta)
            cw = cb2[2] - cb2[0]
            cx2 = (W - cw) // 2
            cy2 = H - 100
            draw.rounded_rectangle([cx2 - 30, cy2 - 16, cx2 + cw + 30, cy2 + 46], radius=16, fill=ACCENT)
            draw.text((cx2, cy2), cta, font=font_cta, fill=(255, 255, 255))

        # `bg` is now the finished background (photos/text/badges), mascot
        # NOT yet drawn. Build this slide's animation sub-frames: bounce on
        # the hook, run while the target changes, then hold a pointing (or
        # confused, on the differentiation slide) pose for the rest.
        del draw
        slide_dur = durations[idx] if idx < len(durations) else 4.0
        moved = (prev_cx is not None and target_cx != prev_cx)
        RAMP = min(1.1, slide_dur * 0.45)   # long enough to read as walking

        settled_pose = (
            'point_both' if (n_sl >= 7 and idx == 5) else   # the verdict names both
            'calm' if (is_last or arc_side == 'both') else
            ('point_left' if arc_side == 'A' else 'point_right')
        )

        def _mascot_at(t):
            """(pose, phase, cx) for the mascot at time t within this slide."""
            if is_first:
                return ('bounce', t / max(slide_dur, 0.01), target_cx)
            if moved and t < RAMP:
                fr = t / RAMP
                # ease in/out so the walk starts and stops naturally rather
                # than snapping to full speed
                eased = fr * fr * (3.0 - 2.0 * fr)
                return ('walk', (fr * 3.0) % 1.0,
                        int(prev_cx + (target_cx - prev_cx) * eased))
            return (settled_pose, 0.0, target_cx)

        # The highlight advances one WORD at a time, each word holding for a
        # share of the slide weighted by its length, so longer words linger
        # and the highlight tracks the narration instead of drifting.
        n_words = len(cap_words)
        weights = [max(2, len(w)) for w in cap_words]
        w_total = sum(weights)
        bounds, acc = [], 0.0
        for wt in weights:
            share = slide_dur * (wt / w_total)
            bounds.append((acc, acc + share))
            acc += share

        # Frame budget is spent where motion actually happens. Sampling the
        # character's walk at the output framerate keeps it genuinely
        # smooth, while a settled character emits ONE frame that simply
        # holds — nothing is moving during it, so extra frames buy nothing.
        MOTION_STEP = 1.0 / 60.0   # matches the 60fps output exactly

        # Every slide is now sampled at the full output framerate, including
        # holds, so no run of identical frames is ever emitted.
        sub_frames = []   # (pose, phase, cx, word_idx, idle_t, dur)
        for ci in range(n_words):
            c_start, c_end = bounds[ci]
            t = c_start
            while t < c_end - 1e-3:
                mp, mph, mcx = _mascot_at(t)
                d = min(MOTION_STEP, c_end - t)
                idle_t = None if mp in ('walk', 'bounce') else (slide_start_t + t)
                sub_frames.append((mp, mph, mcx, ci, idle_t, d))
                t += d

        # Frames are keyed on everything that can change; identical ones are
        # written once and re-referenced in the concat list. With idle
        # breathing active almost every frame is now distinct, so the cache
        # mostly matters for the rare exact repeat.
        cache = {}
        for k, (pose, phase, cx_frame, ci, idle_t, dur) in enumerate(sub_frames):
            key = (pose, round(phase, 3), cx_frame, ci,
                   None if idle_t is None else round(idle_t, 2))
            fp = cache.get(key)
            if fp is None:
                frame = bg.copy()
                _stamp_mascot(frame, pose, cx_frame, mascot_top, phase, idle_t)
                _draw_caption(frame, ci, 1.0, 0, 0)
                fp = os.path.join(work_dir, f"info_{idx}_{k}.jpg")
                frame.save(fp, "JPEG", quality=88)
                del frame
                cache[key] = fp
            frame_paths.append(fp)
            frame_durations.append(dur)

        prev_cx = target_cx
        slide_start_t += slide_dur
        del bg
        gc.collect()
        print(f"  infographic slide {idx+1}/{len(slides)} ready "
              f"({len(sub_frames)} steps, {len(cache)} unique frames)")

    return frame_paths, frame_durations


def create_video_infographic(slides, images, audio_file, durations, output_file, landscape=False,
                              term_a=None, term_b=None, hero_images=(None, None)):
    """Single-pass build (lightweight, matches the original static-slide
    pipeline's memory profile) using the new white-background layout. The
    mascot (running between panels, pointing once it arrives, bouncing on
    the hook) is drawn directly into the frames by prep_infographic_slides —
    no ffmpeg-side overlay/alpha trickery, which twice silently failed on
    Render's ffmpeg build in production despite working locally."""
    work_dir = output_file + "_infowork"
    import shutil
    print("[BUILD] Preparing infographic slides...")

    res = "1920:1080" if landscape else "1080:1920"

    frame_paths, frame_durations = prep_infographic_slides(
        images, slides, work_dir, landscape=landscape,
        term_a=term_a, term_b=term_b, hero_images=hero_images,
        durations=durations,
    )
    n = len(frame_paths)

    concat_file = os.path.join(work_dir, "concat.txt")
    with open(concat_file, 'w') as f:
        for idx in range(n):
            f.write(f"file '{os.path.basename(frame_paths[idx])}'\n")
            f.write(f"duration {frame_durations[idx]:.3f}\n")
        f.write(f"file '{os.path.basename(frame_paths[n-1])}'\n")

    # loudnorm brings the narration up to a clear, consistent broadcast
    # loudness (YouTube/TikTok target ~-14 LUFS) instead of whatever raw
    # level the TTS engine happened to output.
    loudnorm = "loudnorm=I=-14:LRA=11:TP=-1.5"

    # Quiet original music bed under the narration. Optional by design: if
    # it can't be produced we still ship the video with clean narration
    # rather than failing the whole build. Disable with BG_MUSIC=false.
    music_path = None
    if os.getenv("BG_MUSIC", "true").lower() != "false":
        total_len = sum(frame_durations) + 1.0
        candidate = os.path.join(work_dir, "bgmusic.m4a")
        if generate_bg_music(candidate, total_len):
            music_path = candidate

    if music_path:
        # No sidechain ducking. Two rounds of it (ratio 8 then 4) still left
        # the bed inaudible, because narration is near-continuous in a 28s
        # short so the compressor was holding the music down for essentially
        # the whole video. A fixed, deliberately modest level is audible the
        # entire time and cannot be pumped away; amix normalize=0 stops
        # ffmpeg from halving both inputs when it sums them.
        filter_complex = (
            f"[0:v]scale={res},fps=60[v];"
            f"[1:a]{loudnorm}[narr];"
            f"[2:a]volume=1.0[bg];"
            f"[narr][bg]amix=inputs=2:duration=first:normalize=0[aout]"
        )
        inputs = ['-i', audio_file, '-i', music_path]
    else:
        filter_complex = f"[0:v]scale={res},fps=60[v];[1:a]{loudnorm}[aout]"
        inputs = ['-i', audio_file]

    cmd = [
        FFMPEG, '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_file,
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[v]', '-map', '[aout]',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-movflags', '+faststart',
        output_file
    ]

    import shutil
    proc = _run_ffmpeg_hard_timeout(cmd, timeout=600)

    if music_path and (proc is None or proc.returncode != 0):
        # Never let the optional music bed break the build — retry clean.
        print("[WARN] Music mix failed, rebuilding with narration only...")
        cmd = [
            FFMPEG, '-y',
            '-f', 'concat', '-safe', '0', '-i', concat_file,
            '-i', audio_file,
            '-filter_complex', f"[0:v]scale={res},fps=60[v];[1:a]{loudnorm}[aout]",
            '-map', '[v]', '-map', '[aout]',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-movflags', '+faststart',
            output_file
        ]
        proc = _run_ffmpeg_hard_timeout(cmd, timeout=600)

    if proc is None:
        shutil.rmtree(work_dir, ignore_errors=True)
        print("[WARN] Infographic build: ffmpeg encode timed out")
        return False

    shutil.rmtree(work_dir, ignore_errors=True)

    if proc.returncode != 0:
        stderr = proc.stderr.decode('utf-8', errors='replace')[-500:]
        print(f"[WARN] Infographic build failed: {stderr}")
        return False

    print("[OK] Video created (infographic style)!")
    return True


def create_video_ffmpeg(slides, images, audio_file, durations, output_file, landscape=False):
    valid_images = [img for img in images if img is not None]
    if not valid_images:
        return create_video_simple(slides, audio_file, durations, output_file, landscape=landscape)

    work_dir = output_file + "_work"
    print("[BUILD] Preparing slides...")
    prep_slides(images, slides, durations, work_dir, landscape=landscape)

    n = len(slides)
    audio_duration = get_audio_duration(audio_file)
    res = "1920:1080" if landscape else "1080:1920"

    print("[BUILD] Creating video (single-pass concat + audio)...")
    concat_file = os.path.join(work_dir, "concat.txt")
    with open(concat_file, 'w') as f:
        for idx in range(n):
            f.write(f"file 's_{idx}.jpg'\n")
            f.write(f"duration {durations[idx]:.2f}\n")
        f.write(f"file 's_{n-1}.jpg'\n")

    bg_music_path = os.path.join(work_dir, "bgmusic.m4a")
    has_music = generate_bg_music(bg_music_path, audio_duration + 2)

    if has_music:
        cmd = [
            FFMPEG, '-y',
            '-f', 'concat', '-safe', '0', '-i', concat_file,
            '-i', audio_file,
            '-i', bg_music_path,
            '-filter_complex',
            f'[0:v]scale={res},fps=30[v];[2:a]volume=0.10[bg];[1:a][bg]amix=inputs=2:duration=first[aout]',
            '-map', '[v]', '-map', '[aout]',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
                        '-movflags', '+faststart',
            output_file
        ]
    else:
        cmd = [
            FFMPEG, '-y',
            '-f', 'concat', '-safe', '0', '-i', concat_file,
            '-i', audio_file,
            '-vf', f'scale={res},fps=30',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
                        '-movflags', '+faststart',
            output_file
        ]

    proc = subprocess.run(cmd, capture_output=True, timeout=600)

    import shutil
    shutil.rmtree(work_dir, ignore_errors=True)

    if proc.returncode != 0:
        stderr = proc.stderr.decode('utf-8', errors='replace')[-500:]
        print(f"[WARN] FFmpeg failed: {stderr}")
        return create_video_simple(slides, audio_file, durations, output_file)

    print("[OK] Video created!")
    return True


def create_video_simple(slides, audio_file, durations, output_file, landscape=False):
    """Fallback: solid color background with audio, no text."""
    total_dur = sum(durations)
    size = "1920x1080" if landscape else "1080x1920"
    cmd = [
        FFMPEG, '-y',
        '-f', 'lavfi', '-i', f'color=c=0x0C0C28:size={size}:rate=30:d={total_dur:.2f}',
        '-i', audio_file,
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
                '-movflags', '+faststart',
        output_file
    ]
    print("[BUILD] Running FFmpeg (simple mode)...")
    proc = subprocess.run(cmd, capture_output=True, timeout=240)
    if proc.returncode != 0:
        return False
    print("[OK] Video created (simple mode)")
    return True


def generate_daily_video():
    topic = generate_short_topic()
    slides = topic['slides']

    os.makedirs(CONFIG['output_dir'], exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"{CONFIG['output_dir']}/the_ai_dollar_{timestamp}.mp4"
    audio_dir = f"{CONFIG['output_dir']}/audio_{timestamp}"
    img_dir = f"{CONFIG['output_dir']}/imgs_{timestamp}"

    try:
        print("[TTS] Generating per-slide audio...")
        slide_result = create_slide_audios(slides, audio_dir)

        if slide_result:
            audio_file, durations = slide_result
            total_dur = sum(durations)
            print(f"[OK] Per-slide audio: {len(durations)} segments, {total_dur:.1f}s total")
        else:
            print("[WARN] Per-slide audio failed, using single voiceover...")
            audio_file = os.path.join(audio_dir, "full_audio.mp3")
            os.makedirs(audio_dir, exist_ok=True)
            full_text = ' '.join(s['speech'] for s in slides)
            create_audio(full_text, audio_file)
            total_dur = get_audio_duration(audio_file)
            per_slide = total_dur / len(slides)
            durations = [per_slide] * len(slides)

        print("[IMG] Fetching HD images...")
        images = fetch_hd_images(slides, img_dir)
        print(f"[OK] Got {sum(1 for i in images if i)} images")

        term_a = topic.get('term_a')
        term_b = topic.get('term_b')
        hero_images = (None, None)
        if term_a and term_b:
            hero_images = fetch_term_hero_images(
                term_a, term_b, img_dir,
                icon_a=topic.get('icon_a'), icon_b=topic.get('icon_b'))
            print(f"[OK] Hero images: {term_a}={'yes' if hero_images[0] else 'no'}, {term_b}={'yes' if hero_images[1] else 'no'}")

        ok = False
        if os.getenv("USE_INFOGRAPHIC_STYLE", "true").lower() != "false":
            print("[VIDEO] Creating video with infographic style...")
            ok = create_video_infographic(
                slides, images, audio_file, durations, output_file,
                term_a=term_a, term_b=term_b, hero_images=hero_images,
            )
            if not ok:
                print("[WARN] Infographic build failed, falling back to Ken Burns...")

        if not ok and os.getenv("USE_KEN_BURNS", "true").lower() != "false":
            print("[VIDEO] Creating video with Ken Burns motion...")
            ok = create_video_kenburns(slides, images, audio_file, durations, output_file)
            if not ok:
                print("[WARN] Ken Burns build failed, falling back to static slides...")

        if not ok:
            print("[VIDEO] Creating animated video...")
            ok = create_video_ffmpeg(slides, images, audio_file, durations, output_file)

        if not ok:
            return {"status": "error", "message": "Video creation failed"}

        print(f"[OK] Video created: {output_file}")

        voiceover_text = ' '.join(s['speech'] for s in slides)

        try:
            import shutil
            shutil.rmtree(audio_dir, ignore_errors=True)
            shutil.rmtree(img_dir, ignore_errors=True)
        except Exception:
            pass

        return {
            "status": "success",
            "video": output_file,
            "title": topic['title'],
            "script": voiceover_text,
            "keywords": topic['keywords']
        }

    except Exception as e:
        print(f"[ERR] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


def generate_thumbnail(title, first_image, output_path):
    """Generate a high-CTR 1920x1080 YouTube thumbnail with bold text + face/emotion."""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

        W, H = 1920, 1080

        def get_font(size):
            for path in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf",
                         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
            return ImageFont.load_default()

        if first_image and os.path.exists(first_image):
            bg = Image.open(first_image).convert("RGB")
            iw, ih = bg.size
            ratio = max(W / iw, H / ih)
            bg = bg.resize((int(iw * ratio), int(ih * ratio)), Image.LANCZOS)
            left = (bg.width - W) // 2
            top = (bg.height - H) // 2
            bg = bg.crop((left, top, left + W, top + H))
        else:
            bg = Image.new("RGB", (W, H), (12, 12, 40))

        bg = ImageEnhance.Contrast(bg).enhance(1.3)
        bg = ImageEnhance.Color(bg).enhance(1.2)

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        for x in range(W):
            frac = x / W
            a = int(200 * frac)
            ov_draw.rectangle([x, 0, x + 1, H], fill=(0, 0, 0, min(a, 200)))
        for gy in range(int(H * 0.7), H):
            frac = (gy - H * 0.7) / (H * 0.3)
            a = int(180 * frac)
            ov_draw.rectangle([0, gy, W, gy + 1], fill=(0, 0, 0, min(a, 180)))
        bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

        draw = ImageDraw.Draw(bg)

        YELLOW = (255, 230, 0)
        WHITE = (255, 255, 255)

        words = title.upper().split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid]) if mid > 0 else title.upper()
        line2 = " ".join(words[mid:]) if mid > 0 else ""

        text_x = W // 2 + 100
        max_tw = W - text_x - 60

        for fsize in [110, 96, 82, 72, 60]:
            ft = get_font(fsize)
            bb1 = draw.textbbox((0, 0), line1, font=ft)
            w1 = bb1[2] - bb1[0]
            if line2:
                bb2 = draw.textbbox((0, 0), line2, font=ft)
                w2 = bb2[2] - bb2[0]
            else:
                w2 = 0
            if max(w1, w2) <= max_tw:
                break

        total_h = fsize * 2 + 20 if line2 else fsize
        y_start = (H - total_h) // 2

        for ox in range(-4, 5):
            for oy in range(-4, 5):
                if ox * ox + oy * oy <= 16:
                    draw.text((text_x + ox, y_start + oy), line1, font=ft, fill=(0, 0, 0))
        draw.text((text_x, y_start), line1, font=ft, fill=YELLOW)

        if line2:
            y2 = y_start + fsize + 20
            for ox in range(-4, 5):
                for oy in range(-4, 5):
                    if ox * ox + oy * oy <= 16:
                        draw.text((text_x + ox, y2 + oy), line2, font=ft, fill=(0, 0, 0))
            draw.text((text_x, y2), line2, font=ft, fill=WHITE)

        brand_font = get_font(36)
        brand = "THE AI DOLLAR"
        draw.rounded_rectangle([text_x - 10, H - 90, text_x + 320, H - 40], radius=8, fill=(220, 20, 20))
        draw.text((text_x + 10, H - 84), brand, font=brand_font, fill=WHITE)

        draw.rectangle([0, 0, W, 6], fill=YELLOW)
        draw.rectangle([0, H - 6, W, H], fill=YELLOW)

        bg.save(output_path, "JPEG", quality=95)
        print(f"[OK] Thumbnail generated: {output_path}")
        return output_path
    except Exception as e:
        print(f"[WARN] Thumbnail generation failed: {e}")
        return None


def generate_long_video():
    topic = generate_long_topic()
    slides = topic['slides']
    os.makedirs(CONFIG['output_dir'], exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"{CONFIG['output_dir']}/the_ai_dollar_long_{timestamp}.mp4"
    audio_dir = f"{CONFIG['output_dir']}/audio_long_{timestamp}"
    img_dir = f"{CONFIG['output_dir']}/imgs_long_{timestamp}"
    thumb_path = f"{CONFIG['output_dir']}/thumb_long_{timestamp}.jpg"

    try:
        print("[TTS] Generating per-slide audio (long-form)...")
        slide_result = create_slide_audios(slides, audio_dir)

        if slide_result:
            audio_file, durations = slide_result
            total_dur = sum(durations)
            print(f"[OK] Per-slide audio: {len(durations)} segments, {total_dur:.1f}s total")
        else:
            print("[WARN] Per-slide audio failed, using single voiceover...")
            audio_file = os.path.join(audio_dir, "full_audio.mp3")
            os.makedirs(audio_dir, exist_ok=True)
            full_text = ' '.join(s['speech'] for s in slides)
            create_audio(full_text, audio_file)
            total_dur = get_audio_duration(audio_file)
            per_slide = total_dur / len(slides)
            durations = [per_slide] * len(slides)

        print("[IMG] Fetching HD landscape images (long-form)...")
        images = fetch_hd_images(slides, img_dir, landscape=True)
        print(f"[OK] Got {sum(1 for i in images if i)} images")

        print("[THUMB] Generating YouTube thumbnail...")
        first_img = next((img for img in images if img), None)
        generate_thumbnail(topic['title'], first_img, thumb_path)

        print("[VIDEO] Creating long-form video (1920x1080)...")
        ok = create_video_ffmpeg(slides, images, audio_file, durations, output_file, landscape=True)

        if not ok:
            return {"status": "error", "message": "Long video creation failed"}

        print(f"[OK] Long video created: {output_file}")

        voiceover_text = ' '.join(s['speech'] for s in slides)

        try:
            import shutil
            shutil.rmtree(audio_dir, ignore_errors=True)
            shutil.rmtree(img_dir, ignore_errors=True)
        except Exception:
            pass

        return {
            "status": "success",
            "video": output_file,
            "title": topic['title'],
            "script": voiceover_text,
            "keywords": topic['keywords'],
            "is_long": True,
            "thumbnail": thumb_path if os.path.exists(thumb_path) else None,
        }

    except Exception as e:
        print(f"[ERR] Long video error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
