#!/usr/bin/env python3
"""
The AI Dollar - Video Generator
Finance education Shorts with per-slide audio sync + zoom + crossfade + deep male TTS
"""

import os
import gc
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

CONFIG = {"output_dir": "./videos"}

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")


CONTENT_TOPICS = [
    {
        "title": "This Is Why You're Poor (3 Reasons Your Money Disappears)",
        "slides": [
            {"text": "RIGHT NOW\nyour cash is\nLOSING VALUE", "speech": "While you watch this video, your money is actively losing value. Not tomorrow, not next month. RIGHT NOW.", "img": "a real hundred dollar bill burning with orange flames on a dark background"},
            {"text": "Check this out\nInflation hit 7%\nthis year alone", "speech": "Inflation just hit seven percent. That means prices on everything you buy skyrocketed. Your money? It stayed exactly the same.", "img": "price tags on store shelves glowing red as numbers spike upward"},
            {"text": "You lost $7\nfrom $100\nfor literally\nDOING NOTHING", "speech": "One hundred dollars you worked hard for? Now worth ninety three. Seven dollars gone. And you didn't even spend it.", "img": "an open empty wallet with a red X on it"},
            {"text": "This happens\nEVERY\nSINGLE YEAR", "speech": "Seven dollars gone THIS YEAR. Next year? Another seven gone. Then another. And another.", "img": "a calendar showing years stacking up with money disappearing each year"},
            {"text": "Your mattress\nIS EATING YOUR\nWEALTH", "speech": "People think hiding cash under their mattress is safe. It's not safe. It's LOSING MONEY. Your mattress is literally stealing from you.", "img": "money hidden under a mattress slowly fading away into darkness"},
            {"text": "You MUST\ninvest\nor go broke", "speech": "This is not optional. If you don't invest, you're broke in slow motion. That's facts.", "img": "a crossroads with two paths: one going down to bankruptcy, one going up to wealth"},
            {"text": "Stocks CRUSH\ninflation\n10% vs 3%", "speech": "The stock market averages ten percent gains per year. Inflation is three percent. Do the math. Stocks are DOMINATING.", "img": "stock market chart exploding upward with green candles breaking through the roof"},
            {"text": "Your money\ngrows FASTER\nthan prices\nrise", "speech": "For every three percent inflation steals, stocks give you ten percent growth. The gap is your WEALTH.", "img": "an upward rocket ship breaking through clouds heading to the moon"},
            {"text": "Compound\ninterest is\nCHEATCODE\nmoney", "speech": "Your money earns returns. Those returns earn MORE returns. It explodes exponentially. This is how rich people get richer.", "img": "an exponential curve shooting straight up into infinity"},
            {"text": "START TODAY\nOr lose THOUSANDS\nby tomorrow", "speech": "Every single day you wait costs you thousands of dollars in compound growth. This isn't motivation. It's math. START TODAY.", "img": "a clock showing time running out with money being lost with each second"},
        ],
        "keywords": ["Inflation", "Stocks", "Wealth", "Investing"],
    },
    {
        "title": "$5 Daily Habit = $1M In 40 Years (Most People Don't Know This)",
        "slides": [
            {"text": "FIVE DOLLARS\nA DAY\nBECOMES A\nMILLION", "speech": "Your morning coffee. That five dollar latte. Invested every day? Becomes over ONE MILLION DOLLARS. This is not theory. This is math.", "img": "a steaming coffee cup transforming into stacks of hundred dollar bills"},
            {"text": "That's literally\nthe cost of\nyour breakfast", "speech": "Five dollars. That's what you spend on breakfast without thinking. You wouldn't even FEEL the loss.", "img": "a coffee cup and pastry on a cafe table with $5 bill"},
            {"text": "Year ONE\n$1,800", "speech": "After just one year of investing? You've got eighteen hundred dollars. That's a vacation right there.", "img": "a beach vacation scene with money floating in the sand"},
            {"text": "Year TEN\n$30,727", "speech": "Year ten? Thirty thousand dollars. That's a CAR. An actual car. From coffee money.", "img": "a sleek new car with a price tag showing 30k"},
            {"text": "Year TWENTY\n$96,453", "speech": "Year twenty? Nearly one hundred thousand dollars. That's a down payment on a HOUSE.", "img": "a dream house with a sold sign and keys hanging on it"},
            {"text": "Year THIRTY\n$339,073", "speech": "Thirty years? Over THREE HUNDRED THOUSAND DOLLARS. That's generational wealth.", "img": "a luxury penthouse suite overlooking a glittering city at night"},
            {"text": "Year FORTY\n$1,062,000", "speech": "Year forty? Over ONE MILLION DOLLARS. From FIVE DOLLARS A DAY.", "img": "a vault door opening to reveal mountains of gold bars and cash"},
            {"text": "Compound interest\nis the EIGHTH\nWONDER OF THE\nWORLD", "speech": "Einstein called it the eighth wonder of the world. Your money makes money. That money makes MORE money. Unstoppable.", "img": "an exponential curve shooting into infinity with energy and light"},
            {"text": "It EXPLODES\nin year 20+", "speech": "The first ten years? Slow. But then it EXPLODES. The curve goes VERTICAL. This is where wealth gets insane.", "img": "a rocket ship launching with exponential growth bar chart behind it"},
            {"text": "WAIT ONE YEAR\nLOSE $50K\nin lifetime gains", "speech": "Delay one year? You lose fifty thousand dollars in lifetime returns. FIFTY THOUSAND. For what? To NOT invest five dollars?", "img": "a calendar with a year crossed out and money vanishing"},
        ],
        "keywords": ["Compound Interest", "Wealth", "Investing", "Rich"],
    },
    {
        "title": "Bad Credit Costs You $100K (3 Rules to Fix It Fast)",
        "slides": [
            {"text": "Bad credit\nCOSTS YOU\n$100,000", "speech": "Bad credit doesn't just hurt your feelings. It DESTROYS your wealth. We're talking ONE HUNDRED THOUSAND DOLLARS literally stolen from you.", "img": "a credit score meter shattered into pieces with red destructive energy"},
            {"text": "On that $300K\nmortgage you want", "speech": "When you apply for a three hundred thousand dollar mortgage to buy your dream house.", "img": "a beautiful dream house burning with a sold sign on fire"},
            {"text": "Good score 740+?\nYou pay 6.5%\nand keep money", "speech": "A credit score above seven forty gets you six point five percent interest. You're WINNING.", "img": "a glowing green checkmark surrounded by gold coins celebrating victory"},
            {"text": "Bad score below 580?\nYou pay 9.5%\nand GET CRUSHED", "speech": "But a score below five eighty? Nine point five percent or HIGHER. You're getting ANNIHILATED.", "img": "a massive avalanche of debt crushing a person in red darkness"},
            {"text": "That $100K difference\nis money you EARNED\ngoing to banks", "speech": "That hundred thousand dollar difference is money you EARNED, that a bank steals from you over 30 years. HUNDRED THOUSAND DOLLARS.", "img": "money bills being vacuumed out of someone's wallet continuously"},
            {"text": "How to DOMINATE\nthis problem?\n3 unstoppable rules", "speech": "So how do you DOMINATE your credit and take back your money? Three unstoppable rules.", "img": "three golden shields arranged like a fortress wall against red attacks"},
            {"text": "RULE 1: Always pay\non time. ALWAYS.\nEven minimum", "speech": "Rule one, ALWAYS pay on time, even if it's just the minimum. Payment history is THIRTY FIVE PERCENT of your score. This is CRITICAL.", "img": "a calendar exploding with green checkmarks showing perfect on-time payments"},
            {"text": "RULE 2: Blast\nbalances below 30%\nof your limit", "speech": "Rule two, BLAST your balances below thirty percent. If your limit is a thousand, never carry more than three hundred. Keep your credit utilization TIGHT.", "img": "a credit card with a powerful green progress bar showing low usage"},
            {"text": "RULE 3: NEVER\nclose your oldest card\nIt's your wealth weapon", "speech": "Rule three, NEVER close your oldest card. The length of your credit history is a WEAPON. It ages like fine wine.", "img": "an ancient golden credit card on a pedestal with a long timeline behind it"},
            {"text": "Fix your credit\nand STEAL back\n$100K over time", "speech": "Fix your credit NOW and STEAL back that hundred thousand dollars that banks were about to steal from you. Your wealth depends on this.", "img": "a glowing shield protecting mountains of gold coins from debt darkness"},
        ],
        "keywords": ["Credit Score", "Finance", "Mortgage", "Wealth Building"],
    },
    {
        "title": "The 50/30/20 Budget Formula (Build Wealth On Any Salary)",
        "slides": [
            {"text": "This budget rule\nDESTROYED my\nfinancial chaos", "speech": "This budget rule DESTROYED my financial chaos and turned me into a money-building MACHINE.", "img": "a person breaking free from chains of overspending with golden light"},
            {"text": "Take your paycheck\nany size\nDOES NOT MATTER", "speech": "Take your paycheck, any size works. Twenty thousand or two hundred thousand. The ratio works EVERYWHERE.", "img": "a massive paycheck envelope glowing with gold being held up triumphantly"},
            {"text": "50% to needs\nRent food bills\nTransportation", "speech": "Fifty percent goes to NEEDS. That's rent, food, bills, transportation. The bare essentials that keep you alive.", "img": "a modern apartment building lit up with essential services flowing in"},
            {"text": "30% to WANTS\nFun shopping eating\nYes, you DESERVE it", "speech": "Thirty percent goes to WANTS. Fun stuff, shopping, eating out. YES, you deserve to enjoy your money. Stop feeling guilty.", "img": "colorful shopping bags exploding with joy and celebration energy"},
            {"text": "20% goes STRAIGHT\nto savings and\ninvesting no excuses", "speech": "And TWENTY PERCENT goes straight to savings and investing. No excuses. This is non-negotiable.", "img": "a golden river of money flowing directly into a growing vault"},
            {"text": "The SECRET?\nPay savings FIRST\nNot last", "speech": "But here's the CHEAT CODE. Pay your savings FIRST, not last. The SECOND your paycheck hits, move that twenty percent out of reach.", "img": "a rocket launching money directly into space avoiding temptation"},
            {"text": "Automate it\nso you never\neven SEE it", "speech": "Set up automatic transfers so you literally never see that money. It's gone before you can spend it. BOOM. Wealth guaranteed.", "img": "a robotic hand slamming an automate button with electricity sparking"},
            {"text": "Within ONE month\nyou won't even\nnotice its missing", "speech": "Within one month you'll adjust to spending less. I PROMISE. Your lifestyle shifts automatically. You don't suffer.", "img": "a person relaxing peacefully on a couch with a satisfied smile"},
            {"text": "Most millionaires\nstarted with THIS\nexact simple rule", "speech": "Most millionaires didn't start with complicated strategies. They started with THIS. The simple 50/30/20 CRUSH.", "img": "a silhouette of a wealthy person standing on top of skyscrapers at sunrise"},
            {"text": "3 numbers\n50 30 20\nThats the ENTIRE\nwealth formula", "speech": "No fancy apps needed. No complexity. Just three numbers. 50, 30, 20. That's your entire wealth-building formula. START TODAY.", "img": "three glowing golden numbers exploding with power on a dark background"},
        ],
        "keywords": ["Budgeting", "50/30/20", "Wealth Formula"],
    },
    {
        "title": "Stocks vs Bonds: Which Wins? (80/20 Rule Explained)",
        "slides": [
            {"text": "Stocks vs Bonds\nWhich one DESTROYS\nthe other?", "speech": "Stocks versus bonds. Which one DESTROYS the other? Let's end this debate right now.", "img": "a charging bull and a soaring eagle colliding in dramatic battle"},
            {"text": "A stock means\nYOU OWN a piece\nof a real company", "speech": "When you buy a stock, you OWN a tiny piece of a REAL COMPANY. If that company EXPLODES, so does your investment.", "img": "a gleaming corporate skyscraper shooting upward with lightning strikes"},
            {"text": "It EXPLODES up?\nYour wealth EXPLODES\nIt CRASHES?\nYou lose", "speech": "But it crashes? You LOSE. Stocks are a two-way street.", "img": "a dramatic roller coaster with people screaming through peaks and deadly valleys"},
            {"text": "Stocks average\n10% per year\nbut expect the CHAOS", "speech": "Stocks average about ten percent per year historically. But that comes with wild swings, crashes, recoveries, and CHAOS.", "img": "a neon green zigzag chart violently dancing across a dark screen"},
            {"text": "A bond means\nyou LEND money\nto government or\ncompany", "speech": "A bond is different. You LEND money to a government or company. They PROMISE to pay you back with interest.", "img": "a government treasury building made of solid gold in grand daylight"},
            {"text": "They MUST pay you\nback with interest\nno exceptions", "speech": "It's a CONTRACT. They MUST pay you back. It's steady, predictable, RELIABLE.", "img": "a calm peaceful ocean at sunset with waves moving in perfect rhythm"},
            {"text": "Bonds average\n4-5% per year\nsmooth and SAFE", "speech": "Bonds average about four to five percent per year. Much SAFER, but lower returns. You trade growth for stability.", "img": "a perfectly straight road stretching infinitely through calm countryside"},
            {"text": "The REAL wealth\nstrategy? MIX BOTH\nget explosive growth\nwith safety", "speech": "The REAL wealth strategy that crushes all others? MIX BOTH. Get explosive growth AND safety. Best of both worlds.", "img": "a golden balance scale with coins on both sides in perfect harmony"},
            {"text": "Young and HUNGRY?\n80% stocks 20% bonds\nyou have DECADES", "speech": "If you're young and hungry for wealth, go 80 percent stocks, 20 percent bonds. You have DECADES to recover from crashes.", "img": "a young aggressive investor pumping their fist looking at green rockets"},
            {"text": "Getting older?\nFlip it for survival\nMore bonds protect\nyour nest egg", "speech": "As you get older, flip it. More bonds to protect your nest egg since you'll need it sooner. This is called ASSET ALLOCATION and it WORKS.", "img": "a retired couple on a porch watching the sunset over safe investments"},
        ],
        "keywords": ["Stocks", "Bonds", "Asset Allocation", "Investing"],
    },
    {
        "title": "$800 Car Repair Destroyed Them (Build Emergency Fund Now)",
        "slides": [
            {"text": "No emergency fund?\nYou're ONE CRISIS\naway from DISASTER", "speech": "No emergency fund? Let me show you EXACTLY how fast your life can spiral into DISASTER.", "img": "a glowing red emergency alarm shrieking in a dark industrial corridor"},
            {"text": "Your car EXPLODES\n$800 repair bill\nTOMORROW", "speech": "Your car breaks down TOMORROW. Eight hundred dollar repair bill. RIGHT NOW.", "img": "a car smoking with flames and a repair shop bill flying out the windshield"},
            {"text": "No savings?\nCredit card at\n24% BLOODSUCKING\ninterest", "speech": "Without any savings, that goes straight onto a credit card at TWENTY FOUR PERCENT bloodsucking interest.", "img": "a credit card swiping with red lightning bolts and demon energy"},
            {"text": "That $800\njust became $1,100\nin months\nyou got CRUSHED", "speech": "That eight hundred dollar problem just became ELEVEN HUNDRED DOLLARS by the time you pay it off. You got CRUSHED.", "img": "a calculator exploding with growing numbers devouring a stack of bills"},
            {"text": "But an emergency fund?\nPREVENTS THIS\nCOMPLETELY", "speech": "But an emergency fund? PREVENTS THIS COMPLETELY. It's your financial FORTRESS against disaster.", "img": "a massive safety net catching falling coins with golden protective energy"},
            {"text": "Goal: Save 3-6 months\nof expenses\nThat's your armor", "speech": "The goal is to save THREE TO SIX MONTHS of your living expenses. That's your ARMOR against life.", "img": "six calendar pages fanned out with mountains of glowing gold coins"},
            {"text": "Put it in a high\nyield account\n4-5% EXPLODES\nyour money", "speech": "Put it in a high yield savings account earning FOUR TO FIVE PERCENT. Your safety net MAKES MONEY while it protects you.", "img": "a smartphone showing a savings account with a green bar EXPLODING upward"},
            {"text": "Your money makes\nmoney while it\nprotects you\nWIN WIN", "speech": "You don't need to build it overnight. Start SMALL and dominate from there.", "img": "a tiny green plant with gold coins sprouting upward in morning sunlight"},
            {"text": "Start with $500\nAdd $50 every\npaycheck CRUSH it", "speech": "Start with just five hundred dollars. Then add fifty dollars from EVERY SINGLE paycheck. CRUSH IT.", "img": "coins stacking higher and higher into a towering fortress of wealth"},
            {"text": "In one year you'll\nhave a FORTRESS\nnobody can touch", "speech": "In one year you'll have a FORTRESS that makes you BULLETPROOF against ANY emergency. The peace of mind is PRICELESS. BUILD IT NOW.", "img": "a person standing confident on a mountain of coins at glorious sunrise"},
        ],
        "keywords": ["Emergency Fund", "Financial Safety", "Savings"],
    },
    {
        "title": "Recessions Make Millionaires (The Crash Strategy Rich Use)",
        "slides": [
            {"text": "A recession is coming\nWatch what happens\nto WEAK investors", "speech": "A recession is coming. Watch what happens to weak investors while the RICH get richer.", "img": "massive black storm clouds with lightning above a city in chaos"},
            {"text": "Companies CRASH\nthey start cutting\nworkers like crazy", "speech": "Companies CRASH and START CUTTING workers like their lives depend on it. Layoffs EXPLODE.", "img": "a dark abandoned corporate office with empty desks and shadows"},
            {"text": "Millions LOSE jobs\nincome EXPLODES\ndownward", "speech": "Workers LOSE their jobs. Their income EXPLODES downward. Panic sets in.", "img": "people holding cardboard boxes leaving office buildings in the rain"},
            {"text": "People spend less\ncompanies LOSE more\nthe DOWNWARD SPIRAL\naccelerates", "speech": "People stop spending. Companies lose MORE money. It's a DOWNWARD SPIRAL that feeds on itself. TERRIFYING.", "img": "an empty abandoned mall with all stores closed and darkness"},
            {"text": "Everyone PANICS\nthe RED numbers\nget REDDER\nThen what?", "speech": "Everyone PANICS. The red numbers get REDDER. Looks like the end of the world. But here's what they DON'T tell you.", "img": "a glowing red downward spiral arrow crashing through a dark floor"},
            {"text": "EVERY recession\nin history ENDED\nEVERY ONE", "speech": "EVERY SINGLE recession in history ENDED. Not one lasted forever. The average? Only TEN MONTHS.", "img": "golden sunshine breaking through dark clouds after a terrible storm"},
            {"text": "10 months\nthen recovery\nrecessions are\nQUICK", "speech": "Just TEN MONTHS of pain. Then recovery EXPLODES. That's the pattern.", "img": "a timeline bar showing ten tiny red months vs 22 long green recovery months"},
            {"text": "The WORST move?\nPanic selling\nyou lock in losses\nFOREVER", "speech": "The absolute WORST move is panic selling. When you sell during a crash, you PERMANENTLY lock in your losses. FOREVER. This is SUICIDE.", "img": "a panicking trader at a computer screen slamming the sell button crying"},
            {"text": "The BEST move?\nKeep investing\nStocks are on FIRE\nSALE", "speech": "The BEST move? KEEP INVESTING. Stocks are on a FIRE SALE. You're buying GOLD at penny prices.", "img": "glowing green sale tags on stock charts showing MASSIVE discounts"},
            {"text": "Investors who are\nCOURAGEOUS during\nrecessions GET RICH\nin the recovery\nThat's facts", "speech": "Investors who have the COURAGE to keep buying during recessions are the ones who BUILD EMPIRES during recovery. This is PROVEN. DO THIS NOW.", "img": "a stock chart showing a DRAMATIC V-shaped recovery shooting upward explosively"},
        ],
        "keywords": ["Recession", "Market Crash", "Wealth Building"],
    },
    {
        "title": "4 Assets That Print Money Daily (Millionaire Strategy)",
        "slides": [
            {"text": "Rich people don't buy\nSTUFF they buy\nASSETS that PRINT\nMONEY", "speech": "Rich people don't buy stuff. They buy ASSETS that PRINT MONEY. This one difference separates the WEALTHY from BROKE.", "img": "a glowing mansion estate with rivers of golden coins flowing through it"},
            {"text": "An asset PRINTS\nmoney INTO your\npocket every month", "speech": "An asset PRINTS MONEY into your pocket every single month. That's the definition.", "img": "golden coins flowing continuously into an open wallet with green upward arrows"},
            {"text": "A liability BLEEDS\nmoney OUT of your\npocket every month", "speech": "A liability BLEEDS money OUT of your pocket. It's a WEALTH KILLER.", "img": "money bills being vacuum-sucked out of a wallet into darkness"},
            {"text": "Your fancy sports car?\nThat's a LIABILITY\nkilling you daily", "speech": "Your fancy sports car? PURE LIABILITY. Insurance BLEEDS you. Gas BLEEDS you. Maintenance BLEEDS you. Depreciation BLEEDS you.", "img": "a red sports car in a showroom with red X marks all over it"},
            {"text": "It costs you\nTHOUSANDS per month\nand it gets WEAKER\nevery year", "speech": "Thousands per month in costs while it LOSES VALUE daily. This is INSANITY.", "img": "a car dashboard showing declining value meter plummeting downward"},
            {"text": "A rental property\nwith tenants paying rent?\nThat's an ASSET that\nPRINTS MONEY", "speech": "But a rental property with tenants PAYING YOU MORE RENT than your costs? That's an ASSET that PRINTS MONEY every single month.", "img": "an apartment building with golden rent checks flowing in continuously"},
            {"text": "Dividend stocks that\nPAY YOU quarterly?\nPURE ASSET\nPURE WEALTH", "speech": "Dividend stocks that PAY YOU cash every quarter just for owning them? PURE ASSET. PURE WEALTH. Zero effort required.", "img": "a portfolio screen showing quarterly dividend payments raining down"},
            {"text": "A business that\nruns without you?\nThat's an ASSET\nthat OWNS you back", "speech": "A business that GENERATES REVENUE even while you sleep on a beach? That's an ASSET that literally OWN you back.", "img": "a laptop showing business revenue exploding while owner relaxes on paradise beach"},
            {"text": "The secret formula:\nBuy ASSETS first\nLet ASSETS pay\nfor your lifestyle", "speech": "The MILLIONAIRE SECRET: Buy assets FIRST. THEN let those assets fund your lifestyle. Reverse the order and stay broke.", "img": "a tree with golden fruit growing from investment documents on glowing roots"},
            {"text": "ASSETS before\nlifestyle\nThat's the FORMULA\nSTART TODAY with\nYour first ETF", "speech": "ASSETS BEFORE LIFESTYLE. That's the formula that creates MILLIONAIRES. Start TODAY with your first index fund. Stop buying garbage.", "img": "a person climbing golden stairs made of coins toward a bright sunrise of wealth"},
        ],
        "keywords": ["Assets", "Passive Income", "Wealth Building"],
    },
    {
        "title": "$100 → $1,745 In 30 Years (S&P 500 Magic)",
        "slides": [
            {"text": "What is the S&P 500?\nYour ULTIMATE wealth\nmachine explained", "speech": "What is the S and P five hundred? It's your ULTIMATE wealth machine. Let me show you.", "img": "Wall Street bull statue glowing gold under dramatic lighting"},
            {"text": "It's the top 500\ncompanies in America\nCOMBINED into ONE", "speech": "It's the TOP FIVE HUNDRED companies in America. All of them. Combined. Into ONE single investment.", "img": "glowing futuristic holograms of massive tech companies floating"},
            {"text": "Apple Amazon Google\nTesla Microsoft\nALL of them in\nONE place", "speech": "Apple, Amazon, Google, Tesla, Microsoft. All of them. In one single fund.", "img": "holographic logos of major companies floating in neon light"},
            {"text": "Buy ONE fund\nYou own a piece\nof ALL 500\ncompanies", "speech": "When you buy ONE fund, you instantly own a tiny piece of ALL FIVE HUNDRED companies. INSTANT DIVERSIFICATION.", "img": "a woven basket overflowing with miniature skyscrapers and coins"},
            {"text": "Average return\n10% per year\nfor OVER 100 YEARS\nNO JOKE", "speech": "Average return? TEN PERCENT per year for OVER ONE HUNDRED YEARS. This is PROVEN. This is HISTORY.", "img": "a century-long growth chart shooting upward with consistent power"},
            {"text": "Survived:\nGreat Depression\n2008 Crash\nCOVID\nEVERY single crash\nRECOVERED", "speech": "It SURVIVED the Great Depression. The 2008 financial APOCALYPSE. COVID SHUTDOWN. Every crash. And it RECOVERED stronger each time.", "img": "a phoenix rising from flames symbolizing unbreakable market resilience"},
            {"text": "Warren Buffett\nthe GREATEST investor\nSays: Just buy this\nThat's it", "speech": "Warren Buffett, the GREATEST investor alive, says most people should JUST BUY THIS fund. That's his advice. Period.", "img": "a wise elderly investor in suit pointing definitively with golden backdrop"},
            {"text": "How to BUY it?\nOpen free account\nat Fidelity Schwab\nVanguard", "speech": "Open a FREE brokerage account at Fidelity, Schwab, or Vanguard. Takes five minutes. Then buy VOO or SPY.", "img": "a smartphone showing a brokerage app with a glowing green buy button"},
            {"text": "Start with $50 or $100\nit DOES NOT matter\nJust START NOW", "speech": "Start with fifty or a hundred dollars. It doesn't matter. JUST START. Now. Today.", "img": "a single coin being placed on top of a growing stack"},
            {"text": "$100 invested today\ncould be $1,745\nin 30 years\nAUTOMATIC", "speech": "A hundred dollars TODAY could be seventeen hundred and forty five in thirty years. AUTOMATIC. Just sitting there. DOING NOTHING. START THIS WEEK.", "img": "a magical money tree with golden leaves multiplying in sunlight"},
        ],
        "keywords": ["S&P 500", "Index Fund", "Wealth Building"],
    },
    {
        "title": "You're Paying Wrong Taxes (22% vs 13% - The Bracket Secret)",
        "slides": [
            {"text": "You DON'T pay 30%\non everything\nThat's a LIE\nstop believing it", "speech": "You do NOT pay thirty percent on everything you earn. STOP BELIEVING THIS LIE. It's destroying your wealth.", "img": "a tax document with a red 30% being shattered into pieces"},
            {"text": "This myth STOPS\npeople from earning\nmore money\nIt's SABOTAGE", "speech": "This myth STOPS people from earning more money. It's financial SABOTAGE. Let me destroy this myth right now.", "img": "a shattered glass sign reading MYTH with explosive fragments flying"},
            {"text": "Taxes work in\nBRACKETS like a\nSTAIRCASE\neach step different", "speech": "Taxes work in BRACKETS, like climbing a staircase. Each step has a DIFFERENT rate.", "img": "a grand marble staircase with percentages glowing on each step"},
            {"text": "First $11,000?\nOnly 10% tax\nthat's it", "speech": "The first eleven thousand dollars you earn is ONLY taxed at ten percent. That's it.", "img": "a pile of bills marked with 10% in a clear zone"},
            {"text": "Next $34,000?\n12% tax only", "speech": "The next thirty four thousand is taxed at twelve percent. NOT thirty percent on the whole thing.", "img": "a calculator showing tax percentages with coins beside each level"},
            {"text": "$45K to $95K?\n22% tax\nONLY on THAT bracket", "speech": "Money between forty five and ninety five thousand is taxed at twenty two percent. ONLY on that bracket. Not the whole paycheck.", "img": "a layered bar chart showing different colored income brackets"},
            {"text": "Earn $50K?\nYou DON'T pay 22%\non all of it\nMATH time", "speech": "If you earn fifty thousand dollars, you DON'T pay twenty two percent on all of it. You pay TEN PERCENT on the first chunk, TWELVE on the next chunk.", "img": "money divided into color-coded portions showing different tax rates"},
            {"text": "Your real tax rate?\nAbout 13%\nnot 22%\nSee the difference?", "speech": "Your REAL tax rate is about thirteen percent total, not twenty two. See how this myth was CRUSHING your earning potential?", "img": "percentage display showing 13% in green celebrating savings"},
            {"text": "A RAISE will NEVER\nmake you lose money\nThat's MATHEMATICALLY\nimpossible", "speech": "A raise will NEVER make you lose money overall. That's MATHEMATICALLY impossible. NEVER turn down more money because of tax fear.", "img": "a person celebrating a pay raise with confetti and larger paycheck"},
            {"text": "More income ALWAYS\nmeans more money\nin your pocket\nGO EARN more NOW", "speech": "More income ALWAYS means more money in your pocket, even with taxes. GO EARN MORE. Stop letting this myth hold you back. DO THIS NOW.", "img": "upward arrows showing earnings growing while taxes take a smaller percentage"},
        ],
        "keywords": ["Taxes", "Tax Brackets", "Financial Literacy"],
    },
    {
        "title": "Debt Snowball vs Avalanche (Which Actually Works?)",
        "slides": [
            {"text": "Got suffocating debt?\nTwo PROVEN weapons\nto ANNIHILATE it", "speech": "Got debt destroying your dreams? Two PROVEN weapons to ANNIHILATE it completely.", "img": "a pile of bills on fire with red warning lights flashing"},
            {"text": "WEAPON 1:\nThe SNOWBALL\ntarget small wins", "speech": "Weapon one is the DEBT SNOWBALL. This weapon CRUSHES you mentally but WINS emotionally.", "img": "a glowing white snowball rolling downhill growing massive and unstoppable"},
            {"text": "List debts smallest\nto largest\nignore interest rates\nWIN with psychology", "speech": "List all your debts from smallest to largest. IGNORE the interest rates. Pay minimum on everything except the smallest.", "img": "a notebook with debts ranked from small to massive with checkboxes"},
            {"text": "ATTACK the smallest\nwith EVERYTHING\nget a quick WIN", "speech": "Throw EVERY EXTRA DOLLAR at that smallest debt. When it DIES, take that entire payment and ROLL IT into the next debt.", "img": "a trophy being lifted in celebration with explosive golden sparks"},
            {"text": "You get QUICK WINS\nthat CRUSH\ndefeated feeling\nmotivation grows", "speech": "WEAPON 2: The DEBT AVALANCHE. This weapon WINS on pure math and DESTROYS interest payments.","img": "a powerful avalanche crashing down a mountain with devastating force"},
            {"text": "Target HIGHEST\ninterest rate FIRST\nignore balance size", "speech": "Target the debt with the HIGHEST INTEREST RATE first. IGNORE the balance. This SAVES you the most money long-term.", "img": "a red bullseye target with arrow hitting center perfectly"},
            {"text": "You DESTROY\nthe most expensive\ndebt first\nmath wins", "speech": "You DESTROY the most expensive debt first. This saves thousands in interest. Pure mathematical DOMINATION.", "img": "a large red percentage symbol being smashed into pieces"},
            {"text": "SNOWBALL wins on\nmotivation and FEELS\nAVALANCHE wins on\nPURE MATH", "speech": "Snowball WINS on motivation when you see debts disappearing. Avalanche WINS on pure math. Both work. Pick your WEAPON.", "img": "split screen showing heart symbol versus calculator symbol competing"},
            {"text": "Pick ONE TODAY\ncommit FOREVER\nconsistency DESTROYS\nall debt", "speech": "The BEST weapon is the one you'll STICK WITH. Pick one TODAY and commit like your life depends on it. Consistency WINS.", "img": "a determined person walking a straight path toward a glowing finish line"},
            {"text": "Your debt ends SOON\nyour freedom starts\nNOW\nCHOOSE YOUR WEAPON", "speech": "Your debt ends SOON. Your freedom starts NOW. Choose your weapon, commit TODAY, and watch yourself become DEBT-FREE. GO.", "img": "a person breaking free from chains with golden light of freedom"},
        ],
        "keywords": ["Debt Payoff", "Snowball", "Avalanche"],
    },
    {
        "title": "Roth IRA: The Cheat Code Government Left Open",
        "slides": [
            {"text": "A Roth IRA is\nthe BIGGEST cheat code\nin all of finance\nSeriously", "speech": "A Roth IRA is the single BIGGEST cheat code the government left open. I'm SERIOUS. Let me show you the cheat.", "img": "a golden key unlocking a treasure chest overflowing with coins"},
            {"text": "You put in money\nYOU already paid\ntax on\nthat's it", "speech": "You put in money YOU already paid taxes on. Regular after-tax dollars from your paycheck.", "img": "a paycheck with money coming out after taxes have been taken"},
            {"text": "Then it EXPLODES\nCOMPLETELY tax FREE\nFOREVER\nno taxes ever", "speech": "Then that money EXPLODES completely TAX FREE. Forever. For the rest of your life. ZERO taxes.", "img": "a glowing green upward chart shooting into infinity with no tax brake"},
            {"text": "When you retire\nyou take OUT the\nmoney\nZERO TAX\nnothing", "speech": "When you retire and withdraw the money, you pay ZERO taxes on it. Nothing. The government gets NOTHING.", "img": "a person on a tropical beach relaxing with zero tax bills"},
            {"text": "The government\ndoesn't touch\nYOUR gains\nWINS are yours", "speech": "The government doesn't touch your gains. Every SINGLE penny of growth is YOURS. This is INSANE.", "img": "a large zero glowing gold next to massive stacks of money"},
            {"text": "Max contribution?\n$7,000 per year\nmax allowed", "speech": "You can contribute UP TO seven thousand dollars per year into this CHEAT CODE.", "img": "a glass jar filled to maximum with seven thousand dollars in cash"},
            {"text": "Start at 18\nput $7K yearly\nin index funds", "speech": "If you start at eighteen and put in seven thousand EVERY YEAR into an S and P five hundred index fund.", "img": "a young excited person opening their first investment account"},
            {"text": "By 65 you have\n$1.9 MILLION\nTAX FREE\nno taxes ever paid", "speech": "By sixty five you could have ONE POINT NINE MILLION DOLLARS. TAX FREE. Not a single penny to taxes. EVER.", "img": "stacks of gold bars and cash in a glowing vault showing 1.9M"},
            {"text": "Open at Fidelity\nSchwab or Vanguard\nit's FREE\nfive minutes", "speech": "Go to Fidelity, Schwab, or Vanguard right now. It's completely FREE. Takes five minutes. Pick an index fund.", "img": "a smartphone showing brokerage account creation glowing green"},
            {"text": "10 minutes setup\nLifetime of TAX FREE\nwealth\nEXPLODE this NOW", "speech": "Ten minutes of setup for a LIFETIME of tax-free wealth. This is INSANE. OPEN IT THIS WEEK AND START WINNING.", "img": "a clock showing ten minutes next to infinity symbol of lifetime gains"},
        ],
        "keywords": ["Roth IRA", "Tax Free", "Retirement"],
    },
    {
        "title": "Stop Timing the Market (You're Losing $100K)",
        "slides": [
            {"text": "Stop WASTING time\ntrying to time\nthe market\nNobody can", "speech": "Stop WASTING your time trying to time the stock market perfectly. Nobody can do it. Not the experts, not the TV gurus. NOBODY.", "img": "a broken clock next to a chaotic stock chart showing impossible patterns"},
            {"text": "Not hedge fund\nmanagers or TV\nanalysts or your\nuncle Bob", "speech": "Not hedge fund managers with billions of dollars. Not TV financial analysts with teams. Not your friend who SWEARS he always buys at the bottom.", "img": "a financial news studio with screens showing conflicting predictions"},
            {"text": "Instead use the\nweapon that WORKS:\ninvest same amount\nevery single month", "speech": "Instead, use the PROVEN WEAPON that actually WORKS. Invest the EXACT SAME AMOUNT every single month. Period.", "img": "a calendar with monthly investment dates marked with gold coins dropping"},
            {"text": "Market EXPLODES up?\nyou buy FEWER\nshares expensive", "speech": "When the market EXPLODES upward, your money buys FEWER shares because they're expensive. That's okay.", "img": "a rising green chart with fewer coins being collected at high prices"},
            {"text": "Market CRASHES?\nyou buy MORE\ncheaper shares\nBUY the dip", "speech": "When the market CRASHES, your money buys MORE shares because they're CHEAP. You're literally BUYING THE DIP.", "img": "a red crashing chart with many coins being scooped up at discounts"},
            {"text": "Over time your\naverage cost EVENS\nout perfectly\nmath works", "speech": "Over time, your average cost per share EVENS OUT perfectly. This strategy is called DOLLAR COST AVERAGING and it DESTROYS market timing.", "img": "a smoothed average line running through crazy volatile peaks and valleys"},
            {"text": "This removes ALL\nemotion from\ninvesting\nRobot mode ON", "speech": "This removes ALL emotion from investing. No panicking during crashes. No FOMO during rallies. You're a ROBOT. Just keep investing.", "img": "a calm zen person meditating surrounded by floating stock charts"},
            {"text": "Set auto-invest and\nliterally FORGET\nit exists\nauto-pilot", "speech": "Set up automatic monthly investing into an index fund and LITERALLY FORGET IT. Auto-pilot. No thinking required.", "img": "a phone with autopilot engaged showing automatic transfers"},
            {"text": "Check ONCE per year\nnot daily\nStudies show daily\nchecking KILLS returns", "speech": "Check your portfolio MAYBE once a year. Not daily. Studies prove investors who check daily actually EARN LESS. Psychological TORTURE.", "img": "a single calendar page circled once per year in peaceful setting"},
            {"text": "Slow steady wins\nConsistency CRUSHES\nmarket timing\nDO THIS NOW", "speech": "Slow and steady WINS the wealth race. Consistency CRUSHES market timing every single time. START THIS MONTH. DO IT.", "img": "a tortoise crossing finish line ahead of a frantic hare"},
        ],
        "keywords": ["Dollar Cost Averaging", "Investment Strategy", "Passive Income"],
    },
    {
        "title": "Banks Are STEALING $200 Billion From You",
        "slides": [
            {"text": "Banks STEAL money\nfrom you every\nsingle day\nHere's how", "speech": "Banks STEAL money from you every single day. Most people have NO IDEA. Here's exactly how they do it.", "img": "a massive grand bank building with imposing columns towering at night"},
            {"text": "You deposit $1,000\nThey pay you\n0.01% interest\nPATHETIC", "speech": "You deposit a thousand dollars. They pay you ZERO POINT ZERO ONE percent interest. That's TEN CENTS per year. PATHETIC.", "img": "a few tiny copper pennies sitting alone on a vast empty dark floor"},
            {"text": "Ten cents for\nlending them your\nmoney for FREE", "speech": "Ten cents for lending them your money. For free. Every single day.", "img": "a single dime coin sitting meaninglessly on a dark table"},
            {"text": "Then they STEAL\nYOUR money and\nlend it at 7%\nTHIEVES", "speech": "Then they STEAL your money and lend it to OTHER people at SEVEN PERCENT. They POCKET the difference. THIEVES.", "img": "a bank vault with money flowing out one door and massive profits pouring in"},
            {"text": "On top of that\nthey charge HIDDEN\nfees overdraft fees\ntheft", "speech": "On top of that, they charge overdraft fees, late payment fees, monthly maintenance fees, and DOZENS of hidden charges.", "img": "fine print document with hidden fees highlighted in red ink"},
            {"text": "American banks\nmade $200 BILLION\nin fees last year\nFROM you", "speech": "American banks made over TWO HUNDRED BILLION DOLLARS in fees last year. From regular people like you and me.", "img": "mountains of gold coins piling up inside a vault overflowing"},
            {"text": "That's MONEY you\nearned going to\nbanks for NO\nservice", "speech": "That's MONEY YOU EARNED going to BANKS for basically NO SERVICE. This has to STOP.", "img": "a raised fist silhouette against glowing background of resistance"},
            {"text": "How to FIGHT BACK?\nSwitch to online bank\n4-5% interest\nnot 0.01%", "speech": "FIGHT BACK by switching to an online bank earning FOUR TO FIVE PERCENT interest on your savings. Not zero point zero one percent.", "img": "a glowing smartphone showing high-yield savings account with big numbers"},
            {"text": "That's 400x MORE\ninterest going\ninto YOUR pocket\nnot theirs", "speech": "That's FOUR HUNDRED TIMES more interest going into YOUR POCKET. Four hundred times. Not the bank's.", "img": "money multiplying rapidly with green arrows and exploding stacks"},
            {"text": "Same FDIC protection\n400x more money\nfor YOU\nMAKE THE SWITCH\nTODAY", "speech": "Same FDIC insurance. Same safety. Way MORE money for you. MAKE THE SWITCH TODAY. Stop letting banks steal from you. DO IT NOW.", "img": "a glowing shield with FDIC protecting stacks of cash"},
        ],
        "keywords": ["Banks", "High Yield Savings", "Financial Freedom"],
    },
    {
        "title": "Renting Isn't Throwing Money Away (The TRUTH)",
        "slides": [
            {"text": "Renting is NOT\nthrowing money away\npeople are WRONG\nabout this", "speech": "Everyone says renting is throwing money away. That's COMPLETELY WRONG. Let me show you the TRUTH.", "img": "a modern luxury apartment with glass balconies lit beautifully at night"},
            {"text": "A $400K house costs\n$2,800 per month\nmortgage ONLY", "speech": "A four hundred thousand dollar house costs about twenty eight hundred a month in mortgage payments ALONE.", "img": "a beautiful suburban house with for sale sign and large price tag"},
            {"text": "But wait THAT'S\nnot the real cost\nadditional horror\ncoming", "speech": "But that's NOT the real cost. You still have ADDITIONAL costs that DESTROY the budget.", "img": "a tall stack of bills and invoices piling up on a desk"},
            {"text": "Add property taxes\ninsurance repairs\nHOA fees\nthe REAL cost", "speech": "Add property taxes, homeowners insurance, maintenance, repairs, HOA fees. Your REAL monthly cost is.", "img": "a calculator showing shockingly high total glowing red"},
            {"text": "$3,500+ per month\nnot $2,800\nthat's $700 MORE\nhidden", "speech": "THIRTY FIVE HUNDRED DOLLARS or more per month. That's SEVEN HUNDRED dollars MORE than the mortgage. Hidden costs DESTROY you.", "img": "money flowing from a house into a bank through a pipeline"},
            {"text": "PLUS in first 7 years\nmost of your payment\nis INTEREST\nnot equity", "speech": "PLUS in the first SEVEN YEARS most of your payment goes to INTEREST, not building equity. You're paying BANKS, not building WEALTH.", "img": "pie charts showing interest dominating over equity in early years"},
            {"text": "Meanwhile renting\ngives you\nFLEXIBILITY\nzero surprises", "speech": "Meanwhile renting gives you FLEXIBILITY to move for better jobs without being trapped. Zero surprise MASSIVE repair bills.", "img": "a person walking freely through an open door to a new city"},
            {"text": "Invest the\nDIFFERENCE between\nrent and ownership\nin index funds", "speech": "If rent is cheaper than owning, take the difference and INVEST IT in index funds. You might build MORE wealth as a renter.","img": "money redirected from housing costs into a growing investment chart"},
            {"text": "Only buy when\nyou'll stay 5+ years\nand the MATH\nactually works", "speech": "Only buy a house when you plan to stay at least FIVE YEARS and the NUMBERS actually work for your income.", "img": "a house key with a five-year timeline and calculator"},
            {"text": "Zero shame in\nrenting\nIt's often the SMART\nfinancial choice\nDO WHAT WORKS", "speech": "There is ZERO shame in renting. It's often the SMARTER financial choice. Do what WORKS for YOUR numbers. Not what society tells you.", "img": "a confident person standing proud in their well-decorated rental apartment"},
        ],
        "keywords": ["Renting", "Real Estate", "Financial Math"],
    },
    {
        "title": "PAY YOURSELF FIRST (The #1 Wealth Rule)",
        "slides": [
            {"text": "The #1 rule for\nbuilding wealth\nPAY YOURSELF FIRST\nno excuses", "speech": "The NUMBER ONE rule for building wealth. PAY YOURSELF FIRST. Everything else SECOND. No excuses.", "img": "a golden trophy sitting on a pedestal under dramatic spotlight"},
            {"text": "Most people do it\nWRONG\nthey pay bills FIRST", "speech": "Most people do it BACKWARDS. They pay rent, bills, groceries, eat out.", "img": "a stressed person surrounded by bills and payment envelopes"},
            {"text": "Then they TRY to\nsave WHATEVER is\nleft at month end", "speech": "Then they TRY to save whatever is LEFT at the end of the month.","img": "an empty wallet being turned upside down with nothing falling out"},
            {"text": "But there's NEVER\nanything left\nZERO\ngaps open right\nup", "speech": "But there's NEVER anything left. You know it. FLIP IT COMPLETELY.", "img": "a bank account screen showing zero balance with red empty indicator"},
            {"text": "The SECOND your\npaycheck hits\nmove 20% OUT\nimmediately", "speech": "The SECOND your paycheck hits your bank account, IMMEDIATELY move TWENTY PERCENT into savings. Non-negotiable.", "img": "a dramatic switch being flipped from off to on with electricity sparking"},
            {"text": "Set automatic\ntransfer so you\nNEVER see it", "speech": "Set up automatic transfer so you NEVER SEE IT. It's gone before you can spend it. GOLDMINE.", "img": "a phone showing automatic bank transfer moving money invisibly"},
            {"text": "After 2 weeks you'll\ncompletely forget\nit even existed", "speech": "After about two weeks you'll completely FORGET about it. Your brain adapts automatically.","img": "a robot hand slamming an automate button on a glowing panel"},
            {"text": "You adjust your\nspending WITHOUT\nfeeling it\nmagic happens", "speech": "You adjust your spending naturally without even trying. It doesn't FEEL like sacrifice. It's INVISIBLE.", "img": "a relaxed person sitting comfortably with a satisfied smile"},
            {"text": "Every single\nmillionaire does\nthis EXACT thing", "speech": "Every single MILLIONAIRE does this EXACT thing. Income doesn't matter. Fifty thousand or five hundred thousand per year.", "img": "a silhouette of wealthy person on rooftop overlooking glittering city"},
            {"text": "It's not about\nincome it's about\nthe HABIT\nBuild it NOW", "speech": "It's not about HOW MUCH you earn. It's about building the HABIT of KEEPING what you earn. START THIS WEEK. DO IT.", "img": "a chain of golden habits linking upward forming a strong wealth rope"},
        ],
        "keywords": ["Pay Yourself First", "Savings", "Wealth Building"],
    },
    {
        "title": "ETFs: The Safe Way to DOMINATE the Market",
        "slides": [
            {"text": "What is an ETF\nand why do\nALL rich people\nbuy them?", "speech": "What is an ETF and why does literally EVERY successful investor buy them?", "img": "a busy stock exchange trading floor packed with screens and activity"},
            {"text": "ETF stands for\nExchange Traded\nFund\nthat's it", "speech": "ETF stands for EXCHANGE TRADED FUND. Simple as that.", "img": "glowing letters ETF floating above a financial data dashboard"},
            {"text": "Think of it like\na basket holding\nhundreds of stocks\ninside", "speech": "Think of it like a SHOPPING BASKET holding hundreds of different stocks INSIDE.", "img": "a golden basket overflowing with miniature stock certificates"},
            {"text": "Instead of picking\nONE company\nyou own HUNDREDS\ninstantly", "speech": "Instead of picking ONE company and PRAYING it works, you own HUNDREDS at once. Instant DIVERSIFICATION.", "img": "hundreds of company logos arranged in a colorful mosaic pattern"},
            {"text": "If one company\nFAILS the other\nhundreds keep\nyou SAFE", "speech": "If ONE company completely FAILS, the other HUNDREDS keep your money SAFE. That's the POWER of diversification.", "img": "a protective shield dome covering a collection of company icons"},
            {"text": "ETFs trade like\nregular stocks\nbuy anytime sell\nanytime", "speech": "ETFs trade just like regular stocks. Buy or sell them ANYTIME during market hours. Few taps on your phone.", "img": "a hand tapping a buy button on a trading app glowing green"},
            {"text": "Fees are TINY\nusually 0.1%\nor LESS per year\nsteal them", "speech": "The FEES are incredibly TINY, usually UNDER zero point one percent per year. You're basically stealing returns.", "img": "a tiny price tag showing 0.1 percent next to enormous savings pile"},
            {"text": "Compare mutual\nfunds charging\n1-2% per year\nROBBERY", "speech": "Compare that to mutual funds charging ONE TO TWO PERCENT. That difference STEALS tens of thousands from you over time.", "img": "two scales comparing tiny fees versus massive fees in dramatic contrast"},
            {"text": "Best ETFs?\nVOO SPY QQQ\nstart with $10\nno minimum", "speech": "Best ETFs? VOO and SPY track the S and P five hundred. QQQ tracks tech companies. Start with just TEN DOLLARS.", "img": "glowing stock ticker symbols VOO SPY QQQ on futuristic display"},
            {"text": "Simplest safest\ncheapest way to\nstart investing\nDO IT TODAY", "speech": "It's the SIMPLEST, SAFEST, and CHEAPEST way to start investing. Open a free account and buy your first ETF TODAY.", "img": "a welcoming open door with warm light leading to gold coins path"},
        ],
        "keywords": ["ETF", "Index Investing", "Passive Income"],
    },
    {
        "title": "Credit Cards: WEAPON or TRAP? (You Decide)",
        "slides": [
            {"text": "How credit cards\nactually work\nmost people get\nthis WRONG", "speech": "How do credit cards ACTUALLY work? Most people get this COMPLETELY WRONG and it COSTS THEM THOUSANDS.", "img": "a shiny gold credit card floating with glowing halo in space"},
            {"text": "The bank gives you\na spending limit\nthat's YOUR max", "speech": "The bank gives you a CREDIT LIMIT. That's the maximum you can spend on that card.", "img": "a bank building with glowing approved stamp and limit number"},
            {"text": "You buy now\npay later\nhere's where it\ngets CRITICAL", "speech": "You buy things NOW and pay for them LATER. Here's where it gets CRITICAL.", "img": "a shopping cart full of items with pay later timer ticking"},
            {"text": "Pay FULL balance\nbefore due date?\nZERO interest\nFREE LOAN", "speech": "Pay the FULL balance every month before the due date? ZERO INTEREST charged. The bank gives you a FREE LOAN.", "img": "a large glowing green zero with a checkmark celebrating"},
            {"text": "Some cards give\n1-5% CASHBACK\nfree money\nRLY", "speech": "Some cards even give you ONE TO FIVE PERCENT CASHBACK or travel points. FREE MONEY on top of the free loan.", "img": "golden coins and reward points flying upward from card"},
            {"text": "But pay ONLY\nminimum amount?\nHELL starts", "speech": "But pay ONLY the minimum amount? Welcome to DEBT HELL.", "img": "a tiny minimum payment slip glowing red with warning"},
            {"text": "They charge\n20-30% interest\non everything left\nDESTRUCTION", "speech": "They charge TWENTY TO THIRTY PERCENT interest on everything that's LEFT. That's DESTRUCTION.", "img": "a massive red percentage crushing money beneath it"},
            {"text": "$1,000 balance\nat 25% interest\ncosts $250 per year\njust in interest", "speech": "A thousand dollar balance at twenty five percent costs you TWO HUNDRED FIFTY DOLLARS per year just in INTEREST. That's INSANE.", "img": "money draining through a funnel into darkness of debt"},
            {"text": "The RULE is simple\nNever spend more\nthan you can PAY\nOFF that month", "speech": "The RULE is SIMPLE. Never put something on a card unless you can PAY IT OFF IN FULL that same month. Non-negotiable.", "img": "a golden rule tablet with simple text glowing on pedestal"},
            {"text": "Use cards for\nREWARDS not for\nBORROWING\nthat's the SECRET", "speech": "Use credit cards for REWARDS and CASHBACK. Never for borrowing money you DON'T HAVE. That's the winning STRATEGY. DO THIS.", "img": "a glowing golden key unlocking a treasure chest of rewards"},
        ],
        "keywords": ["Credit Cards", "Rewards", "Debt Avoidance"],
    },
    {
        "title": "401k: Your Boss Is Handing You FREE MONEY",
        "slides": [
            {"text": "What is a 401k?\nLet me CRUSH this\nconfusion", "speech": "What is a 401k? Let me CRUSH all the confusion right now. This is CRITICAL for your wealth.", "img": "an official retirement plan document with golden 401k seal"},
            {"text": "It's a retirement\nsavings account\nthrough your JOB", "speech": "It's a RETIREMENT SAVINGS ACCOUNT that comes through your employer. That's it.", "img": "a modern corporate office with employees at desks glowing"},
            {"text": "Money comes out\nBEFORE taxes\nkey advantage", "speech": "Money comes out of your paycheck BEFORE taxes are calculated. This is a HUGE advantage.", "img": "a paycheck with money redirected before a tax gate"},
            {"text": "Earn $50K\nput in $5K?\nYou only pay tax\non $45K\nWIN", "speech": "Earn fifty thousand and put in five thousand into your 401k? You only pay tax on FORTY FIVE THOUSAND. You WIN on taxes right now.", "img": "a tax bill shrinking with a green savings checkmark"},
            {"text": "But wait\nthere's something\nEVEN BETTER\ncoming", "speech": "But wait, there's something EVEN BETTER. The best part.", "img": "confetti and sparkles bursting from a golden gift box"},
            {"text": "Many employers\nMATCH what you\ncontribute\nFREE MONEY", "speech": "Many employers MATCH what you contribute. You put in one hundred dollars, THEY PUT IN ONE HUNDRED DOLLARS.", "img": "two stacks of money side by side doubling with a match label"},
            {"text": "Your money\ninstantly DOUBLES\nFREE from your boss", "speech": "Your money INSTANTLY DOUBLES before it even starts growing. That's FREE MONEY from your BOSS.", "img": "a hundred dollar bill splitting into two identical bills with magic"},
            {"text": "It's literally free\nmoney so ALWAYS\nget the full match", "speech": "It's LITERALLY FREE MONEY so ALWAYS contribute enough to get the FULL MATCH.", "img": "a hand offering a gift box of money with free label glowing"},
            {"text": "If they match 6%\nput in AT LEAST 6%\ndon't leave money\non the table", "speech": "If they match up to six percent, ALWAYS put in at least six percent. Don't LEAVE FREE MONEY on the table.", "img": "a progress bar filling to six percent with green full match"},
            {"text": "Ignoring employer\nmatch is like your\nboss handing you\ncash and you say NO\nBE SMARTER", "speech": "Ignoring the employer match is like your BOSS handing you CASH and you saying NO THANKS. Don't be that person. DO THIS NOW.", "img": "hundred dollar bills catching fire being burned away in flames"},
        ],
        "keywords": ["401k", "Retirement", "Employer Match"],
    },
    {
        "title": "Never Lease a Car (Here's Why You'd Be INSANE)",
        "slides": [
            {"text": "Never lease a car\nit's one of the\nWORST financial\ndecisions ever", "speech": "Never lease a car. It's one of the WORST financial decisions you can EVER make. Let me show you why.", "img": "a shiny car dealership showroom with rows of new cars"},
            {"text": "A lease is just\nlong term renting\nwith CHAINS", "speech": "A lease is basically LONG TERM RENTING with CHAINS and RESTRICTIONS.", "img": "a thick lease contract being signed with chains wrapping around"},
            {"text": "$400 per month\nfor 3 years\n$14,400 GONE", "speech": "You pay about FOUR HUNDRED DOLLARS per month for THREE YEARS. That's FOURTEEN THOUSAND FOUR HUNDRED DOLLARS GONE.", "img": "calendar pages flipping with monthly bills stacking up"},
            {"text": "After 3 years\nyou own\nABSOLUTELY\nNOTHING", "speech": "And after those THREE YEARS, you own ABSOLUTELY NOTHING. Zero. Zilch. You hand the car back to the dealer.", "img": "empty hands with car keys being handed back in dark parking lot"},
            {"text": "You start OVER\nagain from zero\nthe cycle continues\ninsane", "speech": "And you start the ENTIRE PROCESS OVER AGAIN. Endless cycle. INSANE.", "img": "circular arrow loop with car going around endlessly"},
            {"text": "Plus mileage limits\n12,000 miles per year\nGo over? Pay\n25 cents per mile", "speech": "Plus there are MILEAGE LIMITS, usually twelve thousand miles per year. Go over? You pay TWENTY FIVE CENTS for EVERY extra mile.", "img": "a car odometer showing high mileage with red warning"},
            {"text": "Plus wear and tear\nfees for scratches\nand dents\nthey GET YOU", "speech": "Plus WEAR AND TEAR charges for any scratches or dings. They CRUSH you with hidden fees.", "img": "a car door with a scratch and repair bill slapped on windshield"},
            {"text": "Instead BUY a\nreliable used car\n2-3 years old\nSMART", "speech": "Smart people DO THIS: Buy a reliable USED CAR that's TWO TO THREE YEARS OLD. Someone else already took the depreciation hit.", "img": "a clean reliable used car parked on sunny street looking great"},
            {"text": "Pay it off in 3-4\nyears then drive\nit 7-10 MORE YEARS\nFREE", "speech": "Pay it off in THREE TO FOUR YEARS. Then drive it SEVEN TO TEN MORE YEARS with ZERO car payments. FREE DRIVING.", "img": "a person driving on open highway at sunset feeling free"},
            {"text": "You save $30K+\nover 10 years vs\nleasing twice\nGET RICH", "speech": "Over TEN YEARS you save THIRTY THOUSAND DOLLARS plus compared to leasing twice. That's money to INVEST and grow into WEALTH. BE SMART.", "img": "stacks of thirty thousand dollars next to growing investment chart"},
        ],
        "keywords": ["Car Lease", "Used Car", "Saving Money"],
    },
    {
        "title": "Cryptocurrency: The HIGH-RISK Wealth Game",
        "slides": [
            {"text": "What is crypto?\nSimplest explanation\nno BS", "speech": "What is cryptocurrency in the SIMPLEST terms possible? No BS.", "img": "a glowing golden bitcoin coin floating in futuristic digital space"},
            {"text": "It's digital money\nthat exists ONLY\non computers\nno bank controls it", "speech": "It's DIGITAL MONEY that exists ONLY on computers. No bank controls it. No government can print more of it.", "img": "glowing digital code streaming across computer screens"},
            {"text": "No bank owns it\nNo government\ncontrols it\nIt's YOURS", "speech": "It runs on blockchain technology, which is basically a PUBLIC RECORD everyone can see but NOBODY can cheat.", "img": "glowing blockchain network of connected nodes in neon blue"},
            {"text": "Bitcoin was first\ncreated in 2009\nby someone UNKNOWN", "speech": "Bitcoin was the FIRST cryptocurrency, created in 2009 by an ANONYMOUS person or group. UNKNOWN.", "img": "a mysterious hooded figure at computer with bitcoin glowing"},
            {"text": "Today there are\nTHOUSANDS of\ndifferent cryptos", "speech": "Today there are THOUSANDS of different cryptocurrencies competing for your money.", "img": "dozens of cryptocurrency coins scattered across dark surface"},
            {"text": "People buy hoping\nprice EXPLODES\nso they can sell\nfor huge profit", "speech": "People buy CRYPTO hoping the price EXPLODES so they can sell for HUGE PROFITS. Some have made FORTUNES.", "img": "dramatic green crypto chart shooting upward explosively"},
            {"text": "But crypto can DROP\n50% in ONE WEEK\nmost DANGEROUS\ninvestment", "speech": "But crypto can DROP FIFTY PERCENT in a SINGLE WEEK. It's the MOST VOLATILE and DANGEROUS investment available.", "img": "red crypto chart crashing dramatically with alarm indicators"},
            {"text": "RULE 1:\nNever invest more\nthan you can\nAFFORD to lose", "speech": "RULE ONE, never invest more than you can COMPLETELY AFFORD TO LOSE. If you invest a thousand, be okay with it becoming ZERO.", "img": "yellow caution triangle with risk warning glowing"},
            {"text": "RULE 2:\nBuild basics FIRST\nemergency fund\nindex funds 401k", "speech": "RULE TWO, build your FINANCIAL BASICS first. Emergency fund, index funds, 401k. Get the FOUNDATION SOLID before touching crypto.", "img": "stacked building blocks forming solid financial foundation"},
            {"text": "Crypto is DESSERT\nnot the main meal\nGet fundamentals\nright FIRST then play", "speech": "Crypto is DESSERT, not the MAIN MEAL. Get the FUNDAMENTALS RIGHT FIRST. Only then explore crypto with money you can AFFORD to lose. BE SMART.", "img": "fancy dessert plate beside a full main course dinner"},
        ],
        "keywords": ["Cryptocurrency", "Bitcoin", "High Risk"],
    },
    {
        "title": "Insurance: The PROTECTION You Can't Skip",
        "slides": [
            {"text": "How does insurance\nwork? Final simple\nexplanation ever", "speech": "How does insurance work? Here's the FINAL simple explanation ever. Pay attention.", "img": "a large protective umbrella shielding person from heavy rain"},
            {"text": "You pay small amount\nmonthly called\nPREMIUM\nthat's your bet", "speech": "You pay a small amount every month. This is called your PREMIUM. That's your bet against disaster.", "img": "small stack of coins being placed into payment slot monthly"},
            {"text": "Thousands of\npeople like you\nall pay the same\nPREMIUM", "speech": "Thousands of other people with the same insurance also pay their PREMIUMS into the same pool.", "img": "a large crowd of diverse people contributing to one point"},
            {"text": "All that money goes\ninto ONE massive\npool of power", "speech": "All of that money goes into ONE MASSIVE pool of protective power.", "img": "streams of coins flowing into one massive golden pool"},
            {"text": "When something BAD\nhappens to YOU\nthe pool PAYS", "speech": "When something BAD happens to ONE person in the group, that MASSIVE pool pays for their expenses.", "img": "safety net catching falling person with money cushioning impact"},
            {"text": "Car crash? Pool pays\nHospital? Pool pays\nHouse fire? Pool pays", "speech": "Car crash? The pool covers EVERYTHING. Hospital visit? COVERED. House fire? PAID. You're PROTECTED.", "img": "split scene showing car crash hospital and house fire all covered"},
            {"text": "You're trading small\nsure cost for\nprotection against\nHUGE disaster", "speech": "You're trading a small PREDICTABLE cost for protection against a HUGE UNPREDICTABLE disaster. SMART TRADE.", "img": "massive glowing shield dome protecting family from dangers"},
            {"text": "4 types YOU need\nhealth auto home\nlife if you have\nfamily", "speech": "The FOUR types of insurance you ACTUALLY NEED are: Health (non-negotiable), Auto (legally required), Home/Renters, and Life (if you have family).", "img": "four protective shields labeled health auto home life in row"},
            {"text": "Skip the fancy extras\njust get the 4 BASICS", "speech": "Skip all the fancy extras. Just get these FOUR BASICS. That's all you need.", "img": "simple checklist showing four essentials checked off"},
            {"text": "One major event\nwithout insurance\ncan destroy you\nfor YEARS\nDO NOT RISK IT", "speech": "One major event without insurance can PUT YOU IN DEBT FOR YEARS. It's not worth the risk. GET THE FOUR BASICS TODAY.", "img": "person overwhelmed by mountain of medical bills and debt"},
        ],
        "keywords": ["Insurance", "Protection", "Financial Security"],
    },
    {
        "title": "The Rule of 72: The ULTIMATE Math Cheat Code",
        "slides": [
            {"text": "The Rule of 72\nthe most powerful\nmath trick in\nfinance", "speech": "The Rule of SEVENTY TWO is the MOST POWERFUL math trick in all of finance. Master this NOW.", "img": "a large glowing golden number 72 floating above math equation"},
            {"text": "It shows EXACTLY\nhow fast your\nmoney DOUBLES", "speech": "It shows EXACTLY how fast your MONEY DOUBLES. That's it. That's the magic.", "img": "a stack of money splitting into two equal stacks with sparkles"},
            {"text": "Take 72 and\ndivide by your\ninterest rate\nDONE", "speech": "Take the NUMBER SEVENTY TWO and divide it by your ANNUAL INTEREST RATE. The answer is how many YEARS until your money DOUBLES.", "img": "a calculator showing 72 divided by interest rate glowing"},
            {"text": "10% stock returns?\n72/10 = 7.2 years\nto DOUBLE", "speech": "Getting TEN PERCENT returns in stocks? Seventy two divided by ten equals SEVEN POINT TWO YEARS to DOUBLE.", "img": "timeline showing seven years with money doubling at end"},
            {"text": "$10K becomes\n$20K in just\n7 years\nAUTOMATIC", "speech": "So ten thousand dollars becomes TWENTY THOUSAND in about SEVEN YEARS. Without adding a SINGLE dollar. AUTOMATIC.", "img": "ten thousand transforming into twenty thousand with magic glow"},
            {"text": "Then it doubles\nAGAIN to $40K\nthen $80K\nthen $160K", "speech": "Then it DOUBLES AGAIN to forty thousand, then eighty thousand, then ONE HUNDRED SIXTY THOUSAND.", "img": "exponential curve shooting upward steeply with money milestones"},
            {"text": "8 doublings turns\n$10K into\n$2.5 MILLION\nunbelievable", "speech": "EIGHT doublings turns ten thousand into TWO POINT FIVE MILLION DOLLARS. UNBELIEVABLE power.", "img": "vault door opening to reveal 2.5 million in stacked gold"},
            {"text": "But 1% savings\naccount? 72/1\n= 72 YEARS\nto double", "speech": "But put your money in a ONE PERCENT savings account? Seventy two divided by one equals SEVENTY TWO YEARS to double. A LIFETIME.", "img": "tiny snail crawling extremely slowly across infinite desert"},
            {"text": "WHERE you put\nyour money MATTERS\nmore than how\nMUCH you invest", "speech": "WHERE you put your money MATTERS INFINITELY MORE than HOW MUCH you put in. Choose WISELY.", "img": "dramatic crossroads with two paths one to wealth one to nothing"},
            {"text": "Start with 10%\nstock returns\ntoday\nand watch it\nCOMPOUND forever", "speech": "Put your money in stocks earning TEN PERCENT TODAY and watch it COMPOUND into MILLIONS by retirement. START THIS WEEK. DO IT.", "img": "a person watching in amazement as their wealth multiplies"},
        ],
        "keywords": ["Rule of 72", "Compound Interest", "Wealth"],
    },
    {
        "title": "Lottery Winners: Why 70% Go BROKE in 5 Years",
        "slides": [
            {"text": "Why do lottery\nwinners go BROKE?\nIt's not luck\nit's MATH", "speech": "Why do lottery winners go BROKE? It's not bad luck. It's PREDICTABLE MATH. Pattern repeats every single time.", "img": "golden lottery ticket being scratched with dramatic sparkles"},
            {"text": "70% of winners\nLOSE EVERYTHING\nin 5 years\n70%", "speech": "SEVENTY PERCENT of lottery winners LOSE EVERYTHING within FIVE YEARS. SEVENTY PERCENT. This is DOCUMENTED.", "img": "large seventy percent statistic in red with shocking exclamation"},
            {"text": "Government takes\n40% in TAXES\nright away\nGONE", "speech": "First, the GOVERNMENT TAKES FORTY PERCENT in TAXES immediately. That's the starting BLOW.", "img": "government hand taking forty percent of cash pile"},
            {"text": "Win $10 million?\nYou actually get\nabout $6 million\nHALF GONE", "speech": "Win TEN MILLION? You actually get about SIX MILLION. HALF YOUR MONEY GONE before you even SPEND it.",
            "img": "ten million dollar check shrinking to six million with cuts"},
            {"text": "Then friends and\nfamily APPEAR\npeople you haven't\nseen in YEARS", "speech": "Then suddenly, friends and family you HAVEN'T HEARD FROM IN YEARS start APPEARING begging for money.", "img": "crowd of people with outstretched hands surrounding person"},
            {"text": "They buy MASSIVE\nmansions cars\nluxury junk\nwith INSANE costs", "speech": "They buy MASSIVE MANSIONS, LUXURY CARS, and EXPENSIVE junk with INSANE ongoing maintenance costs nobody warns them about.", "img": "massive mansion with luxury sports cars parked in front"},
            {"text": "A $5M mansion?\n$50K per year\njust PROPERTY TAX\nkills them", "speech": "A FIVE MILLION DOLLAR mansion costs FIFTY THOUSAND DOLLARS per year JUST in property taxes. That KILLS them.", "img": "large property tax bill stamped on mansion backdrop"},
            {"text": "Real problem?\nNever learned\nto MANAGE money\nthat's the issue", "speech": "The REAL problem isn't the SPENDING. It's that they NEVER LEARNED how to MANAGE money. Zero education.", "img": "confused person looking at scattered financial documents"},
            {"text": "Getting money and\nKEEPING money are\ncompletely DIFFERENT\nskills", "speech": "Getting MONEY and KEEPING MONEY are COMPLETELY DIFFERENT SKILLS. Most lottery winners have NEITHER.", "img": "two separate skill icons one for earning one for managing"},
            {"text": "Financial education\nbeats luck ALWAYS\nBuild wealth SLOW\nit lasts FOREVER", "speech": "That's why FINANCIAL EDUCATION beats luck EVERY TIME. People who build wealth SLOWLY keep it FOREVER. Quick money DISAPPEARS. BE SMART. EDUCATE YOURSELF.", "img": "open book glowing with financial wisdom golden light"},
        ],
        "keywords": ["Lottery", "Financial Literacy", "Wealth Management"],
    },
    {
        "title": "Passive Income: STOP Trading Time for Money",
        "slides": [
            {"text": "What is passive\nincome? Let me\nMAKE IT CLEAR", "speech": "What is PASSIVE INCOME? Let me make this CRYSTAL CLEAR right now.", "img": "person sleeping peacefully while money flows into bank account"},
            {"text": "It's money you\nEARN without\ntrading your TIME\nfor it", "speech": "It's MONEY YOU EARN without actively TRADING YOUR TIME for it EVERY SINGLE DAY.", "img": "broken clock next to flowing cash showing time is irrelevant"},
            {"text": "Your JOB = active\nincome you stop\nworking you STARVE", "speech": "Your regular job is ACTIVE INCOME. You show up, work, get paid. Stop showing up, you STARVE. It's SLAVERY.", "img": "person working at desk in office under harsh fluorescent lights"},
            {"text": "Passive income is\nDIFFERENT it keeps\nPAYING you while you\nSLEEP forever", "speech": "PASSIVE INCOME is DIFFERENT. It keeps PAYING YOU even while you SLEEP, VACATION, RELAX. It's FREEDOM.", "img": "person relaxing on tropical beach while money notifications pop up"},
            {"text": "Dividend stocks PAY\ncash every quarter\njust for owning them\nSIMPLE", "speech": "Dividend STOCKS PAY YOU CASH every three months just for OWNING SHARES. You do NOTHING. SIMPLE.", "img": "stock portfolio showing quarterly dividend payments in green"},
            {"text": "Rental property\ntenants PAY monthly\nrent into YOUR\nwallet", "speech": "Rental PROPERTIES get tenants PAYING you MONTHLY RENT into YOUR WALLET. They pay YOUR mortgage for you.",
            "img": "apartment building with rent money flowing from windows"},
            {"text": "Online business\nearns revenue\n24/7/365 while\nyou SLEEP", "speech": "Online BUSINESSES or YOUTUBE CHANNELS earn revenue TWENTY FOUR HOURS A DAY, SEVEN DAYS A WEEK, THREE HUNDRED SIXTY FIVE DAYS A YEAR.",
            "img": "glowing laptop showing online revenue 24/7 around the clock"},
            {"text": "But TRUTH: nothing\nis passive at START\nyou must BUILD it", "speech": "But here's the TRUTH nobody tells you: Nothing is TRULY PASSIVE at the START. You must BUILD IT first.",
            "img": "person working hard laying bricks to build strong foundation"},
            {"text": "You invest time\nor money UPFRONT\nthen it PAYS you\nback FOREVER", "speech": "You invest TIME or MONEY upfront. You BUILD it. Then over TIME it PAYS YOU BACK.", "img": "seeds being planted in soil with small green shoots sprouting"},
            {"text": "Start with dividend\nETFs like SCHD\nthen level UP\nto MORE streams", "speech": "The EASIEST passive income for beginners is dividend ETFs like SCHD. Buy shares, receive quarterly cash. START THERE. Then level up. BUILD YOUR FREEDOM.", "img": "golden staircase leading upward toward wealth and freedom"},
        ],
        "keywords": ["Passive Income", "Dividends", "Financial Freedom"],
    },
    {
        "title": "Your Net Worth: The #1 Number That Matters",
        "slides": [
            {"text": "Your net worth\nis the #1 most\nimportant number\nin your finances", "speech": "Your NET WORTH is the NUMBER ONE MOST IMPORTANT number in your entire financial life. It's your COMPLETE snapshot.", "img": "glowing golden number one symbol on dark pedestal"},
            {"text": "It's your complete\nfinancial health\nin one number\nthat's it", "speech": "It's your COMPLETE FINANCIAL HEALTH in ONE SINGLE NUMBER. That tells you EVERYTHING.", "img": "medical health checkup screen showing financial vital signs"},
            {"text": "STEP 1: Add\neverything you\nOWN\nadd it up", "speech": "STEP ONE, add up EVERYTHING YOU OWN. Cash, savings, investments, house value, car value. That's your TOTAL ASSETS.",
            "img": "house car investment portfolio arranged together as assets"},
            {"text": "Cash savings\ninvestments house\ncar total value\nADD UP", "speech": "STEP TWO, subtract everything you OWE. That's your TOTAL LIABILITIES.",
            "img": "calculator adding values with golden totals appearing"},
            {"text": "STEP 2: Subtract\neverything you OWE", "speech": "Credit card debt, car loans, mortgage, student loans, ANYTHING you owe anyone.",
            "img": "red debt numbers being subtracted with minus symbol glowing"},
            {"text": "Credit cards\ncar loans\nmortgage\nstudent loans\nALL of it", "speech": "Assets minus LIABILITIES equals your NET WORTH. Simple formula.",
            "img": "subtraction equation in bold with result highlighted gold"},
            {"text": "Assets minus\nLiabilities\nequals NET WORTH\nDONE", "speech": "If your number is NEGATIVE right now, do NOT PANIC. You're not alone.",
            "img": "clean formula on chalkboard with dramatic chalk writing"},
            {"text": "Negative? You're\nNOT alone\nmost people start\nNEGATIVE", "speech": "MOST PEOPLE in their TWENTIES and THIRTIES have negative net worth because of student loans. COMPLETELY NORMAL.",
            "img": "calm person meditating with peaceful blue aura"},
            {"text": "Track it EVERY\nmonth on a\nspreadsheet\nDON'T quit", "speech": "The KEY is to TRACK THIS NUMBER EVERY SINGLE MONTH. Write it down on a spreadsheet. Make it REAL.",
            "img": "laptop showing monthly net worth tracking spreadsheet"},
            {"text": "Your only GOAL?\nMake it HIGHER\nthan last month\nEVERY MONTH", "speech": "Your ONLY GOAL is to make it HIGHER than last month. EVERY SINGLE MONTH. Pay debt, save, invest. That's how you BUILD REAL WEALTH. START NOW.", "img": "green upward arrow climbing higher each month on chart"},
        ],
        "keywords": ["Net Worth", "Financial Health", "Wealth Tracking"],
    },
    {
        "title": "Bear vs Bull: How to DOMINATE Market Swings",
        "slides": [
            {"text": "Bear market vs\nBull market\nwhich CRUSHES", "speech": "BEAR MARKET versus BULL MARKET. Which one CRUSHES? Let me explain this DEFINITIVELY.",
            "img": "bear and bull statue facing off on Wall Street in gold"},
            {"text": "BULL market =\nstocks EXPLODING\nUP for months", "speech": "A BULL MARKET means stocks have been EXPLODING UP consistently for months or YEARS. Everyone BUYING, prices CLIMBING.",
            "img": "powerful bull charging forward with green upward arrows"},
            {"text": "Everyone buys\nprices climb\npeople CELEBRATE", "speech": "People feel OPTIMISTIC and CONFIDENT. They're WINNING.",
            "img": "happy investors celebrating with confetti and green charts"},
            {"text": "BEAR market =\nstocks CRASH\n20% or more", "speech": "A BEAR MARKET is the OPPOSITE. Stocks have CRASHED down TWENTY PERCENT or more from recent highs.",
            "img": "fierce growling bear with red crashing stock charts"},
            {"text": "Fear EXPLODES\npeople panic sell\nprices CRASH harder", "speech": "FEAR EXPLODES, people PANIC SELL everything, prices CRASH even HARDER. CHAOS.",
            "img": "panicked traders at screens with red numbers cascading"},
            {"text": "BUT here's the\nSECRET: Bear markets\nare OPPORTUNITIES\nin disguise", "speech": "BUT here's the SECRET that separates RICH from POOR: Bear markets are OPPORTUNITIES in disguise. The same companies are on FIRE SALE.",
            "img": "diamond hidden inside rough rock revealed with gold light"},
            {"text": "Stocks are on\nSALE you buy\nquality cheap", "speech": "Since NINETEEN TWENTY EIGHT, EVERY SINGLE BEAR MARKET eventually ENDED and was followed by a NEW BULL MARKET. EVERY ONE.",
            "img": "shopping bags with stock tickers showing massive discounts"},
            {"text": "Since 1928 EVERY\nbear market ENDED\nrecovery ALWAYS\nfollowed", "speech": "The average BEAR MARKET only lasts about NINE MONTHS. The average BULL MARKET lasts TWO POINT SEVEN YEARS.",
            "img": "historical chart showing every crash recovered with green"},
            {"text": "9 months RED\n2.7 YEARS GREEN\nthe good times WIN", "speech": "The GOOD TIMES last THREE TIMES LONGER than the bad times. That's HISTORICAL FACT.",
            "img": "timeline bar showing short red months vs long green years"},
            {"text": "Be greedy when\nothers FEAR\nWarren Buffett\nrule #1\nDO THIS", "speech": "Warren BUFFETT's NUMBER ONE RULE: Be GREEDY when others are FEARFUL. When everyone PANICS, that's when SMART investors are BUYING LIKE CRAZY. DO THIS.", "img": "brave lone investor standing confident while others run afraid"},
        ],
        "keywords": ["Bear Market", "Bull Market", "Investing"],
    },
    {
        "title": "Inflation: The Silent Wealth KILLER",
        "slides": [
            {"text": "What is inflation?\nIt KILLS your wealth\nevery single day", "speech": "What is INFLATION? It KILLS your WEALTH every single day whether you realize it or NOT.",
            "img": "rising red price arrows floating upward from store items"},
            {"text": "Inflation means\nprices RISE\nover time\nsteadily", "speech": "INFLATION means prices go UP over time. Constantly. Relentlessly.",
            "img": "grocery store aisle with glowing red price tags rising"},
            {"text": "Milk cost $1.50\nin 2000\nToday $4.50\ntriple", "speech": "A gallon of milk cost about ONE DOLLAR FIFTY in two thousand. Today that SAME GALLON costs FOUR DOLLARS FIFTY. TRIPLE THE PRICE.",
            "img": "milk gallon on shelf with old and new price tags"},
            {"text": "Same milk\n3x the price\nyour dollar buys\nLESS", "speech": "SAME MILK. THREE TIMES THE PRICE. Your dollar literally BUYS LESS stuff EVERY YEAR.",
            "img": "shrinking dollar bill getting smaller and weaker"},
            {"text": "Average inflation\nabout 3% per year\nthis DESTROYS you", "speech": "Average INFLATION is about THREE PERCENT per year. Here's why this DESTROYS YOUR WEALTH.",
            "img": "three percent number on rising chart with yearly markers"},
            {"text": "Your salary doesn't\ngrow 3%?\nYou get a PAY CUT\nevery year", "speech": "If your SALARY doesn't grow by AT LEAST THREE PERCENT every year, you're getting a PAY CUT. Period.",
            "img": "flat salary line being overtaken by rising cost line"},
            {"text": "Even if paycheck\nstays same\nit buys LESS\nthan last year", "speech": "Even if your PAYCHECK stays the SAME NUMBER, it buys LESS STUFF than it did LAST YEAR. That's a PAY CUT.",
            "img": "paycheck staying same while shopping bags get smaller"},
            {"text": "Savings at 0.01%\ngets CRUSHED\nby 3% inflation", "speech": "A REGULAR SAVINGS ACCOUNT paying ZERO POINT ZERO ONE PERCENT does ABSOLUTELY NOTHING against THREE PERCENT INFLATION. You LOSE.",
            "img": "tiny 0.01 percent being crushed by massive 3 percent wave"},
            {"text": "Stocks at 10%\nBEAT inflation\nyou grow REAL wealth", "speech": "STOCKS averaging TEN PERCENT per year DO BEAT INFLATION. After inflation, you're STILL GAINING SEVEN PERCENT in real PURCHASING POWER.",
            "img": "ten percent investment arrow soaring above three percent"},
            {"text": "Saving keeps money\nSAFE investing\nmakes it GROW\nBoth needed NOW", "speech": "SAVING keeps your money SAFE. INVESTING makes it ACTUALLY GROW over time. You need BOTH. START INVESTING TODAY before inflation kills more of your wealth.", "img": "strong arm holding shield protecting growing money stack"},
        ],
        "keywords": ["Inflation", "Purchasing Power", "Investing"],
    },
    {
        "title": "Your Pay Stub: Understand Where Your Money GOES",
        "slides": [
            {"text": "Can you actually\nread your pay stub?\nMost people CAN'T", "speech": "Can you actually READ your pay stub? MOST PEOPLE just see the deposit and IGNORE everything else. That's IGNORANCE.",
            "img": "detailed pay stub document on desk with sections highlighted"},
            {"text": "GROSS PAY\nis what you EARNED\nbefore taxes", "speech": "GROSS PAY is what you EARNED before ANYTHING gets taken out. It's the BIG NUMBER.",
            "img": "large glowing salary number at top of pay stub"},
            {"text": "That's the big\nnumber at top\nthen deductions\nhappen", "speech": "Then come the DEDUCTIONS. This is where your money VANISHES.",
            "img": "money vanishing through multiple deduction lines"},
            {"text": "Federal income tax\nState tax\nSocial Security\nMedicare\nall gone", "speech": "FEDERAL INCOME TAX takes its percentage. STATE TAX takes its cut if your state has one. SOCIAL SECURITY takes six point two percent. MEDICARE takes one point four five percent.",
            "img": "scissors cutting portions from paycheck labeled taxes"},
            {"text": "All MANDATORY\nno choice\nthey TAKE it", "speech": "All of those are MANDATORY. You don't get a CHOICE. They TAKE IT.",
            "img": "official government stamps for Social Security Medicare"},
            {"text": "Health insurance\nand 401k come\nout too if you\nhave them setup", "speech": "Then your HEALTH INSURANCE PREMIUM and 401K CONTRIBUTIONS come out if you have them set up.",
            "img": "health insurance card and 401k form next to amounts"},
            {"text": "After EVERY\ndeduction\nyou get NET PAY", "speech": "After ALL of those deductions, you're LEFT with your NET PAY. That's your ACTUAL TAKE HOME MONEY.",
            "img": "final net pay amount glowing green at bottom"},
            {"text": "That's your actual\ntake home\nwhat hits your\nbank account", "speech": "The amount that HITS your bank account. That's real money in YOUR POCKET.",
            "img": "phone notification showing direct deposit landing"},
            {"text": "Gross = earned\nNet = kept\ntwo different\nnumbers", "speech": "Easy way to remember it. GROSS is what you EARN. NET is what you KEEP. Two COMPLETELY different numbers.",
            "img": "two columns comparing big gross versus smaller net"},
            {"text": "Check monthly\nfor mistakes\nerrors cost YOU", "speech": "Check your pay stub AT LEAST ONCE A MONTH. Payroll mistakes happen MORE often than you think. Always in the company's favor. STAY ALERT.", "img": "magnifying glass carefully examining pay stub for errors"},
        ],
        "keywords": ["Pay Stub", "Payroll", "Take Home Pay"],
    },
    {
        "title": "Good Debt vs Bad Debt: The TRUTH",
        "slides": [
            {"text": "Not all debt is bad\nsome debt makes\nyou RICHER", "speech": "Not all debt is CREATED EQUAL. Some debt actually makes you RICHER over time. Some DESTROYS you. Know the DIFFERENCE.",
            "img": "balance scale with green good debt vs red bad debt"},
            {"text": "GOOD debt helps\nyou EARN more\nor build wealth", "speech": "GOOD DEBT helps you EARN MORE MONEY or BUILD WEALTH. It's an INVESTMENT.",
            "img": "growing green investment tree with money blossoming"},
            {"text": "Student loans for\nhigh paying career?\nGOOD debt\nif smart", "speech": "Student loans for a HIGH-PAYING career? That's GOOD DEBT if you choose your degree WISELY and actually GRADUATE earning BIG money.",
            "img": "graduation cap tossed with bright successful future"},
            {"text": "Mortgage on\nproperty that\ngrows value?\nGOOD debt", "speech": "A MORTGAGE on a property that APPRECIATES IN VALUE? GOOD DEBT. You're building EQUITY while living there.",
            "img": "house with rising green value arrow showing growth"},
            {"text": "Business loan\nthat generates\nmore than it\ncosts? GOOD debt", "speech": "A BUSINESS LOAN that generates MORE REVENUE than the INTEREST costs? GOOD DEBT. You're using borrowed money to make MORE MONEY.",
            "img": "thriving business storefront with revenue flowing in"},
            {"text": "BAD debt buys\nstuff that LOSES\nvalue and bleeds\ninterest", "speech": "BAD DEBT is the OPPOSITE. It buys things that LOSE VALUE immediately and CHARGES you INTEREST.",
            "img": "shopping bags and impulse purchases fading away"},
            {"text": "Credit cards on\nclothes and eating\nout?\nBAD debt", "speech": "Credit card debt from SHOPPING SPREES and EATING OUT? PURE BAD DEBT. You're BLEEDING MONEY.",
            "img": "pile of credit card bills stacking next to empty bags"},
            {"text": "Car loan on luxury\ncar you can't\nafford? BAD debt", "speech": "A car loan on a BRAND NEW LUXURY CAR you can't AFFORD? BAD DEBT. That car LOSES TWENTY PERCENT the SECOND you drive off.",
            "img": "brand new car driving off lot with value dropping"},
            {"text": "Before debt ask:\nWill this make\nme RICHER or\nPOORER in 5 years?", "speech": "Before taking on ANY DEBT, ask yourself: WILL THIS DEBT MAKE ME RICHER OR POORER IN FIVE YEARS? Be HONEST.",
            "img": "person at crossroads thinking with richer and poorer paths"},
            {"text": "Use debt as TOOL\nto build wealth\nnever trap that\nkeeps you broke", "speech": "Use DEBT as a TOOL to BUILD WEALTH. Never as a TRAP that keeps you BROKE FOREVER. CHOOSE WISELY.", "img": "golden wrench tool building staircase of wealth upward"},
        ],
        "keywords": ["Good Debt", "Bad Debt", "Borrowing Wisely"],
    },
    {
        "title": "Side Hustle Math: Turn $0 Into $1000/Month (6 Ideas)",
        "slides": [
            {"text": "6 side hustles\nthat PAY you\nreal money\nSTART TODAY", "speech": "Six side hustles that PAY REAL MONEY. Not get-rich schemes. Not crypto nonsense. Real income you can start THIS WEEK.", "img": "six icons representing different income streams glowing"},
            {"text": "Freelance writing\n$500-2000\nper month\nzero startup", "speech": "Freelance writing for blogs and websites. Five hundred to two thousand dollars monthly. ZERO startup cost. Start TODAY.", "img": "laptop screen with article being written in gold light"},
            {"text": "Virtual assistant\n$600-1500\nmonth managing\nbusiness tasks", "speech": "Virtual assistant work. Organize calendars, emails, projects. Six hundred to fifteen hundred monthly.", "img": "organized digital workspace with calendar and tasks"},
            {"text": "Tutoring online\n$20-50 per hour\npick your schedule", "speech": "Online tutoring. Twenty to fifty dollars per hour. Set your own schedule. Work whenever you want.", "img": "student and teacher in virtual learning session"},
            {"text": "Sell digital products\nTemplates guides courses\n$1000+ passive", "speech": "Sell digital products. Templates, guides, courses. Thousand plus PASSIVE income monthly. Build ONCE, sell FOREVER.", "img": "digital products icons like templates and courses"},
            {"text": "Dropshipping products\n$800-2000 monthly\nlet others handle shipping", "speech": "Dropshipping. Eight hundred to two thousand monthly. You just market, they handle shipping.", "img": "packages being shipped with profit flowing in"},
            {"text": "Social media management\n$400-1200 per client\nzero experience needed", "speech": "Manage social media for small businesses. Four hundred to twelve hundred PER CLIENT. Zero experience needed.", "img": "colorful social media posts being managed"},
            {"text": "The real secret?\nPick ONE. Go deep.\nMastery beats variety", "speech": "The real secret? Pick ONE side hustle. Go DEEP. Become EXPERT. Mastery beats jumping around.", "img": "arrow going straight up showing focused growth"},
            {"text": "90 days of\nserious work\n$1000 monthly\nGUARANTEED", "speech": "Ninety days of serious focused work? One thousand monthly GUARANTEED. This isn't theoretical. This WORKS.", "img": "ninety day calendar with money growing"},
            {"text": "Extra $1000/month\n= $12K yearly\n= Life changing\nmoney", "speech": "One thousand monthly side income. Twelve thousand yearly. That changes your LIFE. Start THIS WEEK. Pick ONE.", "img": "celebration with wealth growing showing success"},
        ],
        "keywords": ["Side Hustle", "Extra Income", "Make Money"],
    },
    {
        "title": "The Roth IRA Hack (Free Money From Government)",
        "slides": [
            {"text": "The government\nwill give you\nFREE MONEY\nfor retirement", "speech": "The government will literally PAY YOU FREE MONEY to invest in your retirement. Most people don't know this exists.", "img": "government building with money flowing out golden"},
            {"text": "It's called\nRoth IRA\nTax free FOREVER", "speech": "It's called the ROTH IRA. Invest money TODAY, pay taxes TODAY, then NEVER PAY TAXES AGAIN on the growth. EVER.", "img": "retirement account growing tax-free with green arrows"},
            {"text": "You can withdraw\nmoney anytime\nno penalties\nno rules", "speech": "You can withdraw your money anytime. No penalties. No age restrictions. Complete FREEDOM.", "img": "atm machine dispensing money freely"},
            {"text": "$7000 per year\nmaximum contribution\ntax free growth\nFOREVER", "speech": "Contribute up to seven thousand dollars per year. Watch it grow TAX FREE for 30 YEARS. Seven thousand becomes FIFTY THOUSAND.", "img": "seven thousand dollars transforming into wealth"},
            {"text": "Your $7K becomes\n$50K in 30 years\nThat's AUTOMATIC", "speech": "Seven thousand today becomes fifty thousand in thirty years. You didn't do ANYTHING. It just grows. This is MAGIC.", "img": "money multiplying in piggy bank over decades"},
            {"text": "Even better?\nYour employer\nmight MATCH\nyour contributions", "speech": "EVEN BETTER. Some employers MATCH your contributions. Free money. Literally free.", "img": "employer doubling employee contribution with match"},
            {"text": "How to start?\nFidelity Vanguard\nSchwab 5 minutes", "speech": "Open an account at Fidelity, Vanguard, or Schwab. Five minutes. Start with fifty bucks.", "img": "phone opening brokerage account with green checkmark"},
            {"text": "Buy VOO or VTI\nset and forget\nlet compound\ndo the work", "speech": "Buy VOO or VTI. Set and FORGET. Compound interest does the heavy lifting.", "img": "index fund symbols glowing with passive growth"},
            {"text": "People who START\nat 25 vs 35\nWin FIVE HUNDRED\nTHOUSAND more", "speech": "Someone who starts at twenty five versus thirty five? They win FIVE HUNDRED THOUSAND MORE by retirement. TEN YEARS of delay costs half a million.", "img": "two paths diverging with one path to wealth"},
            {"text": "Don't regret this\nSTART TODAY\nfuture you\nwill thank you", "speech": "Don't regret this in twenty years. START TODAY. Your future self will WORSHIP YOU for this decision. DO THIS NOW.", "img": "older person celebrating financial security at retirement"},
        ],
        "keywords": ["Roth IRA", "Retirement", "Tax Free"],
    },
    {
        "title": "Real Estate Secrets (Start With $0)",
        "slides": [
            {"text": "You don't need\nmoney to get\ninto real estate\nThat's a myth", "speech": "You don't need money to start in real estate. THAT'S A LIE. Here's the REAL way to get started.", "img": "house key glowing with opportunity energy"},
            {"text": "Strategy 1:\nFind deals nobody\nelse sees and\nSELL them", "speech": "Strategy ONE. WHOLESALING. Find deals nobody else sees. Get them under contract. Sell them to investors for PROFIT. Zero money needed.", "img": "house deal contract being signed"},
            {"text": "You're the middleman\n$5K-$20K profit\nper deal\nno money needed", "speech": "You're the MIDDLEMAN. Find the deal. Sell it to investor. Take FIVE to TWENTY THOUSAND per deal. ZERO of your own money needed.", "img": "middleman profiting from deal connection"},
            {"text": "Strategy 2:\nFIRST time buyer\nFHA loans\n3.5% down", "speech": "Strategy TWO. FHA LOANS. Buy your first property with only THREE POINT FIVE PERCENT down. Live in it. Rent out rooms. Cover your mortgage.", "img": "first time home buyer with low down payment"},
            {"text": "Your roommates\nPAY your mortgage\nwhile you build\nequity", "speech": "Your roommates PAY YOUR MORTGAGE while you BUILD EQUITY. You literally live for FREE and get RICHER.", "img": "roommates paying rent that covers mortgage"},
            {"text": "Strategy 3:\nLook for deals\nSELLERS are desperate\nto offload", "speech": "Strategy THREE. Find DISTRESSED sellers. Divorced. Bankrupt. Inherited a house they don't want. BUY LOW.", "img": "distressed property with opportunity arrows"},
            {"text": "You negotiate\nlow price\nfix it up\nSELL or rent", "speech": "Negotiate a KILLER price. Fix it up cheap. Either SELL it or RENT IT OUT for PROFIT. Real wealth building.", "img": "property transformation from broken to beautiful"},
            {"text": "Start small\none property\nuse equity to\nbuy second", "speech": "Start small. ONE property. Build EQUITY. Use that equity to BUY PROPERTY TWO with LEVERAGE. Repeat.", "img": "property portfolio growing with each purchase"},
            {"text": "Real estate \nmakes millionaires\nfaster than stocks\nproven", "speech": "Real estate makes MILLIONAIRES FASTER than stocks. It's PROVEN. Leverage plus appreciation equals WEALTH EXPLOSION.", "img": "real estate empire stacking higher"},
            {"text": "Start THIS MONTH\nLook at 10 properties\nmake 1 offer\nYour wealth journey\nSTARTS", "speech": "Start THIS MONTH. Look at properties. Make offers. Your real estate wealth journey STARTS NOW. This works.", "img": "for sale sign with stars representing opportunity"},
        ],
        "keywords": ["Real Estate", "Property", "Wealth Building"],
    },
    {
        "title": "Why Your Boss Doesn't Want You to Know This (Career Hacks)",
        "slides": [
            {"text": "Your boss doesn't want\nyou to know\nthese salary\nTRUTHS", "speech": "Your boss DOESN'T WANT YOU to know these salary truths. They profit when you don't know your VALUE.", "img": "boss protecting money with secret gesture"},
            {"text": "TRUTH 1: You can\nNEGOTIATE salary\neverything is\nnegotiable", "speech": "TRUTH ONE. Salary is NEGOTIABLE. EVERYTHING is negotiable. Your boss expects it.", "img": "negotiation handshake with money on table"},
            {"text": "Most people accept\nfirst offer\nthey're leaving\nTHOUSANDS on table", "speech": "Most people accept the FIRST OFFER. They leave THOUSANDS on the table. Insane.", "img": "money falling from table untouched"},
            {"text": "TRUTH 2: Job hopping\ngets you 10-20%\nraise\nstaying loses money", "speech": "TRUTH TWO. Job hopping. Moving companies gives you TEN TO TWENTY PERCENT raises. Staying costs you MONEY.", "img": "career ladder with big jumps upward"},
            {"text": "Companies budget\n5% raises\nleaving gets you\n15% immediately", "speech": "Companies budget FIVE PERCENT raises. Switching jobs? FIFTEEN PERCENT immediately. The math is BRUTAL.", "img": "salary comparison showing job change advantage"},
            {"text": "TRUTH 3: Remote work\nincreases your\nmarket value\n2x easily", "speech": "TRUTH THREE. Remote work OPENS your job market globally. You can earn in US dollars from ANYWHERE.", "img": "laptop from tropical location earning global salary"},
            {"text": "Your geographic\nmax salary just\nbecame global\nmax salary", "speech": "Your salary ceiling just EXPLODED. You're no longer competing with fifty people in your city. Compete with THOUSANDS.", "img": "global world map with connection lines"},
            {"text": "TRUTH 4: Your network\nis worth $100K+\nin lifetime earnings", "speech": "TRUTH FOUR. Your network is worth ONE HUNDRED THOUSAND PLUS in lifetime earnings. Build GENUINE relationships.", "img": "network of connected people glowing"},
            {"text": "Most people get\ntheir best jobs\nthrough connections\nnot job boards", "speech": "Most people get their BEST JOBS through referrals, not LinkedIn. Build real relationships in your industry.", "img": "person getting referred to dream job"},
            {"text": "Invest in PEOPLE\nthey become your\nwealth network\nfor LIFE", "speech": "Invest in PEOPLE. They become your wealth network for LIFE. This is how you GET RICH. Build your network NOW.", "img": "strong relationships building personal wealth empire"},
        ],
        "keywords": ["Career", "Salary", "Negotiation"],
    },
    {
        "title": "Passive Income Streams (7 Ways Money Works While You Sleep)",
        "slides": [
            {"text": "7 passive income\nstreams that make\nmoney 24/7\nwhile you sleep", "speech": "SEVEN passive income streams that make MONEY WHILE YOU SLEEP. Build them ONCE. Profit FOREVER.", "img": "money flowing in continuously while person sleeps"},
            {"text": "Stream 1: Dividend\nstocks pay you\nquarterly\n$100 becomes\n$200 yearly", "speech": "Dividend stocks. One hundred dollars buys stock that pays you money quarterly. Your money makes money.", "img": "stock certificate with dividend checks"},
            {"text": "Stream 2: Rental\nproperty tenants\npay you monthly\n$2000 profit\nafter expenses", "speech": "Rental property. Tenants PAY YOU monthly. After expenses? Two thousand profit. PASSIVE.", "img": "apartment building with rent checks flowing in"},
            {"text": "Stream 3: High yield\nsavings account\n4.5% interest\nmonthly deposits", "speech": "High yield savings. Put money in. Get FOUR POINT FIVE PERCENT interest annually. ZERO EFFORT.", "img": "savings account growing with interest"},
            {"text": "Stream 4: Affiliate\nmarketing recommend\nproducts earn\ncommission", "speech": "Affiliate marketing. Recommend products. Earn COMMISSION on every sale. PASSIVE sales.", "img": "links generating commissions automatically"},
            {"text": "Stream 5: Create\ncourse once\nsell it 1000 times\n$50K revenue", "speech": "Create a course ONCE. Sell it 1000 times. Fifty thousand in PASSIVE revenue. Do it once in 2024, earn in 2025 and 2026.", "img": "course being purchased repeatedly"},
            {"text": "Stream 6: Vending\nmachine business\nput machines out\ncollect money", "speech": "Vending machines. Put them in locations. Collect money PASSIVELY. Build a network. Build WEALTH.", "img": "vending machine dispensing products and profit"},
            {"text": "Stream 7: Peer\nlending invest\nin other people\nearn interest", "speech": "Peer lending. Invest in loans. Earn INTEREST. Your money funds others while GROWING.", "img": "money lending chain creating passive returns"},
            {"text": "The goal: Build\n$10K monthly\npassive income\nThen you're FREE", "speech": "BUILD ten thousand MONTHLY in PASSIVE income. Then you're FREE. No more working for money. Money works for YOU.", "img": "person free from work celebrating financial independence"},
            {"text": "Start ONE stream\nthis month\ncompound them\nyear by year\nyou WIN", "speech": "Start ONE stream this month. Build it. Add another next month. Year by year COMPOUND them. Eventually you're RICH. DO THIS NOW.", "img": "passive income streams compounding into wealth"},
        ],
        "keywords": ["Passive Income", "Dividends", "Financial Freedom"],
    },
]


