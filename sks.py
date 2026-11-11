import json
import time
import urllib.request
import urllib.parse
import ssl

# ==============================================================================
# உன்னுடைய TELEGRAM & WALLET விவரங்கள் (எந்த லைப்ரரியும் இன்ஸ்டால் செய்ய வேண்டாம்!)
# ==============================================================================
TELEGRAM_BOT_TOKEN = "9231641394:AAG8Iy40KqSetb0fzivnnv4Df2wr7-3Ykos"
TELEGRAM_CHAT_ID = "8915442014"
WALLET_ADDRESS = "0xe08E415Cd6eA703b1c09F3008C1e26341e502207"

# நம்ம ஃப்ளாஷ் லோன் கணக்கு: ₹10,00,000 (10 லட்சம் ரூபாய்)
FLASH_LOAN_INR = 1000000
AAVE_FEE_INR = FLASH_LOAN_INR * 0.0005  # 0.05% Aave வட்டி = ₹500
GAS_FEE_INR = 10                        # பிளாக்செயின் கேஸ் கட்டணம் = ₹10
TOTAL_REPAY_INR = FLASH_LOAN_INR + AAVE_FEE_INR + GAS_FEE_INR  # ₹10,00,510

# உலக சந்தையில் ஸ்கேன் செய்யப்படும் முக்கிய காயின்கள் (Multi-Chain DEX Pairs)
TOKENS_TO_SCAN = ["ETH", "WBTC", "SOL", "MATIC", "AAVE", "UNI", "LINK", "ARB"]

ssl_context = ssl._create_unverified_context()

