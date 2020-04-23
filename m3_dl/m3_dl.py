#coding: utf-8

from concurrent.futures import ThreadPoolExecutor
from os.path import join,basename,dirname
from pathlib import Path
from urllib.parse import urljoin
import argparse
import logging
import os
import random
import queue
import requests
import subprocess
import threading
import tempfile
import uuid
import time
from Crypto.Cipher import AES
import sys
from .progress2 import  pb2

# don`t show verfication warning
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)



from .D  import D,userDefineVisual
from .logx import setup_logging

# don`t remove this line 
setup_logging()

logger = logging.getLogger(__name__)

# proxies={"https":"socks5h://127.0.0.1:5992","http":"socks5h://127.0.0.1:5992"}
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' ,
}

def userDefineVisual2(tag, nowValue, fullValue,extrainfo):
    bar_length = 100
    percent = float(nowValue) / fullValue
    arrow = '#' * int(round(percent * bar_length) - 1) + '#'
    spaces = ' ' * (bar_length - len(arrow))
    return "{2} [{0}] {1}%".format(arrow + spaces, int(round(percent * 100)), tag)



class m3u8_dl(object):

    def __init__(self,url,out_path,proxy,not_verify_ssl,custom_key,debug):
        pool_size           = 10
        self.proxies        = {"https":proxy,"http":proxy}
        self.verify         = not not_verify_ssl
        self.url            = url
        self.is_http_url    = url.startswith("http")
        self.out_path       = out_path
        self.session        = self._get_http_session(pool_size, pool_size, 5)
        self.m3u8_content   = self.m3u8content(url)
        self.ts_list        = [urljoin(self.url, n.strip()) for n in self.m3u8_content.split('\n') if n and not n.startswith("#")]
        self.length         = len(self.ts_list)
        self.ts_list_pair   = zip(self.ts_list, [n for n in range(len(self.ts_list))])
        self.next_merged_id = 0
        self.ready_to_merged= set()
        self.downloadQ      = queue.PriorityQueue()
        self.tempdir        = tempfile.gettempdir()
        # self.tempdir        = "/Users/zk/git/pythonPrj/m3u8_dl/temp/"
        self.tempname       = str(uuid.uuid4())
        self.debug          = debug

        if self.out_path:
            outdir              = dirname(out_path)
            if outdir and not os.path.isdir(outdir):
                os.makedirs(outdir)

            if self.out_path and os.path.isfile(self.out_path):
                os.remove(self.out_path)

        key = self.readkey() if not custom_key else custom_key

        self.cryptor = None
        if key:
            logger.debug(f'key: {key}')
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

                logger.debug(f'segments:{segments}')
                segments_splited = segments.split(",")
                # [method,uri]=segments.split(",")
                method = segments_splited[0]
                uri  = segments_splited[1]
                method,uri = method.split('=',1)[1],uri.split('=',1)[1][1:-1]
                
                logger.debug(f'request uri: {uri}')


                uri = urljoin(self.url,uri)

                r = self.session.get(uri,proxies=self.proxies)
                if r.status_code ==200:
                    return  r.content
                logger.fatal(f"Can`t download key url: {uri}, maybe you should use proxy")
                sys.exit(-1)
                

    def _get_http_session(self, pool_connections, pool_maxsize, max_retries):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize, max_retries=max_retries) 
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session


    def m3u8content(self,m3u8_url):
        logger.debug(f"m3u8_url {m3u8_url}")
        if m3u8_url.startswith("http"):
            r = self.session.get(m3u8_url, timeout=20,headers=headers,proxies=self.proxies,verify=self.verify)
            if r.ok:
                ts_list = [urljoin(m3u8_url, n.strip()) for n in r.text.split('\n') if n and not n.startswith("#")]
                if ts_list[0].endswith("m3u8"):
                    self.url = urljoin(m3u8_url,ts_list[0])
                    return self.m3u8content(self.url)
                return r.text
            else:
                logger.debug(f'respnse:{r}')
        else:
            return Path(m3u8_url).read_text()

        raise Exception("read m3u8 content error.")

    def download(self,url,i):
        try:
            d = D(proxies=self.proxies,headers=headers,verify=self.verify,debug=self.debug)
            logger.debug(f'url:{url}')
            pathname = join(self.tempdir,self.tempname,str(i))
            # logger.debug(f'pathname:{pathname}')
            ret = d.download(url,pathname)
            if ret:
                # logger.info(f'{i} done')
                self.ready_to_merged.add(i)
            else:
                logger.debug(f'{i} download fails! re Q')
                self.downloadQ.put((i,url))

        except Exception as e :
            if self.debug:
                logger.exception(e)


    def target(self):
        while self.next_merged_id < self.length:
            try:
                idx,url = self.downloadQ.get(timeout=3)
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
                self.downloadQ.put((pair[1],pair[0]))


    def try_merge(self):
            outfile  = None

            pp=pb2.getSingleton()
            if self.out_path:
                outfile = open(self.out_path, 'ab')
            while self.next_merged_id < self.length:
                dots = random.randint(0,3)*"."
                
                # p.print(f'\r{self.next_merged_id}/{self.length} merged '+dots+(3-len(dots))*" ",file=sys.stderr,end="")
                pp.update("total merged ", self.next_merged_id, self.length,"",userDefineVisual2)
                pp.update("block pending", self.next_merged_id+len(self.ready_to_merged), self.length,"",userDefineVisual2)
                oldidx = self.next_merged_id
                try:
                    if self.next_merged_id in self.ready_to_merged:
                        logger.debug(f'try merge {self.next_merged_id}  ....')
                        self.ready_to_merged.remove(self.next_merged_id)
                        p = os.path.join(self.tempdir,self.tempname, str(self.next_merged_id))

                        infile= open(p, 'rb')
                        o  = self.decode(infile.read())
                        
                        if  self.out_path:
                            outfile.write(o)
                            outfile.flush()
                        else:
                            sys.stdout.buffer.write(o)
                            sys.stdout.flush()

                        infile.close()

                        self.next_merged_id += 1

                        os.remove(join(self.tempdir,self.tempname,str(oldidx)))
                    else:
                        time.sleep(1)
                        logger.debug(f'waiting for {self.next_merged_id} to merge ')
                        logger.debug(f'unmerged {self.ready_to_merged} active_thread:{threading.active_count()}')
                except Exception as e :
                    logger.exception(e)
                    try:
                        self.next_merged_id=oldidx
                        os.remove(join(self.tempdir,self.tempname,str(oldidx)))
                        logger.error(f'{oldidx} merge error ,reput to thread')
                        logger.exception(e)
                        # print(self.ts_list[oldidx],oldidx)
                        self.downloadQ.put((oldidx,self.ts_list[oldidx]))
                    except Exception as e2:
                        logger.exception(e)

            if self.out_path:
                outfile.close()
            

