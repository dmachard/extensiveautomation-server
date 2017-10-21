# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import base64
import hashlib
import pkgutil
import os
import zipfile

from .command import Command
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.utils import keys_to_typing

# Python 3 imports
try:
    str = basestring
except NameError:
    pass

try:
    from StringIO import StringIO as IOStream
except ImportError:  # 3+
    from io import BytesIO as IOStream

# getAttribute_js = pkgutil.get_data(__package__, 'getAttribute.js').decode('utf8')
# isDisplayed_js = pkgutil.get_data(__package__, 'isDisplayed.js').decode('utf8')

getAttribute_js = """function(){return function(){var aa="function"==typeof Object.defineProperties?Object.defineProperty:function(a,c,b){if(b.get||b.set)throw new TypeError("ES3 does not support getters and setters.");a!=Array.prototype&&a!=Object.prototype&&(a[c]=b.value)},ba="undefined"!=typeof window&&window===this?this:"undefined"!=typeof global?global:this;
function e(a,c){if(c){for(var b=ba,d=a.split("."),f=0;f<d.length-1;f++){var h=d[f];h in b||(b[h]={});b=b[h]}d=d[d.length-1];f=b[d];h=c(f);h!=f&&null!=h&&aa(b,d,{configurable:!0,writable:!0,value:h})}}
e("String.prototype.repeat",function(a){return a?a:function(a){var b;if(null==this)throw new TypeError("The 'this' value for String.prototype.repeat must not be null or undefined");b=this+"";if(0>a||1342177279<a)throw new RangeError("Invalid count value");a|=0;for(var d="";a;)if(a&1&&(d+=b),a>>>=1)b+=b;return d}});e("Math.sign",function(a){return a?a:function(a){a=Number(a);return!a||isNaN(a)?a:0<a?1:-1}});var g=this;function l(a){return"string"==typeof a};function m(a,c){this.a=n[a]||p;this.message=c||"";var b=this.a.replace(/((?:^|\s+)[a-z])/g,function(a){return a.toUpperCase().replace(/^[\s\xa0]+/g,"")}),d=b.length-5;if(0>d||b.indexOf("Error",d)!=d)b+="Error";this.name=b;b=Error(this.message);b.name=this.name;this.stack=b.stack||""}
(function(){var a=Error;function c(){}c.prototype=a.prototype;m.b=a.prototype;m.prototype=new c;m.prototype.constructor=m;m.a=function(b,c,f){for(var h=Array(arguments.length-2),k=2;k<arguments.length;k++)h[k-2]=arguments[k];return a.prototype[c].apply(b,h)}})();var p="unknown error",n={15:"element not selectable",11:"element not visible"};n[31]=p;n[30]=p;n[24]="invalid cookie domain";n[29]="invalid element coordinates";n[12]="invalid element state";n[32]="invalid selector";n[51]="invalid selector";
n[52]="invalid selector";n[17]="javascript error";n[405]="unsupported operation";n[34]="move target out of bounds";n[27]="no such alert";n[7]="no such element";n[8]="no such frame";n[23]="no such window";n[28]="script timeout";n[33]="session not created";n[10]="stale element reference";n[21]="timeout";n[25]="unable to set cookie";n[26]="unexpected alert open";n[13]=p;n[9]="unknown command";m.prototype.toString=function(){return this.name+": "+this.message};var q=String.prototype.trim?function(a){return a.trim()}:function(a){return a.replace(/^[\s\xa0]+|[\s\xa0]+$/g,"")};
function r(a,c){for(var b=0,d=q(String(a)).split("."),f=q(String(c)).split("."),h=Math.max(d.length,f.length),k=0;!b&&k<h;k++){var S=d[k]||"",ja=f[k]||"",ka=RegExp("(\\d*)(\\D*)","g"),la=RegExp("(\\d*)(\\D*)","g");do{var t=ka.exec(S)||["","",""],u=la.exec(ja)||["","",""];if(0==t[0].length&&0==u[0].length)break;b=v(0==t[1].length?0:parseInt(t[1],10),0==u[1].length?0:parseInt(u[1],10))||v(0==t[2].length,0==u[2].length)||v(t[2],u[2])}while(!b)}return b}function v(a,c){return a<c?-1:a>c?1:0};var w;a:{var x=g.navigator;if(x){var y=x.userAgent;if(y){w=y;break a}}w=""}function z(a){return-1!=w.indexOf(a)};function ca(a,c){for(var b=a.length,d=l(a)?a.split(""):a,f=0;f<b;f++)f in d&&c.call(void 0,d[f],f,a)};function A(){return z("iPhone")&&!z("iPod")&&!z("iPad")};function B(){return z("Opera")||z("OPR")}function C(){return(z("Chrome")||z("CriOS"))&&!B()&&!z("Edge")};var D=B(),E=z("Trident")||z("MSIE"),F=z("Edge"),G=z("Gecko")&&!(-1!=w.toLowerCase().indexOf("webkit")&&!z("Edge"))&&!(z("Trident")||z("MSIE"))&&!z("Edge"),da=-1!=w.toLowerCase().indexOf("webkit")&&!z("Edge");function ea(){var a=w;if(G)return/rv\:([^\);]+)(\)|;)/.exec(a);if(F)return/Edge\/([\d\.]+)/.exec(a);if(E)return/\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/.exec(a);if(da)return/WebKit\/(\S+)/.exec(a)}function H(){var a=g.document;return a?a.documentMode:void 0}
var I=function(){if(D&&g.opera){var a;var c=g.opera.version;try{a=c()}catch(b){a=c}return a}a="";(c=ea())&&(a=c?c[1]:"");return E&&(c=H(),null!=c&&c>parseFloat(a))?String(c):a}(),J={},K=g.document,L=K&&E?H()||("CSS1Compat"==K.compatMode?parseInt(I,10):5):void 0;!G&&!E||E&&9<=Number(L)||G&&(J["1.9.1"]||(J["1.9.1"]=0<=r(I,"1.9.1")));E&&(J["9"]||(J["9"]=0<=r(I,"9")));var fa=z("Firefox"),ga=A()||z("iPod"),ha=z("iPad"),M=z("Android")&&!(C()||z("Firefox")||B()||z("Silk")),ia=C(),N=z("Safari")&&!(C()||z("Coast")||B()||z("Edge")||z("Silk")||z("Android"))&&!(A()||z("iPad")||z("iPod"));var ma={SCRIPT:1,STYLE:1,HEAD:1,IFRAME:1,OBJECT:1},na={IMG:" ",BR:"\n"};function oa(a,c,b){if(!(a.nodeName in ma))if(3==a.nodeType)b?c.push(String(a.nodeValue).replace(/(\r\n|\r|\n)/g,"")):c.push(a.nodeValue);else if(a.nodeName in na)c.push(na[a.nodeName]);else for(a=a.firstChild;a;)oa(a,c,b),a=a.nextSibling};function O(a){return(a=a.exec(w))?a[1]:""}var pa=function(){if(fa)return O(/Firefox\/([0-9.]+)/);if(E||F||D)return I;if(ia)return O(/Chrome\/([0-9.]+)/);if(N&&!(A()||z("iPad")||z("iPod")))return O(/Version\/([0-9.]+)/);if(ga||ha){var a=/Version\/(\S+).*Mobile\/(\S+)/.exec(w);if(a)return a[1]+"."+a[2]}else if(M)return(a=O(/Android\s+([0-9.]+)/))?a:O(/Version\/([0-9.]+)/);return""}();var qa;function P(a){ra?qa(a):M?r(sa,a):r(pa,a)}var ra=function(){if(!G)return!1;var a=g.Components;if(!a)return!1;try{if(!a.classes)return!1}catch(f){return!1}var c=a.classes,a=a.interfaces,b=c["@mozilla.org/xpcom/version-comparator;1"].getService(a.nsIVersionComparator),d=c["@mozilla.org/xre/app-info;1"].getService(a.nsIXULAppInfo).version;qa=function(a){b.compare(d,""+a)};return!0}(),Q;if(M){var ta=/Android\s+([0-9\.]+)/.exec(w);Q=ta?ta[1]:"0"}else Q="0";
var sa=Q,ua=E&&!(8<=Number(L)),va=E&&!(9<=Number(L));M&&P(2.3);M&&P(4);N&&P(6);function R(a,c){c=c.toLowerCase();if("style"==c)return wa(a.style.cssText);if(ua&&"value"==c&&T(a,"INPUT"))return a.value;if(va&&!0===a[c])return String(a.getAttribute(c));var b=a.getAttributeNode(c);return b&&b.specified?b.value:null}var xa=/[;]+(?=(?:(?:[^"]*"){2})*[^"]*$)(?=(?:(?:[^']*'){2})*[^']*$)(?=(?:[^()]*\([^()]*\))*[^()]*$)/;
function wa(a){var c=[];ca(a.split(xa),function(a){var d=a.indexOf(":");0<d&&(a=[a.slice(0,d),a.slice(d+1)],2==a.length&&c.push(a[0].toLowerCase(),":",a[1],";"))});c=c.join("");return c=";"==c.charAt(c.length-1)?c:c+";"}function U(a,c){var b;ua&&"value"==c&&T(a,"OPTION")&&null===R(a,"value")?(b=[],oa(a,b,!1),b=b.join("")):b=a[c];return b}function T(a,c){return!!a&&1==a.nodeType&&(!c||a.tagName.toUpperCase()==c)}
function ya(a){return T(a,"OPTION")?!0:T(a,"INPUT")?(a=a.type.toLowerCase(),"checkbox"==a||"radio"==a):!1};var za={"class":"className",readonly:"readOnly"},V="async autofocus autoplay checked compact complete controls declare defaultchecked defaultselected defer disabled draggable ended formnovalidate hidden indeterminate iscontenteditable ismap itemscope loop multiple muted nohref noresize noshade novalidate nowrap open paused pubdate readonly required reversed scoped seamless seeking selected spellcheck truespeed willvalidate".split(" ");function Aa(a,c){var b=null,d=c.toLowerCase();if("style"==d)return(b=a.style)&&!l(b)&&(b=b.cssText),b;if(("selected"==d||"checked"==d)&&ya(a)){if(!ya(a))throw new m(15,"Element is not selectable");var b="selected",f=a.type&&a.type.toLowerCase();if("checkbox"==f||"radio"==f)b="checked";return U(a,b)?"true":null}var h=T(a,"A");if(T(a,"IMG")&&"src"==d||h&&"href"==d)return(b=R(a,d))&&(b=U(a,d)),b;if("spellcheck"==d){b=R(a,d);if(null!==b){if("false"==b.toLowerCase())return"false";if("true"==b.toLowerCase())return"true"}return U(a,
d)+""}h=za[c]||c;a:if(l(V))d=l(d)&&1==d.length?V.indexOf(d,0):-1;else{for(var k=0;k<V.length;k++)if(k in V&&V[k]===d){d=k;break a}d=-1}if(0<=d)return(b=null!==R(a,c)||U(a,h))?"true":null;try{f=U(a,h)}catch(S){}(d=null==f)||(d=typeof f,d="object"==d&&null!=f||"function"==d);d?b=R(a,c):b=f;return null!=b?b.toString():null}var W=["_"],X=g;W[0]in X||!X.execScript||X.execScript("var "+W[0]);for(var Y;W.length&&(Y=W.shift());){var Z;if(Z=!W.length)Z=void 0!==Aa;Z?X[Y]=Aa:X[Y]?X=X[Y]:X=X[Y]={}};; return this._.apply(null,arguments);}.apply({navigator:typeof window!='undefined'?window.navigator:null,document:typeof window!='undefined'?window.document:null}, arguments);}
"""

