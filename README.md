# Intro
This is a pipe compatiable tool for downloading m3u8.

1. Fast download for m3u8.
2. Auto decrpt the key.

![](https://github.com/zk4/m3u8_dl/blob/master/demo.gif?raw=true)
# Install
since the name m3u8_dl is taken by other developer...

short it to m3_dl
```
pip install m3_dl
```

# Usage 
```
m3_dl <m3u8_url> -o <dest>
```

ex:
```
# download to local file
m3_dl http://aaa.com/a.m3u8 -o ./a.mp4

# pipe it to mpv
m3_dl  https://you.tube-kuyun.com/20200210/1144_623a1fb3/index.m3u8 | mpv -

# pipe it to mpv and save to local
m3_dl  https://you.tube-kuyun.com/20200210/1144_623a1fb3/index.m3u8 | tee > ./a.mp4 | mpv -
```

# Full Usage 
```
usage: m3_dl [-h] [-o OUT_PATH] [-p PROXY] [-t THREADCOUNT] [-d] [-w] [-s]
             [--version] [-k]
             url

positional arguments:
  url                   url

optional arguments:
  -h, --help            show this help message and exit
  -o OUT_PATH, --out_path OUT_PATH
                        output path (default: None)
  -p PROXY, --proxy PROXY
                        for example: socks5h://127.0.0.1:5992 (default: None)
  -t THREADCOUNT, --threadcount THREADCOUNT
                        thread count (default: 2)
  -d, --debug           debug info (default: False)
  -w, --overwrite       overwrite existed file (default: False)
  --version             show program's version number and exit
  -k, --ignore_certificate_verfication
                        ignore certificate verfication, don`t use this option
                        only if you know what you are doing! (default: False)
```


# TODO
1. enable redownlowd
1. make it mitm compatiable


