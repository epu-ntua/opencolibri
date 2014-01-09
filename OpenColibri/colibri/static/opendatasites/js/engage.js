function calculateChart(tabledata, title, tabhash) {

    switch (title) {
        case STR_DATA_SOURCES_TYPES:
            var counts = {};
            //DISTINCT COUNT OF DATA SOURCES
            for (var i = 0; i < tabledata.length; i++) {
                var num = tabledata[i][_COLUMN_DATASOURCE];
                counts[num] = counts[num] ? counts[num] + 1 : 1;
            }
            var keys = Object.keys(counts);
            var curData = new Array();
            //Write the distinct column values (keys) and its occurancies (counts) to Chart Data
            for (var j = 0; j < keys.length; j++) {
                curData.push({name: keys[j], data: [counts[keys[j]]]});
            }
            ;
            drawChartBar(curData, title, tabhash);
            break;
        case STR_LICENSES:
            var counts = {};
            //DISTINCT COUNT OF Licenses
            for (var i = 0; (i < tabledata.length); i++) {
                var num = tabledata[i][_COLUMN_LICENSE];
                counts[num] = counts[num] ? counts[num] + 1 : 1;
            }
            ;

            var keys = Object.keys(counts);
            var curData = new Array();
            //Write the distinct column values (keys) and its occurancies (counts) to Chart Data
            for (var j = 0; j < keys.length; j++) {
                curData.push([keys[j], counts[keys[j]]]);
            }
            ;
            drawChart(curData, title, tabhash);
            break;
        case STR_LANGUAGE_UI:

            var counts = [0, 0, 0, 0, 0];
            //Count the number of languages supported
            for (var i = 0; i < tabledata.length; i++) {
                var num = tabledata[i][_COLUMN_LANGUAGE].split(",");
                if (tabledata[i][_COLUMN_LANGUAGE] == "All EU") {
                    counts[4]++;
                }
                if ((num.length == 1)) {
                    counts[0]++;
                }
                else if (num.length == 2) {
                    counts[1]++;
                }
                else if (num.length == 3) {
                    counts[2]++;
                }
                else if (num.length == 4) {
                    counts[3]++;
                }
                else if (num.length > 4) {
                    counts[4]++;
                }
                else;
            }


            var curData = new Array();
            curData.push(["Native Only", counts[0]]);
            curData.push(["2 languages", counts[1]]);
            curData.push(["3 languages", counts[2]]);
            curData.push(["4 languages", counts[3]]);
            curData.push(["More than 4", counts[4]]);

            drawChart(curData, title, tabhash);
            break;
        case STR_DATA_FORMAT:
            var counts = [0, 0, 0, 0, 0, 0, 0];
            // COUNT OF some data formats
            for (var i = 0; i < tabledata.length; i++) {
                var num = tabledata[i][_COLUMN_DATAFORMAT];

                if (num.search("pdf") > -1) {
                    counts[0]++;
                }
                if (num.search("xls") > -1) {
                    counts[1]++;
                }
                if (num.search("csv") > -1) {
                    counts[2]++;
                }
                if (num.search("doc") > -1) {
                    counts[3]++;
                }
                if (num.search("html") > -1) {
                    counts[4]++;
                }
                if (num.search("kml") > -1) {
                    counts[5]++;
                }
                if (num.search("rss") > -1) {
                    counts[6]++;
                }
            }


            var curData = new Array();
            curData.push({name: "pdf", data: [counts[0]]});
            curData.push({name: "xls", data: [counts[1]]});
            curData.push({name: "csv", data: [counts[2]]});
            curData.push({name: "doc", data: [counts[3]]});
            curData.push({name: "html view", data: [counts[4]]});
            curData.push({name: "kml", data: [counts[5]]});
            curData.push({name: "rss", data: [counts[6]]});

            drawChartBar(curData, title, tabhash);
            break;
        case STR_PROVISION:
            var counts = [0, 0, 0, 0, 0];
            // COUNT OF provision utilities
            for (var i = 0; i < tabledata.length; i++) {
                var num = tabledata[i][_COLUMN_PROVISION];

                if (num.search("Download") > -1) {
                    counts[0]++;
                }
                if (num.search("View") > -1) {
                    counts[1]++;
                }
                if (num.search("Map") > -1) {
                    counts[2]++;
                }
                if (num.search("API") > -1) {
                    counts[3]++;
                }
                if (num.search("Charts") > -1) {
                    counts[4]++;
                }

            }

            var curData = new Array();
            curData.push({name: "Download file", data: [counts[0]]});
            curData.push({name: "Online View of datasets", data: [counts[1]]});
            curData.push({name: "Map", data: [counts[2]]});
            curData.push({name: "API", data: [counts[3]]});
            curData.push({name: "Charts", data: [counts[4]]});

            drawChartBar(curData, title, tabhash);
            break;
    } //End of switch
}

