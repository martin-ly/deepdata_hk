
var fs = require('fs');
var utils = require('utils');
var x = require('casper').selectXPath;
var subprocess = require("child_process");

var fname = casper.cli.get("output");
if (fname==undefined) {
    casper.echo('缺少输出文件名称').exit();
}

var param = casper.cli.raw.get("code");
if (param==undefined) {
    casper.echo('您想要抓取哪一个券商的编号维护数据？').exit();
    test.done();
}

casper.test.begin('编号维护'+param, 0, function suite(test) {
    casper.run(function() {
        test.done();
    });
});
