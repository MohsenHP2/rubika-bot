from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

TOKEN = "CHAGI0BXQVIROXEPLGRKVXCUTPZPGDEDPZOUAIMUHOILYAFMKBCZMAOFZBCNPISG"
DATA_FILE = "votes.json"

# ذخیره داده‌ها
votes = {}         # {chat_id: {"yes": 0, "no": 0, "msg_id": "123"}}
voted_users = {}   # {chat_id: [user_id1, user_id2, ...]}

# ===== مدیریت ذخیره‌سازی =====
def load_data():
    global votes, voted_users
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            votes = data.get("votes", {})
            voted_users = data.get("voted_users", {})

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"votes": votes, "voted_users": voted_users}, f, ensure_ascii=False, indent=2)


# ===== وبهوک =====
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("پیام دریافت شد:", json.dumps(data, indent=2, ensure_ascii=False))

    if "update" in data:
        update = data["update"]

        # پیام جدید
        if "new_message" in update:
            msg_data = update["new_message"]
            chat_id = str(update["chat_id"])
            user_id = str(msg_data["sender_id"])
            text = msg_data.get("text", "").strip()

            if text == "/start":
                send_vote_message(chat_id)

            # مدیریت Chat Keypad
            elif text in ["👍 رای مثبت", "👎 رای منفی"]:
                vote_type = "vote_yes" if text == "👍 رای مثبت" else "vote_no"
                handle_vote(chat_id, user_id, vote_type)

    return jsonify({"status": "ok"})


# ===== ارسال پیام رأی با Chat Keypad =====
def send_vote_message(chat_id):
    if chat_id not in votes:
        votes[chat_id] = {"yes": 0, "no": 0, "msg_id": None}
        voted_users[chat_id] = []

    total_yes, total_no, total_voters = get_totals()
    text = f"اگر می‌خواهید ربات دزد و بانک ساخته شود، لطفاً رای بدهید:\n\n" \
           f"✅ رأی مثبت: {total_yes}   ❌ رأی منفی: {total_no}\n👥 کل رأی‌دهنده‌ها: {total_voters}"

    url = f"https://botapi.rubika.ir/v3/{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "chat_keypad_type": "New",
        "chat_keypad": {
            "rows": [
                {"buttons":[{"id":"yes_btn","type":"Simple","button_text":"👍 رای مثبت"}]},
                {"buttons":[{"id":"no_btn","type":"Simple","button_text":"👎 رای منفی"}]}
            ],
            "resize_keyboard": True,
            "on_time_keyboard": False
        }
    }

    try:
        res = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        print("پیام رأی ارسال شد:", res.text)
    except Exception as e:
        print("خطا در ارسال پیام:", e)


# ===== مدیریت رأی =====
def handle_vote(chat_id, user_id, vote_type):
    if chat_id not in votes:
        votes[chat_id] = {"yes": 0, "no": 0, "msg_id": None}
        voted_users[chat_id] = []

    if user_id in voted_users[chat_id]:
        send_thanks(chat_id, "⚠️ شما قبلاً رای داده‌اید!")
        return

    voted_users[chat_id].append(user_id)

    if vote_type == "vote_yes":
        votes[chat_id]["yes"] += 1
    elif vote_type == "vote_no":
        votes[chat_id]["no"] += 1

    save_data()
    update_vote_message(chat_id)


# ===== آپدیت پیام رأی =====
def update_vote_message(chat_id):
    total_yes, total_no, total_voters = get_totals()
    text = f"اگر می‌خواهید ربات دزد و بانک ساخته شود، لطفاً رای بدهید:\n\n" \
           f"✅ رأی مثبت: {total_yes}   ❌ رأی منفی: {total_no}\n👥 کل رأی‌دهنده‌ها: {total_voters}"

    url = f"https://botapi.rubika.ir/v3/{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "chat_keypad_type": "New",
        "chat_keypad": {
            "rows": [
                {"buttons":[{"id":"yes_btn","type":"Simple","button_text":"👍 رای مثبت"}]},
                {"buttons":[{"id":"no_btn","type":"Simple","button_text":"👎 رای منفی"}]}
            ],
            "resize_keyboard": True,
            "on_time_keyboard": False
        }
    }

    try:
        requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        send_thanks(chat_id, "ممنون از اینکه رای دادید! 🌹")
    except Exception as e:
        print("خطا در آپدیت رأی:", e)


# ===== پیام تشکر =====
def send_thanks(chat_id, text):
    url = f"https://botapi.rubika.ir/v3/{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    except Exception as e:
        print("خطا در ارسال پیام تشکر:", e)


# ===== محاسبه مجموع کل =====
def get_totals():
    total_yes = sum(v["yes"] for v in votes.values())
    total_no = sum(v["no"] for v in votes.values())
    total_voters = sum(len(users) for users in voted_users.values())
    return total_yes, total_no, total_voters


# ===== شروع =====
load_data()
app.run(host="0.0.0.0", port=5000)
