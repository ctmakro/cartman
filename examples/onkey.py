# pip install pynput
from pynput import keyboard

def listen(cb,cb2):
    def extract(key):
        try:
            name = key.char
        except AttributeError:
            name = key.name
        return name

    def on_press(key):
        name = extract(key)
        return cb(name)

    def on_release(key):
        name = extract(key)
        return cb2(name)

    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

if __name__ == '__main__':
    listen(lambda k:1, lambda k: False if k=='esc' else True)
