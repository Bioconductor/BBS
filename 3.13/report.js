
var vals = ["timeout", "error", "warnings", "ok"];

function changecss(theClass,element,value) 
{
    var cssRules;
    if (document.all) {
        cssRules = 'rules';
    } else if (document.getElementById) {
        cssRules = 'cssRules';
    }
    var added = false;
    for (var S = 0; S < document.styleSheets.length; S++){
        if (!document.styleSheets[S][cssRules])
            continue;
        for (var R = 0; R < document.styleSheets[S][cssRules].length; R++) {
            if (document.styleSheets[S][cssRules][R].selectorText == theClass) {
                if(document.styleSheets[S][cssRules][R].style[element]){
                    document.styleSheets[S][cssRules][R].style[element] = value;
                    added=true;
                    break;
                }
            }
        }
        if(!added){
            if(document.styleSheets[S].insertRule){
                document.styleSheets[S].insertRule(theClass+' { '+element+': '+value+'; }',
                   document.styleSheets[S][cssRules].length);
            } else if (document.styleSheets[S].addRule) {
                document.styleSheets[S].addRule(theClass,element+': '+value+';');
            }
        }
    }
}

function initialize(){
    var show = [];
    if (location.hash=="") {
        show = [true, true, true, true];
    } else if (location.hash.match(/^#show=/)) {
        var s = location.hash.replace(/^#show=/, "");
        s = s.replace(/ /g, "");
        var segs = s.split(",");
        for (i in vals) {
            var val = vals[i];
            var state = (segs.indexOf(val) > -1);
            show.push(state);
        }
    }
    for (i in show) {
        document.getElementById(vals[i]).checked=show[i];
        if(!show[i])
            toggle(vals[i]);
    }
}

function toggle(theClass) {
    var fullClass = "TABLE.gcard_list TBODY."+theClass;
    var element = "display";
    var show;
    if(document.getElementById(theClass).checked){
        show = "table-row-group";
        if(theClass=="ok"){
            changecss("TABLE.gcard_list TBODY.collapsable_rows", element, "table-row-group");
        }
    }else{
        show = "none";
        if(theClass=="ok"){
            changecss("TABLE.gcard_list TBODY.collapsable_rows", element, "none");
        }
    }
    changecss(fullClass, element, show)
    var errors = document.getElementById("error").checked;
    var warnings = document.getElementById("warnings").checked;
    var timeouts = document.getElementById("timeout").checked;
    var selections = 0;
    if(errors)
        selections = selections+2;
    if(warnings)
        selections = selections+1;
    if(timeouts)
        selections = selections+4;
    changecss("TABLE.gcard_list TBODY.warnings.error.timeout", element, "none");
    changecss("TABLE.gcard_list TBODY.warnings.error", element, "none");
    changecss("TABLE.gcard_list TBODY.warnings.timeout", element, "none");
    changecss("TABLE.gcard_list TBODY.error.timeout", element, "none");
    switch(selections)
    {
    case 1:
        changecss("TABLE.gcard_list TBODY.warnings.error", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.error.timeout", element, "table-row-group");
        break;    
    case 2:
        changecss("TABLE.gcard_list TBODY.warnings.error", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.error.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.error.timeout", element, "table-row-group");
        break;    
    case 3:
        changecss("TABLE.gcard_list TBODY.warnings.error", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.error.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.error.timeout", element, "table-row-group");
        break;   
    case 4:
        changecss("TABLE.gcard_list TBODY.warnings.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.error.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.error.timeout", element, "table-row-group");
        break;      
    case 5:
        changecss("TABLE.gcard_list TBODY.warnings.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.error.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.error.timeout", element, "table-row-group");
        break;
    case 6:
        changecss("TABLE.gcard_list TBODY.error.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.error", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.error.timeout", element, "table-row-group");
        // shouldn't there be a break here?
    case 7:
        changecss("TABLE.gcard_list TBODY.warnings.error.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.error", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.warnings.timeout", element, "table-row-group");
        changecss("TABLE.gcard_list TBODY.error.timeout", element, "table-row-group");
        break;
    }
    var on = [];
    for (i in vals) {
        var val = vals[i];
        if (document.getElementById(val).checked) {
            on.push(val);
        }
    }
    if (on.length == vals.length)
        location.hash = "";
    else if (on.length == 0)
        location.hash = "#show=none";
    else 
        location.hash = "#show=" + on.join(",");
}

