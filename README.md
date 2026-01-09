# ShuraTools 🛠️

Swiss-army knife para testes de carga e automação de reports (SpamMail, SpamZap, BanIG).

## 🚀 Instalação

Para usar o script, clone o repositório e instale as dependências:

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/ShuraTools.git

# Entre na pasta
cd ShuraTools

# Instale as dependências
pip install -r requirements.txt
```

## 🛠️ Uso

O script aceita diversas flags para configurar o seu teste.

### Exemplos:

**Spam de E-mail:**
```bash
python3 ShuraTools.py --mail --target vitima@gmail.com --qty 100 --threads 20
```

**Denúncia de WhatsApp:**
```bash
python3 ShuraTools.py --zap --target 5511999999999 --qty 50 --threads 10
```

**Report de Instagram:**
```bash
python3 ShuraTools.py --ig --target @usuario_alvo --qty 30 --threads 5
```

### Argumentos:
- `--mail`: Ativa o módulo de Spam de E-mail.
- `--zap`: Ativa o módulo de Denúncia de WhatsApp.
- `--ig`: Ativa o módulo de Report de Instagram.
- `--target`: O alvo (email, telefone com DDI ou @user).
- `--qty`: Quantidade total de requisições.
- `--threads`: Número de processos simultâneos.
- `--proxy`: Ativa o uso de proxies rotativos (opcional).
- `--timer`: Delay em segundos entre cada requisição.

---
**Aviso:** Este script foi criado para fins educacionais e testes de estresse em sistemas próprios. O uso indevido para assédio ou atividades ilícitas é de total responsabilidade do usuário.
