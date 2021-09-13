'''
Nicole Li
May 10, 2021
Embedded Coding
Spring Master Project
main
'''

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.widgets import CheckButtons
from datetime import datetime
import numpy as np

import indicators
import tradeSim

# Find the relative minima and maxima.
def extrema(values):
    
    # At relative minima, the minima Series will hold the HMA value for that point.
    # At non-minima, the minima Series will hold nan.
    # Likewise for the maxima Series.
    minima = np.where((values.shift(1) > values) & (values.shift(-1) > values), values, np.nan);
    maxima = np.where((values.shift(1) < values) & (values.shift(-1) < values), values, np.nan);
    
    return minima, maxima;

def main():
    
    # Values that correspond to True in user input.
    trueValues = ["y", "yes", "true", "t"];
    
    # Get user input for whether to graph the transactions.
    # graph is a boolean for whether to graph the transactions.
    displayGraph = input("Display graph? (Y/N) ");
    graph = (displayGraph.lower() in trueValues);
    
    # Determine whether to import all of the lines from the spreadsheet.
    importMaximum = input("Import all data? (Y/N) ");
    if (importMaximum.lower() in trueValues):
        
        # Get the data from the spreadsheet.
        # The format of the spreadsheet is Local time, Open, High, Low, Close.
        # This will memoryerror if used with graphing.
        bidData = pd.read_csv(("SP500 bid minute candlesticks.csv"));
    else:
        
        # Get the number of lines of data to test with and import that many lines of data.
        # Around 1000 graphs quickly.
        dataImportLength = int(input("Number of candlesticks to import: "));
        bidData = pd.read_csv(("SP500 bid minute candlesticks.csv"), nrows = dataImportLength);
    
    # Find the hull moving average.
    bidData["Hma"] = indicators.hullMovingAverage(bidData["Close"], 30);
    
    # Find the local extrema of the hull moving average.
    bidData["minima"], bidData["maxima"] = extrema(bidData["Hma"]);
    
    # Simulate a trade strategy that uses the extrema of the hull moving average.
    bidData["buy"], bidData["sell"] = tradeSim.trade(bidData["maxima"], bidData["minima"], bidData["Close"]);

    # Graph the candlesticks and transactions if the user requests.
    if (graph):
    
        # Set up the graph.
        fig, ax = plt.subplots();
        
        # Convert the string times from the spreadsheet to integers.
        bidData["Local time"] = bidData["Local time"].apply(convertTimestamps);

        # Local time, Open, High, Low, Close, Height (Height is difference between Open and Close)
        bidData["Height"] = bidData["Open"] - bidData["Close"];
        
        # Set up a Series to hold the candlestick colors.
        bidData["Color"] = ["",] * bidData["Local time"].size;

        # Make the increasing candlesticks green, the decreasing candlesticks red, and the neutral candlesticks gray.
        bidData.loc[bidData.Open < bidData.Close, "Color"] = "green";
        bidData.loc[bidData.Open > bidData.Close, "Color"] = "red";
        bidData.loc[bidData.Open == bidData.Close, "Color"] = "gray";
        
        # Sometimes the really small open-close bars don't appear when zoomed out, so make the small candlesticks bigger.
        bidData.loc[((bidData.Height < 0.1) & (bidData.Height >= 0)), "Height"] = 0.1;
        bidData.loc[((bidData.Height > -0.1) & (bidData.Height < 0)), "Height"] = -0.1;    
        
        # Get parts of the graph so they can have the checkbuttons to show/hide them.
        graphParts = [];
        
        # Graph the candlestick bodies.
        candlesticks = ax.bar(x=bidData["Local time"], height=bidData["Height"], width = 0.0009, bottom = bidData["Close"], color = bidData["Color"]);
        graphParts.append(candlesticks);
        
        # Make an xtick once every 60 data points from 0 to the length of bidData and label it with the corresponding bidData.
        # This used to work and I'm not sure how to fix it.
        #plt.xticks(np.arange(0, bidData["Local time"].size, 60), bidData["Local time"], rotation = 90);
        
        # Graph the candlestick wicks.
        wicks = ax.bar(x=bidData["Local time"], height=bidData["High"] - bidData["Low"], width = 0.0002, bottom = bidData["Low"], color = bidData["Color"]);
        graphParts.append(wicks);
    
        # Graph the hull moving average.
        hma = ax.plot(bidData["Local time"], bidData["Hma"], color="black");
        graphParts.append(hma);
    
        # Plot the minima and maxima.
        minima = ax.scatter(bidData["Local time"], bidData["minima"], color = "red");
        maxima = ax.scatter(bidData["Local time"], bidData["maxima"], color = "green");
        graphParts.append(minima);
        graphParts.append(maxima);
        
        # Plot the transactions.
        # Blue dots are buys and orange dots are sells.
        buyLocations = ax.scatter(bidData["Local time"], bidData["buy"], color = "blue", s = 100);
        sellLocations = ax.scatter(bidData["Local time"], bidData["sell"], color = "orange", s = 100);
        
        # Create checkbuttons that allow parts of the graph to be hidden.
        checks = plt.axes([0, 0.4, 0.1, 0.15])
        labels = ["candlesticks", "wicks", "hma", "minima", "maxima"];
        visibility = [True,] * 5;
        buttonBox = CheckButtons(checks, labels, visibility);
        
        # When checkbuttons are clicked, toggle their respective plot parts.
        buttonBox.on_clicked(lambda event: updateVisibility(event, labels, graphParts, fig));

        # Create the graph.
        plt.show();

# Make parts of the graph visible or invisible depending on the checkbuttons.
def updateVisibility(item, labels, graphParts, fig):
    
    # Select the item clicked.
    index = labels.index(item);
    
    # If the visibility of the plot can be directly set, toggle the visibility.
    if (hasattr(graphParts[index], "set_visible")):
        toggleVisibility(graphParts[index]);
    else:
        
        # Toggle the visibility of each item in the BarContainer,
        # This converts the BarContainer to a list of Rectangle objects as a side effect, and I'm not sure if that's a problem.
        graphParts[index] = list(map(lambda item: toggleVisibility(item), graphParts[index]));

# Toggle the visibility of a part.
def toggleVisibility(item):
    item.set_visible(not item.get_visible());
    return item;

# Convert csv string timestamps to integers.
def convertTimestamps(timestamp):
    
    # Original from the csv: 27.02.2018 09:07:00.000 GMT-0500
    # The csv timestamps are all at 00.000 seconds
    # year, month, day, hour, minute, second
    theDatetime = datetime(int(timestamp[6:10]), int(timestamp[3:5]), int(timestamp[:2]), int(timestamp[11:13]), int(timestamp[14:16]));
    return dates.date2num(theDatetime);

if (__name__=="__main__"):
    main();
