import telebot
from telebot import types
import json, os, random

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

USERS_FILE = "users.json"
INV_FILE = "inventory.json"
ADMINS_FILE = "admins.json"

# ==================== UTILS ====================
def load(f, default):
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as x:
            json.dump(default, x, ensure_ascii=False, indent=2)
    with open(f, "r", encoding="utf-8") as x:
        return json.load(x)

def save(f, d):
    with open(f, "w", encoding="utf-8") as x:
        json.dump(d, x, ensure_ascii=False, indent=2)

def money(n):
    return f"{int(n):,}".replace(",", ".")

users = load(USERS_FILE, {})
inventory = load(INV_FILE, {})
admins = load(ADMINS_FILE, [])

# ==================== NFT ====================
NFT_POOL = [
    {"name":"🎁 Neon Cube","rarity":"Common","price":100},
    {"name":"🟢 Green Chip","rarity":"Rare","price":500},
    {"name":"🔵 Cyber Eye","rarity":"Epic","price":2000},
    {"name":"🟣 Neon Dragon","rarity":"Legendary","price":10000},
    {"name":"🔴 Void King","rarity":"Mythic","price":50000},
]

ULTRA_POOL = [
    {"name":"💎 ULTRA1","rarity":"ULTRA","price":7_777_777_777,"chance":5},
    {"name":"👑 ULTRA2","rarity":"ULTRA","price":33_333_333_333,"chance":3},
    {"name":"🕳 ULTRA3","rarity":"ULTRA","price":55_555_555_555,"chance":2},
    {"name":"🔥 ULTRA4","rarity":"ULTRA","price":77_777_777_777,"chance":1.5},
    {"name":"👑 ULTRA5","rarity":"ULTRA","price":111_111_111_111,"chance":1},
    {"name":"🐸 Mqsher Squad PEPE","rarity":"ULTRA","price":777_777_777_777_777_777_777,"chance":0.1},
]

LIMITED_NFT = {"name":"🚀 Major PEPE","rarity":"LIMITED","price":777_777_777_777_777_777_777_777_777_777_777_777,"dropable":False}

RARITY = [("Common",50),("Rare",30),("Epic",12),("Legendary",6),("Mythic",2)]

VIP_LEVELS = {
    0: {"name":"Нет","bonus":0},
    1: {"name":"VIP +5%","bonus":0.05},
    2: {"name":"VIP +15%","bonus":0.15},
    3: {"name":"VIP +30%","bonus":0.30}
}

admin_chance = 1.0

# ==================== USERS ====================
def get_user(uid, username=None):
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "username": username or "user",
            "money": 1_000_000,
            "cases":0,
            "ultra":0,
            "wins":0,
            "loses":0,
            "vip":0,
            "buff":1.0
        }
        inventory[uid] = []
        save(USERS_FILE, users)
        save(INV_FILE, inventory)
    return users[uid]

def find_user_by_username(username):
    username = username.replace("@", "")
    for uid,u in users.items():
        if u["username"] == username:
            return uid
    return None

# ==================== MENU ====================
def menu(admin=False):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎁 Кейсы","📦 Ultra Box")
    kb.add("🎰 Казино","🖼 Мои NFT")
    kb.add("🛒 Продать NFT","💰 Продать все NFT","👤 Профиль")
    kb.add("💎 Донат")
    if admin:
        kb.add("⚙️ Админка")
    return kb

# ==================== START ====================
@bot.message_handler(commands=["start"])
def start(m):
    get_user(m.from_user.id,m.from_user.username)
    bot.send_message(m.chat.id,"💎 *NFT GAME*\n\n🎁 Кейсы\n📦 Ultra NFT\n🎰 Казино\n🖼 Коллекция\n💎 Донат",parse_mode="Markdown",reply_markup=menu(m.from_user.id in admins))

# ==================== АДМИНКА ====================
@bot.message_handler(commands=["adm6667"])
def adm(m):
    if m.from_user.id not in admins:
        admins.append(m.from_user.id)
        save(ADMINS_FILE, admins)
    bot.send_message(m.chat.id,"⚙️ Админка активна",reply_markup=menu(True))

@bot.message_handler(commands=["givenft"])
def give_nft(m):
    if m.from_user.id not in admins:
        return
    try:
        parts = m.text.split()
        if len(parts)!=4:
            txt="Список NFT:\n"
            for i,nft in enumerate(NFT_POOL+ULTRA_POOL+[LIMITED_NFT],1):
                txt+=f"{i}. {nft['name']} — {money(nft['price'])}💰\n"
            return bot.send_message(m.chat.id,txt)
        _,username,nft_num,count = parts
        count=int(count)
        uid=find_user_by_username(username)
        if not uid: return bot.send_message(m.chat.id,"❌ Пользователь не найден")
        nft_num=int(nft_num)-1
        nft_pool=NFT_POOL+ULTRA_POOL+[LIMITED_NFT]
        if nft_num<0 or nft_num>=len(nft_pool): return bot.send_message(m.chat.id,"❌ Неверный номер NFT")
        for _ in range(count):
            inventory[uid].append(nft_pool[nft_num])
        save(INV_FILE, inventory)
        bot.send_message(m.chat.id,f"✅ @{users[uid]['username']} получил {count} x {nft_pool[nft_num]['name']}")
    except:
        bot.send_message(m.chat.id,"❌ Формат:\n/givenft @username номер количество")

