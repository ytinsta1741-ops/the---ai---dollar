import random
import hashlib
import json
import os
from datetime import datetime

from ai_topic_generator import generate_ai_topic

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# THE AI DOLLAR — INFINITE VIRAL TOPIC GENERATOR
# Never repeats. Every video is unique. CTR-optimized titles.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── TITLE TEMPLATES (curiosity gap + social proof + specific numbers) ──
# {person} {amount} {time} {method} {emotion} {age} {job} are placeholders

SHORT_TITLE_TEMPLATES = [
    "{person} Makes ${amount}/Month From {method} (Here's How)",
    "I Tried {method} For {time} — Made ${amount}",
    "A {job} Saved ${amount} In {time} (Stupid Simple Strategy)",
    "Why {percent}% Of People Will Never Be Rich (Are You One?)",
    "${amount} Per Day Turns Into ${big_amount} (Most People Don't Know This)",
    "Never {bad_habit} Again — It Costs You ${amount} Per Year",
    "{person} Went From Broke To ${amount} In {time}",
    "The ${small_amount} Trick That Builds ${big_amount} In {time}",
    "I Asked {count} Millionaires Their #1 Rule — Same Answer Every Time",
    "{age} Year Old Makes ${amount}/Month While Sleeping",
    "Banks Don't Want You To Know This ${amount} Trick",
    "Stop {bad_habit} — You're Losing ${amount} Every Year",
    "How {person} Retired At {age} With ${big_amount}",
    "The {time} Challenge That Changed My Finances Forever",
    "{count} Money Rules That Separate Rich From Poor",
    "This {method} Pays ${amount}/Month — Takes {time} To Set Up",
    "Why Your {expense} Is Keeping You Broke (Fix It Today)",
    "A {job} Makes ${amount}/Month On The Side (No Degree Needed)",
    "If You Make Under ${amount}, Do THIS Immediately",
    "The #{count} Reason You're Still Broke (It's Not Your Salary)",
    "{person} Lost Everything Then Made ${big_amount} In {time}",
    "Your ${expense_amount} {expense} Habit Costs ${big_amount} Over {long_time}",
    "I Lived On ${small_amount}/Month And STILL Invested ${amount}",
    "{famous_person}'s Money Rule Will Change Your Life",
    "This Account Pays {percent}% — Most People Have No Idea",
    "The {age}-Year-Old Who Built A ${big_amount} Empire From ${small_amount}",
    "Do This BEFORE {deadline} Or Lose Thousands",
    "{country} People Save {percent}% Of Income — Here's Their Secret",
    "My ${amount}/Month Side Hustle Takes {minutes} Minutes Per Day",
    "The Investing Mistake That Cost Me ${amount} (Don't Do This)",
    "This Side Hustle Pays ${amount}/Month — Nobody Talks About It",
    "Rich People Do THIS Every Morning (Broke People Never Do)",
    "I Tried Living On ${small_amount}/Day For {time} — Here's What Happened",
    "The {time} Money Challenge That Made Me ${amount} Richer",
    "STOP Scrolling — This {method} Trick Changes EVERYTHING",
    "A {age} Year Old Discovered THIS And Made ${amount} In {time}",
    "Banks Are HIDING This From You (${amount} Strategy)",
    "Why {percent}% Of Millionaires Drive Used Cars (Not What You Think)",
    "This Is The #1 Side Hustle Of {year} (${amount}/Month Proof)",
    "I Asked AI How To Make ${amount} — It Gave Me THIS Plan",
    "The Broke Person's Guide To ${big_amount} (No BS Strategy)",
    "{person} Quit Their Job At {age} — Now Makes ${amount}/Month Online",
    "POV: You Follow These {count} Rules And Retire At {age}",
    "The ${small_amount} Per Week Hack That Builds ${big_amount}",
    "Nobody Told Me THIS About Money Until I Was {age} (Too Late?)",
    "This Is Why You're STILL Broke (Fix It In {time})",
    "I Tested {count} Money Strategies — Only {small_count} Actually Work",
    "The Ugly Truth About {method} (What Gurus Won't Tell You)",
    "How To Turn ${small_amount} Into ${big_amount} (Step By Step)",
    "The {age} Year Old Millionaire's Daily Routine (Copy This)",
    "I Made ${amount} In {time} — Here's My Exact Blueprint",
    "{famous_person} Says Do THIS With Your Money RIGHT NOW",
    "The {method} Nobody Talks About (${amount}/Month Potential)",
    "Watch This BEFORE You {bad_habit} Again (It's Costing You ${amount})",
    "${amount} Invested At {age} = ${big_amount} By Retirement (Math Proof)",
    "I STOPPED {bad_habit} For {time} And Saved ${amount} (Not Clickbait)",
    "5 Things Rich People NEVER Spend Money On (Surprising)",
    "What Happens When You Invest ${small_amount}/Day For {long_time}?",
    "The Financial Advice Your Parents Got WRONG (Don't Repeat It)",
    "I Gave A {job} My ${big_amount} Investment Plan — They Were Shocked",
    "You're {time} Away From Financial Freedom (Do This NOW)",
    "Rich At {age}? Follow These {count} Non-Negotiable Rules",
    "How A {job} Built ${big_amount} Net Worth On ${amount}/Month Salary",
    "{person}'s ${amount} Side Hustle Takes {minutes} Min/Day (Proof Inside)",
    "If You're Under {age}, This Video Is Worth ${big_amount} To You",
    "The Money Mistake {percent}% Of Americans Make Every Single Day",
    "This FREE {method} Strategy Made Me ${amount} Last Month",
    "BROKE At {age}? Here's Your Exact {time} Comeback Plan",
    "The ${small_amount}/Week Rule That Creates Millionaires",
    "Why {famous_person} Refuses To {bad_habit} (And You Should Too)",
]

# ── STORY PERSONAS ──
PERSONAS = [
    {"name": "Sarah", "job": "nurse", "age": 28, "story": "working double shifts"},
    {"name": "Marcus", "job": "teacher", "age": 32, "story": "supporting a family of four"},
    {"name": "James", "job": "janitor", "age": 55, "story": "earning minimum wage"},
    {"name": "Priya", "job": "college student", "age": 21, "story": "drowning in student loans"},
    {"name": "Kevin", "job": "uber driver", "age": 34, "story": "living paycheck to paycheck"},
    {"name": "Lisa", "job": "single mom", "age": 30, "story": "raising two kids alone"},
    {"name": "Daniel", "job": "warehouse worker", "age": 26, "story": "with no college degree"},
    {"name": "Ana", "job": "waitress", "age": 24, "story": "earning tips and minimum wage"},
    {"name": "Tyler", "job": "mechanic", "age": 38, "story": "with $40K in debt"},
    {"name": "Maria", "job": "housekeeper", "age": 45, "story": "an immigrant who spoke no English"},
    {"name": "Jordan", "job": "barista", "age": 22, "story": "fresh out of college"},
    {"name": "Derek", "job": "delivery driver", "age": 29, "story": "who quit his corporate job"},
    {"name": "Nina", "job": "freelancer", "age": 27, "story": "working from a tiny apartment"},
    {"name": "Chris", "job": "security guard", "age": 40, "story": "on the night shift"},
    {"name": "Emma", "job": "retail worker", "age": 23, "story": "making $12 per hour"},
    {"name": "Mike", "job": "plumber", "age": 36, "story": "running his own one-man business"},
    {"name": "Aisha", "job": "pharmacy tech", "age": 25, "story": "working night shifts to pay rent"},
    {"name": "Brandon", "job": "construction worker", "age": 31, "story": "supporting his parents back home"},
    {"name": "Rosa", "job": "hotel cleaner", "age": 42, "story": "a single mom working two jobs"},
    {"name": "Jason", "job": "fast food manager", "age": 27, "story": "with zero financial education"},
    {"name": "Fatima", "job": "daycare worker", "age": 33, "story": "earning barely above minimum wage"},
    {"name": "Alex", "job": "graphic designer", "age": 24, "story": "freelancing with inconsistent income"},
    {"name": "Tony", "job": "truck driver", "age": 44, "story": "on the road 60 hours a week"},
    {"name": "Keisha", "job": "cashier", "age": 20, "story": "saving for college with no family help"},
]

# ── FAMOUS PEOPLE WITH MONEY LESSONS ──
FAMOUS_PEOPLE = [
    {"name": "Warren Buffett", "rule": "never lose money", "lesson": "invest in what you understand", "worth": "100 billion"},
    {"name": "Mark Cuban", "rule": "save before you spend", "lesson": "live like a student until you can afford not to", "worth": "5 billion"},
    {"name": "Dave Ramsey", "rule": "avoid all debt", "lesson": "the debt snowball method works because it's behavioral", "worth": "200 million"},
    {"name": "Robert Kiyosaki", "rule": "buy assets not liabilities", "lesson": "your house is not an asset if it costs you money", "worth": "100 million"},
    {"name": "Suze Orman", "rule": "pay yourself first", "lesson": "people first then money then things", "worth": "75 million"},
    {"name": "Grant Cardone", "rule": "increase income not just cut expenses", "lesson": "you can't save your way to wealth", "worth": "600 million"},
    {"name": "Naval Ravikant", "rule": "build assets that earn while you sleep", "lesson": "code and media are new leverage anyone can use", "worth": "unknown billions"},
    {"name": "Charlie Munger", "rule": "avoid stupidity instead of seeking brilliance", "lesson": "invert always invert when solving money problems", "worth": "2 billion"},
    {"name": "Peter Lynch", "rule": "invest in what you know", "lesson": "the best stock ideas come from your daily life", "worth": "450 million"},
    {"name": "Benjamin Graham", "rule": "margin of safety", "lesson": "buy a dollar for fifty cents", "worth": "pioneer of value investing"},
    {"name": "Elon Musk", "rule": "think in first principles", "lesson": "break problems down to fundamentals instead of following convention", "worth": "250 billion"},
    {"name": "Jeff Bezos", "rule": "think long term always", "lesson": "your margin is my opportunity", "worth": "150 billion"},
    {"name": "Oprah Winfrey", "rule": "invest in yourself first", "lesson": "the biggest investment you can make is in your own abilities", "worth": "2.5 billion"},
    {"name": "Jay-Z", "rule": "own don't rent", "lesson": "you're not a businessman you're a business man", "worth": "2.5 billion"},
    {"name": "Sara Blakely", "rule": "embrace failure as data", "lesson": "my dad asked us what we failed at this week and celebrated it", "worth": "1.2 billion"},
    {"name": "Kevin O'Leary", "rule": "never spend more than you make", "lesson": "money equals freedom and if you don't control it you don't control your life", "worth": "400 million"},
    {"name": "Tony Robbins", "rule": "automate and diversify", "lesson": "the secret to wealth is simple make your money work harder than you do", "worth": "600 million"},
    {"name": "Daymond John", "rule": "be broke not poor", "lesson": "broke is temporary poor is a mindset", "worth": "350 million"},
    {"name": "Barbara Corcoran", "rule": "use other people's money smartly", "lesson": "the joy is in the getting not the having", "worth": "100 million"},
]

# ── MONEY METHODS / STRATEGIES ──
METHODS = [
    {"name": "index fund investing", "effort": "30 minutes per month", "min_start": 50, "potential": "1 million in 30 years"},
    {"name": "dividend investing", "effort": "1 hour per week", "min_start": 100, "potential": "5000 per month passive"},
    {"name": "high yield savings", "effort": "10 minutes to set up", "min_start": 1, "potential": "5 percent interest"},
    {"name": "Roth IRA", "effort": "set it and forget it", "min_start": 50, "potential": "tax free millionaire"},
    {"name": "the 50/30/20 budget", "effort": "15 minutes per week", "min_start": 0, "potential": "save 20 percent automatically"},
    {"name": "side hustle stacking", "effort": "2 hours per day", "min_start": 0, "potential": "3000 to 10000 per month"},
    {"name": "credit card rewards hacking", "effort": "smart spending", "min_start": 0, "potential": "2000 per year in free money"},
    {"name": "house hacking", "effort": "live in one unit rent others", "min_start": 5000, "potential": "live for free"},
    {"name": "automated savings", "effort": "5 minutes once", "min_start": 10, "potential": "12000 per year painlessly"},
    {"name": "debt avalanche method", "effort": "same payments different order", "min_start": 0, "potential": "save thousands in interest"},
    {"name": "freelancing on Fiverr", "effort": "nights and weekends", "min_start": 0, "potential": "2000 to 8000 per month"},
    {"name": "selling digital products", "effort": "create once sell forever", "min_start": 0, "potential": "passive income machine"},
    {"name": "the no-spend challenge", "effort": "30 days of discipline", "min_start": 0, "potential": "save 1000 to 3000 in one month"},
    {"name": "flipping items on eBay", "effort": "weekends at thrift stores", "min_start": 50, "potential": "500 to 2000 per month"},
    {"name": "cashback apps stacking", "effort": "scan receipts", "min_start": 0, "potential": "600 per year for doing nothing"},
    {"name": "print on demand", "effort": "design once sell forever", "min_start": 0, "potential": "1000 to 5000 per month passive"},
    {"name": "YouTube automation", "effort": "faceless channel", "min_start": 0, "potential": "3000 to 20000 per month"},
    {"name": "digital course creation", "effort": "create once sell unlimited", "min_start": 0, "potential": "5000 to 50000 per month"},
    {"name": "Amazon KDP publishing", "effort": "write or outsource ebooks", "min_start": 0, "potential": "1000 to 10000 per month"},
    {"name": "real estate wholesaling", "effort": "find deals connect buyers", "min_start": 0, "potential": "5000 to 20000 per deal"},
    {"name": "dropshipping", "effort": "run online store no inventory", "min_start": 100, "potential": "2000 to 15000 per month"},
    {"name": "social media management", "effort": "manage accounts for businesses", "min_start": 0, "potential": "2000 to 6000 per month per client"},
    {"name": "stock photography", "effort": "upload photos earn royalties", "min_start": 0, "potential": "500 to 3000 per month passive"},
    {"name": "newsletter monetization", "effort": "build email list sell ads", "min_start": 0, "potential": "1000 to 10000 per month"},
]

