from itertools import cycle
import datetime
import binascii

def xor(message, username):
    xord = []
    for a,b in zip(message, cycle(username)):
        xord.append(a^ord(b))
    return ''.join([chr(a) for a in xord])

def xore(data, key):
    return ''.join(chr(a ^ ord(b)) for (a, b) in zip(data, cycle(key)))

def byteInt(b):
    return int.from_bytes(b, byteorder='big')

def byteDate(b):
    return int.from_bytes(b, byteorder='little')
if __name__ == "__main__":
    with open("./Yahoo/20090410-rolisz.dat", "rb") as f:
        messages = []
        username = "rolisz"
        # First four bytes are the Unix timestamp in little Endian order
        # Next four bytes are unknown
        # Next byte is direction (0 you wrote, 1 other contact)
        # Next 4 are length of message in big endian mode
        # Then is message of given length
        # 4 more empty bytes
        fixedBytes = f.read(16)
        while fixedBytes:
            dates = datetime.datetime.fromtimestamp(byteDate(fixedBytes[:4]))
            # print(binascii.hexlify(dates))
            # dunno = f.read(3)
            # print(binascii.hexlify(dunno))
            direction = fixedBytes[8]
            # dunno = f.read(3)
            # print(binascii.hexlify(dunno))
            length = fixedBytes[9:13]
            length = byteInt(length)
            # dunno = f.read(3)
            message = f.read(length)
            # print(dates, direction, length, message, xore(message, username))
            dunno = f.read(4)
            # print("dooone")
            message = xore(message, username)
            fixedBytes = f.read(16)
            contact = 'other' if direction else 'Roland'
            messages.append({'timestamp': dates, 'contact': contact,
                'message': message})


for m in messages:
    print(m['timestamp'])