def main(args):
    if args.debug:
        logger.setLevel("DEBUG")


    logger.debug(f'args.out_path:{args.out_path}')
    if args.out_path and os.path.exists(args.out_path) and not args.overwrite:
            logger.error(f'{args.out_path} exists! use -w if you want to overwrite it ')
            sys.exit(-1) 

    m = m3u8_dl(
            args.url,
            args.out_path,
            args.proxy,
            args.ignore_certificate_verfication,
            args.key,
            args.debug
            )

    # must ensure 1 for merged thread
    threadcount = args.threadcount + 1
    m.run(threadcount)

def entry_point():
    parser = createParse()
    mainArgs=parser.parse_args()
    main(mainArgs)


def createParse():
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="")
    parser.add_argument("url",  help="url")
    parser.add_argument('-o', '--out_path',type=str,  help="output path, ex: ./a.mp4" )
    parser.add_argument('-p', '--proxy',type=str,  help="for example: socks5h://127.0.0.1:5992")
    parser.add_argument('-e', '--key',type=str,  help="custom decrypt key")
    parser.add_argument('-t', '--threadcount',type=int,  help="thread count" ,default=2)
    parser.add_argument('-d', '--debug', help='debug info', default=False, action='store_true') 
    parser.add_argument('-w', '--overwrite', help='overwrite existed file', action='store_true')  
    mydir = os.path.dirname(os.path.abspath(__file__))
    version =Path(join(mydir,"..","version")).read_text()
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('-k',  '--ignore_certificate_verfication',help='ignore certificate verfication, don`t use this option only if you know what you are doing!', action='store_true')  


    return parser
