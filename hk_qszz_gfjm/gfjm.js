// casperjs test gfjm.js --output=111 --code=90005 --today=20160226

var fs = require('fs');
var utils = require('utils');
var x = require('casper').selectXPath;
var subprocess = require("child_process");

var param = casper.cli.raw.get("code");
if (param==undefined) {
    casper.echo('您想要抓取哪一只港股的股份解码数据？').exit();
    test.done();
}

var today = casper.cli.raw.get("today");
if (today==undefined) {
    casper.echo('无日期参数').exit();
    test.done();
}

var fname = today + '/' + param;
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
        casper.capture(fname+'.gfjm.1.png')
        fs.write(fname+'.gfjm.1.html', this.getPageContent(), 'w');

        casper.evaluate(function(code) {
            if (document.querySelector('select#ddlStartDateDD').value == '29' && document.querySelector('select#ddlStartDateMM').value == '02') {
                document.querySelector('select#ddlStartDateDD').value = '01';
                document.querySelector('select#ddlStartDateMM').value = '03';
            }
            document.querySelector('input#txtStockCode').value = code;
            document.querySelector('input#cmdSearch').click();
        }, param);

        casper.waitForText('返回頁頂', function() {
            casper.capture(fname+'.gfjm.2.png')
            fs.write(fname+'.gfjm.2.html', this.getPageContent(), 'w');
            if (casper.fetchText('span#lblRecCount') == '0') {
                casper.then(function() {
                    fs.remove(fname+'.gfjm.1.png');
                    fs.remove(fname+'.gfjm.1.html');
                    fs.remove(fname+'.gfjm.2.png');
                    fs.remove(fname+'.gfjm.2.html');
                    casper.echo('OK');
//                    casper.echo('No Record 1');
                });
            }
            else {
                casper.clickLabel('所有披露權益通知', 'a');
                casper.waitForSelector('input#cmdNewSearch', function() {
                    casper.capture(fname+'.gfjm.3.png')
                    fs.write(fname+'.gfjm.3.html', this.getPageContent(), 'w');
                    if (casper.fetchText('span#lblRecCount') == '0') {
                        casper.then(function() {
                            fs.remove(fname+'.gfjm.1.png');
                            fs.remove(fname+'.gfjm.1.html');
                            fs.remove(fname+'.gfjm.2.png');
                            fs.remove(fname+'.gfjm.2.html');
                            fs.remove(fname+'.gfjm.3.png');
                            fs.remove(fname+'.gfjm.3.html');
                            casper.echo('OK');
//                            casper.echo('No Record 2');
                        });
                    }
                    else {
                        casper.capture(fname+'.gfjm.png')
                        fs.write(fname+'.gfjm.html', this.getPageContent(), 'w');
                        fs.remove(fname+'.gfjm.1.png');
                        fs.remove(fname+'.gfjm.1.html');
                        fs.remove(fname+'.gfjm.2.png');
                        fs.remove(fname+'.gfjm.2.html');
                        fs.remove(fname+'.gfjm.3.png');
                        fs.remove(fname+'.gfjm.3.html');

                        var out = '';
                        var finished = false;
                        subprocess.execFile("python", ["gfjm_main.py", fname], null, function(err, stdout, stderr) {
                            out = stdout;
                            finished = true;
                        });

                        this.waitFor(function check() {
                            return finished;
                        }, function then() {
                            out = out.split('\r\n');
                            var idx = 0;
                            casper.each(out, function(self, item) {
                                if (item.length > 0) {
                                    casper.then(function() {
                                        idx += 1;
                                        casper.echo('Click ' + item);
                                        casper.click(x(item));
                                        casper.waitForSelector('input#cmdBack', function() {
                                            casper.capture(fname+'.'+parseInt(idx)+'.gfjm.click.png')
                                            fs.write(fname+'.'+parseInt(idx)+'.gfjm.click.html', this.getPageContent(), 'w');
                                            fs.write(fname+'.gfjm.click', item, 'w');     //当前最新的已完成的click任务
                                        });
                                        casper.back();
                                    });
                                }
                            });
                            casper.then(function() {
                                casper.echo('OK');
                            });
                        });
                    }
                });
            }
        });
    });

    casper.run(function() {
        test.done();
    });
});
