import pandas

Current_stock = 0
# Put any initialization logic here.  The context object will be passed to
# the other methods in your algorithm.
def initialize(context):
    context.sids = [sid(8655), sid(5923), sid(7797), sid(8229), sid(5484), sid(7488), sid(3136), sid(438), sid(3806), sid(3499)]
    context.long = {}
    context.short = {}
    context.stop_loss = 1
    context.take_profit = 3
    context.max_notional = 10000.1
    context.min_notional = -10000.0
    set_commission(commission.PerTrade(cost=7))
    context.database = {}
    #the RSI is calculated based on the security's returns over a set number
    #of preceding observations.  Here we're setting up an array to collect the
    #preceding 6 ticks to allow us to calc the preceding 5 period returns
    context.tick_history = {}

# Will be called on every trade event for the securities you specify.
def handle_data(context, data):
    acc_rsi=0

    for stock in context.sids:
        global Current_stock
        Current_stock = int(str(stock)[9:-1])

        if Current_stock not in context.database:
            context.database[Current_stock] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        context.database[Current_stock].insert(0, data[stock].price)
        context.database[Current_stock].pop()
        preceding_prices = context.database[Current_stock]

        if preceding_prices[len(preceding_prices)-1] <> 0:
            #create and populate an array of returns from our prices
            returns = [(preceding_prices[i-1]-preceding_prices[i]) for i in range(1,len(preceding_prices))]
            up = []
            down = []
            for i in range(len(returns)):
                if returns[i] > 0:
                    up.append(round(returns[i],2))
                elif returns[i] <= 0:
                    down.append(round(returns[i]*-1,2))

            if len(up) == 0:
                rsi = 0
            elif len(down) == 0:
                rsi = 100

            else:
                av_up = sum(up) / len(up)
                av_down = sum(down) / len(down)

                if av_down == 0:
                    rsi = 100
                elif av_up == 0:
                    rsi = 0
                else:
                    rs = av_up / av_down
                    rsi = 100 - (100 / (1 + rs))

        else:
            rsi = 50

        acc_rsi += rsi



        notional = context.portfolio.positions[stock].amount * data[stock].price

        if stock not in context.long and stock not in context.short and notional < context.max_notional and notional > context.min_notional:
            if rsi < 30:
                order(stock, 100)
                log.info("Long %f, %s" %(data[stock].price, stock))
                context.long[stock] = data[stock].price
            elif rsi > 70:
                order(stock, -100)
                log.info("Short %f, %s" %(data[stock].price, stock))
                context.short[stock] = data[stock].price

        if stock in context.long:
            if context.long[stock] - data[stock].price > context.stop_loss:
                order(stock, -100)
                log.info("LONG Stop loss at %f, %s" %(data[stock].price, stock))
                context.long.pop(stock)
            elif data[stock].price - context.long[stock] > context.take_profit:
                order(stock, -100)
                log.info("LONG Take profit at %f, %s" %(data[stock].price, stock))
                context.long.pop(stock)
        elif stock in context.short:
             if data[stock].price - context.short[stock] > context.stop_loss:
                order(stock, 100)
                log.info("SHORT Stop loss at %f, %s" %(data[stock].price, stock))
                context.short.pop(stock)
             elif context.short[stock] - data[stock].price > context.take_profit:
                order(stock, 100)
                log.info("SHORT Take profit at %f, %s" %(data[stock].price, stock))
                context.short.pop(stock)

    record(RSI=rsi)