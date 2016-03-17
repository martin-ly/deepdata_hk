// casperjs test check_participant.js --output=01089.jjbh.html --code=01089 --today=20160226 --ename=aaa --tname= --addr=qqq --tel= --fax=1234567890 --website=www.aaa.com

var fs = require('fs');
var utils = require('utils');
var x = require('casper').selectXPath;
var subprocess = require("child_process");

var fname = casper.cli.get("output");
if (fname==undefined) {
    casper.echo('缺少output').exit();
}

var code = casper.cli.raw.get("code");
if (code==undefined) {
    casper.echo('您想要抓取哪一个券商的编号维护数据？').exit();
}

var ename = casper.cli.raw.get("ename");
if (ename==undefined) {
    casper.echo('缺少ename').exit();
}

var tname = casper.cli.raw.get("tname");
if (tname==undefined) {
    casper.echo('缺少tname').exit();
}

var addr = casper.cli.raw.get("addr");
if (code==undefined) {
    casper.echo('缺少addr').exit();
}

var tel = casper.cli.raw.get("tel");
if (tel==undefined) {
    casper.echo('缺少tel').exit();
}

var fax = casper.cli.raw.get("fax");
if (fax==undefined) {
    casper.echo('缺少fax').exit();
}

var website = casper.cli.raw.get("website");
if (website==undefined) {
    casper.echo('缺少website').exit();
}

casper.test.begin('编号维护'+code, 0, function suite(test) {
    casper.start('http://www.hkex.com.hk/chi/plw/search_c.aspx?selecttype=se', function() {
        casper.capture(fname+'_1.png')
        fs.write(fname+'_1.html', this.getPageContent(), 'w');

        casper.evaluate(function(code) {
            document.querySelector('input[name="txt_participant_id"]').value = code;
            document.querySelector('img[name="submit2"]').click();
        }, code);

        casper.waitForText('香港交易及結算所有限公司版權所有', function () {
            casper.capture(fname+'.png')
            fs.write(fname, this.getPageContent(), 'w');
            fs.remove(fname+'_1.png');
            fs.remove(fname+'_1.html');
            casper.echo('OK');
        });
    });

    casper.run(function() {
        test.done();
    });
});
