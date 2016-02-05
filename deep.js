// casperjs deep.js --output=111.html 00987

var fs = require('fs');
var utils = require('utils');
var casper = require('casper').create({
    logLevel: "debug",
    verbose: true
});

var fname = casper.cli.get("output");
if (fname==undefined) {
    casper.echo('缺少输出文件名称').echo('FAIL').exit();
}

var param = casper.cli.raw.args[0];

casper.start('http://www.hkexnews.hk/sdw/search/search_sdw_c.asp', function() {
//    require('utils').dump(this.getElementsInfo('a[href*="submit()"]'));
    casper.evaluate(function(code){
        document.querySelector('input#txt_stock_code').value = code;
        document.querySelector('a[href*="submit()"]').click();
    }, param);
    casper.waitForText('市場中介者/願意披露的投資者戶口持有人的紀錄:', function() {
        fs.write(fname, this.getPageContent(), 'w');
        casper.echo('OK');
    });
});

casper.run();
