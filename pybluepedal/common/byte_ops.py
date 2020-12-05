
def byte_array_to_int(value):
    # Raw data is hexstring of int values, as a series of bytes,
    # in little endian byte order
    # values are converted from bytes -> bytearray -> int
    # e.g., b'\xb8\x08\x00\x00' -> bytearray(b'\xb8\x08\x00\x00') -> 2232

    # print(f"{sys._getframe().f_code.co_name}: {value}")

    value = bytearray(value)
    value = int.from_bytes(value, byteorder="little")

    return value


def check_bit_l2r(byte, bit):
    return bool(byte & (0b10000 >> bit))
