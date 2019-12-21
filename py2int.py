from ctypes import (c_int8, c_uint8, c_int16, c_uint16,
                    c_int32, c_uint32, c_int64, c_uint64)

BYTE_ORDER = "big"

def bytes2uint(bytes_):
    print(bytes_)
    return int.from_bytes(bytes_, BYTE_ORDER)

def bytes2sint(bytes_):
    return int.from_bytes(bytes_, BYTE_ORDER, signed=True)

def uint2bytes(nInt, length=4):
    bytes_ = nInt.to_bytes(length, BYTE_ORDER)
    return bytes_

def sint2bytes(nInt, length=4):
    bytes_ = nInt.to_bytes(length, BYTE_ORDER, signed=True)
    return bytes_

def _length2type(length, signed: bool):
    sType = "c_int" if signed else "c_uint"
    nBit = str(length * 8)
    return eval(sType + nBit)

def uint2sint(nInt, length):
    # np_sint = np.int0(nInt)
    # return int(np_sint)
    return _length2type(length, True)(nInt).value


def sint2uint(nInt, length):
    # np_uint = np.uint(nInt)
    # return int(np_uint)
    return _length2type(length, False)(nInt).value

if __name__ == "__main__":
    bytes2 = [0b11111111, ]

    int_ = bytes2sint(bytes2)
    print(f"sint: {int_}")

    int_ = bytes2uint(bytes2)
    print(f"uint: {int_}")

    bytes_ = sint2bytes(-1, 5)
    # bytes_ = bytes([-1])  # failed >> bytes must be in range(0, 256)
    print("bytes(-1) >>", bytes_)

    print(f"uint8({255}) -> int8: {uint2sint(255, 1)}")
    print(f"int8({-1}) -> uint8: {sint2uint(-1, 1)}")
