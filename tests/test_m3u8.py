import m3u8

m3u8_obj = m3u8.load('./index-v1-a1.m3u8')  # this could also be an absolute filename
print(m3u8_obj.segments)
print(m3u8_obj.target_duration)
print(m3u8_obj.keys)

# if you already have the content as string, use

