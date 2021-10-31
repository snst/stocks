from investor_constants import *


class Investor():
    def __init__(self, df, settings):
        self.df = df
        self.settings = settings

    def reset(self):
        self.cnt_stocks = 0.0
        self.cnt_sell = 0
        self.cnt_buy = 0
        self.sum_cash = 0.0
        self.sum_depot = 0.0
        self.sum_invested = 0.0
        self.brutto_balance = 0.0
        self.current_index = None
        self.last_index = None
        self.last_stock_price_action = 0.1
        self.df[D_BUY_PERCENT] = 0.0
        self.df[D_SELL_PERCENT] = 0.0
        self.df[D_LAST_ORDER_PRICE] = 0.0
        self.df[D_INVESTED] = 0.0
        self.df[D_DEPOT] = 0.0
        self.df[D_BALANCE_BRUTTO] = 0.0
        self.df[D_STOCK_CNT] = 0.0
        self.df[D_BUY] = 0.0
        self.df[D_SELL] = 0.0
        self.buy_list = []
        self.tax_profit = 0.0
        self.tax_loss = 0.0
        self.df[D_TAX_PROFIT] = 0.0
        self.df[D_TAX_LOSS] = 0.0
        self.df[D_SELL_BALANCE] = 0.0
        self.price_name_sell = D_HIGH_3
        self.price_name_buy = D_LOW_3
        self.i = 0

    def calc_percent(self, old, new):
        return float((100.0 * new / old) - 100.0)

    def get(self, index, column):
        return self.df.at[index, column]

    def buy(self, index, stock_price, val):
        self.last_stock_price_action = stock_price
        self.cnt_buy += 1
        self.sum_depot += val
        self.sum_invested += val
        stock_cnt = (val / stock_price)
        self.cnt_stocks += stock_cnt
        self.buy_list.append((stock_cnt, stock_price))
        return val

    def sell(self, index, stock_price, val):
        self.last_stock_price_action = stock_price
        self.cnt_sell += 1
        self.sum_depot -= val
        self.sum_invested -= val
        sell_stock_cnt = (val / stock_price)
        self.cnt_stocks -= sell_stock_cnt

        while sell_stock_cnt > 0.0 and len(self.buy_list) > 0:
            bought_stock_cnt, bought_stock_price = self.buy_list[0]
            now_sell_cnt = min(sell_stock_cnt, bought_stock_cnt)
            if sell_stock_cnt >= bought_stock_cnt:
                self.buy_list.pop(0)
            else:
                renmain_cnt = bought_stock_cnt - now_sell_cnt
                self.buy_list[0] = (renmain_cnt, bought_stock_price)
            sell_stock_cnt -= now_sell_cnt

            bought_stock_value = now_sell_cnt * bought_stock_price
            sell_stock_value = now_sell_cnt * stock_price
            balance = sell_stock_value - bought_stock_value

            if balance > 0.0:
                self.tax_profit += balance
            else:
                self.tax_loss += -balance
        return val

    def depot_value(self, stock_price):
        return self.cnt_stocks * stock_price

    def balance_value(self, stock_price):
        return self.depot_value(stock_price) - self.sum_invested

    def run(self):
        self.reset()
        self.i = 0
        for i, (index, row) in enumerate(self.df.iterrows()):
            buy_val = 0.0
            sell_val = 0.0
            stock_price_low = self.get(index, D_LOW)
            stock_price_high = self.get(index, D_HIGH)
            stock_price_open = self.get(index, D_DOPEN)
            stock_price_close = self.get(index, D_CLOSE)

            price_buy = self.get(index, self.price_name_buy)
            price_sell = self.get(index, self.price_name_sell)

            percent_buy = self.calc_percent(
                self.last_stock_price_action, price_buy)
            percent_sell = self.calc_percent(
                self.last_stock_price_action, price_sell)
            self.df.at[index, D_BUY_PERCENT] = percent_buy
            self.df.at[index, D_SELL_PERCENT] = percent_sell

            if self.sum_invested <= 0.0:
                buy_val = self.buy(
                    index, price_buy, self.settings.initial_order)
            else:
                if percent_buy < self.settings.var_buy_threshold:
                    depot_value_price_buy = self.depot_value(price_buy)
                    depot_value_last_order = self.depot_value(
                        self.last_stock_price_action)
                    loss = depot_value_last_order - depot_value_price_buy
                    val = self.settings.var_buy_factor * depot_value_price_buy
                    val = self.settings.var_buy_factor * loss

                    if val > self.settings.min_order:
                        val = min(val, self.settings.max_order)
                        val = min(val, self.settings.max_depot -
                                  self.depot_value(price_buy))
                        buy_val = self.buy(index, price_buy, val)
                    elif self.sum_depot < self.settings.initial_order:
                        val = self.settings.initial_order - \
                            self.depot_value(price_buy)
                        buy_val = self.buy(index, price_buy, val)
                elif percent_sell > self.settings.var_sell_threshold:
                    val = self.depot_value(price_sell) * \
                        self.settings.var_sell_factor
                    # if val > self.sum_invested and val > self.settings.min_order:
                    if val > self.settings.min_order:
                        sell_val = self.sell(index, price_sell, val)

            self.sum_depot = self.depot_value(stock_price_close)
            self.brutto_balance = self.balance_value(stock_price_close)

            self.df.at[index, D_INVESTED] = self.sum_invested
            self.df.at[index, D_DEPOT] = self.sum_depot
            self.df.at[index, D_BALANCE_BRUTTO] = self.brutto_balance
            self.df.at[index, D_BUY] = buy_val
            self.df.at[index, D_SELL] = sell_val
            self.df.at[index, D_STOCK_CNT] = self.cnt_stocks
            self.df.at[index, D_LAST_ORDER_PRICE] = self.last_stock_price_action
            self.df.at[index, D_TAX_PROFIT] = self.tax_profit
            self.df.at[index, D_TAX_LOSS] = self.tax_loss

            self.tax = (max(self.tax_profit - self.tax_loss, 0.0)
                        * self.settings.tax) / 100.0
            self.trading_cost = (self.cnt_buy + self.cnt_sell) * \
                self.settings.order_costs
            self.netto_balance = self.brutto_balance - self.trading_cost
            - self.tax
            self.df.at[index, D_BALANCE_NETTO] = self.netto_balance
            self.i += 1

        return self.netto_balance

    def print(self):
        print(self.df)
        print(f'var_buy_threshold={self.var_buy_threshold:.2f}')
        print(f'var_sell_threshold={self.var_sell_threshold:.2f}')
        print(f'var_buy_factor={self.var_buy_factor:.2f}')
        print(f'cnt_sell={self.cnt_sell:.2f}')
        print(f'cnt_buy={self.cnt_buy:.2f}')
        print(f'sum_invested={self.sum_invested:.2f}')
        print(f'sum_depot={self.sum_depot:.2f}')
        print(f'brutto_balance={self.brutto_balance:.2f}')
