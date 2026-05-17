# 🔍 FasoOSINT

> OSINT Username Intelligence Tool — Bilingue 🇫🇷 Français / 🇬🇧 English

![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-red)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Sites](https://img.shields.io/badge/Sites-367+-yellow)
![Status](https://img.shields.io/badge/Status-En%20développement-orange)

---

## 🇫🇷 Présentation

**FasoOSINT** est un outil OSINT open source permettant de rechercher un pseudonyme sur **367+ plateformes** en quelques secondes.

### Ce qui le distingue
- ✅ Interface **bilingue Français/Anglais**
- ✅ **Plateformes africaines** incluses
- ✅ **Score d'exposition numérique** /100
- ✅ Export **PDF / HTML / CSV / TXT**
- ✅ Mode **CLI** + **Interface Web**
- ✅ Base propre — **zéro faux positif**
- ✅ Aucune API requise — zéro inscription

---

## 🇬🇧 Overview

**FasoOSINT** is an open source OSINT tool to search a username across **367+ platforms** in seconds.

### What makes it different
- ✅ **Bilingual** French/English interface
- ✅ **African platforms** included
- ✅ **Digital Exposure Score** /100
- ✅ **PDF / HTML / CSV / TXT** export
- ✅ **CLI** + **Web dashboard**
- ✅ Clean database — **zero false positives**
- ✅ No API required — no registration

---

## ⚡ Installation

```bash
git clone https://github.com/sawadogo749/Fasoosint
cd Fasoosint
pip install -r requirements.txt
```

---

## 🖥️ CLI Usage

```bash
# Recherche simple / Basic search
python3 fasoosint.py johndoe

# Français
python3 fasoosint.py johndoe --lang fr

# English
python3 fasoosint.py johndoe --lang en

# Tous les formats / All formats
python3 fasoosint.py johndoe --all

# Filtrer par région / Filter by region
python3 fasoosint.py johndoe --region africa

# Filtrer par catégorie / Filter by category
python3 fasoosint.py johndoe --category social
```

---

## 🌐 Interface Web

```bash
cd web
python3 app.py
# → http://localhost:5000
```

---

## 📊 Couverture / Coverage

| Catégorie | Sites |
|-----------|-------|
| Social Media | 40+ |
| Coding/Dev | 35+ |
| Gaming | 30+ |
| Security/CTF | 15+ |
| Music | 15+ |
| Africa Platforms | 20+ |
| + 10 autres catégories | ... |

---

## 🔜 Roadmap

- [ ] Mode `--variants` (johndoe, john_doe, john.doe)
- [ ] Photo de profil automatique
- [ ] Détection email associé
- [ ] 500+ sites africains
- [ ] Déploiement → fasoosint.com
- [ ] API REST publique

---

## ⚠️ Avertissement / Disclaimer

**FR** : Outil destiné à un usage éducatif et défensif uniquement. N'utilisez que sur vos propres pseudonymes ou avec autorisation explicite.

**EN** : For educational and defensive use only. Only use on your own usernames or with explicit permission.

---

## 👤 Auteur / Author

**Abdoul Sawadogo** | Network & Cybersecurity Professional
CCNA | Cisco Meraki | AZ-140 | CompTIA Security+

---

## 📄 Licence

CC BY-NC-SA 4.0 — Voir [LICENSE](LICENSE)
Usage commercial interdit / Commercial use prohibited.
