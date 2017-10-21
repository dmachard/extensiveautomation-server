#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2017 Denis Machard
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

import os
import base64
import zlib
import shutil
import zipfile
import time
import scandir
try:
    # python 2.4 support
    import simplejson as json
except ImportError:
    import json

from Libs import Logger
import Context

TEST_ABSTRACT_EXT               = 'tax'
TEST_UNIT_EXT                   = 'tux'
TEST_SUITE_EXT                  = 'tsx'
TEST_PLAN_EXT                   = 'tpx'
TEST_GLOBAL_EXT                 = 'tgx'
TEST_CONFIG_EXT                 = 'tcx'
TEST_DATA_EXT                   = 'tdx'
TEST_RESULT_EXT                 = 'trx'
TEST_RESULT_VERDICT_EXT         = 'trv'
TEST_RESULT_REPORT_EXT          = 'trp'
TEST_RESULT_BASIC_REPORT_EXT    = 'tbrp'
TEST_RESULT_DESIGN_EXT          = 'trd'
TEST_RESULT_VERDICT_XML_EXT     = 'tvrx'
TEST_RESULT_REPORT_XML_EXT      = 'trpx'
TEST_RESULT_DESIGN_XML_EXT      = 'tdsx'

TXT_EXT                  = 'txt'
CAP_EXT                  = 'cap'
ZIP_EXT                  = 'zip'
PY_EXT                   = 'py'
PYO_EXT                  = 'pyo'
PYC_EXT                  = 'pyc'
LOG_EXT                  = 'log'
PNG_EXT                  = 'png'
HTML_EXT                 = 'html'
PDF_EXT                  = 'pdf'
JPG_EXT                  = 'jpg'
MP4_EXT                  = 'mp4'