# ── BAD MONEY HABITS ──
BAD_HABITS = [
    {"habit": "buying coffee daily", "daily_cost": 6, "yearly_cost": 2190, "thirty_year_cost": "500,000 invested"},
    {"habit": "eating out for lunch", "daily_cost": 15, "yearly_cost": 5475, "thirty_year_cost": "1.2 million invested"},
    {"habit": "impulse shopping on Amazon", "daily_cost": 10, "yearly_cost": 3650, "thirty_year_cost": "800,000 invested"},
    {"habit": "paying only minimum on credit cards", "daily_cost": 0, "yearly_cost": 3000, "thirty_year_cost": "200,000 in interest alone"},
    {"habit": "not negotiating your salary", "daily_cost": 0, "yearly_cost": 7500, "thirty_year_cost": "500,000 in lost earnings"},
    {"habit": "subscribing to things you don't use", "daily_cost": 5, "yearly_cost": 1825, "thirty_year_cost": "400,000 invested"},
    {"habit": "buying new cars", "daily_cost": 20, "yearly_cost": 7300, "thirty_year_cost": "1.6 million invested"},
    {"habit": "keeping money in a checking account", "daily_cost": 3, "yearly_cost": 1000, "thirty_year_cost": "losing to inflation"},
    {"habit": "lifestyle creep after every raise", "daily_cost": 0, "yearly_cost": 5000, "thirty_year_cost": "1 million in missed wealth"},
    {"habit": "paying for a gym you never go to", "daily_cost": 2, "yearly_cost": 720, "thirty_year_cost": "150,000 invested"},
    {"habit": "brand name everything", "daily_cost": 8, "yearly_cost": 2920, "thirty_year_cost": "640,000 invested"},
    {"habit": "not tracking expenses", "daily_cost": 10, "yearly_cost": 3600, "thirty_year_cost": "780,000 in wasted money"},
]

# ── MONEY FACTS / SHOCKING STATS ──
MONEY_FACTS = [
    {"fact": "78% of Americans live paycheck to paycheck", "follow_up": "Even people making six figures are one emergency away from disaster"},
    {"fact": "The average American has $8,000 in credit card debt", "follow_up": "At 20% interest that takes 25 YEARS to pay off with minimums"},
    {"fact": "Only 39% of Americans can cover a $1,000 emergency", "follow_up": "The other 61% go into debt or sell something"},
    {"fact": "Millionaires drive Toyotas and Hondas not Ferraris", "follow_up": "The Millionaire Next Door proved most wealthy people look ordinary"},
    {"fact": "90% of millionaires are first generation", "follow_up": "They didn't inherit it they built it from nothing"},
    {"fact": "A 1% fee on investments costs you $590,000 over 40 years", "follow_up": "Index funds charge 0.03% while financial advisors charge 1%"},
    {"fact": "The average millionaire goes bankrupt 3.5 times", "follow_up": "Failure is literally part of the wealth building process"},
    {"fact": "People who write financial goals are 42% more likely to achieve them", "follow_up": "Your brain treats written goals differently than thoughts"},
    {"fact": "The S&P 500 has returned 10.5% per year for 100 years", "follow_up": "Every crash recovered and hit new highs within a few years"},
    {"fact": "$1 invested in 1926 would be worth $11,000 today", "follow_up": "That is the power of compound interest over time"},
    {"fact": "70% of wealthy families lose their fortune by the second generation", "follow_up": "Money without financial education is temporary"},
    {"fact": "The average car payment is $716 per month in America", "follow_up": "That $716 invested monthly becomes 2 million in 30 years"},
]

# ── SLIDE FRAMEWORKS (story structures for 10-slide shorts) ──
SLIDE_FRAMEWORKS = {
    "person_story": [
        {"role": "hook", "template": "{person_name} was a {job}\n{story_detail}\nmaking ${low_salary}/year"},
        {"role": "struggle", "template": "Every month\nthe same cycle:\nearning → spending →\nNOTHING left\n${debt} in debt"},
        {"role": "cta", "template": "FOLLOW for the\nfull strategy\nThis changed\nEVERYTHING"},
        {"role": "discovery", "template": "Then {pronoun} discovered\n{method_name}\nand everything\nchanged"},
        {"role": "action1", "template": "Step 1:\n{action_step_1}"},
        {"role": "result_big", "template": "After {long_time}:\n${big_result}\nnet worth\nFrom a {job}'s salary"},
        {"role": "loop", "template": "Want the next\nmoney story?\nWatch again or\nswipe to the next one"},
    ],
    "myth_buster": [
        {"role": "hook", "template": "Everything you\nknow about\n{topic} is WRONG"},
        {"role": "myth1", "template": "Myth 1:\n{myth_1}\nREALITY:\n{reality_1}"},
        {"role": "cta", "template": "FOLLOW to stop\nbelieving money\nmyths that keep\nyou BROKE"},
        {"role": "myth2", "template": "Myth 2:\n{myth_2}\nREALITY:\n{reality_2}"},
        {"role": "shocking_stat", "template": "SHOCKING FACT:\n{fact}\n{follow_up}"},
        {"role": "simple_fix", "template": "The simple fix:\n{fix_step_1}\n{fix_step_2}"},
        {"role": "loop", "template": "Which myth did\nyou believe?\nComment below\nWatch again"},
    ],
    "money_math": [
        {"role": "hook", "template": "Your ${daily_cost}\n{expense}\nhabit is costing\nyou ${lifetime_cost}"},
        {"role": "daily_breakdown", "template": "${daily_cost} per day\n= ${monthly_cost}/month\n= ${yearly_cost}/year\nSeems small right?"},
        {"role": "cta", "template": "FOLLOW for more\nmind-blowing\nmoney math\nthat saves you\nTHOUSANDS"},
        {"role": "compound_reveal", "template": "But invested at\n{percent}% per year\nfor {years} years\nthat becomes\n${compound_total}"},
        {"role": "alternative", "template": "The swap:\nInstead of {old_habit}\ndo {new_habit}\nSave ${save_amount}/month"},
        {"role": "future_result", "template": "In {years} years:\n${future_value}\nFrom ONE simple\nswap"},
        {"role": "loop", "template": "Your ${daily_cost}\nhabit is still\ncosting you\nWatch again\nand MAKE the swap"},
    ],
    "rules_list": [
        {"role": "hook", "template": "{count} Money Rules\nThat Separate\nRICH from POOR"},
        {"role": "rule1", "template": "Rule 1:\n{rule_1}\n{rule_1_explain}"},
        {"role": "rule2", "template": "Rule 2:\n{rule_2}\n{rule_2_explain}"},
        {"role": "cta", "template": "FOLLOW for all\n{count} rules\nMost people miss\nrule #{count}"},
        {"role": "rule3", "template": "Rule 3:\n{rule_3}\n{rule_3_explain}"},
        {"role": "common_mistake", "template": "The #1 mistake:\n{big_mistake}\nThis alone keeps\npeople BROKE"},
        {"role": "loop", "template": "How many rules\ndo YOU follow?\nWatch again and\nCOUNT them"},
    ],
    "famous_person": [
        {"role": "hook", "template": "{famous_name} said\nthis ONE thing\nabout money and\nit changed\nEVERYTHING"},
        {"role": "quote", "template": "The rule:\n\"{money_rule}\"\nSimple but\nMOST people\nignore it"},
        {"role": "cta", "template": "FOLLOW for more\nbillionaire money\nrules that\nactually WORK"},
        {"role": "backstory", "template": "{famous_name} is worth\n${net_worth}\nBuilt from\n{origin_story}"},
        {"role": "apply_it", "template": "How to apply\nthis TODAY:\n{apply_step_1}\n{apply_step_2}"},
        {"role": "result", "template": "If you follow\nthis rule:\n${potential_result}\nin {result_time}"},
        {"role": "loop", "template": "{famous_name} said\nONE thing...\nDid you\ncatch it?"},
    ],
    "age_timeline": [
        {"role": "hook", "template": "At {age_start} you should\nhave ${amount_start}\nsaved\nDo you?"},
        {"role": "age_20", "template": "By age 20:\n${goal_20} saved\nHow: {how_20}"},
        {"role": "age_25", "template": "By age 25:\n${goal_25} saved\nHow: {how_25}"},
        {"role": "cta", "template": "FOLLOW to see\nif YOU are\non track\nor behind"},
        {"role": "age_30", "template": "By age 30:\n${goal_30} saved\nHow: {how_30}"},
        {"role": "behind", "template": "Behind?\nDON'T PANIC\nHere's how to\ncatch up FAST"},
        {"role": "loop", "template": "At {age_start} you should\nhave ${amount_start}\nDo you?\nCheck again"},
    ],
    "side_hustle": [
        {"role": "hook", "template": "This side hustle\npays ${amount}/month\nand takes\n{time_required}\nto set up"},
        {"role": "what", "template": "It's called:\n{hustle_name}\nand ANYONE\ncan start it"},
        {"role": "cta", "template": "FOLLOW for a\nnew side hustle\nEVERY day\nAll FREE to start"},
        {"role": "step1", "template": "Step 1:\n{setup_step_1}\nThis takes\n{step1_time}"},
        {"role": "step2", "template": "Step 2:\n{setup_step_2}\nFREE tools\nonly"},
        {"role": "month3", "template": "Month 3:\n${month3_amount}/month\nConsistency\nis the secret"},
        {"role": "loop", "template": "This pays\n${amount}/month\nDid you catch\nall the steps?\nWatch again"},
    ],
    "rich_vs_poor": [
        {"role": "hook", "template": "Rich people do\nTHIS every day\nBroke people\ndo the OPPOSITE"},
        {"role": "habit1_rich", "template": "Rich:\n{rich_habit_1}\nBroke:\n{poor_habit_1}"},
        {"role": "habit2_rich", "template": "Rich:\n{rich_habit_2}\nBroke:\n{poor_habit_2}"},
        {"role": "cta", "template": "FOLLOW to learn\nwhat rich people\ndo differently\nEVERY day"},
        {"role": "habit3_rich", "template": "Rich:\n{rich_habit_3}\nBroke:\n{poor_habit_3}"},
        {"role": "why_matters", "template": "Same 24 hours\nDifferent CHOICES\nDifferent RESULTS"},
        {"role": "loop", "template": "Rich do THIS\nBroke do\nthe OPPOSITE\nWhich one\nare YOU?"},
    ],
    "money_challenge": [
        {"role": "hook", "template": "Try this {duration}\nmoney challenge\nand save ${save_goal}\nGuaranteed."},
        {"role": "rules", "template": "The rules:\n{rule_1}\n{rule_2}\n{rule_3}\nThat's IT"},
        {"role": "cta", "template": "FOLLOW for\nmore money\nchallenges that\nACTUALLY work"},
        {"role": "week1", "template": "Week 1:\n{week1_action}\nDifficulty: Easy\nSaved: ${week1_saved}"},
        {"role": "results", "template": "RESULTS:\n${total_saved} saved\nin just {duration}\nFrom ZERO effort"},
        {"role": "what_changed", "template": "But the REAL win:\n{mindset_change}\nThis changes\nEVERYTHING"},
        {"role": "loop", "template": "Save ${save_goal}\nin {duration}\nWatch again for\nthe EXACT rules"},
    ],
    "secret_strategy": [
        {"role": "hook", "template": "This {who} strategy\nis hidden in\nplain sight\nand it builds\n${result} quietly"},
        {"role": "what_is_it", "template": "The strategy:\n{strategy_name}\nUsed by the\ntop {percent}%"},
        {"role": "cta", "template": "FOLLOW for more\nhidden strategies\nthe wealthy use\nEVERY day"},
        {"role": "how_step1", "template": "How it works:\nStep 1: {step_1}\nTakes {time_1}"},
        {"role": "real_numbers", "template": "Real numbers:\n${start_amount}/month\nfor {years} years\n= ${end_amount}"},
        {"role": "start_now", "template": "You can start\nwith ${min_amount}\nRIGHT NOW\nNo excuses"},
        {"role": "loop", "template": "This builds\n${result} quietly\nDid you catch\nthe strategy?\nWatch again"},
    ],
}

