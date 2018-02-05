# Created by Dmytro Konobrytskyi, 2013 (github.com/Akson/MoveMe)
import wx
from Frames.MoveMe.Canvas.Objects.Base.CanvasObject import CanvasObject
from Frames.MoveMe.Canvas.Objects.Base.MovableObject import MovableObject
from Frames.MoveMe.Canvas.Objects.Base.SelectableObject import SelectableObject
from Frames.MoveMe.Canvas.Objects.Base.DeletableObject import DeletableObject
from Frames.MoveMe.Canvas.Objects.Base.ClonableObject import ClonableObject
from Frames.MoveMe.Canvas.Objects.Base.ResizableObject import ResizableObject
from enum import Enum


class SimpleBoxNode(ClonableObject, DeletableObject, SelectableObject, ResizableObject, MovableObject, CanvasObject):
    """
    SimpleBoxNode class represents a simplest possible canvas object
    that is basically a rectangular box.
    """

    def __init__(self, **kwargs):
        super(SimpleBoxNode, self).__init__(**kwargs)
        self.color = kwargs.get('color', wx.Colour('#00aaaa'))

    def render(self, gc):
        gc.SetBrush(wx.Brush(self.color, wx.SOLID))
        gc.SetPen(wx.Pen('#000000', 1, wx.SOLID))
        gc.DrawRoundedRectangle(self.position[0],
                                self.position[1],
                                self.boundingBoxDimensions[0],
                                self.boundingBoxDimensions[1], 3)

        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        gc.SetFont(font)


    def RenderResizing(self, gc):
        gc.SetPen(wx.Pen('#3603C7', 4, wx.SOLID))
        gc.DrawLines(points=[(self.position[0] - 2,
                    self.position[1]),
                     (self.position[0] - 2,
                    self.boundingBoxDimensions[1] + self.position[1])])

        gc.SetPen(wx.Pen('#3603C7', 4, wx.SOLID))
        gc.DrawLines(points=[(self.position[0] + 2.5 + self.boundingBoxDimensions[0],
                    self.position[1]),
                     (self.position[0] + 2.5 + self.boundingBoxDimensions[0],
                    self.boundingBoxDimensions[1] + self.position[1])])


    def RenderHighlighting(self, gc):
        gc.SetBrush(wx.Brush('#888888', wx.TRANSPARENT))
        gc.SetPen(wx.Pen('#551bfcD9', 4, wx.SOLID))
        gc.DrawRectangle(self.position[0] - 2,
                         self.position[1] - 2,
                         self.boundingBoxDimensions[0] + 5,
                         self.boundingBoxDimensions[1] + 5)

    def RenderSelection(self, gc):
        gc.SetBrush(wx.Brush('#888888', wx.TRANSPARENT))
        gc.SetPen(wx.Pen('#3ee56bD9', 4, wx.SOLID))
        gc.DrawRectangle(self.position[0] - 2,
                         self.position[1] - 2,
                         self.boundingBoxDimensions[0] + 5,
                         self.boundingBoxDimensions[1] + 5)

    def ReturnObjectUnderCursor(self, pos):
        # Check if a position is inside of a rectangle
        if pos[0] < self.position[0]: return None
        if pos[1] < self.position[1]: return None
        if pos[0] > self.position[0] + self.boundingBoxDimensions[0]: return None
        if pos[1] > self.position[1] + self.boundingBoxDimensions[1]: return None
        return self

    def ReturnObjectUnderCursorResizingArea(self, pos):
        if pos[0] >= self.position[0] and pos[0] <= self.position[0] + self.boundingBoxDimensions[0]: return None
        if pos[0] < self.position[0] - 4: return None
        if pos[1] < self.position[1]: return None
        if pos[0] > self.position[0] + self.boundingBoxDimensions[0] + 4: return None
        if pos[1] > self.position[1] + self.boundingBoxDimensions[1]: return None
        return self

    def Delete(self):
        pass

class ObjectState(Enum):
    IDLE = 0
    MOVING = 1
    RESIZING = 2