'''
tradeSim.py
'''

import numpy as np

# Position sizer. Sizes positions at the maximum that can be purchased with current funds without going negative.
def positionSize(money, stock, price, quantityType):
    if (quantityType == "max"):
        stock += int(money / price);
        money -= int(money / price) * price;
    return money, stock;

# Simulate buying and selling the stock when conditions are met.
def trade(maxima, minima, closes):
    money = 10000;
    originalMoney = money;
    stock = 0;
    
    # Merge the minima and maxima Series.
    extrema = maxima.fillna(minima);
    
    # Convert the extrema to a dictionary.
    extremaDict = extrema.to_dict();
    
    # Remove the nan values from the extrema dictionary.
    # Keys are still the original indices.
    extremaDict = {i: extremaDict[i] for i in extremaDict if not np.isnan(extremaDict[i])}
    
    # Determine whether the first extrema point is a minima.
    firstMinima = int(extrema.first_valid_index() != minima.first_valid_index());
    
    # Get a list of the dictionary keys.
    extremaDictKeys = list(extremaDict.keys());
    
    # Create arrays to hold buy and sell locations.
    buyLocations = [];
    sellLocations = [];
    
    # How long to hold the buys after buying.
    holdLength = 20;
    
    # Create and open the tradeLog and start appending data.
    trades = open("tradeLog.txt", "a");
    trades.write("----- start -----");
    
    # Buy when the ABCD pattern forms and sell after holdLength number of minutes.
    for i in range(firstMinima, len(extremaDictKeys), 2):
        try:
            # If for 4 consecutive extrema, starting with every maxima, the most recent minima is greater than the previous minima and the most recent maxima is greater than the previous maxima (ABCD pattern), sell all current holdings.
            if ((extremaDict[extremaDictKeys[i]] > extremaDict[extremaDictKeys[i - 2]]) and ((extremaDict[extremaDictKeys[i - 1]] > extremaDict[extremaDictKeys[i - 3]]))):
                money, stock = buy(closes, extremaDictKeys[i], money, stock, trades);
                buyLocations.append(extremaDictKeys[i] + 1);
                
                # If 20 candlesticks have passed since the selling, buy.
                if (i + holdLength <= closes.size - 2):
                    money, stock = close(closes, extremaDictKeys[i + holdLength], money, stock, trades);
                    sellLocations.append(extremaDictKeys[i] + 1 + holdLength);
                
        # The exeception always happens and I'm not sure how to fix it.
        except Exception as e:
            print(e);
    
    # Close all trades at the end.
    money, stock = close(closes, closes.size - 2, money, stock, trades);
    sellLocations.append(closes.size - 1);
    
    # Log the final profit.
    trades.write("\nfinal profit: ");
    trades.write("%.4f" % ((money - originalMoney) * 100 / originalMoney));
    trades.write("%");
    
    # Create sparse arrays from the arrays of buy and sell locations.
    # The sparse arrays are True where a buy/sell was executed and False everywhere else.
    buyLocationsSparse = np.array([False] * closes.size);
    sellLocationsSparse = np.array([False] * closes.size);
    buyLocationsSparse[buyLocations] = True;
    sellLocationsSparse[sellLocations] = True;
    
    # For the values of the sparse arrays that are True, insert the close of their corresponding candlestick.
    # For the values of the sparse arrays that are False, insert nan.
    buys = np.where(buyLocationsSparse, closes, np.nan);
    sells = np.where(sellLocationsSparse, closes, np.nan);
    
    # Finish and close the tradeLog.
    trades.write("\n\n");
    trades.close();
    
    # Return the transactions.
    return buys, sells;

# Simulate buying using the close of the next candlestick.
def buy(closes, index, money, stock, trades):
    
    # Use the next candlestick so "time travel" isn't simulated.
    index += 1;
    
    # Buy the maximum amount of stock possible without going into negative money.
    money, stock = positionSize(money, stock, closes[index], "max");
    
    # Log the transaction.
    trades.write("\n\nbuy at index ");
    trades.write(str(index));
    trades.write("\nbuying price: $");
    trades.write(str(closes[index]));
    trades.write("\nmoney: $");
    trades.write(str(money));
    trades.write("\nstock: ");
    trades.write(str(stock));
    
    # Return the updated money and stock quantity.
    return money, stock;

# Simulate selling all current holdings.
def close(closes, index, money, stock, trades):
    
    # Use the next candlestick so "time travel" isn't simulated.
    index += 1;
    
    # Sell all current stock and add it to the money.
    money += closes[index] * stock;
    stock = 0;
    
    # Log the transaction.
    trades.write("\n\nclose at index ");
    trades.write(str(index));
    trades.write("\nclosing price: $");
    trades.write(str(closes[index]));
    trades.write("\nmoney: $");
    trades.write(str(money));
    trades.write("\nstock: 0");

    # Return the updated money and stock quantity.
    return money, stock;