# ── SPEECH TEMPLATES (matching slide frameworks) ──
SPEECH_TEMPLATES = {
    "person_story": [
        "Stop scrolling. {person_name} was a {job}, {story_detail}, making just {low_salary} thousand dollars a year. What happened next will blow your mind.",
        "Every month it was the same cycle. Earn, spend, nothing left. {debt} thousand dollars in debt. Zero savings. Sound familiar?",
        "Follow for the full strategy. This is the money move that changes EVERYTHING. Most people will never learn this.",
        "Then {pronoun} discovered {method_name}. Not a get rich quick scheme. A REAL strategy. {speech_action_1}. This alone changed the game.",
        "Step two. {speech_action_2}. Most people skip this but it's the most important part.",
        "After {long_time}, {big_result} dollars net worth. A {job}. Let that sink in. The math doesn't lie.",
        "Want the next money story? Watch this again. Share it. Follow The AI Dollar for a new one every single day.",
    ],
    "myth_buster": [
        "Wait. Everything you KNOW about {topic} is completely WRONG. I can prove it in thirty seconds.",
        "Myth number one. {myth_1}. WRONG. The reality? {reality_1}. This myth alone keeps millions broke.",
        "Follow now because myth number two is even worse. Most people believe this their ENTIRE life and stay poor.",
        "Myth number two. {myth_2}. Also WRONG. {reality_2}. Your parents probably told you this one.",
        "SHOCKING fact. {fact}. {follow_up}. Let that sink in.",
        "The fix is simple. {fix_step_1}. Then {fix_step_2}. That's it. No magic required.",
        "Which myth did YOU believe? Comment below. Watch again and share this with someone who needs it.",
    ],
    "money_math": [
        "Don't skip this. Your {daily_cost} dollar {expense} habit costs you {lifetime_cost} dollars. I'll prove it with math right now.",
        "{daily_cost} per day. {monthly_cost} per month. {yearly_cost} per year. Seems small? Watch what happens next.",
        "Follow for more mind blowing money math. This next number will change how you spend money FOREVER.",
        "Invested at {percent} percent for {years} years, compound interest turns it into {compound_total} dollars. From just one habit.",
        "The swap. Instead of {old_habit}, do {new_habit}. Save {save_amount} dollars per month. Set it and forget it.",
        "In {years} years, {future_value} dollars. You're not giving up {expense}. You're BUYING your freedom.",
        "Your {daily_cost} dollar habit is STILL costing you. Watch this again. Make the swap TODAY.",
    ],
    "rules_list": [
        "Listen. {count} money rules that separate rich from poor. Rule three changed everything for me.",
        "Rule one. {rule_1}. {rule_1_explain}. This is the foundation of ALL wealth.",
        "Rule two. {rule_2}. {rule_2_explain}. Most people do the exact opposite.",
        "Follow for all {count} rules. Most people miss the next one and stay broke forever.",
        "Rule three. {rule_3}. {rule_3_explain}. This one saves you THOUSANDS every year.",
        "The number one mistake? {big_mistake}. Fix THIS and everything else gets easier.",
        "How many rules do YOU follow? Watch again. Count them. Follow for more every day.",
    ],
    "famous_person": [
        "{famous_name} said ONE thing about money that changed everything. Most people completely ignore it.",
        "The rule. {money_rule}. Worth BILLIONS. Yet most people hear it and do nothing.",
        "Follow for more billionaire money rules. The next one is even more powerful than this.",
        "{famous_name} is worth {net_worth} dollars. Built from {origin_story}. This isn't theory. This is proven.",
        "Apply it TODAY. First, {apply_step_1}. Second, {apply_step_2}. That's it. Start winning.",
        "Follow this rule consistently. {potential_result} dollars in {result_time}. The math is real.",
        "{famous_name} said ONE thing. Did you catch it? Watch again. Your wallet will thank you.",
    ],
    "age_timeline": [
        "At age {age_start}, you should have {amount_start} dollars saved. Do you? Keep watching.",
        "By twenty, {goal_20} dollars. How? {how_20}. This sets the foundation for everything.",
        "By twenty five, {goal_25} dollars. How? {how_25}. This is where momentum kicks in.",
        "Follow to see if you're on track or behind. The next number might shock you.",
        "By thirty, {goal_30} dollars. {how_30}. Behind? DON'T PANIC.",
        "Behind? {catchup_1}. Starting at {late_age}? {late_start} per month still becomes {late_result} by sixty five.",
        "At {age_start} you should have {amount_start}. Do you? Check again. Start TODAY not tomorrow.",
    ],
    "side_hustle": [
        "This side hustle pays {amount} dollars per month. Takes {time_required} to set up. No degree needed.",
        "It's called {hustle_name}. ANYONE can start it. Zero experience needed. Here's how.",
        "Follow for a new side hustle EVERY day. All free to start. The next one pays even more.",
        "Step one. {setup_step_1}. Takes {step1_time}. Step two. {setup_step_2}. Free tools only.",
        "Step three. {setup_step_3}. This is where money starts flowing into your account.",
        "Month three. {month3_amount} per month consistently. Because consistency is the real secret.",
        "This pays {amount} per month. Did you catch all the steps? Watch again. Start this week.",
    ],
    "rich_vs_poor": [
        "Rich people do THIS every day. Broke people do the EXACT opposite. Same twenty four hours. Watch closely.",
        "Rich people {rich_habit_1}. Broke people? {poor_habit_1}. This ONE difference compounds into millions.",
        "Rich people {rich_habit_2}. Broke people {poor_habit_2}. And here's what nobody tells you...",
        "Follow to learn what rich people do differently EVERY single day. Habit three separates the top one percent.",
        "Rich people {rich_habit_3}. Broke people {poor_habit_3}. Same hours. Different choices. Different results.",
        "The switch. Pick ONE rich habit. Replace ONE broke habit. Do it thirty days. That's the entire plan.",
        "Rich do THIS. Broke do the opposite. Which one are YOU? Watch again. Comment below.",
    ],
    "money_challenge": [
        "Try this {duration} challenge and save {save_goal} dollars. GUARANTEED. Follow the rules. The money appears.",
        "The rules. {rule_1}. {rule_2}. {rule_3}. That's IT. No apps. No spreadsheets. Just three rules.",
        "Follow for more money challenges that actually work. This next part is the real game changer.",
        "Week one. {week1_action}. Easy. Saved {week1_saved} dollars. Your brain starts rewiring immediately.",
        "Results. {total_saved} dollars saved in {duration}. Zero effort. Zero suffering. Just smart choices.",
        "But the REAL win. {mindset_change}. Your relationship with money completely changes. THAT is priceless.",
        "Save {save_goal} in {duration}. Watch again for the exact rules. Start TODAY not Monday.",
    ],
    "secret_strategy": [
        "This {who} strategy hides in plain sight. Nobody talks about it. But it builds {result} dollars while you sleep.",
        "The strategy. {strategy_name}. Used by the top {percent} percent. Most won't tell you about it.",
        "Follow for more hidden strategies the wealthy use every day. The next one is even more powerful.",
        "Step one. {step_1}. Takes {time_1}. This is where ninety percent of people quit. Don't be them.",
        "Real numbers. {start_amount} per month for {years} years equals {end_amount} dollars. Not a typo.",
        "Start with just {min_amount} dollars. RIGHT NOW. No excuses. The hardest part is step one.",
        "This builds {result} quietly. Did you catch the strategy? Watch again. Follow for more every day.",
    ],
}

# ── IMAGE PROMPTS PER ROLE ──
IMAGE_PROMPTS = {
    "hook": ["person looking shocked at phone screen", "dramatic reveal moment", "jaw dropping reaction to news"],
    "struggle": ["stressed person looking at bills", "empty wallet flat lay", "person overwhelmed by debt papers"],
    "discovery": ["lightbulb moment person excited", "person reading life changing book", "breakthrough moment celebration"],
    "action1": ["person setting up budget on laptop", "organized financial planning desk", "person taking first step confidently"],
    "action2": ["person cutting unnecessary expenses", "automatic savings setup on phone", "disciplined person following a plan"],
    "action3": ["investment portfolio on screen growing", "person investing money wisely", "compound interest graph going up"],
    "result_early": ["person checking growing savings happily", "small wins celebration", "first milestone achievement"],
    "result_big": ["wealthy person lifestyle simple and rich", "large investment portfolio display", "financial freedom celebration"],
    "lesson": ["wise mentor sharing advice", "key takeaway highlight graphic", "simple powerful lesson illustration"],
    "cta": ["person starting investment journey today", "phone showing investment app signup", "motivated person taking action now"],
    "myth1": ["common money myth being busted", "wrong financial advice crossed out", "truth versus myth comparison"],
    "myth2": ["another myth debunked", "reality check financial education", "myth vs fact side by side"],
    "myth3": ["third myth shattered", "outdated money advice torn up", "new financial truth revealed"],
    "shocking_stat": ["shocking statistic displayed dramatically", "eye opening data visualization", "mind blowing financial fact"],
    "what_rich_do": ["wealthy person daily habits", "millionaire morning routine", "rich vs poor habits comparison"],
    "simple_fix": ["easy solution step by step", "simple fix for money problems", "quick financial improvement plan"],
    "proof": ["proof with real numbers and data", "chart showing real results", "before and after financial transformation"],
    "mindset": ["growth mindset versus fixed mindset", "wealthy thinking pattern", "abundance mindset illustration"],
    "daily_breakdown": ["daily expense breakdown calculator", "small spending adding up visual", "money leaking from wallet slowly"],
    "compound_reveal": ["compound interest curve dramatic reveal", "exponential growth chart", "money multiplying over time"],
    "comparison": ["comparison of what money could buy", "opportunity cost illustration", "alternative use of money visual"],
    "not_just_one": ["multiple expenses adding up", "spending categories pie chart", "total waste calculation"],
    "alternative": ["smart swap healthy alternative", "better choice comparison", "frugal but happy lifestyle"],
    "invest_it": ["automatic investment setup on phone", "money flowing into investment account", "index fund growing steadily"],
    "future_result": ["future wealthy self visualization", "long term investment result", "retirement on the beach"],
    "perspective": ["perspective shift on spending", "freedom versus pleasure comparison", "long term thinking illustration"],
    "rule1": ["first money rule golden text", "financial rule number one", "foundation of wealth building"],
    "rule2": ["second money rule", "important financial principle", "wealth rule on chalkboard"],
    "rule3": ["third money rule", "saving rule illustration", "money management principle"],
    "rule4": ["fourth money rule", "investing principle", "smart money habit"],
    "rule5": ["fifth money rule", "final wealth rule", "top money principle"],
    "common_mistake": ["biggest money mistake red flag", "financial error warning sign", "common mistake everyone makes"],
    "rich_vs_poor": ["rich versus poor daily choices", "different lifestyle comparison", "wealth gap choices"],
    "start_today": ["starting today motivation", "first step on wealth journey", "taking action right now"],
    "quote": ["famous quote on elegant background", "powerful words about money", "billionaire wisdom text"],
    "backstory": ["famous person success journey", "rags to riches story", "building an empire from nothing"],
    "explain": ["concept explained simply", "clear explanation diagram", "breaking down complex idea"],
    "example": ["real world example", "practical demonstration", "everyday application of rule"],
    "mistake": ["critical mistake to avoid", "warning about common error", "mistake that costs thousands"],
    "apply_it": ["applying advice right now", "action plan checklist", "practical steps to follow"],
    "result": ["potential result visualization", "what could happen if you start", "future outcome projection"],
    "other_billionaires": ["multiple successful people collage", "billionaires who agree", "consensus among the wealthy"],
    "age_20": ["twenty year old starting to save", "young person first job savings", "early twenties financial start"],
    "age_25": ["twenty five year old investing", "mid twenties financial milestone", "quarter life wealth building"],
    "age_30": ["thirty year old financial check", "thirties investment portfolio", "age thirty money goals"],
    "age_40": ["forty year old wealth status", "midlife financial assessment", "age forty savings target"],
    "behind": ["person catching up financially", "not too late motivation", "starting late but still winning"],
    "catch_up_1": ["aggressive savings strategy", "catching up on retirement", "accelerated wealth building"],
    "catch_up_2": ["income boost side hustle", "additional income strategy", "extra money earning method"],
    "compound_power": ["compound interest at any age", "late start still works", "math proof starting late"],
    "what": ["side hustle revealed exciting", "money making opportunity unveiled", "business idea lightbulb moment"],
    "why_works": ["reasons this works explained", "proof this business model works", "success factors breakdown"],
    "step1": ["first step getting started", "beginner taking action", "simple setup process"],
    "step2": ["second step building momentum", "tools and resources setup", "progress being made"],
    "step3": ["third step scaling up", "money starting to flow in", "system working automatically"],
    "week1": ["first week small earnings", "early results proof of concept", "small wins celebration"],
    "month3": ["three month results impressive", "consistent income growing", "momentum building wealth"],
    "scale": ["scaling business to next level", "growth strategy implementation", "multiplying income streams"],
    "habit1_rich": ["wealthy person morning routine", "rich daily habit comparison", "successful person discipline"],
    "habit2_rich": ["investing habit wealthy people", "smart money decision", "rich person reading about finance"],
    "habit3_rich": ["wealth building daily practice", "rich mindset in action", "top one percent habits"],
    "habit4_rich": ["financial discipline daily", "wealthy person simple lifestyle", "smart spending choices"],
    "habit5_rich": ["game changing money habit", "ultimate wealth building practice", "millionaire daily routine"],
    "why_matters": ["choices lead to results", "same hours different outcomes", "decision making power"],
    "the_switch": ["switching habits transformation", "old habit to new habit", "thirty day challenge start"],
    "rules": ["challenge rules simple list", "three simple rules displayed", "clear instructions on screen"],
    "week2": ["second week progress", "building momentum savings", "challenge getting easier"],
    "week3": ["third week habit forming", "automatic behavior change", "challenge becoming natural"],
    "week4": ["final week strong finish", "challenge completion celebration", "savings goal reached"],
    "results": ["impressive results revealed", "before and after savings", "challenge total displayed"],
    "what_changed": ["mindset transformation moment", "internal shift visualization", "new relationship with money"],
    "next_level": ["leveling up the challenge", "scaling savings annually", "long term impact projection"],
    "what_is_it": ["secret strategy revealed", "hidden wealth building method", "strategy used by wealthy"],
    "why_hidden": ["reason strategy is unknown", "not sexy but effective", "boring but profitable"],
    "how_step1": ["first step secret strategy", "getting started quietly", "simple beginning powerful end"],
    "how_step2": ["key move in strategy", "critical step wealth building", "the turning point action"],
    "how_step3": ["letting compound interest work", "passive growth visualization", "time doing the work"],
    "real_numbers": ["actual numbers on screen", "math proof real calculation", "compound growth result"],
    "who_uses": ["quietly wealthy people", "real millionaires no flex", "ordinary looking rich people"],
    "start_now": ["starting with small amount", "no excuses just start", "first dollar invested today"],
}

