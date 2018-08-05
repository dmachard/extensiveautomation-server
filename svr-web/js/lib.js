/*
---------------------------------------------------------------
 Copyright (c) 2010-2018 Denis Machard. All rights reserved.

 This file is part of the extensive automation project; you can redistribute it and/or
 modify it under the terms of the GNU General Public License, Version 3.

 This file is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 See the GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License,
 along with this program. If not, see http://www.gnu.org/licenses/.
---------------------------------------------------------------
*/

/**
 * General navigation page 
 * @param {String} p
 */
function nav(p){ if (p != ""){ location.href = p ; } }

/**
 * Return value for HTML element the identify by id
 * @param {String} id
 */
function getval(id){ return document.getElementById(id).value; }

/**
 * Return checked for HTML element the identify by id
 * @param {String} id
 */
function getcheck(id){ return document.getElementById(id).checked; }


/**
 * Return element html identify by id
 * @param {String} id
 */
function getel(id){ return document.getElementById(id); }

/**
 * Return element html identify by id
 * @param {String} id
 */
function getelbyname(name){ return document.getElementsByName(name); }

/**
 * Return element html identify by id
 * @param {String} id
 */
function getcheckbyname(name){ return document.getElementsByName(name).checked; }


/**
 * Return XML HTTP request
 */
function getxhr() {
	var xhr = null;
	if (window.XMLHttpRequest || window.ActiveXObject) {
		if (window.ActiveXObject) {
			try { xhr = new ActiveXObject("Msxml2.XMLHTTP"); } 
			catch(e) { xhr = new ActiveXObject("Microsoft.XMLHTTP"); }
		} else { xhr = new XMLHttpRequest(); }
	} else { alert("XMLHTTPRequest not supported..."); return null; }
	return xhr;
}

/**
 * XML HTTP request sender
 * @param {string} data xml format
 * @param {DivElement} el_warn
 * @param {Array} reset_input
 * @param {Array} reset_div
 * @param {DivElement} el_div_dest
 * @param {DivElement} loader
 */
var ws_url = "./ws/ws.php"; // singleton
var xhr = null; //singleton
function callws(data, callback, el_warn, input_clr, div_clr, el_div_dest, el_loader, new_page){
	if (xhr && xhr.readyState != 0) {
		xhr.abort(); // cancel request
	}
	xhr = getxhr();
	xhr.onreadystatechange = function(){
		if(xhr.readyState == 4 && xhr.status == 200){
			callback(xhr.responseXML, el_warn, input_clr, div_clr, el_div_dest, el_loader, new_page);
		}
	}
	xhr.open("POST", ws_url,true);
	xhr.setRequestHeader("Content-Type", "text/xml");
	var xml = '<?xml version="1.0" encoding="utf-8"?>' ;
	xml += data;
	xhr.send(xml);
}

function callws_file(data, callback){
	if (xhr && xhr.readyState != 0) {
		xhr.abort(); // cancel request
	}
	xhr = getxhr();
	xhr.onreadystatechange = function(){
		if(xhr.readyState == 4 && xhr.status == 200){
			callback(xhr.responseText);
		}
	}
	xhr.open("POST", ws_url,true);
	xhr.setRequestHeader("Content-Type", "text/xml");
	var xml = '<?xml version="1.0" encoding="utf-8"?>' ;
	xml += data;
	xhr.send(xml);
}


function readfile_cb(content){
    var a         = document.createElement('a');
    a.href        = 'data:attachment/csv,' +  encodeURIComponent(content);
    a.target      = '_blank';
    a.download    = 'globalvariables.csv';

    document.body.appendChild(a);
    a.click();
}

/**
 * call back function for response
 * @param {Object} data
 * @param {Element} el_warn
 * @param {Array} input_clr 
 * @param {Array} div_clr
 * @param {Element} el_div_dest
 * @param {Element} el_loader
 */
