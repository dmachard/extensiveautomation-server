#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2020 Denis Machard
# This file is part of the extensive automation project
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

from ea.libs import Logger
import os
import base64
import shutil
import zipfile
import platform
try:
    import scandir
except ImportError:  # for python3 support
    scandir = os
import sys

import lxml                                                                     
from lxml import etree 

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


TEST_YAML_EXT = 'yml'
    
TEST_UNIT_EXT = 'tux'
TEST_SUITE_EXT = 'tsx'
TEST_PLAN_EXT = 'tpx'
TEST_GLOBAL_EXT = 'tgx'
TEST_CONFIG_EXT = 'tcx'
TEST_DATA_EXT = 'tdx'
TEST_RESULT_EXT = 'trx'
TEST_RESULT_VERDICT_EXT = 'trv'
TEST_RESULT_REPORT_EXT = 'trp'
TEST_RESULT_BASIC_REPORT_EXT = 'tbrp'
TEST_RESULT_DESIGN_EXT = 'trd'
TEST_RESULT_VERDICT_XML_EXT = 'tvrx'
TEST_RESULT_REPORT_XML_EXT = 'trpx'
TEST_RESULT_DESIGN_XML_EXT = 'tdsx'

TXT_EXT = 'txt'
CAP_EXT = 'cap'
ZIP_EXT = 'zip'
PY_EXT = 'py'
PYO_EXT = 'pyo'
PYC_EXT = 'pyc'
LOG_EXT = 'log'
PNG_EXT = 'png'
HTML_EXT = 'html'
PDF_EXT = 'pdf'
JPG_EXT = 'jpg'
MP4_EXT = 'mp4'


