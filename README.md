# pandas-stock-visualization

Visualizes stock data from a csv using Matplotlib.
Smoothes the data using hull moving average.
Identifies local minima and maxima from the smoothed data and then looks for the ABCD stock pattern to identify points to buy and sell.
Backtests the trading strategy with the historical data and graphs the buying and selling points.

While this strategy proved to be unprofitable from this backtest, I learned more about Pandas and Matplotlib through making this project.

Free historical stock data can be obtained from dukascopy.com and saved as a csv to be used with this program. The program is designed to work with dukascopy's minute data.
