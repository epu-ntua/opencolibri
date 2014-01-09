jQuery(function () {
    jQuery.ajax({
        type: "GET",
        url: '/api/colibri/list/titles/',
        dataType: 'json',

        success: function (json) {
            var _that = this;
            _that.title = json.title;
            jQuery.ajax({
                type: "GET",
                url: '/api/colibri/list/authors/',
                dataType: 'json',

                success: function (json) {
                    _that.author = json.author;
                    jQuery("#id_value").autocomplete({
                        source: _that.author.concat(_that.title)
                    });
                }
            })
        }
    });
})