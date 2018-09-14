from cartman import bot

import numpy as np
def a(*l): return np.array(l,dtype='float32')
def dist(p1, p2):
    return np.sqrt(((p1 - p2)**2).sum())

class mybot(bot):
    def __init__(self,*args,**k):
        super().__init__(*args,**k)

        self.last_line_end = a(0,0)

    def pendown(self): self.goto(z=0)
    def penup(self): self.goto(z=3)
    def goto_2dpoint(self, p): self.goto(x=p[0], y=p[1])

    def drawline(self, p1, p2):
        if dist(p1, self.last_line_end) > dist(p2, self.last_line_end):
            p1,p2 = p2,p1
        self.penup()
        self.goto_2dpoint(p1)
        self.pendown()
        self.goto_2dpoint(p2)
        self.penup()

        self.last_line_end = p2

    def drawlines(self, points):
        for i in range(len(points)-1):
            self.drawline(points[i], points[i+1])

if __name__ == '__main__':

    b = mybot()

    b.home()
    b.set_speed(50000)

    # draw the corners
    b.drawline(a(0,10), a(10,0))
    b.drawline(a(0,90), a(10,100))
    b.drawline(a(100,90), a(90,100))
    b.drawline(a(90,0), a(100,10))

    # draw a mess
    for i in range(50):
        b.drawline(
            np.random.uniform(0,100,size=(2)),
            np.random.uniform(0,100,size=(2)),
        )

    # draw a 100x100mm grid
    for i in range(11):
        y = i*10
        b.drawline(a(0,y), a(100,y))

    for i in range(11):
        x = i*10
        b.drawline(a(x,0), a(x,100))

    b.wait_until_idle()
