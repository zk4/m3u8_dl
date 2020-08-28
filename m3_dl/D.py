#coding: utf-8

import os
from io import BytesIO
import requests
import traceback
import logging
import time
import threading
from .progress2 import  pb2
logger = logging.getLogger(__name__)


def userDefineVisual(  tag, nowValue, fullValue,extrainfo):
    percent = float(nowValue) / fullValue
    icons="🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛✅"
    icons_len=len(icons)
    s="%3d%%" % int(round(percent * 100)) if fullValue != nowValue else "    "
    return    f"{tag} {icons[nowValue%(icons_len-1)] if fullValue!=nowValue else icons[-1]} {s} {extrainfo.rjust(15)}"

class D():

    def __init__(self, cookie    = None, proxies = None,headers = None,verify = True,debug = False,ignore_local = False,retry_times = 9999999999) -> None:
        self.cookie              = cookie
        self.proxies             = proxies
        self.headers             = headers
        self.ignore_local        = ignore_local
        self.retry_times         = retry_times
        self.current_retry_times = 0
        self.verify              = verify
        self.debug               = debug
        super().__init__()

    def download(self, url, destFile, isAppend=True):
        try:
            if not os.path.isdir(os.path.dirname(destFile)):
                    os.mkdir(os.path.dirname(destFile))
            

            if os.path.exists(destFile):
                return True

            webSize = self.getWebFileSize(url)
            if webSize == 0:
                logger.debug("something went wrong, webSize is 0")
                return False

            localSize = 0
            if self.cookie:
                self.headers['cookie']=self.cookie

            if isAppend:
                self.headers['Range']='bytes=%d-' % localSize
            else:
                os.remove(destFile)
                localSize=0

            resp = requests.request("GET", url,timeout=10, headers=self.headers, stream=True, proxies=self.proxies, allow_redirects=True,verify=self.verify)
            # if 300>resp.status_code >= 200:
            if resp.status_code>=200:
                # logger.debug(f"stauts_code:{resp.status_code},destfile:{destFile}")

                name = threading.current_thread().getName()
                p = pb2.getSingleton()
                start=time.time()
                with open(destFile+".tmp", "ab") as f:
                    block_size = 1024
                    wrote = localSize
                    for data in resp.iter_content(block_size):
                        if data:
                            wrote = wrote + len(data)
                            f.write(data)
                            p.update(name.rjust(13,' '), wrote, webSize,str(int(wrote/(int(time.time()-start)+1)/1024)) +"kb/s",userDefineVisual)
                    if wrote != webSize:
                        logger.debug(f"ERROR, something went wrong wroteSize{wrote} != webSize{webSize}")
                        return False

                os.rename(destFile+".tmp",destFile)
                return True

            logger.debug(f"stauts_code:{resp.status_code},url:{resp.url}") 
            raise Exception("status_code is not 200.") 

        except Exception as e:
            if self.debug:
                logger.exception(e)
            # traceback.print_stack()
            return False

    def getWebFileSize(self, url):
        if self.cookie:
            self.headers['cookie']=self.cookie

        rr = requests.get(url, headers=self.headers, stream=True, proxies=self.proxies, verify=self.verify)
        file_size = int(rr.headers['Content-Length'])

        if 300>rr.status_code>=200:
            return file_size
        else:
            return 0
