#!/usr/bin/env python
# vim:set ts=4 sw=4 et:

from __future__ import print_function
import logging
import math
import Tkinter as tk

root3 = math.sqrt(3)

class koch(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self, bg="bisque")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize) # resize event
        self.canvas.bind("<Key>", self.on_key) # need to put canvas on focus first
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonRelease-3>", self.on_zoomout)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.focus_set()
        self.lineobjs = []
        self.rectobjs = None
        self.reset()
    def on_resize(self, event):
        "resize and reset canvas"
        logging.debug('Resize to %s x %s' % (event.width, event.height))
        self.canvas.config(width=event.width, height=event.height)
        self.reset()
    def on_key(self, event):
        "On key press: Escape to kill app, other key to restart"
        logging.debug('Key event %r' % event.char)
        if event.char == '\x1b':
            print("Closing")
            self.winfo_toplevel().destroy()
        else:
            self.reset()
    def on_press(self, event):
        "Press down of mouse button: Starting point for building new line"
        self.x, self.y = event.x, event.y
        logging.debug("Mouse down on pixel (%d,%d)" % (event.x, event.y))
    def on_release(self, event):
        "Evolve the fractal on double click"
        logging.debug("Mouse release on pixel (%d,%d)" % (event.x, event.y))
        x0, y0 = self.canvas2cartesian(self.x, self.y)
        x1, y1 = self.canvas2cartesian(event.x, event.y)
        if not self.initialized:
            # mark fractal intialized: Picture already built by on_drag() function
            self.initialized = True
        elif self.rectobjs:
            # remove the rectangle and zoom in
            self.canvas.delete(self.rectobjs)
            self.rectobjs = None
            # update the canvas domain
            self.xLL, self.yLL = min(x0, x1), min(y0, y1)
            scale = max(abs(x0-x1)/float(self.width), abs(y0-y1)/float(self.height))
            self.xUR = scale * self.width  + self.xLL
            self.yUR = scale * self.height + self.yLL
            # redraw
            self.clear_canvas()
            self.draw_lines()
    def on_zoomout(self, event):
        "Click of `right button` to zoom out "
        self.xLL = self.xLL - (self.xUR - self.xLL)/2.0
        self.yLL = self.yLL - (self.yUR - self.yLL)/2.0
        self.xUR = self.xUR + (self.xUR - self.xLL)/2.0
        self.yUR = self.yUR + (self.yUR - self.yLL)/2.0
        self.clear_canvas()
        self.draw_lines()
    def on_drag(self, event):
        "If not started, drag to create new line; otherwise drag to zoom"
        logging.debug("drag (%d,%d)-(%d,%d)" % (self.x, self.y, event.x, event.y))
        if self.initialized:
            # draw rectangle for zoom level
            if self.rectobjs:
                self.canvas.delete(self.rectobjs)
            self.rectobjs = self.canvas.create_rectangle(self.x, self.y, event.x, event.y)
        else:
            # making initial fractal
            x0, y0 = self.canvas2cartesian(self.x, self.y)
            x1, y1 = self.canvas2cartesian(event.x, event.y)
            xc, yc = rotpi3(x0, y0, x1, y1)
            self.lines = [(x0, y0, xc, yc), (xc, yc, x1, y1), (x1, y1, x0, y0)]
            self.clear_canvas()
            self.draw_lines()
    def on_double_click(self, event):
        "Evolve the fractal on double click"
        logging.debug("Mouse double click on pixel (%d,%d)" % (event.x, event.y))
        self.evolve()
    def canvas2cartesian(self, x, y):
        "convert canvas coordinate to cartesian coordinate"
        cart_x = float(x)/self.width * (self.xUR - self.xLL) + self.xLL
        cart_y = self.yUR - float(y)/self.height * (self.yUR - self.yLL)
        return cart_x, cart_y
    def cartesian2canvas(self, x, y):
        "convert cartesian coordinate to canvas coordinate"
        can_x = (x - self.xLL) / (self.xUR - self.xLL) * self.width
        can_y = (self.yUR - y) / (self.yUR - self.yLL) * self.height
        return can_x, can_y
    def reset(self):
        "reset canvas to initial state"
        self.clear_canvas()
        self.x = self.y = None
        self.xLL = self.yLL = 0.0
        self.width  = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        scale = float(min(self.width, self.height))
        self.xUR = self.width/scale
        self.yUR = self.height/scale
        self.initialized = False
    def clear_canvas(self):
        "clear canvas but keep states to prepare for redraw"
        if self.lineobjs:
            for l in self.lineobjs:
                self.canvas.delete(l)
            self.lineobjs = []
        if self.rectobjs:
            self.canvas.delete(self.rectobjs)
            self.rectobjs = None
        logging.debug("Clear canvas")
    def draw_lines(self):
        "Draw lines according to self.lines and save line objects to self.lineobjs"
        for x0,y0,x1,y1 in self.lines:
            cx0, cy0 = self.cartesian2canvas(x0, y0)
            cx1, cy1 = self.cartesian2canvas(x1, y1)
            self.lineobjs.append(self.canvas.create_line(cx0, cy0, cx1, cy1))
    def evolve(self):
        "Evolve the Koch snowflake"
        newlines = []
        for x0,y0,x1,y1 in self.lines:
            xa,ya = (2*x0+x1)/3, (2*y0+y1)/3 # trisection closer to x0,y0
            xb,yb = (x0+2*x1)/3, (y0+2*y1)/3 # trisection closer to x1,y1
            xc,yc = rotpi3(xa,ya,xb,yb)      # apex of equilateral triangle
            newlines.extend([(x0,y0,xa,ya),(xa,ya,xc,yc),(xc,yc,xb,yb),(xb,yb,x1,y1)])
        xa,ya = self.canvas2cartesian(0,0)
        xb,yb = self.canvas2cartesian(1,1)
        pixelsize = norm(xa,ya,xb,yb)
        maxpixelsize = max(norm(x0,y0,x1,y1) for x0,y0,x1,y1 in newlines)
        logging.debug('Pixelsize = %f' % pixelsize)
        logging.debug('max Pixelsize = %f' % maxpixelsize)
        if all(norm(x0,y0,x1,y1) < pixelsize for x0,y0,x1,y1 in newlines):
            # stop if fractal segments < one pixel
            logging.debug('Line segment is finer than canvas resolution')
            return
        self.clear_canvas()
        self.lines = newlines
        self.draw_lines()
        logging.info("Line segments: %d" % len(newlines))

def norm(x0,y0,x1,y1):
    "Euclidean-norm: ||(x0,y0)-(x1,y1)||"
    return math.sqrt((x0-x1)**2 + (y0-y1)**2)
def rotpi3(x0,y0,x1,y1):
    "Take x0,y0 as origin, rotate x1,y1 counterclockwise for pi/3"
    sin, cos = math.sqrt(3)/2, 0.5
    x = cos*(x1-x0)-sin*(y1-y0) + x0
    y = sin*(x1-x0)+cos*(y1-y0) + y0
    return x,y

def main():
    root = tk.Tk()
    root.title("Koch snowflake (any key to reset, double click to evolve)")
    root.geometry("640x480")
    app = koch(root)
    root.mainloop()

if __name__ == "__main__":
    logging.getLogger('').setLevel(logging.DEBUG)
    main()
