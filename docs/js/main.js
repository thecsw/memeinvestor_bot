//a simple script testing all the plugins -
// probably the materialize.js dependency won't be necessary (used only for the sidebar at the moment)

document.addEventListener('DOMContentLoaded', function() {
    renderPage();
});

function renderPage() {
    var hash = window.location.hash.substr(1);
    if (!hash)
        hash = 'home';

    $.getJSON('/api/?per_page=5', function (api) {
        api.units = function() {
            return function(val, render) {
                return formatToUnits(render(val));
            }
        };

        $.get(hash + '.mst', function(template) {
            console.log(api);
            var rendered = Mustache.render(template, api);
            $('#target').html(rendered);
        });
    });
}

function formatToUnits(val) {
    var number = parseInt(val);
    var abbrev = ['', 'K', 'M', 'B', 'T'];
    var unrangifiedOrder = Math.floor(Math.log10(Math.abs(number)) / 3);
    var order = Math.max(0, Math.min(unrangifiedOrder, abbrev.length -1 ));
    var suffix = abbrev[order];
    var precision = suffix ? 1 : 0;
    var res = (number / Math.pow(10, order * 3)).toFixed(precision) + suffix;

    return res;
}

function iterateDays(days, callback) {
    to = new Date();
    to.setHours(23);
    to.setMinutes(59);
    to.setSeconds(59);
    to.setMilliseconds(999);
    from = new Date();
    from.setTime(to.getTime());
    from.setDate(from.getDate() - 1);

    for (var i = 0; i < days; i++) {
        callback(i, from, to);

        from.setDate(from.getDate() - 1);
        to.setDate(to.getDate() - 1);
    }
}
