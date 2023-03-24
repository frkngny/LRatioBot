# LRatioBot

Explanations of the functions are given in comments or as function description.


##### Possible Improvements
For opening a position simple moving average is used. What can be done:
- Use other indicators such as RSI bands, Bollinger Bands etc
- Use a different approach combined with SMA
- Change the window of the SMA
- Use logic without indicators
- Change stop profit (1-stop loss) and make it independent of stop loss

Closing a position:
- You can remove the profit factor condition since the contracts are sold depending on the profit of each contract
- Use SMA or any other indicator as a condition
- Change stop loss
