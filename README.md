This is a simple arbitrage strategy for commodities trading developed on Equant, which uses the Esunny 9.5 trading platform. The particulars of the strategy like the accounts to be used, contracts to be bought/sold, price buffer, the ratio of contracts, and tolerance margin can be inputted through an Excel file, making it trivial to implement. In this case, I have used INE(long) and LME(short) crude oil contracts, and the SGX forex contract for currency conversion, but the code can be applied to any market or commodity with slight modifications, as long as it's run on Equant. Special attention has to be paid to the 'ratio' parameter, which will change with different markets eg., one contract at LME is worth 5 contracts at INE, so the quantity to be traded has to be adjusted accordingly. In case the orders cannot be filled for some reason, the strategy will automatically close the existing positions in the concerned market, and will try to refill them once the target difference hits.     