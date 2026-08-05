import random
import hashlib
from datetime import datetime

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
        {"role": "discovery", "template": "Then {pronoun} discovered\n{method_name}\nand everything\nchanged"},
        {"role": "action1", "template": "Step 1:\n{action_step_1}"},
        {"role": "action2", "template": "Step 2:\n{action_step_2}"},
        {"role": "action3", "template": "Step 3:\n{action_step_3}"},
        {"role": "result_early", "template": "After {short_time}:\n${early_result}\nsaved and invested"},
        {"role": "result_big", "template": "After {long_time}:\n${big_result}\nnet worth"},
        {"role": "lesson", "template": "The lesson:\n{key_lesson}\nAnyone can do this"},
        {"role": "cta", "template": "Start with ${min_start}\ntoday\nYour future self\nwill THANK you"},
    ],
    "myth_buster": [
        {"role": "hook", "template": "Everything you\nknow about\n{topic} is WRONG"},
        {"role": "myth1", "template": "Myth 1:\n{myth_1}\nREALITY:\n{reality_1}"},
        {"role": "myth2", "template": "Myth 2:\n{myth_2}\nREALITY:\n{reality_2}"},
        {"role": "myth3", "template": "Myth 3:\n{myth_3}\nREALITY:\n{reality_3}"},
        {"role": "shocking_stat", "template": "SHOCKING FACT:\n{fact}\n{follow_up}"},
        {"role": "what_rich_do", "template": "What rich people\nactually do:\n{rich_habit}"},
        {"role": "simple_fix", "template": "The simple fix:\n{fix_step_1}\n{fix_step_2}"},
        {"role": "proof", "template": "Proof it works:\n${proof_amount}\nin {proof_time}\nfrom this alone"},
        {"role": "mindset", "template": "The real difference:\n{mindset_shift}"},
        {"role": "cta", "template": "Stop believing\nthe myths\nStart building\nwealth TODAY"},
    ],
    "money_math": [
        {"role": "hook", "template": "Your ${daily_cost}\n{expense}\nhabit is costing\nyou ${lifetime_cost}"},
        {"role": "daily_breakdown", "template": "${daily_cost} per day\n= ${monthly_cost}/month\n= ${yearly_cost}/year\nSeems small right?"},
        {"role": "compound_reveal", "template": "But invested at\n{percent}% per year\nfor {years} years\nthat becomes\n${compound_total}"},
        {"role": "comparison", "template": "That's enough to:\n{comparison_1}\n{comparison_2}\n{comparison_3}"},
        {"role": "not_just_one", "template": "And it's not\njust {expense}\nAdd {expense_2}\n+ {expense_3}\n= ${combined_yearly}/year WASTED"},
        {"role": "alternative", "template": "The swap:\nInstead of {old_habit}\ndo {new_habit}\nSave ${save_amount}/month"},
        {"role": "invest_it", "template": "Put that ${save_amount}\ninto {investment}\nEvery single month\nAutomatically"},
        {"role": "future_result", "template": "In {years} years:\n${future_value}\nFrom ONE simple\nswap"},
        {"role": "perspective", "template": "You're not\ngiving up {expense}\nYou're BUYING\nyour freedom"},
        {"role": "cta", "template": "Make the swap\nTODAY\n${save_amount}/month\n= ${future_value} future"},
    ],
    "rules_list": [
        {"role": "hook", "template": "{count} Money Rules\nThat Separate\nRICH from POOR"},
        {"role": "rule1", "template": "Rule 1:\n{rule_1}\n{rule_1_explain}"},
        {"role": "rule2", "template": "Rule 2:\n{rule_2}\n{rule_2_explain}"},
        {"role": "rule3", "template": "Rule 3:\n{rule_3}\n{rule_3_explain}"},
        {"role": "rule4", "template": "Rule 4:\n{rule_4}\n{rule_4_explain}"},
        {"role": "rule5", "template": "Rule 5:\n{rule_5}\n{rule_5_explain}"},
        {"role": "common_mistake", "template": "The #1 mistake:\n{big_mistake}\nThis alone keeps\npeople BROKE"},
        {"role": "rich_vs_poor", "template": "Rich people:\n{rich_do}\nPoor people:\n{poor_do}"},
        {"role": "start_today", "template": "Pick just ONE\nrule to follow\nthis week\nThat's all it takes"},
        {"role": "cta", "template": "Follow for\nmore rules that\nbuild REAL wealth"},
    ],
    "famous_person": [
        {"role": "hook", "template": "{famous_name} said\nthis ONE thing\nabout money and\nit changed\nEVERYTHING"},
        {"role": "quote", "template": "The rule:\n\"{money_rule}\"\nSimple but\nMOST people\nignore it"},
        {"role": "backstory", "template": "{famous_name} is worth\n${net_worth}\nBuilt from\n{origin_story}"},
        {"role": "explain", "template": "What this means:\n{explanation_1}\n{explanation_2}"},
        {"role": "example", "template": "Real example:\n{real_example}\nThis is how\nit works in\nreal life"},
        {"role": "mistake", "template": "The mistake\nmost people make:\n{common_mistake}\nThis DESTROYS\nwealth"},
        {"role": "apply_it", "template": "How to apply\nthis TODAY:\n{apply_step_1}\n{apply_step_2}"},
        {"role": "result", "template": "If you follow\nthis rule:\n${potential_result}\nin {result_time}"},
        {"role": "other_billionaires", "template": "Other billionaires\nwho follow this:\n{billionaire_2}\n{billionaire_3}"},
        {"role": "cta", "template": "One rule\nOne change\nStart TODAY\nYour wallet\nwill thank you"},
    ],
    "age_timeline": [
        {"role": "hook", "template": "At {age_start} you should\nhave ${amount_start}\nsaved\nDo you?"},
        {"role": "age_20", "template": "By age 20:\n${goal_20} saved\nHow: {how_20}"},
        {"role": "age_25", "template": "By age 25:\n${goal_25} saved\nHow: {how_25}"},
        {"role": "age_30", "template": "By age 30:\n${goal_30} saved\nHow: {how_30}"},
        {"role": "age_40", "template": "By age 40:\n${goal_40} saved\nHow: {how_40}"},
        {"role": "behind", "template": "Behind?\nDON'T PANIC\nHere's how to\ncatch up FAST"},
        {"role": "catch_up_1", "template": "Catch-up strategy 1:\n{catchup_1}"},
        {"role": "catch_up_2", "template": "Catch-up strategy 2:\n{catchup_2}"},
        {"role": "compound_power", "template": "Starting late?\n${late_start}/month\nat age {late_age}\nstill becomes\n${late_result} by 65"},
        {"role": "cta", "template": "The best time\nto start was\n10 years ago\nThe second best\ntime is TODAY"},
    ],
}

