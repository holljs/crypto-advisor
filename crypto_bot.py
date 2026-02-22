import ccxt
import pandas as pd
import pandas_ta as ta
import time
import datetime

# --- НАСТРОЙКИ ---
SYMBOL = 'BTC/USDT'     # За чем следим
TIMEFRAME = '1h'        # Таймфрейм свечей
CHECK_INTERVAL = 3600   # Проверять раз в час (3600 секунд)

def check_market():
    try:
        # 1. Подключение
        exchange = ccxt.bybit()
        
        # 2. Получение данных
        bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['close'] = df['close'].astype(float)

        # 3. Расчет RSI
        df.ta.rsi(close='close', length=14, append=True)
        current_rsi = df['RSI_14'].iloc[-1]
        current_price = df['close'].iloc[-1]
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        print(f"[{now}] {SYMBOL} | Цена: {current_price} | RSI: {current_rsi:.2f}")

        # 4. Логика сигналов (ТУТ МОЖНО ДОБАВИТЬ ОТПРАВКУ В ТЕЛЕГРАМ)
        if current_rsi < 30:
            msg = f"🟢 {SYMBOL}: Цена упала (RSI {current_rsi:.2f}). Присмотрись!"
            print(msg) 
            # send_telegram(msg) <--- сюда потом добавим функцию отправки

        elif current_rsi > 70:
            msg = f"🔴 {SYMBOL}: Цена высока (RSI {current_rsi:.2f}). Опасно!"
            print(msg)
            # send_telegram(msg)

    except Exception as e:
        print(f"Ошибка: {e}")

# --- ЗАПУСК ВЕЧНОГО ЦИКЛА ---
if __name__ == "__main__":
    print("Бот-советник запущен...")
    while True:
        check_market()
        print(f"Жду {CHECK_INTERVAL} секунд...")
        time.sleep(CHECK_INTERVAL)