LONG_FORM_TOPICS = [
    {
        "title": "How to Build Wealth From ZERO - Complete Money Blueprint",
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
        "title": "The Psychology of Money - Why Smart People Stay Broke",
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
        "title": "Stock Market for Complete Beginners - Your First $1000 Investment",
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
        "title": "Side Hustles That Actually Pay - From $0 to $5000/Month",
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
        "title": "Retirement Planning - How to Retire Early and Never Work Again",
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
        "title": "Real Estate Investing for Beginners - Your First Property Guide",
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
]


def enhance_image(img_path):
    """Upscale, sharpen, and enhance a downloaded AI image to HD quality"""
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        img = Image.open(img_path).convert("RGB")
        w, h = img.size
        if w >= 1080 and h >= 1920:
            return
        img = img.resize((1080, 1920), Image.LANCZOS)
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Color(img).enhance(1.1)
        img.save(img_path, "JPEG", quality=92)
    except Exception as e:
        print(f"  [WARN] Image enhance failed: {e}")


def _extract_search_keywords(desc, text=""):
    """Pull 2-4 search-friendly keywords from img + text context."""
    stop = {'a', 'an', 'the', 'of', 'on', 'in', 'at', 'to', 'and', 'or',
            'with', 'its', 'from', 'into', 'for', 'by', 'is', 'are', 'was',
            'being', 'their', 'that', 'this', 'no', 'not', 'showing',
            'looking', 'getting', 'labeled', 'versus', 'vs', 'next',
            'glowing', 'dramatic', 'golden', 'massive', 'tiny', 'large',
            'behind', 'beside', 'above', 'below', 'under', 'over',
            'dark', 'bright', 'single', 'each', 'every', 'slowly',
            'against', 'through', 'between', 'along', 'across', 'displayed',
            'floating', 'shooting', 'being', 'showing'}

    # Extract nouns from both desc and text
    words = (desc + ' ' + text.lower()).replace(',', ' ').split()
    good = [w for w in words if w not in stop and len(w) > 2 and w.isalpha()]

    # Deduplicate while preserving order
    seen = set()
    result = []
    for w in good:
        if w not in seen:
            seen.add(w)
            result.append(w)

    return ' '.join(result[:3]) if result else 'finance money'


def fetch_hd_images(slides, save_dir):
    """Fetch sharp HD images from Pexels (primary) with Pollinations fallback."""
    os.makedirs(save_dir, exist_ok=True)
    images = []
    headers = {"Authorization": PEXELS_API_KEY} if PEXELS_API_KEY else {}

    for i, slide in enumerate(slides):
        img_path = os.path.join(save_dir, f"slide_{i}.jpg")

        if os.path.exists(img_path) and os.path.getsize(img_path) > 50000:
            images.append(img_path)
            continue

        desc = slide.get('img', 'finance money')
        text = slide.get('text', '')
        query = _extract_search_keywords(desc, text)
        got = False

        if PEXELS_API_KEY:
            try:
                purl = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&orientation=portrait&per_page=15"
                resp = requests.get(purl, headers=headers, timeout=15)
                if resp.status_code == 200:
                    photos = resp.json().get("photos", [])
                    if photos:
                        photo = photos[i % len(photos)]
                        img_url = photo["src"].get("large2x") or photo["src"].get("portrait") or photo["src"]["large"]
                        img_resp = requests.get(img_url, timeout=20)
                        if img_resp.status_code == 200 and len(img_resp.content) > 20000:
                            with open(img_path, 'wb') as f:
                                f.write(img_resp.content)
                            images.append(img_path)
                            print(f"  [HD] Slide {i+1}: {query}")
                            got = True
            except Exception as e:
                print(f"  [WARN] Pexels failed slide {i+1}: {e}")

        if not got:
            style = "cinematic photorealistic, sharp focus, dramatic lighting, no text no watermark"
            prompt = f"{style}, {desc}"
            encoded = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&nologo=true&seed={i + 42}&model=flux&enhance=true"
            try:
                resp = requests.get(url, timeout=90)
                if resp.status_code == 200 and len(resp.content) > 5000:
                    with open(img_path, 'wb') as f:
                        f.write(resp.content)
                    enhance_image(img_path)
                    images.append(img_path)
                    print(f"  [AI] Slide {i+1}: {query} (fallback)")
                    got = True
            except Exception as e:
                print(f"  [WARN] AI gen failed slide {i+1}: {e}")

        if not got:
            images.append(None)

    return images


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
    ("en-US-GuyNeural", "+20%", "-5Hz"),
    ("en-US-ChristopherNeural", "+20%", "-4Hz"),
    ("en-GB-RyanNeural", "+20%", "-5Hz"),
]