@bot.message_handler(commands=["buff"])
def set_buff(m):
    if m.from_user.id not in admins:
        return
    try:
        parts=m.text.split()
        uid=int(parts[1])
        multiplier=float(parts[2])
        u=get_user(uid)
        u["buff"]=multiplier
        save(USERS_FILE, users)
        bot.send_message(m.chat.id,f"⚡ Бафф установлен x{multiplier} для @{u['username']}")
    except:
        bot.send_message(m.chat.id,"❌ Формат:\n/buff user_id множитель (например 2,5,10)")

@bot.message_handler(commands=["chance"])
def set_chance(m):
    global admin_chance
    if m.from_user.id not in admins:
        return
    try:
        multiplier = float(m.text.split()[1])
        admin_chance = multiplier
        bot.send_message(m.chat.id,f"⚡ Шансы на дроп установлены x{multiplier}")
    except:
        bot.send_message(m.chat.id,"❌ Формат: /chance множитель (например 1,2,5,10)")

# ==================== ПРОФИЛЬ ====================
@bot.message_handler(func=lambda m:m.text=="👤 Профиль")
def prof(m):
    uid=str(m.from_user.id)
    u=get_user(m.from_user.id,m.from_user.username)
    inv=inventory.get(uid,[])
    wins=u.get("wins",0)
    loses=u.get("loses",0)
    vip_name = VIP_LEVELS.get(u.get("vip",0),{"name":"Нет"})["name"]
    buff = u.get("buff",1.0)
    text=f"""━━━━━━━━━━━━
👤 Профиль
💰 Баланс: {money(u['money'])}
📦 Кейсы: {u['cases']}
💎 NFT: {len(inv)}
📦 ULTRA кейсы: {u.get('ultra',0)}
🎰 Побед: {wins} / Поражений: {loses}
👑 VIP: {vip_name}
⚡ Бафф: x{buff}
━━━━━━"""
    bot.send_message(m.chat.id,text)

# ==================== ПРОДАЖА ВСЕХ NFT ====================
@bot.message_handler(func=lambda m:m.text=="💰 Продать все NFT")
def sell_all(m):
    uid=str(m.from_user.id)
    inv=inventory.get(uid,[])
    if not inv: return bot.send_message(m.chat.id,"❌ NFT нет")
    total=sum(n["price"] for n in inv)
    inventory[uid]=[]
    users[uid]["money"]+=total
    save(USERS_FILE, users)
    save(INV_FILE, inventory)
    bot.send_message(m.chat.id,f"✅ Все NFT проданы за {money(total)}💰")

# ==================== КЕЙСЫ ====================
@bot.message_handler(func=lambda m:m.text=="🎁 Кейсы")
def case_buttons(m):
    u=get_user(m.from_user.id,m.from_user.username)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("1️⃣ Кейс - 5.000💰","5️⃣ Кейсов - 25.000💰","🔟 Кейсов - 50.000💰")
    kb.add("⬅️ Назад")
    bot.send_message(m.chat.id,"Выберите сколько кейсов купить:",reply_markup=kb)

@bot.message_handler(func=lambda m:m.text in ["1️⃣ Кейс - 5.000💰","5️⃣ Кейсов - 25.000💰","🔟 Кейсов - 50.000💰"])
def buy_case(m):
    u=get_user(m.from_user.id,m.from_user.username)
    if m.text=="1️⃣ Кейс - 5.000💰": count=1
    elif m.text=="5️⃣ Кейсов - 25.000💰": count=5
    elif m.text=="🔟 Кейсов - 50.000💰": count=10
    cost=count*5_000
    if u["money"]<cost: return bot.send_message(m.chat.id,f"❌ Нужно {money(cost)}💰")
    u["money"]-=cost
    u["cases"]+=count
    results=[]
    total_buff = (1 + u.get("buff",1.0) + VIP_LEVELS.get(u.get("vip",0),{"bonus":0})["bonus"]) * admin_chance
    for _ in range(count):
        roll=random.randint(1,100)
        s=0
        for r,c in RARITY:
            s+=c*total_buff
            if roll<=s:
                nft=random.choice([x for x in NFT_POOL if x["rarity"]==r and x["name"] != LIMITED_NFT["name"]])
                break
        inventory[str(m.from_user.id)].append(nft)
        results.append(nft["name"])
    save(USERS_FILE, users)
    save(INV_FILE, inventory)
    bot.send_message(m.chat.id,f"🎉 *Кейсы открыты!*\n\n"+"\n".join(results),parse_mode="Markdown",reply_markup=menu(m.from_user.id in admins))

