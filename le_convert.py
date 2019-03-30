def to_int(str):
    if len(str) != 4:
        print("ololololo")
    return int.from_bytes(bytes(str, "utf8"), byteorder="little")

#test = to_int("\"Ij ")
#print(test)