# ── SPEECH TEMPLATES (matching slide frameworks) ──
SPEECH_TEMPLATES = {
    "person_story": [
        "{person_name} was a {job}, {story_detail}, making just {low_salary} thousand dollars a year. Nobody thought {pronoun} would ever build wealth.",
        "Every month it was the same cycle. Earn money. Spend money. Nothing left. {pronoun_cap} had {debt} thousand dollars in debt and zero savings.",
        "Then {pronoun} discovered {method_name}. And EVERYTHING changed. Not overnight. But the shift started immediately.",
        "Step one. {speech_action_1}. This alone changed the game.",
        "Step two. {speech_action_2}. Most people skip this but it's the most important part.",
        "Step three. {speech_action_3}. This is where the real magic happens.",
        "After just {short_time}, {pronoun} had {early_result} dollars saved and invested. From NOTHING to {early_result} dollars. Let that sink in.",
        "After {long_time}, {pronoun_possessive} net worth hit {big_result} dollars. A {job} with a {big_result} dollar net worth. Sounds impossible but the math doesn't lie.",
        "The lesson is simple. {key_lesson}. Anyone can do this. Literally anyone. You don't need a degree. You don't need connections. You need discipline.",
        "Start with just {min_start} dollars today. Set it up right now. Your future self will be a completely different person because of what you do in the next five minutes.",
    ],
    "myth_buster": [
        "Everything you KNOW about {topic} is completely WRONG. And these myths are keeping you BROKE.",
        "Myth number one. {myth_1}. WRONG. The reality is {reality_1}. This myth alone keeps millions of people poor.",
        "Myth number two. {myth_2}. Also WRONG. The reality is {reality_2}. Once you understand this, everything changes.",
        "Myth number three. {myth_3}. Completely FALSE. The reality is {reality_3}. Your parents probably told you this one.",
        "Here's a SHOCKING fact. {fact}. {follow_up}. Let that sink in for a moment.",
        "What do rich people actually do? {rich_habit}. It's not complicated. It's not a secret. It's just DISCIPLINE.",
        "The simple fix. First, {fix_step_1}. Second, {fix_step_2}. That's literally it. No magic required.",
        "Proof it works. {proof_amount} dollars in {proof_time} from doing just this ONE thing. The numbers don't lie.",
        "The REAL difference between rich and poor isn't money. It's {mindset_shift}. Change your mind and the money follows.",
        "Stop believing the myths that keep you broke. Start building REAL wealth today. Subscribe for more money truths.",
    ],
    "money_math": [
        "Your {daily_cost} dollar {expense} habit is secretly costing you {lifetime_cost} dollars. And I'm going to prove it right now.",
        "{daily_cost} dollars per day. That's {monthly_cost} per month. {yearly_cost} per year. Seems small right? Watch what happens next.",
        "If you invested that money at {percent} percent per year for {years} years, compound interest turns it into {compound_total} dollars. Read that number again.",
        "That's enough to {comparison_1}. Or {comparison_2}. Or {comparison_3}. From just cutting ONE habit.",
        "And it's not just {expense}. Add {expense_2} plus {expense_3} and you're wasting {combined_yearly} dollars per year. That money is just GONE.",
        "The swap is easy. Instead of {old_habit}, do {new_habit}. You'll save {save_amount} dollars per month without feeling it.",
        "Put that {save_amount} dollars into {investment}. Every single month. Automatically. Set it and forget it.",
        "In {years} years that becomes {future_value} dollars. From ONE simple swap. Not a sacrifice. A SWAP.",
        "You're not giving up {expense}. You're BUYING your freedom. You're trading a small pleasure today for total financial freedom tomorrow.",
        "Make the swap today. {save_amount} dollars per month equals {future_value} dollars in your future. The math is on your side.",
    ],
    "rules_list": [
        "{count} money rules that separate the RICH from the POOR. If you follow even THREE of these, your finances will transform.",
        "Rule one. {rule_1}. {rule_1_explain}. This is the foundation of ALL wealth building.",
        "Rule two. {rule_2}. {rule_2_explain}. Most people do the exact opposite of this.",
        "Rule three. {rule_3}. {rule_3_explain}. This one will save you THOUSANDS every year.",
        "Rule four. {rule_4}. {rule_4_explain}. Wealthy people figured this out early. Now you know too.",
        "Rule five. {rule_5}. {rule_5_explain}. Follow this and you're already ahead of ninety percent of people.",
        "The number one mistake that keeps people broke is {big_mistake}. If you fix just THIS, everything else gets easier.",
        "Rich people {rich_do}. Poor people {poor_do}. Same hours in a day. Different choices. Different results.",
        "Pick just ONE rule to follow this week. Not all five. Just ONE. Master it. Then add another. Small steps build empires.",
        "Follow The AI Dollar for more wealth building rules. We drop new money lessons every single day. Subscribe and turn on notifications.",
    ],
    "famous_person": [
        "{famous_name} said ONE thing about money that changed EVERYTHING. And most people completely ignore it.",
        "The rule is simple. {money_rule}. Four words that are worth BILLIONS. Yet most people hear it and do nothing.",
        "{famous_name} is worth {net_worth} dollars. Built from {origin_story}. This isn't theory. This is PROVEN.",
        "What this really means is {explanation_1}. And more importantly, {explanation_2}. Simple but powerful.",
        "Real example. {real_example}. This is how this rule works in everyday life for normal people like us.",
        "The mistake most people make is {common_mistake}. And this single mistake DESTROYS any chance of building wealth.",
        "How to apply this TODAY. First, {apply_step_1}. Second, {apply_step_2}. Do these two things and you're already winning.",
        "If you follow this one rule consistently, you could have {potential_result} dollars in {result_time}. The math is real.",
        "Other billionaires who follow this exact same rule include {billionaire_2} and {billionaire_3}. It's not a coincidence.",
        "One rule. One change. Start TODAY. Your wallet your bank account and your future self will ALL thank you.",
    ],
    "age_timeline": [
        "At age {age_start}, you should have {amount_start} dollars saved. Do you? If not, keep watching because I'm about to show you exactly what to do.",
        "By age twenty, you should have {goal_20} dollars saved. How? {how_20}. This sets the foundation for everything.",
        "By age twenty five, you should have {goal_25} dollars saved. How? {how_25}. This is where momentum kicks in.",
        "By age thirty, the target is {goal_30} dollars. How? {how_30}. You should be investing consistently by now.",
        "By age forty, you should have {goal_40} dollars saved. How? {how_40}. Compound interest is doing the heavy lifting.",
        "If you're behind, DON'T PANIC. Seriously. Here's how to catch up FAST. It's not too late.",
        "Catch up strategy one. {catchup_1}. This alone can add thousands per year to your savings.",
        "Catch up strategy two. {catchup_2}. Combine both strategies and you'll be back on track within a year.",
        "Starting late? {late_start} dollars per month at age {late_age} still becomes {late_result} dollars by age sixty five. The math works at ANY age.",
        "The best time to start was ten years ago. The second best time is RIGHT NOW. Not tomorrow. Not next month. Today. Open that account. Start that transfer. DO IT.",
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

# ── USED TITLE HASHES (never repeat tracker) ──
_generated_title_hashes = set()


def _hash_title(title):
    return hashlib.md5(title.encode()).hexdigest()[:12]


def generate_short_topic():
    """Generate a unique short-form topic that has never been generated before."""
    global _generated_title_hashes

    for attempt in range(200):
        framework_name = random.choice(list(SLIDE_FRAMEWORKS.keys()))
        topic = _build_topic(framework_name)
        if topic:
            title_hash = _hash_title(topic["title"])
            if title_hash not in _generated_title_hashes:
                _generated_title_hashes.add(title_hash)
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
    except Exception as e:
        print(f"[WARN] Topic build failed ({framework_name}): {e}")
        return None


def _get_img(role):
    prompts = IMAGE_PROMPTS.get(role, ["professional finance education visual"])
    return random.choice(prompts)


def _build_person_story():
    persona = random.choice(PERSONAS)
    method = random.choice(METHODS)
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
         "speech": SPEECH_TEMPLATES["person_story"][0].format(person_name=persona['name'], job=persona['job'], story_detail=persona['story'], low_salary=low_salary, pronoun=pronoun),
         "img": _get_img("hook")},
        {"text": f"Every month\nthe same cycle:\nearn → spend →\nNOTHING left\n${debt}K in debt",
         "speech": SPEECH_TEMPLATES["person_story"][1].format(pronoun=pronoun, pronoun_cap=pronoun_cap, debt=debt),
         "img": _get_img("struggle")},
        {"text": f"Then {pronoun} discovered\n{method['name']}\nand everything\nchanged",
         "speech": SPEECH_TEMPLATES["person_story"][2].format(pronoun=pronoun, method_name=method['name']),
         "img": _get_img("discovery")},
        {"text": f"Step 1:\n{action_steps[0][0]}",
         "speech": f"Step one. {action_steps[0][1]}. This alone changed the game.",
         "img": _get_img("action1")},
        {"text": f"Step 2:\n{action_steps[1][0]}",
         "speech": f"Step two. {action_steps[1][1]}. Most people skip this but it's the most important part.",
         "img": _get_img("action2")},
        {"text": f"Step 3:\n{action_steps[2][0]}",
         "speech": f"Step three. {action_steps[2][1]}. This is where the real magic happens.",
         "img": _get_img("action3")},
        {"text": f"After {short_time}:\n${early_result:,}\nsaved and invested\nFrom NOTHING",
         "speech": f"After just {short_time}, {pronoun} had {early_result:,} dollars saved and invested. From NOTHING to {early_result:,} dollars. Let that sink in.",
         "img": _get_img("result_early")},
        {"text": f"After {long_time}:\n${big_result:,}\nnet worth\nAs a {persona['job']}",
         "speech": f"After {long_time}, {pronoun_poss} net worth hit {big_result:,} dollars. A {persona['job']} with a {big_result:,} dollar net worth. The math doesn't lie.",
         "img": _get_img("result_big")},
        {"text": f"The lesson:\n{method['name'].upper()}\n+ CONSISTENCY\n= WEALTH\nAnyone can do this",
         "speech": f"The lesson is simple. {method['name']} plus consistency equals wealth. Anyone can do this. You don't need a degree. You need discipline.",
         "img": _get_img("lesson")},
        {"text": f"Start with ${min_start}\ntoday\nYour future self\nwill THANK you",
         "speech": f"Start with just {min_start} dollars today. Set it up right now. Your future self will be a completely different person because of this moment.",
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
         "speech": f"Everything you KNOW about {myth_set['topic']} is completely WRONG. And these myths are keeping you BROKE.",
         "img": _get_img("hook")},
        {"text": f"Myth 1:\n{myths[0]['myth']}\nREALITY:\n{myths[0]['reality'][:50]}",
         "speech": f"Myth number one. {myths[0]['myth']}. WRONG. The reality is {myths[0]['reality']}.",
         "img": _get_img("myth1")},
        {"text": f"Myth 2:\n{myths[1]['myth']}\nREALITY:\n{myths[1]['reality'][:50]}",
         "speech": f"Myth number two. {myths[1]['myth']}. Also WRONG. The reality is {myths[1]['reality']}.",
         "img": _get_img("myth2")},
        {"text": f"Myth 3:\n{myths[2]['myth']}\nREALITY:\n{myths[2]['reality'][:50]}",
         "speech": f"Myth number three. {myths[2]['myth']}. Completely FALSE. The reality is {myths[2]['reality']}.",
         "img": _get_img("myth3")},
        {"text": f"SHOCKING FACT:\n{fact_data['fact'][:60]}",
         "speech": f"Here's a SHOCKING fact. {fact_data['fact']}. {fact_data['follow_up']}.",
         "img": _get_img("shocking_stat")},
        {"text": f"What rich people\nactually do:\n{random.choice(rich_habits)[:60]}",
         "speech": f"What do rich people actually do? {random.choice(rich_habits)}",
         "img": _get_img("what_rich_do")},
        {"text": f"The fix:\n1. {fix[0][:40]}\n2. {fix[1][:40]}",
         "speech": f"The simple fix. First, {fix[0]}. Second, {fix[1]}. That's literally it.",
         "img": _get_img("simple_fix")},
        {"text": f"Proof:\n${proof_amount:,}\nin {proof_time}\nfrom this alone",
         "speech": f"Proof it works. {proof_amount:,} dollars in {proof_time} from doing just this ONE thing.",
         "img": _get_img("proof")},
        {"text": f"The real difference:\n{random.choice(mindset_shifts)}",
         "speech": f"The REAL difference between rich and poor isn't money. It's this: {random.choice(mindset_shifts)}.",
         "img": _get_img("mindset")},
        {"text": f"Stop believing\nthe myths\nStart building\nwealth TODAY",
         "speech": "Stop believing the myths that keep you broke. Start building REAL wealth today. Subscribe for more money truths that actually work.",
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

    return {"title": title, "slides": slides, "keywords": [data["expense"].title(), "Compound Interest", "Saving Money"]}


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

    return {"title": title, "slides": slides, "keywords": ["Money Rules", "Rich vs Poor", "Wealth Building"]}


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

    return {"title": title, "slides": slides, "keywords": [person["name"], "Money Rules", "Investing"]}


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

    return {"title": title, "slides": slides, "keywords": ["Savings Goals", "Age Milestones", "Retirement"]}


def _build_long_topic():
    """Build a 20-slide long-form topic by combining two frameworks or expanding one."""
    framework1 = random.choice(["person_story", "famous_person", "myth_buster"])
    framework2 = random.choice(["money_math", "rules_list", "age_timeline"])

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
