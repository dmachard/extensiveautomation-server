#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# This file is part of the extensive testing project
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
# -------------------------------------------------------------------

import TestInteropLib
from TestInteropLib import doc_public

from pysphere import * 
from pysphere.resources import VimService_services as VI

class VSphere(TestInteropLib.InteropPlugin):
    """
    VSphere plugin
    Sample on /Samples/Tests_Interop/05_VSphere
    """
    @doc_public
    def __init__(self, parent, host, login, password ):
        """
        VSphere interop
        
        @param parent: testcase parent
        @type parent: testcase
        
        @param host: esx url api
        @type host: string
        
        @param login: login for api
        @type login: string
        
        @param password: password for api
        @type passord: string     
        """
        TestInteropLib.InteropPlugin.__init__(self, parent)
        
        self.__host = host
        self.__login = login
        self.__password = password
        self.__connected = False
        self.__server = VIServer()
    @doc_public
    def server(self):
        """
        Return the server instance
        """
        return self.__server
    @doc_public    
    def connect(self):
        """
        Connect to the vsphere server

        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False

        # log message
        content = {'vsphere-host': self.__host, 'login':"%s" % self.__login, 'cmd': 'connect' }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="connect", details=tpl )
        
        try:
            self.__server.connect(self.__host, self.__login , self.__password) 
            
            self.__connected = True
            ret = True
            
            # log message
            serverType = self.__server.get_server_type()
            serverVersion = self.__server.get_api_version()
            
            content = {'vsphere-type': serverType, 'vsphere-version': serverVersion, 'cmd': 'connect' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="connected", details=tpl )

        except Exception as e:  # log message
            content = { "vsphere-error": "%s" % e, "cmd": "connect" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="connect error", details=tpl )

        return ret
    @doc_public    
    def disconnect(self):
        """
        Disconnect from the vsphere server
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if not self.__connected: 
            return ret

        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'disconnect' }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="disconnect", details=tpl )
        
        try:
            self.__server.disconnect() 
            
            # log message
            content = { 'cmd': 'disconnect' }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="disconnect", details=tpl )
                
            ret = True
            self.__connected = False
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "disconnect" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="disconnect error", details=tpl )
            
        return ret
    @doc_public    
    def cloneVm(self, fromVm, toVm, toFolder, datastore=None):
        """
        Clone a vm
        
        @param fromVm: the virtual machine to clone
        @type fromVm: string
        
        @param toVm: the destination virtual machine name
        @type toVm: string
        
        @param toFolder: the destination folder name
        @type toFolder: string
        
        @param datastore: the destination datastore (default=None)
        @type datastore: string/none
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if not self.__connected: 
            return ret

        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'clone-vm', 'from-vm': fromVm, 'to-vm': toVm}
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="clone vm", details=tpl )
        
        try:
            dest_res_vm = None
            rps = self.__server.get_resource_pools()
            for mor, path in rps.iteritems():
               if path == "/Resources":
                   dest_res_vm = mor
                   break
            if dest_res_vm is None: raise Exception("/Resources not found")
            
            try:
                tpl_vm = self.__server.get_vm_by_name(fromVm)
            except Exception as e:
                raise Exception("From VM %s not found!" % fromVm)

            clone = tpl_vm.clone(name=toVm, sync_run=True, folder=toFolder, 
                                resourcepool=dest_res_vm,  datastore=datastore, host=None,
                                power_on=False, template=False, snapshot=None, linked=False)
            ret = True
            
            content = { "result": "success",  "cmd": "clone-vm", 'vm-name': vmName }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="clone vm", details=tpl )
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "clone-vm" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="clone vm error", details=tpl )
        return ret
    @doc_public    
    def deleteVm(self, vmName):
        """
        Delete the vm from disk according to the name passed as argument
        
        @param vmName: name of the virtual machine to delete
        @type vmName: string
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if not self.__connected: 
            return ret

        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'delete-vm', 'vm-name': vmName}
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="delete vm", details=tpl )
        
        try:
            try:
                vm = self.__server.get_vm_by_name(vmName)
            except Exception as e:
                raise Exception("VM %s not found!" % vmName)
                
            request = VI.Destroy_TaskRequestMsg()
            _this = request.new__this(vm._mor)
            _this.set_attribute_type(vm._mor.get_attribute_type())

            request.set_element__this(_this)
            r = self.__server._proxy.Destroy_Task(request)._returnval
            task = VITask(r, self.__server)

            status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
            if status == task.STATE_ERROR:
               raise Exception("Error removing vm:", task.get_error_message())
               
            ret = True
            
            content = { "result": "success", "cmd": "delete-vm", 'vm-name': vmName }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="delete vm", details=tpl )
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "delete-vm" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="delete vm error", details=tpl )
        return ret
    @doc_public
    def statusVm(self, vmName):
        """
        Get the status of a vm according to the name passed as argument
        
        @param vmName: name of the virtual machine to start
        @type vmName: string

        @return: vm state (POWERED ON, POWERED OFF)
        @rtype: boolean
        """
        state = "UNKNOWN"
        if not self.__connected: 
            return state
            
        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'status-vm', 'vm-name': vmName}
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="status vm", details=tpl )
        
        try:
            try:
                vm = self.__server.get_vm_by_name(vmName)
            except Exception as e:
                raise Exception("VM %s not found!" % vmName)
            
            state = vm.get_status()

            content = { "status": "%s" % state, "cmd": "status-vm", 'vm-name': vmName }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="status vm", details=tpl )
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "status-vm" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="status vm error", details=tpl )
        return state
    @doc_public    
    def powerOn(self, vmName, timeoutTools=120):
        """
        Start the vm according to the name passed as argument
        
        @param vmName: name of the virtual machine to start
        @type vmName: string
        
        @param timeoutTools: wait tools ready until the end of timeout (default=120)
        @type timeoutTools: integer
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if not self.__connected: 
            return ret
            
        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'start-vm', 'vm-name': vmName}
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="start vm", details=tpl )
        
        try:
            try:
                vm = self.__server.get_vm_by_name(vmName)
            except Exception as e:
                raise Exception("VM %s not found!" % vmName)
            
            vm.power_on()
            # check if the vm is running
            if timeoutTools: vm.wait_for_tools(timeout=timeoutTools)

            ret = True
            
            content = { "result": "success", "cmd": "start-vm", 'vm-name': vmName }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="start vm", details=tpl )
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "start-vm" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="start vm error", details=tpl )
        return ret
    @doc_public   
    def powerOff(self, vmName):
        """
        Stop the vm according to the name passed as argument
        
        @param vmName: name of the virtual machine to stop
        @type vmName: string
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if not self.__connected: 
            return ret
            
        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'stop-vm', 'vm-name': vmName}
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="stop vm", details=tpl )
        
        try:
            try:
                vm = self.__server.get_vm_by_name(vmName)
            except Exception as e:
                raise Exception("VM %s not found!" % vmName)
            
            vm.power_off()
            ret = True
            
            content = { "result": "success", "cmd": "stop-vm", 'vm-name': vmName }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="stop vm", details=tpl )
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "stop-vm" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="stop vm error", details=tpl )
        return ret
    @doc_public    
    def updateName(self, vmName, newName):
        """
        Configure the name of the vm
        
        @param vmName: name of the virtual machine to rename
        @type vmName: string
        
        @param newName: new name of the vm
        @type newName: string
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if not self.__connected: 
            return ret
            
        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'configure-name', 'vm-name': vmName, 'new-name': newName}
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="configure vm name", details=tpl )
        
        try:
            try:
                vm = self.__server.get_vm_by_name(vmName)
            except Exception as e:
                raise Exception("VM %s not found!" % vmName)
            
            request = VI.ReconfigVM_TaskRequestMsg()
            _this = request.new__this(vm._mor)
            _this.set_attribute_type(vm._mor.get_attribute_type())
            request.set_element__this(_this)
            spec = request.new_spec()
           
            spec.set_element_name(newName)
            
            request.set_element_spec(spec)
            r = self.__server._proxy.ReconfigVM_Task(request)._returnval
            task = VITask(r, self.__server)
            status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
            if status != task.STATE_SUCCESS:
               raise Exception("VM update error: %s" % task.get_error_message())
               
            ret = True
            
            content = { "result": "success", "cmd": "configure-name", 'vm-name': vmName }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="configure name", details=tpl )
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "configure-name" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="configure name error", details=tpl )
        return ret
    @doc_public    
    def updateMem(self, vmName, vmMem):
        """
        Configure the memory of the vitual machine name passed as argument
        
        @param vmName: name of the virtual machine to rename
        @type vmName: string
        
        @param vmMem: virtual machine memory in MB
        @type vmMem: string
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if not self.__connected: 
            return ret
            
        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'configure-mem', 'vm-name': vmName, 'new-name': vmMem}
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="configure vm mem", details=tpl )
        
        try:
            try:
                vm = self.__server.get_vm_by_name(vmName)
            except Exception as e:
                raise Exception("VM %s not found!" % vmName)
            
            request = VI.ReconfigVM_TaskRequestMsg()
            _this = request.new__this(vm._mor)
            _this.set_attribute_type(vm._mor.get_attribute_type())
            request.set_element__this(_this)
            spec = request.new_spec()
           
            spec.set_element_memoryMB(vmMem)
            
            request.set_element_spec(spec)
            r = self.__server._proxy.ReconfigVM_Task(request)._returnval
            task = VITask(r, self.__server)
            status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
            if status != task.STATE_SUCCESS:
               raise Exception("VM update error: %s" % task.get_error_message())
               
            ret = True
            
            content = { "result": "success", "cmd": "configure-mem", 'vm-name': vmName }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="configure mem", details=tpl )
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "configure-mem" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="configure mem error", details=tpl )
        return ret
    @doc_public
    def updateCpu(self, vmName, nbCpu):
        """
        Configure the number of cpu for the virtual machine name passed as argument
        
        @param vmName: name of the virtual machine to rename
        @type vmName: string
        
        @param nbCpu: number of cpu
        @type nbCpu: integer
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if not self.__connected: 
            return ret
            
        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'configure-cpu', 'vm-name': vmName, 'nb-cpu': nbCpu}
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="configure cpu", details=tpl )
        
        try:
            try:
                vm = self.__server.get_vm_by_name(vmName)
            except Exception as e:
                raise Exception("VM %s not found!" % vmName)
            
            request = VI.ReconfigVM_TaskRequestMsg()
            _this = request.new__this(vm._mor)
            _this.set_attribute_type(vm._mor.get_attribute_type())
            request.set_element__this(_this)
            spec = request.new_spec()
           
            spec.set_element_numCPUs(nbCpu)
            
            request.set_element_spec(spec)
            r = self.__server._proxy.ReconfigVM_Task(request)._returnval
            task = VITask(r, self.__server)
            status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
            if status != task.STATE_SUCCESS:
               raise Exception("VM update error: %s" % task.get_error_message())
               
            ret = True
          
            content = { "result": "success", "cmd": "configure-cpu", 'vm-name': vmName }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="configure cpu", details=tpl )
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "configure-cpu" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="configure cpu error", details=tpl )
        return ret
    @doc_public
    def runCmd(self, vmName, vmLogin, vmPwd, cmd, args=[]):
        """
        Run system command on the virtual machine name passed as argument
        
        @param vmName: name of the virtual machine to rename
        @type vmName: string
        
        @param vmLogin: login of the system running on the virtual machine
        @type vmLogin: string
        
        @param vmPwd: password of the system running on the virtual machine
        @type vmPwd: string
       
        @param cmd: system command to execute
        @type cmd: string
       
        @param args: arguments of the command to execute
        @type args: list
        
        @return: True on success, False otherwise
        @rtype: boolean
        """
        ret = False
        if not self.__connected: 
            return ret
            
        # log message
        content = {'vsphere-host': self.__host, 'cmd': 'run-cmd', 'vm-name': vmName, 
                    'cmd': cmd, 'cmd-args': '%s' % args }
        tpl = self.template(name=self.__class__.__name__.upper(), content=content )
        self.logRequest(msg="run cmd", details=tpl )
        
        try:
            try:
                vm = self.__server.get_vm_by_name(vmName)
            except Exception as e:
                raise Exception("VM %s not found!" % vmName)
               
            vm.login_in_guest(vmLogin,vmPwd)
            pid = vm.start_process(cmd, args)
            
            ret = True
          
            content = { "result": "success", "cmd": "run-cmd", 'vm-name': vmName }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="run cmd", details=tpl )
        except Exception as e: # log message
            content = { "vsphere-error": "%s" % e, "cmd": "run-cmd" }
            tpl = self.template(name=self.__class__.__name__.upper(), content=content )
            self.logResponse(msg="run cmd error", details=tpl )
        return ret