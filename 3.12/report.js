function add_class_mouseover(x)
{
    x.classList.add('mouseover');
}

function remove_class_mouseover(x)
{
    x.classList.remove('mouseover');
}

function update_checkbox(checkbox_id, checked)
{
    var checkbox = document.getElementById(checkbox_id);
    checkbox.checked = checked;
}

/* We also add/remove the 'selected' class on the "toggle" element (currently
   a TD of class 'toggle' but could be anything) surrounding the checkbox. */
function update_toggle(toggle_id, selected)
{
    var toggle = document.getElementById(toggle_id);
    if (selected) {
        toggle.classList.add('selected');
    } else {
        toggle.classList.remove('selected');
    }
}

var timeout_toggle_exists;
var error_toggle_exists;
var warnings_toggle_exists;
var ok_toggle_exists;

var show_timeout_gcards;
var show_error_gcards;
var show_warnings_gcards;
var show_ok_gcards;

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
}

function update_checkboxes()
{
    if (timeout_toggle_exists) {
        update_checkbox('timeout_checkbox', show_timeout_gcards);
        update_toggle('timeout_toggle', show_timeout_gcards);
    }
    if (error_toggle_exists) {
        update_checkbox('error_checkbox', show_error_gcards);
        update_toggle('error_toggle', show_error_gcards);
    }
    if (warnings_toggle_exists) {
        update_checkbox('warnings_checkbox', show_warnings_gcards);
        update_toggle('warnings_toggle', show_warnings_gcards);
    }
    if (ok_toggle_exists) {
        update_checkbox('ok_checkbox', show_ok_gcards);
        update_toggle('ok_toggle', show_ok_gcards);
    }
}

function initialize()
{
    timeout_toggle_exists  = document.getElementById('timeout_toggle') != null;
    error_toggle_exists    = document.getElementById('error_toggle') != null;
    warnings_toggle_exists = document.getElementById('warnings_toggle') != null;
    ok_toggle_exists       = document.getElementById('ok_toggle') != null;
    show_timeout_gcards  = true;
    show_error_gcards    = true;
    show_warnings_gcards = true;
    show_ok_gcards       = true;
    show_selected_gcards();
    update_checkboxes();
}

function update_selection(classname)
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
}

function filter_gcards(classname)
{
    update_selection(classname);
    show_selected_gcards();
    update_checkboxes();
}

