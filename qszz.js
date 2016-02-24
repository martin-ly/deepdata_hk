// casperjs test qszz.js --output=111.html --code=00003

var fs = require('fs');
var utils = require('utils');

var fname = casper.cli.get("output");
if (fname==undefined) {
    casper.echo('缺少输出文件名称').exit();
}

var param = casper.cli.raw.get("code");
if (param==undefined) {
    casper.echo('您想要抓取哪一只港股的券商追踪数据？').exit();
    test.done();
}

var exists = 0;

casper.on('remote.alert', function(message) {
    this.echo('警告: ' + message);
    this.exit();
});

casper.on('page.error', function(message, trace) {
    this.echo('错误: ' + message);
    this.exit();
});

casper.test.begin('券商追踪'+param, 0, function suite(test) {
    casper.start('http://www.hkexnews.hk/sdw/search/search_sdw_c.asp', function() {
        casper.capture(fname+'_1.png')
        fs.write(fname+'_1.html', this.getPageContent(), 'w');

        casper.evaluate(function(code) {
            document.querySelector('input#txt_stock_code').value = code;
            document.querySelector('a[href*="submit()"]').click();
        }, param);

        casper.on('load.finished', function(status) {
            if (this.getPageContent().search(/市場中介者\/願意披露的投資者戶口持有人的紀錄:/) != -1) {
                exists = 1;
            }
            else {
                exists = 2;
            }
        });

        casper.waitFor(function () {
                return exists != 0;
            }, function () {
                if (exists == 1) {
                    fs.write(fname, this.getPageContent(), 'w');
                    fs.remove(fname+'_1.html');
                    fs.remove(fname+'_1.png');
                    casper.echo('OK');
                }
                else {
                    casper.capture(fname+'_2.png');
                    fs.write(fname+'_2.html', this.getPageContent(), 'w');
                    casper.echo('Key Not Found');
                }
            });
    });

    casper.run(function() {
        test.done();
    });
});
