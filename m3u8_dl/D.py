#coding: utf-8

import os
from io import BytesIO
import requests
from tqdm import tqdm
import logging
logger = logging.getLogger(__name__)


class D():

    def __init__(self, cookie=None, proxies=None,headers=None,retry_times=999999) -> None:
        self.cookie = cookie
        self.proxies = proxies
        self.headers=headers
        self.retry_times = retry_times
        self.current_retry_times = 0
        super().__init__()

    def download(self, url, destFile, isAppend=True):
        logger.debug(f'download: {url}')
        try:
            localSize = 0
            webSize = self.getWebFileSize(url)
            if webSize == 0:
                logger.debug("something went wrong, webSize is 0")
                return
            try:
                localSize = os.stat(destFile).st_size
                if localSize == webSize:
                    logger.debug(f"{destFile} local exist! file size is the same:{webSize}")
                    return
                else:
                    logger.debug(f"{destFile} file size isn`t in consistence,localSize:{localSize}   webSize:{webSize} redownload..")

            except FileNotFoundError as e:
                logger.exception(e)


            if self.cookie:
                self.headers['cookie']=self.cookie
            if isAppend:
                self.headers['Range']='bytes=%d-' % localSize
            else:
                os.remove(destFile)
                localSize=0

            resp = requests.request("GET", url, headers=self.headers, stream=True, proxies=self.proxies, allow_redirects=True)
            # if 300>resp.status_code >= 200:
            if resp.status_code>=200:
                logger.debug(f"stauts_code:{resp.status_code},url:{resp.url}")
                total_size = resp.headers.get('content-length', 0)
                logger.debug("total size:" + total_size)
                with open(destFile, "ab") as f:
                    block_size = 1024
                    wrote = localSize
                    for data in tqdm(resp.iter_content(block_size), initial=wrote / block_size, total=webSize / block_size,unit='Mb', unit_scale=True):
                        if data:
                            wrote = wrote + len(data)
                            f.write(data)
                    if wrote != webSize:
                        logger.debug(f"ERROR, something went wrong wroteSize{wrote} != webSize{webSize}")
                    else:
                        return
            else:
                logger.debug(f"stauts_code:{resp.status_code},url:{resp.url}") 
        except Exception as e:
                logger.exception(e)

        if self.current_retry_times<self.retry_times:
            self.current_retry_times+=1
            self.download(url,destFile,isAppend)


    def getWebFileSize(self, url):
        if self.cookie:
            self.headers['cookie']=self.cookie
        rr = requests.get(url, headers=self.headers, stream=True, proxies=self.proxies)
        file_size = int(rr.headers['Content-Length'])
        if 300>rr.status_code>=200:
            return file_size
        else:
            raise Exception(f"网络错误码:{rr.status_code} \n{rr.text}")
