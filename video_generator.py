#!/usr/bin/env python3
"""
The AI Dollar - Video Generator
Finance education Shorts with cartoon/illustration backgrounds + animated zoom + deep male TTS
"""

import os
import gc
import subprocess
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"✅ FFmpeg ready: {FFMPEG}")
except Exception as e:
    FFMPEG = "ffmpeg"
    print(f"⚠️ Using system ffmpeg: {e}")

CONFIG = {"output_dir": "./videos"}

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")


CONTENT_TOPICS = [
    {
        "title": "Your $100 Is Now Worth $93",
        "search_queries": ["hundred dollar bill close up", "grocery store prices rising", "cash money wallet", "burning money fire", "mattress bedroom cozy", "stock market chart green", "index fund investing phone", "person saving money jar", "financial growth chart upward", "dollar losing value"],
        "slides": [
            {"text": "Your $100\nis now worth $93", "duration": 5},
            {"text": "Prices went up\n7% this year", "duration": 5},
            {"text": "Your cash\nstayed the same", "duration": 4},
            {"text": "Thats $7 gone\nfor doing nothing", "duration": 5},
            {"text": "Cash under your\nmattress loses\nvalue every day", "duration": 5},
            {"text": "So what actually\nbeats inflation?", "duration": 4},
            {"text": "Investing in\nstocks and\nindex funds", "duration": 5},
            {"text": "The S&P 500 averages\n10% per year\nInflation is only 3%", "duration": 6},
            {"text": "Your money grows\nfaster than\nprices rise", "duration": 5},
            {"text": "Saving protects\nyour money\nInvesting grows it\nYou need both", "duration": 6},
        ],
        "voiceover": "Your hundred dollars is now worth ninety three bucks. Let that sink in. Prices went up seven percent this year but your cash stayed the exact same. That's seven dollars gone just for doing absolutely nothing. And this happens every single year. Keeping cash under your mattress or in a regular savings account means you are literally losing money every single day. So what actually beats inflation? The answer is investing. Specifically stocks and index funds. The S and P five hundred, which tracks the top five hundred American companies, averages about ten percent per year. Inflation is usually around three percent. So when your investments grow at ten and prices only go up by three, your money is actually getting more powerful over time, not less. That's how you beat the system. Saving is important, it protects your money. But investing is what actually grows it. You need both working together. Start as early as you can, even with small amounts, because time is your biggest advantage.",
        "keywords": ["Inflation", "Finance", "Money", "Investing"],
    },
    {
        "title": "How $5 a Day Makes You a Millionaire",
        "search_queries": ["gold coins stacked", "coffee cup latte art", "stock chart growth upward", "calculator money desk", "calendar planner monthly", "luxury mansion pool", "compound interest graph", "person celebrating success", "investment portfolio screen", "snowball rolling bigger"],
        "slides": [
            {"text": "$5 a day\ncan make you\na millionaire", "duration": 5},
            {"text": "Thats your\nmorning coffee", "duration": 4},
            {"text": "Invest $5 daily\nat 10% returns", "duration": 5},
            {"text": "After 10 years\n$30,727", "duration": 5},
            {"text": "After 30 years\n$339,073", "duration": 5},
            {"text": "After 40 years\n$1,062,000", "duration": 5},
            {"text": "The secret?\nCompound interest", "duration": 4},
            {"text": "Your interest\nearns its own\ninterest", "duration": 5},
            {"text": "It snowballs\nbigger and bigger\nover time", "duration": 5},
            {"text": "Every day you wait\ncosts you thousands\nStart today", "duration": 6},
        ],
        "voiceover": "Five dollars a day can literally make you a millionaire. And that's not some motivational nonsense, that's actual math. Five dollars is your morning coffee. If you invest five dollars every single day into an index fund that averages ten percent returns per year, after ten years you'd have over thirty thousand dollars. After thirty years, three hundred thirty nine thousand. And after forty years, over one million dollars. From just five bucks a day. The secret behind this is compound interest. Your money earns returns, and then those returns earn their own returns. It snowballs. It starts slow, but after twenty years it explodes. The curve goes almost straight up. Here's the part that should scare you though. Every single day you wait to start costs you thousands of dollars in the long run. A twenty year old who invests five dollars a day will have three times more money at retirement than a thirty year old doing the exact same thing. Start today. Not next week. Not next month. Today.",
        "keywords": ["Compound Interest", "Investing", "Millionaire"],
    },
    {
        "title": "Bad Credit Costs You $100,000",
        "search_queries": ["credit card close up", "house exterior real estate", "bank building tall", "person stressed bills", "money stack hundred", "credit score phone screen", "person paying bills on time", "old credit cards wallet", "happy homeowner keys", "interest rate comparison"],
        "slides": [
            {"text": "Bad credit\ncosts you\n$100,000", "duration": 5},
            {"text": "On a $300K\nmortgage", "duration": 4},
            {"text": "Score above 740\nyou pay 6.5%", "duration": 5},
            {"text": "Score below 580\nyou pay 9.5%", "duration": 5},
            {"text": "Thats $100,000\nextra in interest\nover 30 years", "duration": 5},
            {"text": "How to fix it?\n3 simple rules", "duration": 4},
            {"text": "Rule 1\nAlways pay\non time even\nthe minimum", "duration": 5},
            {"text": "Rule 2\nKeep balances\nbelow 30% of\nyour limit", "duration": 5},
            {"text": "Rule 3\nNever close\nyour oldest card\nit helps history", "duration": 6},
            {"text": "Your credit score\nis your financial\nreputation\nProtect it", "duration": 6},
        ],
        "voiceover": "Bad credit doesn't just hurt your pride. It costs you real money. We're talking a hundred thousand dollars or more over your lifetime. Here's exactly how. When you apply for a three hundred thousand dollar mortgage, a credit score above seven forty gets you six point five percent interest. But a score below five eighty? You're looking at nine point five percent or higher. Over thirty years, that three percent difference adds up to over a hundred thousand dollars in extra interest. You're paying for the exact same house, just way more of it. So how do you fix your credit? Three simple rules. Rule one, always pay on time, even if it's just the minimum payment. Payment history is thirty five percent of your score. Rule two, keep your credit card balances below thirty percent of your limit. If your limit is a thousand, never carry more than three hundred. Rule three, never close your oldest credit card. The length of your credit history matters. Your credit score is your financial reputation. It follows you everywhere. Protect it like your life depends on it, because financially, it does.",
        "keywords": ["Credit Score", "Finance", "Mortgage", "Money"],
    },
    {
        "title": "The 50/30/20 Rule Changed My Life",
        "search_queries": ["paycheck salary money", "rent apartment building", "grocery shopping cart", "shopping bags colorful", "restaurant eating out", "piggy bank savings gold", "automatic bank transfer", "wealthy person confident", "financial freedom beach", "budget planner notebook"],
        "slides": [
            {"text": "This budget rule\nchanged my life", "duration": 5},
            {"text": "Take your\npaycheck\nany amount works", "duration": 5},
            {"text": "50% goes to needs\nrent food bills\ntransportation", "duration": 5},
            {"text": "30% goes to wants\nfun shopping\neating out", "duration": 5},
            {"text": "20% goes straight\nto savings\nand investing", "duration": 5},
            {"text": "The key?\nPay savings FIRST\nnot last", "duration": 5},
            {"text": "Automate it\nthe day you\nget paid", "duration": 5},
            {"text": "You will adjust\nto spending less\nwithin one month", "duration": 5},
            {"text": "Most millionaires\nstarted with\nthis exact rule", "duration": 5},
            {"text": "No fancy apps needed\nJust 3 numbers\n50 30 20", "duration": 5},
        ],
        "voiceover": "This budget rule literally changed my entire financial life and it can change yours too. Take your paycheck, any amount works, it doesn't matter how much you make. Fifty percent goes to needs. That's rent, food, bills, and transportation. The stuff you have to pay no matter what. Thirty percent goes to wants. Fun stuff, shopping, eating out, entertainment. Yes you're allowed to enjoy your money. And twenty percent goes straight to savings and investing. Here's the key though, and most people get this wrong. Pay your savings first, not last. The second your paycheck hits your account, move twenty percent into savings automatically. Set it up so you never even see that money. You will adjust to spending less within about one month, I promise. It feels tight at first but then it becomes completely normal. Most millionaires didn't get rich with complicated strategies. They started with this exact simple rule. No fancy budgeting apps needed. Just three numbers. Fifty. Thirty. Twenty. That's the entire system.",
        "keywords": ["Budgeting", "50/30/20", "Personal Finance"],
    },
    {
        "title": "Stocks vs Bonds Explained",
        "search_queries": ["stock market trading screen", "business office building", "handshake business deal", "roller coaster ride", "calm ocean sunset", "young person investing phone", "elderly couple retirement", "diversified portfolio chart", "balance scale golden", "risk reward sign"],
        "slides": [
            {"text": "Stocks vs Bonds\nfinally explained", "duration": 5},
            {"text": "A stock means\nyou OWN a piece\nof a company", "duration": 5},
            {"text": "If it grows\nyour money grows\nIf it tanks you lose", "duration": 5},
            {"text": "Stocks average\n10% per year\nbut its a bumpy ride", "duration": 5},
            {"text": "A bond means\nyou LEND money\nto a government\nor company", "duration": 5},
            {"text": "They pay you\nback with interest\nsteady and safe", "duration": 5},
            {"text": "Bonds average\n4-5% per year\nmuch smoother ride", "duration": 5},
            {"text": "Best strategy?\nMix both", "duration": 4},
            {"text": "Young? 80% stocks\n20% bonds\nYou have time\nto recover", "duration": 6},
            {"text": "Older? Flip it\nMore bonds\nfor stability", "duration": 5},
        ],
        "voiceover": "Stocks versus bonds, finally explained so anyone can understand. When you buy a stock, you own a tiny piece of a real company. If that company grows and makes money, your investment grows too. But if it tanks, you lose money. Stocks have averaged about ten percent per year historically, but it's a bumpy ride with lots of ups and downs. A bond is completely different. When you buy a bond, you're lending money to a government or a company. They promise to pay you back over time with interest. It's steady and predictable. Bonds average about four to five percent per year, much smoother than stocks but lower returns. So what's the best strategy? Mix both. If you're young, go about eighty percent stocks and twenty percent bonds. You have decades to recover from any crashes. The ups and downs don't matter when you're not retiring for thirty years. As you get older, flip it. More bonds for stability since you'll need that money sooner. This is called asset allocation, and it's how the smartest investors manage risk.",
        "keywords": ["Stocks", "Bonds", "Investing", "Asset Allocation"],
    },
    {
        "title": "No Emergency Fund? Heres Why You Need One",
        "search_queries": ["warning sign red", "broken car roadside", "credit card payment terminal", "money burning fire", "glass jar coins savings", "person opening savings account", "safety net trapeze", "bank account phone app", "relieved person smiling", "high yield savings screen"],
        "slides": [
            {"text": "No emergency fund?\nHeres what happens", "duration": 5},
            {"text": "Your car\nbreaks down\n$800 repair", "duration": 5},
            {"text": "No savings?\nCredit card at\n24% interest", "duration": 5},
            {"text": "That $800\njust became $1,100", "duration": 5},
            {"text": "An emergency fund\nprevents this\ncompletely", "duration": 5},
            {"text": "Save 3 to 6 months\nof expenses", "duration": 5},
            {"text": "Put it in a high\nyield savings account\n4-5% interest", "duration": 5},
            {"text": "Your money earns\nmoney while it\nprotects you", "duration": 5},
            {"text": "Start with just $500\nthen add $50\nevery paycheck", "duration": 5},
            {"text": "In one year youll\nhave a real\nsafety net", "duration": 5},
        ],
        "voiceover": "No emergency fund? Let me show you exactly what happens. Your car breaks down tomorrow. Eight hundred dollar repair bill. Without any savings, that goes straight onto a credit card at twenty four percent interest. That eight hundred dollar problem just became eleven hundred dollars by the time you pay it off. And that's just one emergency. An emergency fund prevents this completely. It's your financial safety net. The goal is to save three to six months of your living expenses. Put it in a high yield savings account where it earns four to five percent interest. That means your money is earning money for you while it sits there protecting you. You don't need to build it overnight. Start with just five hundred dollars. Then add fifty dollars from every single paycheck. In about one year you'll have a solid safety net that can handle a car repair, a medical bill, or even a job loss without destroying your finances. The peace of mind alone is worth it. No more stress about unexpected bills.",
        "keywords": ["Emergency Fund", "Savings", "High Yield Savings"],
    },
    {
        "title": "What Happens in a Recession",
        "search_queries": ["storm clouds dark sky", "empty office desks", "unemployment job search", "shopping cart empty store", "stock chart recovery green", "person looking at stocks phone", "investor buying stocks cheap", "economy growing city", "financial planning notebook", "history repeating pattern"],
        "slides": [
            {"text": "A recession\nis coming\nheres what happens", "duration": 5},
            {"text": "Companies make\nless money\nand start cutting", "duration": 5},
            {"text": "They lay off\nworkers to\nsave money", "duration": 5},
            {"text": "People spend less\nbecause they have\nless income", "duration": 5},
            {"text": "Which means companies\nmake even less\nThe cycle repeats", "duration": 5},
            {"text": "But every single\nrecession in history\nhas ended", "duration": 5},
            {"text": "The average recession\nlasts 10 months\nnot forever", "duration": 5},
            {"text": "The worst move\nis panic selling\nyou lock in losses", "duration": 5},
            {"text": "The best move\nis keep investing\nStocks are on sale", "duration": 5},
            {"text": "Those who invest\nduring recessions\nget rich in\nthe recovery", "duration": 6},
        ],
        "voiceover": "A recession might be coming. Here's exactly what happens and what you should do. Companies start making less money, so they cut costs. That means layoffs. Workers lose their jobs, so they have less income and spend less. When people spend less, companies make even less money. It's a downward cycle that feeds on itself. Sounds scary, right? But here's what nobody tells you during a recession. Every single recession in history has ended. Every one. The average recession only lasts about ten months. Not years, not decades, ten months. The absolute worst move you can make is panic selling your investments. When you sell during a crash, you lock in your losses permanently. The best move is to keep investing consistently. Stocks are literally on sale during a recession. You're buying the same companies at a discount. Those who have the courage to keep investing during recessions are the ones who get wealthy during the recovery. The stock market has recovered from every single crash and gone on to reach new highs. History proves this over and over again.",
        "keywords": ["Recession", "Economy", "Bear Market", "Investing"],
    },
    {
        "title": "Rich People Buy Assets Not Stuff",
        "search_queries": ["luxury mansion aerial", "wallet money cash", "money flying away wind", "sports car expensive", "rental apartment building", "dividend stock screen", "passive income laptop", "wealthy lifestyle freedom", "real estate investment sign", "financial freedom sunset"],
        "slides": [
            {"text": "Rich people buy\nassets not stuff", "duration": 5},
            {"text": "An asset puts\nmoney IN\nyour pocket", "duration": 5},
            {"text": "A liability takes\nmoney OUT\nof your pocket", "duration": 5},
            {"text": "Your fancy car?\nThats a liability", "duration": 5},
            {"text": "Insurance gas\ndepreciation\nit costs you\nevery month", "duration": 5},
            {"text": "A rental property\nthat earns income?\nThats an asset", "duration": 5},
            {"text": "Dividend stocks\nthat pay you\nevery quarter?\nAsset", "duration": 5},
            {"text": "A business that\nruns without you?\nAsset", "duration": 5},
            {"text": "Buy assets first\nthen let assets\npay for your stuff", "duration": 5},
            {"text": "Thats the\nmillionaire formula\nAssets before\nlifestyle", "duration": 5},
        ],
        "voiceover": "Rich people don't buy stuff. They buy assets. And that one difference is what separates the wealthy from everyone else. Here's the distinction. An asset puts money into your pocket. A liability takes money out of your pocket. Your fancy car? That's a liability. Insurance, gas, maintenance, depreciation. It costs you money every single month and it's worth less every year. But a rental property that brings in more rent than it costs you? That's an asset. Dividend stocks that pay you cash every three months just for holding them? That's an asset. A business that generates income even when you're not working? That's an asset. The secret of wealthy people is simple. They buy assets first. Then they let those assets generate income. Then they use that income to pay for their lifestyle. They don't buy the luxury car until their investments are paying for it. Assets before lifestyle. That's the millionaire formula. Start small. Buy your first index fund. Let it grow. Then buy more. Let your money work harder than you do.",
        "keywords": ["Assets", "Liabilities", "Wealth Building"],
    },
    {
        "title": "What Is the S&P 500",
        "search_queries": ["wall street sign new york", "stock market trading floor", "apple google amazon logos", "chart line going up green", "person investing laptop", "warren buffett portrait", "index fund vanguard screen", "dollar bills growing plant", "retirement savings graph", "phone brokerage app"],
        "slides": [
            {"text": "What is the\nS&P 500?", "duration": 5},
            {"text": "Its the top 500\ncompanies in\nAmerica combined", "duration": 5},
            {"text": "Apple Google\nAmazon Tesla\nMicrosoft all in one", "duration": 5},
            {"text": "You buy 1 fund\nyou own a piece\nof all 500", "duration": 5},
            {"text": "Average return\n10% per year\nfor over 100 years", "duration": 5},
            {"text": "It survived\nthe Great Depression\n2008 crash and Covid", "duration": 6},
            {"text": "Warren Buffett says\nmost people should\njust buy this", "duration": 5},
            {"text": "How? Open a\nbrokerage account\nbuy VOO or SPY", "duration": 5},
            {"text": "Start with $50 or\n$100 it doesnt matter\njust start", "duration": 5},
            {"text": "A hundred today\ncould be $1,745\nin 30 years\njust sitting there", "duration": 6},
        ],
        "voiceover": "What is the S and P five hundred and why does everyone keep talking about it? It's the top five hundred companies in America combined into one single investment. Apple, Google, Amazon, Tesla, Microsoft, all of them in one place. When you buy one S and P five hundred fund, you instantly own a tiny piece of all five hundred companies. The average return has been about ten percent per year for over a hundred years. It has survived the Great Depression, the two thousand eight financial crisis, and the Covid crash. Every single time it recovered and went higher. Even Warren Buffett, the greatest investor alive, says most people should just buy an S and P five hundred index fund and never touch it. How do you actually buy it? Open a free brokerage account at Fidelity, Schwab, or Vanguard. Then buy a fund called V O O or S P Y. Those track the S and P five hundred. You can start with fifty or a hundred dollars, it doesn't matter. Just start. A hundred dollars invested today could be worth over seventeen hundred in thirty years just sitting there growing on its own.",
        "keywords": ["S&P 500", "Index Fund", "VOO", "Investing"],
    },
    {
        "title": "How Taxes Actually Work",
        "search_queries": ["tax form documents", "paycheck stub closeup", "money divided portions", "calculator tax season", "staircase steps climbing", "person happy refund check", "income bracket chart", "dollar bills sorted piles", "thumbs up celebration", "myth busted sign"],
        "slides": [
            {"text": "You DONT pay 30%\non everything\nyou earn", "duration": 5},
            {"text": "Thats the biggest\nmyth in finance", "duration": 4},
            {"text": "Taxes work\nin brackets\nlike a staircase", "duration": 5},
            {"text": "First $11,000\nyou earn?\nOnly 10% tax", "duration": 5},
            {"text": "Next $34,000\ntaxed at 12%", "duration": 5},
            {"text": "$45K to $95K\ntaxed at 22%", "duration": 5},
            {"text": "Only money ABOVE\neach step gets\nthe higher rate", "duration": 5},
            {"text": "Earn $50K?\nYou pay about\n$6,600 in tax\nnot $11,000", "duration": 6},
            {"text": "Your effective rate\nis about 13%\nnot 22%", "duration": 5},
            {"text": "A raise will NEVER\nmake you lose money\nThats a myth", "duration": 5},
        ],
        "voiceover": "You do not pay thirty percent on everything you earn. That is the biggest myth in finance and it stops people from making more money. Here's how taxes actually work. They work in brackets, like a staircase. Each step has a different rate. The first eleven thousand dollars you earn is only taxed at ten percent. The next thirty four thousand is taxed at twelve percent. Money between forty five and ninety five thousand is taxed at twenty two percent. The key is that only the money above each step gets the higher rate. Not all of your income. So if you earn fifty thousand dollars, you don't pay twenty two percent on all of it. You pay ten percent on the first chunk, twelve on the next, and twenty two only on the last portion. Your actual total tax is about sixty six hundred, which is an effective rate of about thirteen percent, not twenty two. A raise will never make you lose money overall. That is a complete myth. Never turn down more money because you think you'll lose it to taxes. You won't. You always keep more than you give.",
        "keywords": ["Taxes", "Tax Brackets", "Income Tax"],
    },
    {
        "title": "Debt Snowball vs Avalanche",
        "search_queries": ["snowball rolling downhill", "credit card debt pile", "list notebook planning", "celebration confetti win", "avalanche mountain snow", "debt free happy person", "calculator paying bills", "person crossing finish line", "weight lifted shoulders", "money freedom chains broken"],
        "slides": [
            {"text": "Got debt?\n2 proven ways\nto destroy it", "duration": 5},
            {"text": "Method 1\nDebt Snowball", "duration": 4},
            {"text": "List all debts\nsmallest to largest\nIgnore interest rates", "duration": 5},
            {"text": "Pay off the\nsmallest one first\nget a quick win", "duration": 5},
            {"text": "Then roll that\npayment into\nthe next debt", "duration": 5},
            {"text": "Method 2\nDebt Avalanche", "duration": 4},
            {"text": "Pay off the\nhighest interest\nrate first", "duration": 5},
            {"text": "You save the\nmost money\non interest", "duration": 5},
            {"text": "Snowball wins\non motivation\nAvalanche wins\non math", "duration": 6},
            {"text": "Pick one today\nand stick with it\nBoth work\nconsistency wins", "duration": 6},
        ],
        "voiceover": "Got debt? There are two proven ways to destroy it. Method one is the debt snowball. List all your debts from smallest balance to largest. Ignore the interest rates completely. Pay the minimum on everything except the smallest debt. Throw every extra dollar at that smallest one. When it's paid off, take that entire payment and roll it into the next smallest debt. You get quick wins that keep you motivated. Method two is the debt avalanche. Instead of smallest balance, you target the debt with the highest interest rate first. This saves you the most money on interest over time because you're eliminating the most expensive debt first. Snowball wins on motivation. When you see debts disappearing quickly, it feels amazing and keeps you going. Avalanche wins on pure math. You pay less total interest. Honestly, both methods work. The best one is whichever one you'll actually stick with. Pick one today and commit to it. Consistency beats perfection every time. The worst thing you can do is nothing. Start attacking your debt this week.",
        "keywords": ["Debt Snowball", "Debt Avalanche", "Debt Free"],
    },
    {
        "title": "Why You Need a Roth IRA",
        "search_queries": ["retirement elderly happy", "piggy bank growing gold", "tax documents money", "young person phone investing", "beach retirement sunset", "million dollars cash stack", "tax free stamp green", "brokerage account screen", "couple retiring happy", "clock time growing money"],
        "slides": [
            {"text": "A Roth IRA is\nthe biggest\ncheat code\nin finance", "duration": 5},
            {"text": "You put in money\nyou already\npaid tax on", "duration": 5},
            {"text": "It grows\ncompletely\ntax FREE forever", "duration": 5},
            {"text": "You withdraw it\ntax FREE\nin retirement", "duration": 5},
            {"text": "The government gets\nNOTHING when\nyou take it out", "duration": 5},
            {"text": "Max contribution\n$7,000 per year", "duration": 5},
            {"text": "Start at 18\nput in $7K yearly", "duration": 5},
            {"text": "By 65 you could\nhave $1.9 million\nTAX FREE", "duration": 5},
            {"text": "Open one at\nFidelity Schwab\nor Vanguard\nits free", "duration": 5},
            {"text": "10 minutes to set up\nA lifetime of\ntax free wealth", "duration": 5},
        ],
        "voiceover": "A Roth IRA is the single biggest cheat code in personal finance. Let me explain exactly how it works. You put in money that you've already paid taxes on. Normal after tax dollars from your paycheck. Then that money grows completely tax free. Forever. And here's the best part. When you retire and take the money out, you pay zero taxes on it. Nothing. The government doesn't get a single penny of your gains. You can contribute up to seven thousand dollars per year. If you start at eighteen and put in seven thousand every year into an S and P five hundred index fund, by sixty five you could have one point nine million dollars. Completely tax free. Not a dollar of that goes to taxes. How do you open one? Go to Fidelity, Schwab, or Vanguard online. It's completely free to open. Pick an S and P five hundred index fund. Set up automatic monthly contributions. The entire process takes about ten minutes. Ten minutes of setup for a lifetime of tax free wealth. If you're under fifty nine and a half, there's no excuse not to have one. Open it today.",
        "keywords": ["Roth IRA", "Retirement", "Tax Free Investing"],
    },
    {
        "title": "Dollar Cost Averaging Explained",
        "search_queries": ["stock chart up and down zigzag", "person buying phone app", "market crash red screen", "shopping sale discount signs", "calendar monthly reminder", "portfolio growth chart long", "autopilot airplane cockpit", "consistent routine morning", "long road highway distance", "tortoise winning race"],
        "slides": [
            {"text": "Stop trying to\ntime the market\nNobody can do it", "duration": 5},
            {"text": "Not even experts\nhedge funds or\nTV analysts", "duration": 5},
            {"text": "Instead invest\nthe same amount\nevery single month", "duration": 5},
            {"text": "Market goes up?\nYou buy\nfewer shares", "duration": 5},
            {"text": "Market crashes?\nYou buy MORE\ncheaper shares", "duration": 5},
            {"text": "Over time your\naverage cost\nevens out", "duration": 5},
            {"text": "This is called\nDollar Cost\nAveraging", "duration": 5},
            {"text": "Set up automatic\ninvesting and\nforget about it", "duration": 5},
            {"text": "Check it once a year\nnot every day", "duration": 5},
            {"text": "Slow and steady\nwins the\nwealth race", "duration": 5},
        ],
        "voiceover": "Stop trying to time the stock market. Nobody can do it consistently. Not hedge fund managers, not TV analysts, not your friend who says he always buys at the bottom. Nobody. Instead, do what actually works. Invest the exact same amount of money every single month, no matter what the market is doing. When the market goes up, your money buys fewer shares because they're more expensive. When the market crashes, your money buys more shares because they're cheaper. Over time, your average cost per share evens out. This strategy is called dollar cost averaging. It removes all emotion from investing. No more panicking during crashes, no more guessing when to buy. Set up automatic monthly investing into an index fund and literally forget about it. Let it run on autopilot. Check your portfolio maybe once a year, not every single day. Studies show that investors who check their portfolio daily actually earn less than those who check once a year because they panic and make bad decisions. Slow and steady wins the wealth race. Consistency beats timing every single time.",
        "keywords": ["Dollar Cost Averaging", "Investing Strategy", "Passive Investing"],
    },
    {
        "title": "How Banks Make Money From You",
        "search_queries": ["bank building exterior grand", "credit card swiping machine", "loan documents signing pen", "interest rate percentage board", "atm machine withdrawing", "person reading fine print", "high yield savings phone", "online bank neon sign", "person switching banks happy", "money growing comparison"],
        "slides": [
            {"text": "Banks make money\nFROM you\nheres exactly how", "duration": 5},
            {"text": "You deposit $1,000\nthey pay you\n0.01% interest", "duration": 5},
            {"text": "Thats 10 cents\nper year\nfor your money", "duration": 5},
            {"text": "They lend YOUR\nmoney out to\nothers at 7%", "duration": 5},
            {"text": "They keep the\ndifference as\nprofit", "duration": 4},
            {"text": "Plus overdraft fees\nlate fees and\nhidden charges", "duration": 5},
            {"text": "Banks made $200\nbillion in fees\nlast year alone", "duration": 5},
            {"text": "How to fight back?\nSwitch to a high\nyield savings account", "duration": 5},
            {"text": "Online banks pay\n4-5% interest\nnot 0.01%", "duration": 5},
            {"text": "Same FDIC protection\n400x more interest\ngoing to YOU", "duration": 6},
        ],
        "voiceover": "Banks make money from you and most people have no idea how much. Here's the full picture. You deposit a thousand dollars. They pay you zero point zero one percent interest. That's ten cents per year for lending them your money. Then they take your money and lend it out to other people at seven percent interest. They keep the entire difference as profit. On top of that they charge overdraft fees, late payment fees, monthly maintenance fees, and dozens of hidden charges buried in the fine print. American banks made over two hundred billion dollars in fees last year alone. Two hundred billion from regular people like you and me. So how do you fight back? Switch to a high yield savings account at an online bank. Names like Marcus, Ally, or Wealthfront. They pay four to five percent interest on your savings instead of zero point zero one. That's literally four hundred times more interest going into your pocket. They have the same FDIC insurance as big banks, meaning your money is equally protected up to two hundred fifty thousand dollars. Same safety, way more money for you. Make the switch.",
        "keywords": ["Banks", "High Yield Savings", "Fees", "Interest"],
    },
    {
        "title": "Why Renting Is Not Throwing Money Away",
        "search_queries": ["apartment building modern city", "house with sold sign", "money pit hole ground", "repair tools maintenance work", "mortgage calculator screen", "person moving boxes heavy", "home inspection damage found", "renter relaxing couch happy", "financial calculator planning", "flexibility freedom road"],
        "slides": [
            {"text": "Renting is NOT\nthrowing money away\nheres the truth", "duration": 5},
            {"text": "A $400K house costs\n$2,800 per month\njust in mortgage", "duration": 5},
            {"text": "Add property taxes\ninsurance repairs\nand HOA fees", "duration": 5},
            {"text": "Real cost?\n$3,500+ per month\nnot $2,800", "duration": 5},
            {"text": "First 7 years\nmost of your\npayment is INTEREST", "duration": 5},
            {"text": "Youre paying\nthe bank\nnot building equity", "duration": 5},
            {"text": "Renting gives you\nflexibility and\nzero surprise costs", "duration": 5},
            {"text": "Invest the difference\nbetween rent and\nownership costs", "duration": 5},
            {"text": "Only buy when\nyoull stay 5+ years\nand the math\nactually works", "duration": 6},
            {"text": "There is no shame\nin renting\nIts a smart\nfinancial choice", "duration": 5},
        ],
        "voiceover": "Everyone says renting is throwing money away. That's completely wrong. Let me show you the real math. A four hundred thousand dollar house costs about twenty eight hundred a month in mortgage payments alone. But that's not the real cost. Add property taxes, homeowners insurance, maintenance, repairs, and HOA fees. You're actually paying thirty five hundred or more per month. And here's the part nobody mentions. In the first seven years of your mortgage, most of your monthly payment goes to interest, not equity. You're basically paying the bank, not building wealth. Meanwhile renting gives you flexibility to move for better jobs, zero surprise repair costs, and no risk of your home losing value. If rent is cheaper than owning in your area, take the difference and invest it in index funds. You might actually build more wealth as a renter than an owner. Only buy a house when you plan to stay at least five years and the numbers actually make sense for your income. There is absolutely no shame in renting. It's often the smarter financial choice.",
        "keywords": ["Renting vs Buying", "Real Estate", "Housing"],
    },
    {
        "title": "Pay Yourself First",
        "search_queries": ["paycheck direct deposit screen", "savings account phone app", "bills stack pile stress", "empty wallet broke sad", "money growing plant small", "automatic bank transfer setup", "wealthy confident person suit", "financial freedom sunset walk", "piggy bank overflowing coins", "person budget planning calm"],
        "slides": [
            {"text": "The number 1 rule\nof building wealth", "duration": 5},
            {"text": "Pay yourself\nFIRST\nbefore anything else", "duration": 5},
            {"text": "Most people pay\nbills first then\nsave whats left", "duration": 5},
            {"text": "But theres never\nanything left\nand you know it", "duration": 5},
            {"text": "Flip it completely", "duration": 3},
            {"text": "The second your\npaycheck hits\nsave 20%\nimmediately", "duration": 5},
            {"text": "Set up automatic\ntransfer so you\nnever see it", "duration": 5},
            {"text": "After 2 weeks\nyou wont even\nnotice its gone", "duration": 5},
            {"text": "You adjust your\nspending naturally\nwithout trying", "duration": 5},
            {"text": "Every millionaire\ndoes this\nIts not about income\nits about the habit", "duration": 6},
        ],
        "voiceover": "The number one rule of building wealth. Pay yourself first, before you pay anyone or anything else. Most people do it backwards. They pay their rent, their bills, buy groceries, maybe eat out a few times, and then try to save whatever is left at the end of the month. But there's never anything left. You know it, I know it. Flip it completely. The second your paycheck hits your bank account, automatically move twenty percent into a separate savings or investment account. Set up the automatic transfer so you never even see that money. It goes away before you can spend it. Here's what happens next. After about two weeks, you completely forget about it. You adjust your spending naturally without even trying. You find ways to spend less because you have less available. It doesn't feel like sacrifice, it just becomes your new normal. Every single millionaire does this. It doesn't matter if they make fifty thousand or five hundred thousand a year. They all pay themselves first. It's not about how much you earn. It's about building the habit of keeping what you earn.",
        "keywords": ["Pay Yourself First", "Savings Habit", "Wealth Building"],
    },
    {
        "title": "What Is an ETF and Why Everyone Buys Them",
        "search_queries": ["stock exchange building floor", "shopping basket colorful variety", "phone investing app screen", "diversified food plate healthy", "low price tag clearance", "graph growing steadily upward", "person relaxing hammock beach", "index fund comparison chart", "piggy bank gold coins shiny", "beginner investor young"],
        "slides": [
            {"text": "What is an ETF\nand why does\neveryone buy them?", "duration": 5},
            {"text": "ETF stands for\nExchange Traded Fund", "duration": 4},
            {"text": "Think of it like\na basket holding\nhundreds of stocks", "duration": 5},
            {"text": "Instead of picking\none company\nyou own hundreds\nat once", "duration": 5},
            {"text": "If one company\nfails the rest\nkeep you safe", "duration": 5},
            {"text": "ETFs trade like\nregular stocks\nbuy and sell anytime", "duration": 5},
            {"text": "Fees are tiny\nusually under 0.1%\nper year", "duration": 5},
            {"text": "Compare that to\nmutual funds\ncharging 1-2%", "duration": 5},
            {"text": "Popular ETFs?\nVOO SPY QQQ\nstart with $10", "duration": 5},
            {"text": "Its the simplest\nsafest way for\nbeginners to\nstart investing", "duration": 6},
        ],
        "voiceover": "What is an E T F and why does literally everyone buy them? E T F stands for exchange traded fund. Think of it like a shopping basket that holds hundreds of different stocks inside it. Instead of picking one single company and hoping it does well, you own hundreds of companies all at once. If one company completely fails, the rest of the basket keeps your money safe. That's the power of diversification. E T Fs trade just like regular stocks on the stock market. You can buy and sell them anytime during market hours with just a few taps on your phone. The fees are incredibly low, usually under zero point one percent per year. Compare that to traditional mutual funds that charge one to two percent. That difference saves you tens of thousands over your lifetime. The most popular E T Fs are V O O and S P Y which track the S and P five hundred, and Q Q Q which tracks the top tech companies. You can start with as little as ten dollars. It's honestly the simplest, safest, and cheapest way for beginners to start investing. Open a free brokerage account and buy your first E T F today.",
        "keywords": ["ETF", "Exchange Traded Fund", "Index Investing"],
    },
    {
        "title": "How Credit Cards Actually Work",
        "search_queries": ["credit card close up shiny gold", "shopping store checkout counter", "calendar payment due date", "money growing compound interest", "person paying phone tap", "debt trap chain heavy", "credit score screen green", "zero balance bank statement", "smart shopper rewards points", "financial discipline planner"],
        "slides": [
            {"text": "How credit cards\nactually work\nno one teaches this", "duration": 5},
            {"text": "The bank gives\nyou a spending\nlimit", "duration": 5},
            {"text": "You buy stuff now\nand pay for it\nlater", "duration": 5},
            {"text": "Pay the FULL\nbalance each month?\nZero interest charged", "duration": 5},
            {"text": "Its literally\nfree money plus\ncashback and points", "duration": 5},
            {"text": "Only pay the\nminimum amount?", "duration": 4},
            {"text": "They charge 20-30%\ninterest on\neverything left", "duration": 5},
            {"text": "$1,000 balance\nat 25% interest\n= $250 per year\njust in interest", "duration": 6},
            {"text": "The rule is simple\nNever spend more\nthan you can\npay off monthly", "duration": 6},
            {"text": "Use cards for\nrewards not\nfor borrowing\nThats the secret", "duration": 5},
        ],
        "voiceover": "How do credit cards actually work? Nobody teaches this in school. The bank gives you a credit limit, that's the max you can spend. You buy things now and pay for them later. Here's where it gets critical. If you pay the full balance every single month before the due date, you are charged zero interest. Nothing. The bank is giving you a free loan for thirty days. Some cards even give you one to five percent cashback or travel points on top of that. Free money. But if you only pay the minimum amount, they charge you twenty to thirty percent interest on everything that's left. A thousand dollar balance at twenty five percent interest costs you two hundred fifty dollars per year just in interest charges. That balance barely goes down because your minimum payment mostly covers interest, not the actual debt. The rule is dead simple. Never put something on a credit card unless you can pay it off in full that same month. Use credit cards for the rewards and cashback, never for borrowing money you don't have. That's the secret to using credit cards like rich people do.",
        "keywords": ["Credit Cards", "Interest Rates", "Cashback"],
    },
    {
        "title": "What Is a 401k Retirement Plan",
        "search_queries": ["office worker desk computer", "paycheck stub detailed", "employer handshake deal", "money doubling growing", "tax form documents pile", "retirement couple beach happy", "compound growth chart exponential", "birthday cake candles many", "golden nest egg basket", "free money sign neon"],
        "slides": [
            {"text": "What is a 401k?\nLet me explain it\nsimply", "duration": 5},
            {"text": "Its a retirement\nsavings account\nthrough your job", "duration": 5},
            {"text": "Money comes out\nof your paycheck\nBEFORE taxes", "duration": 5},
            {"text": "Earn $50K?\nPut in $5K?\nYou only pay tax\non $45K", "duration": 5},
            {"text": "You save money\non taxes\nright now today", "duration": 5},
            {"text": "Many employers\nMATCH what you\nput in", "duration": 5},
            {"text": "You put in $100\nthey put in $100\nthats DOUBLE", "duration": 5},
            {"text": "Its literally free\nmoney from your boss", "duration": 5},
            {"text": "Always contribute\nenough to get\nthe full match", "duration": 5},
            {"text": "Saying no to\nthe match is like\nburning free money\nDont do it", "duration": 5},
        ],
        "voiceover": "What is a four oh one K? Let me explain it simply so you actually understand it. It's a retirement savings account that you get through your employer. Money comes out of your paycheck before taxes are calculated. So if you earn fifty thousand and put five thousand into your four oh one K, you only pay income tax on forty five thousand. You literally save money on taxes right now, today. But here's the absolute best part. Many employers will match what you contribute. You put in a hundred dollars, they put in a hundred dollars. Your money instantly doubles before it even starts growing. That is free money from your boss. The most important rule is always contribute at least enough to get the full employer match. If they match up to six percent of your salary, make sure you put in at least six percent. Saying no to the employer match is exactly like your boss handing you free money and you saying no thanks, I don't want it. Nobody would do that with cash, but millions of people do it with their four oh one K every single day. Don't be one of them.",
        "keywords": ["401k", "Retirement Plan", "Employer Match"],
    },
    {
        "title": "Why You Should Never Lease a Car",
        "search_queries": ["car dealership shiny lot", "car keys handover deal", "monthly payment bill stack", "car depreciation value drop", "person driving used car", "used car reliable lot", "money going down drain", "calculator car payment loan", "person buying used car happy", "financial mistake warning"],
        "slides": [
            {"text": "Never lease a car\nand heres exactly\nwhy", "duration": 5},
            {"text": "A lease is just\nlong term renting\nwith extra rules", "duration": 5},
            {"text": "You pay $400/month\nfor 3 years\nthats $14,400 total", "duration": 5},
            {"text": "After 3 years\nyou own absolutely\nNOTHING", "duration": 5},
            {"text": "You hand the\ncar back and\nstart over", "duration": 5},
            {"text": "Plus mileage limits\nwear charges and\nhidden fees", "duration": 5},
            {"text": "Go over the\nmileage limit?\nPay 25 cents\nper extra mile", "duration": 5},
            {"text": "Instead buy a\nreliable used car\n2-3 years old", "duration": 5},
            {"text": "Pay it off then\ndrive it for\n7-10 more years\npayment free", "duration": 5},
            {"text": "You save $30,000+\ncompared to leasing\ntwice over 10 years", "duration": 5},
        ],
        "voiceover": "Never lease a car. Here's exactly why it's one of the worst financial decisions you can make. A lease is basically long term renting with extra rules and restrictions. You pay about four hundred dollars a month for three years. That's fourteen thousand four hundred dollars total. And after those three years, you own absolutely nothing. You hand the car right back to the dealer and start the whole process over again. On top of the monthly payments, there are mileage limits, usually around twelve thousand miles per year. Go over? You pay twenty five cents for every extra mile. Plus wear and tear charges for any scratches or dents. Instead, here's what smart people do. Buy a reliable used car that's two to three years old. Someone else already took the biggest depreciation hit. Pay it off in three to four years, then drive it for seven to ten more years with zero car payments. Over ten years, you save over thirty thousand dollars compared to leasing twice. That's thirty thousand extra dollars you could invest and grow into real wealth.",
        "keywords": ["Car Lease", "Used Car", "Saving Money"],
    },
    {
        "title": "What Is Cryptocurrency Explained Simply",
        "search_queries": ["bitcoin coin gold shiny", "digital code screen matrix", "blockchain network connected", "bank building traditional old", "phone crypto trading app", "price chart volatile swings", "lock security digital strong", "person confused question mark", "wallet digital crypto screen", "risk warning sign red"],
        "slides": [
            {"text": "What is\ncryptocurrency?\nSimplest explanation", "duration": 5},
            {"text": "Its digital money\nthat lives only\non computers", "duration": 5},
            {"text": "No bank controls it\nNo government\ncan print more", "duration": 5},
            {"text": "Bitcoin was first\ncreated in 2009\nby an unknown person", "duration": 5},
            {"text": "Today there are\nthousands of\ncryptocurrencies", "duration": 4},
            {"text": "People buy hoping\nthe price goes up\nso they can sell\nfor profit", "duration": 5},
            {"text": "But crypto can drop\n50% in a single week\nIts extremely risky", "duration": 5},
            {"text": "Rule 1\nNever invest more\nthan you can\nafford to lose", "duration": 5},
            {"text": "Rule 2\nBuild your basics\nfirst emergency fund\nindex funds 401k", "duration": 6},
            {"text": "Crypto is dessert\nnot the main meal\nGet the basics\nright first", "duration": 6},
        ],
        "voiceover": "What is cryptocurrency in the simplest terms possible? It's digital money that exists only on computers. No bank controls it and no government can print more of it. It runs on a technology called blockchain, which is basically a public record that everyone can see but nobody can cheat. Bitcoin was the very first cryptocurrency, created in two thousand nine by an anonymous person or group. Today there are thousands of different cryptocurrencies. People buy crypto hoping the price goes up so they can sell it later for a profit. Some people have made fortunes. But here's what you need to know. Crypto can drop fifty percent in a single week. It's the most volatile and risky investment available. Rule one, never invest more than you can completely afford to lose. If you put in a thousand dollars, you should be okay with that becoming zero. Rule two, build your financial basics first. Emergency fund, index fund investments, four oh one K contributions. Get those set up and running before you even think about crypto. Crypto is the dessert, not the main meal. Get the fundamentals right first, then explore crypto with money you can afford to lose.",
        "keywords": ["Cryptocurrency", "Bitcoin", "Digital Currency"],
    },
    {
        "title": "How Insurance Works in 60 Seconds",
        "search_queries": ["umbrella protection rain storm", "car accident aftermath", "hospital emergency entrance", "insurance contract document", "group people community large", "house fire damage smoke", "monthly payment calendar check", "family safe protected home", "shield protection icon strong", "peace of mind relaxed"],
        "slides": [
            {"text": "How does insurance\nwork? Simplest\nexplanation ever", "duration": 5},
            {"text": "You pay a small\namount every month\ncalled a premium", "duration": 5},
            {"text": "Thousands of other\npeople pay the\nsame premium", "duration": 5},
            {"text": "All that money goes\ninto one giant pool", "duration": 4},
            {"text": "When something bad\nhappens to YOU\nthe pool covers it", "duration": 5},
            {"text": "Car crash? Pool pays\nHospital bill?\nPool pays", "duration": 5},
            {"text": "Youre trading\na small certain cost\nfor protection from\na huge one", "duration": 6},
            {"text": "The 4 types\nyou need", "duration": 4},
            {"text": "Health insurance\nAuto insurance\nRenters insurance\nLife insurance\nif you have family", "duration": 6},
            {"text": "One bad event\nwithout insurance\ncan put you in\ndebt for years", "duration": 5},
        ],
        "voiceover": "How does insurance actually work? Here's the simplest explanation ever. You pay a small amount every month. This is called your premium. Thousands of other people with the same insurance also pay their premiums. All of that money goes into one giant pool. When something bad happens to one person in the group, that pool pays for the expenses. Car crash? The pool covers the repair and medical bills. Hospital visit? The pool covers it. House fire? The pool pays to rebuild. You're essentially trading a small predictable cost for protection against a huge unexpected disaster. The four types of insurance you actually need are health insurance, this is non negotiable, one hospital visit without it can cost you hundreds of thousands. Auto insurance, required by law in most places. Renters or homeowners insurance, protects your stuff from theft, fire, and damage. And life insurance if you have a family that depends on your income. Skip the fancy extras insurance companies try to sell you. Just get these four basics. One bad event without insurance can put you in serious debt for years. It's not worth the risk.",
        "keywords": ["Insurance", "Health Insurance", "Financial Protection"],
    },
    {
        "title": "The Rule of 72 Will Blow Your Mind",
        "search_queries": ["calculator close up display", "number 72 large bold", "money doubling stacks coins", "clock time passing fast", "ten percent sign green", "investment growth chart steep", "mind blown surprised face", "compound interest curve graph", "golden egg nest growing", "albert einstein chalkboard"],
        "slides": [
            {"text": "The Rule of 72\nthe fastest math\ntrick in finance", "duration": 5},
            {"text": "It tells you exactly\nhow fast your\nmoney DOUBLES", "duration": 5},
            {"text": "Take 72 and\ndivide it by\nyour interest rate", "duration": 5},
            {"text": "Thats how many\nyears until your\nmoney doubles", "duration": 5},
            {"text": "Getting 10% returns?\n72 / 10 = 7.2 years\nto double", "duration": 5},
            {"text": "$10,000 becomes\n$20,000 in\njust 7 years", "duration": 5},
            {"text": "Then $40,000\nthen $80,000\nthen $160,000", "duration": 5},
            {"text": "8 doublings turns\n$10K into $2.5\nmillion", "duration": 5},
            {"text": "But at 1% savings\naccount? 72 / 1\n= 72 years to double", "duration": 6},
            {"text": "Where you put\nyour money matters\nmore than how much\nyou put in", "duration": 5},
        ],
        "voiceover": "The rule of seventy two is the fastest math trick in all of finance. It tells you exactly how fast your money doubles. Take the number seventy two and divide it by your annual interest rate. The answer is how many years until your money doubles. Getting ten percent returns in the stock market? Seventy two divided by ten equals seven point two years to double your money. So ten thousand dollars becomes twenty thousand in about seven years. Without you adding a single dollar. Then it doubles again to forty thousand, then eighty thousand, then one hundred sixty thousand. Eight doublings turns ten thousand into two point five million. But here's why this matters so much. If your money is sitting in a savings account earning one percent, seventy two divided by one equals seventy two years to double. Your money would take an entire lifetime to double once. In the stock market at ten percent, it doubles seven to eight times in that same period. Where you put your money matters infinitely more than how much you put in. Choose wisely.",
        "keywords": ["Rule of 72", "Compound Interest", "Money Doubling"],
    },
    {
        "title": "Why Lottery Winners Go Broke",
        "search_queries": ["lottery ticket scratch off", "champagne celebration party", "mansion luxury empty pool", "empty wallet broke person", "shopping spree bags expensive", "tax bill IRS document", "friends asking money favor", "bankruptcy court gavel", "financial advisor meeting desk", "slow wealth tortoise"],
        "slides": [
            {"text": "Why do lottery\nwinners go broke?\nIts not bad luck", "duration": 5},
            {"text": "70% of winners\nlose everything\nwithin 5 years", "duration": 5},
            {"text": "First the government\ntakes 40% in taxes\nright away", "duration": 5},
            {"text": "Win $10 million?\nYou actually get\nabout $6 million", "duration": 5},
            {"text": "Then friends and\nfamily you havent\nheard from in years\nshow up", "duration": 5},
            {"text": "They buy mansions\ncars and stuff\nwith massive\nmaintenance costs", "duration": 5},
            {"text": "A $5M house costs\n$50,000 per year\njust in property tax", "duration": 5},
            {"text": "The real problem?\nThey never learned\nhow to manage money", "duration": 5},
            {"text": "Getting money and\nkeeping money are\ntwo completely\ndifferent skills", "duration": 5},
            {"text": "Thats why financial\neducation beats luck\nBuild wealth slowly\nit lasts", "duration": 6},
        ],
        "voiceover": "Why do lottery winners go broke? It's not bad luck. It's a pattern. Seventy percent of lottery winners lose everything within five years. Here's exactly what happens. First, the government takes about forty percent in taxes immediately. Win ten million? You actually get about six million. Then suddenly, friends and family you haven't heard from in years start showing up asking for money. They buy huge mansions, luxury cars, and expensive things with massive ongoing maintenance costs nobody warns them about. A five million dollar house costs fifty thousand dollars per year just in property taxes. Not including maintenance, utilities, and insurance. The real problem isn't the spending. It's that they never learned how to manage money. Getting money and keeping money are two completely different skills. You can hand someone ten million dollars, but without financial knowledge, they'll find a way to lose it all. That's exactly why financial education beats luck every single time. People who build wealth slowly through investing, budgeting, and smart decisions keep their money forever. Quick money disappears. Slow money lasts.",
        "keywords": ["Lottery", "Wealth Management", "Financial Literacy"],
    },
    {
        "title": "What Is Passive Income Explained",
        "search_queries": ["person sleeping money growing", "rental property house sign", "dividend stock portfolio screen", "youtube creator filming laptop", "book author writing desk", "vending machine business", "royalty music headphones studio", "beach laptop working freedom", "multiple streams river water", "financial freedom celebrating"],
        "slides": [
            {"text": "What is passive\nincome? Lets make\nit simple", "duration": 5},
            {"text": "Its money you earn\nwithout trading\nyour time for it", "duration": 5},
            {"text": "Your job = active\nincome you stop\nworking you stop\nearning", "duration": 5},
            {"text": "Passive income keeps\npaying you even\nwhile you sleep", "duration": 5},
            {"text": "Dividend stocks pay\nyou cash every\n3 months just\nfor owning them", "duration": 5},
            {"text": "Rental property\npays monthly rent\nfrom tenants", "duration": 5},
            {"text": "Online business\nearns revenue\n24 hours a day", "duration": 5},
            {"text": "But heres the truth\nnothing is passive\nat the START", "duration": 5},
            {"text": "You invest time\nor money upfront\nthen it pays you\nback over time", "duration": 6},
            {"text": "Start with dividend\nETFs like SCHD\neasiest passive\nincome for beginners", "duration": 5},
        ],
        "voiceover": "What is passive income? Let's make it really simple. It's money you earn without actively trading your time for it every day. Your regular job is active income. You show up, you work, you get paid. Stop showing up, stop getting paid. Passive income is different. It keeps paying you even while you sleep, while you're on vacation, while you're doing absolutely nothing. Dividend stocks pay you cash every three months just for owning shares. You don't have to do anything. Rental properties pay you monthly rent from tenants living in your property. An online business or YouTube channel can earn advertising revenue twenty four hours a day, seven days a week. But here's the truth nobody on social media tells you. Nothing is truly passive at the start. Every passive income stream requires either significant time or money invested upfront. You build it, set it up, and then over time it starts paying you back. The easiest passive income for beginners is dividend E T Fs like S C H D. Buy shares, receive quarterly cash payments. Start there and build more streams over time.",
        "keywords": ["Passive Income", "Dividends", "Financial Freedom"],
    },
    {
        "title": "What Is Net Worth and How to Calculate It",
        "search_queries": ["balance scale weighing gold", "house car valuable assets", "credit card debt stack bills", "calculator notepad pen desk", "bank account statement screen", "net worth growing graph", "person checking finances phone", "wealthy simple lifestyle", "financial health checkup", "progress bar increasing"],
        "slides": [
            {"text": "Your net worth is\nthe most important\nnumber in finance", "duration": 5},
            {"text": "Its a snapshot of\nyour entire\nfinancial health", "duration": 5},
            {"text": "Step 1\nAdd everything\nyou OWN", "duration": 5},
            {"text": "Cash savings\ninvestments\nhouse value\ncar value", "duration": 5},
            {"text": "Step 2\nSubtract everything\nyou OWE", "duration": 5},
            {"text": "Credit card debt\ncar loans\nmortgage\nstudent loans", "duration": 5},
            {"text": "What you OWN\nminus what you OWE\nequals NET WORTH", "duration": 5},
            {"text": "Negative?\nDont panic\nmost people start\nin the negative", "duration": 5},
            {"text": "Track it every\nsingle month\non a spreadsheet", "duration": 5},
            {"text": "Your only goal is\nto make it higher\nthan last month\nevery month", "duration": 5},
        ],
        "voiceover": "Your net worth is the single most important number in personal finance. It's a complete snapshot of your financial health in one number. Here's how to calculate it. Step one, add up everything you own. Cash in your bank accounts, savings, investments, the value of your house if you own one, and your car's current value. That's your total assets. Step two, subtract everything you owe. Credit card balances, car loans, mortgage balance, student loans, any money you owe anyone. That's your total liabilities. Assets minus liabilities equals your net worth. If your number is negative right now, do not panic. Most people in their twenties and thirties have a negative net worth because of student loans and car payments. That's completely normal. The key is to track this number every single month. Write it down on a simple spreadsheet. Your only goal is to make it higher than last month. Every single month. Pay down some debt, save a little more, invest consistently. Watch that number climb. That's how you build real wealth, one month at a time.",
        "keywords": ["Net Worth", "Assets", "Liabilities", "Financial Health"],
    },
    {
        "title": "What Is a Bear Market vs Bull Market",
        "search_queries": ["bear animal fierce standing", "bull statue wall street bronze", "stock chart crashing red arrow", "stock chart rising green arrow", "investor worried looking screen", "investor celebrating gains happy", "history chart timeline long", "person holding steady calm", "sunrise after dark storm", "opportunity sale sign discount"],
        "slides": [
            {"text": "Bear market vs\nBull market\nwhat do they mean?", "duration": 5},
            {"text": "BULL market\nmeans stocks are\ngoing UP for months", "duration": 5},
            {"text": "Everyone is buying\nprices keep climbing\npeople feel great", "duration": 5},
            {"text": "BEAR market means\nstocks have dropped\n20% or more", "duration": 5},
            {"text": "Fear takes over\npeople panic sell\nprices crash further", "duration": 5},
            {"text": "But bear markets\nare actually\nOPPORTUNITIES\nin disguise", "duration": 5},
            {"text": "Stocks are on sale\nyou buy the same\ncompanies cheaper", "duration": 5},
            {"text": "Since 1928 EVERY\nbear market ended\nand a bull market\nfollowed", "duration": 6},
            {"text": "Average bear market\nlasts 9 months\nAverage bull market\nlasts 2.7 YEARS", "duration": 6},
            {"text": "Be greedy when\nothers are fearful\nThats Warren Buffetts\nnumber 1 rule", "duration": 6},
        ],
        "voiceover": "Bear market versus bull market. What do these actually mean? A bull market means stocks have been going up consistently for months or years. Everyone is buying, prices keep climbing, and people feel optimistic and confident. A bear market is the opposite. It means stocks have dropped twenty percent or more from their recent high. Fear takes over, people panic sell everything, and prices crash even further. But here's what most people don't realize. Bear markets are actually opportunities in disguise. The same great companies you wanted to buy are now on sale at a huge discount. Since nineteen twenty eight, every single bear market eventually ended and was followed by a new bull market. Every one, without exception. The average bear market only lasts about nine months. The average bull market lasts two point seven years. The good times last three times longer than the bad times. Warren Buffett's number one rule is be greedy when others are fearful. When everyone is panicking and selling, that's exactly when smart investors are buying. Don't fear the bear. Prepare for it and profit from it.",
        "keywords": ["Bear Market", "Bull Market", "Stock Market Cycles"],
    },
    {
        "title": "What Is Inflation and Why Should You Care",
        "search_queries": ["grocery receipt long expensive", "gas station price sign high", "old vintage money bills", "bread loaf bakery shelf", "shopping cart full groceries", "wages paycheck comparison", "time clock ticking vintage", "central bank federal reserve", "price comparison then and now", "investing beating inflation"],
        "slides": [
            {"text": "What is inflation?\nIt affects you\nevery single day", "duration": 5},
            {"text": "Inflation means\nprices go up\nover time", "duration": 5},
            {"text": "A gallon of milk\ncost $1.50 in 2000\nToday its $4.50", "duration": 5},
            {"text": "Same milk\n3 times the price\nyour dollar buys less", "duration": 5},
            {"text": "Average inflation\nis about 3%\nper year", "duration": 5},
            {"text": "If your salary\ndoesnt grow by\nat least 3%", "duration": 5},
            {"text": "You are getting\na pay cut\nevery single year\neven if your check\nstays the same", "duration": 6},
            {"text": "Savings account at\n0.01% does NOT\nbeat inflation", "duration": 5},
            {"text": "Investing at 10%\nDOES beat inflation\nyour money actually\ngrows", "duration": 5},
            {"text": "Saving keeps your\nmoney safe\nInvesting makes it\nstronger", "duration": 5},
        ],
        "voiceover": "What is inflation? It affects you every single day whether you realize it or not. Inflation means prices go up over time. A gallon of milk cost about a dollar fifty in the year two thousand. Today that exact same gallon costs four dollars fifty. Same milk, three times the price. Your dollar literally buys less stuff each year. Average inflation is about three percent per year. Here's why this matters to you personally. If your salary doesn't grow by at least three percent each year, you are effectively getting a pay cut. Even if your paycheck stays the exact same number, it buys less stuff than it did last year. And here's the real problem. A regular savings account paying zero point zero one percent does absolutely nothing against three percent inflation. Your money is slowly losing purchasing power just sitting there. But investing in the stock market at an average of ten percent per year does beat inflation. After three percent inflation, you're still gaining seven percent in real purchasing power. Saving keeps your money safe. Investing makes it actually stronger over time. You need both.",
        "keywords": ["Inflation", "Cost of Living", "Purchasing Power"],
    },
    {
        "title": "How to Read Your Pay Stub",
        "search_queries": ["paycheck stub paper detailed", "gross pay amount highlighted", "tax deduction list itemized", "social security card blue", "health insurance card medical", "net pay bank deposit", "person confused reading paper", "direct deposit phone notification", "employee working office desk", "take home pay wallet"],
        "slides": [
            {"text": "Can you actually\nread your pay stub?\nMost people cant", "duration": 5},
            {"text": "GROSS PAY\nis what you earned\nbefore deductions", "duration": 5},
            {"text": "This is the big\nnumber at the top", "duration": 4},
            {"text": "Then come\nthe deductions\nthis is where\nmoney disappears", "duration": 5},
            {"text": "Federal income tax\nState tax\nSocial Security\nMedicare", "duration": 5},
            {"text": "Health insurance\nand 401k come\nout too if you\nhave them", "duration": 5},
            {"text": "After ALL deductions\nyou get NET PAY", "duration": 5},
            {"text": "Thats your actual\ntake home money\nwhat hits your\nbank account", "duration": 5},
            {"text": "Gross = what\nyou earn\nNet = what\nyou keep", "duration": 5},
            {"text": "Check it monthly\nfor errors\nMistakes happen\nand cost you money", "duration": 6},
        ],
        "voiceover": "Can you actually read your pay stub? Most people just look at the deposit amount and ignore everything else. Gross pay is what you earned before anything gets taken out. It's the big number at the top of your stub. Then come the deductions. This is where your money seems to disappear. Federal income tax takes a percentage based on your tax bracket. State income tax takes its cut if your state has one. Social Security takes six point two percent. Medicare takes one point four five percent. Those are all mandatory. Then your health insurance premium and four oh one K contributions come out if you have them set up. After all of those deductions, you're left with your net pay. That's your actual take home money. The amount that hits your bank account. Easy way to remember it. Gross pay is what you earn. Net pay is what you keep. Check your pay stub at least once a month and verify everything is correct. Payroll mistakes happen more often than you think, and they always seem to be in the company's favor, not yours.",
        "keywords": ["Pay Stub", "Gross Pay", "Net Pay", "Payroll"],
    },
    {
        "title": "Good Debt vs Bad Debt",
        "search_queries": ["student graduation cap gown", "house mortgage signing papers", "credit card shopping spree bags", "car loan dealership new", "business startup laptop coffee", "person drowning debt water", "scale balance comparing weights", "investment return growing chart", "person celebrating debt free", "tool hammer building"],
        "slides": [
            {"text": "Not all debt is bad\nsome debt actually\nmakes you richer", "duration": 5},
            {"text": "GOOD debt helps\nyou earn more\nmoney over time", "duration": 5},
            {"text": "Student loans for a\nhigh paying career\nGood debt", "duration": 5},
            {"text": "Mortgage on a\nproperty that grows\nin value Good debt", "duration": 5},
            {"text": "Business loan that\ngenerates more than\nit costs Good debt", "duration": 5},
            {"text": "BAD debt buys things\nthat lose value and\ncosts you interest", "duration": 5},
            {"text": "Credit card debt on\nclothes and eating out\nBad debt", "duration": 5},
            {"text": "Car loan on a car\nyou cant afford\nBad debt", "duration": 5},
            {"text": "The test is simple\nwill this debt make\nme richer or poorer\nin 5 years?", "duration": 6},
            {"text": "Use debt as a tool\nto build wealth\nnever as a trap\nthat keeps you broke", "duration": 6},
        ],
        "voiceover": "Not all debt is created equal. Some debt actually makes you richer over time. Good debt helps you earn more money or build wealth. Student loans that lead to a high paying career? That's good debt if you choose your degree wisely. A mortgage on a property that appreciates in value? Good debt. You're building equity while living there. A business loan that generates more revenue than the interest costs? Good debt. You're using borrowed money to make even more money. Bad debt is the opposite. It buys things that lose value immediately and charges you interest while doing it. Credit card debt from shopping sprees and eating out? Bad debt. A car loan on a brand new luxury car you can't really afford? Bad debt. That car loses twenty percent of its value the moment you drive off the lot. The test is simple. Before taking on any debt, ask yourself this question. Will this debt make me richer or poorer in five years? If the answer is poorer, don't do it. Use debt as a tool to build wealth, never as a trap that keeps you broke.",
        "keywords": ["Good Debt", "Bad Debt", "Financial Decisions"],
    },
]


