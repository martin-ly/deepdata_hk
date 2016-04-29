-- =============================================
-- Author:      <Author,,Name>
-- Create date: <Create Date,,>
-- Description: <Description,,>
-- =============================================
ALTER PROCEDURE [dbo].[searchHolderStock]
    @stockcode char(10),
    @nametype int,
    @nameFiled nchar(50),
    @shareType int,
    @startingdate int,
    @enddate int,
    @sortBy varchar(50)
AS
BEGIN
    set nocount on
    declare @sql nvarchar(4000)
    set @sql='select stockcode,tname,capicity,changeDate,left(EventCode,charindex(''('',eventcode)-1),classofshares,AvgPrice,changeQtyL,holdQtyL,issuerPerL,changePerL,changeQtyS,holdQtyS,issuerPerS,changePerS,changeQtyP,holdQtyP,issuerPerP,changePerP from DeepStockHolder where 1=1 '

    if @shareType >0 and @shareType<4
        set @sql=@sql+' and capicity='+convert(char(1),@shareType)

    if Len(Ltrim(Rtrim(isnull(@stockcode,''))))>0
        set @sql=@sql+' and stockcode='''+@stockcode+''''

    if @nametype=0 and Len(Ltrim(Rtrim(isnull(@nameFiled,''))))>0
        set @sql=@sql+' and (ename =N'''+rtrim(ltrim(@nameFiled))+''' or tname=N'''+rtrim(ltrim(@nameFiled))+''' or sname=N'''+rtrim(ltrim(@nameFiled))+''')'
    if @nametype=1 and Len(Ltrim(Rtrim(isnull(@nameFiled,''))))>0
        set @sql=@sql+' and  ename=N'''+rtrim(ltrim(@nameFiled))+''''
    if @nametype=2 and Len(Ltrim(Rtrim(isnull(@nameFiled,''))))>0
        set @sql=@sql+' and  sname=N'''+rtrim(ltrim(@nameFiled))+''''
    if @nametype=3 and Len(Ltrim(Rtrim(isnull(@nameFiled,''))))>0
        set @sql=@sql+' and  tname=N'''+rtrim(ltrim(@nameFiled))+''''
    if  @nametype=4 and Len(Ltrim(Rtrim(isnull(@nameFiled,''))))>0
        set @sql=@sql+' and  capacity=N'''+rtrim(ltrim(@nameFiled))+''''


    if @startingdate>0
        set @sql=@sql+' and  Convert(int,isnull(Convert(char(8),changeDate,112),0))>='+convert(char(8),@startingdate)
    if @enddate>0
        set @sql=@sql+' and  Convert(int,isnull(Convert(char(8),changeDate,112),0))<='+convert(char(8),@enddate)
    if Len(Ltrim(Rtrim(isnull(@sortBy,''))))>0
        set  @sql=@sql+' Order By '+@sortBy
    print @sql
  Exec(@sql)
END