def create_slide_audios(slides, work_dir):
    """Generate audio for each slide's speech separately, measure exact duration per slide"""
    os.makedirs(work_dir, exist_ok=True)

    try:
        import edge_tts
    except ImportError:
        print("[ERR] edge-tts not installed")
        return None

    working_voice = None
    for voice, rate, pitch in VOICE_LIST:
        test_path = os.path.join(work_dir, "test_voice.mp3")
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

    audio_paths = []
    durations = []

    for idx, slide in enumerate(slides):
        audio_path = os.path.join(work_dir, f"speech_{idx}.mp3")
        voice, rate, pitch = working_voice
        if not _run_edge_tts(slide['speech'], audio_path, voice, rate, pitch):
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
    cmd = [
        FFMPEG, '-y',
        '-f', 'lavfi', '-i',
        f'anoisesrc=d={duration}:c=pink:r=44100:a=0.015',
        '-af', 'lowpass=f=300,highpass=f=80,volume=0.4',
        '-c:a', 'aac', '-b:a', '64k',
        output_path
    ]
    proc = subprocess.run(cmd, capture_output=True, timeout=30)
    return proc.returncode == 0 and os.path.exists(output_path)


def get_audio_duration(audio_path):
    cmd = [FFMPEG, '-i', audio_path, '-f', 'null', '-']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = proc.communicate()
    output = stderr.decode('utf-8', errors='replace')
    for line in output.split('\n'):
        if 'Duration' in line:
            time_str = line.split('Duration:')[1].split(',')[0].strip()
            parts = time_str.split(':')
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 4


