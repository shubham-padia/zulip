zrequire('search_pill');
zrequire('util');
zrequire('Filter', 'js/filter');
zrequire('Handlebars', 'handlebars');

var is_starred_item = {
    display_value: 'starred messages',
    search_string: 'is:starred',
}

var is_private_item = {
    display_value: 'private messages',
    search_string: 'is:private',
}

run_test('create_item', () => {

    function test_create_item(search_string, current_items, expected_item) {
        var item = search_pill.create_item_from_search_string(search_string, current_items);
        assert.deepEqual(item, expected_item);
    }

    test_create_item('is:starred', [], is_starred_item);
});

run_test('get_search_string', () => {
    assert.equal(search_pill.get_search_string_from_item(is_starred_item), 'is:starred');
});

run_test('append', () => {
    var appended;
    var cleared;

    function fake_append(search_string) {
        appended = true;
        assert.equal(search_string, is_starred_item.search_string);
    }

    function fake_clear() {
        cleared = true;
    }

    var pill_widget = {
        appendValue: fake_append,
        clear_text: fake_clear,
    };

    search_pill.append_search_string(is_starred_item.search_string, pill_widget);

    assert(appended);
    assert(cleared);
});

run_test('get_items', () => {
    var items = [is_starred_item, is_private_item];

    var pill_widget = {
        items: function () { return items; },
    };

    assert.deepEqual(search_pill.get_search_string_for_current_filter(pill_widget),
                     is_starred_item.search_string + ' ' + is_private_item.search_string);
});