# ==================== ULTRA BOX ====================
@bot.message_handler(func=lambda m:m.text=="📦 Ultra Box")
def ultra(m):
    u=get_user(m.from_user.id,m.from_user.username)
    cost=50_000_000
    desc="📦 *Ultra Box*\nСтоимость 1 кейса: {:,}💰\n\nШансы на выпадение NFT:\n".format(cost).replace(",",".")
    for nft in ULTRA_POOL:
        desc+=f"{nft['name']}: {nft['chance']}% шанс\n"
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("1️⃣ Ultra Box","5️⃣ Ultra Box","🔟 Ultra Box","⬅️ Назад")
    bot.send_message(m.chat.id,desc,parse_mode="Markdown",reply_markup=kb)

@bot.message_handler(func=lambda m:m.text in ["1️⃣ Ultra Box","5️⃣ Ultra Box","🔟 Ultra Box"])
def buy_ultra(m):
    u=get_user(m.from_user.id,m.from_user.username)
    if m.text=="1️⃣ Ultra Box": count=1
    elif m.text=="5️⃣ Ultra Box": count=5
    elif m.text=="🔟 Ultra Box": count=10
    cost=count*50_000_000
    if u["money"]<cost: return bot.send_message(m.chat.id,f"❌ Нужно {money(cost)}💰")
    u["money"]-=cost
    results=[]
    for _ in range(count):
        roll=random.uniform(0,100)
        cumulative=0
        for nft in ULTRA_POOL:
            cumulative+=nft["chance"]
            if roll<=cumulative:
                won=nft
                break
        else:
            won=random.choice(ULTRA_POOL)
        inventory[str(m.from_user.id)].append(won)
        results.append(won["name"])
    save(USERS_FILE, users)
    save(INV_FILE, inventory)
    bot.send_message(m.chat.id,f"💥 Ultra Box x{count} открыт!\n\n🎁 Выпало:\n"+"\n".join(results),reply_markup=menu(m.from_user.id in admins))

# ==================== КАЗИНО ====================
@bot.message_handler(func=lambda m:m.text=="🎰 Казино")
def casino(m):
    bot.send_message(m.chat.id,"🎰 Введи ставку (любое число💰):")
    bot.register_next_step_handler(m,casino_play)

def casino_play(m):
    u=get_user(m.from_user.id,m.from_user.username)
    try:
        bet=int(m.text.replace(".","").replace(",",""))
        if bet<1: return bot.send_message(m.chat.id,"❌ Неверная ставка")
        if bet>u["money"]: return bot.send_message(m.chat.id,"❌ Недостаточно средств")
        if random.choice([True,False]):
            u["money"]+=bet
            u["wins"]+=1
            res="🎉 *ПОБЕДА!*"
        else:
            u["money"]-=bet
            u["loses"]+=1
            res="💥 *ПРОИГРЫШ!*"
        save(USERS_FILE, users)
        bot.send_message(m.chat.id,f"{res}\nБаланс: {money(u['money'])}💰",parse_mode="Markdown")
    except:
        bot.send_message(m.chat.id,"❌ Введи число без точек или пробелов")

# ==================== МОИ NFT ====================
@bot.message_handler(func=lambda m:m.text=="🖼 Мои NFT")
def my_nft(m):
    uid=str(m.from_user.id)
    inv=inventory.get(uid,[])
    if not inv: return bot.send_message(m.chat.id,"📦 NFT нет")
    text="🖼 *Твои NFT:*\n\n"
    for i,n in enumerate(inv,1):
        text+=f"{i}. {n['name']} — {money(n['price'])}\n"
    bot.send_message(m.chat.id,text,parse_mode="Markdown")

# ==================== Продать NFT ====================
@bot.message_handler(func=lambda m:m.text=="🛒 Продать NFT")
def sell(m):
    uid=str(m.from_user.id)
    inv=inventory.get(uid,[])
    if not inv: return bot.send_message(m.chat.id,"❌ NFT нет")
    txt="🛒 Введи номер NFT:\n\n"
    for i,n in enumerate(inv,1):
        txt+=f"{i}. {n['name']} ({money(n['price'])})\n"
    bot.send_message(m.chat.id,txt)
    bot.register_next_step_handler(m,do_sell)

def do_sell(m):
    uid=str(m.from_user.id)
    try:
        i=int(m.text)-1
        nft=inventory[uid].pop(i)
        users[uid]["money"]+=nft["price"]
        save(USERS_FILE,users)
        save(INV_FILE,inventory)
        bot.send_message(m.chat.id,f"✅ Продано за {money(nft['price'])}💰")
    except:
        bot.send_message(m.chat.id,"❌ Ошибка")

# ==================== ДОБАВЛЯЕМ ДОНАТ ====================
@bot.message_handler(func=lambda m:m.text=="💎 Донат")
def donate(m):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💳 Купить", url="https://t.me/mqsherdb"))
    bot.send_message(m.chat.id,"💎 Донат-магазин",reply_markup=kb)

print("BOT STARTED")
bot.infinity_polling()
