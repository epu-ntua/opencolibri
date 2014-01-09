var QueryString = function () {
    // This function is anonymous, is executed immediately and
    // the return value is assigned to QueryString!
    var query_string = {};
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        // If first entry with this name
        if (typeof query_string[pair[0]] === "undefined") {
            query_string[pair[0]] = pair[1];
            // If second entry with this name
        } else if (typeof query_string[pair[0]] === "string") {
            var arr = [ query_string[pair[0]], pair[1] ];
            query_string[pair[0]] = arr;
            // If third or later entry with this name
        } else {
            query_string[pair[0]].push(pair[1]);
        }
    }
    return query_string;
}();

var DatasetSearchView = Backbone.View.extend({

    el: '#dataset-collection-container',
    template: _.template($('#dataset-template').html()),
    loadingSelector: '#loading',

    initialize: function () {
        this.collection = new DatasetCollection();
        this.paginator = new Paginator();
        this.filterManager = new FilterManager(this.collection, this.paginator);
        this.eventAggregator = new EventAggregator(this);
        this.listenTo(this.eventAggregator, 'result:fetch:start', this._loadAnimationOn)
        this.listenTo(this.eventAggregator, 'result:fetch:success', this._loadAnimationOff)
        this.listenTo(this.eventAggregator, 'result:fetch:error', this._loadAnimationOff)
        this.collection.bind('reset', function () {
            this.eventAggregator.trigger('collection:reset');
        }, this.collection);
        this.filterView = new FilterView({
            filterManager: this.filterManager
        });
        this.collection.on('reset', this.render, this);
        this.eventAggregator.fetchResults();
        this.paginatorView = new PaginatorView({
            model: this.paginator
        });
    },

    renderOne: function (dataset, that) {
        var view = new DatasetView({model: dataset});
        $('#dataset-collection-container').append(view.render().el);
    },

    render: function () {
        $(this.el).html('');
        var self = this;
        this.collection.each(this.renderOne, this, self);
        this.paginatorView.render();
        this.filterView.filterByTitleView.onItemChanged();
    },

    _loadAnimationOn: function () {
        $(this.loadingSelector).fadeIn('fast');
    },

    _loadAnimationOff: function () {
        $(this.loadingSelector).fadeOut('fast');
    }
});


var DatasetView = Backbone.View.extend({

    template: _.template($('#dataset-template').html()),

    render: function () {
        this.$el.html(this.template(this.model.toJSON()));
        return this;
    }
});