def fetch_pexels_images(queries, num_images, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    images = []

    for i in range(num_images):
        query = queries[i % len(queries)]
        img_path = os.path.join(save_dir, f"slide_{i}.jpg")

        if os.path.exists(img_path):
            images.append(img_path)
            continue

        try:
            url = f"https://api.pexels.com/v1/search?query={query}&orientation=portrait&per_page=15&page=1"
            headers = {"Authorization": PEXELS_API_KEY}
            resp = requests.get(url, headers=headers, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                photos = data.get("photos", [])
                if photos:
                    photo = photos[i % len(photos)]
                    img_url = photo["src"].get("portrait", photo["src"]["large"])
                    img_resp = requests.get(img_url, timeout=15)
                    if img_resp.status_code == 200:
                        with open(img_path, 'wb') as f:
                            f.write(img_resp.content)
                        images.append(img_path)
                        print(f"  📸 Image {i+1}: {query}")
                        continue

            print(f"  ⚠️ Pexels {resp.status_code}: {resp.text[:150]}")
            images.append(None)

        except Exception as e:
            print(f"  ⚠️ Image error: {e}")
            images.append(None)

    return images


def create_audio(text, output_path):
    # Try edge-tts first — DavisNeural is the deepest free male voice
    try:
        import edge_tts
        voices = [
            ("en-US-DavisNeural", "+10%", "-4Hz"),
            ("en-US-GuyNeural", "+10%", "-3Hz"),
            ("en-US-ChristopherNeural", "+10%", "-2Hz"),
            ("en-GB-RyanNeural", "+10%", "-3Hz"),
        ]
        for voice, rate, pitch in voices:
            try:
                communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
                loop = asyncio.new_event_loop()
                loop.run_until_complete(communicate.save(output_path))
                loop.close()
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    print(f"✅ Audio ready (deep voice: {voice})")
                    return True
            except Exception:
                continue
        raise Exception("All edge-tts voices failed")
    except Exception as e:
        print(f"⚠️ edge-tts failed ({e}), trying piper-tts...")

    # Piper TTS fallback — offline, works on Render
    try:
        import wave
        from piper import PiperVoice
        model_path = os.path.join(os.path.dirname(__file__), "voice.onnx")
        if os.path.exists(model_path):
            voice = PiperVoice.load(model_path)
            wav_path = output_path.replace(".mp3", ".wav")
            with wave.open(wav_path, "wb") as wav_file:
                voice.synthesize(text, wav_file)
            cmd = [FFMPEG, '-y', '-i', wav_path, '-b:a', '128k', output_path]
            subprocess.run(cmd, capture_output=True, timeout=30)
            os.remove(wav_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print("✅ Audio ready (Piper TTS)")
                return True
        raise Exception("No piper model found")
    except Exception as e2:
        print(f"⚠️ piper-tts failed ({e2}), using gTTS")

    # Final fallback
    from gtts import gTTS
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)
    print("✅ Audio ready (gTTS fallback)")
    return True


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
    return 25


def escape_ffmpeg_text(text):
    text = text.replace("'", "")
    text = text.replace(":", "\\:")
    text = text.replace("$", "\\$")
    text = text.replace("%", "%%")
    text = text.replace('"', "")
    text = text.replace(";", "\\;")
    return text


def prep_slides(images, slides, scale, work_dir):
    """Pre-render each slide as a JPEG with text burned in via Pillow (faster, better fonts)"""
    os.makedirs(work_dir, exist_ok=True)
    concat_file = os.path.join(work_dir, "concat.txt")

    from PIL import Image, ImageDraw, ImageFont

    def get_font(size):
        font_search = [
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "impact.ttf", "Impact.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "DejaVuSans-Bold.ttf", "FreeSansBold.ttf",
            "LiberationSans-Bold.ttf",
        ]
        for path in font_search:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    font_big = get_font(58)
    font_med = get_font(50)

    W, H = 720, 1280

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

        bg = bg.convert("RGBA")
        gradient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(gradient)
        for y_pos in range(H):
            if y_pos < H // 2:
                alpha = 0
            else:
                alpha = int(200 * ((y_pos - H // 2) / (H // 2)))
            g_draw.rectangle([(0, y_pos), (W, y_pos)], fill=(0, 0, 0, alpha))
        bg = Image.alpha_composite(bg, gradient).convert("RGB")
        del gradient, g_draw

        draw = ImageDraw.Draw(bg)
        lines = slide['text'].upper().split('\n')
        line_h = 80
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

            if li == 0:
                color = (255, 255, 255)
            else:
                color = (255, 255, 50)
            draw.text((x, y), line, font=font, fill=color)

        bg.save(out, "JPEG", quality=90)
        del draw, bg
        gc.collect()
        print(f"  slide {idx+1}/{len(slides)} ready")

    with open(concat_file, 'w') as f:
        for idx, slide in enumerate(slides):
            dur = slide['duration'] * scale
            f.write(f"file 's_{idx}.jpg'\n")
            f.write(f"duration {dur:.2f}\n")
        f.write(f"file 's_{len(slides)-1}.jpg'\n")

    return concat_file


def create_video_ffmpeg(slides, images, audio_file, output_file):
    audio_duration = get_audio_duration(audio_file)
    total_slide_dur = sum(s['duration'] for s in slides)
    scale = audio_duration / total_slide_dur if total_slide_dur > 0 else 1.0

    valid_images = [img for img in images if img is not None]
    if not valid_images:
        return create_video_simple(slides, audio_file, output_file)

    work_dir = output_file + "_work"
    print("🖼️ Preparing slides with text...")
    concat_file = prep_slides(images, slides, scale, work_dir)

    cmd = [
        FFMPEG, '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_file,
        '-i', audio_file,
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-vsync', 'vfr',
        output_file
    ]

    print(f"🔧 Running FFmpeg (concat {len(slides)} slides)...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        print("❌ FFmpeg timed out")
        return create_video_simple(slides, audio_file, output_file)

    import shutil
    shutil.rmtree(work_dir, ignore_errors=True)

    if proc.returncode != 0:
        err = stderr.decode('utf-8', errors='replace')[-500:]
        print(f"❌ FFmpeg failed: {err[-300:]}")
        return create_video_simple(slides, audio_file, output_file)

    print("✅ Video created with animated images!")
    return True


def create_video_simple(slides, audio_file, output_file):
    audio_duration = get_audio_duration(audio_file)
    total_slide_dur = sum(s['duration'] for s in slides)
    scale = audio_duration / total_slide_dur if total_slide_dur > 0 else 1.0

    filters = []

    t = 0
    for slide in slides:
        dur = slide['duration'] * scale
        lines = slide['text'].split('\n')
        num_lines = len(lines)
        start_y = f"(h/2)-{(num_lines * 30)}"

        for li, line in enumerate(lines):
            escaped = escape_ffmpeg_text(line)
            y_pos = f"({start_y})+{li * 60}"
            color = "white" if li == 0 else "0x00DDFF"
            filters.append(
                f"drawtext=text='{escaped}':"
                f"x=(w-text_w)/2:y={y_pos}:"
                f"fontsize=42:fontcolor={color}:"
                f"borderw=3:bordercolor=black:"
                f"enable='between(t,{t:.2f},{t+dur:.2f})'"
            )
        t += dur

    vf = ",".join(filters)
    cmd = [
        FFMPEG, '-y',
        '-f', 'lavfi', '-i', 'color=c=0x0A0A2E:size=720x1280:rate=24',
        '-i', audio_file,
        '-vf', vf,
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_file
    ]

    print(f"🔧 Running FFmpeg (simple mode)...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=240)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        print("❌ FFmpeg timed out")
        return False

    if proc.returncode != 0:
        print(f"❌ FFmpeg failed")
        print(stderr.decode('utf-8', errors='replace')[-500:])
        return False

    print("✅ Video created (simple mode)")
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

    os.makedirs(CONFIG['output_dir'], exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"{CONFIG['output_dir']}/the_ai_dollar_{timestamp}.mp4"
    audio_file = f"{CONFIG['output_dir']}/audio_{timestamp}.mp3"
    img_dir = f"{CONFIG['output_dir']}/imgs_{timestamp}"

    try:
        print("🎤 Generating voiceover...")
        create_audio(topic['voiceover'], audio_file)

        images = []
        if PEXELS_API_KEY:
            print("📸 Fetching images from Pexels...")
            images = fetch_pexels_images(
                topic['search_queries'],
                len(topic['slides']),
                img_dir
            )
            print(f"✅ Got {sum(1 for i in images if i)} images")
        else:
            print("⚠️ No PEXELS_API_KEY, using color background")

        print("🎬 Creating animated video...")
        ok = create_video_ffmpeg(topic['slides'], images, audio_file, output_file)

        if not ok:
            return {"status": "error", "message": "Video creation failed"}

        print(f"✅ Video created: {output_file}")

        try:
            os.remove(audio_file)
        except Exception:
            pass
        try:
            import shutil
            shutil.rmtree(img_dir, ignore_errors=True)
        except Exception:
            pass

        return {
            "status": "success",
            "video": output_file,
            "title": topic['title'],
            "script": topic['voiceover'],
            "keywords": topic['keywords']
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