def prep_slides(images, slides, durations, work_dir):
    """Prepare slides: full image + text overlay at bottom (white text with black outline)."""
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

    W, H = 720, 1280
    font_big = get_font(48)
    font_med = get_font(40)
    font_brand = get_font(24)
    font_cta = get_font(36)

    for idx, slide in enumerate(slides):
        img_src = images[idx] if idx < len(images) else None
        out = os.path.join(work_dir, f"s_{idx}.jpg")

        if img_src and os.path.exists(img_src):
            bg = Image.open(img_src).convert("RGB")
            iw, ih = bg.size
            ratio = max(W / iw, H / ih)
            bg = bg.resize((int(iw * ratio), int(ih * ratio)), Image.LANCZOS)
            left = (bg.width - W) // 2
            top = (bg.height - H) // 2
            bg = bg.crop((left, top, left + W, top + H))
        else:
            bg = Image.new("RGB", (W, H), (10, 10, 46))

        draw = ImageDraw.Draw(bg)

        brand = "THE AI DOLLAR"
        bb = draw.textbbox((0, 0), brand, font=font_brand)
        bw = bb[2] - bb[0]
        bx = (W - bw) // 2
        for ox in range(-2, 3):
            for oy in range(-2, 3):
                if abs(ox) + abs(oy) > 0:
                    draw.text((bx + ox, 30 + oy), brand, font=font_brand, fill=(0, 0, 0))
        draw.text((bx, 30), brand, font=font_brand, fill=(255, 215, 0))

        text = slide['text'].upper()
        lines = text.split('\n')

        line_h = 90
        total_h = len(lines) * line_h
        start_y = H - total_h - 120

        for li, line in enumerate(lines):
            font = font_big if li == 0 else font_med
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            y = start_y + li * line_h

            for ox in range(-4, 5):
                for oy in range(-4, 5):
                    if abs(ox) + abs(oy) > 0:
                        draw.text((x + ox, y + oy), line, font=font, fill=(0, 0, 0))

            color = (255, 255, 255) if li == 0 else (255, 255, 100)
            draw.text((x, y), line, font=font, fill=color)

        is_last = (idx == len(slides) - 1)
        if is_last:
            cta = "SUBSCRIBE FOR MORE"
            cb = draw.textbbox((0, 0), cta, font=font_cta)
            cw = cb[2] - cb[0]
            ch = cb[3] - cb[1]
            cx = (W - cw) // 2
            cy = 80
            draw.rounded_rectangle(
                [cx - 20, cy - 10, cx + cw + 20, cy + ch + 10],
                radius=12, fill=(255, 0, 0)
            )
            draw.text((cx, cy), cta, font=font_cta, fill=(255, 255, 255))

        bg.save(out, "JPEG", quality=95)
        del draw, bg
        gc.collect()
        print(f"  slide {idx+1}/{len(slides)} ready")


