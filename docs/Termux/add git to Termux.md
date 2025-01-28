---
title: add git to Termux
created: 28.01.2025
modified: 28.01.2025
---
1. Убедись, что Git установлен
- Если Git еще не установлен, выполни:
```bash
pkg update
pkg install git
```

2. Настрой SSH-ключ
Если ты еще не настроил SSH-ключ на Termux, выполни следующие шаги:
- Сгенерируй SSH-ключ:
```bash
ssh-keygen -t ed25519 -C "ваш.email@example.com"
```

- Или, если твоя версия SSH не поддерживает ed25519:
```bash
ssh-keygen -t rsa -b 4096 -C "ваш.email@example.com"
```

- Выведи публичный ключ:
```bashy
cat ~/.ssh/id_ed25519.pub
```

Или:
```bash
cat ~/.ssh/id_rsa.pub
```

- Скопируй ключ и добавь его в GitHub:
- Перейди в Settings → SSH and GPG keys.
- Нажми New SSH key.
- Вставь ключ и сохрани.
- Проверь подключение:
```bash
ssh -T git@github.com
```

- Должно появиться:
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

3. Инициализируй Git в проекте
- Перейди в папку с проектом:
```bash
cd /путь/к/твоему/проекту
```

- Инициализируй Git:
```bash
git init
```

- Добавь удаленный репозиторий (замени username и repository на свои):
```bash
git remote add origin git@github.com:username/repository.git
```

- Проверь, что удаленный репозиторий добавлен:
```bash
git remote -v
```

- Должно появиться что-то вроде:
```bash
origin  git@github.com:username/repository.git (fetch)
origin  git@github.com:username/repository.git (push)
```

4. Синхронизируй проект с GitHub
- Получи последние изменения с GitHub:
```bash
git fetch origin
```

- Если в твоем проекте есть изменения, которые ты хочешь сохранить, создай новую ветку:
```bash
git checkout -b temp-branch
```
- Переключись на ветку, которая используется в GitHub (обычно main или master):

```bash
git checkout main
```
- Если ветка называется иначе, замени main на нужное имя.
- Слей изменения из GitHub с твоим проектом:
```bash
git pull origin main
```

- Если были конфликты, Git сообщит о них. Реши конфликты вручную, отредактировав файлы, а затем добавь их:
```bash
git add имя_файла
```
- Создай коммит:
```bash
git commit -m "Синхронизация с GitHub"
```
5. Работа с проектом
    - Теперь ты можешь:
    - Пуллить изменения: git pull origin main
    - Пушить изменения: git push origin main
    - Создавать новые ветки: git checkout -b новая_ветка
    - Переключаться между ветками: git checkout имя_ветки

6. Если твои изменения важны
- Если твои локальные изменения важны, и ты не хочешь их потерять, перед пуллингом создай новую ветку и закоммить изменения:
```bash
git checkout -b мои-изменения
git add .
git commit -m "Мои текущие изменения"
```

- Затем переключись на основную ветку (main или master) и выполни пуллинг:
```bash
git checkout main
git pull origin main
```

- После этого можно слить изменения из мои-изменения в main:
```bash
git merge мои-изменения
```

[[Termux]]
