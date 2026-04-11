import keyboard
import time

print()
print("  Press Shift+F1 ... (10 seconds)")
print()

got = [False]

def cb():
    got[0] = True
    print("  >>> SHIFT+F1 WORKS!")

keyboard.add_hotkey('shift+f1', cb)
time.sleep(10)
keyboard.unhook_all()

if not got[0]:
    print("  Shift+F1 NOPE")
    print()
    print("  Trying just F1 ... (10 seconds)")
    print()

    got2 = [False]
    def cb2():
        got2[0] = True
        print("  >>> F1 WORKS!")

    keyboard.add_hotkey('f1', cb2)
    time.sleep(10)
    keyboard.unhook_all()

    if not got2[0]:
        print("  F1 NOPE too")
        print()
        print("  Let me see what keys you press...")
        print("  Press ANY key (10 seconds):")
        print()

        def show(e):
            print(f"  -> name={e.name} scan={e.scan_code} type={e.event_type}")

        keyboard.hook(show)
        time.sleep(10)
        keyboard.unhook_all()

print()
input("Enter to close...")
