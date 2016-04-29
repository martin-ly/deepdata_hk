-- SecuritiesTraderDailyHoldStock -> DeepSecurityHolder
-- 券商追踪
delete from DeepSecurityHolder;
insert into DeepSecurityHolder select a.publishdate, b.exchangertraderno, a.stockcode, a.holdstockamount, a.issuerper, a.dayqty, a.dayper, a.weekqty, a.weekper, a.monthqty, a.monthper from SecuritiesTraderDailyHoldStock a, ExchangerTrader b where a.exchangertraderid=b.exchangertraderid;

-- stockholderRecords -> DeepStockHolder
-- 股份解码
delete from DeepStockHolder;
insert into DeepStockHolder select a.changedate, c.ename, c.tname, c.sname, b.capacity, a.changeevetcode, b.stockcode, a.avgprice, a.classofshares, a.changeqtyl, a.holdqtyl, issuerperl, null, a.changeqtys, a.holdqtys, issuerpers, null, a.changeqtyp, a.holdqtyp, issuerperp, null from stockholderRecords a, stockholder b,
 (select companyid as comstuid, ename, sname, tname from company UNION select stuffid as comstuid, ename, sname, tname from stuffs) c where a.stockholderid=b.stockholderid and b.companystuffsid=c.comstuid

-- security.shortname
-- 经纪公司简称
update Security set shortname = (SELECT t.shortname_tc
FROM (SELECT a.*, ROW_NUMBER() OVER (partition by securityid ORDER BY securityid) rn FROM
 (SELECT * FROM (select a.securityid, a.shortname, a.ename, a.sname, a.tname, b.shortname_tc from Security a left join
 (select c.shortname_tc, d.exchangertraderno from tbEconomy c, ExchangerTrader d where c.companyid=d.companyid) b
 on a.securityid=b.exchangertraderno) AS newtable) a) t where t.rn=1 and Security.securityid=t.securityid)

-- 检查原始表中结算编号与简称的对应关系
select a.name_tc, a.shortname_tc, c.securityid from tbEconomy a, ExchangerTrader b, Security c where a.companyid=b.companyid and c.securityid=b.ExchangerTraderNo and c.securityid='B01977'