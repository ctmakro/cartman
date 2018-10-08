from cartman import bot, choose_serial_connection

serial_port = choose_serial_connection()

g = bot(name=serial_port)
g.home()

g.set_offset(100,300)

for i in range(1):
    print(g.where())
    g.set_speed(50000)

    g.goto(x=100, y=0)
    g.goto(x=170, y=30)

    g.goto(x=200, y=100)
    g.goto(x=170, y=170)

    g.set_speed(10000)

    g.goto(x=100, y=200)
    g.goto(x=30, y=170)

    g.goto(x=0, y=100)
    g.goto(x=30, y=30)

import math
for i in range(3):
    # go around in circles

    g.set_speed(10000*(i+1)) # in different speed

    [g.goto(
        x=math.cos(k/128*math.pi*2)*100+50,
        y=math.sin(k/128*math.pi*2)*100+50) for k in range(128)]

print(g.where())
# try G2 clockwise arcs
g.goto(x=100, y=100)
print(g.where())

# for i in range(4):
#     g.send('G2 X100 Y200 R50')
#     g.send('G2 X100 Y100 R55')

# don't close the serial connection before all the commands
# finish execution. otherwise the machine may restart.
g.sync()
