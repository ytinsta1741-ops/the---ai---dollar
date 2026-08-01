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
        "title": "Your Money Is Dying Right Now",
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
        "title": "Turn Your Coffee Money Into A Million",
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
        "title": "Bad Credit DESTROYS Your Wealth",
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
        "title": "The 50/30/20 Rule DESTROYS Poverty",
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
        "title": "Stocks vs Bonds: The POWER Comparison",
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
        "title": "No Emergency Fund? You're ONE Crisis Away",
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
        "title": "Recessions DESTROY Weak Investors (But BUILD Rich Ones)",
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
        "title": "RICH People Buy Assets That PRINT MONEY",
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
        "title": "The S&P 500 Is Your ULTIMATE Wealth Machine",
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
        "title": "Taxes DESTROYED You (Until Now)",
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
        "title": "ANNIHILATE Your Debt with These Two Weapons",
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
    ("en-US-DavisNeural", "+20%", "-6Hz"),
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

    W, H = 864, 1536
    font_big = get_font(56)
    font_med = get_font(48)

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

        bg.save(out, "JPEG", quality=95)
        del draw, bg
        gc.collect()
        print(f"  slide {idx+1}/{len(slides)} ready")


def create_video_ffmpeg(slides, images, audio_file, durations, output_file):
    valid_images = [img for img in images if img is not None]
    if not valid_images:
        return create_video_simple(slides, audio_file, durations, output_file)

    work_dir = output_file + "_work"
    print("[BUILD] Preparing slides with text + zoom...")
    prep_slides(images, slides, durations, work_dir)

    FPS = 30
    FADE_DUR = 0.5
    n = len(slides)

    print("[BUILD] Creating zoom clips...")
    clip_paths = []
    for idx in range(n):
        clip_path = os.path.join(work_dir, f"clip_{idx}.mp4")
        dur = durations[idx]
        total_frames = int(dur * FPS)
        if total_frames < 2:
            total_frames = 2

        if idx % 2 == 0:
            zexpr = "min(zoom+0.0003,1.08)"
        else:
            zexpr = "if(eq(on\\,0)\\,1.08\\,max(zoom-0.0003\\,1.0))"

        cmd = [
            FFMPEG, '-y',
            '-loop', '1', '-i', os.path.join(work_dir, f"s_{idx}.jpg"),
            '-vf', f"zoompan=z='{zexpr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={total_frames}:s=720x1280:fps={FPS}",
            '-t', f"{dur:.2f}",
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '26',
            '-pix_fmt', 'yuv420p',
            clip_path
        ]
        proc = subprocess.run(cmd, capture_output=True, timeout=30)
        if proc.returncode != 0:
            cmd_simple = [
                FFMPEG, '-y',
                '-loop', '1', '-i', os.path.join(work_dir, f"s_{idx}.jpg"),
                '-vf', 'scale=720:1280',
                '-t', f"{dur:.2f}", '-r', str(FPS),
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '26',
                '-pix_fmt', 'yuv420p',
                clip_path
            ]
            subprocess.run(cmd_simple, capture_output=True, timeout=30)

        clip_paths.append(clip_path)

    print("[BUILD] Joining clips with crossfade...")
    if n == 1:
        import shutil as _sh
        _sh.copy2(clip_paths[0], os.path.join(work_dir, "joined.mp4"))
    else:
        inputs = []
        for cp in clip_paths:
            inputs.extend(['-i', cp])

        fc_parts = []
        offset = durations[0] - FADE_DUR
        prev = "[0:v]"
        for i in range(1, n):
            out_label = f"[v{i}]"
            fc_parts.append(
                f"{prev}[{i}:v]xfade=transition=fade:duration={FADE_DUR}:offset={max(0, offset):.2f}{out_label}"
            )
            prev = out_label
            if i < n - 1:
                offset += durations[i] - FADE_DUR

        filter_complex = ";".join(fc_parts)
        joined_path = os.path.join(work_dir, "joined.mp4")
        cmd = [FFMPEG, '-y'] + inputs + [
            '-filter_complex', filter_complex,
            '-map', prev,
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '26',
            '-pix_fmt', 'yuv420p',
            joined_path
        ]
        proc = subprocess.run(cmd, capture_output=True, timeout=120)
        if proc.returncode != 0:
            concat_file = os.path.join(work_dir, "concat.txt")
            with open(concat_file, 'w') as f:
                for cp in clip_paths:
                    f.write(f"file '{os.path.basename(cp)}'\n")
            cmd = [
                FFMPEG, '-y',
                '-f', 'concat', '-safe', '0', '-i', concat_file,
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '26',
                '-pix_fmt', 'yuv420p',
                joined_path
            ]
            subprocess.run(cmd, capture_output=True, timeout=60)

    joined_path = os.path.join(work_dir, "joined.mp4")
    audio_duration = get_audio_duration(audio_file)

    print("[BUILD] Mixing voiceover + background music...")
    bg_music_path = os.path.join(work_dir, "bgmusic.m4a")
    has_music = generate_bg_music(bg_music_path, audio_duration + 2)

    if has_music:
        cmd = [
            FFMPEG, '-y',
            '-i', joined_path,
            '-i', audio_file,
            '-i', bg_music_path,
            '-filter_complex',
            '[2:a]volume=0.12[bg];[1:a][bg]amix=inputs=2:duration=first[aout]',
            '-map', '0:v', '-map', '[aout]',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '128k',
            '-shortest',
            output_file
        ]
    else:
        cmd = [
            FFMPEG, '-y',
            '-i', joined_path,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '128k',
            '-shortest',
            output_file
        ]

    proc = subprocess.run(cmd, capture_output=True, timeout=60)

    import shutil
    shutil.rmtree(work_dir, ignore_errors=True)

    if proc.returncode != 0:
        return create_video_simple(slides, audio_file, durations, output_file)

    print("[OK] Video created with zoom + crossfade + music!")
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
