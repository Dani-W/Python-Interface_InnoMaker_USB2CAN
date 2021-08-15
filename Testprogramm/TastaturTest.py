import can_lib
from pynput import keyboard
can = None


def on_press(key):
    global can
    try: k = key.char  # single-char keys
    except: k1 = key.name  # other keys
    if key == keyboard.Key.esc:
        return False  # stop listener
    if k in ['1', '2', '3', '4']:  # keys interested
        # self.keys.append(k) # store it in global-like variables
        if k is '1':
            can.add_msg(0x320, 8, 0x0102030405060708)

        elif k is '2':
            can.add_msg(0x15, 2, 0x3E8)

        elif k is '3':
            can.shutdown()

        elif k is '4':
            can.add_msg(0x16, 2, 0x2710)


if __name__ == "__main__":
    can = can_lib.canLib()
    lis = keyboard.Listener(on_press=on_press)
    lis.start()  # start to listen on a separate thread
    lis.join()  # no this if main thread is polling self.keys