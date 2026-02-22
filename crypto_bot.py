import ccxt
import pandas as pd
import time
from datetime import datetime

# --- НАСТРОЙКИ ---
SYMBOL = 'BTC/USDT'     # За чем следим
TIMEFRAME = '1h'        # Таймфрейм свечей
CHECK_INTERVAL = 60     # Проверять раз в минуту (для тестов)

def calculate_rsi(series, period=14):
    """
    Математическая магия: считаем RSI вручную.
    Нам не нужна библиотека pandas_ta!
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_market():
    try:
        # 1. Подключение
        exchange = ccxt.bybit()
        
        # 2. Получение данных
        bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # 3. Считаем RSI сами
        df['rsi'] = calculate_rsi(df['close'])
        
        current_price = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        now = datetime.now().strftime("%H:%M:%S")

        print(f"[{now}] {SYMBOL} | Цена: {current_price:.2f} $ | RSI: {current_rsi:.2f}")

        # 4. Логика сигналов
        if current_rsi < 30:
            print("🟢 СИГНАЛ: ЦЕНА УПАЛА! (Перепроданность)")
        elif current_rsi > 70:
            print("🔴 СИГНАЛ: ЦЕНА ВЫСОКА! (Перекупленность)")
            
    except Exception as e:
        print(f"Ошибка: {e}")

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Бот запущен! Жми Ctrl+C, чтобы остановить.")
    while True:
        check_market()
        time.sleep(CHECK_INTERVAL)
