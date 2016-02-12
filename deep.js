// casperjs test deep.js --output=111.html --code=00987

var fs = require('fs');
var utils = require('utils');

var fname = casper.cli.get("output");
if (fname==undefined) {
    casper.echo('缺少输出文件名称').exit();
}

var param = casper.cli.raw.get("code");
if (param==undefined) {
    casper.echo('您想要抓取哪一只港股的深度数据？').exit();
}

casper.test.begin('券商追踪', 0, function suite(test) {
    casper.start('http://www.hkexnews.hk/sdw/search/search_sdw_c.asp', function() {
        casper.evaluate(function(code){
            document.querySelector('input#txt_stock_code').value = code;
            document.querySelector('a[href*="submit()"]').click();
        }, param);
        casper.waitForText('市場中介者/願意披露的投資者戶口持有人的紀錄:', function() {
            fs.write(fname, this.getPageContent(), 'w');
            casper.echo('OK');
        });
    });

    casper.run(function() {
        test.done();
    });
});
