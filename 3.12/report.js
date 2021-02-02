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
function update_toggle(toggle, selected)
{
    if (selected) {
        toggle.classList.add('selected');
    } else {
        toggle.classList.remove('selected');
    }
}

var THE_BIG_GCARD_LIST;

var timeout_toggle;
var error_toggle;
var warnings_toggle;
var ok_toggle;

var show_timeout_gcards;
var show_error_gcards;
var show_warnings_gcards;
var show_ok_gcards;

function show_selected_gcards()
{
    if (show_timeout_gcards)
        THE_BIG_GCARD_LIST.classList.add('show_timeout_gcards');
    else
        THE_BIG_GCARD_LIST.classList.remove('show_timeout_gcards');
    if (show_error_gcards)
        THE_BIG_GCARD_LIST.classList.add('show_error_gcards');
    else
        THE_BIG_GCARD_LIST.classList.remove('show_error_gcards');
    if (show_warnings_gcards)
        THE_BIG_GCARD_LIST.classList.add('show_warnings_gcards');
    else
        THE_BIG_GCARD_LIST.classList.remove('show_warnings_gcards');
    if (show_ok_gcards)
        THE_BIG_GCARD_LIST.classList.add('show_ok_gcards');
    else
        THE_BIG_GCARD_LIST.classList.remove('show_ok_gcards');
}

function update_checkboxes()
{
    if (timeout_toggle  != null) {
        update_checkbox('timeout_checkbox', show_timeout_gcards);
        update_toggle(timeout_toggle, show_timeout_gcards);
    }
    if (error_toggle    != null) {
        update_checkbox('error_checkbox', show_error_gcards);
        update_toggle(error_toggle, show_error_gcards);
    }
    if (warnings_toggle != null) {
        update_checkbox('warnings_checkbox', show_warnings_gcards);
        update_toggle(warnings_toggle, show_warnings_gcards);
    }
    if (ok_toggle       != null) {
        update_checkbox('ok_checkbox', show_ok_gcards);
        update_toggle(ok_toggle, show_ok_gcards);
    }
}

function initialize()
{
    THE_BIG_GCARD_LIST = document.getElementById("THE_BIG_GCARD_LIST");
    if (THE_BIG_GCARD_LIST != null) {
        timeout_toggle  = document.getElementById('timeout_toggle');
        error_toggle    = document.getElementById('error_toggle');
        warnings_toggle = document.getElementById('warnings_toggle');
        ok_toggle       = document.getElementById('ok_toggle');
        show_timeout_gcards  = true;
        show_error_gcards    = true;
        show_warnings_gcards = true;
        show_ok_gcards       = true;
        show_selected_gcards();
        update_checkboxes();
    }
}

function update_selection(classname)
{
    if ((timeout_toggle  == null || show_timeout_gcards) &&
        (error_toggle    == null || show_error_gcards) &&
        (warnings_toggle == null || show_warnings_gcards) &&
        (ok_toggle       == null || show_ok_gcards))
    {
        if (timeout_toggle  != null)
            show_timeout_gcards  = false;
        if (error_toggle    != null)
            show_error_gcards    = false;
        if (warnings_toggle != null)
            show_warnings_gcards = false;
        if (ok_toggle       != null)
            show_ok_gcards       = false;
    }

    if (classname == 'timeout')
        show_timeout_gcards = !show_timeout_gcards;
    if (classname == 'error')
        show_error_gcards = !show_error_gcards;
    if (classname == 'warnings')
        show_warnings_gcards = !show_warnings_gcards;
    if (classname == 'ok')
        show_ok_gcards = !show_ok_gcards;

    if ((timeout_toggle  == null || !show_timeout_gcards) &&
        (error_toggle    == null || !show_error_gcards) &&
        (warnings_toggle == null || !show_warnings_gcards) &&
        (ok_toggle       == null || !show_ok_gcards))
    {
        if (timeout_toggle  != null)
            show_timeout_gcards  = true;
        if (error_toggle    != null)
            show_error_gcards    = true;
        if (warnings_toggle != null)
            show_warnings_gcards = true;
        if (ok_toggle       != null)
            show_ok_gcards       = true;
    }
}

function filter_gcards(classname)
{
    update_selection(classname);
    show_selected_gcards();
    update_checkboxes();
}

