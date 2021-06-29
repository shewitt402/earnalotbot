from environ import Env
env = Env()
from {{cookiecutter.project_slug}}.example_app.utils.robinhood_login import *
robinhood_login()
import robin_stocks.robinhood as rh
import alpaca_trade_api
alpaca = alpaca_trade_api.REST()
from {{cookiecutter.project_slug}}.example_app.utils.market_hours import *
from {{cookiecutter.project_slug}}.example_app.utils.orders import *
from {{cookiecutter.project_slug}}.example_app.utils.{{cookiecutter.project_slug}}_helpers import *
from {{cookiecutter.project_slug}}.example_app.utils.robinhood_ratings import *
from {{cookiecutter.project_slug}}.example_app.utils.tradingview_ta_ratings import *
import time

testing_bool = env.bool("TESTING", default=True)
current_holdings_dict = {}
if not testing_bool:
    try:
        current_holdings_dict = rh.account.build_holdings()
        time.sleep(float(env('RH_SLEEP')))
    except: current_holdings_dict = {}
elif testing_bool:
    try:
        portfolio = alpaca.list_positions()
        for position in portfolio:
            current_holdings_dict[position.symbol] = {
                "average_buy_price": position.avg_entry_price,
                "quantity": position.qty,
                "equity": position.market_value,
                "equity_change": position.unrealized_pl,
                "percent_change": position.unrealized_plpc,
                "price": position.current_price,
            }
        time.sleep(float(env('AL_SLEEP')))
    except: current_holdings_dict = {}

def {{cookiecutter.project_slug}}_main(
        max_buys=10, min_profit=0.01, allocation_style='two', 
        buy_time=buy_time(), hold_time=hold_time(), sell_time=sell_time()
        # adding time funcs here for testing ease. Not aesthetics haha.
    ):
    current_holdings_list = [ticker for ticker in current_holdings_dict]    
    profitable_holdings_list = profitable_holdings(current_holdings_dict, min_profit)
    if buy_time:
        projected_winners_list = projected_winners(max_buys)
        print('winners list:',projected_winners_list)
        sell_list = [
            ticker for ticker in profitable_holdings_list 
            if ticker not in projected_winners_list
            ]
        for ticker in sell_list:
            sell(ticker, current_holdings_dict)
        print('sell list:',sell_list)
        if purchasing_power():
            print("pruchasing_power() = True")
            if allocation_style == "one":
                buy_list = [ticker for ticker in projected_winners_list] 
                # ^^ optional add on: # if ticker not in current_holdings_list
                for ticker in buy_list:
                    buy_size = monetary_allocation_experiment_one(buy_list)
                    buy(ticker, buy_size)
            elif allocation_style == "two":
                for ticker in projected_winners_list:
                    print(f"getting ready to buy {ticker}")
                    buy_size = monetary_allocation_experiment_two()
                    buy(ticker, buy_size)
    elif hold_time:
        for ticker in current_holdings_dict:
            if ticker in profitable_holdings_list and projected_loss_soon(ticker):
                sell(ticker, current_holdings_dict)
    elif sell_time:
        for ticker in current_holdings_dict:
            if ticker in profitable_holdings_list and projected_loss_soon(ticker):
                sell(ticker, current_holdings_dict)
            elif earnings_coming_soon(ticker):
                sell(ticker, current_holdings_dict)
    else: print("The market is closed. Might be a holiday. Go celebrate!")

def {{cookiecutter.project_slug}}_emergency(
    emergency_safe_havens={
        'GLD':0.2, 'SLV':0.2, 'DKNG':0.2, 'KO':0.2
        },
    emergency_allocation_style='two'
    ):
    for ticker in current_holdings_dict:
        sell(ticker)
    if emergency_allocation_style == 'one':
        cash = float(rh.account.build_user_profile()['cash'])
        time.sleep(float(env('RH_SLEEP')))
        for ticker in emergency_safe_havens:
            buy_size = cash * emergency_safe_havens[ticker]
            buy(ticker, buy_size)
    elif emergency_allocation_style == 'two': # Absolutely insane
        while True:
            try:
                current_holdings_dict = rh.account.build_holdings()
                time.sleep(float(env('RH_SLEEP')))
                for ticker in current_holdings_dict:
                    if tradingview_ta_sell(ticker, exchange=False):
                        sell(ticker)
            except: pass
            top_movers_list = rh.markets.get_top_movers() # len = 2
            time.sleep(float(env('RH_SLEEP')))
            for mover in top_movers_list:
                ticker = mover['symbol']
                if (
                    tradingview_ta_buy(ticker, exchange=False) 
                    and robinhood_rating_buy(ticker)
                ):
                    buy_size = monetary_allocation_experiment_two()
                    buy(ticker, buy_size)