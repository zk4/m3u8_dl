#coding: utf-8
import logging
import os
import argparse
import requests
import subprocess
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .logx import setup_logging
from .D  import D

# don`t remove this line 
setup_logging()

logger = logging.getLogger(__name__)

from Crypto.Cipher import AES
import sys

proxies={"https":"socks5h://127.0.0.1:5992","http":"socks5h://127.0.0.1:5992"}
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' ,
}



class m3u8_dl(object):

    def __init__(self,url):
        pool_size = 10
        self.url =url
        self.session = self._get_http_session(pool_size, pool_size, 5)
        self.m3u8_content = self.m3u8content(url)
        self.ts_list = [urljoin(url, n.strip()) for n in self.m3u8_content.split('\n') if n and not n.startswith("#")]
        key = self.readkey()

        self.cryptor = None
        if key:
            self.cryptor = AES.new(key, AES.MODE_CBC, key)


    def decode(self, content,outfileHandler):
        outfileHandler.write(self.cryptor.decrypt(content))

    def readkey(self):
        tag_list = [n.strip() for n in self.m3u8_content.split('\n') if n and n.startswith("#")]
        for s in tag_list:
            if str.upper(s).startswith("#EXT-X-KEY"):
                logger.debug(f'{s} found')
                segments = s[len("#EXT-X-KEY")+1:]
                if segments == "NONE":
                    return None

                logger.debug(f'segments: {segments}')
                [method,uri]=segments.split(",")
                method,uri = method.split('=')[1],uri.split('=')[1][1:-1]
                
                r = self.session.get(uri,proxies=proxies)
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
            r = self.session.get(m3u8_url, timeout=10,headers=headers,proxies=proxies)
            if r.ok:
                return r.content
        else:
            return Path(m3u8_url).read_text()

        return None

    def download(self,url,i):
        try:
            # logger.debug(f"{i}->{url}")
            d = D(proxies=proxies,headers=headers)
            d.download(url,"./a/"+str( i ))
            # process = subprocess.Popen(["proxychains4", "axel",  url ])  
            # process.wait()
        except Exception as e :
            logger.exception(e)

    

    def run(self):
        if self.ts_list:
            with ThreadPoolExecutor(max_workers=50) as executor:
                index = 1
                for url in self.ts_list:
                    e = executor.submit(self.download,url,index)
                    index +=1



def merge(url):
    try:
        m = m3u8_dl(url)
        # key = m .readkey()
        # cryptor = AES.new(key, AES.MODE_CBC, key)

        index = 1
        outfile = ''
        while index < 338:
            logger.debug(f'{index} merged')
            output = "./a"
            infile = open(os.path.join(output, str(index)), 'rb')
            if not outfile:
                outfile = open(os.path.join(output,"all.mp4"), 'wb')
            m.decode(infile.read(),outfile)
            # outfile.write(infile.read())
            infile.close()
            # os.remove(os.path.join(self.dir, file_name))
            index += 1
        if outfile:
            outfile.close()
    except Exception as e :
        print(e)



def main(args):
    # logger.debug(args.url)
    # m = m3u8_dl(args.url)
    # m.readkey()
    # m.run()
    # merge()
    merge(args.url)

def entry_point():
    parser = createParse()
    mainArgs=parser.parse_args()
    main(mainArgs)


def createParse():
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="")
    parser.add_argument("url",  help="url" )

    return parser
