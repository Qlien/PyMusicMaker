# Created by Dmytro Konobrytskyi, 2013 (github.com/Akson/MoveMe)
import threading

import wx, sys, os
from Frames.MoveMe.Canvas.NodesFactory import NodesFactory
from Frames.MoveMe.Canvas.Objects.SimpleTextBoxNode import SimpleTextBoxNode
from Frames.MoveMe.Canvas.soundBoardBG import *
import math
from threading import Thread
import pyaudio
import numpy as np
import pygame
import time

BUFFERED = 0


# Define Text Drop Target class
class TextDropTarget(wx.TextDropTarget):
    def __init__(self, canvas):
        wx.TextDropTarget.__init__(self)
        self._canvas = canvas

    def OnDropText(self, x, y, data):
        self._canvas.create_node_from_description_at_position(data, [x, y])


class SoundBoard(wx.ScrolledWindow):
    """
    Canvas stores and renders all nodes and node connections.
    It also handles all user interaction.
    """

    def __init__(self, parent, instrumentsPanel, id=-1, size=wx.DefaultSize, **kw):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.parent = parent
        self.instrumentsPanel = instrumentsPanel
        self.scrollStep = kw.get("scrollStep", 30)
        self._soundBoardBG = SoundBoardBG(parts=20)
        self.canvasDimensions = kw.get("canvasDimensions", [1 + self._soundBoardBG.xBegin +
                                                            (self._soundBoardBG.parts *
                                                             self._soundBoardBG.columnsInSubPart *
                                                             self._soundBoardBG.subParts *
                                                             (self._soundBoardBG.columnWidth +
                                                              self._soundBoardBG.columnSpacing)),
                                                            8 + self._soundBoardBG.yBegin +
                                                            len(self._soundBoardBG.notes) *
                                                            (self._soundBoardBG.rowHeight +
                                                             self._soundBoardBG.rowSpacing)])
        self.SetScrollbars(self.scrollStep,
                           self.scrollStep,
                           self.canvasDimensions[0] / self.scrollStep,
                           self.canvasDimensions[1] / self.scrollStep)
        self.SetBackgroundColour("WHITE")

        self._canvasObjects = []
        # This list stores all objects on canvas
        # self._canvasObjects = [SimpleTextBoxNode(position=[20, 20], text="A", boundingBoxDimensions=[31,22]),
        #                        SimpleTextBoxNode(position=[140, 40], text="B", boundingBoxDimensions=[31,22]),
        #                        SimpleTextBoxNode(position=[60, 120], text="C", boundingBoxDimensions=[31,22]),
        #                        SimpleTextBoxNode(position=[60, 120], text="C", boundingBoxDimensions=[31,22])]
        self._nodesFactory = NodesFactory()
        self.SetVirtualSize(*self.canvasDimensions)

        # References to objects required for implementing moving, highlighting, etc
        self._objectUnderCursor = None
        self._draggingObject = None
        self._lastDraggingPosition = None
        self._lastLeftDownPos = None
        self._selectedObject = None
        self._objectUnderResizingGrippers = None
        self._resizingObject = None
        self._elementStartDragPosition = None
        self._elementResizePosition = None
        self._firstTimeRender = True;
        self.instrumentToDraw = None

        self.buffer = wx.Bitmap(*self.canvasDimensions)
        dc = wx.BufferedDC(None, self.buffer)
        dc.Clear()
        self.do_drawing(dc)

        # User interaction handling
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_KEY_DOWN, self.on_char)

        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.mixer.init()

        self.SetDropTarget(TextDropTarget(self))

        self.horizontalInterval = 40
        self.verticalInterval = 20

    def on_play(self, event):
        t = threading.Thread(target=self.play_song)
        t.start()

    def play_song(self):
        small_parts = self._soundBoardBG.columnsInSubPart * self._soundBoardBG.subParts * self._soundBoardBG.parts
        x_distance = self._soundBoardBG.columnWidth + self._soundBoardBG.columnSpacing
        y_distance = self._soundBoardBG.rowHeight + self._soundBoardBG.rowSpacing
        x_beginning = self._soundBoardBG.xBegin
        y_beginning = self._soundBoardBG.yBegin
        for i in range(20):
            notes_in_place = [sound for sound in self._canvasObjects if
                              sound.position[0] == (x_beginning + x_distance * i)]
            for note in notes_in_place:
                frequency_n = int((note.position[1] - y_beginning) / y_distance)
                frequency = frequencyFormula(frequency_n)
                instrument = self.instrumentsPanel.instruments[note.text]
                note_duration = float(note.boundingBoxDimensions[0]) / float(x_distance) * (60 / 128) * (1 / 4)
                sound = instrument.generateSound(frequency=frequency, duration=note_duration, sample_rate=44100,
                                                 bits=16)
                sound = pygame.sndarray.make_sound(sound)
                # play once, then loop forever
                sound.play()

            time.sleep((60 / 128) * (1 / 4))

    def on_char(self, event):
        if event.GetUnicodeKey() == wx.WXK_SPACE:
            tempInstrument = self.instrumentsPanel.get_selected_instrument()
            if tempInstrument:
                dim = self._canvasObjects[-1].boundingBoxDimensions if self._canvasObjects else [31, 22]
                self.instrumentToDraw = \
                    SimpleTextBoxNode(position=[self._soundBoardBG.xBegin, self._soundBoardBG.yBegin]
                                      , text=tempInstrument.pluginName, boundingBoxDimensions=dim
                                      , color=tempInstrument.get_color())

        if event.GetKeyCode() == wx.WXK_DELETE:
            if self._selectedObject and self._selectedObject.deletable:
                self._selectedObject.Delete()
                if self._selectedObject in self._canvasObjects:
                    self._canvasObjects.remove(self._selectedObject)
                self._selectedObject = None
        else:
            event.Skip()

        # Update object under cursor
        pos = self.CalcUnscrolledPosition(event.GetPosition()).Get()
        self._objectUnderCursor = self.FindObjectUnderPoint(pos)

        self.render()
        event.Skip()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        dc.Clear()
        self.do_drawing(dc)

    def do_drawing(self, dc, printing=False):

        self._soundBoardBG.render(dc)

        for obj in self._canvasObjects:
            obj.render(dc)

    def refresh_painting_area(self, dc):
        x1, y1, x2, y2 = dc.GetBoundingBox()
        x1, y1 = self.CalcScrolledPosition(x1, y1)
        x2, y2 = self.CalcScrolledPosition(x2, y2)
        # make a rectangle
        rect = wx.Rect()
        rect.SetTopLeft((x1, y1))
        rect.SetBottomRight((x2, y2))
        rect.Inflate(2, 2)
        # refresh it
        self.RefreshRect(rect)

    def create_node_from_description_at_position(self, nodeDescription, pos):
        node = self._nodesFactory.CreateNodeFromDescription(text=nodeDescription,
                                                            color=self.instrumentsPanel.instruments[
                                                                nodeDescription].get_color())
        self.parent.SetFocus()
        if node:
            node.position = pos
            self._canvasObjects.append(node)
            self.render()

    def render_play_line(self, gc, pos1, pos2):
        pos1Copy = pos1
        pos2Copy = pos2
        while True:
            self._soundBoardBG.render_grid_play_line(gc, (pos1Copy[0] + 1, pos1Copy[1]), (pos2Copy[0], pos2Copy[1]))
            pos1Copy = (pos1Copy[0] + 1, pos1Copy[1])
            pos2Copy = (pos2Copy[0] + 1, pos2Copy[1])
            if pos1Copy[0] > 200:
                pos1Copy = pos1
                pos2Copy = pos2

    def render(self):
        cdc = wx.ClientDC(self)
        self.PrepareDC(cdc)
        gc = wx.BufferedDC(cdc, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        gc.Clear()
        # dc.SetUserScale(2, 2)

        # thread = Thread(target=self.render_play_line, args=(gc, (10, 10), (10, 300)))
        # thread.start()
        gc.SetBrush(wx.Brush('#00aaaa', wx.SOLID))
        gc.SetPen(wx.Pen('#00aaaa', 1, wx.SOLID))

        scrolliewData = (self.GetViewStart()[0] * self.scrollStep,
                         self.GetViewStart()[1] * self.scrollStep,
                         *self.GetTargetWindow().BestVirtualSize)

        self._soundBoardBG.render(gc)

        for obj in self._canvasObjects:
            obj.render(gc)

        if self.instrumentToDraw:
            self.instrumentToDraw.render(gc)

        if self._selectedObject:
            self._selectedObject.RenderSelection(gc)

        if (self._objectUnderCursor or self._draggingObject) and not self._resizingObject:
            if self._objectUnderCursor:
                self._objectUnderCursor.RenderHighlighting(gc)
            else:
                self._draggingObject.RenderHighlighting(gc)

        if (self._objectUnderResizingGrippers or self._resizingObject) and not self._draggingObject:
            if self._objectUnderResizingGrippers:
                self._objectUnderResizingGrippers.RenderResizing(gc)
            else:
                self._resizingObject.RenderResizing(gc)

    def OnMouseMotion(self, evt):
        pos = self.CalcUnscrolledPosition(evt.GetPosition()).Get()
        self._objectUnderCursor = self.FindObjectUnderPoint(pos)
        self._objectUnderResizingGrippers = self.FindResizingGrippersObjectUnderPoint(pos)

        if evt.RightIsDown():
            self.remove_element_in_pos(pos)
        if self._objectUnderCursor and evt.LeftIsDown():
            self.pushObjectOnTopOfCanvas(self._objectUnderCursor)
        if self._objectUnderResizingGrippers and evt.LeftIsDown():
            self.pushObjectOnTopOfCanvas(self._objectUnderResizingGrippers)

        if not evt.LeftIsDown():
            self._draggingObject = None
            self._resizingObject = None

        if (
                evt.LeftIsDown() and evt.Dragging() and self._draggingObject and not self._resizingObject) or self.instrumentToDraw:
            x, y = self._elementStartDragPosition if self._elementStartDragPosition else [
                self.instrumentToDraw.boundingBoxDimensions[0] / 2, self.instrumentToDraw.boundingBoxDimensions[1] / 2]
            newX = pos[0] - x
            newY = pos[1] - y

            # Check canvas boundaries
            newX = min(newX, self.canvasDimensions[0] - (
            self._draggingObject.boundingBoxDimensions[0] if not self.instrumentToDraw else
            self.instrumentToDraw.boundingBoxDimensions[0]))
            newY = min(newY, self.canvasDimensions[1] - (
            self._draggingObject.boundingBoxDimensions[1] if not self.instrumentToDraw else
            self.instrumentToDraw.boundingBoxDimensions[1]))
            newX = max(newX, self._soundBoardBG.xBegin)
            newY = max(newY, self._soundBoardBG.yBegin)
            rx = roundup(newX - self._soundBoardBG.xBegin - (self._soundBoardBG.columnWidth / 2),
                         (self._soundBoardBG.columnWidth + self._soundBoardBG.columnSpacing))
            ry = roundup(newY - self._soundBoardBG.yBegin - (self._soundBoardBG.rowHeight / 2),
                         (self._soundBoardBG.rowHeight + self._soundBoardBG.rowSpacing))

            if self.instrumentToDraw:
                self.instrumentToDraw.position = [rx + self._soundBoardBG.xBegin, ry + + self._soundBoardBG.yBegin]
            else:
                self._draggingObject.position = [rx + self._soundBoardBG.xBegin, ry + + self._soundBoardBG.yBegin]

        if evt.LeftIsDown() and self._resizingObject and self._elementResizePosition and not self._draggingObject:
            x, y = self._elementResizePosition
            newX = pos[0] - x

            if self._resizingObject.leftGripper == True:
                rx = roundup(newX - self._soundBoardBG.xBegin - (self._soundBoardBG.columnWidth / 2),
                             (self._soundBoardBG.columnWidth + self._soundBoardBG.columnSpacing))
                newWidth = self._resizingObject.boundingBoxDimensions[0] + self._resizingObject.position[
                    0] - rx - self._soundBoardBG.xBegin

                if newWidth >= self._resizingObject.minimumClipSize[0]:
                    self._resizingObject.position = [rx + self._soundBoardBG.xBegin, self._resizingObject.position[1]]
                    self._resizingObject.boundingBoxDimensions = \
                        [newWidth,
                         self._resizingObject.boundingBoxDimensions[1]]
            else:
                rx = roundup(newX - self._soundBoardBG.xBegin - (self._soundBoardBG.columnWidth / 2),
                             (self._soundBoardBG.columnWidth + self._soundBoardBG.columnSpacing))
                newWidth = rx + self._soundBoardBG.xBegin - self._resizingObject.position[0]
                if newWidth >= self._resizingObject.minimumClipSize[1]:
                    self._resizingObject.boundingBoxDimensions = \
                        [newWidth,
                         self._resizingObject.boundingBoxDimensions[1]]

        self.render()
        self._lastDraggingPosition = [min(pos[0], self.canvasDimensions[0]), min(pos[1], self.canvasDimensions[1])]

    def OnMouseLeftDown(self, evt):
        if self.instrumentToDraw:
            self._canvasObjects.append(self.instrumentToDraw)
            self.instrumentToDraw = None

        if self._objectUnderCursor:
            if evt.ControlDown() and self._objectUnderCursor.clonable:
                text = self._objectUnderCursor.GetCloningNodeDescription()
                data = wx.TextDataObject(text)
                dropSource = wx.DropSource(self)
                dropSource.SetData(data)
                dropSource.DoDragDrop(wx.Drag_AllowMove)
            else:
                if self._objectUnderCursor.movable and not self._resizingObject and not self._draggingObject:
                    self._lastDraggingPosition = self.CalcUnscrolledPosition(evt.GetPosition()).Get()
                    self._elementStartDragPosition = \
                        (abs(self._lastDraggingPosition[0] - self._objectUnderCursor.position[0])
                         , abs(self._lastDraggingPosition[1] - self._objectUnderCursor.position[1]))
                    self._draggingObject = self._objectUnderCursor

        if self._objectUnderResizingGrippers and not self._draggingObject and not self._resizingObject:
            if self._objectUnderResizingGrippers.resizable:
                self._lastDraggingPosition = self.CalcUnscrolledPosition(evt.GetPosition()).Get()
                self._resizingObject = self._objectUnderResizingGrippers
                if self._lastDraggingPosition[0] <= self._objectUnderResizingGrippers.position[0]:
                    self._resizingObject.leftGripper = True

                    self._elementResizePosition = \
                        (self._lastDraggingPosition[0] - self._objectUnderResizingGrippers.position[0]
                         , self._lastDraggingPosition[1] - self._objectUnderResizingGrippers.position[1])
                else:
                    self._resizingObject.leftGripper = False

                    self._elementResizePosition = \
                        (self._lastDraggingPosition[0] - self._objectUnderResizingGrippers.position[0] -
                         self._objectUnderResizingGrippers.boundingBoxDimensions[0]
                         , self._lastDraggingPosition[1] - self._objectUnderResizingGrippers.position[1])

        if not self._objectUnderCursor or self._objectUnderResizingGrippers:
            return

        self._lastLeftDownPos = evt.GetPosition()

    def OnMouseLeftUp(self, evt):
        # Selection
        if (self._lastLeftDownPos
                and self._lastLeftDownPos[0] == evt.GetPosition()[0]
                and self._lastLeftDownPos[1] == evt.GetPosition()[1]
                and self._objectUnderCursor
                and self._objectUnderCursor.selectable):
            self._selectedObject = self._objectUnderCursor
        elif not self._resizingObject and not self._draggingObject:
            self._selectedObject = None

    def OnMouseRightDown(self, evt):
        self.remove_element_in_pos(self.CalcUnscrolledPosition(evt.GetPosition()).Get())

    def remove_element_in_pos(self, pos):
        if self.instrumentToDraw:
            self.instrumentToDraw = None
        else:
            objIndex = self.FindObjectUnderPoint(pos)
            if objIndex != None and self._canvasObjects[self._canvasObjects.index(objIndex)]:
                del self._canvasObjects[self._canvasObjects.index(objIndex)]
            if self._objectUnderCursor:
                self._objectUnderCursor = None
            if self._objectUnderResizingGrippers:
                self._objectUnderResizingGrippers = None

    def FindObjectUnderPoint(self, pos):
        # Check all objects on a canvas.
        for obj in reversed(self._canvasObjects):
            objUnderCursor = obj.ReturnObjectUnderCursor(pos)
            if objUnderCursor:
                return objUnderCursor
        return None

    def FindResizingGrippersObjectUnderPoint(self, pos):
        # Check all objects on a canvas.
        for obj in reversed(self._canvasObjects):
            objUnderCursor = obj.ReturnObjectUnderCursorResizingArea(pos)
            if objUnderCursor:
                return objUnderCursor
        return None

    def pushObjectOnTopOfCanvas(self, obj):
        if obj in self._canvasObjects:
            self._canvasObjects.remove(obj)
            self._canvasObjects.append(obj)


def roundup(x, y):
    return int(math.ceil(x / y)) * y
