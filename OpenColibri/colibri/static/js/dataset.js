jQuery(function () {
    jQuery('.chzn-select').chosen();
    jQuery('#dataset-add-form tbody tr').formset({
        prefix: 'resource', addText: '<span class="command_icons">+</span> Add Resource', deleteText: '<span class="command_icons">-</span> Remove'
    });
    jQuery('#dataset-extend-form tbody tr').formset({
        prefix: 'resource', addText: '<span class="command_icons">+</span> Add Resource', deleteText: '<span class="command_icons">-</span> Remove'
    });
    jQuery('.popupDatepicker').datepicker();
    jQuery.ajax({
        type: "GET",
        url: '/api/colibri/list/licenses/',
        dataType: 'json',

        success: function (json) {
            jQuery("#id_license").autocomplete({
                source: json.licenses
            });
        }
    });
    jQuery.ajax({
        type: "GET",
        url: '/api/colibri/list/authors/',
        dataType: 'json',

        success: function (json) {
            jQuery("#id_author").autocomplete({
                source: json.author
            });
        }
    });
    jQuery.ajax({
        type: "GET",
        url: '/api/colibri/list/publishers/',
        dataType: 'json',

        success: function (json) {
            jQuery("#id_publisher").autocomplete({
                source: json.publishers
            });
        }
    });
    jQuery.ajax({
        type: "GET",
        url: '/api/colibri/list/tempGranularities/',
        dataType: 'json',

        success: function (json) {
            jQuery("#id_temporal_granularity").autocomplete({
                source: json.tempGranularities
            });
        }
    });
    jQuery.ajax({
        type: "GET",
        url: '/api/colibri/list/geoGranularities/',
        dataType: 'json',

        success: function (json) {
            jQuery("#id_geographical_granularity").autocomplete({
                source: json.geoGranularities
            });
        }
    });
    jQuery.ajax({
        type: "GET",
        url: '/api/colibri/list/dataCollectionTypes/',
        dataType: 'json',

        success: function (json) {
            jQuery("#id_data_collection_type").autocomplete({
                source: json.dataCollectionTypes
            });
        }
    });
    jQuery.ajax({
        type: "GET",
        url: '/api/colibri/list/softwarePackages/',
        dataType: 'json',

        success: function (json) {
            jQuery("#id_software_package").autocomplete({
                source: json.softwarePackages
            });
        }
    });
    jQuery.ajax({
        type: "GET",
        url: '/api/colibri/list/analysisUnits/',
        dataType: 'json',

        success: function (json) {
            jQuery("#id_analysis_unit").autocomplete({
                source: json.analysisUnits
            });
        }
    });
})