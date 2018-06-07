var search_pill = (function () {
var exports = {};

exports.create_item_from_search_string = function (search_string) {
    var operator = Filter.parse(search_string);
    var description = Filter.describe(operator);
    return {
        display_value: description,
        search_string: search_string,
    };
};

exports.get_search_string_from_item = function (item) {
    return item.search_string;
};

exports.create_pills = function (pill_container) {
    var pills = input_pill.create({
        container: pill_container,
        create_item_from_text: exports.create_item_from_search_string,
        get_text_from_item: exports.get_search_string_from_item,
    });
    return pills;
};

return exports;
}());

if (typeof module !== 'undefined') {
    module.exports = search_pill;
}
