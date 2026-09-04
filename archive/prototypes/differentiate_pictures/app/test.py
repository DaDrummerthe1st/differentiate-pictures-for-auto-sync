import mimetypes
mimetypes.init()

mimestart = mimetypes.guess_type("/home/joakim/Pictures/Screenshots/doru_luca/doru_luca.zip")[0]

if mimestart != None:
    mimestart = mimestart.split('/')[0]

    if mimestart == 'audio' or mimestart == 'video' or mimestart == 'image':
        print("media types " + mimestart)
    else:
        print("no valid mimetype " + mimestart)
