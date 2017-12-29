#!/usr/bin/env python
# vim:set ts=4 sw=4 et:

from __future__ import print_function
import Tkinter as tk
import math

class koch(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.lines = []
        self.objs = []
        self.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize) # resize event
        self.canvas.bind("<ButtonPress-1>", self.on_down) # mouse down
        self.canvas.bind("<B1-Motion>", self.on_drag) # mouse drag
    def on_resize(self, event):
        "Change canvas size and clear the canvas"
        self.canvas.config(width=event.width, height=event.height)
        self.clear_canvas()
    def on_down(self, event):
        "Mouse down: remember the position and evolve if we already drew a line"
        self.x0, self.y0 = float(event.x), float(event.y)
        if self.objs:
            self.evolve()
    def on_drag(self, event):
        "Mouse drag: clear the canvas and draw a new line"
        x1, y1 = float(event.x), float(event.y)
        self.lines = [(self.x0, self.y0, x1, y1)]
        self.draw()
    def clear_canvas(self):
        for lineobj in self.objs:
            self.canvas.delete(lineobj)
        self.objs = []
    def draw(self):
        "Clear canvas, draw every line segments and save the object"
        self.clear_canvas()
        for coords in self.lines:
            self.objs.append(self.canvas.create_line(*coords))
    def evolve(self):
        newlines = []
        for x0,y0,x1,y1 in self.lines:
            xa,ya,xb,yb = trisec(x0,y0,x1,y1)
            xc,yc = rotpi3(xa,ya,xb,yb)
            newlines.extend([(x0,y0,xa,ya),(xa,ya,xc,yc),(xc,yc,xb,yb),(xb,yb,x1,y1)])
        self.lines = newlines
        self.draw()

def rotpi3(xa,ya,xb,yb):
    sin, cos = math.sqrt(3)/2, 0.5
    xc = cos*(xb-xa) - sin*(yb-ya) + xa
    yc = sin*(xb-xa) + cos*(yb-ya) + ya
    return xc, yc

def trisec(x0,y0,x1,y1):
    xa,ya = (2*x0+x1)/3.0, (2*y0+y1)/3.0
    xb,yb = (x0+2*x1)/3.0, (y0+2*y1)/3.0
    return xa,ya,xb,yb

root = tk.Tk()
root.title("Koch snowflake")
root.geometry("640x480") # init size
_ = koch(root)
root.mainloop()