def create_video_ffmpeg(slides, images, audio_file, durations, output_file):
    valid_images = [img for img in images if img is not None]
    if not valid_images:
        return create_video_simple(slides, audio_file, durations, output_file)

    work_dir = output_file + "_work"
    print("[BUILD] Preparing slides...")
    prep_slides(images, slides, durations, work_dir)

    n = len(slides)
    audio_duration = get_audio_duration(audio_file)

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
            '[0:v]scale=720:1280,fps=24[v];[2:a]volume=0.12[bg];[1:a][bg]amix=inputs=2:duration=first[aout]',
            '-map', '[v]', '-map', '[aout]',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-c:a', 'aac', '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            output_file
        ]
    else:
        cmd = [
            FFMPEG, '-y',
            '-f', 'concat', '-safe', '0', '-i', concat_file,
            '-i', audio_file,
            '-vf', 'scale=720:1280,fps=24',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-c:a', 'aac', '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            output_file
        ]

    proc = subprocess.run(cmd, capture_output=True, timeout=180)

    import shutil
    shutil.rmtree(work_dir, ignore_errors=True)

    if proc.returncode != 0:
        stderr = proc.stderr.decode('utf-8', errors='replace')[-500:]
        print(f"[WARN] FFmpeg failed: {stderr}")
        return create_video_simple(slides, audio_file, durations, output_file)

    print("[OK] Video created!")
    return True