class RepoManager(Logger.ClassLogger):
    """
    Repository manager
    """
    def __init__(self, pathRepo, extensionsSupported=[]):
        """
        Class repository manager
        """
        self.testsPath = pathRepo
        self.destBackup = None
        self.extensionsSupported = extensionsSupported
        
        self.trace("Extensions supported: %s" % extensionsSupported)

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="RMG - %s" % txt)

    def encodeData(self, data):
        """
        Encode data
        """
        ret = ''
        try:
            tasks_json = json.dumps(data)
        except Exception as e:
            self.error( "Unable to encode in json: %s" % str(e) )
        else:
            try: 
                tasks_zipped = zlib.compress(tasks_json)
            except Exception as e:
                self.error( "Unable to compress: %s" % str(e) )
            else:
                try: 
                    ret = base64.b64encode(tasks_zipped)
                except Exception as e:
                    self.error( "Unable to encode in base 64: %s" % str(e) )
        return ret

    def getTimestamp(self):
        """
        Converts timestamp for human-readable

        @return: date time
        @rtype: string
        """
        ret = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))  + ".%3.3d" % int((time.time() * 1000)% 1000  )
        return ret

    def bytes2human(self, n):
        """
        Converts bytes to readable size

        @type  n:
        @param n: int

        @return: human readable size
        @rtype: string
        """
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i+1)*10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.1f%s' % (value, s)
        return "%sB" % n

    def diskUsage(self, p, asDict=False):
        """
        Return the disk usage of a specific directory

        @type  p:
        @param p: string

        @return:  total/used/free
        @rtype: tuple
        """
        st = os.statvfs(p)
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        
        if asDict: return {'total': "%s" % total, 'used': "%s" % used, 'free': "%s" % free}
        return (total, used, free)

    def freeSpaceMb(self, p):
        """
        Returns the number of free MegaBytes
    
        @type  p:
        @param p: string

        @return:  size in megabytes
        @rtype: int
        """
        s = os.statvfs(p)
        return (s.f_bsize * s.f_bavail)/(1024*1024)

    def freeSpace(self, p):
        """
        Returns the number of free bytes

        @type  p:
        @param p: string

        @return:  size in bytes
        @rtype: int
        """
        statvfs = os.statvfs(p)
        return "%s" % (statvfs.f_frsize * statvfs.f_bfree) 
        
    def sizeFilesystem(self, p):
        """
        Returns the number of free bytes

        @type  p:
        @param p: string

        @return:  size in bytes
        @rtype: int
        """
        statvfs  = os.statvfs(p)
        return "%s" % (statvfs.f_frsize * statvfs.f_blocks)
    
    def zipFolder(self, folderPath, zipName, zipPath, ignoreExt=[], includeExt=[]):
        """
        Zip folder and compress it
        """
        ret = Context.CODE_ERROR
        zip_file = None
        self.trace("starting to zip folder=%s" % folderPath)

        # Retrieve the paths of the folder contents.
        contents = os.walk(folderPath)
        try:
            zip_file = zipfile.ZipFile( "%s/%s" % (zipPath,zipName), 'w', zipfile.ZIP_DEFLATED)
            for root, folders, files in contents:
                # Include all subfolders, including empty ones.
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    if not os.listdir(absolute_path): # exclude empty folder
                        continue
                    relative_path = absolute_path.replace(folderPath,'')
                    zip_file.write(absolute_path, relative_path)
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)
                    
                    ignored = False
                    for e in ignoreExt:
                        if file_name.endswith(e):
                            ignored=True
                    if ignored: 
                        continue
                    
                    if len(includeExt):
                        included = False
                        for e in includeExt:
                            if file_name.endswith(e):
                                included = True
                                break
                        if not included: 
                            continue
                        
                    relative_path = absolute_path.replace(folderPath, '')
                    zip_file.write(absolute_path, relative_path)
        except IOError as message:
            self.error( "io error: %s" % message )
            ret = Context.CODE_FORBIDDEN
            if zip_file is not None:
                zip_file.close()
        except OSError as message:
            self.error( "os error: %s" % message )
            ret = Context.CODE_FORBIDDEN
            if zip_file is not None:
                zip_file.close()
        except zipfile.BadZipfile as message:
            self.error( "bad zip file: %s" % message )
            ret = Context.CODE_FORBIDDEN
            if zip_file is not None:
                zip_file.close()
        except Exception as e:
            self.error( "generic zip error: %s" % e )
            if zip_file is not None:
                zip_file.close()
            ret = Context.CODE_ERROR
        else:
            if zip_file is not None:
                zip_file.close()
                self.trace("%s created successfully." % zipName )
                ret = Context.CODE_OK
        return ret
        
    def toZip(self, file, filename, extToInclude=[ TEST_RESULT_EXT, TXT_EXT, CAP_EXT, ZIP_EXT], 
                    fileToExclude=[], extToExclude=[], keepTree=True):
        """
        Create zip

        @type  file:
        @param file: 

        @type  filename:
        @param filename: 

        @type  extToInclude: extension file to include in the zip, empty list means "include all types of files"
        @param extToInclude: list

        @type  fileToExclude: file to exclude from the zip
        @param fileToExclude: list

        @type  extToExclude: extentsion file to exclude from the zip
        @param extToExclude: list

        @type  keepTree: keep the disk arboresence
        @param keepTree: boolean

        @return: response code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        try:
            zip_file = zipfile.ZipFile(filename, 'w')
            if os.path.isfile(file):
                zip_file.write(file)
            else:
                self.addFolderToZip(zip_file, file, extToInclude=extToInclude, fileToExclude=fileToExclude, extToExclude=extToExclude, keepTree=keepTree)
            zip_file.close()
            ret = Context.CODE_OK
        except IOError, e:
            self.trace( e )
            return Context.CODE_FORBIDDEN
        except Exception as e:
            raise Exception( "[toZip] %s" % str(e) )
        return ret

    def addFolderToZip(self, zip_file, folder, extToInclude, fileToExclude, extToExclude, keepTree=True): 
        """
        Add folder to zip

        @type  zip_file:
        @param zip_file: 

        @type  folder:
        @param folder: 

        @type  extToInclude: extension file to include in the zip, empty list means "include all types of files"
        @param extToInclude: list

        @type  fileToExclude: file to exclude from the zip
        @param fileToExclude: list

        @type  extToExclude: extentsion file to exclude from the zip
        @param extToExclude: list

        @type  keepTree: keep the disk arboresence
        @param keepTree: boolean
        """
        try:
            for file in os.listdir(folder):
                full_path = os.path.join(folder, file)
                if os.path.isfile(full_path):
                    includeFile = False
                    if len(extToInclude) == 0:
                        includeFile = True
                    for f in extToInclude:
                        if file.endswith(f):
                            includeFile = True
                    if includeFile:
                        excludeFile = False
                        for e in extToExclude:
                            if file.endswith(e):
                                excludeFile=True
                        for f in fileToExclude:
                            if file == f:
                                excludeFile = True
                        if not excludeFile:
                            if keepTree:
                                zip_file.write(full_path)
                            else:
                                zip_file.write(filename=full_path, arcname=file)
                elif os.path.isdir(full_path):
                    self.addFolderToZip(zip_file, full_path, extToInclude, fileToExclude, extToExclude, keepTree)
        except IOError, e:
            raise IOError(e)
        except Exception as e:
            raise Exception( "[addFolderToZip] %s" % str(e) )

    def getSizeRepoV2(self, folder):
        """
        Returns the size of a specific folder
        With scandir function, better perf

        @type  folder: folder path
        @param folder: string

        @return: folder size
        @rtype: int
        """
        total = 0
        try:
            for entry in scandir.scandir(folder):
                if entry.is_dir(follow_symlinks=False):
                    total += self.getSizeRepoV2(folder=entry.path)
                else:
                    total += entry.stat(follow_symlinks=False).st_size
        except Exception as e:
            self.error( e )
        return total
        
    def sorted_ls(self, path):
        """
        Sorted as ls command
        """
        mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
        return list(sorted(os.listdir(path), key=mtime))

    def getListingFilesV2(self, path, extensionsSupported=[], nbDirs=None, project=0, supportSnapshot=False, archiveMode=False):
        """
        New listing file with generator
        
        """
        nbFolders = 0
        nbFiles = 0
        content = []
        statistics = {}
        try:
            statistics = { 'disk-usage': self.diskUsage(p=path, asDict=True) }
            for entry in reversed( list( sorted(scandir.scandir(path), key=lambda m:m.name) ) ):
                if entry.is_dir(follow_symlinks=False) and not entry.name.startswith(".") :
                    nbFolders += 1
                    
                    folderName = entry.name.decode("utf-8")
                    
                    # new in v16, to fix the issue file name too long
                    if archiveMode:
                        virtualFolderName=""
                        res = os.path.exists( "%s/TESTPATH" % (entry.path) )
                        if res:
                            try:
                                f = open( "%s/TESTPATH" % (entry.path) , 'r' )
                                newFolderName = f.read().strip()
                                if len(newFolderName): 
                                    folderNameList = entry.name.split(".")
                                    folderNameList[2] = base64.b64encode(newFolderName.encode("utf8"))
                                    virtualFolderName = ".".join(folderNameList)
                                f.close()
                            except Exception as e:
                                continue
                    # end of new 
                    
                    d_nbFolders, d_nbFiles, d_content, d_statistics = self.getListingFilesV2( entry.path, extensionsSupported, 
                                                                                                nbDirs, project, supportSnapshot,
                                                                                             archiveMode=archiveMode)
                    
                    folderDescr = {
                                        "type": "folder", "name": folderName, "content": d_content,
                                        'size': entry.stat(follow_symlinks=False).st_size,
                                        'modification': entry.stat(follow_symlinks=False).st_mtime, 
                                        'nb-folders': str(d_nbFolders), 'nb-files': str(d_nbFiles), 'project': "%s" % project
                                    }
                                    
                    # new in v16
                    if archiveMode:
                        if len(virtualFolderName):
                            folderDescr["virtual-name"] = virtualFolderName
                    # end of new
                    
                    content.append(folderDescr)
                    
                    nbFolders += d_nbFolders
                    nbFiles += d_nbFiles
                    for d_key, d_value in d_statistics.items():
                        if d_key == 'disk-usage': continue
                        if d_key not in statistics:
                            statistics[d_key] = d_value
                        else:
                            statistics[d_key]['nb'] += d_value['nb']
                            statistics[d_key]['total'] += d_value['total']
                            if d_value['max'] > statistics[d_key]['max']: statistics[d_key]['max'] = d_value['max']
                            if d_value['min'] < statistics[d_key]['min']: statistics[d_key]['min'] = d_value['min']
                                
                    # max loop
                    if nbDirs is not None:
                        if nbFolders >= nbDirs:
                            break
                else:
                    extSupported = []
                    if len(extensionsSupported) > 0:  extSupported = extensionsSupported
                    else: extSupported = self.extensionsSupported
                    
                    if entry.name.lower().endswith( tuple(extSupported) ) and not entry.name.startswith(".") :
                        nbFiles += 1
                        sizeFile = entry.stat(follow_symlinks=False).st_size
                        dictFile = { "type": "file", "name": entry.name.decode("utf-8"), 'size': "%s" % sizeFile,
                                     'modification': entry.stat(follow_symlinks=False).st_mtime, 'project': "%s" % project }
                        ext = entry.name.rsplit(".", 1)[1]
                        ext = ext.lower()
                        # new in v11.3
                        if ext not in statistics:
                            statistics[ext] = { 'nb': 1, 'min': sizeFile, 'max': sizeFile, 'total': sizeFile }
                        else:
                            statistics[ext]['nb'] += 1
                            statistics[ext]['total'] += sizeFile
                            if sizeFile > statistics[ext]['max']: statistics[ext]['max'] = sizeFile
                            if sizeFile < statistics[ext]['min']: statistics[ext]['min'] = sizeFile
                        # end of new
                        
                        if supportSnapshot:
                            dictFile['snapshots'] = self.listSnapshotsV2(currentPath=path, currentFile=entry.name)
                        content.append( dictFile )
                            
        except Exception as e:
            self.error( e )
        return ( nbFolders, nbFiles, content, statistics )

    def listSnapshotsV2(self, currentPath, currentFile):
        """
        List snapshots in the current folder
        """
        ret = []
        for file in scandir.scandir(currentPath):
            if file.name.lower().endswith(".snapshot") and file.name.startswith(currentFile):
                snapName, snapExt = file.name.rsplit(".", 2)[1:]
                dictSnap = { 'name': "%s.%s" % (base64.b64decode(snapName), snapExt), 'realname': file.name }
                ret.append( dictSnap )
        return ret
        
    def getFile(self, pathFile, binaryMode=True, project='', addLock=True, login='', forceOpen=False, readOnly=False, projectsList=[]):
        """
        Returns the content of the file gived in argument

        @param pathFile: 
        @type pathFile:

        @param binaryMode: 
        @type binaryMode: boolean

        @param addLock: lock support
        @type addLock: boolean

        @return: 
        @rtype: list
        """
        try:
            # read the file
            self.trace( "get file ProjectId=%s FilePath=%s LockSupport=%s ForceOpen=%s ReadOnly=%s" % 
                        (project, pathFile, addLock, forceOpen, readOnly) )
            
            # extract filename, extension and path file
            ext_file = str(pathFile).rsplit(".", 1)[1]
            path_file = str(pathFile).rsplit("/", 1)[0]
            if len( str(pathFile).rsplit("/", 1) ) > 1:
                name_file = str(pathFile).rsplit("/", 1)[1].rsplit(".", 1)[0]
            else:
                path_file = ""
                name_file = str(pathFile).rsplit(".", 1)[0]
                
            # prepare lock file path
            is_locked = False
            locked_by = ''
            lockPath = "%s/%s/%s/.%s.%s.lock" % (self.testsPath, project, path_file, name_file, ext_file)
            
            if not forceOpen:
                if os.path.exists( lockPath ): 
                    is_locked=True
                    fd_lock = open(lockPath, 'r')
                    locked_by = fd_lock.read()
                    fd_lock.close()
                    
                    # cancel lock when login
                    if base64.b64encode(login) ==  locked_by:
                        is_locked = False
                        locked_by = ''
            
            if is_locked and not forceOpen and addLock and not readOnly:
                return [ Context.CODE_LOCKED, path_file, name_file, ext_file, base64.b64encode(""), project, (is_locked,locked_by) ]
                
            # open the file in binary mode ? yes by default
            if binaryMode:
                f = open( "%s/%s/%s" % (self.testsPath, project, pathFile), 'rb')
            else:
                f = open( "%s/%s/%s" % (self.testsPath, project, pathFile), 'r')
                
            # read the content, encode in base64 and return it
            data_read = f.read()
            ret =  [ Context.CODE_OK, path_file, name_file, ext_file, base64.b64encode(data_read), project, (is_locked,locked_by) ]
            f.close()
            
            # create lock file only if activated
            if addLock and not readOnly:
                if ext_file.lower() not in [PNG_EXT, ZIP_EXT, CAP_EXT, PDF_EXT]:
                    self.trace("creating lock file for FilePath=%s" % pathFile)
                    fd_lock = open(lockPath, 'w')
                    fd_lock.write(base64.b64encode(login))
                    fd_lock.close()
        except IOError as e:
            self.error( e )
            ret =  [ Context.CODE_FORBIDDEN, False, False, False, False, False, (False,'') ]
        except Exception as e:
            self.error( e )
            ret =  [ Context.CODE_NOT_FOUND, False, False, False, False, False, (False,'') ]
        return ret
        
    def getBackup(self, pathFile, binaryMode=True, project=''):
        """
        Returns the content of the backp gived in argument

        @param pathFile: 
        @type pathFile:

        @param binaryMode: 
        @type binaryMode: boolean

        @param forTs: 
        @type forTs:

        @return: 
        @rtype: list
        """
        if self.destBackup is None:
            return
        try:
            self.trace( "get backup ProjectId=%s FilePath=%s" % (project, pathFile) )
            ext_file = str(pathFile).rsplit(".", 1)[1]
            path_file = str(pathFile).rsplit("/", 1)[0]
            if len( str(pathFile).rsplit("/", 1) ) > 1:
                name_file = str(pathFile).rsplit("/", 1)[1].rsplit(".", 1)[0]
            else:
                path_file = ""
                name_file = str(pathFile).rsplit(".", 1)[0]
            if binaryMode:
                f = open( "%s/%s/%s" % (self.destBackup, project, pathFile), 'rb')
            else:
                f = open( "%s/%s/%s" % (self.destBackup, project, pathFile), 'r')
            data_read = f.read()
            ret =  [ Context.CODE_OK, path_file, name_file, ext_file, base64.b64encode(data_read), project ]
            f.close()
        except Exception as e:
            self.error( e )
            ret =  [ Context.CODE_NOT_FOUND, False, False, False, False, False ]
        return ret
        
    def importFile(self, pathFile, nameFile, extFile, contentFile, binaryMode=True, project='', makeDirs=False):
        """
        Save data in the file passed in argument

        @param pathFile: 
        @type pathFile:

        @param nameFile: 
        @type nameFile:

        @param extFile: 
        @type extFile:

        @param contentFile: file content in base64
        @type contentFile:

        @param updateFile: 
        @type updateFile:

        @param binaryMode: 
        @type binaryMode:

        @return: 
        @rtype: list
        """
        try:
            if extFile.lower() not in [ PY_EXT, PNG_EXT, TXT_EXT, TEST_UNIT_EXT, TEST_SUITE_EXT, 
                                    TEST_PLAN_EXT, TEST_GLOBAL_EXT, TEST_CONFIG_EXT, TEST_DATA_EXT]:
                raise Exception('Extension: %s not supported!' % extFile)

            if len(pathFile) > 0:
                complete_path = "%s/%s/%s/%s.%s" % (self.testsPath, project, pathFile, nameFile, extFile)
            else:
                complete_path = "%s/%s/%s.%s" % (self.testsPath, project, nameFile, extFile)
            self.trace( "importing file %s" % complete_path  ) 
            res = os.path.exists( complete_path )
            if res:
                return ( Context.CODE_ALLREADY_EXISTS, pathFile, nameFile, extFile, project )
            
            # create missing directory
            if makeDirs:
                folderPath = "%s/%s/%s/" % (self.testsPath, project, pathFile)
                if not os.path.exists( folderPath ):
                    os.makedirs(folderPath)
                
            # decode the content
            content_decoded = base64.b64decode(contentFile)
            
            # write the file
            if binaryMode:
                f = open( complete_path, 'wb')
            else:
                f = open( complete_path, 'w')
            f.write( content_decoded )
            f.close()
            
            ret = (  Context.CODE_OK, pathFile, nameFile, extFile, project )
        except Exception as e:
            self.error( e )
            ret = (  Context.CODE_ERROR, False, False, False, project)
        return ret
        
    def unlockFile(self, pathFile, nameFile, extFile, project='', login=''):
        """
        Save data in the file passed in argument

        @param pathFile: 
        @type pathFile:

        @param nameFile: 
        @type nameFile:

        @param extFile: 
        @type extFile:

        @param contentFile: 
        @type contentFile:

        @param updateFile: 
        @type updateFile:

        @param binaryMode: 
        @type binaryMode:

        @return: 
        @rtype: list
        """
        ret = Context.CODE_OK
        try:
            completepath = "%s/%s/%s/.%s.%s.lock" % ( self.testsPath, project, unicode(pathFile), nameFile, extFile )
            
            self.trace( "trying to unlock file=%s" % completepath )
            res = os.path.exists( completepath )
            if res:
                fd_lock = open(completepath, 'r')
                locked_by = fd_lock.read()
                fd_lock.close()
                if base64.b64encode(login) == locked_by:
                    os.remove( completepath )
                    self.trace( "unlocked file=%s" % completepath )
        except Exception as e:
            self.error( "unable to unlock file: %s" % e )
            ret = Context.CODE_ERROR
        return ret

    def putFile(self, pathFile, nameFile, extFile, contentFile, updateFile, binaryMode=True,
                        project='', closeAfter=False, login=''):
        """
        Save data in the file passed in argument

        @param pathFile: 
        @type pathFile:

        @param nameFile: 
        @type nameFile:

        @param extFile: 
        @type extFile:

        @param contentFile: 
        @type contentFile:

        @param updateFile: 
        @type updateFile:

        @param binaryMode: 
        @type binaryMode:

        @return: 
        @rtype: list
        """
        try:
            lockedBy = ''
        
            if extFile.lower() not in [ PY_EXT, PNG_EXT, TXT_EXT, TEST_ABSTRACT_EXT, TEST_UNIT_EXT, TEST_SUITE_EXT, TEST_PLAN_EXT,
                                        TEST_GLOBAL_EXT, TEST_CONFIG_EXT, TEST_DATA_EXT]:
                raise Exception('Extension: %s not supported!' % extFile)

            # prepare path files
            if len(pathFile) > 0:
                lockPath = "%s/%s/%s/.%s.%s.lock" % (self.testsPath, project, pathFile, nameFile, extFile)
                complete_path = "%s/%s/%s/%s.%s" % (self.testsPath, project, pathFile, nameFile, extFile)
            else:
                complete_path = "%s/%s/%s.%s" % (self.testsPath, project, nameFile, extFile)
                lockPath = "%s/%s/.%s.%s.lock" % (self.testsPath, project,  nameFile, extFile)
            
            
            self.trace( "putting file %s" % complete_path  ) 
            if not updateFile:
                res = os.path.exists( complete_path )
                if res:
                    return ( Context.CODE_ALLREADY_EXISTS, pathFile, nameFile, extFile, 
                                updateFile, project, closeAfter, lockedBy )

            # refuse to save if a lock already exist with a diffent login name
            is_locked = False
            if os.path.exists( lockPath ): 
                is_locked=True
                fd_lock = open(lockPath, 'r')
                lockedBy = fd_lock.read()
                fd_lock.close()
                
                # cancel lock when login
                if base64.b64encode(login) !=  lockedBy:
                    return ( Context.CODE_LOCKED, pathFile, nameFile, extFile, 
                                updateFile, project, closeAfter, lockedBy )
                    
            # decode the content and save it in the file
            content_decoded = base64.b64decode(contentFile)
            if binaryMode:
                f = open( complete_path, 'wb')
            else:
                f = open( complete_path, 'w')
            f.write( content_decoded )
            f.close()
            
            ret = (  Context.CODE_OK, pathFile, nameFile, extFile, updateFile, project, closeAfter, lockedBy )
        except Exception as e:
            self.error( e )
            ret = (  Context.CODE_ERROR, False, False, False, False, project, closeAfter, lockedBy)
        return ret

    def addDir(self, pathFolder, folderName, project=''):
        """
        Add directory in the repository

        @param pathFolder: 
        @type pathFolder:

        @param folderName: 
        @type folderName:

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        try:
            if str(pathFolder) != "":
                completepath = "%s/%s/%s/%s" % ( self.testsPath, project, unicode(pathFolder) , unicode(folderName ) )
            else:
                completepath = "%s/%s/%s" % ( self.testsPath, project, unicode(folderName) )
            self.trace( "adding folder %s" %completepath )
            res = os.path.exists( completepath )
            if res:
                return Context.CODE_ALLREADY_EXISTS
            else:
                os.mkdir( completepath, 0755 )
                return Context.CODE_OK
        except Exception as e:
            self.error( e )
            return ret
        return ret

    def delDir(self, pathFolder, project=''):
        """
        Delete the folder gived in argument

        @param pathFolder: 
        @type pathFolder:

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        try:
            completepath = "%s/%s/%s/" % ( self.testsPath, project, unicode(pathFolder) )
            completepath = os.path.normpath(completepath)
            self.trace( "deleting folder %s" % completepath )
            res = os.path.exists( completepath )
            if not res:
                return Context.CODE_NOT_FOUND
            else:
                os.rmdir( completepath )
                return Context.CODE_OK
        except OSError, e:
            self.trace( e )
            return Context.CODE_FORBIDDEN
        except Exception as e:
            self.error( e )
            return ret
        return ret

    def delDirAll(self, pathFolder, project=''):
        """
        Delete the folder gived in argument and all sub folders

        @param pathFolder: 
        @type pathFolder:

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        try:
            completepath = "%s/%s/%s/" % ( self.testsPath, project, unicode(pathFolder) )
            completepath = os.path.normpath(completepath)
            self.trace( "deleting all folders %s" % completepath )
            res = os.path.exists( completepath )
            if not res:
                return Context.CODE_NOT_FOUND
            else:
                shutil.rmtree( completepath )
                return Context.CODE_OK
        except OSError, e:
            self.trace( e )
            return Context.CODE_FORBIDDEN
        except Exception as e:
            self.error( e )
            return ret
        return ret
    
    def emptyRepo(self, projectId=1):
        """
        Removes all files/folders on the repository

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        try:
            self.trace( "%s/%s" % (self.testsPath, projectId) )
            files=os.listdir( "%s/%s" % (self.testsPath, projectId) )
            for x in files:
                fullpath=os.path.join( "%s/%s" % (self.testsPath, projectId), x)
                if os.path.isfile(fullpath):
                    os.remove( fullpath )
                else:
                    shutil.rmtree( fullpath )
            return Context.CODE_OK
        except OSError, e:
            self.trace( e )
            return Context.CODE_FORBIDDEN
        except Exception as e:
            raise Exception( e )
            return ret
        return ret

    def renameDir(self, mainPath, oldPath, newPath, project=''):
        """
        Rename the folder gived in argument

        @param mainPath: 
        @type mainPath:

        @param oldPath: 
        @type oldPath:

        @param newPath: 
        @type newPath:

        @return:
        @rtype: tuple
        """
        if not len(newPath):
            self.error( "empty folder name" )
            return (Context.CODE_ERROR, mainPath, oldPath, newPath, project )
        try:
            oldpath = "%s/%s/%s/%s/" % ( self.testsPath, project, mainPath, unicode(oldPath) )
            newpath = "%s/%s/%s/%s/" % ( self.testsPath, project, mainPath, unicode(newPath) )

            self.trace( "renaming folder %s to  %s" % ( oldpath,newpath ) )
            res = os.path.exists( oldpath )
            if not res:
                return ( Context.CODE_NOT_FOUND, mainPath, oldPath, newPath, project )
            else:
                res = os.path.exists( newpath )
                if res:
                    return ( Context.CODE_ALLREADY_EXISTS, mainPath, oldPath, newPath, project)
                else:
                    os.rename( oldpath, newpath )
                    return ( Context.CODE_OK, mainPath, oldPath, newPath, project )
        except Exception as e:
            self.error( e )
            return (Context.CODE_ERROR, mainPath, oldPath, newPath, project )

    def duplicateDir(self, mainPath, oldPath, newPath, project='', newProject='', newMainPath=''):
        """
        Duplicate the folder gived in argument

        @param mainPath: 
        @type mainPath:

        @param oldPath: 
        @type oldPath:

        @param newPath: 
        @type newPath:

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        if len( "%s" % project) and not len("%s" % newProject):
            self.error( "empty project name" )
            return Context.CODE_ERROR
        try:
            oldpath = "%s/%s/%s/%s/" % ( self.testsPath, project, mainPath, unicode(oldPath) )
            newpath = "%s/%s/%s/%s/" % ( self.testsPath, newProject, newMainPath, unicode(newPath) )

            self.trace( "duplicating folder %s to  %s" % ( oldpath,newpath ) )
            res = os.path.exists( oldpath )
            if not res:
                return Context.CODE_NOT_FOUND
            else:
                res = os.path.exists( newpath )
                if res:
                    return Context.CODE_ALLREADY_EXISTS
                else:
                    shutil.copytree( oldpath, newpath )
                    return Context.CODE_OK
        except Exception as e:
            self.error( e )
            return Context.CODE_ERROR

    def delFile(self, pathFile, project='', supportSnapshot=False):
        """
        Delete the file gived in argument

        @param pathFile: 
        @type pathFile:

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        try:
            completepath = "%s/%s/%s" % ( self.testsPath, project, unicode(pathFile) )
            self.trace( "deleting %s" % completepath )
            res = os.path.exists( completepath )
            if not res:
                return Context.CODE_NOT_FOUND
            else:
                os.remove( completepath )
                
                # remove all snapshot, new in v11
                if supportSnapshot:
                    self.trace( "deleting snapshots too")
                    currentPath, currentName = completepath.rsplit("/", 1)
                    for file in os.listdir(currentPath):
                        if file.endswith(".snapshot") and file.startswith(currentName):
                            os.remove( "%s/%s" % (currentPath, file) )
                    self.trace( "snapshots deleted too")
                # end of new in v11
                
                return Context.CODE_OK
        except OSError, e:
            self.trace( e )
            return Context.CODE_FAILED
        except Exception as e:
            self.error( e )
            return ret
        return ret

    def renameFile(self, mainPath, oldFilename, newFilename, extFilename, project='', supportSnapshot=False):
        """
        Rename the file gived in argument

        @param mainPath: 
        @type mainPath:

        @param oldFilename: 
        @type oldFilename:

        @param newFilename: 
        @type newFilename:

        @param extFilename: 
        @type extFilename:

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        if not len(newFilename):
            self.error( "empty filename" )
            return ( Context.CODE_ERROR, mainPath, oldFilename, newFilename, extFilename, project)
        try:
            oldpath = "%s/%s/%s/%s.%s" % ( self.testsPath, project, mainPath, unicode(oldFilename), extFilename )
            newpath = "%s/%s/%s/%s.%s" % ( self.testsPath, project, mainPath, unicode(newFilename), extFilename )

            self.trace( "renaming %s to  %s" % ( oldpath,newpath ) )
            res = os.path.exists( oldpath )
            if not res:
                return ( Context.CODE_NOT_FOUND, mainPath, oldFilename, newFilename, extFilename, project)
            else:
                res = os.path.exists( newpath )
                if res:
                    return ( Context.CODE_ALLREADY_EXISTS, mainPath, oldFilename, newFilename, extFilename, project )
                else:
                    os.rename( oldpath, newpath )

                    # remove all snapshot, new in v11
                    if supportSnapshot:
                        self.trace( "renaming snapshots too")
                        # detect snapshots
                        snapshotsDetected = []
                        for file in os.listdir( "%s/%s/%s/" % ( self.testsPath, project, mainPath) ):
                            if file.endswith(".snapshot") and file.startswith(oldFilename):
                                snapshotsDetected.append( file )
                                
                        # renaming all
                        for snap in snapshotsDetected:
                            oldpathSnap = "%s/%s/%s/%s" % ( self.testsPath, project, mainPath, snap)
                            newSnap = snap.replace(oldFilename, newFilename)
                            newpathSnap = "%s/%s/%s/%s" % ( self.testsPath, project, mainPath, newSnap)
                            os.rename( oldpathSnap, newpathSnap )
                        self.trace( "snapshots renamed too")    
                    # end of new in v11
                    
                    return ( Context.CODE_OK, mainPath, oldFilename, newFilename, extFilename, project)
        except IOError as e:
            self.error( "io error: %s" % e )
            return ( Context.CODE_FORBIDDEN, mainPath, oldFilename, newFilename, extFilename, project)
        except Exception as e:
            self.error( "generic error: %s" %  e )
            return ( Context.CODE_ERROR, mainPath, oldFilename, newFilename, extFilename, project)
        return ret

    def duplicateFile(self, mainPath, oldFilename, newFilename, extFilename, project='', newProject='', newMainPath=''):
        """
        Duplicate the file gived in argument

        @param mainPath: 
        @type mainPath:

        @param oldFilename: 
        @type oldFilename:

        @param newFilename: 
        @type newFilename:

        @param extFilename: 
        @type extFilename:

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        try:
            oldpath = "%s/%s/%s/%s.%s" % ( self.testsPath, project, mainPath, unicode(oldFilename), extFilename )
            newpath = "%s/%s/%s/%s.%s" % ( self.testsPath, newProject, newMainPath, unicode(newFilename), extFilename )

            self.trace( "duplicating %s to  %s" % ( oldpath,newpath ) )
            res = os.path.exists( oldpath )
            if not res:
                return Context.CODE_NOT_FOUND
            else:
                res = os.path.exists( newpath )
                if res:
                    return Context.CODE_ALLREADY_EXISTS
                else:
                    shutil.copy( oldpath, newpath )
                    return Context.CODE_OK
        except Exception as e:
            self.error( e )
            return ret
        return ret

    def moveDir(self, mainPath, folderName, newPath, project='', newProject=''):
        """
        Move the file gived in argument

        @param mainPath: 
        @type mainPath:

        @param fileName: 
        @type fileName:

        @param newPath: 
        @type newPath:

        @param extFilename: 
        @type extFilename:

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        if not len(folderName):
            self.error( "empty folder name" )
            return ( Context.CODE_ERROR, mainPath, folderName, newPath, project)
        if len("%s" % project) and not len("%s" % newProject):
            self.error( "empty project name" )
            return ( Context.CODE_ERROR, mainPath, folderName, newPath, project)
        
        try:
            oldpath = "%s/%s/%s/%s/" % ( self.testsPath, project, mainPath, unicode(folderName) )
            newpath = "%s/%s/%s/%s/" % ( self.testsPath, newProject, newPath, unicode(folderName) )
    
            # begin issue 248
            if "%s/%s" % (mainPath,unicode(folderName)) == newPath:
                return ( Context.CODE_ALLREADY_EXISTS, mainPath, folderName, newPath, project )
            # end issue 248

            self.trace( "moving folder %s in  %s" % ( oldpath,newpath ) )
            res = os.path.exists( oldpath )
            if not res:
                return ( Context.CODE_NOT_FOUND, mainPath, folderName, newPath, project)
            else:
                res = os.path.exists( newpath )
                if res:
                    self.trace( "the destination already exists" )
                    return ( Context.CODE_ALLREADY_EXISTS, mainPath, folderName, newPath, project )
                else:
                    # duplicate folder
                    shutil.copytree( oldpath, newpath )
                    # remove old
                    shutil.rmtree( oldpath )
                    return ( Context.CODE_OK, mainPath, folderName, newPath, project)
        except Exception as e:
            self.error( e )
            return ( Context.CODE_ERROR, mainPath, folderName, newPath, project)

    def moveFile(self, mainPath, fileName, extFilename, newPath, project='', newProject='', supportSnapshot=False):
        """
        Move the file gived in argument

        @param mainPath: 
        @type mainPath:

        @param fileName: 
        @type fileName:

        @param newPath: 
        @type newPath:

        @param extFilename: 
        @type extFilename:

        @return: respone code
        @rtype: int
        """
        ret = Context.CODE_ERROR
        try:
            oldpath = "%s/%s/%s/%s.%s" % ( self.testsPath, project, mainPath, unicode(fileName), extFilename )
            newpath = "%s/%s/%s/%s.%s" % ( self.testsPath, newProject, newPath, unicode(fileName), extFilename )

            self.trace( "moving file from %s to %s" % ( oldpath,newpath ) )
            res = os.path.exists( oldpath )
            if not res:
                return ( Context.CODE_NOT_FOUND, mainPath, fileName, newPath, extFilename, project)
            else:
                res = os.path.exists( newpath )
                if res:
                    self.trace( "test name already exists in the destination" )
                    return ( Context.CODE_ALLREADY_EXISTS, mainPath, fileName, newPath, extFilename, project )
                else:
                    shutil.move( oldpath, newpath )
                    
                    # remove all snapshot, new in v11
                    if supportSnapshot:
                        self.trace( "moving snapshots too")
                        # detect snapshots
                        snapshotsDetected = []
                        for file in os.listdir( "%s/%s/%s/" % ( self.testsPath, project, mainPath) ):
                            if file.endswith(".snapshot") and file.startswith(fileName):
                                snapshotsDetected.append( file )
                                
                        # moving all
                        for snap in snapshotsDetected:
                            oldpathSnap = "%s/%s/%s/%s" % ( self.testsPath, project, mainPath, snap)
                            newpathSnap = "%s/%s/%s/%s" % ( self.testsPath, project, newPath, snap)
                            shutil.move( oldpathSnap, newpathSnap )
                        self.trace( "snapshots moved too")    
                    # end of new in v11
                    
                    return ( Context.CODE_OK, mainPath, fileName, newPath, extFilename, project)
        except Exception as e:
            self.error( e )
            return ret
        return ret


###############################
RepoMng = None
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return RepoMng

def initialize ():
    """
    Instance creation
    """
    global RepoMng
    RepoMng = RepoManager()

def finalize ():
    """
    Destruction of the singleton
    """
    global RepoMng
    if RepoMng:
        RepoMng = None