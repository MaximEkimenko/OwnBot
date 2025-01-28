---
title: Install older python version for Termux
created: 28.01.2025
modified: 28.01.2025
---
#### 1. Install older python version for termux:
- Step 0: `pkg remove python{version}`
* Step 1:   `pkg update && pkg upgrade`
* Step 2:   `pkg install clang cmake ninja rust make`
* Step 3:   `pkg install tur-repo`
* Step 4:   `pkg install python{version}
* Step 5:  `pip{version} install --upgrade pip wheel`
- Usage:
```bash
pip3.10 install -r requirements.txt
python3.10 main.py
```
#### 2. Storage access:
```bash
termux-setup-storage
```

[[Termux]]
