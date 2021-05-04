def conv_bytes_to_int(bytes):
    """
    converts a bytearray in integer
    :param bytes: bytes
    :return: int
    """
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result


def conv_int_to_bytes(value, length):
    """
    converts a integer value to a bytearray
    :param value: int
    :param length: int length of bytearray
    :return: bytearray
    """
    result = []
    for i in range(0, length):
        result.append(value >> (i * 8) & 0xff)
    result.reverse()
    return result


def conv_str_to_bitarr(arr, length):
    """
    converts a bitarray as Sting with 0b at begin to a real bitarray if length is greater its will be filled with 0
    :param arr: string
    :param length: int
    :return: bitarray
    """
    bin = list()
    if "0b" in arr:
        arr = arr.replace("0b", "")
    if len(arr) < length:
        for i in range(0, (length-len(arr))):
            bin.append(0)
    for i in range(0, len(arr)):
        bin.append(int(arr[i]))
    return bin


def conv_bitarr_to_string(bin):
    """
    converts a bitarray to similar string
    :param bin: bitarray
    :return: String
    """
    string = ''
    for i in range(0, len(bin)):
        string = string+'{}'.format(bin[i])
    return string


def conv_bytearr_to_string(byt):
    """
    converts a bytearray to a similar string
    :param byt: byte
    :return: String
    """
    string = "0x"
    for i in range(0, len(byt)):
        string = string + "{}".format(hex(byt[i])).replace("0x", "").upper()
    return string


def conv_bitarr_to_int(bin):
    """
    converts bitarray to int
    :param bin: bit
    :return: int
    """
    return int(conv_bitarr_to_string(bin), 2)


def get_ack_tribeID(mymsg,dcdcID):
    """
    reconstructs the send id from the given ack datafield
    :param mymsg: byte
    :param dcdcID: int
    :return: int
    """
    val = format(conv_bytes_to_int(mymsg), '0>5b')
    a = conv_str_to_bitarr(val, 5)
    id_past_msg = a+dcdcID+[1]
    IDhex_past = int(conv_bitarr_to_string(id_past_msg), 2)
    return IDhex_past