var search_pill_widget = (function () {

var exports = {};

exports.initialize = function () {
    var container = $('#search_arrows');
    exports.my_pill = search_pill.create_pills(container);
};

return exports;
}());

if (typeof module !== 'undefined') {
    module.exports = search_pill_widget;
}
