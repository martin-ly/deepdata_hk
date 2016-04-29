ALTER proc [dbo].[sp_GetShortSelling]
@itemCode char(20)
as
        if isnull(@itemCode,'')=''   --get last record
        Begin
            select convert(char(8),a.issuerdate,112) as dwDate,'20:00:00' as wTime,a.stockcode ItemCode,a.shares fShare,a.shareChgPer fShareChgPer,a.amount fTurnover,a.turnoverChgPer fTurnoverChgPer,b.totalShare fTotalShare,b.totalTurnover fTotalTurnover,b.constituentTurnover ConstituentTurnover,b.marketTurnover fMarketTurnover from DeepStockShortSelling a, DeepMarketShortSelling b where a.issuerdate in(select max(issuerdate) from DeepStockShortSelling) and b.currency='HKD' and a.issuerdate=b.issuerdate and convert(char(10),a.issuerdate,121)=(select max(convert(char(10),issuerdate,121)) from DeepStockShortSelling) order by a.shares desc
        End
        else
        Begin               ----get last 2 month record by stockcode
            select convert(char(8),a.issuerdate,112) as dwDate,'20:00:00' as wTime,a.stockcode ItemCode,a.shares fShare,a.shareChgPer fShareChgPer,a.amount fTurnover,a.turnoverChgPer fTurnoverChgPer,b.totalShare fTotalShare,b.totalTurnover fTotalTurnover,b.constituentTurnover ConstituentTurnover,b.marketTurnover fMarketTurnover from DeepStockShortSelling a, DeepMarketShortSelling b where a.stockcode=@itemCode and b.currency='HKD' and a.issuerdate=b.issuerdate and DATEDIFF(mm,a.issuerdate,getdate())<2 and a.timesign=1 order by a.issuerdate desc
        End
