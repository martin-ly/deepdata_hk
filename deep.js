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
    require('utils').dump(this.getElementsInfo('a[href]'));
    casper.evaluate(function(code){
        document.querySelector('input#txt_stock_code').value = code;
//        document.querySelector().click('');
    }, param);
    this.capture('1111.png');
});

casper.run();
