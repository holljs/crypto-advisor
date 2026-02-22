import ccxt
import pandas as pd
import time
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# --- ЗАГРУЗКА НАСТРОЕК ---
load_dotenv() 

TOKEN = os.getenv('TG_TOKEN')
CHAT_ID = os.getenv('TG_ID')

# ТЕПЕРЬ ТУТ СПИСОК (LIST) МОНЕТ!
SYMBOLS = [
    'BTC/USDT',  # Биткоин
    'ETH/USDT',  # Эфириум
    'TON/USDT',  # Тонкоин (Телеграм)
    'SOL/USDT'   # Солана (быстрая и модная)
]

TIMEFRAME = '1h'        
CHECK_INTERVAL = 3600   # Проверка раз в час

def send_telegram(message):
    if not TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        pass

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_market(symbol):
    try:
        exchange = ccxt.bybit()
        bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        df['rsi'] = calculate_rsi(df['close'])
        
        current_price = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        now = datetime.now().strftime("%H:%M")

        print(f"[{now}] {symbol} | Цена: {current_price} | RSI: {current_rsi:.2f}")

        # Сигналы
        if current_rsi < 30:
            msg = f"🟢 {symbol}\nЦена: {current_price}\nRSI: {current_rsi:.2f}\nМожно брать (дешево)!"
            send_telegram(msg)
        elif current_rsi > 70:
            msg = f"🔴 {symbol}\nЦена: {current_price}\nRSI: {current_rsi:.2f}\nЛучше продать (дорого)!"
            send_telegram(msg)
            
    except Exception as e:
        print(f"Ошибка с {symbol}: {e}")

if __name__ == "__main__":
    print("Мульти-бот запущен...")
    send_telegram("🚀 Бот теперь следит за BTC, ETH, TON и SOL!")
    
    while True:
        # Проверяем КАЖДУЮ монету из списка
        for coin in SYMBOLS:
            check_market(coin)
            time.sleep(5) # Маленькая пауза между монетами
            
        print(f"Жду {CHECK_INTERVAL} секунд...")
        time.sleep(CHECK_INTERVAL)