var EventAggregator = Backbone.Model.extend({

    initialize: function (datasetSearchView) {
        this.datasetSearchView = datasetSearchView
        this.collection = this.datasetSearchView.collection;
        this.filterManager = this.datasetSearchView.filterManager;

        this.collection.eventAggregator = this;
        this.filterManager.eventAggregator = this;

        this.paginator = this.datasetSearchView.paginator
        this.on('filter:change', this.fetchResults, this);
        this.collection.once('reset', this.reloadFilterManager, this);
        this.paginator.on('change', this.fetchResults, this);
    },

    reloadFilterManager: function () {
        this.filterManager.reload();
        var self = this;
        jQuery.ajax({
            type: "GET",
            url: '/api/colibri/list/titles/',
            dataType: 'json',

            success: function (json) {
                self.filterManager.filterByTitle.distinctTitles = json.title;
                jQuery.ajax({
                    type: "GET",
                    url: '/api/colibri/list/authors/',
                    dataType: 'json',

                    success: function (json) {
                        self.filterManager.filterByAuthor.distinctAuthors = json.author;
                        value = QueryString.value;
                        if (value) {
                            $('#filter-by-title').val(value);
                        }
                        $('#filter-by-title').autocomplete({
                            source: self.filterManager.filterByTitle.distinctTitles,
                            close: function () {
                                self.datasetSearchView.filterView.filterByTitleView.onItemChanged();
                            },
                        });
                        $('#filter-by-author').autocomplete({
                            source: self.filterManager.filterByAuthor.distinctAuthors,
                            close: function () {
                                self.datasetSearchView.filterView.filterByAuthorView.onItemChanged();
                            }
                        });
                    }
                })
            }
        });
        jQuery.ajax({
            type: "GET",
            url: '/api/colibri/list/datasetLanguages/?format=json',
            dataType: 'json',
            success: function (json) {
                self.filterManager.filterByLanguage.setDistinctLanguages(json.language);
            }
        });
        jQuery.ajax({
            type: "GET",
            url: '/api/colibri/list/datasetCountries/?format=json',
            dataType: 'json',
            success: function (json) {
                self.filterManager.filterByCountry.setDistinctCountries(json.country);
            }
        });
        jQuery.ajax({
            type: "GET",
            url: '/api/colibri/list/datasetUploaders/?format=json',
            dataType: 'json',
            success: function (json) {
                self.filterManager.filterByUploader.setDistinctUploaders(json.uploader);
            }
        });
    },

    fetchResults: function () {
        console.log('fetchResults');
        if (this.filterManager.filterByUploader && this.filterManager.filterByUploader.get('uploader') != '') {
            var data = {
                title__icontains: this.filterManager.filterByTitle.get('value'),
                description__icontains: this.filterManager.filterByDescription.get('value'),
                author__icontains: this.filterManager.filterByAuthor.get('value'),
                country__icontains: this.filterManager.filterByCountry.get('country'),
                language: this.filterManager.filterByLanguage.get('language'),
                uploader: this.filterManager.filterByUploader.get('uploader'),
                offset: this.paginator.get('offset'),
            }
        } else {
            var data = {
                title__icontains: this.filterManager.filterByTitle.get('value'),
                description__icontains: this.filterManager.filterByDescription.get('value'),
                author__icontains: this.filterManager.filterByAuthor.get('value'),
                country__icontains: this.filterManager.filterByCountry.get('country'),
                language: this.filterManager.filterByLanguage.get('language'),
                offset: this.paginator.get('offset'),
            }
        }
        var _that = this;
        _that.trigger('result:fetch:start', _that)
        this.collection.fetch({
            data: data,

            success: function (collection, response, options) {
                _that.trigger('result:fetch:success', _that)
                // self.filterManager.paginator.parse(response.meta);
                _that.datasetSearchView.paginator.limit = (response.meta.limit);
                _that.datasetSearchView.paginator.next = (response.meta.next);
                _that.datasetSearchView.paginator.offset = (response.meta.offset);
                _that.datasetSearchView.paginator.previous = (response.meta.previous);
                _that.datasetSearchView.paginator.total_count = (response.meta.total_count);
                _that.collection.reset(response.objects);
            }
        });
    }

});


RegExp.escape = function (text) {
    if (!arguments.callee.sRE) {
        var specials = [
            '/', '.', '*', '+', '?', '|',
            '(', ')', '[', ']', '{', '}', '\\'
        ];
        arguments.callee.sRE = new RegExp(
            '(\\' + specials.join('|\\') + ')', 'g'
        );
    }
    return text.replace(arguments.callee.sRE, '\\$1');
}


var FilterManager = Backbone.Model.extend({

    eventAggregator: null,

    initialize: function (collection, paginator) {
        this.paginator = paginator;
        this.collection = collection;
        this.filterByTitle = new FilterByTitle();
        this.filterByDescription = new FilterByDescription();
        this.filterByAuthor = new FilterByAuthor();
        this.filterByCountry = new FilterByCountry(this.collection);
        this.filterByLanguage = new FilterByLanguage(this.collection);
        this.filterByUploader = new FilterByUploader(this.collection);
        this.filterByTitle.on('change', this.onFilterChange, this);
        this.filterByDescription.on('change', this.onFilterChange, this);
        this.filterByAuthor.on('change', this.onFilterChange, this);
        this.filterByCountry.on('change', this.onFilterChange, this);
        this.filterByLanguage.on('change', this.onFilterChange, this);
        this.filterByUploader.on('change', this.onFilterChange, this);
        this.filterByTitle.on('renderFilters', this.onFilterChange, this);
        this.filterByDescription.on('renderFilters', this.renderFilters, this);
        this.filterByAuthor.on('renderFilters', this.renderFilters, this);
        this.filterByCountry.on('renderFilters', this.renderFilters, this);
        this.filterByLanguage.on('renderFilters', this.renderFilters, this);
        this.filterByUploader.on('renderFilters', this.renderFilters, this);
    },

    reload: function () {
        this.filterByTitle.reload();
        this.filterByDescription.reload();
        this.filterByAuthor.reload();
        this.filterByCountry.reload();
        this.filterByLanguage.reload();
        this.filterByUploader.reload();
        this.trigger('filter:models:reloaded')
    },

    renderFilters: function () {
        this.trigger('renderFilters', this);
    },

    onFilterChange: function () {
        this.eventAggregator.trigger('filter:change', this);
    }

})