def create_video_simple(slides, audio_file, durations, output_file):
    """Fallback: solid color background with audio, no text."""
    total_dur = sum(durations)
    cmd = [
        FFMPEG, '-y',
        '-f', 'lavfi', '-i', f'color=c=0x0A0A2E:size=720x1280:rate=24:d={total_dur:.2f}',
        '-i', audio_file,
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_file
    ]
    print("[BUILD] Running FFmpeg (simple mode)...")
    proc = subprocess.run(cmd, capture_output=True, timeout=240)
    if proc.returncode != 0:
        return False
    print("[OK] Video created (simple mode)")
    return True


def _get_next_topic_index():
    counter_file = "topic_counter.txt"
    try:
        if os.path.exists(counter_file):
            with open(counter_file) as f:
                idx = int(f.read().strip())
        else:
            idx = 0
    except Exception:
        idx = 0
    next_idx = (idx + 1) % len(CONTENT_TOPICS)
    with open(counter_file, "w") as f:
        f.write(str(next_idx))
    return idx


def generate_daily_video():
    index = _get_next_topic_index()
    topic = CONTENT_TOPICS[index]
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


def generate_long_video():
    counter_file = "long_topic_counter.txt"
    try:
        if os.path.exists(counter_file):
            with open(counter_file) as f:
                idx = int(f.read().strip())
        else:
            idx = 0
    except Exception:
        idx = 0

    topic = LONG_FORM_TOPICS[idx % len(LONG_FORM_TOPICS)]
    next_idx = (idx + 1) % len(LONG_FORM_TOPICS)
    with open(counter_file, "w") as f:
        f.write(str(next_idx))

    slides = topic['slides']
    os.makedirs(CONFIG['output_dir'], exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"{CONFIG['output_dir']}/the_ai_dollar_long_{timestamp}.mp4"
    audio_dir = f"{CONFIG['output_dir']}/audio_long_{timestamp}"
    img_dir = f"{CONFIG['output_dir']}/imgs_long_{timestamp}"

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

        print("[IMG] Fetching HD images (long-form)...")
        images = fetch_hd_images(slides, img_dir)
        print(f"[OK] Got {sum(1 for i in images if i)} images")

        print("[VIDEO] Creating long-form video...")
        ok = create_video_ffmpeg(slides, images, audio_file, durations, output_file)

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
            "is_long": True
        }

    except Exception as e:
        print(f"[ERR] Long video error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