# ── MONEY RULES POOL ──
MONEY_RULES = [
    {"rule": "Spend less than you earn", "explain": "The gap between income and expenses is where ALL wealth is built"},
    {"rule": "Automate your savings", "explain": "If you have to think about saving you won't do it make it automatic"},
    {"rule": "Never carry credit card debt", "explain": "At 20% interest credit cards are the fastest way to stay poor"},
    {"rule": "Invest in index funds", "explain": "They beat 90% of professional fund managers and cost almost nothing"},
    {"rule": "Build an emergency fund first", "explain": "3 to 6 months of expenses so one bad month doesn't ruin you"},
    {"rule": "Increase income not just cut costs", "explain": "There's a floor to cutting but no ceiling to earning"},
    {"rule": "Pay yourself first not last", "explain": "Saving what's left over means saving nothing invest before you spend"},
    {"rule": "Avoid lifestyle inflation", "explain": "When you earn more save more don't spend more"},
    {"rule": "Never invest in what you don't understand", "explain": "If you can't explain it to a 10 year old don't put money in it"},
    {"rule": "Time in the market beats timing the market", "explain": "Nobody can predict crashes just invest consistently and hold"},
    {"rule": "Track every dollar", "explain": "You can't improve what you don't measure know where your money goes"},
    {"rule": "Live on last month's income", "explain": "Always be one month ahead so you're never stressed about bills"},
    {"rule": "Have multiple income streams", "explain": "One paycheck is a single point of failure millionaires average 7 sources"},
    {"rule": "Buy assets not liabilities", "explain": "Assets put money in your pocket liabilities take it out"},
    {"rule": "Set financial goals with deadlines", "explain": "A goal without a deadline is just a wish write it down with a date"},
]

# ── MYTH TOPICS ──
MYTH_SETS = [
    {
        "topic": "saving money",
        "myths": [
            {"myth": "You need to earn more to save more", "reality": "People earning 200K are still broke because they SPEND more not save more"},
            {"myth": "Saving means sacrificing everything fun", "reality": "It means being INTENTIONAL not deprived just cut waste not joy"},
            {"myth": "A savings account is the best place for money", "reality": "At 0.01% interest your money LOSES value to inflation every day"},
        ],
    },
    {
        "topic": "investing",
        "myths": [
            {"myth": "Investing is only for rich people", "reality": "You can start with ONE DOLLAR on apps like Fidelity or Schwab"},
            {"myth": "You need to pick individual stocks", "reality": "Index funds outperform 90% of professional stock pickers"},
            {"myth": "The stock market is like gambling", "reality": "Over any 20 year period in history the market has ALWAYS gone up"},
        ],
    },
    {
        "topic": "getting rich",
        "myths": [
            {"myth": "Rich people got lucky or inherited it", "reality": "90% of millionaires are FIRST generation they built it themselves"},
            {"myth": "You need a high paying job to be wealthy", "reality": "A janitor died with 8 million from just investing consistently"},
            {"myth": "You need to be smart to build wealth", "reality": "You need to be DISCIPLINED which is a choice not a talent"},
        ],
    },
    {
        "topic": "debt",
        "myths": [
            {"myth": "All debt is bad debt", "reality": "A mortgage on a rental property that cash flows is GOOD debt it makes you richer"},
            {"myth": "Paying minimum on loans is fine", "reality": "A 30K student loan at minimum payments costs you 60K total in interest"},
            {"myth": "You should pay off all debt before investing", "reality": "If your debt is under 6% interest you should invest AND pay debt simultaneously"},
        ],
    },
    {
        "topic": "retirement",
        "myths": [
            {"myth": "Social Security will take care of you", "reality": "Average Social Security payment is 1800 per month try living on that"},
            {"myth": "You need a million dollars to retire", "reality": "With the 4% rule 500K gives you 20K per year plus Social Security"},
            {"myth": "You can catch up on retirement savings later", "reality": "Starting at 25 vs 35 with the same amount means DOUBLE the money at 65"},
        ],
    },
    {
        "topic": "credit cards",
        "myths": [
            {"myth": "Credit cards are evil and you should avoid them", "reality": "Used right credit cards give you FREE money in cashback and rewards"},
            {"myth": "Carrying a balance improves your credit score", "reality": "This is 100% FALSE pay your balance in FULL every month"},
            {"myth": "Closing old cards helps your credit", "reality": "Closing cards HURTS your score by reducing your credit history length"},
        ],
    },
]

# ── EXPENSE COMPARISONS ──
EXPENSE_MATH = [
    {"expense": "coffee", "daily": 6, "monthly": 180, "yearly": 2190, "expense_2": "lunch out", "expense_3": "snacks", "combined": 8760,
     "investment": "an S&P 500 index fund", "years": 30, "percent": 10, "compound": "394,000", "comparisons": ["buy a house down payment", "retire 5 years early", "pay for your kid's college"]},
    {"expense": "eating out", "daily": 15, "monthly": 450, "yearly": 5475, "expense_2": "delivery fees", "expense_3": "tips on takeout", "combined": 9000,
     "investment": "a total market index fund", "years": 25, "percent": 10, "compound": "590,000", "comparisons": ["buy a rental property", "become a half millionaire", "generate 2000 per month in dividends"]},
    {"expense": "unused subscriptions", "daily": 5, "monthly": 150, "yearly": 1825, "expense_2": "streaming services", "expense_3": "app purchases", "combined": 4200,
     "investment": "a Roth IRA", "years": 35, "percent": 10, "compound": "487,000", "comparisons": ["retire tax free", "travel the world for years", "never worry about money again"]},
    {"expense": "new car payments", "daily": 24, "monthly": 716, "yearly": 8592, "expense_2": "full coverage insurance", "expense_3": "depreciation", "combined": 15000,
     "investment": "index funds", "years": 20, "percent": 10, "compound": "490,000", "comparisons": ["buy a house in cash", "start your own business", "achieve complete financial freedom"]},
    {"expense": "impulse Amazon orders", "daily": 8, "monthly": 240, "yearly": 2880, "expense_2": "fast fashion", "expense_3": "gadgets you never use", "combined": 7500,
     "investment": "a diversified portfolio", "years": 30, "percent": 10, "compound": "517,000", "comparisons": ["become a half millionaire", "generate passive income for life", "retire a decade early"]},
    {"expense": "brand name everything", "daily": 7, "monthly": 210, "yearly": 2555, "expense_2": "designer clothes", "expense_3": "premium gas in a regular car", "combined": 6500,
     "investment": "a target date retirement fund", "years": 30, "percent": 10, "compound": "456,000", "comparisons": ["quit your job forever", "live off dividends", "leave wealth for your family"]},
]

# ── AGE TIMELINE DATA ──
AGE_TIMELINES = [
    {"start_age": 20, "goals": {"20": "5,000", "25": "25,000", "30": "100,000", "40": "400,000"},
     "how": {"20": "Save 200 per month from your first job", "25": "Invest 500 per month in index funds", "30": "Max out your Roth IRA every year", "40": "Compound interest does 80% of the work now"},
     "catchup": ["Increase income with a side hustle and invest 100% of extra earnings", "Cut your 3 biggest expenses and redirect ALL savings to investments"],
     "late": {"start": 300, "age": 35, "result": "450,000"}},
    {"start_age": 25, "goals": {"20": "2,000", "25": "20,000", "30": "80,000", "40": "350,000"},
     "how": {"20": "Put birthday and holiday money in a savings account", "25": "Start your 401k and get the FULL employer match", "30": "Have 1x your salary saved and invested", "40": "Have 3x your salary in retirement accounts"},
     "catchup": ["Automate 25% of every paycheck into investments starting TODAY", "Negotiate a raise or switch jobs for a 20% salary bump"],
     "late": {"start": 500, "age": 40, "result": "380,000"}},
]

# ── SIDE HUSTLE DATA ──
SIDE_HUSTLES = [
    {"name": "freelance writing", "amount": "3,000", "time": "one weekend", "steps": ["Create a portfolio with 3 sample articles", "Sign up on Upwork Fiverr and Contently", "Apply to 10 jobs per day for the first week"], "week1": 150, "month3": 2500, "scaled": "8,000", "scale": "Hire writers and become an agency", "reasons": ["Businesses ALWAYS need content", "You can work from anywhere in the world"]},
    {"name": "print on demand t-shirts", "amount": "2,000", "time": "2 hours", "steps": ["Create designs using free Canva templates", "Upload to Redbubble Merch by Amazon and TeePublic", "Make 50 designs in your first month"], "week1": 30, "month3": 1500, "scaled": "5,000", "scale": "Use trending niches and scale to 500 designs", "reasons": ["Zero inventory zero shipping zero risk", "Designs sell while you sleep forever"]},
    {"name": "social media management", "amount": "4,000", "time": "one day", "steps": ["Learn scheduling tools like Buffer or Later", "Reach out to 20 local businesses this week", "Offer first month at 50 percent off to build portfolio"], "week1": 200, "month3": 3000, "scaled": "10,000", "scale": "Get 5 clients and hire a virtual assistant", "reasons": ["Every business needs social media", "Recurring monthly income not one time"]},
    {"name": "Amazon KDP ebooks", "amount": "2,500", "time": "one week", "steps": ["Research profitable niches on Amazon bestsellers", "Write or outsource a 10000 word ebook", "Create a cover using Canva and publish"], "week1": 50, "month3": 2000, "scaled": "7,000", "scale": "Publish one new book every two weeks", "reasons": ["Books sell forever with zero extra work", "Amazon does ALL the marketing for you"]},
    {"name": "YouTube faceless channel", "amount": "5,000", "time": "3 days", "steps": ["Pick a niche like finance facts or scary stories", "Use AI voiceover and stock footage", "Upload 3 videos per week consistently"], "week1": 0, "month3": 500, "scaled": "15,000", "scale": "Run multiple channels in different niches", "reasons": ["Videos earn money YEARS after posting", "No face no voice just content and cash"]},
    {"name": "virtual bookkeeping", "amount": "3,500", "time": "2 weeks of learning", "steps": ["Learn QuickBooks basics with free YouTube courses", "Get certified through QuickBooks ProAdvisor free", "Find clients on local Facebook groups"], "week1": 100, "month3": 2500, "scaled": "8,000", "scale": "Hire junior bookkeepers and manage 15 clients", "reasons": ["Small businesses desperately need this", "Recurring income every single month"]},
    {"name": "flipping items from thrift stores", "amount": "2,000", "time": "this Saturday", "steps": ["Visit 3 thrift stores and look for brands", "List items on eBay Poshmark or Facebook Marketplace", "Start with clothes electronics and books"], "week1": 200, "month3": 2000, "scaled": "6,000", "scale": "Hit estate sales and liquidation auctions", "reasons": ["Buy for 3 dollars sell for 30 dollars", "You get PAID to go shopping"]},
    {"name": "AI prompt engineering", "amount": "4,000", "time": "one day of practice", "steps": ["Master ChatGPT Claude and Midjourney prompts", "Create prompt packs and sell on Gumroad", "Offer prompt consulting to businesses"], "week1": 100, "month3": 3000, "scaled": "10,000", "scale": "Create a course teaching prompt engineering", "reasons": ["Brand new skill everyone needs", "Companies will PAY for better AI results"]},
]

