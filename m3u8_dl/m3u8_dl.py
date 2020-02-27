#coding: utf-8

from .D  import D
from .logx import setup_logging
from concurrent.futures import ThreadPoolExecutor
from os.path import join,basename,dirname
from pathlib import Path
from urllib.parse import urljoin
import argparse
import logging
import os
import queue
import requests
import subprocess
import threading
import m3u8
import time
from Crypto.Cipher import AES
import sys

# don`t remove this line 
setup_logging()

logger = logging.getLogger(__name__)

# proxies={"https":"socks5h://127.0.0.1:5992","http":"socks5h://127.0.0.1:5992"}
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' ,
}



class m3u8_dl(object):

    def __init__(self,url,out_path,proxy):
        self.threads        = []
        pool_size           = 100
        self.proxies        = {"https":proxy,"http":proxy}
        self.url            = url
        self.is_http_url    = url.startswith("http")
        self.out_path       = out_path
        self.session        = self._get_http_session(pool_size, pool_size, 5)
        self.m3u8_content   = self.m3u8content(url)
        self.ts_list        = [urljoin(self.url, n.strip()) for n in self.m3u8_content.split('\n') if n and not n.startswith("#")]
        self.length         = len(self.ts_list)
        self.ts_list_pair   = zip(self.ts_list, [n for n in range(len(self.ts_list))])
        self.next_merged_id = 0
        self.outdir         = dirname(out_path)
        self.ready_to_merged       = set()
        self.downloadQ      = queue.Queue()

        if self.outdir and not os.path.isdir(self.outdir):
            os.makedirs(self.outdir)

        if self.out_path and os.path.isfile(self.out_path):
            os.remove(self.out_path)
        
        key = self.readkey()

        self.cryptor = None
        if key:
            self.cryptor = AES.new(key, AES.MODE_CBC, key)


    def decode(self, content):
        if self.cryptor:
            return self.cryptor.decrypt(content)
        else:
            return content

    def readkey(self):
        tag_list = [n.strip() for n in self.m3u8_content.split('\n') if n and n.startswith("#")]
        for s in tag_list:
            if str.upper(s).startswith("#EXT-X-KEY"):
                logger.debug(f'{s} found')
                segments = s[len("#EXT-X-KEY")+1:]
                if segments == "NONE":
                    return None

                [method,uri]=segments.split(",")
                method,uri = method.split('=')[1],uri.split('=')[1][1:-1]
                
                logger.debug(f'request uri: {uri}')


                uri = urljoin(self.url,uri)

                r = self.session.get(uri,proxies=self.proxies)
                return  r.content

    def _get_http_session(self, pool_connections, pool_maxsize, max_retries):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize, max_retries=max_retries) 
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session


    def m3u8content(self,m3u8_url):
        logger.debug(f"m3u8_url {m3u8_url}")
        if m3u8_url.startswith("http"):
            r = self.session.get(m3u8_url, timeout=10,headers=headers,proxies=self.proxies)
            if ":path" in r.headers:
                print(r.headers[":path"])
            if r.ok:
                ts_list = [urljoin(m3u8_url, n.strip()) for n in r.text.split('\n') if n and not n.startswith("#")]
                if ts_list[0].endswith("m3u8"):
                    self.url = urljoin(m3u8_url,ts_list[0])
                    return self.m3u8content(self.url)
                return r.text
        else:
            return Path(m3u8_url).read_text()

        raise Exception("read m3u8 content error.")

    def download(self,url,i):
        try:
            d = D(proxies=self.proxies,headers=headers)
            logger.debug(f'url:{url}')
            ret = d.download(url,join(dirname(self.out_path),str(i)))
            if ret:
                # logger.info(f'{i} done')
                self.ready_to_merged.add(i)
            else:
                logger.error(f'{i} download fails! re Q')
                self.downloadQ.put((url,i))

        except Exception as e :
            logger.exception(e)

    def target(self):
        while self.next_merged_id < self.length:
            try:
                url,idx = self.downloadQ.get(timeout=3)
                if url:
                    self.download(url,idx)
            except Exception as e:
                # logger.exception(e)
                pass

    def run(self,threadcount):
        if self.ts_list_pair:

            for i in range(threadcount):
                threading.Thread(target=self.target).start()

            threading.Thread(target=self.try_merge).start()


            for pair in self.ts_list_pair:
                self.downloadQ.put((pair[0],pair[1]))


    def try_merge(self):
            outfile  = None

            if not outfile:
                outfile = open(self.out_path, 'ab')
            while self.next_merged_id < self.length:

                logger.debug(f'{self.next_merged_id}/{self.length} merged')
                oldidx = self.next_merged_id
                try:
                    if self.next_merged_id in self.ready_to_merged:
                        self.ready_to_merged.remove(self.next_merged_id)
                        output = dirname(self.out_path)
                        p = os.path.join(output, str(self.next_merged_id))

                        infile= open(p, 'rb')
                        o  = self.decode(infile.read())

                        outfile.write(o)
                        infile.close()

                        self.next_merged_id += 1

                        outfile.flush()
                        os.remove(join(self.outdir,str(oldidx)))
                    else:
                        time.sleep(1)
                        # logger.debug(f'waiting for {self.next_merged_id} to merge ')
                        logger.debug(f'unmerged {self.ready_to_merged} active_thread:{threading.active_count()}')
                except Exception as e :
                    # logger.exception(e)
                    self.next_merged_id=oldidx
                    os.remove(join(self.outdir,str(oldidx)))
                    logger.error(f'{oldidx} merge error ,reput to thread')
                    # print(self.ts_list[oldidx],oldidx)
                    self.downloadQ.put((self.ts_list[oldidx],oldidx))
            if outfile:
                outfile.close()

def main(args):
    if args.debug:
        logger.setLevel("DEBUG")

    logger.debug(f'args.overwrite:{args.overwrite}')
    if os.path.exists(args.out_path) and not args.overwrite:
            logger.error(f'{args.out_path} exists! use -w if you want to overwrite it ')
            sys.exit(-1) 

    m = m3u8_dl(args.url,args.out_path,args.proxy)

    # must ensure 1 for merged thread
    threadcount = args.threadcount + 1
    m.run(threadcount)

def entry_point():
    parser = createParse()
    mainArgs=parser.parse_args()
    main(mainArgs)


def createParse():
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="")
    parser.add_argument("url",  help="url" )
    parser.add_argument("out_path",  help="out path" )
    parser.add_argument('-p', '--proxy',type=str,  help="proxy" ,default="socks5h://127.0.0.1:5992")
    parser.add_argument('-t', '--threadcount',type=int,  help="thread count" ,default=2)
    parser.add_argument('-d', '--debug', help='debug info', default=False, action='store_true') 
    parser.add_argument('-w', '--overwrite', help='overwrite exist file', action='store_true')  


    return parser
