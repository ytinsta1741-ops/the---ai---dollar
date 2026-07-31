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
        "title": "Your $100 Is Now Worth $93",
        "slides": [
            {"text": "Your $100\nis now worth $93", "speech": "Your hundred dollars is now worth ninety three bucks. Let that sink in.", "img": "a crisp hundred dollar bill slowly dissolving into dust on a dark surface"},
            {"text": "Prices went up\n7% this year", "speech": "Prices went up seven percent this year but your cash stayed the exact same.", "img": "grocery store shelf with glowing red price tags showing rising numbers"},
            {"text": "Your cash\nstayed the same", "speech": "That's seven dollars gone just for doing absolutely nothing.", "img": "an open empty leather wallet under a single spotlight in darkness"},
            {"text": "Thats $7 gone\nfor doing nothing", "speech": "And this happens every single year.", "img": "paper money catching fire with orange flames against a black background"},
            {"text": "Cash under your\nmattress loses\nvalue every day", "speech": "Keeping cash under your mattress or in a regular savings account means you are literally losing money every single day.", "img": "cash bills hidden under a white mattress in a dim bedroom"},
            {"text": "So what actually\nbeats inflation?", "speech": "So what actually beats inflation? The answer is investing.", "img": "a glowing golden question mark floating above a pile of coins"},
            {"text": "Investing in\nstocks and\nindex funds", "speech": "Specifically stocks and index funds. The S and P five hundred tracks the top five hundred American companies.", "img": "a futuristic stock trading screen with green charts and neon data"},
            {"text": "The S&P 500 averages\n10% per year\nInflation is only 3%", "speech": "It averages about ten percent per year. Inflation is usually around three percent. Your money grows faster than prices rise.", "img": "a dramatic green upward chart line breaking through clouds into sunlight"},
            {"text": "Your money grows\nfaster than\nprices rise", "speech": "That's how you beat the system. Saving protects your money but investing is what actually grows it.", "img": "a tiny seedling growing from a pile of gold coins with light beams"},
            {"text": "Saving protects\nyour money\nInvesting grows it\nYou need both", "speech": "You need both working together. Start as early as you can, even with small amounts, because time is your biggest advantage.", "img": "a golden piggy bank next to a growing stack of coins with sparkles"},
        ],
        "keywords": ["Inflation", "Finance", "Money", "Investing"],
    },
    {
        "title": "How $5 a Day Makes You a Millionaire",
        "slides": [
            {"text": "$5 a day\ncan make you\na millionaire", "speech": "Five dollars a day can literally make you a millionaire. And that's not some motivational nonsense, that's actual math.", "img": "towering stack of gold coins reaching into clouds with dramatic lighting"},
            {"text": "Thats your\nmorning coffee", "speech": "Five dollars is your morning coffee.", "img": "a steaming latte on a cafe table with a five dollar bill beside it"},
            {"text": "Invest $5 daily\nat 10% returns", "speech": "If you invest five dollars every single day into an index fund that averages ten percent returns per year.", "img": "a smartphone showing a green investment chart with coins dropping in"},
            {"text": "After 10 years\n$30,727", "speech": "After ten years you'd have over thirty thousand dollars.", "img": "a growing mountain of cash bills stacking higher and higher"},
            {"text": "After 30 years\n$339,073", "speech": "After thirty years, three hundred thirty nine thousand.", "img": "a luxurious penthouse view overlooking a glittering city skyline at night"},
            {"text": "After 40 years\n$1,062,000", "speech": "And after forty years, over one million dollars. From just five bucks a day.", "img": "a vault door opening to reveal stacks of gold bars and cash"},
            {"text": "The secret?\nCompound interest", "speech": "The secret behind this is compound interest. Your money earns returns, and then those returns earn their own returns.", "img": "an exponential curve chart glowing green shooting upward dramatically"},
            {"text": "Your interest\nearns its own\ninterest", "speech": "It snowballs. It starts slow, but after twenty years it explodes. The curve goes almost straight up.", "img": "a giant glowing snowball rolling downhill getting bigger and bigger"},
            {"text": "It snowballs\nbigger and bigger\nover time", "speech": "Here's the part that should scare you though. Every single day you wait to start costs you thousands of dollars in the long run.", "img": "a large hourglass with golden sand running out in dramatic red light"},
            {"text": "Every day you wait\ncosts you thousands\nStart today", "speech": "A twenty year old who invests five dollars a day will have three times more money at retirement than a thirty year old doing the exact same thing. Start today.", "img": "a confident young person standing on top of a mountain at sunrise"},
        ],
        "keywords": ["Compound Interest", "Investing", "Millionaire"],
    },
    {
        "title": "Bad Credit Costs You $100,000",
        "slides": [
            {"text": "Bad credit\ncosts you\n$100,000", "speech": "Bad credit doesn't just hurt your pride. It costs you real money. We're talking a hundred thousand dollars or more over your lifetime.", "img": "a credit score meter in the red zone glowing ominously on a dark screen"},
            {"text": "On a $300K\nmortgage", "speech": "Here's exactly how. When you apply for a three hundred thousand dollar mortgage.", "img": "a beautiful suburban house with a sold sign in the front yard at dusk"},
            {"text": "Score above 740\nyou pay 6.5%", "speech": "A credit score above seven forty gets you six point five percent interest.", "img": "a glowing green checkmark with a high credit score number above it"},
            {"text": "Score below 580\nyou pay 9.5%", "speech": "But a score below five eighty? You're looking at nine point five percent or higher.", "img": "a flashing red warning triangle with an exclamation mark in darkness"},
            {"text": "Thats $100,000\nextra in interest\nover 30 years", "speech": "Over thirty years, that three percent difference adds up to over a hundred thousand dollars in extra interest. Same house, way more money.", "img": "hundred dollar bills being swept away by wind into a dark void"},
            {"text": "How to fix it?\n3 simple rules", "speech": "So how do you fix your credit? Three simple rules.", "img": "a glowing checklist with three items on a clipboard in blue light"},
            {"text": "Rule 1\nAlways pay\non time even\nthe minimum", "speech": "Rule one, always pay on time, even if it's just the minimum payment. Payment history is thirty five percent of your score.", "img": "a calendar page with a payment due date circled in red marker"},
            {"text": "Rule 2\nKeep balances\nbelow 30% of\nyour limit", "speech": "Rule two, keep your credit card balances below thirty percent of your limit. If your limit is a thousand, never carry more than three hundred.", "img": "a credit card with a low balance meter bar showing green safe zone"},
            {"text": "Rule 3\nNever close\nyour oldest card\nit helps history", "speech": "Rule three, never close your oldest credit card. The length of your credit history matters.", "img": "a vintage worn credit card on a leather surface with a timeline behind it"},
            {"text": "Your credit score\nis your financial\nreputation\nProtect it", "speech": "Your credit score is your financial reputation. It follows you everywhere. Protect it like your life depends on it, because financially, it does.", "img": "a glowing golden shield protecting a stack of coins from danger"},
        ],
        "keywords": ["Credit Score", "Finance", "Mortgage", "Money"],
    },
    {
        "title": "The 50/30/20 Rule Changed My Life",
        "slides": [
            {"text": "This budget rule\nchanged my life", "speech": "This budget rule literally changed my entire financial life and it can change yours too.", "img": "an open budget planner notebook on a clean desk with a golden pen"},
            {"text": "Take your\npaycheck\nany amount works", "speech": "Take your paycheck, any amount works, it doesn't matter how much you make.", "img": "a paycheck envelope being opened with cash visible inside"},
            {"text": "50% goes to needs\nrent food bills\ntransportation", "speech": "Fifty percent goes to needs. That's rent, food, bills, and transportation. The stuff you have to pay no matter what.", "img": "a modern apartment building exterior at sunset with warm window lights"},
            {"text": "30% goes to wants\nfun shopping\neating out", "speech": "Thirty percent goes to wants. Fun stuff, shopping, eating out, entertainment. Yes you're allowed to enjoy your money.", "img": "colorful shopping bags and gift boxes on a table with warm lighting"},
            {"text": "20% goes straight\nto savings\nand investing", "speech": "And twenty percent goes straight to savings and investing.", "img": "a glass jar overflowing with gold coins next to a growing green plant"},
            {"text": "The key?\nPay savings FIRST\nnot last", "speech": "Here's the key though. Pay your savings first, not last. The second your paycheck hits your account, move twenty percent into savings automatically.", "img": "a smartphone screen showing an automated bank transfer in progress"},
            {"text": "Automate it\nthe day you\nget paid", "speech": "Set it up so you never even see that money.", "img": "a robotic hand pressing a button labeled automate on a glowing screen"},
            {"text": "You will adjust\nto spending less\nwithin one month", "speech": "You will adjust to spending less within about one month, I promise. It feels tight at first but then it becomes completely normal.", "img": "a peaceful person sitting comfortably on a couch looking relaxed and content"},
            {"text": "Most millionaires\nstarted with\nthis exact rule", "speech": "Most millionaires didn't get rich with complicated strategies. They started with this exact simple rule.", "img": "a silhouette of a successful person overlooking a city skyline at dusk"},
            {"text": "No fancy apps needed\nJust 3 numbers\n50 30 20", "speech": "No fancy budgeting apps needed. Just three numbers. Fifty. Thirty. Twenty. That's the entire system.", "img": "three glowing golden numbers 50 30 20 floating in a dark space"},
        ],
        "keywords": ["Budgeting", "50/30/20", "Personal Finance"],
    },
    {
        "title": "Stocks vs Bonds Explained",
        "slides": [
            {"text": "Stocks vs Bonds\nfinally explained", "speech": "Stocks versus bonds, finally explained so anyone can understand.", "img": "the Wall Street bull statue in golden light with stock ticker data"},
            {"text": "A stock means\nyou OWN a piece\nof a company", "speech": "When you buy a stock, you own a tiny piece of a real company. If that company grows, your investment grows too.", "img": "a gleaming corporate skyscraper reflecting sunset light from below"},
            {"text": "If it grows\nyour money grows\nIf it tanks you lose", "speech": "But if it tanks, you lose money.", "img": "a dramatic roller coaster track with sharp peaks and valleys at night"},
            {"text": "Stocks average\n10% per year\nbut its a bumpy ride", "speech": "Stocks have averaged about ten percent per year historically, but it's a bumpy ride with lots of ups and downs.", "img": "a volatile zigzag stock chart line glowing neon green on dark background"},
            {"text": "A bond means\nyou LEND money\nto a government\nor company", "speech": "A bond is completely different. When you buy a bond, you're lending money to a government or a company. They promise to pay you back with interest.", "img": "a grand government treasury building with classical columns at dusk"},
            {"text": "They pay you\nback with interest\nsteady and safe", "speech": "It's steady and predictable.", "img": "a calm turquoise ocean at sunset with golden sky and peaceful waves"},
            {"text": "Bonds average\n4-5% per year\nmuch smoother ride", "speech": "Bonds average about four to five percent per year, much smoother than stocks but lower returns.", "img": "a smooth straight road stretching into the horizon through open plains"},
            {"text": "Best strategy?\nMix both", "speech": "So what's the best strategy? Mix both.", "img": "a golden balance scale with coins on both sides perfectly balanced"},
            {"text": "Young? 80% stocks\n20% bonds\nYou have time\nto recover", "speech": "If you're young, go about eighty percent stocks and twenty percent bonds. You have decades to recover from any crashes.", "img": "a young confident investor looking at rising charts on multiple screens"},
            {"text": "Older? Flip it\nMore bonds\nfor stability", "speech": "As you get older, flip it. More bonds for stability since you'll need that money sooner. This is called asset allocation.", "img": "a retired couple relaxing on a porch overlooking a beautiful garden"},
        ],
        "keywords": ["Stocks", "Bonds", "Investing", "Asset Allocation"],
    },
    {
        "title": "No Emergency Fund? Heres Why You Need One",
        "slides": [
            {"text": "No emergency fund?\nHeres what happens", "speech": "No emergency fund? Let me show you exactly what happens.", "img": "a glowing red emergency alarm light flashing in a dark corridor"},
            {"text": "Your car\nbreaks down\n$800 repair", "speech": "Your car breaks down tomorrow. Eight hundred dollar repair bill.", "img": "a car with its hood open and smoke rising in a dark parking lot"},
            {"text": "No savings?\nCredit card at\n24% interest", "speech": "Without any savings, that goes straight onto a credit card at twenty four percent interest.", "img": "a credit card being swiped with red danger sparks flying from it"},
            {"text": "That $800\njust became $1,100", "speech": "That eight hundred dollar problem just became eleven hundred dollars by the time you pay it off. And that's just one emergency.", "img": "a calculator showing growing numbers with stacks of bills being consumed"},
            {"text": "An emergency fund\nprevents this\ncompletely", "speech": "An emergency fund prevents this completely. It's your financial safety net.", "img": "a strong safety net catching falling coins against a dramatic sky"},
            {"text": "Save 3 to 6 months\nof expenses", "speech": "The goal is to save three to six months of your living expenses.", "img": "six calendar pages fanned out with golden coins stacked on each"},
            {"text": "Put it in a high\nyield savings account\n4-5% interest", "speech": "Put it in a high yield savings account where it earns four to five percent interest. Your money earns money while it protects you.", "img": "a smartphone showing a savings account with a growing green interest bar"},
            {"text": "Your money earns\nmoney while it\nprotects you", "speech": "You don't need to build it overnight.", "img": "a small green plant sprouting from a pile of coins with golden light"},
            {"text": "Start with just $500\nthen add $50\nevery paycheck", "speech": "Start with just five hundred dollars. Then add fifty dollars from every single paycheck.", "img": "coins being stacked one by one into a tall growing tower"},
            {"text": "In one year youll\nhave a real\nsafety net", "speech": "In about one year you'll have a solid safety net that can handle any emergency without destroying your finances. The peace of mind alone is worth it.", "img": "a person sitting peacefully on a park bench with a sunset behind them"},
        ],
        "keywords": ["Emergency Fund", "Savings", "High Yield Savings"],
    },
    {
        "title": "What Happens in a Recession",
        "slides": [
            {"text": "A recession\nis coming\nheres what happens", "speech": "A recession might be coming. Here's exactly what happens and what you should do.", "img": "massive dark storm clouds rolling over a city skyline with lightning"},
            {"text": "Companies make\nless money\nand start cutting", "speech": "Companies start making less money, so they cut costs. That means layoffs.", "img": "a dark empty corporate office with abandoned desks and dim lights"},
            {"text": "They lay off\nworkers to\nsave money", "speech": "Workers lose their jobs, so they have less income and spend less.", "img": "a person holding a cardboard box leaving an office building at night"},
            {"text": "People spend less\nbecause they have\nless income", "speech": "When people spend less, companies make even less money. It's a downward cycle that feeds on itself.", "img": "an empty abandoned shopping mall with closed stores and dark lighting"},
            {"text": "Which means companies\nmake even less\nThe cycle repeats", "speech": "Sounds scary, right? But here's what nobody tells you during a recession.", "img": "a glowing red downward spiral arrow against a dark stormy background"},
            {"text": "But every single\nrecession in history\nhas ended", "speech": "Every single recession in history has ended. Every one. The average recession only lasts about ten months.", "img": "a brilliant golden sunrise breaking through dark storm clouds over water"},
            {"text": "The average recession\nlasts 10 months\nnot forever", "speech": "Not years, not decades, ten months.", "img": "a short timeline bar showing ten months highlighted against a long scale"},
            {"text": "The worst move\nis panic selling\nyou lock in losses", "speech": "The absolute worst move you can make is panic selling your investments. When you sell during a crash, you lock in your losses permanently.", "img": "a panicking person at a computer with red stock charts crashing"},
            {"text": "The best move\nis keep investing\nStocks are on sale", "speech": "The best move is to keep investing consistently. Stocks are literally on sale during a recession. You're buying the same companies at a discount.", "img": "a glowing green sale tag on a stock chart with discount prices"},
            {"text": "Those who invest\nduring recessions\nget rich in\nthe recovery", "speech": "Those who have the courage to keep investing during recessions are the ones who get wealthy during the recovery. History proves this over and over again.", "img": "a stock chart showing a dramatic V-shaped recovery shooting upward green"},
        ],
        "keywords": ["Recession", "Economy", "Bear Market", "Investing"],
    },
    {
        "title": "Rich People Buy Assets Not Stuff",
        "slides": [
            {"text": "Rich people buy\nassets not stuff", "speech": "Rich people don't buy stuff. They buy assets. And that one difference is what separates the wealthy from everyone else.", "img": "an aerial view of a luxurious mansion estate with manicured gardens"},
            {"text": "An asset puts\nmoney IN\nyour pocket", "speech": "Here's the distinction. An asset puts money into your pocket.", "img": "golden coins flowing into an open wallet with a green glowing arrow up"},
            {"text": "A liability takes\nmoney OUT\nof your pocket", "speech": "A liability takes money out of your pocket.", "img": "money bills flying out of a wallet into darkness with red arrow down"},
            {"text": "Your fancy car?\nThats a liability", "speech": "Your fancy car? That's a liability. Insurance, gas, maintenance, depreciation. It costs you money every single month.", "img": "a sleek red sports car in a showroom with a price tag dangling"},
            {"text": "Insurance gas\ndepreciation\nit costs you\nevery month", "speech": "And it's worth less every year.", "img": "a car dashboard with a declining value meter and money symbols fading"},
            {"text": "A rental property\nthat earns income?\nThats an asset", "speech": "But a rental property that brings in more rent than it costs you? That's an asset.", "img": "a modern apartment building with glowing windows and rent checks flowing in"},
            {"text": "Dividend stocks\nthat pay you\nevery quarter?\nAsset", "speech": "Dividend stocks that pay you cash every three months just for holding them? That's an asset.", "img": "a stock portfolio screen showing dividend payments with green cash icons"},
            {"text": "A business that\nruns without you?\nAsset", "speech": "A business that generates income even when you're not working? That's an asset.", "img": "a laptop showing business revenue growing while owner relaxes on a beach"},
            {"text": "Buy assets first\nthen let assets\npay for your stuff", "speech": "The secret of wealthy people is simple. They buy assets first. Then they let those assets generate income to pay for their lifestyle.", "img": "a tree with golden fruit growing from a pile of investment documents"},
            {"text": "Thats the\nmillionaire formula\nAssets before\nlifestyle", "speech": "Assets before lifestyle. That's the millionaire formula. Start small. Buy your first index fund. Let your money work harder than you do.", "img": "a person standing at the top of stairs made of golden coins at sunrise"},
        ],
        "keywords": ["Assets", "Liabilities", "Wealth Building"],
    },
    {
        "title": "What Is the S&P 500",
        "slides": [
            {"text": "What is the\nS&P 500?", "speech": "What is the S and P five hundred and why does everyone keep talking about it?", "img": "the iconic Wall Street street sign in New York City with buildings"},
            {"text": "Its the top 500\ncompanies in\nAmerica combined", "speech": "It's the top five hundred companies in America combined into one single investment.", "img": "a dramatic city skyline of corporate skyscrapers lit up at night"},
            {"text": "Apple Google\nAmazon Tesla\nMicrosoft all in one", "speech": "Apple, Google, Amazon, Tesla, Microsoft, all of them in one place.", "img": "glowing futuristic holographic icons of major tech companies floating"},
            {"text": "You buy 1 fund\nyou own a piece\nof all 500", "speech": "When you buy one S and P five hundred fund, you instantly own a tiny piece of all five hundred companies.", "img": "a woven basket overflowing with miniature company buildings and coins"},
            {"text": "Average return\n10% per year\nfor over 100 years", "speech": "The average return has been about ten percent per year for over a hundred years.", "img": "a long-term growth chart spanning decades showing steady upward climb"},
            {"text": "It survived\nthe Great Depression\n2008 crash and Covid", "speech": "It has survived the Great Depression, the two thousand eight financial crisis, and the Covid crash. Every single time it recovered.", "img": "a phoenix rising from flames symbolizing market recovery and resilience"},
            {"text": "Warren Buffett says\nmost people should\njust buy this", "speech": "Even Warren Buffett, the greatest investor alive, says most people should just buy an S and P five hundred index fund.", "img": "a wise elderly investor in a suit gesturing wisely with golden backdrop"},
            {"text": "How? Open a\nbrokerage account\nbuy VOO or SPY", "speech": "How do you buy it? Open a free brokerage account at Fidelity, Schwab, or Vanguard. Then buy a fund called V O O or S P Y.", "img": "a smartphone showing a brokerage app with a buy button glowing green"},
            {"text": "Start with $50 or\n$100 it doesnt matter\njust start", "speech": "You can start with fifty or a hundred dollars, it doesn't matter. Just start.", "img": "a small pile of coins on a table with one coin being placed on top"},
            {"text": "A hundred today\ncould be $1,745\nin 30 years\njust sitting there", "speech": "A hundred dollars invested today could be worth over seventeen hundred in thirty years just sitting there growing on its own.", "img": "a magical money tree with golden leaves growing taller in sunlight"},
        ],
        "keywords": ["S&P 500", "Index Fund", "VOO", "Investing"],
    },
    {
        "title": "How Taxes Actually Work",
        "slides": [
            {"text": "You DONT pay 30%\non everything\nyou earn", "speech": "You do not pay thirty percent on everything you earn. That is the biggest myth in finance.", "img": "a tax form document with a red X stamped over a thirty percent label"},
            {"text": "Thats the biggest\nmyth in finance", "speech": "And it stops people from making more money. Here's how taxes actually work.", "img": "a shattered glass sign reading myth with dramatic fragments flying"},
            {"text": "Taxes work\nin brackets\nlike a staircase", "speech": "They work in brackets, like a staircase. Each step has a different rate.", "img": "a grand marble staircase with each step labeled a different percentage"},
            {"text": "First $11,000\nyou earn?\nOnly 10% tax", "speech": "The first eleven thousand dollars you earn is only taxed at ten percent.", "img": "a small neat pile of bills on a desk with a ten percent tag"},
            {"text": "Next $34,000\ntaxed at 12%", "speech": "The next thirty four thousand is taxed at twelve percent.", "img": "a calculator showing tax percentages with golden coins beside it"},
            {"text": "$45K to $95K\ntaxed at 22%", "speech": "Money between forty five and ninety five thousand is taxed at twenty two percent. Only the money above each step gets the higher rate.", "img": "a layered bar chart showing income brackets at different color levels"},
            {"text": "Only money ABOVE\neach step gets\nthe higher rate", "speech": "So if you earn fifty thousand dollars, you don't pay twenty two percent on all of it.", "img": "a staircase with money on each step and arrows pointing to different rates"},
            {"text": "Earn $50K?\nYou pay about\n$6,600 in tax\nnot $11,000", "speech": "You pay ten percent on the first chunk, twelve on the next, and twenty two only on the last portion. Your total tax is about sixty six hundred.", "img": "money divided into three color coded portions on a dark table"},
            {"text": "Your effective rate\nis about 13%\nnot 22%", "speech": "Which is an effective rate of about thirteen percent, not twenty two.", "img": "a percentage display showing thirteen in green instead of twenty two in red"},
            {"text": "A raise will NEVER\nmake you lose money\nThats a myth", "speech": "A raise will never make you lose money overall. That is a complete myth. Never turn down more money because you think you'll lose it to taxes.", "img": "a person celebrating a pay raise with confetti and a bigger paycheck"},
        ],
        "keywords": ["Taxes", "Tax Brackets", "Income Tax"],
    },
    {
        "title": "Debt Snowball vs Avalanche",
        "slides": [
            {"text": "Got debt?\n2 proven ways\nto destroy it", "speech": "Got debt? There are two proven ways to destroy it.", "img": "a pile of overdue bills and credit cards on a table with dramatic red light"},
            {"text": "Method 1\nDebt Snowball", "speech": "Method one is the debt snowball.", "img": "a glowing white snowball rolling downhill growing massive in moonlight"},
            {"text": "List all debts\nsmallest to largest\nIgnore interest rates", "speech": "List all your debts from smallest balance to largest. Ignore the interest rates completely. Pay the minimum on everything except the smallest debt.", "img": "a notebook with a ranked list of debts from small to large amounts"},
            {"text": "Pay off the\nsmallest one first\nget a quick win", "speech": "Throw every extra dollar at that smallest one. When it's paid off, take that entire payment and roll it into the next smallest debt. You get quick wins that keep you motivated.", "img": "a golden trophy being lifted in celebration with sparkles and light"},
            {"text": "Then roll that\npayment into\nthe next debt", "speech": "Method two is the debt avalanche.", "img": "a powerful snow avalanche crashing down a mountain with dramatic force"},
            {"text": "Method 2\nDebt Avalanche", "speech": "Instead of smallest balance, you target the debt with the highest interest rate first.", "img": "a red bullseye target with an arrow hitting the center precisely"},
            {"text": "Pay off the\nhighest interest\nrate first", "speech": "This saves you the most money on interest over time because you're eliminating the most expensive debt first.", "img": "a large red percentage symbol being smashed and crumbling apart"},
            {"text": "You save the\nmost money\non interest", "speech": "Snowball wins on motivation. When you see debts disappearing quickly, it feels amazing.", "img": "a happy person pumping their fist in triumph with a glowing background"},
            {"text": "Snowball wins\non motivation\nAvalanche wins\non math", "speech": "Avalanche wins on pure math. You pay less total interest. Honestly, both methods work.", "img": "a split screen showing heart versus calculator representing emotion versus math"},
            {"text": "Pick one today\nand stick with it\nBoth work\nconsistency wins", "speech": "The best one is whichever one you'll actually stick with. Pick one today and commit to it. Consistency beats perfection every time.", "img": "a determined person walking a straight path toward a glowing finish line"},
        ],
        "keywords": ["Debt Snowball", "Debt Avalanche", "Debt Free"],
    },
    {
        "title": "Why You Need a Roth IRA",
        "slides": [
            {"text": "A Roth IRA is\nthe biggest\ncheat code\nin finance", "speech": "A Roth IRA is the single biggest cheat code in personal finance. Let me explain exactly how it works.", "img": "a golden key unlocking a treasure chest overflowing with glowing coins"},
            {"text": "You put in money\nyou already\npaid tax on", "speech": "You put in money that you've already paid taxes on. Normal after tax dollars from your paycheck.", "img": "a paycheck with dollar bills coming out of it after tax deductions"},
            {"text": "It grows\ncompletely\ntax FREE forever", "speech": "Then that money grows completely tax free. Forever.", "img": "a glowing green upward growth chart stretching infinitely into the sky"},
            {"text": "You withdraw it\ntax FREE\nin retirement", "speech": "And when you retire and take the money out, you pay zero taxes on it. Nothing.", "img": "a person relaxing on a tropical beach with a sunset and palm trees"},
            {"text": "The government gets\nNOTHING when\nyou take it out", "speech": "The government doesn't get a single penny of your gains.", "img": "a large zero symbol glowing gold next to a stack of tax-free money"},
            {"text": "Max contribution\n$7,000 per year", "speech": "You can contribute up to seven thousand dollars per year.", "img": "a glass jar filled to the brim with seven thousand dollars in cash"},
            {"text": "Start at 18\nput in $7K yearly", "speech": "If you start at eighteen and put in seven thousand every year into an S and P five hundred index fund.", "img": "a young adult at a desk opening their first investment account excited"},
            {"text": "By 65 you could\nhave $1.9 million\nTAX FREE", "speech": "By sixty five you could have one point nine million dollars. Completely tax free. Not a dollar goes to taxes.", "img": "stacks of gold bars and cash in a vault with the number 1.9 million"},
            {"text": "Open one at\nFidelity Schwab\nor Vanguard\nits free", "speech": "Go to Fidelity, Schwab, or Vanguard online. It's completely free to open. Pick an S and P five hundred index fund.", "img": "a smartphone showing a brokerage app account creation screen glowing"},
            {"text": "10 minutes to set up\nA lifetime of\ntax free wealth", "speech": "The entire process takes about ten minutes. Ten minutes of setup for a lifetime of tax free wealth. Open it today.", "img": "a clock showing ten minutes next to a lifetime of growing wealth"},
        ],
        "keywords": ["Roth IRA", "Retirement", "Tax Free Investing"],
    },
    {
        "title": "Dollar Cost Averaging Explained",
        "slides": [
            {"text": "Stop trying to\ntime the market\nNobody can do it", "speech": "Stop trying to time the stock market. Nobody can do it consistently.", "img": "a broken clock next to a chaotic stock chart showing impossible timing"},
            {"text": "Not even experts\nhedge funds or\nTV analysts", "speech": "Not hedge fund managers, not TV analysts, not your friend who says he always buys at the bottom. Nobody.", "img": "a financial news studio with screens showing conflicting market predictions"},
            {"text": "Instead invest\nthe same amount\nevery single month", "speech": "Instead, do what actually works. Invest the exact same amount of money every single month, no matter what the market is doing.", "img": "a calendar with monthly investment dates marked and coins dropping in"},
            {"text": "Market goes up?\nYou buy\nfewer shares", "speech": "When the market goes up, your money buys fewer shares because they're more expensive.", "img": "a rising green stock chart with fewer coins being collected at the top"},
            {"text": "Market crashes?\nYou buy MORE\ncheaper shares", "speech": "When the market crashes, your money buys more shares because they're cheaper.", "img": "a crashed red stock chart with many coins being scooped up at a discount"},
            {"text": "Over time your\naverage cost\nevens out", "speech": "Over time, your average cost per share evens out. This strategy is called dollar cost averaging.", "img": "a smoothed out average line running through volatile chart peaks and valleys"},
            {"text": "This is called\nDollar Cost\nAveraging", "speech": "It removes all emotion from investing. No more panicking during crashes, no more guessing when to buy.", "img": "a calm zen person meditating surrounded by floating stock charts"},
            {"text": "Set up automatic\ninvesting and\nforget about it", "speech": "Set up automatic monthly investing into an index fund and literally forget about it. Let it run on autopilot.", "img": "a phone with autopilot mode enabled showing automatic investment transfers"},
            {"text": "Check it once a year\nnot every day", "speech": "Check your portfolio maybe once a year, not every single day. Studies show that investors who check daily actually earn less.", "img": "a single calendar page circled once per year in a peaceful setting"},
            {"text": "Slow and steady\nwins the\nwealth race", "speech": "Slow and steady wins the wealth race. Consistency beats timing every single time.", "img": "a determined tortoise crossing a golden finish line ahead of a hare"},
        ],
        "keywords": ["Dollar Cost Averaging", "Investing Strategy", "Passive Investing"],
    },
    {
        "title": "How Banks Make Money From You",
        "slides": [
            {"text": "Banks make money\nFROM you\nheres exactly how", "speech": "Banks make money from you and most people have no idea how much. Here's the full picture.", "img": "a massive grand bank building with imposing marble columns at night"},
            {"text": "You deposit $1,000\nthey pay you\n0.01% interest", "speech": "You deposit a thousand dollars. They pay you zero point zero one percent interest. That's ten cents per year.", "img": "a few tiny copper pennies sitting alone on a vast empty dark surface"},
            {"text": "Thats 10 cents\nper year\nfor your money", "speech": "Ten cents for lending them your money.", "img": "a single dime coin sitting on a dark table looking insignificant"},
            {"text": "They lend YOUR\nmoney out to\nothers at 7%", "speech": "Then they take your money and lend it out to other people at seven percent interest. They keep the entire difference as profit.", "img": "a bank vault with money flowing out one door and profits pouring in"},
            {"text": "They keep the\ndifference as\nprofit", "speech": "On top of that they charge overdraft fees, late payment fees, monthly maintenance fees, and dozens of hidden charges.", "img": "fine print on a document with hidden fees highlighted in red ink"},
            {"text": "Plus overdraft fees\nlate fees and\nhidden charges", "speech": "American banks made over two hundred billion dollars in fees last year alone. From regular people like you and me.", "img": "mountains of gold coins piling up inside a bank vault overflowing"},
            {"text": "Banks made $200\nbillion in fees\nlast year alone", "speech": "So how do you fight back?", "img": "a raised fist silhouette against a glowing background of resistance"},
            {"text": "How to fight back?\nSwitch to a high\nyield savings account", "speech": "Switch to a high yield savings account at an online bank. They pay four to five percent interest on your savings.", "img": "a glowing smartphone showing a high yield savings account with big returns"},
            {"text": "Online banks pay\n4-5% interest\nnot 0.01%", "speech": "That's literally four hundred times more interest going into your pocket.", "img": "money multiplying rapidly with green upward arrows and growing stacks"},
            {"text": "Same FDIC protection\n400x more interest\ngoing to YOU", "speech": "They have the same FDIC insurance as big banks. Same safety, way more money for you. Make the switch.", "img": "a glowing shield with FDIC written on it protecting a stack of cash"},
        ],
        "keywords": ["Banks", "High Yield Savings", "Fees", "Interest"],
    },
    {
        "title": "Why Renting Is Not Throwing Money Away",
        "slides": [
            {"text": "Renting is NOT\nthrowing money away\nheres the truth", "speech": "Everyone says renting is throwing money away. That's completely wrong. Let me show you the real math.", "img": "a modern luxury apartment building with glass balconies lit up at night"},
            {"text": "A $400K house costs\n$2,800 per month\njust in mortgage", "speech": "A four hundred thousand dollar house costs about twenty eight hundred a month in mortgage payments alone.", "img": "a beautiful suburban house with a for sale sign and a large price tag"},
            {"text": "Add property taxes\ninsurance repairs\nand HOA fees", "speech": "But that's not the real cost. Add property taxes, homeowners insurance, maintenance, repairs, and HOA fees.", "img": "a tall stack of bills and expense invoices piling up on a desk"},
            {"text": "Real cost?\n$3,500+ per month\nnot $2,800", "speech": "You're actually paying thirty five hundred or more per month.", "img": "a calculator showing a surprisingly high total cost number glowing red"},
            {"text": "First 7 years\nmost of your\npayment is INTEREST", "speech": "And in the first seven years of your mortgage, most of your monthly payment goes to interest, not equity. You're paying the bank, not building wealth.", "img": "money flowing from a house into a bank building through a pipeline"},
            {"text": "Youre paying\nthe bank\nnot building equity", "speech": "Meanwhile renting gives you flexibility to move for better jobs, zero surprise repair costs.", "img": "a person walking freely through an open door to a new city skyline"},
            {"text": "Renting gives you\nflexibility and\nzero surprise costs", "speech": "And no risk of your home losing value.", "img": "a person relaxing comfortably on a modern apartment couch looking happy"},
            {"text": "Invest the difference\nbetween rent and\nownership costs", "speech": "If rent is cheaper than owning, take the difference and invest it in index funds. You might build more wealth as a renter.", "img": "money being redirected from housing costs into a growing investment chart"},
            {"text": "Only buy when\nyoull stay 5+ years\nand the math\nactually works", "speech": "Only buy a house when you plan to stay at least five years and the numbers actually make sense for your income.", "img": "a house key being held up with a five year timeline and calculator"},
            {"text": "There is no shame\nin renting\nIts a smart\nfinancial choice", "speech": "There is absolutely no shame in renting. It's often the smarter financial choice.", "img": "a confident person standing proudly in their well-decorated rental apartment"},
        ],
        "keywords": ["Renting vs Buying", "Real Estate", "Housing"],
    },
    {
        "title": "Pay Yourself First",
        "slides": [
            {"text": "The number 1 rule\nof building wealth", "speech": "The number one rule of building wealth. Pay yourself first, before you pay anyone or anything else.", "img": "a golden number one trophy on a pedestal with dramatic spotlight"},
            {"text": "Pay yourself\nFIRST\nbefore anything else", "speech": "Most people do it backwards. They pay their rent, their bills, buy groceries, maybe eat out.", "img": "a person stressed at a desk surrounded by bills and expense envelopes"},
            {"text": "Most people pay\nbills first then\nsave whats left", "speech": "And then try to save whatever is left at the end of the month.", "img": "an empty wallet turned upside down with nothing falling out in dim light"},
            {"text": "But theres never\nanything left\nand you know it", "speech": "But there's never anything left. You know it, I know it. Flip it completely.", "img": "a bank account screen showing zero balance with red empty indicator"},
            {"text": "Flip it completely", "speech": "The second your paycheck hits your bank account, automatically move twenty percent into savings.", "img": "a dramatic switch being flipped from off to on with sparks flying"},
            {"text": "The second your\npaycheck hits\nsave 20%\nimmediately", "speech": "Set up the automatic transfer so you never even see that money. It goes away before you can spend it.", "img": "a phone showing an automatic bank transfer moving money to savings"},
            {"text": "Set up automatic\ntransfer so you\nnever see it", "speech": "After about two weeks, you completely forget about it.", "img": "a robot hand pressing an automate button on a sleek control panel"},
            {"text": "After 2 weeks\nyou wont even\nnotice its gone", "speech": "You adjust your spending naturally without even trying. It doesn't feel like sacrifice.", "img": "a relaxed person sitting comfortably with a smile looking content"},
            {"text": "You adjust your\nspending naturally\nwithout trying", "speech": "Every single millionaire does this. It doesn't matter if they make fifty thousand or five hundred thousand a year.", "img": "a silhouette of a wealthy person on a rooftop overlooking city lights"},
            {"text": "Every millionaire\ndoes this\nIts not about income\nits about the habit", "speech": "It's not about how much you earn. It's about building the habit of keeping what you earn.", "img": "a chain of golden habits linking together forming a strong rope upward"},
        ],
        "keywords": ["Pay Yourself First", "Savings Habit", "Wealth Building"],
    },
    {
        "title": "What Is an ETF and Why Everyone Buys Them",
        "slides": [
            {"text": "What is an ETF\nand why does\neveryone buy them?", "speech": "What is an E T F and why does literally everyone buy them?", "img": "a busy stock exchange trading floor with screens and traders in action"},
            {"text": "ETF stands for\nExchange Traded Fund", "speech": "E T F stands for exchange traded fund.", "img": "glowing letters ETF floating above a financial data dashboard screen"},
            {"text": "Think of it like\na basket holding\nhundreds of stocks", "speech": "Think of it like a shopping basket that holds hundreds of different stocks inside it.", "img": "a golden basket overflowing with miniature stock certificates and coins"},
            {"text": "Instead of picking\none company\nyou own hundreds\nat once", "speech": "Instead of picking one single company and hoping it does well, you own hundreds of companies all at once.", "img": "hundreds of small company logos arranged in a colorful mosaic pattern"},
            {"text": "If one company\nfails the rest\nkeep you safe", "speech": "If one company completely fails, the rest of the basket keeps your money safe. That's the power of diversification.", "img": "a glowing protective shield dome covering a collection of company icons"},
            {"text": "ETFs trade like\nregular stocks\nbuy and sell anytime", "speech": "E T Fs trade just like regular stocks. You can buy and sell them anytime during market hours with just a few taps on your phone.", "img": "a hand tapping a buy button on a sleek trading app on a smartphone"},
            {"text": "Fees are tiny\nusually under 0.1%\nper year", "speech": "The fees are incredibly low, usually under zero point one percent per year.", "img": "a tiny price tag showing 0.1 percent next to a large pile of savings"},
            {"text": "Compare that to\nmutual funds\ncharging 1-2%", "speech": "Compare that to traditional mutual funds that charge one to two percent. That difference saves you tens of thousands over your lifetime.", "img": "two scales comparing a tiny fee versus a large fee with dramatic contrast"},
            {"text": "Popular ETFs?\nVOO SPY QQQ\nstart with $10", "speech": "The most popular E T Fs are V O O and S P Y which track the S and P five hundred, and Q Q Q which tracks top tech companies. You can start with as little as ten dollars.", "img": "glowing stock ticker symbols VOO SPY QQQ on a futuristic dark display"},
            {"text": "Its the simplest\nsafest way for\nbeginners to\nstart investing", "speech": "It's the simplest, safest, and cheapest way for beginners to start investing. Open a free brokerage account and buy your first E T F today.", "img": "a welcoming open door with warm light leading to a path of gold coins"},
        ],
        "keywords": ["ETF", "Exchange Traded Fund", "Index Investing"],
    },
    {
        "title": "How Credit Cards Actually Work",
        "slides": [
            {"text": "How credit cards\nactually work\nno one teaches this", "speech": "How do credit cards actually work? Nobody teaches this in school.", "img": "a shiny gold credit card floating with a glowing halo in dark space"},
            {"text": "The bank gives\nyou a spending\nlimit", "speech": "The bank gives you a credit limit, that's the max you can spend.", "img": "a bank building with a glowing approved stamp and credit limit number"},
            {"text": "You buy stuff now\nand pay for it\nlater", "speech": "You buy things now and pay for them later. Here's where it gets critical.", "img": "a shopping cart full of items with a pay later countdown timer"},
            {"text": "Pay the FULL\nbalance each month?\nZero interest charged", "speech": "If you pay the full balance every single month before the due date, you are charged zero interest. Nothing. The bank is giving you a free loan.", "img": "a large glowing green zero percent with a checkmark beside it"},
            {"text": "Its literally\nfree money plus\ncashback and points", "speech": "Some cards even give you one to five percent cashback or travel points on top of that. Free money.", "img": "golden coins and reward points flying upward from a credit card"},
            {"text": "Only pay the\nminimum amount?", "speech": "But if you only pay the minimum amount.", "img": "a tiny minimum payment slip glowing red with a warning symbol"},
            {"text": "They charge 20-30%\ninterest on\neverything left", "speech": "They charge you twenty to thirty percent interest on everything that's left.", "img": "a massive red percentage number crushing a pile of money beneath it"},
            {"text": "$1,000 balance\nat 25% interest\n= $250 per year\njust in interest", "speech": "A thousand dollar balance at twenty five percent interest costs you two hundred fifty dollars per year just in interest charges.", "img": "money being drained through a funnel into a dark pit of debt"},
            {"text": "The rule is simple\nNever spend more\nthan you can\npay off monthly", "speech": "The rule is dead simple. Never put something on a credit card unless you can pay it off in full that same month.", "img": "a golden rule tablet with simple text glowing on a dark pedestal"},
            {"text": "Use cards for\nrewards not\nfor borrowing\nThats the secret", "speech": "Use credit cards for the rewards and cashback, never for borrowing money you don't have. That's the secret.", "img": "a glowing golden key unlocking a treasure chest of credit card rewards"},
        ],
        "keywords": ["Credit Cards", "Interest Rates", "Cashback"],
    },
    {
        "title": "What Is a 401k Retirement Plan",
        "slides": [
            {"text": "What is a 401k?\nLet me explain it\nsimply", "speech": "What is a four oh one K? Let me explain it simply so you actually understand it.", "img": "an official retirement plan document with a golden 401k seal on it"},
            {"text": "Its a retirement\nsavings account\nthrough your job", "speech": "It's a retirement savings account that you get through your employer.", "img": "a modern corporate office with employees at desks and warm lighting"},
            {"text": "Money comes out\nof your paycheck\nBEFORE taxes", "speech": "Money comes out of your paycheck before taxes are calculated.", "img": "a paycheck with money being redirected before a tax gate labeled taxes"},
            {"text": "Earn $50K?\nPut in $5K?\nYou only pay tax\non $45K", "speech": "If you earn fifty thousand and put five thousand into your four oh one K, you only pay income tax on forty five thousand. You save money on taxes right now.", "img": "a tax bill getting smaller with a green savings checkmark beside it"},
            {"text": "You save money\non taxes\nright now today", "speech": "But here's the absolute best part.", "img": "confetti and sparkles bursting from a golden gift box surprise moment"},
            {"text": "Many employers\nMATCH what you\nput in", "speech": "Many employers will match what you contribute. You put in a hundred dollars, they put in a hundred dollars.", "img": "two stacks of money side by side doubling with an employer match label"},
            {"text": "You put in $100\nthey put in $100\nthats DOUBLE", "speech": "Your money instantly doubles before it even starts growing. That is free money from your boss.", "img": "a hundred dollar bill splitting into two identical bills with magic glow"},
            {"text": "Its literally free\nmoney from your boss", "speech": "The most important rule is always contribute at least enough to get the full employer match.", "img": "a hand offering a gift box of money with a free label glowing green"},
            {"text": "Always contribute\nenough to get\nthe full match", "speech": "If they match up to six percent of your salary, make sure you put in at least six percent.", "img": "a progress bar filling to six percent with a green full match indicator"},
            {"text": "Saying no to\nthe match is like\nburning free money\nDont do it", "speech": "Saying no to the employer match is exactly like your boss handing you free money and you saying no thanks. Don't be one of those people.", "img": "hundred dollar bills catching fire and burning away in dramatic flames"},
        ],
        "keywords": ["401k", "Retirement Plan", "Employer Match"],
    },
    {
        "title": "Why You Should Never Lease a Car",
        "slides": [
            {"text": "Never lease a car\nand heres exactly\nwhy", "speech": "Never lease a car. Here's exactly why it's one of the worst financial decisions you can make.", "img": "a shiny car dealership showroom with rows of new cars under bright lights"},
            {"text": "A lease is just\nlong term renting\nwith extra rules", "speech": "A lease is basically long term renting with extra rules and restrictions.", "img": "a thick lease contract being signed with chains wrapping around it"},
            {"text": "You pay $400/month\nfor 3 years\nthats $14,400 total", "speech": "You pay about four hundred dollars a month for three years. That's fourteen thousand four hundred dollars total.", "img": "calendar pages flipping with monthly payment bills stacking up each month"},
            {"text": "After 3 years\nyou own absolutely\nNOTHING", "speech": "And after those three years, you own absolutely nothing. You hand the car right back to the dealer.", "img": "empty open hands with car keys being handed back in a dim parking lot"},
            {"text": "You hand the\ncar back and\nstart over", "speech": "And start the whole process over again.", "img": "a circular arrow loop with a car going around endlessly never stopping"},
            {"text": "Plus mileage limits\nwear charges and\nhidden fees", "speech": "On top of the monthly payments, there are mileage limits, usually around twelve thousand miles per year. Go over? You pay twenty five cents for every extra mile.", "img": "a car odometer close up showing high mileage with a red warning limit"},
            {"text": "Go over the\nmileage limit?\nPay 25 cents\nper extra mile", "speech": "Plus wear and tear charges for any scratches or dents.", "img": "a car door with a scratch and a repair bill being slapped on the windshield"},
            {"text": "Instead buy a\nreliable used car\n2-3 years old", "speech": "Instead, here's what smart people do. Buy a reliable used car that's two to three years old. Someone else already took the biggest depreciation hit.", "img": "a clean reliable used car parked on a sunny street looking great"},
            {"text": "Pay it off then\ndrive it for\n7-10 more years\npayment free", "speech": "Pay it off in three to four years, then drive it for seven to ten more years with zero car payments.", "img": "a person driving on an open highway at sunset feeling free and happy"},
            {"text": "You save $30,000+\ncompared to leasing\ntwice over 10 years", "speech": "Over ten years, you save over thirty thousand dollars compared to leasing twice. That's money you could invest and grow into real wealth.", "img": "a stack of thirty thousand dollars next to a growing investment chart"},
        ],
        "keywords": ["Car Lease", "Used Car", "Saving Money"],
    },
    {
        "title": "What Is Cryptocurrency Explained Simply",
        "slides": [
            {"text": "What is\ncryptocurrency?\nSimplest explanation", "speech": "What is cryptocurrency in the simplest terms possible?", "img": "a glowing golden bitcoin coin floating in a futuristic digital space"},
            {"text": "Its digital money\nthat lives only\non computers", "speech": "It's digital money that exists only on computers. No bank controls it and no government can print more of it.", "img": "streams of glowing digital code flowing across computer screens in the dark"},
            {"text": "No bank controls it\nNo government\ncan print more", "speech": "It runs on a technology called blockchain, which is basically a public record that everyone can see but nobody can cheat.", "img": "a glowing blockchain network of connected nodes and chains in neon blue"},
            {"text": "Bitcoin was first\ncreated in 2009\nby an unknown person", "speech": "Bitcoin was the very first cryptocurrency, created in two thousand nine by an anonymous person or group.", "img": "a mysterious hooded figure at a computer with the bitcoin symbol glowing"},
            {"text": "Today there are\nthousands of\ncryptocurrencies", "speech": "Today there are thousands of different cryptocurrencies.", "img": "dozens of different cryptocurrency coins scattered across a dark surface"},
            {"text": "People buy hoping\nthe price goes up\nso they can sell\nfor profit", "speech": "People buy crypto hoping the price goes up so they can sell it later for a profit. Some people have made fortunes.", "img": "a dramatic green crypto price chart shooting upward with golden glow"},
            {"text": "But crypto can drop\n50% in a single week\nIts extremely risky", "speech": "But crypto can drop fifty percent in a single week. It's the most volatile and risky investment available.", "img": "a red crypto chart crashing dramatically downward with alarm indicators"},
            {"text": "Rule 1\nNever invest more\nthan you can\nafford to lose", "speech": "Rule one, never invest more than you can completely afford to lose. If you put in a thousand dollars, you should be okay with that becoming zero.", "img": "a yellow caution triangle with a risk warning symbol glowing in darkness"},
            {"text": "Rule 2\nBuild your basics\nfirst emergency fund\nindex funds 401k", "speech": "Rule two, build your financial basics first. Emergency fund, index fund investments, four oh one K contributions. Get those set up before you think about crypto.", "img": "stacked building blocks forming a solid foundation with financial labels"},
            {"text": "Crypto is dessert\nnot the main meal\nGet the basics\nright first", "speech": "Crypto is the dessert, not the main meal. Get the fundamentals right first, then explore crypto with money you can afford to lose.", "img": "a fancy dessert plate beside a full main course dinner on a table"},
        ],
        "keywords": ["Cryptocurrency", "Bitcoin", "Digital Currency"],
    },
    {
        "title": "How Insurance Works in 60 Seconds",
        "slides": [
            {"text": "How does insurance\nwork? Simplest\nexplanation ever", "speech": "How does insurance actually work? Here's the simplest explanation ever.", "img": "a large protective umbrella shielding a person from a heavy rain storm"},
            {"text": "You pay a small\namount every month\ncalled a premium", "speech": "You pay a small amount every month. This is called your premium.", "img": "a small stack of coins being placed into a payment slot each month"},
            {"text": "Thousands of other\npeople pay the\nsame premium", "speech": "Thousands of other people with the same insurance also pay their premiums.", "img": "a large crowd of diverse people all contributing to one central point"},
            {"text": "All that money goes\ninto one giant pool", "speech": "All of that money goes into one giant pool.", "img": "streams of coins and money flowing into one massive golden pool"},
            {"text": "When something bad\nhappens to YOU\nthe pool covers it", "speech": "When something bad happens to one person in the group, that pool pays for the expenses.", "img": "a safety net catching a falling person with money cushioning the impact"},
            {"text": "Car crash? Pool pays\nHospital bill?\nPool pays", "speech": "Car crash? The pool covers the repair and medical bills. Hospital visit? The pool covers it. House fire? The pool pays to rebuild.", "img": "a split scene showing car crash hospital and house fire all being covered"},
            {"text": "Youre trading\na small certain cost\nfor protection from\na huge one", "speech": "You're essentially trading a small predictable cost for protection against a huge unexpected disaster.", "img": "a massive glowing shield dome protecting a family from incoming dangers"},
            {"text": "The 4 types\nyou need", "speech": "The four types of insurance you actually need are.", "img": "four glowing icons in a row representing essential insurance types"},
            {"text": "Health insurance\nAuto insurance\nRenters insurance\nLife insurance\nif you have family", "speech": "Health insurance, this is non negotiable. Auto insurance, required by law. Renters or homeowners insurance. And life insurance if you have a family that depends on your income.", "img": "four protective shields labeled health auto home and life in a row"},
            {"text": "One bad event\nwithout insurance\ncan put you in\ndebt for years", "speech": "Skip the fancy extras. Just get these four basics. One bad event without insurance can put you in serious debt for years. It's not worth the risk.", "img": "a person overwhelmed by a mountain of medical bills and debt papers"},
        ],
        "keywords": ["Insurance", "Health Insurance", "Financial Protection"],
    },
    {
        "title": "The Rule of 72 Will Blow Your Mind",
        "slides": [
            {"text": "The Rule of 72\nthe fastest math\ntrick in finance", "speech": "The rule of seventy two is the fastest math trick in all of finance.", "img": "a large glowing golden number 72 floating above a math equation"},
            {"text": "It tells you exactly\nhow fast your\nmoney DOUBLES", "speech": "It tells you exactly how fast your money doubles.", "img": "a stack of money splitting into two equal stacks with sparkle effects"},
            {"text": "Take 72 and\ndivide it by\nyour interest rate", "speech": "Take the number seventy two and divide it by your annual interest rate. The answer is how many years until your money doubles.", "img": "a calculator showing 72 divided by interest rate with glowing result"},
            {"text": "Thats how many\nyears until your\nmoney doubles", "speech": "Getting ten percent returns in the stock market?", "img": "a stock market chart showing ten percent annual returns in green"},
            {"text": "Getting 10% returns?\n72 / 10 = 7.2 years\nto double", "speech": "Seventy two divided by ten equals seven point two years to double your money.", "img": "a timeline showing seven years with money doubling at the end"},
            {"text": "$10,000 becomes\n$20,000 in\njust 7 years", "speech": "So ten thousand dollars becomes twenty thousand in about seven years. Without you adding a single dollar.", "img": "ten thousand dollars transforming into twenty thousand with magical glow"},
            {"text": "Then $40,000\nthen $80,000\nthen $160,000", "speech": "Then it doubles again to forty thousand, then eighty thousand, then one hundred sixty thousand.", "img": "an exponential curve shooting upward steeply with money milestones"},
            {"text": "8 doublings turns\n$10K into $2.5\nmillion", "speech": "Eight doublings turns ten thousand into two point five million.", "img": "a vault door opening to reveal 2.5 million in stacked gold and cash"},
            {"text": "But at 1% savings\naccount? 72 / 1\n= 72 years to double", "speech": "But if your money is in a savings account earning one percent, seventy two divided by one equals seventy two years to double. Your money takes a lifetime to double once.", "img": "a tiny snail crawling extremely slowly across a long empty desert road"},
            {"text": "Where you put\nyour money matters\nmore than how much\nyou put in", "speech": "Where you put your money matters infinitely more than how much you put in. Choose wisely.", "img": "a dramatic crossroads with two paths one leading to wealth one to nothing"},
        ],
        "keywords": ["Rule of 72", "Compound Interest", "Money Doubling"],
    },
    {
        "title": "Why Lottery Winners Go Broke",
        "slides": [
            {"text": "Why do lottery\nwinners go broke?\nIts not bad luck", "speech": "Why do lottery winners go broke? It's not bad luck. It's a pattern.", "img": "a golden lottery ticket being scratched with dramatic sparkles flying"},
            {"text": "70% of winners\nlose everything\nwithin 5 years", "speech": "Seventy percent of lottery winners lose everything within five years. Here's exactly what happens.", "img": "a large seventy percent statistic in red with a shocking exclamation mark"},
            {"text": "First the government\ntakes 40% in taxes\nright away", "speech": "First, the government takes about forty percent in taxes immediately.", "img": "a government building hand reaching out taking forty percent of cash pile"},
            {"text": "Win $10 million?\nYou actually get\nabout $6 million", "speech": "Win ten million? You actually get about six million.", "img": "a ten million dollar check shrinking down to six million with red cuts"},
            {"text": "Then friends and\nfamily you havent\nheard from in years\nshow up", "speech": "Then suddenly, friends and family you haven't heard from in years start showing up asking for money.", "img": "a crowd of people with outstretched hands surrounding a nervous person"},
            {"text": "They buy mansions\ncars and stuff\nwith massive\nmaintenance costs", "speech": "They buy huge mansions, luxury cars, and expensive things with massive ongoing maintenance costs nobody warns them about.", "img": "a massive mansion with luxury sports cars parked in front at night"},
            {"text": "A $5M house costs\n$50,000 per year\njust in property tax", "speech": "A five million dollar house costs fifty thousand dollars per year just in property taxes.", "img": "a large property tax bill stamped on a mansion backdrop looking expensive"},
            {"text": "The real problem?\nThey never learned\nhow to manage money", "speech": "The real problem isn't the spending. It's that they never learned how to manage money.", "img": "a confused person looking at scattered financial documents overwhelmed"},
            {"text": "Getting money and\nkeeping money are\ntwo completely\ndifferent skills", "speech": "Getting money and keeping money are two completely different skills.", "img": "two separate skill icons one for earning one for managing side by side"},
            {"text": "Thats why financial\neducation beats luck\nBuild wealth slowly\nit lasts", "speech": "That's exactly why financial education beats luck every single time. People who build wealth slowly keep their money forever. Quick money disappears.", "img": "an open book of financial knowledge glowing with golden wisdom light"},
        ],
        "keywords": ["Lottery", "Wealth Management", "Financial Literacy"],
    },
    {
        "title": "What Is Passive Income Explained",
        "slides": [
            {"text": "What is passive\nincome? Lets make\nit simple", "speech": "What is passive income? Let's make it really simple.", "img": "a person sleeping peacefully while money flows into their bank account"},
            {"text": "Its money you earn\nwithout trading\nyour time for it", "speech": "It's money you earn without actively trading your time for it every day.", "img": "a broken clock next to flowing cash showing time is not needed"},
            {"text": "Your job = active\nincome you stop\nworking you stop\nearning", "speech": "Your regular job is active income. You show up, you work, you get paid. Stop showing up, stop getting paid.", "img": "a person working at a desk in an office under fluorescent lights"},
            {"text": "Passive income keeps\npaying you even\nwhile you sleep", "speech": "Passive income is different. It keeps paying you even while you sleep, while you're on vacation.", "img": "a person relaxing on a tropical beach while money notifications pop up"},
            {"text": "Dividend stocks pay\nyou cash every\n3 months just\nfor owning them", "speech": "Dividend stocks pay you cash every three months just for owning shares. You don't have to do anything.", "img": "a stock portfolio screen showing quarterly dividend payments in green"},
            {"text": "Rental property\npays monthly rent\nfrom tenants", "speech": "Rental properties pay you monthly rent from tenants living in your property.", "img": "an apartment building with rent money flowing from windows to the owner"},
            {"text": "Online business\nearns revenue\n24 hours a day", "speech": "An online business or YouTube channel can earn revenue twenty four hours a day, seven days a week.", "img": "a glowing laptop screen showing online revenue coming in around the clock"},
            {"text": "But heres the truth\nnothing is passive\nat the START", "speech": "But here's the truth nobody tells you. Nothing is truly passive at the start. Every passive income stream requires time or money invested upfront.", "img": "a person working hard laying bricks to build a strong foundation"},
            {"text": "You invest time\nor money upfront\nthen it pays you\nback over time", "speech": "You build it, set it up, and then over time it starts paying you back.", "img": "seeds being planted in soil with small green shoots starting to grow"},
            {"text": "Start with dividend\nETFs like SCHD\neasiest passive\nincome for beginners", "speech": "The easiest passive income for beginners is dividend E T Fs like S C H D. Buy shares, receive quarterly cash payments. Start there.", "img": "a welcoming first step on a golden staircase leading upward to wealth"},
        ],
        "keywords": ["Passive Income", "Dividends", "Financial Freedom"],
    },
    {
        "title": "What Is Net Worth and How to Calculate It",
        "slides": [
            {"text": "Your net worth is\nthe most important\nnumber in finance", "speech": "Your net worth is the single most important number in personal finance. It's a complete snapshot of your financial health.", "img": "a glowing golden number one symbol on a dark pedestal of importance"},
            {"text": "Its a snapshot of\nyour entire\nfinancial health", "speech": "Here's how to calculate it.", "img": "a medical-style health checkup screen showing financial vital signs"},
            {"text": "Step 1\nAdd everything\nyou OWN", "speech": "Step one, add up everything you own. Cash in your bank accounts, savings, investments, house value, car value. That's your total assets.", "img": "a house car and investment portfolio arranged together as total assets"},
            {"text": "Cash savings\ninvestments\nhouse value\ncar value", "speech": "Step two, subtract everything you owe.", "img": "a calculator adding up values with golden totals appearing on screen"},
            {"text": "Step 2\nSubtract everything\nyou OWE", "speech": "Credit card balances, car loans, mortgage balance, student loans, any money you owe anyone. That's your total liabilities.", "img": "red debt numbers being subtracted with a minus symbol glowing red"},
            {"text": "Credit card debt\ncar loans\nmortgage\nstudent loans", "speech": "Assets minus liabilities equals your net worth.", "img": "a subtraction equation in bold with the result highlighted in gold"},
            {"text": "What you OWN\nminus what you OWE\nequals NET WORTH", "speech": "If your number is negative right now, do not panic.", "img": "a clean formula displayed on a chalkboard with dramatic chalk writing"},
            {"text": "Negative?\nDont panic\nmost people start\nin the negative", "speech": "Most people in their twenties and thirties have a negative net worth because of student loans. That's completely normal.", "img": "a calm serene person meditating with a peaceful blue aura around them"},
            {"text": "Track it every\nsingle month\non a spreadsheet", "speech": "The key is to track this number every single month. Write it down on a simple spreadsheet.", "img": "a laptop showing a monthly net worth tracking spreadsheet with charts"},
            {"text": "Your only goal is\nto make it higher\nthan last month\nevery month", "speech": "Your only goal is to make it higher than last month. Every single month. Pay down debt, save more, invest consistently. That's how you build real wealth.", "img": "a green upward arrow climbing higher each month on a progress chart"},
        ],
        "keywords": ["Net Worth", "Assets", "Liabilities", "Financial Health"],
    },
    {
        "title": "What Is a Bear Market vs Bull Market",
        "slides": [
            {"text": "Bear market vs\nBull market\nwhat do they mean?", "speech": "Bear market versus bull market. What do these actually mean?", "img": "a bear and bull statue facing each other on Wall Street in golden light"},
            {"text": "BULL market\nmeans stocks are\ngoing UP for months", "speech": "A bull market means stocks have been going up consistently for months or years. Everyone is buying, prices keep climbing.", "img": "a powerful bull charging forward with green upward arrows behind it"},
            {"text": "Everyone is buying\nprices keep climbing\npeople feel great", "speech": "People feel optimistic and confident.", "img": "happy investors celebrating with confetti and green stock charts rising"},
            {"text": "BEAR market means\nstocks have dropped\n20% or more", "speech": "A bear market is the opposite. It means stocks have dropped twenty percent or more from their recent high.", "img": "a fierce growling bear with red crashing stock charts behind it"},
            {"text": "Fear takes over\npeople panic sell\nprices crash further", "speech": "Fear takes over, people panic sell everything, and prices crash even further.", "img": "panicked traders at screens with red numbers cascading downward"},
            {"text": "But bear markets\nare actually\nOPPORTUNITIES\nin disguise", "speech": "But bear markets are actually opportunities in disguise. The same great companies are now on sale at a huge discount.", "img": "a diamond hidden inside a rough rock being revealed with golden light"},
            {"text": "Stocks are on sale\nyou buy the same\ncompanies cheaper", "speech": "Since nineteen twenty eight, every single bear market eventually ended and was followed by a new bull market. Every one, without exception.", "img": "shopping bags with stock ticker labels showing huge discount sale prices"},
            {"text": "Since 1928 EVERY\nbear market ended\nand a bull market\nfollowed", "speech": "The average bear market only lasts about nine months. The average bull market lasts two point seven years.", "img": "a long historical chart showing every crash recovered with green rebounds"},
            {"text": "Average bear market\nlasts 9 months\nAverage bull market\nlasts 2.7 YEARS", "speech": "The good times last three times longer than the bad times.", "img": "a timeline bar showing short red bear periods vs long green bull periods"},
            {"text": "Be greedy when\nothers are fearful\nThats Warren Buffetts\nnumber 1 rule", "speech": "Warren Buffett's number one rule is be greedy when others are fearful. When everyone is panicking, that's when smart investors are buying.", "img": "a brave lone investor standing confidently while others run away in fear"},
        ],
        "keywords": ["Bear Market", "Bull Market", "Stock Market Cycles"],
    },
    {
        "title": "What Is Inflation and Why Should You Care",
        "slides": [
            {"text": "What is inflation?\nIt affects you\nevery single day", "speech": "What is inflation? It affects you every single day whether you realize it or not.", "img": "rising red price arrows floating upward from everyday items in a store"},
            {"text": "Inflation means\nprices go up\nover time", "speech": "Inflation means prices go up over time.", "img": "a grocery store aisle with glowing red price tags getting higher"},
            {"text": "A gallon of milk\ncost $1.50 in 2000\nToday its $4.50", "speech": "A gallon of milk cost about a dollar fifty in the year two thousand. Today that exact same gallon costs four dollars fifty.", "img": "a milk gallon on a grocery shelf with old and new price tags compared"},
            {"text": "Same milk\n3 times the price\nyour dollar buys less", "speech": "Same milk, three times the price. Your dollar literally buys less stuff each year.", "img": "a shrinking dollar bill getting smaller and weaker against a dark background"},
            {"text": "Average inflation\nis about 3%\nper year", "speech": "Average inflation is about three percent per year. Here's why this matters to you personally.", "img": "a three percent number displayed on a rising chart with yearly markers"},
            {"text": "If your salary\ndoesnt grow by\nat least 3%", "speech": "If your salary doesn't grow by at least three percent each year, you are effectively getting a pay cut.", "img": "a flat horizontal salary line being overtaken by a rising cost line"},
            {"text": "You are getting\na pay cut\nevery single year\neven if your check\nstays the same", "speech": "Even if your paycheck stays the exact same number, it buys less stuff than it did last year.", "img": "a paycheck staying the same while shopping bags get smaller and fewer"},
            {"text": "Savings account at\n0.01% does NOT\nbeat inflation", "speech": "A regular savings account paying zero point zero one percent does absolutely nothing against three percent inflation.", "img": "a tiny 0.01 percent being crushed by a massive 3 percent inflation wave"},
            {"text": "Investing at 10%\nDOES beat inflation\nyour money actually\ngrows", "speech": "But investing in the stock market at ten percent per year does beat inflation. After inflation, you're still gaining seven percent in real purchasing power.", "img": "a ten percent investment arrow soaring above a three percent inflation line"},
            {"text": "Saving keeps your\nmoney safe\nInvesting makes it\nstronger", "speech": "Saving keeps your money safe. Investing makes it actually stronger over time. You need both.", "img": "a strong muscular arm holding a shield protecting a growing stack of money"},
        ],
        "keywords": ["Inflation", "Cost of Living", "Purchasing Power"],
    },
    {
        "title": "How to Read Your Pay Stub",
        "slides": [
            {"text": "Can you actually\nread your pay stub?\nMost people cant", "speech": "Can you actually read your pay stub? Most people just look at the deposit amount and ignore everything else.", "img": "a detailed pay stub document on a desk with sections highlighted"},
            {"text": "GROSS PAY\nis what you earned\nbefore deductions", "speech": "Gross pay is what you earned before anything gets taken out. It's the big number at the top of your stub.", "img": "a large glowing salary number at the top of a pay stub document"},
            {"text": "This is the big\nnumber at the top", "speech": "Then come the deductions. This is where your money seems to disappear.", "img": "money vanishing through multiple deduction lines on a dark screen"},
            {"text": "Then come\nthe deductions\nthis is where\nmoney disappears", "speech": "Federal income tax takes a percentage based on your tax bracket. State income tax takes its cut if your state has one.", "img": "scissors cutting portions from a paycheck labeled federal and state tax"},
            {"text": "Federal income tax\nState tax\nSocial Security\nMedicare", "speech": "Social Security takes six point two percent. Medicare takes one point four five percent. Those are all mandatory.", "img": "official government stamps for Social Security and Medicare on documents"},
            {"text": "Health insurance\nand 401k come\nout too if you\nhave them", "speech": "Then your health insurance premium and four oh one K contributions come out if you have them set up.", "img": "health insurance card and 401k form next to deducted money amounts"},
            {"text": "After ALL deductions\nyou get NET PAY", "speech": "After all of those deductions, you're left with your net pay. That's your actual take home money.", "img": "a final net pay amount glowing green at the bottom of a pay stub"},
            {"text": "Thats your actual\ntake home money\nwhat hits your\nbank account", "speech": "The amount that hits your bank account.", "img": "a phone notification showing a direct deposit landing in a bank account"},
            {"text": "Gross = what\nyou earn\nNet = what\nyou keep", "speech": "Easy way to remember it. Gross pay is what you earn. Net pay is what you keep.", "img": "two columns side by side comparing a big gross number vs smaller net"},
            {"text": "Check it monthly\nfor errors\nMistakes happen\nand cost you money", "speech": "Check your pay stub at least once a month. Payroll mistakes happen more often than you think, and they always seem to be in the company's favor.", "img": "a magnifying glass carefully examining a pay stub for errors and mistakes"},
        ],
        "keywords": ["Pay Stub", "Gross Pay", "Net Pay", "Payroll"],
    },
    {
        "title": "Good Debt vs Bad Debt",
        "slides": [
            {"text": "Not all debt is bad\nsome debt actually\nmakes you richer", "speech": "Not all debt is created equal. Some debt actually makes you richer over time.", "img": "a balance scale with green good debt on one side and red bad debt on other"},
            {"text": "GOOD debt helps\nyou earn more\nmoney over time", "speech": "Good debt helps you earn more money or build wealth.", "img": "a growing green investment tree with money blossoming from its branches"},
            {"text": "Student loans for a\nhigh paying career\nGood debt", "speech": "Student loans that lead to a high paying career? That's good debt if you choose your degree wisely.", "img": "a graduation cap being tossed in the air with a bright successful future"},
            {"text": "Mortgage on a\nproperty that grows\nin value Good debt", "speech": "A mortgage on a property that appreciates in value? Good debt. You're building equity while living there.", "img": "a house with a rising green value arrow showing property appreciation"},
            {"text": "Business loan that\ngenerates more than\nit costs Good debt", "speech": "A business loan that generates more revenue than the interest costs? Good debt. You're using borrowed money to make more money.", "img": "a thriving business storefront with revenue flowing in and growing"},
            {"text": "BAD debt buys things\nthat lose value and\ncosts you interest", "speech": "Bad debt is the opposite. It buys things that lose value immediately and charges you interest.", "img": "shopping bags and impulse purchases fading away and losing value"},
            {"text": "Credit card debt on\nclothes and eating out\nBad debt", "speech": "Credit card debt from shopping sprees and eating out? Bad debt.", "img": "a pile of credit card bills stacking up next to empty shopping bags"},
            {"text": "Car loan on a car\nyou cant afford\nBad debt", "speech": "A car loan on a brand new luxury car you can't really afford? Bad debt. That car loses twenty percent the moment you drive off.", "img": "a brand new car driving off a lot with its value dropping immediately"},
            {"text": "The test is simple\nwill this debt make\nme richer or poorer\nin 5 years?", "speech": "The test is simple. Before taking on any debt, ask yourself, will this debt make me richer or poorer in five years?", "img": "a person at a crossroads thinking with richer and poorer paths ahead"},
            {"text": "Use debt as a tool\nto build wealth\nnever as a trap\nthat keeps you broke", "speech": "Use debt as a tool to build wealth, never as a trap that keeps you broke.", "img": "a golden wrench tool building a staircase of wealth upward to success"},
        ],
        "keywords": ["Good Debt", "Bad Debt", "Financial Decisions"],
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


def _extract_search_keywords(desc):
    """Pull 2-4 search-friendly keywords from a descriptive img prompt."""
    stop = {'a', 'an', 'the', 'of', 'on', 'in', 'at', 'to', 'and', 'or',
            'with', 'its', 'from', 'into', 'for', 'by', 'is', 'are', 'was',
            'being', 'their', 'that', 'this', 'no', 'not', 'showing',
            'looking', 'getting', 'labeled', 'versus', 'vs', 'next',
            'glowing', 'dramatic', 'golden', 'massive', 'tiny', 'large',
            'behind', 'beside', 'above', 'below', 'under', 'over',
            'dark', 'bright', 'single', 'each', 'every', 'slowly',
            'against', 'through', 'between', 'along', 'across'}
    words = desc.lower().replace(',', ' ').split()
    good = [w for w in words if w not in stop and len(w) > 2 and w.isalpha()]
    return ' '.join(good[:3]) if good else 'finance money'


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
        query = _extract_search_keywords(desc)
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


def create_slide_audios(slides, work_dir):
    """Generate audio for each slide's speech separately, measure exact duration per slide"""
    os.makedirs(work_dir, exist_ok=True)

    try:
        import edge_tts
    except ImportError:
        return None

    voices = [
        ("en-US-DavisNeural", "+20%", "-6Hz"),
        ("en-US-GuyNeural", "+20%", "-5Hz"),
        ("en-US-ChristopherNeural", "+20%", "-4Hz"),
        ("en-GB-RyanNeural", "+20%", "-5Hz"),
    ]

    working_voice = None
    for voice, rate, pitch in voices:
        try:
            test_path = os.path.join(work_dir, "test_voice.mp3")
            communicate = edge_tts.Communicate("Testing voice.", voice, rate=rate, pitch=pitch)
            loop = asyncio.new_event_loop()
            loop.run_until_complete(communicate.save(test_path))
            loop.close()
            if os.path.exists(test_path) and os.path.getsize(test_path) > 500:
                working_voice = (voice, rate, pitch)
                try:
                    os.remove(test_path)
                except Exception:
                    pass
                print(f"[OK] Using voice: {voice}")
                break
        except Exception:
            continue

    if not working_voice:
        return None

    audio_paths = []
    durations = []

    for idx, slide in enumerate(slides):
        audio_path = os.path.join(work_dir, f"speech_{idx}.mp3")
        voice, rate, pitch = working_voice
        try:
            communicate = edge_tts.Communicate(slide['speech'], voice, rate=rate, pitch=pitch)
            loop = asyncio.new_event_loop()
            loop.run_until_complete(communicate.save(audio_path))
            loop.close()
        except Exception as e:
            print(f"  [WARN] TTS failed for slide {idx}: {e}")
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
        voices = [
            ("en-US-DavisNeural", "+20%", "-6Hz"),
            ("en-US-GuyNeural", "+20%", "-5Hz"),
            ("en-US-ChristopherNeural", "+20%", "-4Hz"),
            ("en-GB-RyanNeural", "+20%", "-5Hz"),
        ]
        for voice, rate, pitch in voices:
            try:
                communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
                loop = asyncio.new_event_loop()
                loop.run_until_complete(communicate.save(output_path))
                loop.close()
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    print(f"[OK] Audio ready (deep voice: {voice})")
                    return True
            except Exception:
                continue
        raise Exception("All edge-tts voices failed")
    except Exception as e:
        print(f"[WARN] edge-tts failed ({e}), using gTTS...")

    from gtts import gTTS
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)
    print("[OK] Audio ready (gTTS fallback)")
    return True


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
    """Prepare clean slide images - no text overlay, just the image."""
    os.makedirs(work_dir, exist_ok=True)

    from PIL import Image

    W, H = 864, 1536

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

        bg.save(out, "JPEG", quality=95)
        del bg
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
