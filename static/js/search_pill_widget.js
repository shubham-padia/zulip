var search_pill_widget = (function () {

var exports = {};

exports.initialize = function () {
    var container = $('#search_arrows');
    exports.my_pill = search_pill.create_pills(container);

    exports.my_pill.onPillRemove(function () {
        var base_query = search_pill.get_search_string_for_current_filter(exports.my_pill);
        var operators = Filter.parse(base_query);
        narrow.activate(operators, {trigger: 'search'});
    });
};

return exports;
}());

if (typeof module !== 'undefined') {
    module.exports = search_pill_widget;
}
