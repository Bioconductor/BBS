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

var show_timeout_gcards;
var show_error_gcards;
var show_warnings_gcards;
var show_ok_gcards;

var timeout_toggle_exists;
var error_toggle_exists;
var warnings_toggle_exists;
var ok_toggle_exists;

function show_selected_gcards()
{
    var table = document.getElementById("THE_BIG_GCARD_LIST");
    if (show_timeout_gcards)
        table.classList.add('show_timeout_gcards');
    else
        table.classList.remove('show_timeout_gcards');
    if (show_error_gcards)
        table.classList.add('show_error_gcards');
    else
        table.classList.remove('show_error_gcards');
    if (show_warnings_gcards)
        table.classList.add('show_warnings_gcards');
    else
        table.classList.remove('show_warnings_gcards');
    if (show_ok_gcards)
        table.classList.add('show_ok_gcards');
    else
        table.classList.remove('show_ok_gcards');
/*
    for (var i = 0, tbody; tbody = table.tBodies[i]; i++) {
        if (tbody.classList.contains('collapsable_rows')) {
            show = show_ok_gcards;
        } else if (tbody.classList.contains('gcard_separator')
                || tbody.classList.contains('gcard'))
        {
            show = false;
            if (show_timeout_gcards)
                show ||= tbody.classList.contains('timeout');
            if (show_error_gcards)
                show ||= tbody.classList.contains('error');
            if (show_warnings_gcards)
                show ||= tbody.classList.contains('warnings');
            //if (show_ok_gcards)
            //    show ||= tbody.classList.contains('ok');
        } else {
            show = true;
        }
        if (show) {
            tbody.style['display'] = 'table-row-group';
        } else {
            tbody.style['display'] = 'none';
        }
    }
*/
}

function update_selection_toggles()
{
    update_toggle('timeout_toggle', show_timeout_gcards);
    update_checkbox('timeout_checkbox', show_timeout_gcards);

    update_toggle('error_toggle', show_error_gcards);
    update_checkbox('error_checkbox', show_error_gcards);

    update_toggle('warnings_toggle', show_warnings_gcards);
    update_checkbox('warnings_checkbox', show_warnings_gcards);

    update_toggle('ok_toggle', show_ok_gcards);
    update_checkbox('ok_checkbox', show_ok_gcards);
}

function initialize()
{
    show_timeout_gcards  = true;
    show_error_gcards    = true;
    show_warnings_gcards = true;
    show_ok_gcards       = true;
    timeout_toggle_exists  = document.getElementById('timeout_toggle') != null;
    error_toggle_exists    = document.getElementById('error_toggle') != null;
    warnings_toggle_exists = document.getElementById('warnings_toggle') != null;
    ok_toggle_exists       = document.getElementById('ok_toggle') != null;
    show_selected_gcards();
    update_selection_toggles();
}

function filter_gcards(classname)
{

    if ((!timeout_toggle_exists || show_timeout_gcards) &&
        (!error_toggle_exists || show_error_gcards) &&
        (!warnings_toggle_exists || show_warnings_gcards) &&
        (!ok_toggle_exists || show_ok_gcards))
    {
        if (timeout_toggle_exists)
            show_timeout_gcards = false;
        if (error_toggle_exists)
            show_error_gcards = false;
        if (warnings_toggle_exists)
            show_warnings_gcards = false;
        if (ok_toggle_exists)
            show_ok_gcards = false;
    }
    if (classname == 'timeout')
        show_timeout_gcards = !show_timeout_gcards;
    if (classname == 'error')
        show_error_gcards = !show_error_gcards;
    if (classname == 'warnings')
        show_warnings_gcards = !show_warnings_gcards;
    if (classname == 'ok')
        show_ok_gcards = !show_ok_gcards;
    if ((!timeout_toggle_exists || !show_timeout_gcards) &&
        (!error_toggle_exists || !show_error_gcards) &&
        (!warnings_toggle_exists || !show_warnings_gcards) &&
        (!ok_toggle_exists || !show_ok_gcards))
    {
        if (timeout_toggle_exists)
            show_timeout_gcards = true;
        if (error_toggle_exists)
            show_error_gcards = true;
        if (warnings_toggle_exists)
            show_warnings_gcards = true;
        if (ok_toggle_exists)
            show_ok_gcards = true;
    }
    show_selected_gcards();
    update_selection_toggles();
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

