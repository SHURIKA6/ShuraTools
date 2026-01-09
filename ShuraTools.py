#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam/banimento.
"""

import os, sys, time, random, string, argparse, threading, requests
try:
    from faker import Faker
    fake = Faker()
except ImportError:
    # Apenas loga o erro, o main() lidará com a falta da lib
    fake = None

BANNER = r"""
   _____ _    _ _______ _______ _____  ______ 
  / ____| |  | |__   __|__   __|  __ \|  ____|
 | (___ | |__| |  | |     | |  | |  | | |__   
  \___ \|  __  |  | |     | |  | |  | |  __|  
  ____) | |  | |  | |     | |  | |__| | |____ 
 |_____/|_|  |_|  |_|     |_|  |_____/|______|
  SpamMail | SpamZap | BanIG – by Shura
"""

# ---------- Configurações globais ----------
LOCK = threading.Lock()
PROXY_LIST = [
    "http://51.222.146.133:3128",
    "http://177.54.229.164:8080",
    "http://45.235.14.116:8080"
]
UA_LIST = [
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36 Instagram 150.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "WhatsApp/2.21.4.22 A",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
]

def rnd_proxy():
    if not PROXY_LIST: return None
    p = random.choice(PROXY_LIST)
    return {"http": p, "https": p}

def rnd_ua():
    return random.choice(UA_LIST)

def log(msg):
    with LOCK:
        print(msg)

# ---------- Threading Helper ----------
def run_threads(target_func, qty, threads, *args):
    if threads <= 0: threads = 1
    chunk = qty // threads
    remainder = qty % threads
    ts = []
    start = 0
    for i in range(threads):
        end = start + chunk + (1 if i < remainder else 0)
        if start == end: continue
        t = threading.Thread(target=target_func, args=(start, end, *args))
        t.start()
        ts.append(t)
        start = end
    for t in ts:
        t.join()

# ---------- 1) SpamMail ----------
def spam_mail(target, qty, threads, timer, use_proxy):
    if fake is None:
        print("[!] Erro: Biblioteca 'faker' não instalada. Execute: pip install -r requirements.txt")
        return

    def job(start, end, target, timer, use_proxy):
        for i in range(start, end):
            mail = fake.email()
            proxies = rnd_proxy() if use_proxy else None
            try:
                requests.post("https://api.anonfiles.com/mail", timeout=5,
                              data={"to": target, "from": mail, "subj": "ShuraSpam",
                                    "body": "Você foi escolhido."},
                              proxies=proxies, headers={"User-Agent": rnd_ua()})
                log(f"[+] {i+1}: {mail} -> {target}")
            except Exception as e:
                log(f"[~] {i+1}: {mail} falhou ({e})")
            if timer > 0:
                time.sleep(timer)
    
    run_threads(job, qty, threads, target, timer, use_proxy)
    log("[+] SpamMail finalizado.")

# ---------- 2) SpamZap ----------
def spam_zap(target, qty, threads, timer, use_proxy):
    def job(start, end, target, timer, use_proxy):
        for i in range(start, end):
            proxies = rnd_proxy() if use_proxy else None
            try:
                requests.post("https://v.whatsapp.net/v2/report", timeout=5,
                              data={"phone": target, "reason": "spam",
                                    "session": os.urandom(16).hex()},
                              proxies=proxies, headers={"User-Agent": rnd_ua()})
                log(f"[+] Denúncia {i+1} enviada.")
            except Exception as e:
                log(f"[~] Denúncia {i+1} falhou ({e})")
            if timer > 0:
                time.sleep(timer)

    run_threads(job, qty, threads, target, timer, use_proxy)
    log("[+] SpamZap finalizado.")

# ---------- 3) BanIG ----------
def ban_ig(target, qty, threads, timer, use_proxy):
    def job(start, end, target, timer, use_proxy):
        for i in range(start, end):
            proxies = rnd_proxy() if use_proxy else None
            try:
                requests.post("https://i.instagram.com/api/v1/users/web_report/", timeout=5,
                              data={"username": target, "source_name": "profile",
                                    "reason_id": "2"},
                              proxies=proxies, headers={"User-Agent": rnd_ua()})
                log(f"[+] Report {i+1} enviado.")
            except Exception as e:
                log(f"[~] Report {i+1} falhou ({e})")
            if timer > 0:
                time.sleep(timer)

    run_threads(job, qty, threads, target, timer, use_proxy)
    log("[+] BanIG finalizado.")

def main():
    print(BANNER)
    ap = argparse.ArgumentParser(description="ShuraTools – Utilitário de testes de carga e spam.")
    ap.add_argument("--mail", action="store_true", help="Ativa SpamMail")
    ap.add_argument("--zap", action="store_true", help="Ativa SpamZap")
    ap.add_argument("--ig", action="store_true", help="Ativa BanIG")
    ap.add_argument("--target", required=True, help="E-mail, telefone ou @user")
    ap.add_argument("--qty", type=int, default=50, help="Quantidade total (padrão 50)")
    ap.add_argument("--threads", type=int, default=10, help="Número de threads (padrão 10)")
    ap.add_argument("--proxy", action="store_true", help="Usar proxy rotativo")
    ap.add_argument("--timer", type=float, default=0, help="Delay entre requisições (s)")
    
    if len(sys.argv) <= 1:
        ap.print_help()
        sys.exit(0)
        
    args = ap.parse_args()

    # Checar requests
    try:
        import requests
    except ImportError:
        print("[!] Erro: 'requests' não instalado. Execute: pip install -r requirements.txt")
        sys.exit(1)

    if args.mail:
        print(f"[*] Iniciando SpamMail para {args.target}...")
        spam_mail(args.target, args.qty, args.threads, args.timer, args.proxy)
    
    if args.zap:
        print(f"[*] Iniciando SpamZap para {args.target}...")
        spam_zap(args.target, args.qty, args.threads, args.timer, args.proxy)
    
    if args.ig:
        print(f"[*] Iniciando BanIG para {args.target}...")
        ban_ig(args.target, args.qty, args.threads, args.timer, args.proxy)
    
    if not (args.mail or args.zap or args.ig):
        print("\n[!] Escolha uma função (--mail, --zap, --ig)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Saindo...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Erro: {e}")
