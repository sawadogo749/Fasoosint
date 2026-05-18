# 🔍 FasoOSINT

> OSINT Username Intelligence Tool — Bilingue 🇫🇷 Français / 🇬🇧 English  
> Un produit **BISNAABA** 🇧🇫

![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-red)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Sites](https://img.shields.io/badge/Sites-618+-yellow)
![Status](https://img.shields.io/badge/Status-En%20développement-orange)
![Web](https://img.shields.io/badge/Web-fasoosint.com-red)

---

## 🌐 Site officiel

**[https://fasoosint.com](https://fasoosint.com)**

---

## 🇫🇷 Présentation

**FasoOSINT** est un outil OSINT open source permettant de rechercher un pseudonyme sur **618+ plateformes** en quelques secondes — réseaux sociaux, gaming, coding, sécurité, plateformes africaines et bien plus.

### Ce qui le distingue
- ✅ Interface **bilingue Français/Anglais** — pas de russe
- ✅ **618+ plateformes** dont Facebook, Instagram, TikTok, Twitter
- ✅ **Plateformes africaines** incluses (Wave, MTN, Jumia, Selar...)
- ✅ **Score d'exposition numérique** /100
- ✅ **Photos de profil** téléchargées automatiquement
- ✅ **Détection d'emails** associés
- ✅ Export **PDF / HTML / CSV / TXT**
- ✅ Mode **--variants** (johndoe, john_doe, john.doe...)
- ✅ Mode **--batch** (plusieurs usernames en même temps)
- ✅ Mode **CLI** + **Interface Web** → fasoosint.com
- ✅ Base propre — **0 faux positif**
- ✅ Aucune API requise — zéro inscription

### Applications
- 🏛️ **Gouvernements** — surveillance des menaces numériques
- 🪖 **Forces armées** — renseignement et contre-espionnage
- 👮 **Forces de l'ordre** — investigation et traçabilité
- 🔐 **Agences de cybersécurité** — audit d'exposition digitale
- 🏢 **Entreprises** — vérification d'identité et due diligence

---

## 🇬🇧 Overview

**FasoOSINT** is an open source OSINT tool to search a username across **618+ platforms** in seconds — social media, gaming, coding, security, African platforms and more.

### What makes it different
- ✅ **Bilingual** French/English interface — no Russian
- ✅ **618+ platforms** including Facebook, Instagram, TikTok, Twitter
- ✅ **African platforms** included (Wave, MTN, Jumia, Selar...)
- ✅ **Digital Exposure Score** /100
- ✅ **Automatic profile picture** retrieval
- ✅ **Associated email** detection
- ✅ **PDF / HTML / CSV / TXT** export
- ✅ **--variants** mode (johndoe, john_doe, john.doe...)
- ✅ **--batch** mode (multiple usernames at once)
- ✅ **CLI** + **Web dashboard** → fasoosint.com
- ✅ Clean database — **0 false positives**
- ✅ No API required — no registration

### Use cases
- 🏛️ **Governments** — digital threat monitoring
- 🪖 **Military forces** — intelligence & counter-espionage
- 👮 **Law enforcement** — investigation & tracking
- 🔐 **Cybersecurity agencies** — digital exposure auditing
- 🏢 **Corporations** — identity verification & due diligence

---

## ⚡ Installation

```bash
git clone https://github.com/sawadogo749/Fasoosint
cd Fasoosint
pip install -r requirements.txt
```

---

## 🖥️ CLI Usage / Utilisation CLI

```bash
# Recherche simple
python3 fasoosint.py johndoe

# Français
python3 fasoosint.py johndoe --lang fr

# English
python3 fasoosint.py johndoe --lang en

# Tous les formats
python3 fasoosint.py johndoe --all

# Avec photo de profil et email
python3 fasoosint.py johndoe --avatar --email

# Mode variantes
python3 fasoosint.py "john doe" --variants --lang fr

# Mode batch
python3 fasoosint.py --batch liste.txt --lang fr

# Filtrer par région Africa
python3 fasoosint.py johndoe --region africa

# Filtrer par catégorie
python3 fasoosint.py johndoe --category social
```

---

## 🌐 Interface Web

Accès direct : **[https://fasoosint.com](https://fasoosint.com)**

Ou en local :
```bash
cd web
python3 app.py
# → http://localhost:5000
```

---

## 📊 Couverture / Coverage

| Catégorie | Sites |
|-----------|-------|
| Social Media | 80+ |
| Coding/Dev | 60+ |
| Gaming | 50+ |
| Security/CTF | 25+ |
| Music | 30+ |
| Art/Design | 30+ |
| Forum/Community | 40+ |
| Africa Platforms | 20+ |
| Dating | 20+ |
| Shopping | 25+ |
| + autres catégories | ... |
| **TOTAL** | **618+** |

---

## 🔐 Sécurité

- ✅ HTTPS forcé via Cloudflare
- ✅ Protection DDoS
- ✅ Anti-injection SQL/XSS
- ✅ Rate limiting (10 req/min/IP)
- ✅ Fail2ban + UFW Firewall
- ✅ WAF Cloudflare

---

## 🔜 Roadmap

- [ ] 200+ plateformes africaines
- [ ] Mode --variants dans le Web UI
- [ ] Rapport PDF depuis le Web UI
- [ ] API REST publique documentée
- [ ] Version Termux Android optimisée
- [ ] Application mobile
- [ ] Plugin navigateur

---

## ⚠️ Avertissement / Disclaimer

**FR** : Outil destiné à un usage éducatif et défensif uniquement. N'utilisez que sur vos propres pseudonymes ou avec autorisation explicite. L'utilisation malveillante est illégale.

**EN** : For educational and defensive use only. Only use on your own usernames or with explicit permission. Malicious use is illegal.

---

## 👤 Auteur / Author

**Abdoul Sawadogo** | Network & Cybersecurity Professional  
CCNA | Cisco Meraki | AZ-140 | CompTIA Security+  
📍 Nebraska, USA

---

## 🏢 Produit / Product

Un produit **BISNAABA** 🇧🇫

---

## 📄 Licence

CC BY-NC-SA 4.0 — Voir [LICENSE](LICENSE)  
Usage commercial interdit / Commercial use prohibited.  
Toute modification doit créditer **Abdoul Sawadogo**.
