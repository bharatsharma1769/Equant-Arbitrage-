import time
import pandas as pd
contractfx = 'SGX|Z|UC|MAIN'
contractINE = 'INE|Z|BC|MAIN'
contractLME = 'LME|F|CA|3M'
account1 = 'TCOMP2'
account2 = 'TESTING2'
price_bfr = 0.0
price = 0.0
INE_qty = 0
LME_qty = 0
ratio = 0
INEtraded_qty = 0
LMEtraded_qty = 0
INEfilled_orders=[]
INEunfilled_orders=[]
LMEfilled_orders=[]
LMEunfilled_orders=[]
c1,c2,c=0,0,0
ci,cl=0,0
margin = 0.0

def initialize(context): 
    filepath = r'C:\Users\hp\Downloads\Project 2\Project 2\Timed Order Input.xlsx' # path of the file containing the particulars
    df = pd.read_excel(filepath,engine = 'openpyxl')
    account1 = df['Value'][2]
    account2 = df['Value'][3]
    contractINE = df['Value'][4]
    contractLME = df['Value'][5]
    contractfx = df['Value'][6]
    price_bfr = df['Value'][7]
    price = df['Value'][8]
    LME_qty = df['Value'][9]  #Quantity of lots to be sold/bought for contractLME
    ratio = df['Value'][10]  #ratio of the number of contracts in the two markets 
    margin = df['Value'][11] 
    SetActual()
    SetUserNo(account1, account2)
    SubQuote(contractfx, contractINE, contractLME)
    SetTriggerType(3, 1000)
    
