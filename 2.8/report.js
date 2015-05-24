function changecss(theClass,element,value) 
{
    var cssRules;
    if (document.all) {
	cssRules = 'rules';
    }
    else if (document.getElementById) {
	cssRules = 'cssRules';
    }
    var added = false;
    for (var S = 0; S < document.styleSheets.length; S++){
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
    document.getElementById("ok").checked=true;
    document.getElementById("warnings").checked=true;
    document.getElementById("error").checked=true;
    document.getElementById("timeout").checked=true;
}

function toggle(theClass) {
    var fullClass = "TABLE.mainrep TR."+theClass;
    var element = "display";
    var show;
    if(document.getElementById(theClass).checked){
	show = "table-row";
	if(theClass=="ok"){
	    changecss("TABLE.mainrep TR.abc", element, "table-row");
	}
    }else{
	show = "none";
	    if(theClass=="ok"){
		changecss("TABLE.mainrep TR.abc", element, "none");
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
    changecss("TABLE.mainrep TR.warnings.error.timeout", element, "none");
    changecss("TABLE.mainrep TR.warnings.error", element, "none");
    changecss("TABLE.mainrep TR.warnings.timeout", element, "none");
    changecss("TABLE.mainrep TR.error.timeout", element, "none");
    switch(selections)
    {
    case 1:
	changecss("TABLE.mainrep TR.warnings.error", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.error.timeout", element, "table-row");
	break;    
    case 2:
	changecss("TABLE.mainrep TR.warnings.error", element, "table-row");
	changecss("TABLE.mainrep TR.error.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.error.timeout", element, "table-row");
	break;    
    case 3:
	changecss("TABLE.mainrep TR.warnings.error", element, "table-row");
	changecss("TABLE.mainrep TR.error.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.error.timeout", element, "table-row");
	break;   
    case 4:
	changecss("TABLE.mainrep TR.warnings.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.error.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.error.timeout", element, "table-row");
	break;   	
    case 5:
	changecss("TABLE.mainrep TR.warnings.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.error.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.error.timeout", element, "table-row");
	break;
    case 6:
	changecss("TABLE.mainrep TR.error.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.error", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.error.timeout", element, "table-row");
    case 7:
	changecss("TABLE.mainrep TR.warnings.error.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.error", element, "table-row");
	changecss("TABLE.mainrep TR.warnings.timeout", element, "table-row");
	changecss("TABLE.mainrep TR.error.timeout", element, "table-row");
	break;
    }
}

  