function readresponse_cb(data, el_warn, input_clr, div_clr, el_div_dest, el_loader, new_page) {
	var tagCode = data.getElementsByTagName("code");
	if(!tagCode || tagCode.length == 0)
		return;
	//
	var tagMsg = data.getElementsByTagName("msg");
	if(!tagMsg || tagMsg.length == 0)
		return;
	var rsp_value = tagCode.item(0).firstChild;
	if ( rsp_value == null) {  rsp_value = ""; } else  { rsp_value = rsp_value.nodeValue; }
	var msg_value = tagMsg.item(0).firstChild;
	if ( msg_value == null) {  msg_value = ""; } else  { msg_value = msg_value.nodeValue; }
	//
	hideloader(el_loader);
	// response ok
	if (rsp_value == 200)
	{
		for(i=0;i<input_clr.length;i++) { getel(input_clr[i]).value = ""; }
		for(i=0;i<div_clr.length;i++) { getel(div_clr[i]).innerHTML = ""; }
		if(el_div_dest != null) { 
            el_div_dest.innerHTML = unescape(msg_value);
        } else if (new_page != null) {
            myWindow = window.open("about:blank", "_blank", "scrollbars=yes, width=800,height=800");
            myWindow.document.write(unescape(msg_value));  
        } else { alert(html_entity_decode(msg_value)); }
	}
	// bad request
	else if (rsp_value == 400)
	{
		showwarning(el_warn, msg_value);
	}
	// request refused
	else if (rsp_value == 403)
	{
		hidewarning(el_warn);
		alert(html_entity_decode(msg_value));	
	}
	// not found
	else if (rsp_value == 404)
	{
		hidewarning(el_warn);
		alert(html_entity_decode(msg_value));	
	}
	// server problem
	else if (rsp_value == 500)
	{
		hidewarning(el_warn);
		alert(html_entity_decode(msg_value));
	}
	// request not authorized
	else if (rsp_value == 603)
	{
		showwarning(el_warn, msg_value);
	}
	// unknown error
	else {
		hidewarning(el_warn);
		alert(html_entity_decode(msg_value));
	}

	// redirect to ...
	var tagMoveTo = data.getElementsByTagName("moveto")
	if (tagMoveTo)
	{
		if(tagMoveTo.length == 0)
			return;
		var moveto_value = tagMoveTo.item(0).firstChild;
		if ( moveto_value == null) {  moveto_value = ""; } else  { moveto_value = moveto_value.nodeValue; }
		if(moveto_value != undefined) {document.location.href=moveto_value;}
	}
}

/**
 * Template XMl for request
 * @param {string} cmd
 * @param {string} args
 */
function request(cmd, args) {
	var req = "<req><cmd>" + escape(cmd) + "</cmd><args>" + args + "</args></req>";
	return req;
}

/**
 * Template XMl for args
 * @param {string} key
 * @param {string} value
 */
function arg(key, value){
	var arg = "<" + key + ">" + escape(value) + "</" + key + ">";
	var arg = "<" + key + ">" + value + "</" + key + ">";
	return arg
}

function arg_no_escaped(key, value){
	var arg = "<" + key + ">" + value + "</" + key + ">";
	return arg
}

/**
 * Hide div warning
 * @param {Div Element} warning
 */
function hidewarning(warning) { if(warning != null){warning.style.display = "none";} }

/**
 * Show div warning
 * @param {Div Element} warning
 */
function showwarning(warning, msg) { if(warning != null){warning.style.display = "block"; warning.innerHTML = msg;} }

/**
 * Hide loader
 * @param {Div Element} warning
 */
function hideloader(loader) { if(loader != null){loader.style.visibility = "hidden";} }

/**
 * Show loader
 * @param {Div Element} warning
 */
function showloader(loader) { if(loader != null){loader.style.visibility = "visible";} }


/**
 * Show or Hide tab menu
 * @param {Div Element} warning
 */
function showsubtabmenu(dv, max) {
	for(i=0;i<max;i++) { 
		getel( "stmb" + i).style.display = "none";
		getel("stm" + i).className= "subtabmenu_unselected";
	}
	getel("stmb" + dv).style.display = "block";
	getel("stm" + dv).className= "subtabmenu_selected";
}

/**
 * HTML entity decoder for javascrip alert
 * @param {string} txt
 */
function html_entity_decode(txt) {
	var y=document.createElement('span');
	y.innerHTML=txt;
	return y.innerHTML;
}