class RepoManager(Logger.ClassLogger):
    """
    Repository manager
    """

    def __init__(self, pathRepo, extensionsSupported=[], context=None):
        """
        Class repository manager
        """
        self.context = context
        self.testsPath = pathRepo
        self.extensionsSupported = extensionsSupported

        self.trace("Extensions supported: %s" % extensionsSupported)

    def diskUsage(self, p, asDict=False):
        """
        Return the disk usage of a specific directory
        """
        if platform.system() == "Windows":
            total = 0
            used = 0
            free = 0
        else:
            st = os.statvfs(p)
            free = st.f_bavail * st.f_frsize
            total = st.f_blocks * st.f_frsize
            used = (st.f_blocks - st.f_bfree) * st.f_frsize

        if asDict:
            return {'total': "%s" % total,
                    'used': "%s" % used, 'free': "%s" % free}
        return (total, used, free)

    def freeSpace(self, p):
        """
        Returns the number of free bytes
        Function used to check the space left on disk before to run a new test
        """
        if platform.system() == "Windows":
            return "0"
        else:
            statvfs = os.statvfs(p)
            return "%s" % (statvfs.f_frsize * statvfs.f_bfree)

    def zipFolder(self, folderPath, zipName, zipPath,
                  ignoreExt=[], includeExt=[]):
        """
        Zip folder and compress it
        """
        ret = self.context.CODE_ERROR
        zip_file = None
        self.trace("starting to zip folder=%s" % folderPath)

        # Retrieve the paths of the folder contents.
        contents = os.walk(folderPath)
        try:
            zip_file = zipfile.ZipFile(
                "%s/%s" %
                (zipPath, zipName), 'w', zipfile.ZIP_DEFLATED)
            for root, folders, files in contents:
                # Include all subfolders, including empty ones.
                for folder_name in folders:
                    absolute_path = os.path.join(root, folder_name)
                    if not os.listdir(absolute_path):  # exclude empty folder
                        continue
                    relative_path = absolute_path.replace(folderPath, '')
                    zip_file.write(absolute_path, relative_path)
                for file_name in files:
                    absolute_path = os.path.join(root, file_name)

                    ignored = False
                    for e in ignoreExt:
                        if file_name.endswith(e):
                            ignored = True
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
            self.error("io error: %s" % message)
            ret = self.context.CODE_FORBIDDEN
            if zip_file is not None:
                zip_file.close()
        except OSError as message:
            self.error("os error: %s" % message)
            ret = self.context.CODE_FORBIDDEN
            if zip_file is not None:
                zip_file.close()
        except zipfile.BadZipfile as message:
            self.error("bad zip file: %s" % message)
            ret = self.context.CODE_FORBIDDEN
            if zip_file is not None:
                zip_file.close()
        except Exception as e:
            self.error("generic zip error: %s" % e)
            if zip_file is not None:
                zip_file.close()
            ret = self.context.CODE_ERROR
        else:
            if zip_file is not None:
                zip_file.close()
                self.trace("%s created successfully." % zipName)
                ret = self.context.CODE_OK
        return ret

    def __getBasicListing(self, testPath, initialPath):
        """
        """
        listing = []
        for entry in list(scandir.scandir(testPath)):
            if not entry.is_dir(follow_symlinks=False):
                filePath = entry.path
                listing.append(filePath.split(initialPath)[1])
            else:
                listing.extend(self.__getBasicListing(testPath=entry.path,
                                                      initialPath=initialPath))
        return listing

    def getBasicListing(self, projectId=''):
        """
        """
        listing = []
        initialPath = "%s/%s" % (self.testsPath, projectId)
        for entry in list(scandir.scandir(initialPath)):
            if not entry.is_dir(follow_symlinks=False):
                filePath = entry.path
                listing.append(filePath.split(initialPath)[1])
            else:
                listing.extend(self.__getBasicListing(testPath=entry.path,
                                                      initialPath=initialPath))
        return listing

    def __getDictListing(self, folder_path, parent_id):
        """
        """
        item_id = 0
        listing = {}
        for entry in list(scandir.scandir(folder_path)):
            # parse folders
            if entry.is_dir(follow_symlinks=False):
                # ignore some folders
                if entry.name == "__pycache__":
                    continue
                if entry.name.startswith("."):
                    continue

                item_id += 1
                listing["%s%s" % (parent_id, item_id)] = {"type": "folder",
                                                          "name": entry.name,
                                                          "parent-id": "%s" % parent_id}

                new_listing = self.__getDictListing(folder_path=entry.path,
                                                    parent_id="%s%s" % (parent_id, item_id))
                listing.update(new_listing)

            # parse files
            else:
                if entry.name.startswith("."):
                    continue

                item_id += 1
                file_name, file_ext = os.path.splitext(entry.name)
                file_ext = file_ext[1:]
                listing["%s%s" % (parent_id, item_id)] = {"type": "file",
                                                          "name": file_name,
                                                          "parent-id": "%s" % parent_id,
                                                          "extension": file_ext}

        return listing

    def getDictListing(self, projectId=''):
        """
        """
        item_id = 0
        parent_id = 0
        listing = {}

        initial_path = "%s/%s" % (self.testsPath, projectId)
        for entry in list(scandir.scandir(initial_path)):
            # parse folders
            if entry.is_dir(follow_symlinks=False):
                # ignore some folders
                if entry.name == "__pycache__":
                    continue
                if entry.name.startswith("."):
                    continue

                item_id += 1
                listing["0%s" % item_id] = {"type": "folder",
                                            "name": entry.name,
                                            "parent-id": "%s0" % parent_id}

                new_listing = self.__getDictListing(folder_path=entry.path,
                                                    parent_id="0%s" % item_id)
                listing.update(new_listing)

            # parse files
            else:
                if entry.name.startswith("."):
                    continue

                item_id += 1
                file_name, file_ext = os.path.splitext(entry.name)
                file_ext = file_ext[1:]
                listing["0%s" % item_id] = {"type": "file",
                                            "name": file_name,
                                            "parent-id": "%s0" % parent_id,
                                            "extension": file_ext}

        return listing

    def getSizeRepoV2(self, folder):
        """
        Returns the size of a specific folder
        With scandir function, better perf
        """
        total = 0
        try:
            for entry in scandir.scandir(folder):
                if entry.is_dir(follow_symlinks=False):
                    total += self.getSizeRepoV2(folder=entry.path)
                else:
                    total += entry.stat(follow_symlinks=False).st_size
        except Exception as e:
            self.error(e)
        return total

    def getListingFilesV2(self, path, extensionsSupported=[], nbDirs=None, project=0,
                          supportSnapshot=False, archiveMode=False, folderIgnored=None):
        """
        New listing file with generator
        """
        nbFolders = 0
        nbFiles = 0
        content = []
        statistics = {}
        try:
            statistics = {'disk-usage': self.diskUsage(p=path, asDict=True)}
            for entry in reversed(
                    list(sorted(scandir.scandir(path), key=lambda m: m.name))):
                if entry.is_dir(
                        follow_symlinks=False) and not entry.name.startswith("."):

                    # ignore python folder
                    if entry.name == "__pycache__":
                        continue
                    if folderIgnored is not None:
                        folderignored_matched = False
                        for fld in folderIgnored:
                            if entry.name == fld:
                                folderignored_matched = True
                        if folderignored_matched:
                            continue

                    nbFolders += 1

                    if sys.version_info > (3,):
                        folderName = entry.name
                    else:
                        folderName = entry.name.decode("utf-8")

                    # get the testresult name
                    if archiveMode:
                        virtualFolderName = None
                        res = os.path.exists("%s/TESTPATH" % (entry.path))
                        if res:
                            try:
                                f = open("%s/TESTPATH" % (entry.path), 'r')
                                newFolderName = f.read().strip()
                                if len(newFolderName):
                                    folderNameList = entry.name.split(".")
                                    b64_folder_name = base64.b64encode(
                                        newFolderName.encode("utf8"))

                                    if sys.version_info > (3,):
                                        b64_folder_name = b64_folder_name.decode(
                                            "utf8")

                                    folderNameList[2] = b64_folder_name
                                    virtualFolderName = ".".join(
                                        folderNameList)
                                    del folderNameList
                                del newFolderName
                                f.close()
                            except Exception as e:
                                self.error("virtual folder name: %s" % e)
                                continue

                    d_nbFolders, d_nbFiles, d_content, d_statistics = self.getListingFilesV2(entry.path, extensionsSupported,
                                                                                             nbDirs, project, supportSnapshot,
                                                                                             archiveMode=archiveMode,
                                                                                             folderIgnored=folderIgnored)

                    folderDescr = {
                        "type": "folder", "name": folderName, "content": d_content,
                        'size': entry.stat(follow_symlinks=False).st_size,
                        'modification': entry.stat(follow_symlinks=False).st_mtime,
                        'nb-folders': str(d_nbFolders), 'nb-files': str(d_nbFiles),
                        'project': "%s" % project
                    }
                    if archiveMode:
                        if virtualFolderName is not None:
                            folderDescr["virtual-name"] = virtualFolderName

                    content.append(folderDescr)

                    nbFolders += d_nbFolders
                    nbFiles += d_nbFiles
                    for d_key, d_value in d_statistics.items():
                        if d_key == 'disk-usage':
                            continue
                        if d_key not in statistics:
                            statistics[d_key] = d_value
                        else:
                            statistics[d_key]['nb'] += d_value['nb']
                            statistics[d_key]['total'] += d_value['total']
                            if d_value['max'] > statistics[d_key]['max']:
                                statistics[d_key]['max'] = d_value['max']
                            if d_value['min'] < statistics[d_key]['min']:
                                statistics[d_key]['min'] = d_value['min']

                    # max loop
                    if nbDirs is not None:
                        if nbFolders >= nbDirs:
                            break
                else:
                    extSupported = []
                    if len(extensionsSupported) > 0:
                        extSupported = extensionsSupported
                    else:
                        extSupported = self.extensionsSupported

                    if entry.name.lower().endswith(tuple(extSupported)
                                                   ) and not entry.name.startswith("."):
                        nbFiles += 1
                        sizeFile = entry.stat(follow_symlinks=False).st_size

                        if sys.version_info > (3,):
                            fileName = entry.name
                        else:
                            fileName = entry.name.decode("utf-8")
                        dictFile = {"type": "file", "name": fileName,
                                    'size': "%s" % sizeFile,
                                    'modification': entry.stat(follow_symlinks=False).st_mtime,
                                    'project': "%s" % project}
                        ext = entry.name.rsplit(".", 1)[1]
                        ext = ext.lower()
                        # new in v11.3
                        if ext not in statistics:
                            statistics[ext] = {
                                'nb': 1, 'min': sizeFile, 'max': sizeFile, 'total': sizeFile}
                        else:
                            statistics[ext]['nb'] += 1
                            statistics[ext]['total'] += sizeFile
                            if sizeFile > statistics[ext]['max']:
                                statistics[ext]['max'] = sizeFile
                            if sizeFile < statistics[ext]['min']:
                                statistics[ext]['min'] = sizeFile
                        # end of new

                        content.append(dictFile)

        except Exception as e:
            self.error(e)
        return (nbFolders, nbFiles, content, statistics)

    def getFile(self, pathFile, binaryMode=True, project='', addLock=True, login='',
                forceOpen=False, readOnly=False, b64encode=True):
        """
        Returns the content of the file gived in argument
        """
        # read the file
        self.trace("get file ProjectId=%s FilePath=%s LockSupport=%s ForceOpen=%s ReadOnly=%s" %
                   (project, pathFile, addLock, forceOpen, readOnly))

        # extract filename, extension and path file
        path_tmp, ext_file = os.path.splitext(pathFile)
        ext_file = ext_file.replace(".", "")
        path_file = os.path.dirname(path_tmp)
        if len(path_file) == 1:
            path_file = ""  # path_file = /
        name_file = os.path.basename(path_tmp)

        ret = (path_file, name_file, ext_file, project)
        try:
            # prepare lock file path
            is_locked = False
            locked_by = ''
            lockPath = "%s/%s/%s/.%s.%s.lock" % (self.testsPath,
                                                 project,
                                                 path_file,
                                                 name_file,
                                                 ext_file)

            if sys.version_info > (3,):
                b64login = base64.b64encode(bytes(login, "utf8"))
                b64login = b64login.decode("utf8")
            else:
                b64login = base64.b64encode(login)

            if not forceOpen:
                if os.path.exists(lockPath):
                    is_locked = True
                    fd_lock = open(lockPath, 'r')
                    locked_by = fd_lock.read()
                    fd_lock.close()

                    # cancel lock when login
                    if b64login == locked_by:
                        is_locked = False
                        locked_by = ''

            if is_locked and not forceOpen and addLock and not readOnly:
                return (self.context.CODE_OK,) + ret + ("", is_locked, locked_by)

            # open the file in binary mode ? yes by default
            if binaryMode:
                f = open( "%s/%s/%s" % (self.testsPath, project, pathFile), 'rb')
            else:
                f = open("%s/%s/%s" % (self.testsPath, project, pathFile), 'r')

            # read the content, encode in base64 and return it
            data_read = f.read()
            f.close()

            # create lock file only if activated
            if addLock and not readOnly:
                if ext_file.lower() not in [
                        PNG_EXT, ZIP_EXT, CAP_EXT, PDF_EXT]:
                    self.trace("creating lock file for FilePath=%s" % pathFile)
                    fd_lock = open(lockPath, 'w')
                    fd_lock.write(b64login)
                    fd_lock.close()

            if b64encode:
                b64file = base64.b64encode(data_read)
                if sys.version_info > (3,):
                    b64file = b64file.decode("utf8")
            else:
                b64file = data_read
            return (self.context.CODE_OK,) + ret + (b64file, is_locked, locked_by)
        except IOError as e:
            self.error("io: %s" % e)
            return (self.context.CODE_FORBIDDEN,) + ret + ('', False, '')
        except Exception as e:
            self.error("general: %s" % e)
            return (self.context.CODE_NOT_FOUND,) + ret + ('', False, '')

    def uploadFile(self, pathFile, nameFile, extFile, contentFile, login='', project='',
                   overwriteFile=False, createFolders=False, lockMode=False,
                   binaryMode=True, closeAfter=False):
        """
        """
        ret = (pathFile, nameFile, extFile, project, overwriteFile, closeAfter)
        lockedBy = ''
        is_locked = False
        try:
            # checking extension
            if extFile.lower() not in [PY_EXT,
                                       PNG_EXT,
                                       TXT_EXT,
                                       TEST_UNIT_EXT,
                                       TEST_SUITE_EXT,
                                       TEST_PLAN_EXT,
                                       TEST_GLOBAL_EXT,
                                       TEST_CONFIG_EXT,
                                       TEST_DATA_EXT,
                                       TEST_YAML_EXT]:
                return (self.context.CODE_FORBIDDEN,) + \
                    ret + (is_locked, lockedBy,)

            # prepare path files
            if len(pathFile) > 0:
                lockPath = "%s/%s/%s/.%s.%s.lock" % (self.testsPath,
                                                     project,
                                                     pathFile,
                                                     nameFile,
                                                     extFile)
                complete_path = "%s/%s/%s/%s.%s" % (self.testsPath,
                                                    project,
                                                    pathFile,
                                                    nameFile,
                                                    extFile)
            else:
                complete_path = "%s/%s/%s.%s" % (self.testsPath,
                                                 project,
                                                 nameFile,
                                                 extFile)
                lockPath = "%s/%s/.%s.%s.lock" % (self.testsPath,
                                                  project,
                                                  nameFile,
                                                  extFile)

            # normalize the path
            complete_path = os.path.normpath(complete_path)
            lockPath = os.path.normpath(lockPath)

            # refuse to save if a lock already exist with a diffent login name
            if lockMode:
                if os.path.exists(lockPath):
                    is_locked = True
                    fd_lock = open(lockPath, 'r')
                    lockedBy = fd_lock.read()
                    fd_lock.close()

                    if sys.version_info > (3,):
                        b64login = base64.b64encode(bytes(login, "utf8"))
                        b64login = b64login.decode("utf8")
                    else:
                        b64login = base64.b64encode(login)

                    # cancel lock when login
                    if b64login != lockedBy:
                        return (self.context.CODE_OK,) + \
                            ret + (is_locked, lockedBy,)

            # create missing directory
            if createFolders:
                folderPath = "%s/%s/%s/" % (self.testsPath, project, pathFile)
                if not os.path.exists(folderPath):
                    os.makedirs(folderPath)

            # overwrite the file ?
            if not overwriteFile:
                if os.path.exists(complete_path):
                    return (self.context.CODE_ALREADY_EXISTS,) + \
                        ret + (is_locked, lockedBy,)

            # write the file
            content_decoded = base64.b64decode(contentFile)
            if binaryMode:
                f = open(complete_path, 'wb')
            else:
                f = open(complete_path, 'w')

            f.write(content_decoded)
            
            
            f.close()

            return (self.context.CODE_OK,) + ret + (is_locked, lockedBy,)

        except Exception as e:
            self.error(e)
            return (self.context.CODE_ERROR,) + ret + (is_locked, lockedBy,)

    def unlockFile(self, pathFile, nameFile, extFile, project='', login=''):
        """
        Save data in the file passed in argument
        """
        ret = self.context.CODE_OK
        try:
            completepath = "%s/%s/%s/.%s.%s.lock" % (self.testsPath,
                                                     project,
                                                     unicode(pathFile),
                                                     nameFile,
                                                     extFile)

            # normalize the path
            completepath = os.path.normpath(completepath)

            self.trace("trying to unlock file=%s" % completepath)
            res = os.path.exists(completepath)
            if res:
                fd_lock = open(completepath, 'r')
                locked_by = fd_lock.read()
                fd_lock.close()

                if sys.version_info > (3,):
                    b64login = base64.b64encode(bytes(login, "utf8"))
                    b64login = b64login.decode("utf8")
                else:
                    b64login = base64.b64encode(login)
                if b64login == locked_by:
                    os.remove(completepath)
                    self.trace("unlocked file=%s" % completepath)
        except Exception as e:
            self.error("unable to unlock file: %s" % e)
            ret = self.context.CODE_ERROR
        return ret

    def addDir(self, pathFolder, folderName, project=''):
        """
        Add directory in the repository
        """
        ret = self.context.CODE_ERROR
        try:
            if str(pathFolder) != "":
                completepath = "%s/%s/%s/%s" % (self.testsPath,
                                                project,
                                                unicode(pathFolder),
                                                unicode(folderName))
            else:
                completepath = "%s/%s/%s" % (self.testsPath,
                                             project, unicode(folderName))

            # normalize the path
            completepath = os.path.normpath(completepath)

            self.trace("adding folder %s" % completepath)
            res = os.path.exists(completepath)
            if res:
                return self.context.CODE_ALREADY_EXISTS
            else:
                os.mkdir(completepath, 0o755)
                return self.context.CODE_OK
        except Exception as e:
            self.error(e)
            return ret
        return ret

    def delDir(self, pathFolder, project=''):
        """
        Delete the folder gived in argument
        """
        ret = self.context.CODE_ERROR
        try:
            completepath = "%s/%s/%s/" % (self.testsPath,
                                          project,
                                          unicode(pathFolder))

            # normalize the path
            completepath = os.path.normpath(completepath)

            self.trace("deleting folder %s" % completepath)
            res = os.path.exists(completepath)
            if not res:
                return self.context.CODE_NOT_FOUND
            else:
                os.rmdir(completepath)
                return self.context.CODE_OK
        except OSError as e:
            self.trace(e)
            return self.context.CODE_FORBIDDEN
        except Exception as e:
            self.error(e)
            return ret
        return ret

    def delDirAll(self, pathFolder, project=''):
        """
        Delete the folder gived in argument and all sub folders
        """
        ret = self.context.CODE_ERROR
        try:
            completepath = "%s/%s/%s/" % (self.testsPath,
                                          project,
                                          unicode(pathFolder))

            # normalize the path
            completepath = os.path.normpath(completepath)

            self.trace("deleting all folders %s" % completepath)
            res = os.path.exists(completepath)
            if not res:
                return self.context.CODE_NOT_FOUND
            else:
                shutil.rmtree(completepath)
                return self.context.CODE_OK
        except OSError as e:
            self.trace(e)
            return self.context.CODE_FORBIDDEN
        except Exception as e:
            self.error(e)
            return ret
        return ret

    def emptyRepo(self, projectId=1):
        """
        Removes all files/folders on the repository
        """
        ret = self.context.CODE_ERROR
        try:
            self.trace("%s/%s" % (self.testsPath, projectId))
            files = os.listdir("%s/%s" % (self.testsPath, projectId))
            for x in files:
                fullpath = os.path.join(
                    "%s/%s" %
                    (self.testsPath, projectId), x)
                if os.path.isfile(fullpath):
                    os.remove(fullpath)
                else:
                    shutil.rmtree(fullpath)
            return self.context.CODE_OK
        except OSError as e:
            self.trace(e)
            return self.context.CODE_FORBIDDEN
        except Exception as e:
            raise Exception(e)
            return ret
        return ret

    def renameDir(self, mainPath, oldPath, newPath, project=''):
        """
        Rename the folder gived in argument
        """
        if not len(newPath):
            self.error("empty folder name")
            return (self.context.CODE_ERROR, mainPath,
                    oldPath, newPath, project)
        try:
            oldpath = "%s/%s/%s/%s/" % (self.testsPath,
                                        project,
                                        mainPath,
                                        unicode(oldPath))
            newpath = "%s/%s/%s/%s/" % (self.testsPath,
                                        project,
                                        mainPath,
                                        unicode(newPath))

            oldpath = os.path.normpath(oldpath)
            newpath = os.path.normpath(newpath)

            self.trace("renaming folder %s to  %s" % (oldpath, newpath))
            res = os.path.exists(oldpath)
            if not res:
                return (self.context.CODE_NOT_FOUND,
                        mainPath, oldPath, newPath, project)
            else:
                res = os.path.exists(newpath)
                if res:
                    return (self.context.CODE_ALREADY_EXISTS,
                            mainPath,
                            oldPath,
                            newPath,
                            project)
                else:
                    os.rename(oldpath, newpath)
                    return (self.context.CODE_OK, mainPath,
                            oldPath, newPath, project)
        except Exception as e:
            self.error(e)
            return (self.context.CODE_ERROR, mainPath,
                    oldPath, newPath, project)

    def duplicateDir(self, mainPath, oldPath, newPath,
                     project='', newProject='', newMainPath=''):
        """
        Duplicate the folder gived in argument
        """
        if len("%s" % project) and not len("%s" % newProject):
            self.error("empty project name")
            return self.context.CODE_ERROR
        try:
            oldpath = "%s/%s/%s/%s/" % (self.testsPath,
                                        project,
                                        mainPath,
                                        unicode(oldPath))
            newpath = "%s/%s/%s/%s/" % (self.testsPath,
                                        newProject,
                                        newMainPath,
                                        unicode(newPath))

            oldpath = os.path.normpath(oldpath)
            newpath = os.path.normpath(newpath)

            self.trace("duplicating folder %s to  %s" % (oldpath, newpath))
            res = os.path.exists(oldpath)
            if not res:
                return self.context.CODE_NOT_FOUND
            else:
                res = os.path.exists(newpath)
                if res:
                    return self.context.CODE_ALREADY_EXISTS
                else:
                    shutil.copytree(oldpath, newpath)
                    return self.context.CODE_OK
        except Exception as e:
            self.error(e)
            return self.context.CODE_ERROR

    def delFile(self, pathFile, project='', supportSnapshot=False):
        """
        Delete the file gived in argument
        """
        ret = self.context.CODE_ERROR
        try:
            completepath = "%s/%s/%s" % (self.testsPath,
                                         project,
                                         unicode(pathFile))

            # normalize the path
            completepath = os.path.normpath(completepath)

            self.trace("deleting %s" % completepath)
            res = os.path.exists(completepath)
            if not res:
                return self.context.CODE_NOT_FOUND
            else:
                os.remove(completepath)

                return self.context.CODE_OK
        except OSError as e:
            self.trace(e)
            return self.context.CODE_FAILED
        except Exception as e:
            self.error(e)
            return ret
        return ret

    def renameFile(self, mainPath, oldFilename, newFilename,
                   extFilename, project='', supportSnapshot=False):
        """
        Rename the file gived in argument
        """
        ret = self.context.CODE_ERROR
        if not len(newFilename):
            self.error("empty filename")
            return (self.context.CODE_ERROR, mainPath, oldFilename,
                    newFilename, extFilename, project)
        try:
            oldpath = "%s/%s/%s/%s.%s" % (self.testsPath,
                                          project,
                                          mainPath,
                                          unicode(oldFilename),
                                          extFilename)
            newpath = "%s/%s/%s/%s.%s" % (self.testsPath,
                                          project,
                                          mainPath,
                                          unicode(newFilename),
                                          extFilename)

            oldpath = os.path.normpath(oldpath)
            newpath = os.path.normpath(newpath)

            self.trace("renaming %s to  %s" % (oldpath, newpath))
            res = os.path.exists(oldpath)
            if not res:
                return (self.context.CODE_NOT_FOUND, mainPath, oldFilename,
                        newFilename, extFilename, project)
            else:
                res = os.path.exists(newpath)
                if res:
                    return (self.context.CODE_ALREADY_EXISTS, mainPath, oldFilename,
                            newFilename, extFilename, project)
                else:
                    os.rename(oldpath, newpath)

                    return (self.context.CODE_OK, mainPath, oldFilename,
                            newFilename, extFilename, project)
        except IOError as e:
            self.error("io error: %s" % e)
            return (self.context.CODE_FORBIDDEN, mainPath, oldFilename,
                    newFilename, extFilename, project)
        except Exception as e:
            self.error("generic error: %s" % e)
            return (self.context.CODE_ERROR, mainPath, oldFilename,
                    newFilename, extFilename, project)
        return ret

    def duplicateFile(self, mainPath, oldFilename, newFilename, extFilename,
                      project='', newProject='', newMainPath=''):
        """
        Duplicate the file gived in argument
        """
        ret = self.context.CODE_ERROR
        try:
            oldpath = "%s/%s/%s/%s.%s" % (self.testsPath,
                                          project,
                                          mainPath,
                                          unicode(oldFilename),
                                          extFilename)
            newpath = "%s/%s/%s/%s.%s" % (self.testsPath,
                                          newProject,
                                          newMainPath,
                                          unicode(newFilename),
                                          extFilename)

            oldpath = os.path.normpath(oldpath)
            newpath = os.path.normpath(newpath)

            self.trace("duplicating %s to  %s" % (oldpath, newpath))
            res = os.path.exists(oldpath)
            if not res:
                return self.context.CODE_NOT_FOUND
            else:
                res = os.path.exists(newpath)
                if res:
                    return self.context.CODE_ALREADY_EXISTS
                else:
                    shutil.copy(oldpath, newpath)
                    return self.context.CODE_OK
        except Exception as e:
            self.error(e)
            return ret
        return ret

    def moveDir(self, mainPath, folderName,
                newPath, project='', newProject=''):
        """
        Move the file gived in argument
        """
        if not len(folderName):
            self.error("empty folder name")
            return (self.context.CODE_ERROR, mainPath,
                    folderName, newPath, project)
        if len("%s" % project) and not len("%s" % newProject):
            self.error("empty project name")
            return (self.context.CODE_ERROR, mainPath,
                    folderName, newPath, project)

        try:
            oldpath = "%s/%s/%s/%s/" % (self.testsPath,
                                        project,
                                        mainPath,
                                        unicode(folderName))
            newpath = "%s/%s/%s/%s/" % (self.testsPath,
                                        newProject,
                                        newPath,
                                        unicode(folderName))

            oldpath = os.path.normpath(oldpath)
            newpath = os.path.normpath(newpath)

            # begin issue 248
            if "%s/%s" % (mainPath, unicode(folderName)) == newPath:
                return (self.context.CODE_ALREADY_EXISTS,
                        mainPath, folderName, newPath, project)
            # end issue 248

            self.trace("moving folder %s in  %s" % (oldpath, newpath))
            res = os.path.exists(oldpath)
            if not res:
                return (self.context.CODE_NOT_FOUND, mainPath,
                        folderName, newPath, project)
            else:
                res = os.path.exists(newpath)
                if res:
                    self.trace("the destination already exists")
                    return (self.context.CODE_ALREADY_EXISTS,
                            mainPath, folderName, newPath, project)
                else:
                    # duplicate folder
                    shutil.copytree(oldpath, newpath)
                    # remove old
                    shutil.rmtree(oldpath)
                    return (self.context.CODE_OK, mainPath,
                            folderName, newPath, project)
        except Exception as e:
            self.error(e)
            return (self.context.CODE_ERROR, mainPath,
                    folderName, newPath, project)

    def moveFile(self, mainPath, fileName, extFilename, newPath, project='',
                 newProject='', supportSnapshot=False):
        """
        Move the file gived in argument
        """
        ret = self.context.CODE_ERROR
        try:
            oldpath = "%s/%s/%s/%s.%s" % (self.testsPath,
                                          project,
                                          mainPath,
                                          unicode(fileName),
                                          extFilename)
            newpath = "%s/%s/%s/%s.%s" % (self.testsPath,
                                          newProject,
                                          newPath,
                                          unicode(fileName),
                                          extFilename)

            oldpath = os.path.normpath(oldpath)
            newpath = os.path.normpath(newpath)

            self.trace("moving file from %s to %s" % (oldpath, newpath))
            res = os.path.exists(oldpath)
            if not res:
                return (self.context.CODE_NOT_FOUND, mainPath, fileName,
                        newPath, extFilename, project)
            else:
                res = os.path.exists(newpath)
                if res:
                    self.trace("test name already exists in the destination")
                    return (self.context.CODE_ALREADY_EXISTS, mainPath, fileName,
                            newPath, extFilename, project)
                else:
                    shutil.move(oldpath, newpath)

                    return (self.context.CODE_OK, mainPath, fileName,
                            newPath, extFilename, project)
        except Exception as e:
            self.error(e)
            return ret
        return ret


RepoMng = None


def instance():
    """
    Returns the singleton
    """
    return RepoMng


def initialize(context):
    """
    Instance creation
    """
    global RepoMng
    RepoMng = RepoManager(context=context)


def finalize():
    """
    Destruction of the singleton
    """
    global RepoMng
    if RepoMng:
        RepoMng = None
