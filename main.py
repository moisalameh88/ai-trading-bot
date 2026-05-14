import requests
import ccxt
import pandas as pd
import ta
import time
from binance.client import Client

# =========================
# BINANCE API
# =========================

API_KEY = "0AfsX9q4aBSs5lXdGMldBPtl1kdiOAJ3nkqYAspZwQP4ajQAdcGvcTgw9gx20ov4"
API_SECRET = "7HbuL3yoyYGsPkteG3zxUckY4HqnsJ52tJLQV2D6z2cyMM8GMdUsPyzQpfRwlnlu"

client = Client(API_KEY, API_SECRET)

# =========================
# TELEGRAM
# =========================

TELEGRAM_BOT_TOKEN = "8872438664:AAFlrUIeI1sYCQRYq7PAONGxpFknu8kp8N4"
TELEGRAM_CHAT_ID = "7289083098"

# =========================
# TELEGRAM FUNCTION
# =========================

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)

# =========================
# EXCHANGE
# =========================

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

symbol = "BTC/USDT"
timeframe = "1m"

print("🚀 AI Trading Bot Started")

last_signal = "NONE"

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)

        df = pd.DataFrame(
            ohlcv,
            columns=['time', 'open', 'high', 'low', 'close', 'volume']
        )

        # =========================
        # INDICATORS
        # =========================

        df['RSI'] = ta.momentum.RSIIndicator(
            df['close']
        ).rsi()

        df['EMA20'] = ta.trend.EMAIndicator(
            df['close'],
            window=20
        ).ema_indicator()

        df['EMA50'] = ta.trend.EMAIndicator(
            df['close'],
            window=50
        ).ema_indicator()

        # =========================
        # VALUES
        # =========================

        price = df['close'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        ema20 = df['EMA20'].iloc[-1]
        ema50 = df['EMA50'].iloc[-1]

        print(f"\nBTC Price: {price}")
        print(f"RSI: {rsi:.2f}")
        print(f"EMA20: {ema20:.2f}")
        print(f"EMA50: {ema50:.2f}")

        # =========================
        # BUY SIGNAL
        # =========================

        if rsi < 30:

            if last_signal != "BUY":

                print("🟢 BUY SIGNAL")

                send_telegram_message(
f"""
🟢 BUY SIGNAL BTC/USDT

💰 Price: {price}
📈 RSI: {round(rsi,2)}

⚡ EMA20: {round(ema20,2)}
🔥 EMA50: {round(ema50,2)}

🎯 السوق في منطقة شراء
"""
                )

                # تنفيذ شراء حقيقي
                try:

                    order = exchange.create_market_buy_order(
                        symbol,
                        0.00001
                    )

                    print("✅ BUY ORDER EXECUTED")
                    print(order)

                    send_telegram_message(
                        "✅ تم تنفيذ BUY ORDER"
                    )

                except Exception as e:

                    print("❌ BUY ERROR:", e)

                    send_telegram_message(
                        f"❌ BUY ERROR:\n{e}"
                    )

                last_signal = "BUY"

        # =========================
        # SELL SIGNAL
        # =========================

        elif rsi > 70:

            if last_signal != "SELL":

                print("🔴 SELL SIGNAL")

                send_telegram_message(
f"""
🔴 SELL SIGNAL BTC/USDT

💰 Price: {price}
📉 RSI: {round(rsi,2)}

⚡ EMA20: {round(ema20,2)}
🔥 EMA50: {round(ema50,2)}

🎯 السوق في منطقة بيع
"""
                )

                # تنفيذ بيع حقيقي
                try:

                    order = exchange.create_market_sell_order(
                        symbol,
                        0.00001
                    )

                    print("✅ SELL ORDER EXECUTED")
                    print(order)

                    send_telegram_message(
                        "✅ تم تنفيذ SELL ORDER"
                    )

                except Exception as e:

                    print("❌ SELL ERROR:", e)

                    send_telegram_message(
                        f"❌ SELL ERROR:\n{e}"
                    )

                last_signal = "SELL"

        else:

            print("⚪ WAITING FOR SIGNAL")

            last_signal = "NONE"

        time.sleep(10)

    except Exception as error:

        print("❌ ERROR:", error)

        send_telegram_message(
            f"❌ BOT ERROR:\n{error}"
        )

        time.sleep(10)