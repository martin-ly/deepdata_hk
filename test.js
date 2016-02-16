var casper = require('casper').create();
var url = 'http://ip-addr.es/';

casper.start(url, function() {
    var js = this.evaluate(function() {
        return document;
    });
    this.echo(js.all[0].outerText);
});
casper.run();
