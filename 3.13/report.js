function add_class_mouseover(x)
{
    x.classList.add('mouseover');
}

function remove_class_mouseover(x)
{
    x.classList.remove('mouseover');
}

function update_toggle(toggle_id, on)
{
    var toggle = document.getElementById(toggle_id);
    if (toggle != null) {
        if (on) {
            toggle.classList.add('selected');
        } else {
            toggle.classList.remove('selected');
        }
    }
}

function update_checkbox(checkbox_id, checked)
{
    var checkbox = document.getElementById(checkbox_id);
    if (checkbox != null)
        checkbox.checked = checked;
}

var show_timeout_cards  = true;
var show_error_cards    = true;
var show_warnings_cards = true;
var show_ok_cards       = true;

function show_selected_gcards()
{
    var table = document.getElementById("THE_BIG_GCARD_LIST");
    for (var i = 0, tbody; tbody = table.tBodies[i]; i++) {
        if (tbody.classList.contains('collapsable_rows')) {
            show = show_ok_cards;
        } else if (tbody.classList.contains('gcard_separator')
                || tbody.classList.contains('gcard'))
        {
            show = false;
            if (show_timeout_cards)
                show ||= tbody.classList.contains('timeout');
            if (show_error_cards)
                show ||= tbody.classList.contains('error');
            if (show_warnings_cards)
                show ||= tbody.classList.contains('warnings');
            if (show_ok_cards)
                show ||= tbody.classList.contains('ok');
        } else {
            show = true;
        }
        if (show) {
            tbody.style['display'] = 'table-row-group';
        } else {
            tbody.style['display'] = 'none';
        }
    }
}

function update_filter_toggles()
{
    update_toggle('timeout_toggle', show_timeout_cards);
    update_checkbox('timeout_checkbox', show_timeout_cards);

    update_toggle('error_toggle', show_error_cards);
    update_checkbox('error_checkbox', show_error_cards);

    update_toggle('warnings_toggle', show_warnings_cards);
    update_checkbox('warnings_checkbox', show_warnings_cards);

    update_toggle('ok_toggle', show_ok_cards);
    update_checkbox('ok_checkbox', show_ok_cards);
}

function initialize()
{
    update_filter_toggles();
}

function filter_gcards(classname)
{
    if (show_timeout_cards &&
        show_error_cards &&
        show_warnings_cards &&
        show_ok_cards)
    {
        show_timeout_cards =
        show_error_cards =
        show_warnings_cards =
        show_ok_cards = false;
    }
    if (classname == 'timeout')
        show_timeout_cards = !show_timeout_cards;
    if (classname == 'error')
        show_error_cards = !show_error_cards;
    if (classname == 'warnings')
        show_warnings_cards = !show_warnings_cards;
    if (classname == 'ok')
        show_ok_cards = !show_ok_cards;
    if (!show_timeout_cards &&
        !show_error_cards &&
        !show_warnings_cards &&
        !show_ok_cards)
    {
        show_timeout_cards =
        show_error_cards =
        show_warnings_cards =
        show_ok_cards = true;
    }
    show_selected_gcards();
    update_filter_toggles();
}

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

function OLD_initialize(){
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

