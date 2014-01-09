$.fn.dataTableExt.oApi.fnGetFilteredData = function (oSettings) {
    var a = [];
    for (var i = 0, iLen = oSettings.aiDisplay.length; i < iLen; i++) {
        a.push(oSettings.aoData[ oSettings.aiDisplay[i] ]._aData);
    }
    return a;
}