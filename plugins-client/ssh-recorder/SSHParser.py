#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive testing project
# Copyright (c) 2010-2017 Denis Machard
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
#
# Gfi Informatique, Inc., hereby disclaims all copyright interest in the
# extensive testing project written by Denis Machard
# 
# Author: Emmanuel Monsoro
# Contact: e1gle1984@gmail.com
# Website: www.extensivetesting.org
# -------------------------------------------------------------------

import copy
import re

class SSHParser():
    def __init__(self):
        """
        """
        self.sshLog = None
        self.prompts = []
        self.commands_dict = {}
        self.commands_line_indices = []
        self.ignored_line_indices = []
        self.ip=""
        self.login=""

    def txt2html(self, text, prompts=None):

        lines = text.splitlines()
        logs = ""
        if prompts is None:
            prompt_re = r'\[?[^\]\n]*@[^\]\n]*[ :][^\]\n]+\]?[#\$] ?'
        else:
            self.sshLog = None
            self.prompts = []
            self.commands_dict = {}
            self.commands_line_indices = []
            self.ip=""
            self.login=""
            prompt_re = r'('
            for p in prompts:
                prompt_re += re.escape(p)+' ?|'
            prompt_re=prompt_re[:-1] +')'

        exp_lines=""
        line_index=0
        index = 0

        current_command = ""
        for line in lines:
            if index == 0:
                if re.search(r'[A-Za-z]+@(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',line) is not None:
                    self.login=re.sub(r'.*\b([A-Za-z]+)@.*','\\1',line)
                    self.ip=re.sub(r'.*@((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)).*','\\1',line)
            if re.search(prompt_re,line) is not None: #prompt + command
                
                if len(exp_lines)>0:
                    exp_lines=exp_lines[:-1]
                    if index >0:
                        self.commands_dict[index]["expected"]=exp_lines
                        if self.commands_dict[index]["command"].startswith("su") or self.commands_dict[index]["command"].startswith("scp") or self.commands_dict[index]["command"].startswith("ssh"):
                            if self.commands_dict[index]["expected"].startswith("Password:") or re.search(re.compile(r'^.*@.*password:$',re.MULTILINE),self.commands_dict[index]["expected"]):
                                index+=1
                                self.commands_line_indices.append(index)
                                self.commands_dict[index]=dict()
                                self.commands_dict[index]["command"]="[PASSWORD]"
                                self.commands_dict[index]["prompt"] = ""
                                self.commands_dict[index]["line_index"] = line_index
                                line1 = '<p id="c%s"><code id="c%s" class="command">%s</code></p>'%(index,index,command)
                                logs+=line1 + "<br/>"
                                line_index+=1
                    else:
                        self.commands_line_indices.append(index)
                        self.commands_dict[index]=dict()
                        self.commands_dict[index]["command"]= ""
                        self.commands_dict[index]["prompt"] = ""
                        self.commands_dict[index]["line_index"] = line_index
                        self.commands_dict[index]["expected"]=exp_lines
                    exp_lines=""
                    logs+="</p>"
                promptlist=re.findall(prompt_re, line)
                if prompts is None:
                    for p in promptlist:
                        if p not in self.prompts:
                            self.prompts.append(p)

                prompt = promptlist[0]
                lc = re.split(re.escape(prompt),line)

                if len(lc)>1:
                    for command in lc:
                        if len(command):
                            index+=1

                            self.commands_line_indices.append(index)
                            current_command = command
                            self.commands_dict[index]=dict()
                            self.commands_dict[index]["command"]=command

                            self.commands_dict[index]["prompt"] = prompt
                            self.commands_dict[index]["line_index"] = line_index
                            line = '<p id="c%s"><code class="prompt">%s</code> <code id="c%s" class="command">%s</code></p>'%(index,prompt,index,command)
                            logs+=line + "<br/>"
                            line_index+=1

            else:
                header=""
                if len(exp_lines)==0:
                    header='<p id="o%s" class="output_line">'%(index)
                exp_lines+=line+"\n"
                logs+=header + line + "<br/>"
                line_index+=1
                
            
        self.sshLog = logs
        return self.sshLog
    
    def getCommandList(self):
        return self.commands
    
    def detect_prompt(self,text):
        self.prompts = re.findall(r'\[.*@.* .+\][#\$]', text)
    