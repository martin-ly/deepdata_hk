var fs = require('fs');
var utils = require('utils');
var casper = require('casper').create();

var fname = casper.cli.get("output");
if (fname==undefined) {
    casper.echo('缺少输出文件名称').echo('FAIL').exit();
}

casper.start('http://www.hkexnews.hk/sdw/search/search_sdw_c.asp', function() {
	this.clickLabel('股份名單', 'span');
});

casper.waitForPopup(/.*stocklist_c\.asp.*/, function() {
	casper.withPopup(/.*stocklist_c\.asp.*/, function() {
		fs.write(fname, this.getPageContent(), 'w');
        casper.echo('OK');
	});
});

casper.run();
