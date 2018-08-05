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
 * Generate cache
 */
function gencache(id)
{
	var warning = getel("box-warn");
	var loader = getel('loader-gen');
	hidewarning(warning);
	// prepare request
	var cmd = "cache.generate";
	var args = new Array();
	// call webservice
	showloader(loader); 
	callws( data = request(cmd = cmd, args = args.join("")) ,
			callback = readresponse_cb,
			el_warm = warning,
			input_clr = new Array(),
			div_clr =  new Array(),
			el_div_dst = null,
			el_loader = loader
		);
}