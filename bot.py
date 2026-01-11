user_data = {}

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) == 12)
def get_utr(m):
    utr = m.text

    cur.execute("SELECT * FROM used_utrs WHERE utr=?", (utr,))
    if cur.fetchone():
        bot.send_message(m.chat.id, "❌ UTR already used")
        return

    user_data[m.chat.id] = {"utr": utr}
    bot.send_message(m.chat.id, "💰 Enter amount you paid (example: 15, 30, 45)")

@bot.message_handler(func=lambda m: m.chat.id in user_data and m.text.isdigit())
def get_amount(m):
    amt = int(m.text)

    if amt % 15 != 0:
        bot.send_message(m.chat.id, "❌ Amount must be multiple of 15")
        return

    qty = amt // 15

    cur.execute("SELECT COUNT(*) FROM coupons")
    stock = cur.fetchone()[0]

    if stock < qty:
        bot.send_message(m.chat.id, "❌ Not enough stock")
        return

    codes = []
    for i in range(qty):
        cur.execute("SELECT code FROM coupons LIMIT 1")
        code = cur.fetchone()[0]
        cur.execute("DELETE FROM coupons WHERE code=?", (code,))
        codes.append(code)

    cur.execute("INSERT INTO used_utrs VALUES (?)", (user_data[m.chat.id]["utr"],))
    db.commit()

    msg = "✅ Payment confirmed!\n\n🎁 Your Coupons:\n"
    for c in codes:
        msg += c + "\n"

    bot.send_message(m.chat.id, msg)
    user_data.pop(m.chat.id)