function drawChartBar(cData, charttitle, tabhash) {

    //Initialize Chart

    var chart;
    chart = new Highcharts.Chart({
        chart: {
            type: 'bar',
            renderTo: 'chart' + tabhash,
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        xAxis: {
            categories: [''],
            title: {
                text: null
            }
        },
        yAxis: {
            labels: {
                enabled: false
            },
            title: {
                text: null
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'bottom',
            floating: true,
            borderWidth: 1,
            backgroundColor: '#FFFFFF',
            shadow: true
        },
        credits: {
            enabled: false
        },
        title: {
            text: 'European ' + charttitle
        },
        tooltip: {
            formatter: function () {
                return '' +
                    this.series.name + ': ' + this.y + ' sources';
            }
        },
        plotOptions: {
            bar: {
                dataLabels: {
                    enabled: true
                }
            }
        },
        series: cData
    });
}

function drawChart(cData, charttitle, tabhash) {
    //Initialize Chart
    var chart;
    chart = new Highcharts.Chart({
        chart: {
            renderTo: 'chart' + tabhash,
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        credits: {
            enabled: false
        },
        title: {
            text: charttitle
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'top',
            x: -300,
            floating: true,
            borderWidth: 1,
            backgroundColor: '#FFFFFF',
            shadow: true
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.point.name + '</b>: ' + ' ' + this.y + ' items (' + this.percentage + ' %)';
            }
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true
                },
                showInLegend: false
            }
        },
        series: [
            {
                type: 'pie',
                name: charttitle,
                data: cData
            }
        ]
    });
}

//Update map colors
function updatemapColors(mydata) {
    //Reset colors
    $('#map').vectorMap('set', 'colors', {BE: '#aaaaaa', FR: '#aaaaaa', BG: '#aaaaaa', DK: '#aaaaaa', HR: '#aaaaaa', DE: '#aaaaaa', BA: '#aaaaaa', HU: '#aaaaaa', JO: '#aaaaaa', DZ: '#aaaaaa', _1: '#aaaaaa', JE: '#aaaaaa', FI: '#aaaaaa', BY: '#aaaaaa', FO: '#aaaaaa', PS: '#aaaaaa', LB: '#aaaaaa', PT: '#aaaaaa', NO: '#aaaaaa', TR: '#aaaaaa', GE: '#aaaaaa', LI: '#aaaaaa', LV: '#aaaaaa', EE: '#aaaaaa', LT: '#aaaaaa', LU: '#aaaaaa', RO: '#aaaaaa', EG: '#aaaaaa', PL: '#aaaaaa', LY: '#aaaaaa', CH: '#aaaaaa', GR: '#aaaaaa', RU: '#aaaaaa', IQ: '#aaaaaa', IS: '#aaaaaa', AL: '#aaaaaa', IT: '#aaaaaa', GG: '#aaaaaa', CZ: '#aaaaaa', CY: '#aaaaaa', GB: '#aaaaaa', IM: '#aaaaaa', AT: '#aaaaaa', NL: '#aaaaaa', AD: '#aaaaaa', IE: '#aaaaaa', ES: '#aaaaaa', ME: '#aaaaaa', MD: '#aaaaaa', SY: '#aaaaaa', TN: '#aaaaaa', MA: '#aaaaaa', MC: '#aaaaaa', RS: '#aaaaaa', _2: '#aaaaaa', MK: '#aaaaaa', _0: '#aaaaaa', SK: '#aaaaaa', MT: '#aaaaaa', SI: '#aaaaaa', SM: '#aaaaaa', SA: '#aaaaaa', UA: '#aaaaaa', SE: '#aaaaaa', IL: '#aaaaaa'});
    var counts = [];
    for (var i = 0; i < mydata.length; i++) {
        var num = mydata[i][_COLUMN_COUNTRY];
        counts[num] = counts[num] ? counts[num] + 1 : 1;
    }
    var keys = Object.keys(counts);
    var countriesColored = {}
    //Write the distinct column values (keys) and the respective color
    for (var j = 0; j < keys.length; j++) {
        countriesColored[getCountryCode(keys[j])] = '#006C71';
    }
    ;

    $('#map').vectorMap('set', 'colors', countriesColored);
}

