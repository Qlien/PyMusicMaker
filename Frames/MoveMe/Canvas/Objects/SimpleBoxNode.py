# Created by Dmytro Konobrytskyi, 2013 (github.com/Akson/MoveMe)
from enum import Enum
import wx


class SimpleBoxNode():

    def __init__(self, **kwargs):
        tempColor = kwargs.get('color', wx.Colour('#00aaaa'))
        self.color = tempColor if type(tempColor) != int else wx.Colour(tempColor)
        self.position = kwargs.get("position", [0, 0])
        self.boundingBoxDimensions = kwargs.get("boundingBoxDimensions", [31, 22])
        self.minimumClipSize = kwargs.get("minimumClipSize", [31, 22])

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

    def render_resizing(self, gc):
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

    def render_highlighting(self, gc):
        gc.SetBrush(wx.Brush('#888888', wx.TRANSPARENT))
        gc.SetPen(wx.Pen('#551bfcD9', 4, wx.SOLID))
        gc.DrawRectangle(self.position[0] - 2,
                         self.position[1] - 2,
                         self.boundingBoxDimensions[0] + 5,
                         self.boundingBoxDimensions[1] + 5)

    def render_selection(self, gc):
        gc.SetBrush(wx.Brush('#888888', wx.TRANSPARENT))
        gc.SetPen(wx.Pen('#3ee56bD9', 4, wx.SOLID))
        gc.DrawRectangle(self.position[0] - 2,
                         self.position[1] - 2,
                         self.boundingBoxDimensions[0] + 5,
                         self.boundingBoxDimensions[1] + 5)

    def return_object_under_cursor(self, pos):
        # Check if a position is inside of a rectangle
        if pos[0] < self.position[0]: return None
        if pos[1] < self.position[1]: return None
        if pos[0] > self.position[0] + self.boundingBoxDimensions[0]: return None
        if pos[1] > self.position[1] + self.boundingBoxDimensions[1]: return None
        return self

    def return_object_under_cursor_resizing_area(self, pos):
        if self.position[0] <= pos[0] <= self.position[0] + self.boundingBoxDimensions[0]: return None
        if pos[0] < self.position[0] - 4: return None
        if pos[1] < self.position[1]: return None
        if pos[0] > self.position[0] + self.boundingBoxDimensions[0] + 4: return None
        if pos[1] > self.position[1] + self.boundingBoxDimensions[1]: return None
        return self


class ObjectState(Enum):
    IDLE = 0
    MOVING = 1
    RESIZING = 2