# ── RICH VS POOR HABITS ──
RICH_POOR_HABITS = [
    {"rich": "wake up before 6am and plan the day", "poor": "hit snooze 5 times and rush out the door"},
    {"rich": "read 30 minutes about money every day", "poor": "scroll social media for 3 hours every night"},
    {"rich": "track every dollar in and out", "poor": "check their balance and hope it's enough"},
    {"rich": "invest FIRST then spend what's left", "poor": "spend first then save what's left which is nothing"},
    {"rich": "buy assets that make money", "poor": "buy liabilities that lose value"},
    {"rich": "say no to 90 percent of things", "poor": "say yes to everything and wonder why they're tired and broke"},
    {"rich": "surround themselves with people smarter than them", "poor": "hang around people who complain about being broke"},
    {"rich": "see problems as opportunities", "poor": "see problems as reasons to give up"},
    {"rich": "live below their means even as income grows", "poor": "upgrade their lifestyle every time they get a raise"},
    {"rich": "invest in courses skills and mentors", "poor": "think education ends after school"},
    {"rich": "have 3 to 7 income streams", "poor": "depend on one single paycheck"},
    {"rich": "automate savings and investments", "poor": "try to save manually and always fail"},
    {"rich": "think in decades and build long term", "poor": "think in days and want instant results"},
    {"rich": "embrace failure as a learning tool", "poor": "avoid failure and never take any risks"},
    {"rich": "pay themselves first before any bills", "poor": "pay everyone else first and keep nothing"},
]

# ── MONEY CHALLENGE DATA ──
MONEY_CHALLENGES = [
    {"name": "No Spend Challenge", "duration": "30 days", "goal": 1500, "rules": ["Only buy absolute necessities food and bills", "No eating out no online shopping no impulse buys", "Track every dollar you DIDN'T spend"],
     "weeks": [{"action": "Cook every meal at home and cancel unused subscriptions", "saved": 300}, {"action": "Use free entertainment only and pack lunch for work", "saved": 350}, {"action": "Negotiate one bill and sell 3 things you don't use", "saved": 400}, {"action": "Final week no spending at all except groceries and gas", "saved": 450}],
     "mindset": "You realize 80 percent of what you buy you don't actually NEED", "next_duration": "3 months", "annual": 6000},
    {"name": "Round Up Challenge", "duration": "30 days", "goal": 200, "rules": ["Round up every purchase to the nearest dollar", "Transfer the difference to savings immediately", "Do this for EVERY single transaction"],
     "weeks": [{"action": "Set up auto round ups on your bank app", "saved": 35}, {"action": "Keep rounding up every single purchase", "saved": 45}, {"action": "You don't even notice the money leaving anymore", "saved": 55}, {"action": "Check your savings and be SHOCKED", "saved": 65}],
     "mindset": "Small amounts become BIG amounts when you're consistent", "next_duration": "12 months", "annual": 2400},
    {"name": "50 Dollar Bill Challenge", "duration": "30 days", "goal": 1000, "rules": ["Every time you get a 50 dollar bill save it", "If you use cash break 100s to get 50s on purpose", "Never spend a 50 dollar bill again ever"],
     "weeks": [{"action": "Start using cash for daily purchases to get change", "saved": 200}, {"action": "Ask for change in 50s whenever possible", "saved": 250}, {"action": "The habit is automatic now you see 50s differently", "saved": 250}, {"action": "Count your stash and watch your jaw DROP", "saved": 300}],
     "mindset": "You trained your brain to see saving as a GAME not a sacrifice", "next_duration": "6 months", "annual": 6000},
    {"name": "Side Hustle Sprint", "duration": "30 days", "goal": 2000, "rules": ["Dedicate 2 hours per day to a side hustle", "Reinvest zero percent spend zero percent save 100 percent", "Track daily earnings no matter how small"],
     "weeks": [{"action": "Pick one hustle and do the setup work completely", "saved": 200}, {"action": "Start getting your first sales or clients", "saved": 400}, {"action": "Optimize what's working and double down", "saved": 600}, {"action": "Push hard final week and hit your target", "saved": 800}],
     "mindset": "You proved you can make money OUTSIDE your job and that changes everything", "next_duration": "6 months", "annual": 12000},
]

# ── SECRET STRATEGY DATA ──
SECRET_STRATEGIES = [
    {"name": "backdoor Roth IRA", "who": "millionaire", "result": "500,000", "percent": 1, "hidden": "financial advisors make no commission recommending it so they push expensive products instead",
     "analogy": "Think of it like a loophole in a toll road. You pay a small toll once, then drive that road tax free forever.",
     "steps": ["Open a traditional IRA and contribute the max 7000 dollars", "Convert it to a Roth IRA the next day called a conversion", "Pay a small tax now and NEVER pay taxes on growth again"],
     "numbers": {"start": 583, "years": 30, "end": "1,200,000"}, "users": ["Most tech executives in Silicon Valley", "Every smart accountant you've ever met", "Millionaires who pay almost zero tax legally"], "min": 50},
    {"name": "dividend growth snowball", "who": "quietly wealthy", "result": "800,000", "percent": 5, "hidden": "it takes 5 to 10 years to see big results so impatient people quit before the magic happens",
     "analogy": "It's like planting a fruit tree. Every year it grows more branches, and each branch grows more fruit than the last.",
     "steps": ["Buy dividend stocks that INCREASE their payout every year", "Reinvest ALL dividends automatically buying more shares", "Watch your income grow by 10 to 15 percent per year without adding a dollar"],
     "numbers": {"start": 500, "years": 25, "end": "850,000"}, "users": ["Warren Buffett literally built billions this way", "Every pension fund in the country", "The janitor who died with 8 million dollars"], "min": 25},
    {"name": "geographic arbitrage", "who": "remote worker", "result": "300,000", "percent": 10, "hidden": "employers don't want you to know your salary goes 3x further somewhere else",
     "analogy": "It's like buying groceries at a cheaper store but still getting paid your normal salary. Same income, way lower prices.",
     "steps": ["Get a remote job paying US or UK salary", "Move to a low cost of living area or country", "Save 50 to 70 percent of your income effortlessly"],
     "numbers": {"start": 2000, "years": 10, "end": "410,000"}, "users": ["Digital nomads earning six figures in Thailand", "Remote workers in Portugal on US salaries", "People in small US towns earning big city money"], "min": 0},
    {"name": "I bond ladder", "who": "risk averse saver", "result": "200,000", "percent": 15, "hidden": "the government literally created this for regular people but barely advertises it",
     "analogy": "Think of it like a savings account that automatically gives itself a raise every time prices go up, so your money never loses its punching power.",
     "steps": ["Buy I Bonds from TreasuryDirect dot gov up to 10K per year", "The interest rate adjusts with inflation so you never lose purchasing power", "Build a ladder buying max amount every year for guaranteed safe growth"],
     "numbers": {"start": 833, "years": 20, "end": "250,000"}, "users": ["Financial advisors for their OWN personal money", "Government employees who know the system", "Conservative investors who sleep well at night"], "min": 25},
]

# ── USED TITLE HASHES (never repeat tracker) ──
# Persisted to disk so it survives process restarts/crashes (in-memory
# alone would forget every posted title whenever Render restarts the app).
_HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posted_titles.json")
_HISTORY_TITLES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posted_titles_text.json")


def _load_title_hashes():
    try:
        if os.path.exists(_HISTORY_FILE):
            with open(_HISTORY_FILE, "r") as f:
                return set(json.load(f))
    except Exception as e:
        print(f"[WARN] Could not load posted title history: {e}")
    return set()


def _save_title_hash(title_hash):
    try:
        with open(_HISTORY_FILE, "w") as f:
            json.dump(list(_generated_title_hashes), f)
    except Exception as e:
        print(f"[WARN] Could not save posted title history: {e}")


_generated_title_hashes = _load_title_hashes()


def _hash_title(title):
    return hashlib.md5(title.encode()).hexdigest()[:12]


