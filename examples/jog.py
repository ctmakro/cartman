# jogging is fun

# from getkey import getKey as getkey
from onkey import listen

from cartman import bot
b = bot(verbose=True)
b.home()

def jog(x=None,y=None,z=None,f=None):
    def n2z(x): return 0 if x is None else x
    jog_command = '$J=G91G21X{:.2f}Y{:.2f}Z{:.2f}F{:.1f}'.format(
        *[n2z(k) for k in [x,y,z,f]]
    )
    try:
        b.command_ok(jog_command)
    except Exception as e:
        if ':15' in repr(e): # jog exceed limits
            print(e)
        else:
            raise e

def unjog():
    # b.command(b'\x85')
    b.command_ok(b'\x85G4P0\n')
    b.status_report()
    # b.sync(interval=0.1)
    # b.command_ok('G4P100')
    print('X{:.1f} Y{:.1f} Z{:.1f}'.format(*b.working_position))
    time.sleep(0.05)
import time
import threading as th

lock = th.Lock()

def jogging_state_machine():
    global keyd,pressed
    import math
    # jogstate = 0
    dt = 0.06
    base_movement = 10 # mm
    fade_constant = fc = 0.93

    speediir = [0,0,0]

    while 1:
        p = pressed
        acc = [
            (-1 if p('left') else 0) + (1 if p('right') else 0),
            (-1 if p('down') else 0) + (1 if p('up') else 0),
            (-1 if p('z') else 0) + (1 if p('a') else 0),
        ]

        # if sum([a**2 for a in acc])==0:
        #     # if jogstate==1:
        #     #     unjog()
        #     #     jogstate=0
        #     speediir=[0,0,0]
        # else:
        import random
        speediir = [s * fc + a * (1-fc) for s,a in zip(speediir, acc)]
        speediir2 = [k*(abs(k)**1.3) for k in speediir]

        # motion proportional to iir-ed speed command
        motion = [(base_movement+0.1*random.random()) * s for s in speediir2]
        distance = math.sqrt(sum([a**2 for a in motion]))

        # fr proportional to distance
        feedrate = distance / (dt * 1.1) * 60 # mm/min

        if feedrate > 1 and distance > 0.05:
            jog(*motion, f = feedrate)
            # jogstate=1

        time.sleep(dt)

keyd = {}

def on_press(key):
    keyd[key] = 2
    if key=='esc' or not t.is_alive():
        return False

def on_release(key):
    if key in keyd:
        keyd[key] = 1
    if key=='esc' or not t.is_alive():
        return False

def pressed(k):
    if k in keyd and keyd[k]>=1:
        if keyd[k]==1:
            keyd[k] = 0
        return True
    else:
        return False

print('Press arrow keys to move the machine. Press ESC to quit.')
print('Press A/Z to go up/down on Z-axis.')
print('WARNING: The keys will still work after the terminal loses focus.')

t = th.Thread(target=jogging_state_machine, daemon=True)
t.start()

listen(on_press, on_release)
