import time

def market_making_algorithm(exchange, inventory_threshold, market_depth):
    while True:
        # Check if inventory is below the minimum threshold
        if exchange.get_inventory() < inventory_threshold:
            print("Pausing algorithm due to low inventory")
            break
        
        order_book = exchange.get_order_book()
        buy_pressure = sum([order['volume'] for order in order_book['bids']])
        sell_pressure = sum([order['volume'] for order in order_book['asks']])
        current_price = (order_book['bids'][0]['price'] + order_book['asks'][0]['price']) / 2

        # Calculate target spread
        target_spread = current_price * 0.0005  # 0.05% of the current price

        # Extract 50% of buy pressure by selling
        if buy_pressure > sell_pressure:
            sell_volume = 0.5 * buy_pressure
            exchange.place_order('sell', current_price + target_spread / 2, sell_volume)

        # Mitigate 15% of sell pressure by buying
        if sell_pressure > buy_pressure:
            buy_volume = min(0.15 * sell_pressure, exchange.get_dynamic_budget())
            exchange.place_order('buy', current_price - target_spread / 2, buy_volume)

        # Ensure market depth of ~24k USD on both sides
        for side in ['bids', 'asks']:
            total_volume = sum([order['price'] * order['volume'] for order in order_book[side]])
            if total_volume < 24000:  # USD
                adjust_volume = (24000 - total_volume) / current_price
                order_type = 'buy' if side == 'bids' else 'sell'
                exchange.place_order(order_type, current_price, adjust_volume)

        # Perform passive self trades during times of low volume
        if buy_pressure + sell_pressure < low_volume_threshold:
            exchange.place_order('buy', current_price - target_spread / 2, small_trade_volume)
            exchange.place_order('sell', current_price + target_spread / 2, small_trade_volume)

        time.sleep(1)  # Sleep for a second before the next cycle

# Usage
exchange = ExchangeAPI()
inventory_threshold = 100  # Example threshold
market_depth = 24000  # USD
market_making_algorithm(exchange, inventory_threshold, market_depth)