function getCountryName(countrycode) {
    switch (countrycode) {
        case "AF":
            return "Afghanistan";
            break;
        case "AX":
            return "Aland Islands";
            break;
        case "AL":
            return "Albania";
            break;
        case "DZ":
            return "Algeria";
            break;
        case "AS":
            return "American Samoa";
            break;
        case "AD":
            return "Andorra";
            break;
        case "AO":
            return "Angola";
            break;
        case "AI":
            return "Anguilla";
            break;
        case "AQ":
            return "Antarctica";
            break;
        case "AG":
            return "Antigua and Barbuda";
            break;
        case "AR":
            return "Argentina";
            break;
        case "AM":
            return "Armenia";
            break;
        case "AW":
            return "Aruba";
            break;
        case "AU":
            return "Australia";
            break;
        case "AT":
            return "Austria";
            break;
        case "AZ":
            return "Azerbaijan";
            break;
        case "BS":
            return "Bahamas";
            break;
        case "BH":
            return "Bahrain";
            break;
        case "BD":
            return "Bangladesh";
            break;
        case "BB":
            return "Barbados";
            break;
        case "BY":
            return "Belarus";
            break;
        case "BE":
            return "Belgium";
            break;
        case "BZ":
            return "Belize";
            break;
        case "BJ":
            return "Benin";
            break;
        case "BM":
            return "Bermuda";
            break;
        case "BT":
            return "Bhutan";
            break;
        case "BO":
            return "Bolivia, Plurinational State of";
            break;
        case "BA":
            return "Bosnia and Herzegovina";
            break;
        case "BW":
            return "Botswana";
            break;
        case "BV":
            return "Bouvet Island";
            break;
        case "BR":
            return "Brazil";
            break;
        case "IO":
            return "British Indian Ocean Territory";
            break;
        case "BN":
            return "Brunei Darussalam";
            break;
        case "BG":
            return "Bulgaria";
            break;
        case "BF":
            return "Burkina Faso";
            break;
        case "BI":
            return "Burundi";
            break;
        case "KH":
            return "Cambodia";
            break;
        case "CM":
            return "Cameroon";
            break;
        case "CA":
            return "Canada";
            break;
        case "CV":
            return "Cape Verde";
            break;
        case "KY":
            return "Cayman Islands";
            break;
        case "CF":
            return "Central African Republic";
            break;
        case "TD":
            return "Chad";
            break;
        case "CL":
            return "Chile";
            break;
        case "CN":
            return "China";
            break;
        case "CX":
            return "Christmas Island";
            break;
        case "CC":
            return "Cocos (Keeling) Islands";
            break;
        case "CO":
            return "Colombia";
            break;
        case "KM":
            return "Comoros";
            break;
        case "CG":
            return "Congo";
            break;
        case "CD":
            return "Congo, the Democratic Republic of the";
            break;
        case "CK":
            return "Cook Islands";
            break;
        case "CR":
            return "Costa Rica";
            break;
        case "CI":
            return "Cote d'Ivoire";
            break;
        case "HR":
            return "Croatia";
            break;
        case "CU":
            return "Cuba";
            break;
        case "CY":
            return "Cyprus";
            break;
        case "CZ":
            return "Czech Republic";
            break;
        case "DK":
            return "Denmark";
            break;
        case "DJ":
            return "Djibouti";
            break;
        case "DM":
            return "Dominica";
            break;
        case "DO":
            return "Dominican Republic";
            break;
        case "EC":
            return "Ecuador";
            break;
        case "EG":
            return "Egypt";
            break;
        case "SV":
            return "El Salvador";
            break;
        case "GQ":
            return "Equatorial Guinea";
            break;
        case "ER":
            return "Eritrea";
            break;
        case "EE":
            return "Estonia";
            break;
        case "ET":
            return "Ethiopia";
            break;
        case "FK":
            return "Falkland Islands (Malvinas)";
            break;
        case "FO":
            return "Faroe Islands";
            break;
        case "FJ":
            return "Fiji";
            break;
        case "FI":
            return "Finland";
            break;
        case "FR":
            return "France";
            break;
        case "GF":
            return "French Guiana";
            break;
        case "PF":
            return "French Polynesia";
            break;
        case "TF":
            return "French Southern Territories";
            break;
        case "GA":
            return "Gabon";
            break;
        case "GM":
            return "Gambia";
            break;
        case "GE":
            return "Georgia";
            break;
        case "DE":
            return "Germany";
            break;
        case "GH":
            return "Ghana";
            break;
        case "GI":
            return "Gibraltar";
            break;
        case "GR":
            return "Greece";
            break;
        case "GL":
            return "Greenland";
            break;
        case "GD":
            return "Grenada";
            break;
        case "GP":
            return "Guadeloupe";
            break;
        case "GU":
            return "Guam";
            break;
        case "GT":
            return "Guatemala";
            break;
        case "GG":
            return "Guernsey";
            break;
        case "GN":
            return "Guinea";
            break;
        case "GW":
            return "Guinea-Bissau";
            break;
        case "GY":
            return "Guyana";
            break;
        case "HT":
            return "Haiti";
            break;
        case "HM":
            return "Heard Island and McDonald Islands";
            break;
        case "VA":
            return "Holy See (Vatican City State)";
            break;
        case "HN":
            return "Honduras";
            break;
        case "HK":
            return "Hong Kong";
            break;
        case "HU":
            return "Hungary";
            break;
        case "IS":
            return "Iceland";
            break;
        case "IN":
            return "India";
            break;
        case "ID":
            return "Indonesia";
            break;
        case "IR":
            return "Iran, Islamic Republic of";
            break;
        case "IQ":
            return "Iraq";
            break;
        case "IE":
            return "Ireland";
            break;
        case "IM":
            return "Isle of Man";
            break;
        case "IL":
            return "Israel";
            break;
        case "IT":
            return "Italy";
            break;
        case "JM":
            return "Jamaica";
            break;
        case "JP":
            return "Japan";
            break;
        case "JE":
            return "Jersey";
            break;
        case "JO":
            return "Jordan";
            break;
        case "KZ":
            return "Kazakhstan";
            break;
        case "KE":
            return "Kenya";
            break;
        case "KI":
            return "Kiribati";
            break;
        case "KP":
            return "Korea, Democratic People's Republic of";
            break;
        case "KR":
            return "Korea, Republic of";
            break;
        case "KW":
            return "Kuwait";
            break;
        case "KG":
            return "Kyrgyzstan";
            break;
        case "LA":
            return "Lao People's Democratic Republic";
            break;
        case "LV":
            return "Latvia";
            break;
        case "LB":
            return "Lebanon";
            break;
        case "LS":
            return "Lesotho";
            break;
        case "LR":
            return "Liberia";
            break;
        case "LY":
            return "Libyan Arab Jamahiriya";
            break;
        case "LI":
            return "Liechtenstein";
            break;
        case "LT":
            return "Lithuania";
            break;
        case "LU":
            return "Luxembourg";
            break;
        case "MO":
            return "Macao";
            break;
        case "MK":
            return "Macedonia, the former Yugoslav Republic of";
            break;
        case "MG":
            return "Madagascar";
            break;
        case "MW":
            return "Malawi";
            break;
        case "MY":
            return "Malaysia";
            break;
        case "MV":
            return "Maldives";
            break;
        case "ML":
            return "Mali";
            break;
        case "MT":
            return "Malta";
            break;
        case "MH":
            return "Marshall Islands";
            break;
        case "MQ":
            return "Martinique";
            break;
        case "MR":
            return "Mauritania";
            break;
        case "MU":
            return "Mauritius";
            break;
        case "YT":
            return "Mayotte";
            break;
        case "MX":
            return "Mexico";
            break;
        case "FM":
            return "Micronesia, Federated States of";
            break;
        case "MD":
            return "Moldova, Republic of";
            break;
        case "MC":
            return "Monaco";
            break;
        case "MN":
            return "Mongolia";
            break;
        case "ME":
            return "Montenegro";
            break;
        case "MS":
            return "Montserrat";
            break;
        case "MA":
            return "Morocco";
            break;
        case "MZ":
            return "Mozambique";
            break;
        case "MM":
            return "Myanmar";
            break;
        case "NA":
            return "Namibia";
            break;
        case "NR":
            return "Nauru";
            break;
        case "NP":
            return "Nepal";
            break;
        case "NL":
            return "Netherlands";
            break;
        case "AN":
            return "Netherlands Antilles";
            break;
        case "NC":
            return "New Caledonia";
            break;
        case "NZ":
            return "New Zealand";
            break;
        case "NI":
            return "Nicaragua";
            break;
        case "NE":
            return "Niger";
            break;
        case "NG":
            return "Nigeria";
            break;
        case "NU":
            return "Niue";
            break;
        case "NF":
            return "Norfolk Island";
            break;
        case "MP":
            return "Northern Mariana Islands";
            break;
        case "NO":
            return "Norway";
            break;
        case "OM":
            return "Oman";
            break;
        case "PK":
            return "Pakistan";
            break;
        case "PW":
            return "Palau";
            break;
        case "PS":
            return "Palestinian Territory, Occupied";
            break;
        case "PA":
            return "Panama";
            break;
        case "PG":
            return "Papua New Guinea";
            break;
        case "PY":
            return "Paraguay";
            break;
        case "PE":
            return "Peru";
            break;
        case "PH":
            return "Philippines";
            break;
        case "PN":
            return "Pitcairn";
            break;
        case "PL":
            return "Poland";
            break;
        case "PT":
            return "Portugal";
            break;
        case "PR":
            return "Puerto Rico";
            break;
        case "QA":
            return "Qatar";
            break;
        case "RE":
            return "Reunion  Reunion";
            break;
        case "RO":
            return "Romania";
            break;
        case "RU":
            return "Russian Federation";
            break;
        case "RW":
            return "Rwanda";
            break;
        case "BL":
            return "Saint Barthelemy";
            break;
        case "SH":
            return "Saint Helena";
            break;
        case "KN":
            return "Saint Kitts and Nevis";
            break;
        case "LC":
            return "Saint Lucia";
            break;
        case "MF":
            return "Saint Martin (French part)";
            break;
        case "PM":
            return "Saint Pierre and Miquelon";
            break;
        case "VC":
            return "Saint Vincent and the Grenadines";
            break;
        case "WS":
            return "Samoa";
            break;
        case "SM":
            return "San Marino";
            break;
        case "ST":
            return "Sao Tome and Principe";
            break;
        case "SA":
            return "Saudi Arabia";
            break;
        case "SN":
            return "Senegal";
            break;
        case "RS":
            return "Serbia";
            break;
        case "SC":
            return "Seychelles";
            break;
        case "SL":
            return "Sierra Leone";
            break;
        case "SG":
            return "Singapore";
            break;
        case "SK":
            return "Slovakia";
            break;
        case "SI":
            return "Slovenia";
            break;
        case "SB":
            return "Solomon Islands";
            break;
        case "SO":
            return "Somalia";
            break;
        case "ZA":
            return "South Africa";
            break;
        case "GS":
            return "South Georgia and the South Sandwich Islands";
            break;
        case "ES":
            return "Spain";
            break;
        case "LK":
            return "Sri Lanka";
            break;
        case "SD":
            return "Sudan";
            break;
        case "SR":
            return "Suriname";
            break;
        case "SJ":
            return "Svalbard and Jan Mayen";
            break;
        case "SZ":
            return "Swaziland";
            break;
        case "SE":
            return "Sweden";
            break;
        case "CH":
            return "Switzerland";
            break;
        case "SY":
            return "Syrian Arab Republic";
            break;
        case "TW":
            return "Taiwan, Province of China";
            break;
        case "TJ":
            return "Tajikistan";
            break;
        case "TZ":
            return "Tanzania, United Republic of";
            break;
        case "TH":
            return "Thailand";
            break;
        case "TL":
            return "Timor-Leste";
            break;
        case "TG":
            return "Togo";
            break;
        case "TK":
            return "Tokelau";
            break;
        case "TO":
            return "Tonga";
            break;
        case "TT":
            return "Trinidad and Tobago";
            break;
        case "TN":
            return "Tunisia";
            break;
        case "TR":
            return "Turkey";
            break;
        case "TM":
            return "Turkmenistan";
            break;
        case "TC":
            return "Turks and Caicos Islands";
            break;
        case "TV":
            return "Tuvalu";
            break;
        case "UG":
            return "Uganda";
            break;
        case "UA":
            return "Ukraine";
            break;
        case "AE":
            return "United Arab Emirates";
            break;
        case "GB":
            return "United Kingdom";
            break;
        case "US":
            return "United States";
            break;
        case "UM":
            return "United States Minor Outlying Islands";
            break;
        case "UY":
            return "Uruguay";
            break;
        case "UZ":
            return "Uzbekistan";
            break;
        case "VU":
            return "Vanuatu";
            break;
        case "VE":
            return "Venezuela, Bolivarian Republic of";
            break;
        case "VN":
            return "Viet Nam";
            break;
        case "VG":
            return "Virgin Islands, British";
            break;
        case "VI":
            return "Virgin Islands, U.S.";
            break;
        case "WF":
            return "Wallis and Futuna";
            break;
        case "EH":
            return "Western Sahara";
            break;
        case "YE":
            return "Yemen";
            break;
        case "ZM":
            return "Zambia";
            break;
        case "ZW":
            return "Zimbabwe";
            break;
    }
}