def send_telegram_msg(text):
    """டெலிகிராமுக்கு நேரடியாக மெசேஜ் அனுப்பும் ஃபங்ஷன்"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("ok"):
                print("✅ [Telegram] உன் மொபைலுக்கு மெசேஜ் அனுப்பியாச்சு!")
            else:
                print("❌ [Telegram Error]", res)
    except Exception as e:
        print(f"❌ [Telegram Failed] உன் பாட்டில் /start அழுத்தியிருக்கிறாயா என செக் செய்! Error: {e}")

def scan_global_dex_markets(symbol):
    """உலகில் உள்ள அனைத்து DEX எக்ஸ்சேஞ்சுகளிலும் (Uniswap, SushiSwap, PancakeSwap, etc.) விலையை ஒப்பிடுதல்"""
    url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}/USDC"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ssl_context, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    pairs = data.get("pairs", [])
    valid_markets = []

    for p in pairs:
        # உண்மையான லிக்விடிட்டி ($50,000+) உள்ள எக்ஸ்சேஞ்சுகளை மட்டும் எடுத்தல்
        liquidity = p.get("liquidity", {}).get("usd", 0)
        price_usd = float(p.get("priceUsd", 0) or 0)
        base_sym = p.get("baseToken", {}).get("symbol", "").upper()

        if base_sym == symbol and price_usd > 0 and liquidity and float(liquidity) > 50000:
            valid_markets.append({
                "dex": p.get("dexId", "unknown").upper(),
                "chain": p.get("chainId", "unknown").upper(),
                "price": price_usd
            })

    if len(valid_markets) < 2:
        return None

    # ஒரே चेன் (Same Chain) உள்ள எக்ஸ்சேஞ்சுகளுக்குள் விலை வித்தியாசத்தைக் கண்டுபிடித்தல்
    chains = {}
    for m in valid_markets:
        chains.setdefault(m["chain"], []).append(m)

    best_opportunity = None
    for chain_name, markets in chains.items():
        if len(markets) < 2:
            continue
        lowest = min(markets, key=lambda x: x["price"])
        highest = max(markets, key=lambda x: x["price"])

        if lowest["dex"] == highest["dex"] and lowest["price"] == highest["price"]:
            continue

        # ₹10,00,000 போட்டு கம்மியான விலையில் வாங்கி, அதிக விலையில் விற்றால் எவ்வளவு வரும்?
        coins_bought = FLASH_LOAN_INR / lowest["price"]
        gross_return_inr = coins_bought * highest["price"]
        net_profit_inr = gross_return_inr - TOTAL_REPAY_INR

        if (best_opportunity is None) or (net_profit_inr > best_opportunity["net_profit"]):
            best_opportunity = {
                "symbol": symbol,
                "chain": chain_name,
                "buy_dex": lowest["dex"],
                "buy_price": lowest["price"],
                "sell_dex": highest["dex"],
                "sell_price": highest["price"],
                "gross_return": gross_return_inr,
                "net_profit": net_profit_inr
            }

    return best_opportunity

def run_bot():
    print("🚀 பாட் ஸ்டார்ட் ஆகிவிட்டது! டெலிகிராமுக்கு முதல் மெசேஜ் போகிறது...")
    start_text = (
        f"🚀 <b>FLASH LOAN GLOBAL SCANNER STARTED!</b>\n\n"
        f"👛 <b>வாலட்:</b> <code>{WALLET_ADDRESS}</code>\n"
        f"💰 <b>ஃப்ளாஷ் லோன் தொகை:</b> ₹10,00,000\n"
        f"🏦 <b>திருப்பிக் கட்ட வேண்டியது (வட்டி+கேஸ் சேர்த்து):</b> ₹10,00,510\n\n"
        f"📡 <i>இப்போ உலக மார்க்கெட்டில் என்ன நடக்குதுன்னு ஒவ்வொரு ரவுண்டும் லைவ் ரிப்போர்ட் கீழே வரும் பாரு பங்கு!</i>"
    )
    send_telegram_msg(start_text)

    cycle = 0
    while True:
        cycle += 1
        print(f"\n🔄 [Scan Round #{cycle}] உலக எக்ஸ்சேஞ்சுகளை ஸ்கேன் செய்கிறது...")
        report_lines = [f"📊 <b>LIVE SCAN REPORT #{cycle} (₹10 லட்சம் கணக்கு)</b>\n"]
        best_overall = None

        for token in TOKENS_TO_SCAN:
            try:
                res = scan_global_dex_markets(token)
                if res:
                    status_icon = "🟢" if res["net_profit"] > 0 else "🔴"
                    report_lines.append(
                        f"{status_icon} <b>{res['symbol']} ({res['chain']})</b>\n"
                        f"   • வாங்கும் இடம்: {res['buy_dex']} (${res['buy_price']:.4f})\n"
                        f"   • விற்கும் இடம்: {res['sell_dex']} (${res['sell_price']:.4f})\n"
                        f"   • ₹10 லட்சம் மாறுவது: <b>₹{res['gross_return']:,.0f}</b>\n"
                        f"   • நிகர லாபம்/நஷ்டம்: <b>₹{res['net_profit']:,.0f}</b>\n"
                    )
                    if (best_overall is None) or (res["net_profit"] > best_overall["net_profit"]):
                        best_overall = res
            except Exception as e:
                print(f"[Skip {token}] {e}")

        if best_overall and best_overall["net_profit"] > 0:
            report_lines.append(
                f"\n🔥 <b>சான்ஸ் மாட்டிக்கிச்சு!</b> {best_overall['symbol']} காயினில் "
                f"<b>₹{best_overall['net_profit']:,.0f} நிகர லாபம்</b> இருக்கு!"
            )
        else:
            report_lines.append("\n⏳ <i>தற்போது வட்டி போக லாபம் இல்லை (Revert Safe). அடுத்த ஸ்கேன் போகிறது...</i>")

        # ஒவ்வொரு ரவுண்டும் டெலிகிராமுக்கு முழு ரிப்போர்ட் அனுப்புதல்!
        send_telegram_msg("\n".join(report_lines))
        time.sleep(10)

if __name__ == "__main__":
    run_bot()
