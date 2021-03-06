from PIL import Image
import re
import struct
import os

# /usr/local/lib/python2.7/dist-packages/PIL/Image.py:2210: DecompressionBombWarning: Image size (941782785 pixels) exceeds limit of 89478485 pixels, could be decompression bomb DOS attack.
#   DecompressionBombWarning)
Image.MAX_IMAGE_PIXELS = None


class HugeImage(Exception):
    pass


class HugeJPEG(HugeImage):
    pass


class HugeTIF(HugeImage):
    pass


def coord(fn):
    '''Return (x, y) for filename'''
    # st_021365x_005217y.jpg
    m = re.match('.*st_([0-9]*)x_([0-9]*)y.jpg', fn)
    return (int(m.group(1), 10), int(m.group(2), 10))


def singlify(fns_in, fn_out, fn_out_alt=None):
    if not fns_in:
        raise Exception("No input")

    print('Calculating dimensions...')
    xmin = None
    xmax = None
    for fn in fns_in:
        (x, y) = coord(fn)
        if xmin is None:
            xmin = x
            ymin = y
            xmax = x
            ymax = y
        else:
            xmin = min(xmin, x)
            ymin = min(ymin, y)
            xmax = max(xmax, x)
            ymax = max(ymax, y)

    print('X: %d:%d' % (xmin, xmax))
    print('Y: %d:%d' % (ymin, ymax))
    #with Image.open(fns_in[0]) as im0:
    im0 = Image.open(fns_in[0])
    if 1:
        print('Supertile 0 size: %dw x %dh' % (im0.size[0], im0.size[1]))
        w = im0.size[0] + xmax - xmin
        h = im0.size[1] + ymax - ymin
        print('Output size: %dw x %dh' % (w, h))
        dst = Image.new(im0.mode, (w, h))

    def verify_format():
        if fn_out.find('.jpg') >= 0:
            if w >= 2**16 or h >= 2**16:
                if fn_out_alt:
                    print(
                        'WARNING: image exceeds maximum JPEG w/h.  Forcing alt format'
                    )
                    return fn_out_alt
                raise HugeJPEG('Image exceeds maximum JPEG w/h')
            # think this was tiff, not jpg...?
            if w * h >= 2**32:
                if fn_out_alt:
                    print(
                        'WARNING: image exceeds maximum JPEG size.  Forcing alt format'
                    )
                    return fn_out_alt
                raise HugeJPEG('Image exceeds maximum JPEG size')
        '''
        is this even true?  I think it was size which isn't the same since compressed
        elif fn_out.find('.tif') >= 0:
            if w * h >= 2**32:
                raise HugeJPEG('Image exceeds maximum tif size')
        '''
        return fn_out

    fn_out = verify_format()

    for fni, fn in enumerate(fns_in):
        print('Merging %d/%d %s...' % (fni + 1, len(fns_in), fn))
        (x, y) = coord(fn)
        im = Image.open(fn)
        dst.paste(im, (x - xmin, y - ymin))
    width, height = im.size
    print('Saving %uw x %uh %s...' % (width, height, fn_out))
    try:
        dst.save(fn_out, quality=95)
    # File "/usr/lib/python2.7/dist-packages/PIL/TiffImagePlugin.py", line 550, in _pack
    #   return struct.pack(self._endian + fmt, *values)
    # struct.error: 'L' format requires 0 <= number <= 4294967295
    except struct.error:
        try:
            os.remove(fn_out)
        except OSError:
            pass
        raise HugeTIF("Failed to save image of size %uw x %uh" %
                      (width, height))
    print('Done!')