var FilterByLanguage = Backbone.Model.extend({

    language: null,
    distinctLanguages: [],

    initialize: function (collection) {
        this.collection = collection;
    },

    setDistinctLanguages: function (distinctLanguages) {
        this.set('distinctLanguages', distinctLanguages, {silent: true});
        this.trigger('renderFilters');
    },

    reload: function () {
        this.set('language', '', {silent: true});
    },

    // distinctLanguages: function() {
    // 	array = _.map(this.collection.pluck('resources'), function(datasetResources) {
    // 		return _.map(datasetResources, function(resource) {
    // 			return resource.language;
    // 		});
    // 	});
    // 	return _.sortBy(
    // 		_.map(
    // 			_.uniq(array, function(ar) {
    // 				return ar[0].code;
    // 			}), function(a){
    // 				return a[0];
    // 			}),
    // 		function(language) {
    // 			return language.code;
    // 	});
    // }
});


var FilterByCountry = Backbone.Model.extend({

    country: null,
    distinctCountries: [],

    initialize: function (collection) {
        this.collection = collection;
    },

    setDistinctCountries: function (distinctCountries) {
        this.set('distinctCountries', distinctCountries, {silent: true});
        this.trigger('renderFilters');
    },

    reload: function () {
        this.set('country', '', {silent: true});
    },

    // distinctCountries: function() {
    // 	return _.uniq(_.sortBy(this.collection.pluck('country'), function (country) { return country.code;}), true, function(country) {
    // 		return country.code;
    // 	});
    // },
});

var FilterByUploader = Backbone.Model.extend({

    uploader: null,
    distinctUploaders: [],

    initialize: function (collection) {
        this.collection = collection;
    },

    setDistinctUploaders: function (distinctUploaders) {
        this.set('distinctUploaders', distinctUploaders, {silent: true});
        this.trigger('renderFilters');
    },

    reload: function () {
        this.set('uploader', '', {silent: true});
    },

    // distinctUploaders: function() {
    // 	uploaderIds = _.uniq(_.sortBy(this.collection.pluck('uploader'), function (uploader) { return uploader.id;}), true, function(uploader) {
    // 		return uploader.id;
    // 	});
    // 	uploaderIds.splice(0, 0, {'username': ''});
    // 	return uploaderIds;
    // },
});


var BaseFilterByText = Backbone.Model.extend({

    value: '',

    reload: function () {
        this.set('value', '', {silent: true});
    }
});


var FilterByTitle = BaseFilterByText.extend({

    distinctTitles: null,

    initialize: function () {
        this.set('value', '');
        this.column = 'title';
    }
});


var FilterByDescription = BaseFilterByText.extend({

    initialize: function () {
        this.set('value', '');
        this.column = 'description';
    }
});

var FilterByAuthor = BaseFilterByText.extend({

    distinctAuthors: null,

    initialize: function () {
        this.set('value', '');
        this.column = 'author';
    }
});


var FilterView = Backbone.View.extend({

    initialize: function (options) {
        this.filterByTitleView = new FilterByTitleView({
            model: this.options.filterManager.filterByTitle
        });
        this.filterByDescriptionView = new FilterByDescriptionView({
            model: this.options.filterManager.filterByDescription
        });
        this.filterByAuthorView = new FilterByAuthorView({
            model: this.options.filterManager.filterByAuthor
        });
        this.filterByCountryView = new FilterByCountryView({
            model: this.options.filterManager.filterByCountry
        });
        this.filterByLanguageView = new FilterByLanguageView({
            model: this.options.filterManager.filterByLanguage
        });
        this.filterByUploaderView = new FilterByUploaderView({
            model: this.options.filterManager.filterByUploader
        });

        this.options.filterManager.bind('filter:models:reloaded', this.render, this)
        this.options.filterManager.bind('renderFilters', this.render, this)
    },

    render: function () {
        this.filterByTitleView.render();
        this.filterByDescriptionView.render();
        this.filterByAuthorView.render();
        this.filterByCountryView.render();
        this.filterByLanguageView.render();
        this.filterByUploaderView.render();
    }
});


