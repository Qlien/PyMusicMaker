import math
import threading

import numpy as np

from Frames.MoveMe.Canvas.nodesFactory import NodesFactory
from Frames.MoveMe.Canvas.Objects.simpleTextNote import SimpleTextNote
from Frames.MoveMe.Canvas.soundBoardBG import *
from bin.plugin import PluginType
from bin.soundGeneration import SoundPanelElement

BUFFERED = 0


class TextDropTarget(wx.TextDropTarget):
    def __init__(self, canvas):
        wx.TextDropTarget.__init__(self)
        self._canvas = canvas

    def OnDropText(self, x, y, data):
        self._canvas.create_node_from_description_at_position(data, [x, y])
        return 0


class SoundBoardSubWindow(wx.ScrolledWindow):
    def __init__(self, parent, windowType, soundGenerator, id=-1, size=wx.DefaultSize, **kw):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.play_menu = None
        self._objectUnderCursor = None
        self._draggingObject = None
        self._lastDraggingPosition = None
        self._lastLeftDownPos = None
        self._selectedObject = None
        self._objectUnderResizingGrippers = None
        self._resizingObject = None
        self._elementStartDragPosition = None
        self._elementResizePosition = None
        self._firstTimeRender = True
        self.instrumentToDraw = None
        self.lastMousePos = [0, 0]
        self.instrumentsPanel = None
        self.neighbouring_vertical_view = None
        self.neighbouring_horizontal_view = None
        self.soundGenerator = soundGenerator
        self.windowType = windowType
        self.SetMinSize((100, 110))

        self.parent = parent

        self.scrollStep = kw.get("scrollStep", 30)
        self._soundBoardBG = SoundBoardBG(parts=20, boardType=windowType, parent=self)
        self.canvasDimensions = kw.get("canvasDimensions"
                                       , [1 + self._soundBoardBG.xBegin +
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
        self._nodesFactory = NodesFactory()
        self.SetVirtualSize(*self.canvasDimensions)

        self.buffer = wx.Bitmap(*self.canvasDimensions)
        dc = wx.BufferedDC(None, self.buffer)
        dc.Clear()
        self.do_drawing(dc)

        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_right_down)
        self.Bind(wx.EVT_SCROLLWIN, self.scroll_evt)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.SetDropTarget(TextDropTarget(self))

        self.horizontalInterval = 40
        self.verticalInterval = 20

    def scroll_evt(self, evt):
        virtual_size = self.GetViewStart()
        if self.neighbouring_vertical_view is not None:
            self.neighbouring_vertical_view.Scroll(virtual_size[0]
                                                   , self.neighbouring_vertical_view.GetViewStart()[1])
        if self.neighbouring_horizontal_view is not None:
            self.neighbouring_horizontal_view.Scroll(self.neighbouring_horizontal_view.GetViewStart()[0]
                                                     , virtual_size[1])
        evt.Skip()
        pass

    def set_instruments_panel(self, instruments_panel):
        self.instrumentsPanel = instruments_panel

    def set_play_menu(self, play_menu):
        self.play_menu = play_menu

    def Destroy(self):
        try:
            super(wx.ScrolledWindow, self).Destroy()
            self.parent.Destroy()
        except:
            print('already deleted')

    def add_note(self, params):
        self._canvasObjects.append(SimpleTextNote(**params))

    def get_serialization_data(self):
        return [noteData.get_serialization_data() for noteData in self._canvasObjects]

    def generate_sound_representation(self):
        small_parts = self._soundBoardBG.columnsInSubPart * self._soundBoardBG.subParts * self._soundBoardBG.parts
        x_distance = self._soundBoardBG.columnWidth + self._soundBoardBG.columnSpacing
        y_distance = self._soundBoardBG.rowHeight + self._soundBoardBG.rowSpacing
        x_beginning = self._soundBoardBG.xBegin
        y_beginning = self._soundBoardBG.yBegin

        instruments_dict = dict()

        for i in range(small_parts):

            notes_in_place = [sound for sound in self._canvasObjects if
                              sound.position[0] == (x_beginning + x_distance * i)]
            for note in notes_in_place:
                soundElement = SoundPanelElement(self.instrumentsPanel.instruments[note.text]
                                                 , self.windowType
                                                 , note.boundingBoxDimensions[0] / x_distance
                                                 , int((note.position[1] - y_beginning) / y_distance))
                if i not in instruments_dict:
                    instruments_dict[i] = [soundElement]
                else:
                    instruments_dict[i].append(soundElement)

        return instruments_dict

    def on_char(self, event):
        var = self.GetViewStart()
        if event.GetUnicodeKey() == wx.WXK_SPACE:
            tempInstrument = self.instrumentsPanel.get_selected_instrument()
            if tempInstrument and tempInstrument.pluginType == PluginType.FILTER \
                    and self.windowType == PluginType.FILTER:
                dim = self._canvasObjects[-1].boundingBoxDimensions if self._canvasObjects else [31, 22]
                self.instrumentToDraw = \
                    SimpleTextNote(position=self.sound_rounded_pos(self.lastMousePos)
                                   , text=tempInstrument.pluginName, boundingBoxDimensions=dim
                                   , color=tempInstrument.get_color())
            elif tempInstrument and tempInstrument.pluginType == PluginType.SOUNDGENERATOR \
                    and self.windowType == PluginType.SOUNDGENERATOR:
                dim = self._canvasObjects[-1].boundingBoxDimensions if self._canvasObjects else [31, 22]
                self.instrumentToDraw = \
                    SimpleTextNote(position=self.sound_rounded_pos(self.lastMousePos)
                                   , text=tempInstrument.pluginName, boundingBoxDimensions=dim
                                   , color=tempInstrument.get_color())

        elif event.GetKeyCode() == wx.WXK_DELETE:
            if self._selectedObject and self._selectedObject.deletable:
                self._selectedObject.Delete()
                if self._selectedObject in self._canvasObjects:
                    self._canvasObjects.remove(self._selectedObject)
                self._selectedObject = None
        else:
            event.Skip()

        # Update object under cursor
        pos = self.CalcUnscrolledPosition(event.GetPosition()).Get()
        self._objectUnderCursor = self.find_object_under_point(pos)

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

    def create_node_from_description_at_position(self, node_description, pos):

        if self.instrumentsPanel.instruments[node_description].pluginType == PluginType.FILTER \
                and self.windowType == PluginType.FILTER:
            self.create_note_subpart(node_description, pos)
        elif self.instrumentsPanel.instruments[node_description].pluginType == PluginType.SOUNDGENERATOR \
                and self.windowType == PluginType.SOUNDGENERATOR:
            self.create_note_subpart(node_description, pos)

    def create_note_subpart(self, node_description, pos):
        node = self._nodesFactory.CreateNodeFromDescription(text=node_description,
                                                            color=self.instrumentsPanel.instruments[
                                                                node_description].get_color())
        self.parent.SetFocus()
        if node:
            node.position = self.sound_rounded_pos(pos)
            self._canvasObjects.append(node)
            self.render()

    def sound_rounded_pos(self, pos):

        newX = min(pos[0], self.canvasDimensions[0])
        newY = min(pos[1], self.canvasDimensions[1])
        newX = max(newX, self._soundBoardBG.xBegin)
        newY = max(newY, self._soundBoardBG.yBegin)
        newX = newX - ((newX - self._soundBoardBG.xBegin) % (
                self._soundBoardBG.columnWidth + self._soundBoardBG.columnSpacing))
        newY = newY - (
                (newY - self._soundBoardBG.yBegin) % (self._soundBoardBG.rowHeight + self._soundBoardBG.rowSpacing))
        return newX, newY

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

        gc.SetBrush(wx.Brush('#00aaaa', wx.SOLID))
        gc.SetPen(wx.Pen('#00aaaa', 1, wx.SOLID))
        self._soundBoardBG.render(gc)

        for obj in self._canvasObjects:
            obj.render(gc)

        if self.instrumentToDraw:
            self.instrumentToDraw.render(gc)

        if self._selectedObject:
            self._selectedObject.render_selection(gc)

        if (self._objectUnderCursor or self._draggingObject) and not self._resizingObject:
            if self._objectUnderCursor:
                self._objectUnderCursor.render_highlighting(gc)
            else:
                self._draggingObject.render_highlighting(gc)

        if (self._objectUnderResizingGrippers or self._resizingObject) and not self._draggingObject:
            if self._objectUnderResizingGrippers:
                self._objectUnderResizingGrippers.render_resizing(gc)
            else:
                self._resizingObject.render_resizing(gc)

    def on_mouse_motion(self, evt):
        self.lastMousePos = self.CalcUnscrolledPosition(evt.GetPosition()).Get()
        self._objectUnderCursor = self.find_object_under_point(self.lastMousePos)
        self._objectUnderResizingGrippers = self.find_resizing_grippers_object_under_point(self.lastMousePos)

        if evt.RightIsDown():
            self.remove_element_in_pos(self.lastMousePos)
        if self._objectUnderCursor and evt.LeftIsDown():
            self.push_object_on_top_of_canvas(self._objectUnderCursor)
        if self._objectUnderResizingGrippers and evt.LeftIsDown():
            self.push_object_on_top_of_canvas(self._objectUnderResizingGrippers)

        if not evt.LeftIsDown():
            self._draggingObject = None
            self._resizingObject = None

        if (evt.LeftIsDown() and evt.Dragging() and self._draggingObject and not self._resizingObject) \
                or self.instrumentToDraw:
            x, y = self._elementStartDragPosition if self._elementStartDragPosition else [
                self.instrumentToDraw.boundingBoxDimensions[0] / 2, self.instrumentToDraw.boundingBoxDimensions[1] / 2]
            newX = self.lastMousePos[0] - x
            newY = self.lastMousePos[1] - y

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
            newX = self.lastMousePos[0] - x

            if self._resizingObject.leftGripper:
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
        self._lastDraggingPosition = [min(self.lastMousePos[0], self.canvasDimensions[0]),
                                      min(self.lastMousePos[1], self.canvasDimensions[1])]
        evt.Skip()

    def on_mouse_left_down(self, evt):
        if self.instrumentToDraw:
            self._canvasObjects.append(self.instrumentToDraw)
            self.instrumentToDraw = None

        if self._objectUnderCursor:
            if evt.ControlDown():
                text = self._objectUnderCursor.get_cloning_node_description()
                data = wx.TextDataObject(text)
                dropSource = wx.DropSource(self)
                dropSource.SetData(data)
                dropSource.DoDragDrop(wx.Drag_AllowMove)
            else:
                if not self._resizingObject and not self._draggingObject:
                    self._lastDraggingPosition = self.CalcUnscrolledPosition(evt.GetPosition()).Get()
                    self._elementStartDragPosition = \
                        (abs(self._lastDraggingPosition[0] - self._objectUnderCursor.position[0])
                         , abs(self._lastDraggingPosition[1] - self._objectUnderCursor.position[1]))
                    self._draggingObject = self._objectUnderCursor

        if self._objectUnderResizingGrippers and not self._draggingObject and not self._resizingObject:
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

    def on_mouse_left_up(self, evt):
        # Selection
        if (self._lastLeftDownPos
                and self._lastLeftDownPos[0] == evt.GetPosition()[0]
                and self._lastLeftDownPos[1] == evt.GetPosition()[1]
                and self._objectUnderCursor):
            self._selectedObject = self._objectUnderCursor
        elif not self._resizingObject and not self._draggingObject:
            self._selectedObject = None

    def on_mouse_right_down(self, evt):
        self.remove_element_in_pos(self.CalcUnscrolledPosition(evt.GetPosition()).Get())

    def remove_element_in_pos(self, pos):
        if self.instrumentToDraw:
            self.instrumentToDraw = None
        else:
            objIndex = self.find_object_under_point(pos)
            if objIndex is not None and self._canvasObjects[self._canvasObjects.index(objIndex)]:
                del self._canvasObjects[self._canvasObjects.index(objIndex)]
            if self._objectUnderCursor:
                self._objectUnderCursor = None
            if self._objectUnderResizingGrippers:
                self._objectUnderResizingGrippers = None

    def find_object_under_point(self, pos):
        # Check all objects on a canvas.
        for obj in reversed(self._canvasObjects):
            objUnderCursor = obj.return_object_under_cursor(pos)
            if objUnderCursor:
                return objUnderCursor
        return None

    def find_resizing_grippers_object_under_point(self, pos):
        # Check all objects on a canvas.
        for obj in reversed(self._canvasObjects):
            objUnderCursor = obj.return_object_under_cursor_resizing_area(pos)
            if objUnderCursor:
                return objUnderCursor
        return None

    def push_object_on_top_of_canvas(self, obj):
        if obj in self._canvasObjects:
            self._canvasObjects.remove(obj)
            self._canvasObjects.append(obj)


def roundup(x, y):
    return int(math.ceil(x / y)) * y
