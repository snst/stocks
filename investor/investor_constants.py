D_CLOSE = 'Close'
D_HIGH = 'High'
D_LOW = 'Low'
D_CLOSE_SCALED = 'Close scaled'
D_SPREAD = 'Spread'
D_LOW_3 = 'Low3'
D_HIGH_3 = 'High3'
D_CLOSE_DELTA_PERCENT = 'Close delta %'
D_DOPEN = 'Open'
D_STOCK_CNT = 'Stock cnt'
D_INVESTED = 'Invested'
D_BALANCE_BRUTTO = 'Balance brutto'
D_BALANCE_NETTO = 'Balance netto'
D_DEPOT = 'Depot'
D_BUY = 'Buy'
D_SELL = 'Sell'
D_BUY_PERCENT = 'Buy %'
D_SELL_PERCENT = 'Sell %'
D_TAX_WON = 'Tax won'
D_TAX_LOSS = 'Tax loss'
D_SPREAD_BAR = 'Spread bar'
D_SELL_BALANCE = 'Sell balance'
D_LAST_ORDER_PRICE = 'Last order price'

SETTINGS_FILENAME = 'settings.yml'

ALL_STOCKNAMES = ['BAS.DE', 'ALV.DE', 'MTX.DE', 'BAYN.DE', 'HEI.DE', 'HFG.DE', 'DBK.DE', 'DB1.DE', 'CON.DE', 'MRK.DE', 'FRE.DE',
                  'SY1.DE', 'ADS.DE', 'SHL.DE', '1COV.DE', 'DTE.DE', 'SIE.DE', 'DWNI.DE', 'ENR.DE', 'FME.DE', 'PUM.DE', 'RWE.DE', 'DPW.DE', 'AIR.DE',
                  'ZAL.DE', 'LIN.DE', 'BMW.DE', 'IFX.DE', 'VOW3.DE', 'DHER.DE']

ALL_COLUMNS = [D_DOPEN, D_CLOSE, D_CLOSE_SCALED, D_CLOSE_DELTA_PERCENT, D_HIGH, D_LOW, D_LOW_3, D_HIGH_3, D_SPREAD, D_SPREAD_BAR, D_SELL_BALANCE, D_TAX_WON, D_TAX_LOSS,
               D_INVESTED, D_DEPOT, D_BALANCE_BRUTTO, D_BALANCE_NETTO, D_BUY, D_SELL, D_BUY_PERCENT, D_SELL_PERCENT, D_STOCK_CNT, D_LAST_ORDER_PRICE]

# https://matplotlib.org/stable/gallery/color/named_colors.html
COLOR_MAP = {D_CLOSE: 'blue', D_BALANCE_BRUTTO: 'green', D_BUY: 'tomato',
             D_SELL: 'lawngreen', D_DEPOT: 'black', D_SPREAD_BAR: 'lightgray'}