isDisplayed_js = """function(){return function(){var aa="function"==typeof Object.defineProperties?Object.defineProperty:function(a,b,c){if(c.get||c.set)throw new TypeError("ES3 does not support getters and setters.");a!=Array.prototype&&a!=Object.prototype&&(a[b]=c.value)},ba="undefined"!=typeof window&&window===this?this:"undefined"!=typeof global?global:this;
function ca(a,b){if(b){for(var c=ba,d=a.split("."),e=0;e<d.length-1;e++){var f=d[e];f in c||(c[f]={});c=c[f]}d=d[d.length-1];e=c[d];f=b(e);f!=e&&null!=f&&aa(c,d,{configurable:!0,writable:!0,value:f})}}
ca("String.prototype.repeat",function(a){return a?a:function(a){var c;if(null==this)throw new TypeError("The 'this' value for String.prototype.repeat must not be null or undefined");c=this+"";if(0>a||1342177279<a)throw new RangeError("Invalid count value");a|=0;for(var d="";a;)if(a&1&&(d+=c),a>>>=1)c+=c;return d}});ca("Math.sign",function(a){return a?a:function(a){a=Number(a);return!a||isNaN(a)?a:0<a?1:-1}});var k=this;function l(a){return void 0!==a}
function da(a,b){var c=a.split("."),d=k;c[0]in d||!d.execScript||d.execScript("var "+c[0]);for(var e;c.length&&(e=c.shift());)!c.length&&l(b)?d[e]=b:d[e]?d=d[e]:d=d[e]={}}
function ea(a){var b=typeof a;if("object"==b)if(a){if(a instanceof Array)return"array";if(a instanceof Object)return b;var c=Object.prototype.toString.call(a);if("[object Window]"==c)return"object";if("[object Array]"==c||"number"==typeof a.length&&"undefined"!=typeof a.splice&&"undefined"!=typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("splice"))return"array";if("[object Function]"==c||"undefined"!=typeof a.call&&"undefined"!=typeof a.propertyIsEnumerable&&!a.propertyIsEnumerable("call"))return"function"}else return"null";
else if("function"==b&&"undefined"==typeof a.call)return"object";return b}function n(a){return"string"==typeof a}function fa(a,b,c){return a.call.apply(a.bind,arguments)}function ga(a,b,c){if(!a)throw Error();if(2<arguments.length){var d=Array.prototype.slice.call(arguments,2);return function(){var c=Array.prototype.slice.call(arguments);Array.prototype.unshift.apply(c,d);return a.apply(b,c)}}return function(){return a.apply(b,arguments)}}
function ha(a,b,c){ha=Function.prototype.bind&&-1!=Function.prototype.bind.toString().indexOf("native code")?fa:ga;return ha.apply(null,arguments)}function ia(a,b){var c=Array.prototype.slice.call(arguments,1);return function(){var b=c.slice();b.push.apply(b,arguments);return a.apply(this,b)}}
function q(a,b){function c(){}c.prototype=b.prototype;a.H=b.prototype;a.prototype=new c;a.prototype.constructor=a;a.G=function(a,c,f){for(var g=Array(arguments.length-2),h=2;h<arguments.length;h++)g[h-2]=arguments[h];return b.prototype[c].apply(a,g)}};function ja(a,b){this.a=r[a]||ka;this.message=b||"";var c=this.a.replace(/((?:^|\s+)[a-z])/g,function(a){return a.toUpperCase().replace(/^[\s\xa0]+/g,"")}),d=c.length-5;if(0>d||c.indexOf("Error",d)!=d)c+="Error";this.name=c;c=Error(this.message);c.name=this.name;this.stack=c.stack||""}q(ja,Error);var ka="unknown error",r={15:"element not selectable",11:"element not visible"};r[31]=ka;r[30]=ka;r[24]="invalid cookie domain";r[29]="invalid element coordinates";r[12]="invalid element state";r[32]="invalid selector";
r[51]="invalid selector";r[52]="invalid selector";r[17]="javascript error";r[405]="unsupported operation";r[34]="move target out of bounds";r[27]="no such alert";r[7]="no such element";r[8]="no such frame";r[23]="no such window";r[28]="script timeout";r[33]="session not created";r[10]="stale element reference";r[21]="timeout";r[25]="unable to set cookie";r[26]="unexpected alert open";r[13]=ka;r[9]="unknown command";ja.prototype.toString=function(){return this.name+": "+this.message};var la={aliceblue:"#f0f8ff",antiquewhite:"#faebd7",aqua:"#00ffff",aquamarine:"#7fffd4",azure:"#f0ffff",beige:"#f5f5dc",bisque:"#ffe4c4",black:"#000000",blanchedalmond:"#ffebcd",blue:"#0000ff",blueviolet:"#8a2be2",brown:"#a52a2a",burlywood:"#deb887",cadetblue:"#5f9ea0",chartreuse:"#7fff00",chocolate:"#d2691e",coral:"#ff7f50",cornflowerblue:"#6495ed",cornsilk:"#fff8dc",crimson:"#dc143c",cyan:"#00ffff",darkblue:"#00008b",darkcyan:"#008b8b",darkgoldenrod:"#b8860b",darkgray:"#a9a9a9",darkgreen:"#006400",
darkgrey:"#a9a9a9",darkkhaki:"#bdb76b",darkmagenta:"#8b008b",darkolivegreen:"#556b2f",darkorange:"#ff8c00",darkorchid:"#9932cc",darkred:"#8b0000",darksalmon:"#e9967a",darkseagreen:"#8fbc8f",darkslateblue:"#483d8b",darkslategray:"#2f4f4f",darkslategrey:"#2f4f4f",darkturquoise:"#00ced1",darkviolet:"#9400d3",deeppink:"#ff1493",deepskyblue:"#00bfff",dimgray:"#696969",dimgrey:"#696969",dodgerblue:"#1e90ff",firebrick:"#b22222",floralwhite:"#fffaf0",forestgreen:"#228b22",fuchsia:"#ff00ff",gainsboro:"#dcdcdc",
ghostwhite:"#f8f8ff",gold:"#ffd700",goldenrod:"#daa520",gray:"#808080",green:"#008000",greenyellow:"#adff2f",grey:"#808080",honeydew:"#f0fff0",hotpink:"#ff69b4",indianred:"#cd5c5c",indigo:"#4b0082",ivory:"#fffff0",khaki:"#f0e68c",lavender:"#e6e6fa",lavenderblush:"#fff0f5",lawngreen:"#7cfc00",lemonchiffon:"#fffacd",lightblue:"#add8e6",lightcoral:"#f08080",lightcyan:"#e0ffff",lightgoldenrodyellow:"#fafad2",lightgray:"#d3d3d3",lightgreen:"#90ee90",lightgrey:"#d3d3d3",lightpink:"#ffb6c1",lightsalmon:"#ffa07a",
lightseagreen:"#20b2aa",lightskyblue:"#87cefa",lightslategray:"#778899",lightslategrey:"#778899",lightsteelblue:"#b0c4de",lightyellow:"#ffffe0",lime:"#00ff00",limegreen:"#32cd32",linen:"#faf0e6",magenta:"#ff00ff",maroon:"#800000",mediumaquamarine:"#66cdaa",mediumblue:"#0000cd",mediumorchid:"#ba55d3",mediumpurple:"#9370db",mediumseagreen:"#3cb371",mediumslateblue:"#7b68ee",mediumspringgreen:"#00fa9a",mediumturquoise:"#48d1cc",mediumvioletred:"#c71585",midnightblue:"#191970",mintcream:"#f5fffa",mistyrose:"#ffe4e1",
moccasin:"#ffe4b5",navajowhite:"#ffdead",navy:"#000080",oldlace:"#fdf5e6",olive:"#808000",olivedrab:"#6b8e23",orange:"#ffa500",orangered:"#ff4500",orchid:"#da70d6",palegoldenrod:"#eee8aa",palegreen:"#98fb98",paleturquoise:"#afeeee",palevioletred:"#db7093",papayawhip:"#ffefd5",peachpuff:"#ffdab9",peru:"#cd853f",pink:"#ffc0cb",plum:"#dda0dd",powderblue:"#b0e0e6",purple:"#800080",red:"#ff0000",rosybrown:"#bc8f8f",royalblue:"#4169e1",saddlebrown:"#8b4513",salmon:"#fa8072",sandybrown:"#f4a460",seagreen:"#2e8b57",
seashell:"#fff5ee",sienna:"#a0522d",silver:"#c0c0c0",skyblue:"#87ceeb",slateblue:"#6a5acd",slategray:"#708090",slategrey:"#708090",snow:"#fffafa",springgreen:"#00ff7f",steelblue:"#4682b4",tan:"#d2b48c",teal:"#008080",thistle:"#d8bfd8",tomato:"#ff6347",turquoise:"#40e0d0",violet:"#ee82ee",wheat:"#f5deb3",white:"#ffffff",whitesmoke:"#f5f5f5",yellow:"#ffff00",yellowgreen:"#9acd32"};function ma(a,b){this.width=a;this.height=b}ma.prototype.clone=function(){return new ma(this.width,this.height)};ma.prototype.toString=function(){return"("+this.width+" x "+this.height+")"};ma.prototype.ceil=function(){this.width=Math.ceil(this.width);this.height=Math.ceil(this.height);return this};ma.prototype.floor=function(){this.width=Math.floor(this.width);this.height=Math.floor(this.height);return this};
ma.prototype.round=function(){this.width=Math.round(this.width);this.height=Math.round(this.height);return this};var na=String.prototype.trim?function(a){return a.trim()}:function(a){return a.replace(/^[\s\xa0]+|[\s\xa0]+$/g,"")};
function oa(a,b){for(var c=0,d=na(String(a)).split("."),e=na(String(b)).split("."),f=Math.max(d.length,e.length),g=0;!c&&g<f;g++){var h=d[g]||"",p=e[g]||"",w=RegExp("(\\d*)(\\D*)","g"),m=RegExp("(\\d*)(\\D*)","g");do{var u=w.exec(h)||["","",""],y=m.exec(p)||["","",""];if(0==u[0].length&&0==y[0].length)break;c=pa(0==u[1].length?0:parseInt(u[1],10),0==y[1].length?0:parseInt(y[1],10))||pa(0==u[2].length,0==y[2].length)||pa(u[2],y[2])}while(!c)}return c}function pa(a,b){return a<b?-1:a>b?1:0}
function qa(a){return String(a).replace(/\-([a-z])/g,function(a,c){return c.toUpperCase()})};/*

 The MIT License

 Copyright (c) 2007 Cybozu Labs, Inc.
 Copyright (c) 2012 Google Inc.

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to
 deal in the Software without restriction, including without limitation the
 rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 sell copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 IN THE SOFTWARE.
*/
function ra(a,b,c){this.a=a;this.b=b||1;this.f=c||1};function sa(a){this.b=a;this.a=0}function ta(a){a=a.match(ua);for(var b=0;b<a.length;b++)va.test(a[b])&&a.splice(b,1);return new sa(a)}var ua=RegExp("\\$?(?:(?![0-9-\\.])(?:\\*|[\\w-\\.]+):)?(?![0-9-\\.])(?:\\*|[\\w-\\.]+)|\\/\\/|\\.\\.|::|\\d+(?:\\.\\d*)?|\\.\\d+|\"[^\"]*\"|'[^']*'|[!<>]=|\\s+|.","g"),va=/^\s/;function t(a,b){return a.b[a.a+(b||0)]}function v(a){return a.b[a.a++]}function wa(a){return a.b.length<=a.a};var x;a:{var xa=k.navigator;if(xa){var ya=xa.userAgent;if(ya){x=ya;break a}}x=""}function z(a){return-1!=x.indexOf(a)};function A(a,b){this.h=a;this.c=l(b)?b:null;this.b=null;switch(a){case "comment":this.b=8;break;case "text":this.b=3;break;case "processing-instruction":this.b=7;break;case "node":break;default:throw Error("Unexpected argument");}}function za(a){return"comment"==a||"text"==a||"processing-instruction"==a||"node"==a}A.prototype.a=function(a){return null===this.b||this.b==a.nodeType};A.prototype.f=function(){return this.h};
A.prototype.toString=function(){var a="Kind Test: "+this.h;!this.c||(a+=B(this.c));return a};function Aa(a,b){this.j=a.toLowerCase();var c;c="*"==this.j?"*":"http://www.w3.org/1999/xhtml";this.c=b?b.toLowerCase():c}Aa.prototype.a=function(a){var b=a.nodeType;if(1!=b&&2!=b)return!1;b=l(a.localName)?a.localName:a.nodeName;return"*"!=this.j&&this.j!=b.toLowerCase()?!1:"*"==this.c?!0:this.c==(a.namespaceURI?a.namespaceURI.toLowerCase():"http://www.w3.org/1999/xhtml")};Aa.prototype.f=function(){return this.j};
Aa.prototype.toString=function(){return"Name Test: "+("http://www.w3.org/1999/xhtml"==this.c?"":this.c+":")+this.j};function Ba(a){switch(a.nodeType){case 1:return ia(Ca,a);case 9:return Ba(a.documentElement);case 11:case 10:case 6:case 12:return Da;default:return a.parentNode?Ba(a.parentNode):Da}}function Da(){return null}function Ca(a,b){if(a.prefix==b)return a.namespaceURI||"http://www.w3.org/1999/xhtml";var c=a.getAttributeNode("xmlns:"+b);return c&&c.specified?c.value||null:a.parentNode&&9!=a.parentNode.nodeType?Ca(a.parentNode,b):null};function Ea(a,b){if(n(a))return n(b)&&1==b.length?a.indexOf(b,0):-1;for(var c=0;c<a.length;c++)if(c in a&&a[c]===b)return c;return-1}function C(a,b){for(var c=a.length,d=n(a)?a.split(""):a,e=0;e<c;e++)e in d&&b.call(void 0,d[e],e,a)}function Fa(a,b){for(var c=a.length,d=[],e=0,f=n(a)?a.split(""):a,g=0;g<c;g++)if(g in f){var h=f[g];b.call(void 0,h,g,a)&&(d[e++]=h)}return d}function Ga(a,b,c){var d=c;C(a,function(c,f){d=b.call(void 0,d,c,f,a)});return d}
function Ha(a,b){for(var c=a.length,d=n(a)?a.split(""):a,e=0;e<c;e++)if(e in d&&b.call(void 0,d[e],e,a))return!0;return!1}function Ia(a,b){for(var c=a.length,d=n(a)?a.split(""):a,e=0;e<c;e++)if(e in d&&!b.call(void 0,d[e],e,a))return!1;return!0}function Ja(a,b){var c;a:{c=a.length;for(var d=n(a)?a.split(""):a,e=0;e<c;e++)if(e in d&&b.call(void 0,d[e],e,a)){c=e;break a}c=-1}return 0>c?null:n(a)?a.charAt(c):a[c]}function Ka(a){return Array.prototype.concat.apply(Array.prototype,arguments)}
function La(a,b,c){return 2>=arguments.length?Array.prototype.slice.call(a,b):Array.prototype.slice.call(a,b,c)};function Ma(){return z("iPhone")&&!z("iPod")&&!z("iPad")};var Na="backgroundColor borderTopColor borderRightColor borderBottomColor borderLeftColor color outlineColor".split(" "),Oa=/#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])/,Pa=/^#(?:[0-9a-f]{3}){1,2}$/i,Qa=/^(?:rgba)?\((\d{1,3}),\s?(\d{1,3}),\s?(\d{1,3}),\s?(0|1|0\.\d*)\)$/i,Ra=/^(?:rgb)?\((0|[1-9]\d{0,2}),\s?(0|[1-9]\d{0,2}),\s?(0|[1-9]\d{0,2})\)$/i;function Sa(){return z("Opera")||z("OPR")}function Ta(){return(z("Chrome")||z("CriOS"))&&!Sa()&&!z("Edge")};function D(a,b){this.x=l(a)?a:0;this.y=l(b)?b:0}D.prototype.clone=function(){return new D(this.x,this.y)};D.prototype.toString=function(){return"("+this.x+", "+this.y+")"};D.prototype.ceil=function(){this.x=Math.ceil(this.x);this.y=Math.ceil(this.y);return this};D.prototype.floor=function(){this.x=Math.floor(this.x);this.y=Math.floor(this.y);return this};D.prototype.round=function(){this.x=Math.round(this.x);this.y=Math.round(this.y);return this};var Ua=Sa(),E=z("Trident")||z("MSIE"),Va=z("Edge"),Wa=z("Gecko")&&!(-1!=x.toLowerCase().indexOf("webkit")&&!z("Edge"))&&!(z("Trident")||z("MSIE"))&&!z("Edge"),Xa=-1!=x.toLowerCase().indexOf("webkit")&&!z("Edge");function Ya(){var a=x;if(Wa)return/rv\:([^\);]+)(\)|;)/.exec(a);if(Va)return/Edge\/([\d\.]+)/.exec(a);if(E)return/\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/.exec(a);if(Xa)return/WebKit\/(\S+)/.exec(a)}function Za(){var a=k.document;return a?a.documentMode:void 0}
var $a=function(){if(Ua&&k.opera){var a;var b=k.opera.version;try{a=b()}catch(c){a=b}return a}a="";(b=Ya())&&(a=b?b[1]:"");return E&&(b=Za(),null!=b&&b>parseFloat(a))?String(b):a}(),ab={};function bb(a){return ab[a]||(ab[a]=0<=oa($a,a))}var cb=k.document,db=cb&&E?Za()||("CSS1Compat"==cb.compatMode?parseInt($a,10):5):void 0;!Wa&&!E||E&&9<=Number(db)||Wa&&bb("1.9.1");E&&bb("9");function eb(a,b,c,d){this.top=a;this.right=b;this.bottom=c;this.left=d}eb.prototype.clone=function(){return new eb(this.top,this.right,this.bottom,this.left)};eb.prototype.toString=function(){return"("+this.top+"t, "+this.right+"r, "+this.bottom+"b, "+this.left+"l)"};eb.prototype.ceil=function(){this.top=Math.ceil(this.top);this.right=Math.ceil(this.right);this.bottom=Math.ceil(this.bottom);this.left=Math.ceil(this.left);return this};
eb.prototype.floor=function(){this.top=Math.floor(this.top);this.right=Math.floor(this.right);this.bottom=Math.floor(this.bottom);this.left=Math.floor(this.left);return this};eb.prototype.round=function(){this.top=Math.round(this.top);this.right=Math.round(this.right);this.bottom=Math.round(this.bottom);this.left=Math.round(this.left);return this};var fb=z("Firefox"),gb=Ma()||z("iPod"),hb=z("iPad"),ib=z("Android")&&!(Ta()||z("Firefox")||Sa()||z("Silk")),jb=Ta(),kb=z("Safari")&&!(Ta()||z("Coast")||Sa()||z("Edge")||z("Silk")||z("Android"))&&!(Ma()||z("iPad")||z("iPod"));var F=E&&!(9<=Number(db)),lb=E&&!(8<=Number(db));function mb(a,b){if(!a||!b)return!1;if(a.contains&&1==b.nodeType)return a==b||a.contains(b);if("undefined"!=typeof a.compareDocumentPosition)return a==b||!!(a.compareDocumentPosition(b)&16);for(;b&&a!=b;)b=b.parentNode;return b==a}
function nb(a,b){if(a==b)return 0;if(a.compareDocumentPosition)return a.compareDocumentPosition(b)&2?1:-1;if(E&&!(9<=Number(db))){if(9==a.nodeType)return-1;if(9==b.nodeType)return 1}if("sourceIndex"in a||a.parentNode&&"sourceIndex"in a.parentNode){var c=1==a.nodeType,d=1==b.nodeType;if(c&&d)return a.sourceIndex-b.sourceIndex;var e=a.parentNode,f=b.parentNode;return e==f?ob(a,b):!c&&mb(e,b)?-1*pb(a,b):!d&&mb(f,a)?pb(b,a):(c?a.sourceIndex:e.sourceIndex)-(d?b.sourceIndex:f.sourceIndex)}d=G(a);c=d.createRange();
c.selectNode(a);c.collapse(!0);d=d.createRange();d.selectNode(b);d.collapse(!0);return c.compareBoundaryPoints(k.Range.START_TO_END,d)}function pb(a,b){var c=a.parentNode;if(c==b)return-1;for(var d=b;d.parentNode!=c;)d=d.parentNode;return ob(d,a)}function ob(a,b){for(var c=b;c=c.previousSibling;)if(c==a)return-1;return 1}function G(a){return 9==a.nodeType?a:a.ownerDocument||a.document}function qb(a,b){a=a.parentNode;for(var c=0;a;){if(b(a))return a;a=a.parentNode;c++}return null}
function rb(a){this.a=a||k.document||document};function H(a,b,c,d){this.left=a;this.top=b;this.width=c;this.height=d}H.prototype.clone=function(){return new H(this.left,this.top,this.width,this.height)};H.prototype.toString=function(){return"("+this.left+", "+this.top+" - "+this.width+"w x "+this.height+"h)"};H.prototype.ceil=function(){this.left=Math.ceil(this.left);this.top=Math.ceil(this.top);this.width=Math.ceil(this.width);this.height=Math.ceil(this.height);return this};
H.prototype.floor=function(){this.left=Math.floor(this.left);this.top=Math.floor(this.top);this.width=Math.floor(this.width);this.height=Math.floor(this.height);return this};H.prototype.round=function(){this.left=Math.round(this.left);this.top=Math.round(this.top);this.width=Math.round(this.width);this.height=Math.round(this.height);return this};function sb(a){return(a=a.exec(x))?a[1]:""}var tb=function(){if(fb)return sb(/Firefox\/([0-9.]+)/);if(E||Va||Ua)return $a;if(jb)return sb(/Chrome\/([0-9.]+)/);if(kb&&!(Ma()||z("iPad")||z("iPod")))return sb(/Version\/([0-9.]+)/);if(gb||hb){var a=/Version\/(\S+).*Mobile\/(\S+)/.exec(x);if(a)return a[1]+"."+a[2]}else if(ib)return(a=sb(/Android\s+([0-9.]+)/))?a:sb(/Version\/([0-9.]+)/);return""}();function ub(a,b,c,d){this.a=a;this.nodeName=c;this.nodeValue=d;this.nodeType=2;this.parentNode=this.ownerElement=b}function vb(a,b){var c=lb&&"href"==b.nodeName?a.getAttribute(b.nodeName,2):b.nodeValue;return new ub(b,a,b.nodeName,c)};var wb;function xb(a){yb?wb(a):ib?oa(zb,a):oa(tb,a)}var yb=function(){if(!Wa)return!1;var a=k.Components;if(!a)return!1;try{if(!a.classes)return!1}catch(e){return!1}var b=a.classes,a=a.interfaces,c=b["@mozilla.org/xpcom/version-comparator;1"].getService(a.nsIVersionComparator),d=b["@mozilla.org/xre/app-info;1"].getService(a.nsIXULAppInfo).version;wb=function(a){c.compare(d,""+a)};return!0}(),Ab;if(ib){var Bb=/Android\s+([0-9\.]+)/.exec(x);Ab=Bb?Bb[1]:"0"}else Ab="0";var zb=Ab,Cb=E&&!(9<=Number(db));
ib&&xb(2.3);ib&&xb(4);kb&&xb(6);function I(a){var b=null,c=a.nodeType;1==c&&(b=a.textContent,b=void 0==b||null==b?a.innerText:b,b=void 0==b||null==b?"":b);if("string"!=typeof b)if(F&&"title"==a.nodeName.toLowerCase()&&1==c)b=a.text;else if(9==c||1==c){a=9==c?a.documentElement:a.firstChild;for(var c=0,d=[],b="";a;){do 1!=a.nodeType&&(b+=a.nodeValue),F&&"title"==a.nodeName.toLowerCase()&&(b+=a.text),d[c++]=a;while(a=a.firstChild);for(;c&&!(a=d[--c].nextSibling););}}else b=a.nodeValue;return""+b}
function J(a,b,c){if(null===b)return!0;try{if(!a.getAttribute)return!1}catch(d){return!1}lb&&"class"==b&&(b="className");return null==c?!!a.getAttribute(b):a.getAttribute(b,2)==c}function Db(a,b,c,d,e){return(F?Eb:Fb).call(null,a,b,n(c)?c:null,n(d)?d:null,e||new K)}
function Eb(a,b,c,d,e){if(a instanceof Aa||8==a.b||c&&null===a.b){var f=b.all;if(!f)return e;a=Gb(a);if("*"!=a&&(f=b.getElementsByTagName(a),!f))return e;if(c){for(var g=[],h=0;b=f[h++];)J(b,c,d)&&g.push(b);f=g}for(h=0;b=f[h++];)"*"==a&&"!"==b.tagName||L(e,b);return e}Hb(a,b,c,d,e);return e}
function Fb(a,b,c,d,e){b.getElementsByName&&d&&"name"==c&&!E?(b=b.getElementsByName(d),C(b,function(b){a.a(b)&&L(e,b)})):b.getElementsByClassName&&d&&"class"==c?(b=b.getElementsByClassName(d),C(b,function(b){b.className==d&&a.a(b)&&L(e,b)})):a instanceof A?Hb(a,b,c,d,e):b.getElementsByTagName&&(b=b.getElementsByTagName(a.f()),C(b,function(a){J(a,c,d)&&L(e,a)}));return e}
function Ib(a,b,c,d,e){var f;if((a instanceof Aa||8==a.b||c&&null===a.b)&&(f=b.childNodes)){var g=Gb(a);if("*"!=g&&(f=Fa(f,function(a){return a.tagName&&a.tagName.toLowerCase()==g}),!f))return e;c&&(f=Fa(f,function(a){return J(a,c,d)}));C(f,function(a){"*"==g&&("!"==a.tagName||"*"==g&&1!=a.nodeType)||L(e,a)});return e}return Jb(a,b,c,d,e)}function Jb(a,b,c,d,e){for(b=b.firstChild;b;b=b.nextSibling)J(b,c,d)&&a.a(b)&&L(e,b);return e}
function Hb(a,b,c,d,e){for(b=b.firstChild;b;b=b.nextSibling)J(b,c,d)&&a.a(b)&&L(e,b),Hb(a,b,c,d,e)}function Gb(a){if(a instanceof A){if(8==a.b)return"!";if(null===a.b)return"*"}return a.f()};function M(a,b){return!!a&&1==a.nodeType&&(!b||a.tagName.toUpperCase()==b)};function K(){this.b=this.a=null;this.l=0}function Kb(a){this.node=a;this.a=this.b=null}function Lb(a,b){if(!a.a)return b;if(!b.a)return a;for(var c=a.a,d=b.a,e=null,f,g=0;c&&d;){f=c.node;var h=d.node;f==h||f instanceof ub&&h instanceof ub&&f.a==h.a?(f=c,c=c.a,d=d.a):0<nb(c.node,d.node)?(f=d,d=d.a):(f=c,c=c.a);(f.b=e)?e.a=f:a.a=f;e=f;g++}for(f=c||d;f;)f.b=e,e=e.a=f,g++,f=f.a;a.b=e;a.l=g;return a}K.prototype.unshift=function(a){a=new Kb(a);a.a=this.a;this.b?this.a.b=a:this.a=this.b=a;this.a=a;this.l++};
function L(a,b){var c=new Kb(b);c.b=a.b;a.a?a.b.a=c:a.a=a.b=c;a.b=c;a.l++}function Mb(a){return(a=a.a)?a.node:null}function Nb(a){return(a=Mb(a))?I(a):""}function N(a,b){return new Ob(a,!!b)}function Ob(a,b){this.f=a;this.b=(this.c=b)?a.b:a.a;this.a=null}function O(a){var b=a.b;if(b){var c=a.a=b;a.b=a.c?b.b:b.a;return c.node}return null};function P(a){this.i=a;this.b=this.g=!1;this.f=null}function B(a){return"\n  "+a.toString().split("\n").join("\n  ")}function Pb(a,b){a.g=b}function Qb(a,b){a.b=b}function R(a,b){var c=a.a(b);return c instanceof K?+Nb(c):+c}function S(a,b){var c=a.a(b);return c instanceof K?Nb(c):""+c}function Rb(a,b){var c=a.a(b);return c instanceof K?!!c.l:!!c};function Sb(a,b,c){P.call(this,a.i);this.c=a;this.h=b;this.o=c;this.g=b.g||c.g;this.b=b.b||c.b;this.c==Tb&&(c.b||c.g||4==c.i||0==c.i||!b.f?b.b||b.g||4==b.i||0==b.i||!c.f||(this.f={name:c.f.name,s:b}):this.f={name:b.f.name,s:c})}q(Sb,P);
function Ub(a,b,c,d,e){b=b.a(d);c=c.a(d);var f;if(b instanceof K&&c instanceof K){b=N(b);for(d=O(b);d;d=O(b))for(e=N(c),f=O(e);f;f=O(e))if(a(I(d),I(f)))return!0;return!1}if(b instanceof K||c instanceof K){b instanceof K?(e=b,d=c):(e=c,d=b);f=N(e);for(var g=typeof d,h=O(f);h;h=O(f)){switch(g){case "number":h=+I(h);break;case "boolean":h=!!I(h);break;case "string":h=I(h);break;default:throw Error("Illegal primitive type for comparison.");}if(e==b&&a(h,d)||e==c&&a(d,h))return!0}return!1}return e?"boolean"==
typeof b||"boolean"==typeof c?a(!!b,!!c):"number"==typeof b||"number"==typeof c?a(+b,+c):a(b,c):a(+b,+c)}Sb.prototype.a=function(a){return this.c.m(this.h,this.o,a)};Sb.prototype.toString=function(){var a="Binary Expression: "+this.c,a=a+B(this.h);return a+=B(this.o)};function Vb(a,b,c,d){this.a=a;this.A=b;this.i=c;this.m=d}Vb.prototype.toString=function(){return this.a};var Wb={};
function T(a,b,c,d){if(Wb.hasOwnProperty(a))throw Error("Binary operator already created: "+a);a=new Vb(a,b,c,d);return Wb[a.toString()]=a}T("div",6,1,function(a,b,c){return R(a,c)/R(b,c)});T("mod",6,1,function(a,b,c){return R(a,c)%R(b,c)});T("*",6,1,function(a,b,c){return R(a,c)*R(b,c)});T("+",5,1,function(a,b,c){return R(a,c)+R(b,c)});T("-",5,1,function(a,b,c){return R(a,c)-R(b,c)});T("<",4,2,function(a,b,c){return Ub(function(a,b){return a<b},a,b,c)});
T(">",4,2,function(a,b,c){return Ub(function(a,b){return a>b},a,b,c)});T("<=",4,2,function(a,b,c){return Ub(function(a,b){return a<=b},a,b,c)});T(">=",4,2,function(a,b,c){return Ub(function(a,b){return a>=b},a,b,c)});var Tb=T("=",3,2,function(a,b,c){return Ub(function(a,b){return a==b},a,b,c,!0)});T("!=",3,2,function(a,b,c){return Ub(function(a,b){return a!=b},a,b,c,!0)});T("and",2,2,function(a,b,c){return Rb(a,c)&&Rb(b,c)});T("or",1,2,function(a,b,c){return Rb(a,c)||Rb(b,c)});function Xb(a,b){if(b.a.length&&4!=a.i)throw Error("Primary expression must evaluate to nodeset if filter has predicate(s).");P.call(this,a.i);this.c=a;this.h=b;this.g=a.g;this.b=a.b}q(Xb,P);Xb.prototype.a=function(a){a=this.c.a(a);return Yb(this.h,a)};Xb.prototype.toString=function(){var a;a="Filter:"+B(this.c);return a+=B(this.h)};function Zb(a,b){if(b.length<a.B)throw Error("Function "+a.j+" expects at least"+a.B+" arguments, "+b.length+" given");if(null!==a.v&&b.length>a.v)throw Error("Function "+a.j+" expects at most "+a.v+" arguments, "+b.length+" given");a.C&&C(b,function(b,d){if(4!=b.i)throw Error("Argument "+d+" to function "+a.j+" is not of type Nodeset: "+b);});P.call(this,a.i);this.h=a;this.c=b;Pb(this,a.g||Ha(b,function(a){return a.g}));Qb(this,a.F&&!b.length||a.D&&!!b.length||Ha(b,function(a){return a.b}))}
q(Zb,P);Zb.prototype.a=function(a){return this.h.m.apply(null,Ka(a,this.c))};Zb.prototype.toString=function(){var a="Function: "+this.h;if(this.c.length)var b=Ga(this.c,function(a,b){return a+B(b)},"Arguments:"),a=a+B(b);return a};function $b(a,b,c,d,e,f,g,h,p){this.j=a;this.i=b;this.g=c;this.F=d;this.D=e;this.m=f;this.B=g;this.v=l(h)?h:g;this.C=!!p}$b.prototype.toString=function(){return this.j};var ac={};
function U(a,b,c,d,e,f,g,h){if(ac.hasOwnProperty(a))throw Error("Function already created: "+a+".");ac[a]=new $b(a,b,c,d,!1,e,f,g,h)}U("boolean",2,!1,!1,function(a,b){return Rb(b,a)},1);U("ceiling",1,!1,!1,function(a,b){return Math.ceil(R(b,a))},1);U("concat",3,!1,!1,function(a,b){return Ga(La(arguments,1),function(b,d){return b+S(d,a)},"")},2,null);U("contains",2,!1,!1,function(a,b,c){b=S(b,a);a=S(c,a);return-1!=b.indexOf(a)},2);U("count",1,!1,!1,function(a,b){return b.a(a).l},1,1,!0);
U("false",2,!1,!1,function(){return!1},0);U("floor",1,!1,!1,function(a,b){return Math.floor(R(b,a))},1);U("id",4,!1,!1,function(a,b){function c(a){if(F){var b=e.all[a];if(b){if(b.nodeType&&a==b.id)return b;if(b.length)return Ja(b,function(b){return a==b.id})}return null}return e.getElementById(a)}var d=a.a,e=9==d.nodeType?d:d.ownerDocument,d=S(b,a).split(/\s+/),f=[];C(d,function(a){a=c(a);!a||0<=Ea(f,a)||f.push(a)});f.sort(nb);var g=new K;C(f,function(a){L(g,a)});return g},1);
U("lang",2,!1,!1,function(){return!1},1);U("last",1,!0,!1,function(a){if(1!=arguments.length)throw Error("Function last expects ()");return a.f},0);U("local-name",3,!1,!0,function(a,b){var c=b?Mb(b.a(a)):a.a;return c?c.localName||c.nodeName.toLowerCase():""},0,1,!0);U("name",3,!1,!0,function(a,b){var c=b?Mb(b.a(a)):a.a;return c?c.nodeName.toLowerCase():""},0,1,!0);U("namespace-uri",3,!0,!1,function(){return""},0,1,!0);
U("normalize-space",3,!1,!0,function(a,b){return(b?S(b,a):I(a.a)).replace(/[\s\xa0]+/g," ").replace(/^\s+|\s+$/g,"")},0,1);U("not",2,!1,!1,function(a,b){return!Rb(b,a)},1);U("number",1,!1,!0,function(a,b){return b?R(b,a):+I(a.a)},0,1);U("position",1,!0,!1,function(a){return a.b},0);U("round",1,!1,!1,function(a,b){return Math.round(R(b,a))},1);U("starts-with",2,!1,!1,function(a,b,c){b=S(b,a);a=S(c,a);return!b.lastIndexOf(a,0)},2);U("string",3,!1,!0,function(a,b){return b?S(b,a):I(a.a)},0,1);
U("string-length",1,!1,!0,function(a,b){return(b?S(b,a):I(a.a)).length},0,1);U("substring",3,!1,!1,function(a,b,c,d){c=R(c,a);if(isNaN(c)||Infinity==c||-Infinity==c)return"";d=d?R(d,a):Infinity;if(isNaN(d)||-Infinity===d)return"";c=Math.round(c)-1;var e=Math.max(c,0);a=S(b,a);return Infinity==d?a.substring(e):a.substring(e,c+Math.round(d))},2,3);U("substring-after",3,!1,!1,function(a,b,c){b=S(b,a);a=S(c,a);c=b.indexOf(a);return-1==c?"":b.substring(c+a.length)},2);
U("substring-before",3,!1,!1,function(a,b,c){b=S(b,a);a=S(c,a);a=b.indexOf(a);return-1==a?"":b.substring(0,a)},2);U("sum",1,!1,!1,function(a,b){for(var c=N(b.a(a)),d=0,e=O(c);e;e=O(c))d+=+I(e);return d},1,1,!0);U("translate",3,!1,!1,function(a,b,c,d){b=S(b,a);c=S(c,a);var e=S(d,a);a={};for(d=0;d<c.length;d++){var f=c.charAt(d);f in a||(a[f]=e.charAt(d))}c="";for(d=0;d<b.length;d++)f=b.charAt(d),c+=f in a?a[f]:f;return c},3);U("true",2,!1,!1,function(){return!0},0);function bc(a){P.call(this,3);this.c=a.substring(1,a.length-1)}q(bc,P);bc.prototype.a=function(){return this.c};bc.prototype.toString=function(){return"Literal: "+this.c};function cc(a){P.call(this,1);this.c=a}q(cc,P);cc.prototype.a=function(){return this.c};cc.prototype.toString=function(){return"Number: "+this.c};function dc(a,b){P.call(this,a.i);this.h=a;this.c=b;this.g=a.g;this.b=a.b;if(1==this.c.length){var c=this.c[0];c.u||c.c!=ec||(c=c.o,"*"!=c.f()&&(this.f={name:c.f(),s:null}))}}q(dc,P);function fc(){P.call(this,4)}q(fc,P);fc.prototype.a=function(a){var b=new K;a=a.a;9==a.nodeType?L(b,a):L(b,a.ownerDocument);return b};fc.prototype.toString=function(){return"Root Helper Expression"};function gc(){P.call(this,4)}q(gc,P);gc.prototype.a=function(a){var b=new K;L(b,a.a);return b};gc.prototype.toString=function(){return"Context Helper Expression"};
function hc(a){return"/"==a||"//"==a}dc.prototype.a=function(a){var b=this.h.a(a);if(!(b instanceof K))throw Error("Filter expression must evaluate to nodeset.");a=this.c;for(var c=0,d=a.length;c<d&&b.l;c++){var e=a[c],f=N(b,e.c.a),g;if(e.g||e.c!=ic)if(e.g||e.c!=jc)for(g=O(f),b=e.a(new ra(g));g=O(f);)g=e.a(new ra(g)),b=Lb(b,g);else g=O(f),b=e.a(new ra(g));else{for(g=O(f);(b=O(f))&&(!g.contains||g.contains(b))&&b.compareDocumentPosition(g)&8;g=b);b=e.a(new ra(g))}}return b};
dc.prototype.toString=function(){var a;a="Path Expression:"+B(this.h);if(this.c.length){var b=Ga(this.c,function(a,b){return a+B(b)},"Steps:");a+=B(b)}return a};function kc(a,b){this.a=a;this.b=!!b}
function Yb(a,b,c){for(c=c||0;c<a.a.length;c++)for(var d=a.a[c],e=N(b),f=b.l,g,h=0;g=O(e);h++){var p=a.b?f-h:h+1;g=d.a(new ra(g,p,f));if("number"==typeof g)p=p==g;else if("string"==typeof g||"boolean"==typeof g)p=!!g;else if(g instanceof K)p=0<g.l;else throw Error("Predicate.evaluate returned an unexpected type.");if(!p){p=e;g=p.f;var w=p.a;if(!w)throw Error("Next must be called at least once before remove.");var m=w.b,w=w.a;m?m.a=w:g.a=w;w?w.b=m:g.b=m;g.l--;p.a=null}}return b}
kc.prototype.toString=function(){return Ga(this.a,function(a,b){return a+B(b)},"Predicates:")};function lc(a){P.call(this,1);this.c=a;this.g=a.g;this.b=a.b}q(lc,P);lc.prototype.a=function(a){return-R(this.c,a)};lc.prototype.toString=function(){return"Unary Expression: -"+B(this.c)};function mc(a){P.call(this,4);this.c=a;Pb(this,Ha(this.c,function(a){return a.g}));Qb(this,Ha(this.c,function(a){return a.b}))}q(mc,P);mc.prototype.a=function(a){var b=new K;C(this.c,function(c){c=c.a(a);if(!(c instanceof K))throw Error("Path expression must evaluate to NodeSet.");b=Lb(b,c)});return b};mc.prototype.toString=function(){return Ga(this.c,function(a,b){return a+B(b)},"Union Expression:")};function nc(a,b,c,d){P.call(this,4);this.c=a;this.o=b;this.h=c||new kc([]);this.u=!!d;b=this.h;b=0<b.a.length?b.a[0].f:null;a.b&&b&&(a=b.name,a=F?a.toLowerCase():a,this.f={name:a,s:b.s});a:{a=this.h;for(b=0;b<a.a.length;b++)if(c=a.a[b],c.g||1==c.i||0==c.i){a=!0;break a}a=!1}this.g=a}q(nc,P);
nc.prototype.a=function(a){var b=a.a,c=this.f,d=null,e=null,f=0;c&&(d=c.name,e=c.s?S(c.s,a):null,f=1);if(this.u)if(this.g||this.c!=oc)if(b=N((new nc(pc,new A("node"))).a(a)),c=O(b))for(a=this.m(c,d,e,f);c=O(b);)a=Lb(a,this.m(c,d,e,f));else a=new K;else a=Db(this.o,b,d,e),a=Yb(this.h,a,f);else a=this.m(a.a,d,e,f);return a};nc.prototype.m=function(a,b,c,d){a=this.c.f(this.o,a,b,c);return a=Yb(this.h,a,d)};
nc.prototype.toString=function(){var a;a="Step:"+B("Operator: "+(this.u?"//":"/"));this.c.j&&(a+=B("Axis: "+this.c));a+=B(this.o);if(this.h.a.length){var b=Ga(this.h.a,function(a,b){return a+B(b)},"Predicates:");a+=B(b)}return a};function qc(a,b,c,d){this.j=a;this.f=b;this.a=c;this.b=d}qc.prototype.toString=function(){return this.j};var rc={};function V(a,b,c,d){if(rc.hasOwnProperty(a))throw Error("Axis already created: "+a);b=new qc(a,b,c,!!d);return rc[a]=b}
V("ancestor",function(a,b){for(var c=new K,d=b;d=d.parentNode;)a.a(d)&&c.unshift(d);return c},!0);V("ancestor-or-self",function(a,b){var c=new K,d=b;do a.a(d)&&c.unshift(d);while(d=d.parentNode);return c},!0);
var ec=V("attribute",function(a,b){var c=new K,d=a.f();if("style"==d&&F&&b.style)return L(c,new ub(b.style,b,"style",b.style.cssText)),c;var e=b.attributes;if(e)if(a instanceof A&&null===a.b||"*"==d)for(var d=0,f;f=e[d];d++)F?f.nodeValue&&L(c,vb(b,f)):L(c,f);else(f=e.getNamedItem(d))&&(F?f.nodeValue&&L(c,vb(b,f)):L(c,f));return c},!1),oc=V("child",function(a,b,c,d,e){return(F?Ib:Jb).call(null,a,b,n(c)?c:null,n(d)?d:null,e||new K)},!1,!0);V("descendant",Db,!1,!0);
var pc=V("descendant-or-self",function(a,b,c,d){var e=new K;J(b,c,d)&&a.a(b)&&L(e,b);return Db(a,b,c,d,e)},!1,!0),ic=V("following",function(a,b,c,d){var e=new K;do for(var f=b;f=f.nextSibling;)J(f,c,d)&&a.a(f)&&L(e,f),e=Db(a,f,c,d,e);while(b=b.parentNode);return e},!1,!0);V("following-sibling",function(a,b){for(var c=new K,d=b;d=d.nextSibling;)a.a(d)&&L(c,d);return c},!1);V("namespace",function(){return new K},!1);
var sc=V("parent",function(a,b){var c=new K;if(9==b.nodeType)return c;if(2==b.nodeType)return L(c,b.ownerElement),c;var d=b.parentNode;a.a(d)&&L(c,d);return c},!1),jc=V("preceding",function(a,b,c,d){var e=new K,f=[];do f.unshift(b);while(b=b.parentNode);for(var g=1,h=f.length;g<h;g++){var p=[];for(b=f[g];b=b.previousSibling;)p.unshift(b);for(var w=0,m=p.length;w<m;w++)b=p[w],J(b,c,d)&&a.a(b)&&L(e,b),e=Db(a,b,c,d,e)}return e},!0,!0);
V("preceding-sibling",function(a,b){for(var c=new K,d=b;d=d.previousSibling;)a.a(d)&&c.unshift(d);return c},!0);var tc=V("self",function(a,b){var c=new K;a.a(b)&&L(c,b);return c},!1);function uc(a,b){this.a=a;this.b=b}function vc(a){for(var b,c=[];;){W(a,"Missing right hand side of binary expression.");b=wc(a);var d=v(a.a);if(!d)break;var e=(d=Wb[d]||null)&&d.A;if(!e){a.a.a--;break}for(;c.length&&e<=c[c.length-1].A;)b=new Sb(c.pop(),c.pop(),b);c.push(b,d)}for(;c.length;)b=new Sb(c.pop(),c.pop(),b);return b}function W(a,b){if(wa(a.a))throw Error(b);}function xc(a,b){var c=v(a.a);if(c!=b)throw Error("Bad token, expected: "+b+" got: "+c);}
function yc(a){a=v(a.a);if(")"!=a)throw Error("Bad token: "+a);}function zc(a){a=v(a.a);if(2>a.length)throw Error("Unclosed literal string");return new bc(a)}
function Ac(a){var b,c=[],d;if(hc(t(a.a))){b=v(a.a);d=t(a.a);if("/"==b&&(wa(a.a)||"."!=d&&".."!=d&&"@"!=d&&"*"!=d&&!/(?![0-9])[\w]/.test(d)))return new fc;d=new fc;W(a,"Missing next location step.");b=Bc(a,b);c.push(b)}else{a:{b=t(a.a);d=b.charAt(0);switch(d){case "$":throw Error("Variable reference not allowed in HTML XPath");case "(":v(a.a);b=vc(a);W(a,'unclosed "("');xc(a,")");break;case '"':case "'":b=zc(a);break;default:if(isNaN(+b))if(!za(b)&&/(?![0-9])[\w]/.test(d)&&"("==t(a.a,1)){b=v(a.a);
b=ac[b]||null;v(a.a);for(d=[];")"!=t(a.a);){W(a,"Missing function argument list.");d.push(vc(a));if(","!=t(a.a))break;v(a.a)}W(a,"Unclosed function argument list.");yc(a);b=new Zb(b,d)}else{b=null;break a}else b=new cc(+v(a.a))}"["==t(a.a)&&(d=new kc(Cc(a)),b=new Xb(b,d))}if(b)if(hc(t(a.a)))d=b;else return b;else b=Bc(a,"/"),d=new gc,c.push(b)}for(;hc(t(a.a));)b=v(a.a),W(a,"Missing next location step."),b=Bc(a,b),c.push(b);return new dc(d,c)}
function Bc(a,b){var c,d,e;if("/"!=b&&"//"!=b)throw Error('Step op should be "/" or "//"');if("."==t(a.a))return d=new nc(tc,new A("node")),v(a.a),d;if(".."==t(a.a))return d=new nc(sc,new A("node")),v(a.a),d;var f;if("@"==t(a.a))f=ec,v(a.a),W(a,"Missing attribute name");else if("::"==t(a.a,1)){if(!/(?![0-9])[\w]/.test(t(a.a).charAt(0)))throw Error("Bad token: "+v(a.a));c=v(a.a);f=rc[c]||null;if(!f)throw Error("No axis with name: "+c);v(a.a);W(a,"Missing node name")}else f=oc;c=t(a.a);if(/(?![0-9])[\w\*]/.test(c.charAt(0)))if("("==
t(a.a,1)){if(!za(c))throw Error("Invalid node type: "+c);c=v(a.a);if(!za(c))throw Error("Invalid type name: "+c);xc(a,"(");W(a,"Bad nodetype");e=t(a.a).charAt(0);var g=null;if('"'==e||"'"==e)g=zc(a);W(a,"Bad nodetype");yc(a);c=new A(c,g)}else if(c=v(a.a),e=c.indexOf(":"),-1==e)c=new Aa(c);else{var g=c.substring(0,e),h;if("*"==g)h="*";else if(h=a.b(g),!h)throw Error("Namespace prefix not declared: "+g);c=c.substr(e+1);c=new Aa(c,h)}else throw Error("Bad token: "+v(a.a));e=new kc(Cc(a),f.a);return d||
new nc(f,c,e,"//"==b)}function Cc(a){for(var b=[];"["==t(a.a);){v(a.a);W(a,"Missing predicate expression.");var c=vc(a);b.push(c);W(a,"Unclosed predicate expression.");xc(a,"]")}return b}function wc(a){if("-"==t(a.a))return v(a.a),new lc(wc(a));var b=Ac(a);if("|"!=t(a.a))a=b;else{for(b=[b];"|"==v(a.a);)W(a,"Missing next union location path."),b.push(Ac(a));a.a.a--;a=new mc(b)}return a};function Dc(a,b){if(!a.length)throw Error("Empty XPath expression.");var c=ta(a);if(wa(c))throw Error("Invalid XPath expression.");b?"function"==ea(b)||(b=ha(b.lookupNamespaceURI,b)):b=function(){return null};var d=vc(new uc(c,b));if(!wa(c))throw Error("Bad token: "+v(c));this.evaluate=function(a,b){var c=d.a(new ra(a));return new X(c,b)}}
function X(a,b){if(!b)if(a instanceof K)b=4;else if("string"==typeof a)b=2;else if("number"==typeof a)b=1;else if("boolean"==typeof a)b=3;else throw Error("Unexpected evaluation result.");if(2!=b&&1!=b&&3!=b&&!(a instanceof K))throw Error("value could not be converted to the specified type");this.resultType=b;var c;switch(b){case 2:this.stringValue=a instanceof K?Nb(a):""+a;break;case 1:this.numberValue=a instanceof K?+Nb(a):+a;break;case 3:this.booleanValue=a instanceof K?0<a.l:!!a;break;case 4:case 5:case 6:case 7:var d=
N(a);c=[];for(var e=O(d);e;e=O(d))c.push(e instanceof ub?e.a:e);this.snapshotLength=a.l;this.invalidIteratorState=!1;break;case 8:case 9:d=Mb(a);this.singleNodeValue=d instanceof ub?d.a:d;break;default:throw Error("Unknown XPathResult type.");}var f=0;this.iterateNext=function(){if(4!=b&&5!=b)throw Error("iterateNext called with wrong result type");return f>=c.length?null:c[f++]};this.snapshotItem=function(a){if(6!=b&&7!=b)throw Error("snapshotItem called with wrong result type");return a>=c.length||
0>a?null:c[a]}}X.ANY_TYPE=0;X.NUMBER_TYPE=1;X.STRING_TYPE=2;X.BOOLEAN_TYPE=3;X.UNORDERED_NODE_ITERATOR_TYPE=4;X.ORDERED_NODE_ITERATOR_TYPE=5;X.UNORDERED_NODE_SNAPSHOT_TYPE=6;X.ORDERED_NODE_SNAPSHOT_TYPE=7;X.ANY_UNORDERED_NODE_TYPE=8;X.FIRST_ORDERED_NODE_TYPE=9;function Ec(a){this.lookupNamespaceURI=Ba(a)}
function Fc(a,b){var c=a||k,d=c.Document&&c.Document.prototype||c.document;if(!d.evaluate||b)c.XPathResult=X,d.evaluate=function(a,b,c,d){return(new Dc(a,c)).evaluate(b,d)},d.createExpression=function(a,b){return new Dc(a,b)},d.createNSResolver=function(a){return new Ec(a)}}da("wgxpath.install",Fc);var Gc=function(){var a={I:"http://www.w3.org/2000/svg"};return function(b){return a[b]||null}}();
function Hc(a,b){var c=G(a);if(!c.documentElement)return null;(E||ib)&&Fc(c?c.parentWindow||c.defaultView:window);try{var d=c.createNSResolver?c.createNSResolver(c.documentElement):Gc;if(E&&!bb(7))return c.evaluate.call(c,b,a,d,9,null);if(!E||9<=Number(db)){for(var e={},f=c.getElementsByTagName("*"),g=0;g<f.length;++g){var h=f[g],p=h.namespaceURI;if(p&&!e[p]){var w=h.lookupPrefix(p);if(!w)var m=p.match(".*/(\\w+)/?$"),w=m?m[1]:"xhtml";e[p]=w}}var u={},y;for(y in e)u[e[y]]=y;d=function(a){return u[a]||
null}}try{return c.evaluate(b,a,d,9,null)}catch(Q){if("TypeError"===Q.name)return d=c.createNSResolver?c.createNSResolver(c.documentElement):Gc,c.evaluate(b,a,d,9,null);throw Q;}}catch(Q){if(!Wa||"NS_ERROR_ILLEGAL_VALUE"!=Q.name)throw new ja(32,"Unable to locate an element with the xpath expression "+b+" because of the following error:\n"+Q);}}
function Ic(a,b){var c=function(){var c=Hc(b,a);return c?c.singleNodeValue||null:b.selectSingleNode?(c=G(b),c.setProperty&&c.setProperty("SelectionLanguage","XPath"),b.selectSingleNode(a)):null}();if(null!==c&&(!c||1!=c.nodeType))throw new ja(32,'The result of the xpath expression "'+a+'" is: '+c+". It should be an element.");return c};var Jc="function"===typeof ShadowRoot;function Kc(a){for(a=a.parentNode;a&&1!=a.nodeType&&9!=a.nodeType&&11!=a.nodeType;)a=a.parentNode;return M(a)?a:null}
function Y(a,b){var c=qa(b);if("float"==c||"cssFloat"==c||"styleFloat"==c)c=Cb?"styleFloat":"cssFloat";var d;a:{d=c;var e=G(a);if(e.defaultView&&e.defaultView.getComputedStyle&&(e=e.defaultView.getComputedStyle(a,null))){d=e[d]||e.getPropertyValue(d)||"";break a}d=""}d=d||Lc(a,c);if(null===d)d=null;else if(0<=Ea(Na,c)){b:{var f=d.match(Qa);if(f){var c=Number(f[1]),e=Number(f[2]),g=Number(f[3]),f=Number(f[4]);if(0<=c&&255>=c&&0<=e&&255>=e&&0<=g&&255>=g&&0<=f&&1>=f){c=[c,e,g,f];break b}}c=null}if(!c)b:{if(g=
d.match(Ra))if(c=Number(g[1]),e=Number(g[2]),g=Number(g[3]),0<=c&&255>=c&&0<=e&&255>=e&&0<=g&&255>=g){c=[c,e,g,1];break b}c=null}if(!c)b:{c=d.toLowerCase();e=la[c.toLowerCase()];if(!e&&(e="#"==c.charAt(0)?c:"#"+c,4==e.length&&(e=e.replace(Oa,"#$1$1$2$2$3$3")),!Pa.test(e))){c=null;break b}c=[parseInt(e.substr(1,2),16),parseInt(e.substr(3,2),16),parseInt(e.substr(5,2),16),1]}d=c?"rgba("+c.join(", ")+")":d}return d}
function Lc(a,b){var c=a.currentStyle||a.style,d=c[b];!l(d)&&"function"==ea(c.getPropertyValue)&&(d=c.getPropertyValue(b));return"inherit"!=d?l(d)?d:null:(c=Kc(a))?Lc(c,b):null}
function Mc(a,b,c){function d(a){var b=Nc(a);return 0<b.height&&0<b.width?!0:M(a,"PATH")&&(0<b.height||0<b.width)?(a=Y(a,"stroke-width"),!!a&&0<parseInt(a,10)):"hidden"!=Y(a,"overflow")&&Ha(a.childNodes,function(a){return 3==a.nodeType||M(a)&&d(a)})}function e(a){return Oc(a)==Z&&Ia(a.childNodes,function(a){return!M(a)||e(a)||!d(a)})}if(!M(a))throw Error("Argument to isShown must be of type Element");if(M(a,"BODY"))return!0;if(M(a,"OPTION")||M(a,"OPTGROUP"))return a=qb(a,function(a){return M(a,"SELECT")}),
!!a&&Mc(a,!0,c);var f=Pc(a);if(f)return!!f.w&&0<f.rect.width&&0<f.rect.height&&Mc(f.w,b,c);if(M(a,"INPUT")&&"hidden"==a.type.toLowerCase()||M(a,"NOSCRIPT"))return!1;f=Y(a,"visibility");return"collapse"!=f&&"hidden"!=f&&c(a)&&(b||Qc(a))&&d(a)?!e(a):!1}var Z="hidden";
function Oc(a){function b(a){function b(a){return a==g?!0:!Y(a,"display").lastIndexOf("inline",0)||"absolute"==c&&"static"==Y(a,"position")?!1:!0}var c=Y(a,"position");if("fixed"==c)return w=!0,a==g?null:g;for(a=Kc(a);a&&!b(a);)a=Kc(a);return a}function c(a){var b=a;if("visible"==p)if(a==g&&h)b=h;else if(a==h)return{x:"visible",y:"visible"};b={x:Y(b,"overflow-x"),y:Y(b,"overflow-y")};a==g&&(b.x="visible"==b.x?"auto":b.x,b.y="visible"==b.y?"auto":b.y);return b}function d(a){if(a==g){var b=(new rb(f)).a;
a=b.scrollingElement?b.scrollingElement:Xa||"CSS1Compat"!=b.compatMode?b.body||b.documentElement:b.documentElement;b=b.parentWindow||b.defaultView;a=E&&bb("10")&&b.pageYOffset!=a.scrollTop?new D(a.scrollLeft,a.scrollTop):new D(b.pageXOffset||a.scrollLeft,b.pageYOffset||a.scrollTop)}else a=new D(a.scrollLeft,a.scrollTop);return a}var e=Rc(a),f=G(a),g=f.documentElement,h=f.body,p=Y(g,"overflow"),w;for(a=b(a);a;a=b(a)){var m=c(a);if("visible"!=m.x||"visible"!=m.y){var u=Nc(a);if(!u.width||!u.height)return Z;
var y=e.right<u.left,Q=e.bottom<u.top;if(y&&"hidden"==m.x||Q&&"hidden"==m.y)return Z;if(y&&"visible"!=m.x||Q&&"visible"!=m.y){y=d(a);Q=e.bottom<u.top-y.y;if(e.right<u.left-y.x&&"visible"!=m.x||Q&&"visible"!=m.x)return Z;e=Oc(a);return e==Z?Z:"scroll"}y=e.left>=u.left+u.width;u=e.top>=u.top+u.height;if(y&&"hidden"==m.x||u&&"hidden"==m.y)return Z;if(y&&"visible"!=m.x||u&&"visible"!=m.y){if(w&&(m=d(a),e.left>=g.scrollWidth-m.x||e.right>=g.scrollHeight-m.y))return Z;e=Oc(a);return e==Z?Z:"scroll"}}}return"none"}
function Nc(a){var b=Pc(a);if(b)return b.rect;if(M(a,"HTML"))return a=G(a),a=((a?a.parentWindow||a.defaultView:window)||window).document,a="CSS1Compat"==a.compatMode?a.documentElement:a.body,a=new ma(a.clientWidth,a.clientHeight),new H(0,0,a.width,a.height);var c;try{c=a.getBoundingClientRect()}catch(d){return new H(0,0,0,0)}b=new H(c.left,c.top,c.right-c.left,c.bottom-c.top);E&&a.ownerDocument.body&&(a=G(a),b.left-=a.documentElement.clientLeft+a.body.clientLeft,b.top-=a.documentElement.clientTop+
a.body.clientTop);return b}function Pc(a){var b=M(a,"MAP");if(!b&&!M(a,"AREA"))return null;var c=b?a:M(a.parentNode,"MAP")?a.parentNode:null,d=null,e=null;c&&c.name&&(d=Ic('/descendant::*[@usemap = "#'+c.name+'"]',G(c)))&&(e=Nc(d),b||"default"==a.shape.toLowerCase()||(a=Sc(a),b=Math.min(Math.max(a.left,0),e.width),c=Math.min(Math.max(a.top,0),e.height),e=new H(b+e.left,c+e.top,Math.min(a.width,e.width-b),Math.min(a.height,e.height-c))));return{w:d,rect:e||new H(0,0,0,0)}}
function Sc(a){var b=a.shape.toLowerCase();a=a.coords.split(",");if("rect"==b&&4==a.length){var b=a[0],c=a[1];return new H(b,c,a[2]-b,a[3]-c)}if("circle"==b&&3==a.length)return b=a[2],new H(a[0]-b,a[1]-b,2*b,2*b);if("poly"==b&&2<a.length){for(var b=a[0],c=a[1],d=b,e=c,f=2;f+1<a.length;f+=2)b=Math.min(b,a[f]),d=Math.max(d,a[f]),c=Math.min(c,a[f+1]),e=Math.max(e,a[f+1]);return new H(b,c,d-b,e-c)}return new H(0,0,0,0)}function Rc(a){a=Nc(a);return new eb(a.top,a.left+a.width,a.top+a.height,a.left)}
function Qc(a){if(Cb){if("relative"==Y(a,"position"))return 1;a=Y(a,"filter");return(a=a.match(/^alpha\(opacity=(\d*)\)/)||a.match(/^progid:DXImageTransform.Microsoft.Alpha\(Opacity=(\d*)\)/))?Number(a[1])/100:1}return Tc(a)}function Tc(a){var b=1,c=Y(a,"opacity");c&&(b=Number(c));(a=Kc(a))&&(b*=Tc(a));return b};da("_",function(a,b){var c;c=Jc?function(b){if("none"==Y(b,"display"))return!1;var e;do{e=b.parentNode;if(b.getDestinationInsertionPoints){var f=b.getDestinationInsertionPoints();0<f.length&&(e=f[f.length-1])}if(e instanceof ShadowRoot){if(e.host.shadowRoot!=e)return!1;e=e.host}else if(9==e.nodeType||11==e.nodeType)e=null}while(a&&1!=a.nodeType);return!e||c(e)}:function(a){if("none"==Y(a,"display"))return!1;a=Kc(a);return!a||c(a)};return Mc(a,!!b,c)});; return this._.apply(null,arguments);}.apply({navigator:typeof window!='undefined'?window.navigator:null,document:typeof window!='undefined'?window.document:null}, arguments);}
"""