def handle_data(context):
    global price, qty, l1, l2,INEtraded_qty,LMEtraded_qty,INE_qty,LME_qty,c,c1,c2,ci,cl,INEfilled_orders,INEunfilled_orders,LMEfilled_orders,LMEunfilled_orders,ratio
    INE_qty = ratio*LME_qty  #Quantity of contracts to be bought/sold in contractINE 
    INEBidPrice = Q_BidPrice(contractINE)
    LMEAskPrice = Q_AskPrice(contractLME)
    INEAskPrice = Q_AskPrice(contractINE)
    LMEBidPrice = Q_BidPrice(contractLME)
    fx = Q_Last(contractfx)
   
    diff1 =  INEBidPrice/fx - (LMEAskPrice) + price_bfr #calculating the price difference
   
    LogInfo(f"The price difference is: {diff1}")
    total_Sell_pos = A_SellPosition(contractINE,account1)
    total_Buy_pos = A_BuyPosition(contractINE,account1)
    if total_Buy_pos and c1==0 and c==0 : 
        total_pos = A_BuyPosition(contractINE,account1)
        crr_pos = A_TodayBuyPosition(contractINE,account1) 
        if(total_pos):    
            A_SendOrder(Enum_Sell(),Enum_ExitToday(),crr_pos,INEBidPrice,contractINE,account1) #closing any existing long positions
            diff = total_pos-crr_pos
            if (diff!=0):
               A_SendOrder(Enum_Sell(),Enum_Exit(),diff,INEBidPrice,contractINE,account1)
            LogInfo(f"{total_pos} contracts sold at {INEBidPrice}. The position is closed")
            c1+=1
    elif total_Sell_pos and c2==0 and c==0:
        total_pos = A_SellPosition()
        crr_pos = A_TodaySellPosition() 
        if(total_pos):    
            A_SendOrder(Enum_Buy(),Enum_ExitToday(),crr_pos,INEAskPrice,contractINE,account1) #closing any existing short positions
            diff = total_pos-crr_pos
            if (diff!=0):
               A_SendOrder(Enum_Buy(),Enum_Exit(),diff,INEAskPrice,contractINE,account1)
            LogInfo(f"{total_pos} contracts bought at {INEAskPrice}. The position is closed")
            c2+=1
    
    c+=1
    if(abs(diff1) >= price):  #check if price difference is equal to target difference
        ask_price = Q_AskPrice(contractINE)
        ask_vol = int(Q_AskVol(contractINE))     
        if (ask_vol+ci) <= INE_qty :
            a,i = A_SendOrder(Enum_Buy(),Enum_Entry(),ask_vol,ask_price,contractINE,account1) #taking long position on contractINE
            ci+=ask_vol
            time.sleep(0.5)
            status = A_OrderStatus(i)
            LogInfo(status)
            if (status=='6'):
                INEfilled_orders.append(i)
                INEtraded_qty = INEtraded_qty+ask_vol
                LogInfo(f"{ask_vol} contracts bought at {ask_price}. Current position in INE: {INEtraded_qty}")
            else:
                INEunfilled_orders.append(i) #seperating the unfilled orders
                
        elif(ci<INE_qty):     
            a1 = INE_qty - ci
            if a1!=0:
                a,i = A_SendOrder(Enum_Buy(),Enum_Entry(),a1,ask_price,contractINE,account1)
                ci+=a1
                time.sleep(0.5)
                status = A_OrderStatus(i)
                if (status=='6'):
                    INEfilled_orders.append(i)
                    INEtraded_qty+=a1
                    LogInfo(f"{a1} contracts bought at {ask_price}. Current position in INE: {INEtraded_qty}")    
                else:
                    INEunfilled_orders.append(i) 
               
        bid_vol = int(Q_BidVol(contractLME))
        bid_price = Q_BidPrice(contractLME)
        if (bid_vol+cl) <= LME_qty:
            a,i = A_SendOrder(Enum_Sell(),Enum_Entry(),bid_vol,bid_price,contractLME,account2)  #taking short position on contractINE
            cl+=bid_vol
            time.sleep(0.5)
            status = A_OrderStatus(i)
            if (status=='6'):
                LMEfilled_orders.append(i)
                LMEtraded_qty = LMEtraded_qty+bid_vol
                LogInfo(f"{bid_vol} contracts sold at {bid_price}. Current position in LME: {LMEtraded_qty}")
            else:
                LMEunfilled_orders.append(i) 
                   
        
        elif(cl<LME_qty):    
            a1 = LME_qty - cl
            if(a1!=0):
                a,i = A_SendOrder(Enum_Sell(),Enum_Entry(),a1,bid_price,contractLME,account2)
                cl+=a1
                time.sleep(0.5)
                status = A_OrderStatus(i)
                if (status=='6'):
                    LMEfilled_orders.append(i)
                    LMEtraded_qty+=a1
                    LogInfo(f"{a1} contracts sold at {bid_price}. Current position in LME: {LMEtraded_qty}")
                else:
                    LMEunfilled_orders.append(i) 
                

    
    if ci == INE_qty and cl == LME_qty:
        if len(INEunfilled_orders):  #check if there are unfilled orders
          
           for i in INEunfilled_orders:
             if(A_OrderStatus(i)!='6'): 
               filled = A_OrderFilledLot(i)
               fill_price = A_OrderFilledPrice(i)
               unfill = A_OrderLot(i) - filled
               if (Q_AskPrice() > fill_price):
                 new_price = fill_price + ((margin/100)*fill_price) #max price tolerance
               else:
                 new_price = fill_price
               if(Q_AskPrice() <= new_price):  
                    a,x = A_ModifyOrder(i,unfill,new_price)
                    if(a>=0):
                          INEunfilled_orders.remove(i) 
                          LogInfo(f'{unfill} lots bought at {new_price} at INE')
                    # A_DeleteOrder(i)
                    # a,x = A_SendOrder(Enum_Buy(),Enum_Entry(),unfill,new_price,contractINE,account1)
                    # time.sleep(0.5)
                    # if(A_OrderStatus(x) == '6'):
                    #     INEfilled_orders.append(x) 
                    #     INEtraded_qty = INEtraded_qty+unfill
                    #     LogInfo(f"{unfill} contracts bought at {new_price}. Current position in INE: {INEtraded_qty}")
                    # else:
                    #     INEunfilled_orders.append(x)  
               elif(filled!=0):
                    A_DeleteOrder(i)
                    a,x = A_SendOrder(Enum_Sell(),Enum_ExitToday(),filled,Q_BidPrice(),contractINE,account1) #if price out of range, close the position
                    LogInfo("The position at INE is being closed")
                    ci = ci-filled
             else:  
                    INEunfilled_orders.remove(i) 
        if len(LMEunfilled_orders): 
           
           for i in LMEunfilled_orders:
             if(A_OrderStatus(i)!='6'): 
               filled = A_OrderFilledLot(i)
               fill_price = A_OrderFilledPrice(i)
               unfill = A_OrderLot(i) - filled
               if (Q_BidPrice() < fill_price):
                 new_price = fill_price - ((margin/100)*fill_price)
               else:
                 new_price = fill_price
               if (new_price<=Q_BidPrice()):
                   a,x = A_ModifyOrder(i,unfill,new_price) #place order at updated price
                   if(a>=0): 
                       LMEunfilled_orders.remove(i)
                       LogInfo(f'{unfill} lots sold at {new_price} at LME')
                    # a,x = A_SendOrder(Enum_Sell(),Enum_Entry(),unfill,new_price,contractLME,account2)
                    # time.sleep(0.5)
                    # if(A_OrderStatus(x) == '6'):
                    #     LMEfilled_orders.append(x) 
                    #     LMEtraded_qty = LMEtraded_qty+unfill
                    #     LogInfo(f"{unfill} contracts bought at {new_price}. Current position in LME: {LMEtraded_qty}")
                    # else:
                    #     LMEunfilled_orders.append(x)  
               elif(filled!=0):
                    A_DeleteOrder(i)
                    a,x = A_SendOrder(Enum_Buy(),Enum_Exit(),filled,Q_AskPrice(),contractLME,account2) 
                    LogInfo("The position at LME is being closed") 
                    cl = cl-filled     
             else:  
                    LMEunfilled_orders.remove(i)   
        if(len(INEunfilled_orders) == 0 and len(LMEunfilled_orders) == 0):
            raise SystemExit(0)

def exit_callback(context):
    LogInfo('Order Executed')
    


