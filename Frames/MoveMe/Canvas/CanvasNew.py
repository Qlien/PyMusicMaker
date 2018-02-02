import wx, sys, os
from Frames.MoveMe.Canvas.NodesFactory import NodesFactory
from Frames.MoveMe.Canvas.Objects.SimpleTextBoxNode import SimpleTextBoxNode
from Frames.MoveMe.Canvas.soundBoardBG import *
import math
BUFFERED = 1

class MyCanvas(wx.ScrolledWindow):
    def __init__(self, parent, id = -1, size = wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)

        self._soundBoardBG = SoundBoardBG(parts=20)

        self.lines = []
        self.maxWidth  = 10000
        self.maxHeight = 10000
        self.x = self.y = 0
        self.curLine = []
        self.drawing = False

        self._canvasObjects = [SimpleTextBoxNode(position=[20, 20], text="A", boundingBoxDimensions=[30,21]),
                               SimpleTextBoxNode(position=[140, 40], text="B", boundingBoxDimensions=[30,21]),
                               SimpleTextBoxNode(position=[60, 120], text="C", boundingBoxDimensions=[30,21]),
                               SimpleTextBoxNode(position=[60, 120], text="C", boundingBoxDimensions=[30,21])]

        self._nodesFactory = NodesFactory()

        self.SetBackgroundColour("WHITE")
        self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))
        iconsBase = 'Icons/typicons/png/'

        bmp = wx.Bitmap(iconsBase + 'repeat.png')

        mask = wx.Mask(bmp, wx.BLUE)
        bmp.SetMask(mask)
        self.bmp = bmp

        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.SetScrollRate(20,20)

        if BUFFERED:
            # Initialize the buffer bitmap.  No real DC is needed at this point.
            self.buffer = wx.Bitmap(self.maxWidth, self.maxHeight)
            dc = wx.BufferedDC(None, self.buffer)
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
            self.DoDrawing(dc)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftButtonEvent)
        self.Bind(wx.EVT_LEFT_UP,   self.OnLeftButtonEvent)
        self.Bind(wx.EVT_MOTION,    self.OnLeftButtonEvent)
        self.Bind(wx.EVT_PAINT,     self.OnPaint)


    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight


    def OnPaint(self, event):
        if BUFFERED:
            # Create a buffered paint DC.  It will create the real
            # wx.PaintDC and then blit the bitmap to it when dc is
            # deleted.  Since we don't need to draw anything else
            # here that's all there is to it.
            dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        else:
            dc = wx.PaintDC(self)
            self.PrepareDC(dc)
            # Since we're not buffering in this case, we have to
            # (re)paint the all the contents of the window, which can
            # be potentially time consuming and flickery depending on
            # what is being drawn and how much of it there is.
            self.DoDrawing(dc)


    def Render(self):
        pass
        cdc = wx.ClientDC(self)
        self.PrepareDC(cdc)
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        # dc.SetUserScale(2, 2)
        gc = wx.GraphicsContext.Create(dc)

    def DoDrawing(self, dc, printing=False):
        dc.Clear()

        self._soundBoardBG.Render(dc)

        for obj in self._canvasObjects:
            obj.Render(dc)

    def DrawSavedLines(self, dc):
        dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
        for line in self.lines:
            for coords in line:
                dc.DrawLine(*coords)


    def SetXY(self, event):
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):
        newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        return newpos

    def OnLeftButtonEvent(self, event):
        if self.IsAutoScrolling():
            self.StopAutoScrolling()

        if event.LeftDown():
            self.SetFocus()
            self.SetXY(event)
            self.curLine = []
            self.CaptureMouse()
            self.drawing = True

        elif event.Dragging() and self.drawing:
            if BUFFERED:
                # If doing buffered drawing we'll just update the
                # buffer here and then refresh that portion of the
                # window.  Then the system will send an event and that
                # portion of the buffer will be redrawn in the
                # EVT_PAINT handler.
                dc = wx.BufferedDC(None, self.buffer)
            else:
                # otherwise we'll draw directly to a wx.ClientDC
                dc = wx.ClientDC(self)
                self.PrepareDC(dc)


            dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
            coords = (self.x, self.y) + self.ConvertEventCoords(event)
            # self.curLine.append(coords)
            # dc.DrawLine(*coords)
            SimpleTextBoxNode(position=coords, text="B", boundingBoxDimensions=[30, 20]).Render(dc)
            self.SetXY(event)

            if BUFFERED:
                # figure out what part of the window to refresh, based
                # on what parts of the buffer we just updated
                x1,y1, x2,y2 = dc.GetBoundingBox()
                x1,y1 = self.CalcScrolledPosition(x1, y1)
                x2,y2 = self.CalcScrolledPosition(x2, y2)
                # make a rectangle
                rect = wx.Rect()
                rect.SetTopLeft((x1,y1))
                rect.SetBottomRight((x2,y2))
                rect.Inflate(2,2)
                # refresh it
                self.RefreshRect(rect)

        elif event.LeftUp() and self.drawing:
            self.lines.append(self.curLine)
            self.curLine = []
            self.ReleaseMouse()
            self.drawing = False