class WebElement(object):
    """Represents a DOM element.

    Generally, all interesting operations that interact with a document will be
    performed through this interface.

    All method calls will do a freshness check to ensure that the element
    reference is still valid.  This essentially determines whether or not the
    element is still attached to the DOM.  If this test fails, then an
    ``StaleElementReferenceException`` is thrown, and all future calls to this
    instance will fail."""

    def __init__(self, parent, id_, w3c=False):
        self._parent = parent
        self._id = id_
        self._w3c = w3c

    def __repr__(self):
        return '<{0.__module__}.{0.__name__} (session="{1}", element="{2}")>'.format(
            type(self), self._parent.session_id, self._id)

    @property
    def tag_name(self):
        """This element's ``tagName`` property."""
        return self._execute(Command.GET_ELEMENT_TAG_NAME)['value']

    @property
    def text(self):
        """The text of the element."""
        return self._execute(Command.GET_ELEMENT_TEXT)['value']

    def click(self):
        """Clicks the element."""
        self._execute(Command.CLICK_ELEMENT)

    def submit(self):
        """Submits a form."""
        if self._w3c:
            form = self.find_element(By.XPATH, "./ancestor-or-self::form")
            self._parent.execute_script(
                "var e = arguments[0].ownerDocument.createEvent('Event');"
                "e.initEvent('submit', true, true);"
                "if (arguments[0].dispatchEvent(e)) { arguments[0].submit() }", form)
        else:
            self._execute(Command.SUBMIT_ELEMENT)

    def clear(self):
        """Clears the text if it's a text entry element."""
        self._execute(Command.CLEAR_ELEMENT)

    def get_property(self, name):
        """
        Gets the given property of the element.

        :Args:
            - name - Name of the property to retrieve.

        Example::

            # Check if the "active" CSS class is applied to an element.
            text_length = target_element.get_property("text_length")
        """
        try:
            return self._execute(Command.GET_ELEMENT_PROPERTY, {"name": name})["value"]
        except WebDriverException:
            # if we hit an end point that doesnt understand getElementProperty lets fake it
            return self.parent.execute_script('return arguments[0][arguments[1]]', self, name)

    def get_attribute(self, name):
        """Gets the given attribute or property of the element.

        This method will first try to return the value of a property with the
        given name. If a property with that name doesn't exist, it returns the
        value of the attribute with the same name. If there's no attribute with
        that name, ``None`` is returned.

        Values which are considered truthy, that is equals "true" or "false",
        are returned as booleans.  All other non-``None`` values are returned
        as strings.  For attributes or properties which do not exist, ``None``
        is returned.

        :Args:
            - name - Name of the attribute/property to retrieve.

        Example::

            # Check if the "active" CSS class is applied to an element.
            is_active = "active" in target_element.get_attribute("class")

        """

        attributeValue = ''
        if self._w3c:
            attributeValue = self.parent.execute_script(
                "return (%s).apply(null, arguments);" % getAttribute_js,
                self, name)
        else:
            resp = self._execute(Command.GET_ELEMENT_ATTRIBUTE, {'name': name})
            attributeValue = resp.get('value')
            if attributeValue is not None:
                if name != 'value' and attributeValue.lower() in ('true', 'false'):
                    attributeValue = attributeValue.lower()
        return attributeValue

    def is_selected(self):
        """Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.
        """
        return self._execute(Command.IS_ELEMENT_SELECTED)['value']

    def is_enabled(self):
        """Returns whether the element is enabled."""
        return self._execute(Command.IS_ELEMENT_ENABLED)['value']

    def find_element_by_id(self, id_):
        """Finds element within this element's children by ID.

        :Args:
            - id\_ - ID of child element to locate.
        """
        return self.find_element(by=By.ID, value=id_)

    def find_elements_by_id(self, id_):
        """Finds a list of elements within this element's children by ID.

        :Args:
            - id\_ - Id of child element to find.
        """
        return self.find_elements(by=By.ID, value=id_)

    def find_element_by_name(self, name):
        """Finds element within this element's children by name.

        :Args:
            - name - name property of the element to find.
        """
        return self.find_element(by=By.NAME, value=name)

    def find_elements_by_name(self, name):
        """Finds a list of elements within this element's children by name.

        :Args:
            - name - name property to search for.
        """
        return self.find_elements(by=By.NAME, value=name)

    def find_element_by_link_text(self, link_text):
        """Finds element within this element's children by visible link text.

        :Args:
            - link_text - Link text string to search for.
        """
        return self.find_element(by=By.LINK_TEXT, value=link_text)

    def find_elements_by_link_text(self, link_text):
        """Finds a list of elements within this element's children by visible link text.

        :Args:
            - link_text - Link text string to search for.
        """
        return self.find_elements(by=By.LINK_TEXT, value=link_text)

    def find_element_by_partial_link_text(self, link_text):
        """Finds element within this element's children by partially visible link text.

        :Args:
            - link_text - Link text string to search for.
        """
        return self.find_element(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_elements_by_partial_link_text(self, link_text):
        """Finds a list of elements within this element's children by link text.

        :Args:
            - link_text - Link text string to search for.
        """
        return self.find_elements(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_element_by_tag_name(self, name):
        """Finds element within this element's children by tag name.

        :Args:
            - name - name of html tag (eg: h1, a, span)
        """
        return self.find_element(by=By.TAG_NAME, value=name)

    def find_elements_by_tag_name(self, name):
        """Finds a list of elements within this element's children by tag name.

        :Args:
            - name - name of html tag (eg: h1, a, span)
        """
        return self.find_elements(by=By.TAG_NAME, value=name)

    def find_element_by_xpath(self, xpath):
        """Finds element by xpath.

        :Args:
            xpath - xpath of element to locate.  "//input[@class='myelement']"

        Note: The base path will be relative to this element's location.

        This will select the first link under this element.

        ::

            myelement.find_elements_by_xpath(".//a")

        However, this will select the first link on the page.

        ::

            myelement.find_elements_by_xpath("//a")

        """
        return self.find_element(by=By.XPATH, value=xpath)

    def find_elements_by_xpath(self, xpath):
        """Finds elements within the element by xpath.

        :Args:
            - xpath - xpath locator string.

        Note: The base path will be relative to this element's location.

        This will select all links under this element.

        ::

            myelement.find_elements_by_xpath(".//a")

        However, this will select all links in the page itself.

        ::

            myelement.find_elements_by_xpath("//a")

        """
        return self.find_elements(by=By.XPATH, value=xpath)

    def find_element_by_class_name(self, name):
        """Finds element within this element's children by class name.

        :Args:
            - name - class name to search for.
        """
        return self.find_element(by=By.CLASS_NAME, value=name)

    def find_elements_by_class_name(self, name):
        """Finds a list of elements within this element's children by class name.

        :Args:
            - name - class name to search for.
        """
        return self.find_elements(by=By.CLASS_NAME, value=name)

    def find_element_by_css_selector(self, css_selector):
        """Finds element within this element's children by CSS selector.

        :Args:
            - css_selector - CSS selctor string, ex: 'a.nav#home'
        """
        return self.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def find_elements_by_css_selector(self, css_selector):
        """Finds a list of elements within this element's children by CSS selector.

        :Args:
            - css_selector - CSS selctor string, ex: 'a.nav#home'
        """
        return self.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def send_keys(self, *value):
        """Simulates typing into the element.

        :Args:
            - value - A string for typing, or setting form fields.  For setting
              file inputs, this could be a local file path.

        Use this to send simple key events or to fill out form fields::

            form_textfield = driver.find_element_by_name('username')
            form_textfield.send_keys("admin")

        This can also be used to set file inputs.

        ::

            file_input = driver.find_element_by_name('profilePic')
            file_input.send_keys("path/to/profilepic.gif")
            # Generally it's better to wrap the file path in one of the methods
            # in os.path to return the actual path to support cross OS testing.
            # file_input.send_keys(os.path.abspath("path/to/profilepic.gif"))

        """
        # transfer file to another machine only if remote driver is used
        # the same behaviour as for java binding
        if self.parent._is_remote:
            local_file = self.parent.file_detector.is_local_file(*value)
            if local_file is not None:
                value = self._upload(local_file)

        self._execute(Command.SEND_KEYS_TO_ELEMENT, {'value': keys_to_typing(value)})

    # RenderedWebElement Items
    def is_displayed(self):
        """Whether the element is visible to a user."""
        # Only go into this conditional for browsers that don't use the atom themselves
        if self._w3c and self.parent.capabilities['browserName'] == 'safari':
            return self.parent.execute_script(
                "return (%s).apply(null, arguments);" % isDisplayed_js,
                self)
        else:
            return self._execute(Command.IS_ELEMENT_DISPLAYED)['value']

    @property
    def location_once_scrolled_into_view(self):
        """THIS PROPERTY MAY CHANGE WITHOUT WARNING. Use this to discover
        where on the screen an element is so that we can click it. This method
        should cause the element to be scrolled into view.

        Returns the top lefthand corner location on the screen, or ``None`` if
        the element is not visible.

        """
        if self._w3c:
            old_loc = self._execute(Command.EXECUTE_SCRIPT, {
                'script': "arguments[0].scrollIntoView(true); return arguments[0].getBoundingClientRect()",
                'args': [self]})['value']
            return {"x": round(old_loc['x']),
                    "y": round(old_loc['y'])}
        else:
            return self._execute(Command.GET_ELEMENT_LOCATION_ONCE_SCROLLED_INTO_VIEW)['value']

    @property
    def size(self):
        """The size of the element."""
        size = {}
        if self._w3c:
            size = self._execute(Command.GET_ELEMENT_RECT)['value']
        else:
            size = self._execute(Command.GET_ELEMENT_SIZE)['value']
        new_size = {"height": size["height"],
                    "width": size["width"]}
        return new_size

    def value_of_css_property(self, property_name):
        """The value of a CSS property."""
        return self._execute(Command.GET_ELEMENT_VALUE_OF_CSS_PROPERTY, {
            'propertyName': property_name})['value']

    @property
    def location(self):
        """The location of the element in the renderable canvas."""
        if self._w3c:
            old_loc = self._execute(Command.GET_ELEMENT_RECT)['value']
        else:
            old_loc = self._execute(Command.GET_ELEMENT_LOCATION)['value']
        new_loc = {"x": round(old_loc['x']),
                   "y": round(old_loc['y'])}
        return new_loc

    @property
    def rect(self):
        """A dictionary with the size and location of the element."""
        return self._execute(Command.GET_ELEMENT_RECT)['value']

    @property
    def screenshot_as_base64(self):
        """
        Gets the screenshot of the current element as a base64 encoded string.

        :Usage:
            img_b64 = element.screenshot_as_base64
        """
        return self._execute(Command.ELEMENT_SCREENSHOT)['value']

    @property
    def screenshot_as_png(self):
        """
        Gets the screenshot of the current element as a binary data.

        :Usage:
            element_png = element.screenshot_as_png
        """
        return base64.b64decode(self.screenshot_as_base64.encode('ascii'))

    def screenshot(self, filename):
        """
        Gets the screenshot of the current element. Returns False if there is
           any IOError, else returns True. Use full paths in your filename.

        :Args:
         - filename: The full path you wish to save your screenshot to.

        :Usage:
            element.screenshot('/Screenshots/foo.png')
        """
        png = self.screenshot_as_png
        try:
            with open(filename, 'wb') as f:
                f.write(png)
        except IOError:
            return False
        finally:
            del png
        return True

    @property
    def parent(self):
        """Internal reference to the WebDriver instance this element was found from."""
        return self._parent

    @property
    def id(self):
        """Internal ID used by selenium.

        This is mainly for internal use. Simple use cases such as checking if 2
        webelements refer to the same element, can be done using ``==``::

            if element1 == element2:
                print("These 2 are equal")

        """
        return self._id

    def __eq__(self, element):
        return hasattr(element, 'id') and self._id == element.id

    def __ne__(self, element):
        return not self.__eq__(element)

    # Private Methods
    def _execute(self, command, params=None):
        """Executes a command against the underlying HTML element.

        Args:
          command: The name of the command to _execute as a string.
          params: A dictionary of named parameters to send with the command.

        Returns:
          The command's JSON response loaded into a dictionary object.
        """
        if not params:
            params = {}
        params['id'] = self._id
        return self._parent.execute(command, params)

    def find_element(self, by=By.ID, value=None):
        if self._w3c:
            if by == By.ID:
                by = By.CSS_SELECTOR
                value = '[id="%s"]' % value
            elif by == By.TAG_NAME:
                by = By.CSS_SELECTOR
            elif by == By.CLASS_NAME:
                by = By.CSS_SELECTOR
                value = ".%s" % value
            elif by == By.NAME:
                by = By.CSS_SELECTOR
                value = '[name="%s"]' % value

        return self._execute(Command.FIND_CHILD_ELEMENT,
                             {"using": by, "value": value})['value']

    def find_elements(self, by=By.ID, value=None):
        if self._w3c:
            if by == By.ID:
                by = By.CSS_SELECTOR
                value = '[id="%s"]' % value
            elif by == By.TAG_NAME:
                by = By.CSS_SELECTOR
            elif by == By.CLASS_NAME:
                by = By.CSS_SELECTOR
                value = ".%s" % value
            elif by == By.NAME:
                by = By.CSS_SELECTOR
                value = '[name="%s"]' % value

        return self._execute(Command.FIND_CHILD_ELEMENTS,
                             {"using": by, "value": value})['value']

    def __hash__(self):
        return int(hashlib.md5(self._id.encode('utf-8')).hexdigest(), 16)

    def _upload(self, filename):
        fp = IOStream()
        zipped = zipfile.ZipFile(fp, 'w', zipfile.ZIP_DEFLATED)
        zipped.write(filename, os.path.split(filename)[1])
        zipped.close()
        content = base64.encodestring(fp.getvalue())
        if not isinstance(content, str):
            content = content.decode('utf-8')
        try:
            return self._execute(Command.UPLOAD_FILE, {'file': content})['value']
        except WebDriverException as e:
            if "Unrecognized command: POST" in e.__str__():
                return filename
            elif "Command not found: POST " in e.__str__():
                return filename
            elif '{"status":405,"value":["GET","HEAD","DELETE"]}' in e.__str__():
                return filename
            else:
                raise e
