"""
@copyright (c) 2016-2017 Synapse Product Development LLC ("Synapse").
All Rights Reserved. This file is subject to the terms and conditions
defined in the license obtained by you from Synapse.
"""
from struct import pack, unpack

def _next_zero(buf):
    n = len(buf)
    if n > 254:
        n = 254
    n += 1
    code = 1
    # string can contain 1 - 254 chars, and if 254 chars
    # then last char is non-zero
    while code < n:
        if buf[code - 1] == 0:
            break
        code += 1


    return code


def encode(buf):
    """
    COBS encode buf, buf should be a packed structure
    returns: COBS encoded packed structure
    """
    out      = [1]  # save one free space for code
    code_idx = 0    # index to be replaced with code
    code     = 1    # the next code to generate -- initialy 1
    for i in range(len(buf)):
        if buf[i] == 0:
            # zero will be replaced with a code
            # save previous code
            out[code_idx] = code
            code = 1
            code_idx = len(out)
            # insert place-hoder for next code
            out.append(code)
        else:
            out.append(buf[i])
            code += 1
            if code == 255:
                # save the max-run of 254 non-zero chars
                out[code_idx] = code
                code = 1
                code_idx = len(out)
                out.append(code)


    # save the last code
    out[code_idx] = code

    # terminate its
    out.append(0)

    return out


def decode(buf):
    # convert raw data to python representation
    if len(buf) < 3:
        # miniumum length of an encoded datagram is 3
        return ''

    buf = list(buf)
    i = 0
    j = 0
    # don't process trailing zero
    data_len = len(buf) - 1
    while i < data_len:
        # extract the next code in the stream
        code = buf[i]
        n = i + code
        i += 1
        if n > data_len:
            # FIXME should notify client of error
            n = data_len

        while i < n:
            # decode the string of non-zero bytes
            buf[j] = buf[i]
            j += 1
            i += 1

        if (code < 255) and (i < data_len):
            # we haven't processed all chars and the next code does not point
            # to extra overhead byte -- recover 0
            buf[j] = 0
            j+= 1

    return buf[:j]


if __name__ == '__main__':
    from binascii import hexlify

    def mkbuf(val, length, zeros=[]):
        buf = [val for i in range(length)]
        for i in zeros:
            buf[i] = 0
        return buf

    def serialize(buf):
        return pack('%dB' %len(buf), *buf)

    def show(buf):
        print (hexlify(serialize(buf)))

    in_buf = mkbuf(0xab, 256, [253])
    enc_buf = encode(in_buf)
    dec_buf = decode(enc_buf)
    show(in_buf)
    print len(in_buf)
    show(enc_buf)
    print len(enc_buf)
    show(dec_buf)
    print len(dec_buf)