function getCountryCode(countryName) {
    switch (countryName) {
        case "Afghanistan" :
            return "AF";
            break;
        case "Aland Islands" :
            return "AX";
            break;
        case "Albania" :
            return "AL";
            break;
        case "Algeria" :
            return "DZ";
            break;
        case "American Samoa" :
            return "AS";
            break;
        case "Andorra" :
            return "AD";
            break;
        case "Angola" :
            return "AO";
            break;
        case "Anguilla" :
            return "AI";
            break;
        case "Antarctica" :
            return "AQ";
            break;
        case "Antigua and Barbuda" :
            return "AG";
            break;
        case "Argentina" :
            return "AR";
            break;
        case "Armenia" :
            return "AM";
            break;
        case "Aruba" :
            return "AW";
            break;
        case "Australia" :
            return "AU";
            break;
        case "Austria" :
            return "AT";
            break;
        case "Azerbaijan" :
            return "AZ";
            break;
        case "Bahamas" :
            return "BS";
            break;
        case "Bahrain" :
            return "BH";
            break;
        case "Bangladesh" :
            return "BD";
            break;
        case "Barbados" :
            return "BB";
            break;
        case "Belarus" :
            return "BY";
            break;
        case "Belgium" :
            return "BE";
            break;
        case "Belize" :
            return "BZ";
            break;
        case "Benin" :
            return "BJ";
            break;
        case "Bermuda" :
            return "BM";
            break;
        case "Bhutan" :
            return "BT";
            break;
        case "Bolivia, Plurinational State of" :
            return "BO";
            break;
        case "Bosnia and Herzegovina" :
            return "BA";
            break;
        case "Botswana" :
            return "BW";
            break;
        case "Bouvet Island" :
            return "BV";
            break;
        case "Brazil" :
            return "BR";
            break;
        case "British Indian Ocean Territory" :
            return "IO";
            break;
        case "Brunei Darussalam" :
            return "BN";
            break;
        case "Bulgaria" :
            return "BG";
            break;
        case "Burkina Faso" :
            return "BF";
            break;
        case "Burundi" :
            return "BI";
            break;
        case "Cambodia" :
            return "KH";
            break;
        case "Cameroon" :
            return "CM";
            break;
        case "Canada" :
            return "CA";
            break;
        case "Cape Verde" :
            return "CV";
            break;
        case "Cayman Islands" :
            return "KY";
            break;
        case "Central African Republic" :
            return "CF";
            break;
        case "Chad" :
            return "TD";
            break;
        case "Chile" :
            return "CL";
            break;
        case "China" :
            return "CN";
            break;
        case "Christmas Island" :
            return "CX";
            break;
        case "Cocos (Keeling) Islands" :
            return "CC";
            break;
        case "Colombia" :
            return "CO";
            break;
        case "Comoros" :
            return "KM";
            break;
        case "Congo" :
            return "CG";
            break;
        case "Congo, the Democratic Republic of the" :
            return "CD";
            break;
        case "Cook Islands" :
            return "CK";
            break;
        case "Costa Rica" :
            return "CR";
            break;
        case "Cote d'Ivoire" :
            return "CI";
            break;
        case "Croatia" :
            return "HR";
            break;
        case "Cuba" :
            return "CU";
            break;
        case "Cyprus" :
            return "CY";
            break;
        case "Czech Republic" :
            return "CZ";
            break;
        case "Denmark" :
            return "DK";
            break;
        case "Djibouti" :
            return "DJ";
            break;
        case "Dominica" :
            return "DM";
            break;
        case "Dominican Republic" :
            return "DO";
            break;
        case "Ecuador" :
            return "EC";
            break;
        case "Egypt" :
            return "EG";
            break;
        case "El Salvador" :
            return "SV";
            break;
        case "Equatorial Guinea" :
            return "GQ";
            break;
        case "Eritrea" :
            return "ER";
            break;
        case "Estonia" :
            return "EE";
            break;
        case "Ethiopia" :
            return "ET";
            break;
        case "Falkland Islands (Malvinas)" :
            return "FK";
            break;
        case "Faroe Islands" :
            return "FO";
            break;
        case "Fiji" :
            return "FJ";
            break;
        case "Finland" :
            return "FI";
            break;
        case "France" :
            return "FR";
            break;
        case "French Guiana" :
            return "GF";
            break;
        case "French Polynesia" :
            return "PF";
            break;
        case "French Southern Territories" :
            return "TF";
            break;
        case "Gabon" :
            return "GA";
            break;
        case "Gambia" :
            return "GM";
            break;
        case "Georgia" :
            return "GE";
            break;
        case "Germany" :
            return "DE";
            break;
        case "Ghana" :
            return "GH";
            break;
        case "Gibraltar" :
            return "GI";
            break;
        case "Greece" :
            return "GR";
            break;
        case "Greenland" :
            return "GL";
            break;
        case "Grenada" :
            return "GD";
            break;
        case "Guadeloupe" :
            return "GP";
            break;
        case "Guam" :
            return "GU";
            break;
        case "Guatemala" :
            return "GT";
            break;
        case "Guernsey" :
            return "GG";
            break;
        case "Guinea" :
            return "GN";
            break;
        case "Guinea-Bissau" :
            return "GW";
            break;
        case "Guyana" :
            return "GY";
            break;
        case "Haiti" :
            return "HT";
            break;
        case "Heard Island and McDonald Islands" :
            return "HM";
            break;
        case "Holy See (Vatican City State)" :
            return "VA";
            break;
        case "Honduras" :
            return "HN";
            break;
        case "Hong Kong" :
            return "HK";
            break;
        case "Hungary" :
            return "HU";
            break;
        case "Iceland" :
            return "IS";
            break;
        case "India" :
            return "IN";
            break;
        case "Indonesia" :
            return "ID";
            break;
        case "Iran, Islamic Republic of" :
            return "IR";
            break;
        case "Iraq" :
            return "IQ";
            break;
        case "Ireland" :
            return "IE";
            break;
        case "Isle of Man" :
            return "IM";
            break;
        case "Israel" :
            return "IL";
            break;
        case "Italy" :
            return "IT";
            break;
        case "Jamaica" :
            return "JM";
            break;
        case "Japan" :
            return "JP";
            break;
        case "Jersey" :
            return "JE";
            break;
        case "Jordan" :
            return "JO";
            break;
        case "Kazakhstan" :
            return "KZ";
            break;
        case "Kenya" :
            return "KE";
            break;
        case "Kiribati" :
            return "KI";
            break;
        case "Korea, Democratic People's Republic of" :
            return "KP";
            break;
        case "Korea, Republic of" :
            return "KR";
            break;
        case "Kuwait" :
            return "KW";
            break;
        case "Kyrgyzstan" :
            return "KG";
            break;
        case "Lao People's Democratic Republic" :
            return "LA";
            break;
        case "Latvia" :
            return "LV";
            break;
        case "Lebanon" :
            return "LB";
            break;
        case "Lesotho" :
            return "LS";
            break;
        case "Liberia" :
            return "LR";
            break;
        case "Libyan Arab Jamahiriya" :
            return "LY";
            break;
        case "Liechtenstein" :
            return "LI";
            break;
        case "Lithuania" :
            return "LT";
            break;
        case "Luxembourg" :
            return "LU";
            break;
        case "Macao" :
            return "MO";
            break;
        case "Macedonia, the former Yugoslav Republic of" :
            return "MK";
            break;
        case "Madagascar" :
            return "MG";
            break;
        case "Malawi" :
            return "MW";
            break;
        case "Malaysia" :
            return "MY";
            break;
        case "Maldives" :
            return "MV";
            break;
        case "Mali" :
            return "ML";
            break;
        case "Malta" :
            return "MT";
            break;
        case "Marshall Islands" :
            return "MH";
            break;
        case "Martinique" :
            return "MQ";
            break;
        case "Mauritania" :
            return "MR";
            break;
        case "Mauritius" :
            return "MU";
            break;
        case "Mayotte" :
            return "YT";
            break;
        case "Mexico" :
            return "MX";
            break;
        case "Micronesia, Federated States of" :
            return "FM";
            break;
        case "Moldova, Republic of" :
            return "MD";
            break;
        case "Monaco" :
            return "MC";
            break;
        case "Mongolia" :
            return "MN";
            break;
        case "Montenegro" :
            return "ME";
            break;
        case "Montserrat" :
            return "MS";
            break;
        case "Morocco" :
            return "MA";
            break;
        case "Mozambique" :
            return "MZ";
            break;
        case "Myanmar" :
            return "MM";
            break;
        case "Namibia" :
            return "NA";
            break;
        case "Nauru" :
            return "NR";
            break;
        case "Nepal" :
            return "NP";
            break;
        case "Netherlands" :
            return "NL";
            break;
        case "Netherlands Antilles" :
            return "AN";
            break;
        case "New Caledonia" :
            return "NC";
            break;
        case "New Zealand" :
            return "NZ";
            break;
        case "Nicaragua" :
            return "NI";
            break;
        case "Niger" :
            return "NE";
            break;
        case "Nigeria" :
            return "NG";
            break;
        case "Niue" :
            return "NU";
            break;
        case "Norfolk Island" :
            return "NF";
            break;
        case "Northern Mariana Islands" :
            return "MP";
            break;
        case "Norway" :
            return "NO";
            break;
        case "Oman" :
            return "OM";
            break;
        case "Pakistan" :
            return "PK";
            break;
        case "Palau" :
            return "PW";
            break;
        case "Palestinian Territory, Occupied" :
            return "PS";
            break;
        case "Panama" :
            return "PA";
            break;
        case "Papua New Guinea" :
            return "PG";
            break;
        case "Paraguay" :
            return "PY";
            break;
        case "Peru" :
            return "PE";
            break;
        case "Philippines" :
            return "PH";
            break;
        case "Pitcairn" :
            return "PN";
            break;
        case "Poland" :
            return "PL";
            break;
        case "Portugal" :
            return "PT";
            break;
        case "Puerto Rico" :
            return "PR";
            break;
        case "Qatar" :
            return "QA";
            break;
        case "Reunion  Reunion" :
            return "RE";
            break;
        case "Romania" :
            return "RO";
            break;
        case "Russian Federation" :
            return "RU";
            break;
        case "Rwanda" :
            return "RW";
            break;
        case "Saint Barthelemy" :
            return "BL";
            break;
        case "Saint Helena" :
            return "SH";
            break;
        case "Saint Kitts and Nevis" :
            return "KN";
            break;
        case "Saint Lucia" :
            return "LC";
            break;
        case "Saint Martin (French part)" :
            return "MF";
            break;
        case "Saint Pierre and Miquelon" :
            return "PM";
            break;
        case "Saint Vincent and the Grenadines" :
            return "VC";
            break;
        case "Samoa" :
            return "WS";
            break;
        case "San Marino" :
            return "SM";
            break;
        case "Sao Tome and Principe" :
            return "ST";
            break;
        case "Saudi Arabia" :
            return "SA";
            break;
        case "Senegal" :
            return "SN";
            break;
        case "Serbia" :
            return "RS";
            break;
        case "Seychelles" :
            return "SC";
            break;
        case "Sierra Leone" :
            return "SL";
            break;
        case "Singapore" :
            return "SG";
            break;
        case "Slovakia" :
            return "SK";
            break;
        case "Slovenia" :
            return "SI";
            break;
        case "Solomon Islands" :
            return "SB";
            break;
        case "Somalia" :
            return "SO";
            break;
        case "South Africa" :
            return "ZA";
            break;
        case "South Georgia and the South Sandwich Islands" :
            return "GS";
            break;
        case "Spain" :
            return "ES";
            break;
        case "Sri Lanka" :
            return "LK";
            break;
        case "Sudan" :
            return "SD";
            break;
        case "Suriname" :
            return "SR";
            break;
        case "Svalbard and Jan Mayen" :
            return "SJ";
            break;
        case "Swaziland" :
            return "SZ";
            break;
        case "Sweden" :
            return "SE";
            break;
        case "Switzerland" :
            return "CH";
            break;
        case "Syrian Arab Republic" :
            return "SY";
            break;
        case "Taiwan, Province of China" :
            return "TW";
            break;
        case "Tajikistan" :
            return "TJ";
            break;
        case "Tanzania, United Republic of" :
            return "TZ";
            break;
        case "Thailand" :
            return "TH";
            break;
        case "Timor-Leste" :
            return "TL";
            break;
        case "Togo" :
            return "TG";
            break;
        case "Tokelau" :
            return "TK";
            break;
        case "Tonga" :
            return "TO";
            break;
        case "Trinidad and Tobago" :
            return "TT";
            break;
        case "Tunisia" :
            return "TN";
            break;
        case "Turkey" :
            return "TR";
            break;
        case "Turkmenistan" :
            return "TM";
            break;
        case "Turks and Caicos Islands" :
            return "TC";
            break;
        case "Tuvalu" :
            return "TV";
            break;
        case "Uganda" :
            return "UG";
            break;
        case "Ukraine" :
            return "UA";
            break;
        case "United Arab Emirates" :
            return "AE";
            break;
        case "United Kingdom" :
            return "GB";
            break;
        case "United States" :
            return "US";
            break;
        case "United States Minor Outlying Islands" :
            return "UM";
            break;
        case "Uruguay" :
            return "UY";
            break;
        case "Uzbekistan" :
            return "UZ";
            break;
        case "Vanuatu" :
            return "VU";
            break;
        case "Venezuela, Bolivarian Republic of" :
            return "VE";
            break;
        case "Viet Nam" :
            return "VN";
            break;
        case "Virgin Islands, British" :
            return "VG";
            break;
        case "Virgin Islands, U.S." :
            return "VI";
            break;
        case "Wallis and Futuna" :
            return "WF";
            break;
        case "Western Sahara" :
            return "EH";
            break;
        case "Yemen" :
            return "YE";
            break;
        case "Zambia" :
            return "ZM";
            break;
        case "Zimbabwe" :
            return "ZW";
            break;
    }
}