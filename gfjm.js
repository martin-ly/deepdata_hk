// casperjs test gfjm.js --output=111.html --code=00001

var fs = require('fs');
var utils = require('utils');

var fname = casper.cli.get("output");
if (fname==undefined) {
    casper.echo('缺少输出文件名称').exit();
}

var param = casper.cli.raw.get("code");
if (param==undefined) {
    casper.echo('您想要抓取哪一只港股的股份解码数据？').exit();
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

casper.test.begin('股份解码'+param, 0, function suite(test) {
    casper.start('http://sdinotice.hkex.com.hk/di/NSSrchCorp.aspx?src=MAIN&lang=ZH&in=1', function() {
        casper.capture(fname+'_1.png')
        fs.write(fname+'_1.html', this.getPageContent(), 'w');

        casper.evaluate(function(code) {
            document.querySelector('input#txtStockCode').value = code;
            document.querySelector('input#cmdSearch').click();
        }, param);

        casper.waitForText('返回頁頂', function() {
            casper.capture(fname+'_2.png')
            fs.write(fname+'_2.html', this.getPageContent(), 'w');
            casper.clickLabel('所有披露權益通知', 'a');

            casper.waitForText('返回頁頂', function() {
                casper.capture(fname+'_3.png')
                fs.write(fname+'_3.html', this.getPageContent(), 'w');
            });
        });
    });

    casper.run(function() {
        test.done();
    });
});