def _prime_hashes_from_youtube():
    """Rebuild the never-repeat list from the channel's actual upload
    history on YouTube. This is the permanent source of truth — unlike
    posted_titles.json, it survives every Render redeploy, which wipes
    the local disk on every code push."""
    global _generated_title_hashes

    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
    client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    if not refresh_token or not client_id or not client_secret:
        print("[WARN] YouTube credentials not set, skipping title history sync")
        return

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=[
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube",
            ],
        )
        youtube = build("youtube", "v3", credentials=creds)

        channels_resp = youtube.channels().list(part="contentDetails", mine=True).execute()
        items = channels_resp.get("items", [])
        if not items:
            print("[WARN] Could not resolve channel uploads playlist")
            return
        uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

        titles = []
        page_token = None
        while True:
            resp = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=page_token,
            ).execute()
            titles.extend(item["snippet"]["title"] for item in resp.get("items", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        added = 0
        for title in titles:
            h = _hash_title(title)
            if h not in _generated_title_hashes:
                _generated_title_hashes.add(h)
                added += 1

        try:
            with open(_HISTORY_FILE, "w") as f:
                json.dump(list(_generated_title_hashes), f)
        except Exception as e:
            print(f"[WARN] Could not persist synced title history: {e}")

        print(f"[OK] Synced {len(titles)} titles from YouTube, {added} new to dedup list")

        # Also rebuild which confusable TERM PAIRS have already been covered
        # (not just exact title matches) so the same pair can't come back
        # around with a slightly reworded title after a redeploy.
        try:
            from ai_topic_generator import sync_used_pairs_from_titles
            sync_used_pairs_from_titles(titles)
        except Exception as e:
            print(f"[WARN] Could not sync used pairs: {e}")

    except Exception as e:
        print(f"[WARN] Could not sync title history from YouTube: {e}")


_prime_hashes_from_youtube()


def _recent_titles_hint(limit=15):
    """Sample a few recent titles as plain text so the AI avoids near-duplicates."""
    try:
        if os.path.exists(_HISTORY_TITLES_FILE):
            with open(_HISTORY_TITLES_FILE, "r") as f:
                titles = json.load(f)
            return "; ".join(titles[-limit:])
    except Exception:
        pass
    return ""


def _remember_title(title):
    try:
        titles = []
        if os.path.exists(_HISTORY_TITLES_FILE):
            with open(_HISTORY_TITLES_FILE, "r") as f:
                titles = json.load(f)
        titles.append(title)
        titles = titles[-200:]
        with open(_HISTORY_TITLES_FILE, "w") as f:
            json.dump(titles, f)
    except Exception as e:
        print(f"[WARN] Could not save recent title text: {e}")


def generate_short_topic():
    """Generate a unique short-form topic that has never been generated before.

    Tries AI-written scripts first (Gemini) for more natural, analogy-rich
    content; falls back to the template system if the API key is missing
    or the request fails, so posting never stops because of an AI outage.
    """
    global _generated_title_hashes
    import time as _time

    for attempt in range(6):
        if attempt > 0:
            _time.sleep(3)
        topic = generate_ai_topic(existing_titles_hint=_recent_titles_hint())
        if topic:
            title_hash = _hash_title(topic["title"])
            if title_hash not in _generated_title_hashes:
                _generated_title_hashes.add(title_hash)
                _save_title_hash(title_hash)
                _remember_title(topic["title"])
                print(f"[GEN-AI] Generated unique AI topic: {topic['title'][:60]}")
                return topic

    for attempt in range(200):
        framework_name = random.choice(list(SLIDE_FRAMEWORKS.keys()))
        topic = _build_topic(framework_name)
        if topic:
            title_hash = _hash_title(topic["title"])
            if title_hash not in _generated_title_hashes:
                _generated_title_hashes.add(title_hash)
                _save_title_hash(title_hash)
                print(f"[GEN] Generated unique topic: {topic['title'][:60]}")
                return topic

    print("[WARN] Could not generate fully unique topic, using random combination")
    return _build_topic(random.choice(list(SLIDE_FRAMEWORKS.keys())))


def generate_long_topic():
    """Generate a unique long-form topic (20 slides) that never repeats."""
    global _generated_title_hashes

    for attempt in range(200):
        topic = _build_long_topic()
        if topic:
            title_hash = _hash_title(topic["title"])
            if title_hash not in _generated_title_hashes:
                _generated_title_hashes.add(title_hash)
                _save_title_hash(title_hash)
                print(f"[GEN] Generated unique long topic: {topic['title'][:60]}")
                return topic

    return _build_long_topic()


def _build_topic(framework_name):
    """Build a complete 10-slide topic from a framework."""
    try:
        if framework_name == "person_story":
            return _build_person_story()
        elif framework_name == "myth_buster":
            return _build_myth_buster()
        elif framework_name == "money_math":
            return _build_money_math()
        elif framework_name == "rules_list":
            return _build_rules_list()
        elif framework_name == "famous_person":
            return _build_famous_person()
        elif framework_name == "age_timeline":
            return _build_age_timeline()
        elif framework_name == "side_hustle":
            return _build_side_hustle()
        elif framework_name == "rich_vs_poor":
            return _build_rich_vs_poor()
        elif framework_name == "money_challenge":
            return _build_money_challenge()
        elif framework_name == "secret_strategy":
            return _build_secret_strategy()
    except Exception as e:
        print(f"[WARN] Topic build failed ({framework_name}): {e}")
        return None


def _get_img(role):
    prompts = IMAGE_PROMPTS.get(role, ["professional finance education visual"])
    return random.choice(prompts)


LOOP_SPEECHES = [
    "Did you catch everything? Watch again. Follow The AI Dollar for more every single day.",
    "Watch this again. Share it with someone who needs it. Follow for daily money tips.",
    "That's it. The whole strategy. Watch again to make sure you got it. Follow for more.",
    "Comment which tip helped you most. Watch again. Follow The AI Dollar for daily lessons.",
]

LOOP_TEXTS = [
    "Did you catch\neverything?\nWatch again\nFollow for more",
    "Share this with\nsomeone who\nneeds it\nFollow for daily tips",
    "Comment your\n#1 takeaway\nWatch again\nFollow for more",
]

CTA_SPEECHES = [
    "Follow right now. The next video is even more powerful. Don't miss it.",
    "Follow for daily money tips that actually work. The next one could change your life.",
    "Hit follow right now. We drop money lessons like this every single day.",
]

CTA_TEXTS = [
    "FOLLOW NOW\nfor daily\nmoney tips\nthat WORK",
    "FOLLOW\nfor the next\nmoney lesson\nDon't miss it",
    "Hit FOLLOW\nNew money tips\nEVERY day",
]


def _to_7_slides(slides):
    """Trim any 10-slide set to 7: hook + 2 content + early CTA + 2 content + loop ending."""
    if len(slides) <= 7:
        return slides
    cta_slide = {
        "text": random.choice(CTA_TEXTS),
        "speech": random.choice(CTA_SPEECHES),
        "img": _get_img("cta"),
    }
    loop_slide = {
        "text": random.choice(LOOP_TEXTS),
        "speech": random.choice(LOOP_SPEECHES),
        "img": _get_img("cta"),
    }
    return [
        slides[0],
        slides[1],
        cta_slide,
        slides[2],
        slides[3],
        slides[4],
        loop_slide,
    ]


def _build_person_story():
    persona = random.choice(PERSONAS)
    method = random.choice(METHODS)
    female_names = {"Sarah", "Priya", "Lisa", "Ana", "Maria", "Nina", "Emma", "Aisha", "Rosa", "Fatima", "Keisha"}
    male_names = {"Marcus", "James", "Kevin", "Daniel", "Tyler", "Jordan", "Derek", "Chris", "Mike", "Brandon", "Jason", "Tony"}
    if persona["name"] in female_names:
        pronoun = "she"
    elif persona["name"] in male_names:
        pronoun = "he"
    else:
        pronoun = random.choice(["he", "she", "they"])
    pronoun_cap = pronoun.capitalize()
    pronoun_poss = {"he": "his", "she": "her", "they": "their"}[pronoun]
    low_salary = random.choice([18, 20, 22, 25, 28, 30, 32, 35])
    debt = random.choice([5, 10, 15, 20, 25, 30, 40])
    short_time = random.choice(["3 months", "6 months", "90 days", "4 months"])
    long_time = random.choice(["2 years", "3 years", "5 years", "18 months"])
    early_result = random.choice([3000, 5000, 8000, 10000, 12000])
    big_result = random.choice([50000, 75000, 100000, 150000, 200000])
    min_start = method["min_start"] if method["min_start"] > 0 else random.choice([10, 25, 50])

    action_steps = [
        ("Tracked every dollar\nfor 30 days\nFound ${} in\nhidden waste".format(random.choice([200, 300, 400, 500])),
         f"{pronoun_cap} tracked every single dollar for 30 days and found {random.choice([200, 300, 400, 500])} dollars per month in completely hidden waste"),
        ("Cut 3 biggest\nunnecessary expenses\nSaved ${}/month\ninstantly".format(random.choice([300, 400, 500, 600])),
         f"{pronoun_cap} cut the three biggest unnecessary expenses and saved {random.choice([300, 400, 500, 600])} dollars per month instantly"),
        ("Set up automatic\ninvesting on payday\n${}/month into\n{}".format(random.choice([200, 300, 500]), method["name"]),
         f"{pronoun_cap} set up automatic investing on payday. {random.choice([200, 300, 500])} dollars per month straight into {method['name']}"),
    ]
    random.shuffle(action_steps)

    title_templates = [
        f"A {persona['job'].title()} Made ${big_result:,} In {long_time} (Copy {pronoun_poss.title()} Strategy)",
        f"{persona['name']} Was A {persona['job'].title()} Making ${low_salary}K — Now {pronoun_cap} Has ${big_result:,}",
        f"From ${low_salary}K Salary To ${big_result:,} Net Worth ({persona['job'].title()}'s Secret)",
        f"How A {persona['job'].title()} Built ${big_result:,} While {persona['story'].title()}",
    ]
    title = random.choice(title_templates)

    slides = [
        {"text": f"{persona['name']} was a {persona['job']}\n{persona['story']}\nmaking ${low_salary}K/year",
         "speech": SPEECH_TEMPLATES["person_story"][0].format(person_name=persona['name'], job=persona['job'], story_detail=persona['story'], low_salary=low_salary),
         "img": _get_img("hook")},
        {"text": f"Every month\nthe same cycle:\nearn → spend →\nNOTHING left\n${debt}K in debt",
         "speech": SPEECH_TEMPLATES["person_story"][1].format(debt=debt),
         "img": _get_img("struggle")},
        {"text": f"FOLLOW for the\nfull strategy\nThis changed\nEVERYTHING",
         "speech": SPEECH_TEMPLATES["person_story"][2],
         "img": _get_img("cta")},
        {"text": f"Then {pronoun} discovered\n{method['name']}\n{action_steps[0][0]}",
         "speech": SPEECH_TEMPLATES["person_story"][3].format(pronoun=pronoun, method_name=method['name'], speech_action_1=action_steps[0][1]),
         "img": _get_img("discovery")},
        {"text": f"Step 2:\n{action_steps[1][0]}",
         "speech": SPEECH_TEMPLATES["person_story"][4].format(speech_action_2=action_steps[1][1]),
         "img": _get_img("action1")},
        {"text": f"After {long_time}:\n${big_result:,}\nnet worth\nAs a {persona['job']}",
         "speech": SPEECH_TEMPLATES["person_story"][5].format(long_time=long_time, big_result=f"{big_result:,}", job=persona['job']),
         "img": _get_img("result_big")},
        {"text": f"Want the next\nmoney story?\nWatch again\nFollow The AI Dollar",
         "speech": SPEECH_TEMPLATES["person_story"][6],
         "img": _get_img("cta")},
    ]

    return {"title": title, "slides": slides, "keywords": [method["name"].title(), persona["job"].title(), "Wealth Building"]}


def _build_myth_buster():
    myth_set = random.choice(MYTH_SETS)
    fact_data = random.choice(MONEY_FACTS)
    rich_habits = [
        "They automate EVERYTHING. Savings. Investments. Bills. They remove willpower from the equation.",
        "They spend on ASSETS that make money. Not liabilities that lose value.",
        "They read one book per month about money. Knowledge compounds just like interest.",
        "They track every dollar and know exactly where their money goes.",
        "They have 3 to 7 income streams. Never depend on just one paycheck.",
        "They live BELOW their means even when they can afford more.",
    ]
    fixes = [
        ("Open a free brokerage account today", "Set up automatic monthly investing even if it's just 50 dollars"),
        ("Track every dollar for 30 days", "Cut the 3 biggest wastes and redirect that money to investments"),
        ("Max out your employer 401K match", "Open a Roth IRA and contribute monthly"),
        ("Cancel subscriptions you don't use weekly", "Move savings to a high yield account paying 5 percent"),
    ]
    fix = random.choice(fixes)
    proof_amount = random.choice([5000, 10000, 15000, 20000, 25000])
    proof_time = random.choice(["6 months", "1 year", "18 months", "2 years"])
    mindset_shifts = [
        "Rich think in DECADES poor think in DAYS",
        "Rich see money as a TOOL poor see it as a REWARD",
        "Rich invest FIRST spend second. Poor spend first save never",
        "Rich learn about money DAILY. Poor avoid the topic entirely",
    ]

    title_templates = [
        f"Everything You Know About {myth_set['topic'].title()} Is WRONG ({len(myth_set['myths'])} Myths Exposed)",
        f"Stop Believing These {myth_set['topic'].title()} Myths (They're Keeping You Broke)",
        f"{len(myth_set['myths'])} {myth_set['topic'].title()} Lies Everyone Believes (The Truth Is Shocking)",
        f"Your Parents Were WRONG About {myth_set['topic'].title()} (Here's Proof)",
    ]
    title = random.choice(title_templates)
    myths = myth_set["myths"]

    slides = [
        {"text": f"Everything you\nknow about\n{myth_set['topic']}\nis WRONG",
         "speech": SPEECH_TEMPLATES["myth_buster"][0].format(topic=myth_set['topic']),
         "img": _get_img("hook")},
        {"text": f"Myth 1:\n{myths[0]['myth']}\nREALITY:\n{myths[0]['reality'][:50]}",
         "speech": SPEECH_TEMPLATES["myth_buster"][1].format(myth_1=myths[0]['myth'], reality_1=myths[0]['reality']),
         "img": _get_img("myth1")},
        {"text": f"FOLLOW to stop\nbelieving money\nmyths that keep\nyou BROKE",
         "speech": SPEECH_TEMPLATES["myth_buster"][2],
         "img": _get_img("cta")},
        {"text": f"Myth 2:\n{myths[1]['myth']}\nREALITY:\n{myths[1]['reality'][:50]}",
         "speech": SPEECH_TEMPLATES["myth_buster"][3].format(myth_2=myths[1]['myth'], reality_2=myths[1]['reality']),
         "img": _get_img("myth2")},
        {"text": f"SHOCKING FACT:\n{fact_data['fact'][:60]}",
         "speech": SPEECH_TEMPLATES["myth_buster"][4].format(fact=fact_data['fact'], follow_up=fact_data['follow_up']),
         "img": _get_img("shocking_stat")},
        {"text": f"The fix:\n1. {fix[0][:40]}\n2. {fix[1][:40]}",
         "speech": SPEECH_TEMPLATES["myth_buster"][5].format(fix_step_1=fix[0], fix_step_2=fix[1]),
         "img": _get_img("simple_fix")},
        {"text": f"Which myth did\nyou believe?\nComment below\nWatch again",
         "speech": SPEECH_TEMPLATES["myth_buster"][6],
         "img": _get_img("cta")},
    ]

    return {"title": title, "slides": slides, "keywords": [myth_set["topic"].title(), "Money Myths", "Financial Education"]}


def _build_money_math():
    data = random.choice(EXPENSE_MATH)
    old_habits = [
        f"spending ${data['daily']} on {data['expense']} every day",
        f"buying {data['expense']} without thinking about it",
        f"treating yourself to {data['expense']} daily because you deserve it",
    ]
    new_habits = [
        f"make it at home for a tenth of the price",
        f"do it yourself and pocket the difference",
        f"find the free or cheap alternative and invest the savings",
    ]

    title_templates = [
        f"Your ${data['daily']}/Day {data['expense'].title()} Habit Costs ${data['compound']} (The Math Is Scary)",
        f"${data['daily']} Per Day = ${data['compound']} Lost (Stop Doing This)",
        f"The ${data['daily']} {data['expense'].title()} Trap That's Stealing ${data['compound']} From You",
        f"I Did The Math On {data['expense'].title()} — You're Losing ${data['compound']}",
    ]
    title = random.choice(title_templates)

    slides = [
        {"text": f"Your ${data['daily']}/day\n{data['expense']} habit\nis costing you\n${data['compound']}",
         "speech": f"Your {data['daily']} dollar {data['expense']} habit is secretly costing you {data['compound']} dollars. And I'm going to prove it right now.",
         "img": _get_img("hook")},
        {"text": f"${data['daily']}/day\n= ${data['monthly']}/month\n= ${data['yearly']:,}/year\nSeems small right?",
         "speech": f"{data['daily']} dollars per day. That's {data['monthly']} per month. {data['yearly']:,} per year. Seems small right? Watch what happens next.",
         "img": _get_img("daily_breakdown")},
        {"text": f"Invested at {data['percent']}%\nfor {data['years']} years\n= ${data['compound']}",
         "speech": f"If you invested that money at {data['percent']} percent per year for {data['years']} years, compound interest turns it into {data['compound']} dollars.",
         "img": _get_img("compound_reveal")},
        {"text": f"That's enough to:\n• {data['comparisons'][0]}\n• {data['comparisons'][1]}\n• {data['comparisons'][2]}",
         "speech": f"That's enough to {data['comparisons'][0]}. Or {data['comparisons'][1]}. Or {data['comparisons'][2]}. From just cutting ONE habit.",
         "img": _get_img("comparison")},
        {"text": f"Add {data['expense_2']}\n+ {data['expense_3']}\n= ${data['combined']:,}/year\nWASTED",
         "speech": f"And it's not just {data['expense']}. Add {data['expense_2']} plus {data['expense_3']} and you're wasting {data['combined']:,} dollars per year.",
         "img": _get_img("not_just_one")},
        {"text": f"The swap:\nInstead of\n{random.choice(old_habits)[:40]}\n{random.choice(new_habits)[:40]}",
         "speech": f"The swap is easy. Instead of {random.choice(old_habits)}, {random.choice(new_habits)}. You'll save {data['monthly']} dollars per month.",
         "img": _get_img("alternative")},
        {"text": f"Put ${data['monthly']}/month\ninto {data['investment']}\nEvery month\nAutomatically",
         "speech": f"Put that {data['monthly']} dollars into {data['investment']}. Every single month. Automatically. Set it and forget it.",
         "img": _get_img("invest_it")},
        {"text": f"In {data['years']} years:\n${data['compound']}\nFrom ONE simple\nswap",
         "speech": f"In {data['years']} years that becomes {data['compound']} dollars. From ONE simple swap. Not a sacrifice. A SWAP.",
         "img": _get_img("future_result")},
        {"text": f"You're not\ngiving up {data['expense']}\nYou're BUYING\nyour FREEDOM",
         "speech": f"You're not giving up {data['expense']}. You're BUYING your freedom. Trading a small pleasure today for total financial freedom tomorrow.",
         "img": _get_img("perspective")},
        {"text": f"Make the swap\nTODAY\n${data['monthly']}/month\n= ${data['compound']} future",
         "speech": f"Make the swap today. {data['monthly']} dollars per month equals {data['compound']} dollars in your future. Do it NOW.",
         "img": _get_img("cta")},
    ]

    return {"title": title, "slides": _to_7_slides(slides), "keywords": [data["expense"].title(), "Compound Interest", "Saving Money"]}


def _build_rules_list():
    rules = random.sample(MONEY_RULES, 5)
    count = random.choice([5, 7])
    mistakes = [
        "trying to look rich instead of BEING rich",
        "spending first and saving what's left which is always NOTHING",
        "ignoring your finances and hoping it works out",
        "comparing your chapter 1 to someone else's chapter 20",
        "waiting for the perfect time to start investing which never comes",
    ]
    rich_dos = [
        "invest first then spend what's left",
        "buy assets that make money while they sleep",
        "read about money every single day",
        "live below their means even when they don't have to",
    ]
    poor_dos = [
        "spend first then wonder where the money went",
        "buy things to impress people they don't even like",
        "avoid thinking about money entirely",
        "inflate their lifestyle every time they get a raise",
    ]

    title_templates = [
        f"{count} Money Rules Rich People Follow (That Poor People Ignore)",
        f"The {count} Rules That Separate Millionaires From Everyone Else",
        f"Follow These {count} Rules Or Stay Broke Forever (Your Choice)",
        f"{count} Wealth Rules I Wish I Learned At 18 (Not In School)",
    ]
    title = random.choice(title_templates)

    slides = [
        {"text": f"{count} Money Rules\nThat Separate\nRICH from POOR",
         "speech": f"{count} money rules that separate the RICH from the POOR. If you follow even THREE of these, your finances will transform.",
         "img": _get_img("hook")},
        {"text": f"Rule 1:\n{rules[0]['rule']}\n{rules[0]['explain'][:40]}",
         "speech": f"Rule one. {rules[0]['rule']}. {rules[0]['explain']}. This is the foundation.",
         "img": _get_img("rule1")},
        {"text": f"Rule 2:\n{rules[1]['rule']}\n{rules[1]['explain'][:40]}",
         "speech": f"Rule two. {rules[1]['rule']}. {rules[1]['explain']}.",
         "img": _get_img("rule2")},
        {"text": f"Rule 3:\n{rules[2]['rule']}\n{rules[2]['explain'][:40]}",
         "speech": f"Rule three. {rules[2]['rule']}. {rules[2]['explain']}.",
         "img": _get_img("rule3")},
        {"text": f"Rule 4:\n{rules[3]['rule']}\n{rules[3]['explain'][:40]}",
         "speech": f"Rule four. {rules[3]['rule']}. {rules[3]['explain']}.",
         "img": _get_img("rule4")},
        {"text": f"Rule 5:\n{rules[4]['rule']}\n{rules[4]['explain'][:40]}",
         "speech": f"Rule five. {rules[4]['rule']}. {rules[4]['explain']}.",
         "img": _get_img("rule5")},
        {"text": f"#1 Mistake:\n{random.choice(mistakes)[:50]}",
         "speech": f"The number one mistake that keeps people broke is {random.choice(mistakes)}. Fix just THIS and everything else gets easier.",
         "img": _get_img("common_mistake")},
        {"text": f"Rich people:\n{random.choice(rich_dos)[:40]}\nPoor people:\n{random.choice(poor_dos)[:40]}",
         "speech": f"Rich people {random.choice(rich_dos)}. Poor people {random.choice(poor_dos)}. Same hours. Different choices.",
         "img": _get_img("rich_vs_poor")},
        {"text": f"Pick just ONE\nrule to follow\nthis week\nThat's all it takes",
         "speech": "Pick just ONE rule to follow this week. Not all five. Just ONE. Master it. Then add another. Small steps build empires.",
         "img": _get_img("start_today")},
        {"text": f"Follow for\nmore rules that\nbuild REAL wealth",
         "speech": "Follow The AI Dollar for more wealth building rules. New money lessons every single day. Subscribe now.",
         "img": _get_img("cta")},
    ]

    return {"title": title, "slides": _to_7_slides(slides), "keywords": ["Money Rules", "Rich vs Poor", "Wealth Building"]}


def _build_famous_person():
    person = random.choice(FAMOUS_PEOPLE)
    other_people = [p for p in FAMOUS_PEOPLE if p["name"] != person["name"]]
    other1, other2 = random.sample(other_people, 2)
    origins = [
        "absolutely nothing", "a small town with no connections",
        "humble beginnings and pure discipline", "zero advantages and raw determination",
    ]
    explanations = [
        ("Never put your money somewhere you could lose it all", "Even small consistent gains beat big risky bets over time"),
        ("Protect your capital at all costs because recovery is twice as hard", "A 50% loss needs a 100% gain just to break even"),
        ("Focus on NOT being stupid rather than being brilliant", "Avoiding big mistakes matters more than finding big wins"),
        ("The best opportunities look boring and ordinary", "Exciting investments are usually the ones that lose you money"),
    ]
    examples = [
        "If you invested 10K and lost 50% you now have 5K. To get back to 10K you need a 100% return. Avoiding the loss was worth more than finding the gain.",
        "Putting 500 per month into boring index funds for 30 years gives you over a million dollars. No stock picking. No excitement. Just boring consistent wealth.",
        "Someone who saves 20% of a 50K salary builds more wealth than someone who saves 5% of a 200K salary. The habit matters more than the income.",
    ]
    mistakes = [
        "trying to get rich FAST which leads to get poor FAST instead",
        "following hot stock tips from social media instead of proven strategies",
        "thinking they're smarter than the market and trying to time it",
        "investing based on emotion instead of logic and discipline",
    ]
    apply_steps = [
        ("Set up automatic investing today even if it's just 50 dollars per month", "Never check your portfolio more than once per month to avoid emotional decisions"),
        ("Write down your financial goal with a specific number and deadline", "Automate everything so discipline isn't required willpower always fails"),
        ("Start with one index fund and invest the same amount every month", "Ignore all market news and predictions just keep investing consistently"),
    ]
    apply = random.choice(apply_steps)
    potential = random.choice(["250,000", "500,000", "750,000", "1,000,000"])
    result_time = random.choice(["15 years", "20 years", "25 years", "30 years"])

    title_templates = [
        f"{person['name']}'s #1 Money Rule Will Change Your Life",
        f"{person['name']} Said This About Money And It Changed Everything",
        f"The ONE Rule {person['name']} Follows (Worth ${person['worth']})",
        f"I Followed {person['name']}'s Money Advice For 1 Year (Results Were Insane)",
    ]
    title = random.choice(title_templates)
    explanation = random.choice(explanations)

    slides = [
        {"text": f"{person['name']} said\nthis ONE thing\nabout money\nand it changed\nEVERYTHING",
         "speech": f"{person['name']} said ONE thing about money that changed EVERYTHING. And most people completely ignore it.",
         "img": _get_img("hook")},
        {"text": f"The rule:\n\"{person['rule'].upper()}\"\nSimple but\nMOST ignore it",
         "speech": f"The rule is simple. {person['rule'].capitalize()}. Simple but most people hear it and do nothing.",
         "img": _get_img("quote")},
        {"text": f"{person['name']}\nWorth: ${person['worth']}\nBuilt from\n{random.choice(origins)}",
         "speech": f"{person['name']} is worth {person['worth']} dollars. Built from {random.choice(origins)}. This isn't theory. This is PROVEN.",
         "img": _get_img("backstory")},
        {"text": f"What this means:\n{explanation[0][:50]}\n{explanation[1][:50]}",
         "speech": f"What this really means is {explanation[0]}. And more importantly, {explanation[1]}.",
         "img": _get_img("explain")},
        {"text": f"Real example:\n{random.choice(examples)[:80]}",
         "speech": f"Real example. {random.choice(examples)}",
         "img": _get_img("example")},
        {"text": f"The mistake:\n{random.choice(mistakes)[:60]}",
         "speech": f"The mistake most people make is {random.choice(mistakes)}. This single mistake DESTROYS any chance of building wealth.",
         "img": _get_img("mistake")},
        {"text": f"Apply TODAY:\n1. {apply[0][:45]}\n2. {apply[1][:45]}",
         "speech": f"How to apply this TODAY. First, {apply[0]}. Second, {apply[1]}.",
         "img": _get_img("apply_it")},
        {"text": f"Follow this rule:\n${potential}\nin {result_time}",
         "speech": f"If you follow this one rule consistently, you could have {potential} dollars in {result_time}. The math is real.",
         "img": _get_img("result")},
        {"text": f"Also followed by:\n{other1['name']}\n{other2['name']}\nNot a coincidence",
         "speech": f"Other billionaires who follow this exact same rule include {other1['name']} and {other2['name']}. It's not a coincidence.",
         "img": _get_img("other_billionaires")},
        {"text": f"One rule\nOne change\nStart TODAY",
         "speech": "One rule. One change. Start TODAY. Your wallet, your bank account, and your future self will ALL thank you.",
         "img": _get_img("cta")},
    ]

    return {"title": title, "slides": _to_7_slides(slides), "keywords": [person["name"], "Money Rules", "Investing"]}


def _build_age_timeline():
    timeline = random.choice(AGE_TIMELINES)
    title_templates = [
        f"How Much Money You Should Have Saved By Age {timeline['start_age']} to 40",
        f"Are You Behind? Money Milestones By Age ({timeline['start_age']}-40)",
        f"The Savings Target For Every Age ({timeline['start_age']}, 25, 30, 40) — Where Are You?",
        f"At Age {timeline['start_age']} You Should Have ${timeline['goals']['20']} Saved (Do You?)",
    ]
    title = random.choice(title_templates)

    slides = [
        {"text": f"At age {timeline['start_age']}\nyou should have\n${timeline['goals']['20']}\nsaved\nDo you?",
         "speech": f"At age {timeline['start_age']}, you should have {timeline['goals']['20']} dollars saved. Do you? If not, keep watching.",
         "img": _get_img("hook")},
        {"text": f"By age 20:\n${timeline['goals']['20']} saved\n{timeline['how']['20'][:40]}",
         "speech": f"By age twenty, you should have {timeline['goals']['20']} dollars saved. How? {timeline['how']['20']}.",
         "img": _get_img("age_20")},
        {"text": f"By age 25:\n${timeline['goals']['25']} saved\n{timeline['how']['25'][:40]}",
         "speech": f"By age twenty five, you should have {timeline['goals']['25']} dollars saved. How? {timeline['how']['25']}.",
         "img": _get_img("age_25")},
        {"text": f"By age 30:\n${timeline['goals']['30']} saved\n{timeline['how']['30'][:40]}",
         "speech": f"By age thirty, the target is {timeline['goals']['30']} dollars. How? {timeline['how']['30']}.",
         "img": _get_img("age_30")},
        {"text": f"By age 40:\n${timeline['goals']['40']} saved\n{timeline['how']['40'][:40]}",
         "speech": f"By age forty, you should have {timeline['goals']['40']} dollars saved. How? {timeline['how']['40']}.",
         "img": _get_img("age_40")},
        {"text": f"Behind?\nDON'T PANIC\nHere's how to\ncatch up FAST",
         "speech": "If you're behind, DON'T PANIC. Seriously. Here's how to catch up FAST. It's not too late.",
         "img": _get_img("behind")},
        {"text": f"Catch-up #1:\n{timeline['catchup'][0][:60]}",
         "speech": f"Catch up strategy one. {timeline['catchup'][0]}.",
         "img": _get_img("catch_up_1")},
        {"text": f"Catch-up #2:\n{timeline['catchup'][1][:60]}",
         "speech": f"Catch up strategy two. {timeline['catchup'][1]}.",
         "img": _get_img("catch_up_2")},
        {"text": f"Starting late?\n${timeline['late']['start']}/month\nat age {timeline['late']['age']}\n= ${timeline['late']['result']}\nby 65",
         "speech": f"Starting late? {timeline['late']['start']} dollars per month at age {timeline['late']['age']} still becomes {timeline['late']['result']} dollars by age sixty five.",
         "img": _get_img("compound_power")},
        {"text": f"The best time\nto start was\n10 years ago\nThe second best\ntime is TODAY",
         "speech": "The best time to start was ten years ago. The second best time is RIGHT NOW. Open that account. Start that transfer. DO IT.",
         "img": _get_img("cta")},
    ]

    return {"title": title, "slides": _to_7_slides(slides), "keywords": ["Savings Goals", "Age Milestones", "Retirement"]}


def _build_side_hustle():
    hustle = random.choice(SIDE_HUSTLES)
    title_templates = [
        f"This Side Hustle Pays ${hustle['amount']}/Month — Takes {hustle['time']} To Start",
        f"I Found A Side Hustle That Pays ${hustle['amount']}/Month (No Experience Needed)",
        f"${hustle['amount']}/Month From {hustle['name'].title()} — Full Breakdown",
        f"The ${hustle['amount']}/Month Side Hustle Nobody Talks About (2026 Edition)",
    ]
    title = random.choice(title_templates)
    slides = [
        {"text": f"This side hustle\npays ${hustle['amount']}/month\nand takes\n{hustle['time']}\nto set up",
         "speech": f"This side hustle pays {hustle['amount']} dollars per month. Takes {hustle['time']} to set up. No degree needed.",
         "img": _get_img("hook")},
        {"text": f"It's called:\n{hustle['name'].upper()}\nand ANYONE\ncan start it",
         "speech": f"It's called {hustle['name']}. ANYONE can start it. Zero experience needed.",
         "img": _get_img("what")},
        {"text": f"Step 1:\n{hustle['steps'][0][:50]}",
         "speech": f"Step one. {hustle['steps'][0]}. Takes about an hour. Stop overthinking it.",
         "img": _get_img("step1")},
        {"text": f"Step 2:\n{hustle['steps'][1][:50]}",
         "speech": f"Step two. {hustle['steps'][1]}. Free tools only. Don't spend a dollar until you make one.",
         "img": _get_img("step2")},
        {"text": f"Step 3:\n{hustle['steps'][2][:50]}",
         "speech": f"Step three. {hustle['steps'][2]}. This is where money starts flowing.",
         "img": _get_img("step3")},
        {"text": f"Month 3:\n${hustle['month3']:,}/month\nConsistency\nis the secret",
         "speech": f"Month three. {hustle['month3']:,} dollars per month consistently. Consistency is the real secret.",
         "img": _get_img("month3")},
        {"text": f"This pays\n${hustle['amount']}/month\nDid you catch\nall the steps?\nWatch again",
         "speech": f"This pays {hustle['amount']} per month. Did you catch all the steps? Watch again. Follow for more.",
         "img": _get_img("cta")},
    ]
    return {"title": title, "slides": slides, "keywords": [hustle["name"].title(), "Side Hustle", "Make Money"]}


def _build_rich_vs_poor():
    habits = random.sample(RICH_POOR_HABITS, 5)
    proof_amounts = [500, 1000, 1500, 2000, 3000]
    proof = random.choice(proof_amounts)
    title_templates = [
        f"5 Things Rich People Do Every Day (Broke People Do The Opposite)",
        f"Rich vs Broke — {random.choice([5,7])} Habits That Separate Them",
        f"The Daily Habits Of Millionaires (Copy These And Watch What Happens)",
        f"Do You Have Rich Habits Or Broke Habits? (Honest Check)",
    ]
    title = random.choice(title_templates)
    slides = [
        {"text": "Rich people do\nTHIS every day\nBroke people\ndo the OPPOSITE",
         "speech": "Rich people do THIS every day. Broke people do the EXACT opposite. Same twenty four hours. Watch closely.",
         "img": _get_img("hook")},
        {"text": f"Rich:\n{habits[0]['rich'][:35]}\nBroke:\n{habits[0]['poor'][:35]}",
         "speech": f"Rich people {habits[0]['rich']}. Broke people? {habits[0]['poor']}. This ONE difference compounds into millions.",
         "img": _get_img("habit1_rich")},
        {"text": f"Rich:\n{habits[1]['rich'][:35]}\nBroke:\n{habits[1]['poor'][:35]}",
         "speech": f"Rich people {habits[1]['rich']}. Broke people {habits[1]['poor']}. And here's what nobody tells you.",
         "img": _get_img("habit2_rich")},
        {"text": f"Rich:\n{habits[2]['rich'][:35]}\nBroke:\n{habits[2]['poor'][:35]}",
         "speech": f"Rich people {habits[2]['rich']}. Broke people {habits[2]['poor']}. Same hours. Different choices. Different results.",
         "img": _get_img("habit3_rich")},
        {"text": "The switch:\nPick ONE rich habit\nReplace ONE broke habit\nDo it for 30 days",
         "speech": "The switch. Pick ONE rich habit. Replace ONE broke habit. Do it thirty days. That's the entire plan.",
         "img": _get_img("the_switch")},
        {"text": f"After 30 days:\n${proof:,} more saved\nand a NEW mindset",
         "speech": f"After thirty days, {proof:,} dollars more saved. And a completely new mindset. That is priceless.",
         "img": _get_img("proof")},
        {"text": "Rich do THIS\nBroke do\nthe OPPOSITE\nWhich one\nare YOU?\nWatch again",
         "speech": "Rich do THIS. Broke do the opposite. Which one are YOU? Watch again. Follow for more.",
         "img": _get_img("cta")},
    ]
    return {"title": title, "slides": slides, "keywords": ["Rich vs Poor", "Money Habits", "Millionaire Mindset"]}


def _build_money_challenge():
    challenge = random.choice(MONEY_CHALLENGES)
    title_templates = [
        f"The {challenge['duration']} {challenge['name']} — Save ${challenge['goal']:,} Guaranteed",
        f"Try This {challenge['duration']} Challenge And Save ${challenge['goal']:,}",
        f"I Tried The {challenge['name']} For {challenge['duration']} (Results Were INSANE)",
        f"${challenge['goal']:,} In {challenge['duration']} — The {challenge['name']} Works",
    ]
    title = random.choice(title_templates)
    w = challenge["weeks"]
    running_total_2 = w[0]["saved"] + w[1]["saved"]
    total = sum(week["saved"] for week in w)
    slides = [
        {"text": f"Try this {challenge['duration']}\nmoney challenge\nand save ${challenge['goal']:,}\nGuaranteed.",
         "speech": f"Try this {challenge['duration']} challenge and save {challenge['goal']:,} dollars. GUARANTEED. Follow the rules. The money appears.",
         "img": _get_img("hook")},
        {"text": f"The rules:\n{challenge['rules'][0][:35]}\n{challenge['rules'][1][:35]}\n{challenge['rules'][2][:35]}",
         "speech": f"The rules. {challenge['rules'][0]}. {challenge['rules'][1]}. {challenge['rules'][2]}. That's IT. No apps. No spreadsheets.",
         "img": _get_img("rules")},
        {"text": f"Week 1:\n{w[0]['action'][:40]}\nSaved: ${w[0]['saved']}",
         "speech": f"Week one. {w[0]['action']}. Easy. Saved {w[0]['saved']} dollars. Your brain starts rewiring immediately.",
         "img": _get_img("week1")},
        {"text": f"Week 2:\n{w[1]['action'][:40]}\nTotal: ${running_total_2}",
         "speech": f"Week two. {w[1]['action']}. Total so far {running_total_2} dollars. The momentum is building.",
         "img": _get_img("week2")},
        {"text": f"RESULTS:\n${total:,} saved\nin just {challenge['duration']}\nFrom ZERO effort",
         "speech": f"Results. {total:,} dollars saved in {challenge['duration']}. Zero effort. Zero suffering. Just smart choices.",
         "img": _get_img("results")},
        {"text": f"The REAL win:\n{challenge['mindset'][:50]}",
         "speech": f"But the REAL win. {challenge['mindset']}. Your relationship with money completely changes. THAT is priceless.",
         "img": _get_img("what_changed")},
        {"text": f"Save ${challenge['goal']:,}\nin {challenge['duration']}\nWatch again\nStart TODAY",
         "speech": f"Save {challenge['goal']:,} in {challenge['duration']}. Watch again for the exact rules. Start TODAY not Monday.",
         "img": _get_img("cta")},
    ]
    return {"title": title, "slides": slides, "keywords": [challenge["name"], "Money Challenge", "Saving Money"]}


def _build_secret_strategy():
    strategy = random.choice(SECRET_STRATEGIES)
    title_templates = [
        f"The {strategy['name'].title()} — A {strategy['who'].title()} Strategy Hidden In Plain Sight",
        f"This {strategy['who'].title()} Strategy Quietly Builds ${strategy['result']} (Nobody Talks About It)",
        f"The Strategy That Built ${strategy['result']} While People Slept (Not Clickbait)",
        f"Top {strategy['percent']}% Use THIS Strategy — Now You Can Too",
    ]
    title = random.choice(title_templates)
    n = strategy["numbers"]
    slides = [
        {"text": f"This {strategy['who']} strategy\nis hidden in\nplain sight\nand it builds\n${strategy['result']} quietly",
         "speech": SPEECH_TEMPLATES["secret_strategy"][0].format(who=strategy['who'], result=strategy['result']),
         "img": _get_img("hook")},
        {"text": f"The strategy:\n{strategy['name'].upper()}\nIn simple terms:\n{strategy['analogy'][:70]}",
         "speech": SPEECH_TEMPLATES["secret_strategy"][1].format(strategy_name=strategy['name'], percent=strategy['percent']) + f" In simple terms, {strategy['analogy']}",
         "img": _get_img("what_is_it")},
        {"text": f"Why nobody\ntalks about it:\n{strategy['hidden'][:50]}",
         "speech": SPEECH_TEMPLATES["secret_strategy"][2].format(hidden_reason=strategy['hidden']),
         "img": _get_img("why_hidden")},
        {"text": f"Step 1:\n{strategy['steps'][0][:55]}",
         "speech": SPEECH_TEMPLATES["secret_strategy"][3].format(step_1=strategy['steps'][0], time_1="about 30 minutes"),
         "img": _get_img("how_step1")},
        {"text": f"Step 2:\n{strategy['steps'][1][:55]}",
         "speech": f"Step two. {strategy['steps'][1]}. This is the key move.",
         "img": _get_img("how_step2")},
        {"text": f"Step 3:\n{strategy['steps'][2][:55]}",
         "speech": f"Step three. {strategy['steps'][2]}. Now sit back and let compound interest work.",
         "img": _get_img("how_step3")},
        {"text": f"Real numbers:\n${n['start']}/month\nfor {n['years']} years\n= ${n['end']}",
         "speech": SPEECH_TEMPLATES["secret_strategy"][4].format(start_amount=n['start'], years=n['years'], end_amount=n['end']),
         "img": _get_img("real_numbers")},
        {"text": f"Start with\n${strategy['min']}\nRIGHT NOW\nNo excuses",
         "speech": SPEECH_TEMPLATES["secret_strategy"][5].format(min_amount=strategy['min']),
         "img": _get_img("start_now")},
        {"text": f"This builds\n${strategy['result']} quietly\nDid you catch it?\nFollow for more",
         "speech": SPEECH_TEMPLATES["secret_strategy"][6].format(result=strategy['result']),
         "img": _get_img("cta")},
    ]
    return {"title": title, "slides": _to_7_slides(slides), "keywords": [strategy["name"].title(), "Wealth Strategy", "Investing"]}


def _build_long_topic():
    """Build a 20-slide long-form topic by combining two frameworks or expanding one."""
    framework1 = random.choice(["person_story", "famous_person", "myth_buster", "rich_vs_poor", "side_hustle"])
    framework2 = random.choice(["money_math", "rules_list", "age_timeline", "money_challenge", "secret_strategy"])

    topic1 = _build_topic(framework1)
    topic2 = _build_topic(framework2)

    if not topic1 or not topic2:
        return None

    combined_title_templates = [
        f"The Complete Money Guide — {topic1['title'][:40]} + {topic2['keywords'][0]}",
        f"Everything About Money In 10 Minutes (Watch This If You're Broke)",
        f"From Broke To Wealthy — The Full Blueprint ({topic1['keywords'][0]} + {topic2['keywords'][0]})",
        f"The Money Masterclass Nobody Teaches You ({topic1['keywords'][0]} Edition)",
        f"10 Minutes That Will Change Your Financial Life Forever",
        f"Watch This Before You Spend Another Dollar ({topic1['keywords'][0]} Deep Dive)",
    ]
    title = random.choice(combined_title_templates)

    slides = topic1["slides"] + topic2["slides"]
    keywords = list(set(topic1["keywords"] + topic2["keywords"]))[:5]

    return {"title": title, "slides": slides, "keywords": keywords}