var BaseFilterByTextView = Backbone.View.extend({

    render: function () {
        this.$el.html(this.template);
        this.delegateEvents();
        return this;
    },

    onItemChanged: function () {
        this.model.set('value', $(this.input.selector).val());
    }
});


var FilterByTitleView = BaseFilterByTextView.extend({

    events: {
        'keyup #filter-by-title': 'onItemChanged',
    },

    template: _.template($('#filter-by-title-template').html()),

    el: $('.filter-by-title-container')[0],

    input: $('#filter-by-title'),
});


var FilterByDescriptionView = BaseFilterByTextView.extend({

    events: {'keyup #filter-by-description': 'onItemChanged'},

    template: _.template($('#filter-by-description-template').html()),

    el: $('.filter-by-description-container')[0],

    input: $('#filter-by-description'),
});


var FilterByAuthorView = BaseFilterByTextView.extend({

    events: {
        'keyup #filter-by-author': 'onItemChanged',
    },

    template: _.template($('#filter-by-author-template').html()),

    el: $('.filter-by-author-container')[0],

    input: $('#filter-by-author'),
});


var FilterByLanguageView = Backbone.View.extend({

    events: {
        'change #filter-by-language': 'onItemChanged'
    },

    template: _.template($('#filter-by-language-template').html()),

    el: $('.filter-by-language-container'),

    initialize: function () {
        this.model.on('change', this.render, this);
    },

    onItemChanged: function (element) {
        this.model.set('language', $(element.target).val());
    },

    render: function () {
        if (this.model.hasChanged('distinctLanguages')) {
            var languages = this.model.get('distinctLanguages')
            this.$el.html(this.template({languages: languages}));
            this.delegateEvents();
        }
        return this;
    }
});


var FilterByCountryView = Backbone.View.extend({

    events: {
        'change #filter-by-country': 'onItemChanged'
    },

    template: _.template($('#filter-by-country-template').html()),

    el: $('.filter-by-country-container'),

    initialize: function () {
        this.model.on('change', this.render, this);
    },

    onItemChanged: function (element) {
        this.model.set('country', $(element.target).val());
    },


    render: function () {
        if (this.model.hasChanged('distinctCountries')) {
            var countries = this.model.get('distinctCountries');
            this.$el.html(this.template({countries: countries}));
            this.delegateEvents();
        }
        return this;
    }
});

var FilterByUploaderView = Backbone.View.extend({

    events: {
        'change #filter-by-uploader': 'onItemChanged'
    },

    template: _.template($('#filter-by-uploader-template').html()),

    el: $('.filter-by-uploader-container'),

    initialize: function () {
        this.model.on('change', this.render, this);
    },

    onItemChanged: function (element) {
        this.model.set('uploader', $(element.target).val());
    },


    render: function () {
        if (this.model.hasChanged('distinctUploaders')) {
            var uploaders = this.model.get('distinctUploaders')
            this.$el.html(this.template({uploaders: uploaders}));
            this.delegateEvents();
            return this;
        }
    }
});


var Paginator = Backbone.Model.extend({
    offset: 0
});

var PaginatorView = Backbone.View.extend({

    events: {
        'click .paginator-button': 'onItemChanged',
    },

    template: _.template($('#paginator-template').html()),

    el: $('.paginator-container'),

    render: function () {
        this.$el.html(this.template(this.model));
        this.delegateEvents();
        return this;
    },

    onItemChanged: function (element) {
        this.model.set('offset', $(element.target).data('offset'));
    }
});

var Dataset = Backbone.Model.extend({
});


var DatasetCollection = Backbone.Collection.extend({
    model: Dataset,
    url: '/api/colibri/datasets/?format=json',
    eventAggregator: null,
});

var appView = new DatasetSearchView();
