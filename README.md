# Intro
This is a pipe compatiable tool for downloading m3u8.

1. Fast download for m3u8.
2. Auto decrpt the key.

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
m3_dl  https://you.tube-kuyun.com/20200210/1144_623a1fb3/index.m3u8 -w -s | mpv -

# pipe it to mpv and save to local
m3_dl  https://you.tube-kuyun.com/20200210/1144_623a1fb3/index.m3u8 -w -s | tee > ./a.mp4 | mpv -
```

# Full Usage 
```
m3u8_dl --help

usage: m3u8_dl [-h] [-p PROXY] url out_path

positional arguments:
  url                   url
  out_path              out path

optional arguments:
  -h, --help            show this help message and exit
  -p PROXY, --proxy PROXY
                        proxy (default: socks5h://127.0.0.1:5992)
```


# TODO
1. add temp name in case clash when multipal download happens
2. put cache in memory to reduce disk RW
3. enable redownlowd
