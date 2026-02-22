import ccxt
import pandas as pd
import time
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# --- ЗАГРУЗКА НАСТРОЕК ---
load_dotenv() # Эта команда ищет файл .env и читает его

TOKEN = os.getenv('TG_TOKEN')
CHAT_ID = os.getenv('TG_ID')

SYMBOL = 'BTC/USDT'     
TIMEFRAME = '1h'        
CHECK_INTERVAL = 3600   # Проверка раз в час

# --- ФУНКЦИЯ ОТПРАВКИ В ТЕЛЕГРАМ ---
def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("⚠️ Ошибка: Нет токена или ID в файле .env")
        return
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Не удалось отправить сообщение: {e}")

# --- ФУНКЦИЯ РАСЧЕТА RSI ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- ОСНОВНОЙ ЦИКЛ ---
def check_market():
    try:
        exchange = ccxt.bybit()
        bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        df['rsi'] = calculate_rsi(df['close'])
        
        current_price = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        now = datetime.now().strftime("%d.%m %H:%M")

        log_msg = f"[{now}] {SYMBOL} | Цена: {current_price:.2f} $ | RSI: {current_rsi:.2f}"
        print(log_msg)

        # ЛОГИКА СИГНАЛОВ
        if current_rsi < 30:
            msg = f"🟢 {SYMBOL}\nЦена: {current_price}\nRSI: {current_rsi:.2f}\nРынок перепродан (дешево)! Можно искать точку входа."
            print("Отправляю сигнал на покупку...")
            send_telegram(msg)
            
        elif current_rsi > 70:
            msg = f"🔴 {SYMBOL}\nЦена: {current_price}\nRSI: {current_rsi:.2f}\nРынок перегрет (дорого)! Опасно, возможен откат."
            print("Отправляю сигнал на продажу...")
            send_telegram(msg)
            
    except Exception as e:
        print(f"Ошибка: {e}")
        send_telegram(f"⚠️ Бот упал с ошибкой: {e}")

if __name__ == "__main__":
    print("Бот-советник запущен...")
    send_telegram(f"🚀 Бот {SYMBOL} запущен и следит за рынком!")
    while True:
        check_market()
        time.sleep(CHECK_INTERVAL)
