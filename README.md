# Install
```
pip install m3u8_dl
```

# Usage 
```
m3u8_dl <m3u8_url> <dest>

```

ex:
```
m3u8_dl http://aaa.com/a.m3u8  ./a.mp4
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
4. smart schedule
