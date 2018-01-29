# Created by Dmytro Konobrytskyi, 2013 (github.com/Akson/MoveMe)

import wx, sys, os, pygame
from Frames.MoveMe.Canvas.NodesFactory import NodesFactory
from Frames.MoveMe.Canvas.Objects.SimpleTextBoxNode import SimpleTextBoxNode
from Frames.MoveMe.Canvas.soundBoardBG import *
import math
BUFFERED = 0

# Define Text Drop Target class
class TextDropTarget(wx.TextDropTarget):
    def __init__(self, canvas):
        wx.TextDropTarget.__init__(self)
        self._canvas = canvas

    def OnDropText(self, x, y, data):
        self._canvas.CreateNodeFromDescriptionAtPosition(data, [x, y])


class Canvas(wx.ScrolledWindow):
    """
    Canvas stores and renders all nodes and node connections.
    It also handles all user interaction.
    """

    def __init__(self, parent, id = -1, size = wx.DefaultSize, **kw):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)

        self.scrollStep = kw.get("scrollStep", 10)
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
        # self.SetBackgroundColour("WHITE")

        # This list stores all objects on canvas
        self._canvasObjects = [SimpleTextBoxNode(position=[20, 20], text="A", boundingBoxDimensions=[30,20]),
                               SimpleTextBoxNode(position=[140, 40], text="B", boundingBoxDimensions=[30,20]),
                               SimpleTextBoxNode(position=[60, 120], text="C", boundingBoxDimensions=[30,20]),
                               SimpleTextBoxNode(position=[60, 120], text="C", boundingBoxDimensions=[30,20])]
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
        self._firstTimeRender = True;

        self._dcBuffer = wx.Bitmap(*self.canvasDimensions)
        self.Render()
        self.Bind(wx.EVT_PAINT,
                  lambda evt: wx.BufferedPaintDC(self, self._dcBuffer, wx.BUFFER_VIRTUAL_AREA)
                  )


        # Rendering initialization
        # self.Render()

        # User interaction handling
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)



        self.SetDropTarget(TextDropTarget(self))

        self.horizontalInterval = 40
        self.verticalInterval = 20


    def CreateNodeFromDescriptionAtPosition(self, nodeDescription, pos):
        node = self._nodesFactory.CreateNodeFromDescription(nodeDescription)
        if node:
            node.position = pos
            self._canvasObjects.append(node)
            self.Render()

    def Render(self):
        cdc = wx.ClientDC(self)
        self.PrepareDC(cdc)
        dc = wx.BufferedDC(cdc, self._dcBuffer)
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)

        gc.SetBrush(wx.Brush('#00aaaa', wx.SOLID))
        gc.SetPen(wx.Pen('#00aaaa', 1, wx.SOLID))

        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        gc.SetFont(font, wx.Colour())



        gc.PushState()
        self._soundBoardBG.Render(gc)
        gc.PopState()

        for obj in self._canvasObjects:
            gc.PushState()
            obj.Render(gc)
            gc.PopState()

        if self._selectedObject:
            gc.PushState()
            self._selectedObject.RenderSelection(gc)
            gc.PopState()

        if (self._objectUnderCursor or self._draggingObject) and not self._resizingObject:
            gc.PushState()
            if self._objectUnderCursor:
                self._objectUnderCursor.RenderHighlighting(gc)
            else:
                self._draggingObject.RenderHighlighting(gc)
            gc.PopState()

        if (self._objectUnderResizingGrippers or self._resizingObject) and not self._draggingObject:
            gc.PushState()
            if self._objectUnderResizingGrippers:
                self._objectUnderResizingGrippers.RenderResizing(gc)
            else:
                self._resizingObject.RenderResizing(gc)
            gc.PopState()


    def OnMouseMotion(self, evt):
        pos = self.CalcUnscrolledPosition(evt.GetPosition()).Get()
        self._objectUnderCursor = self.FindObjectUnderPoint(pos)
        self._objectUnderResizingGrippers = self.FindResizingGrippersObjectUnderPoint(pos)

        if self._objectUnderCursor:
            self.pushObjectOnTopOfCanvas(self._objectUnderCursor)
        if self._objectUnderResizingGrippers:
            self.pushObjectOnTopOfCanvas(self._objectUnderResizingGrippers)

        if not evt.LeftIsDown():
            self._draggingObject = None
            self._resizingObject = None

        if evt.LeftIsDown() and evt.Dragging() and self._draggingObject and not self._resizingObject:
            dx = pos[0] - self._lastDraggingPosition[0]
            dy = pos[1] - self._lastDraggingPosition[1]
            newX = self._draggingObject.position[0] + dx
            newY = self._draggingObject.position[1] + dy

            # Check canvas boundaries
            newX = min(newX, self.canvasDimensions[0] - self._draggingObject.boundingBoxDimensions[0])
            newY = min(newY, self.canvasDimensions[1] - self._draggingObject.boundingBoxDimensions[1])
            newX = max(newX, 0)
            newY = max(newY, 0)

            self._draggingObject.position = [newX, newY]


        if evt.LeftIsDown() and self._resizingObject and not self._draggingObject:
            dx = pos[0] - self._lastDraggingPosition[0]
            dy = pos[1] - self._lastDraggingPosition[1]
            newX = self._resizingObject.position[0] + dx
            newY = self._resizingObject.position[1] + dy

            if self._resizingObject.leftGripper == True:
                if self._resizingObject.boundingBoxDimensions[0] - dx >= 30:
                    self._resizingObject.position = [newX, self._resizingObject.position[1]]
                    self._resizingObject.boundingBoxDimensions = \
                        [self._resizingObject.boundingBoxDimensions[0] - dx,
                         self._resizingObject.boundingBoxDimensions[1]]
            else:
                if self._resizingObject.boundingBoxDimensions[0] + dx >= 30:
                    self._resizingObject.boundingBoxDimensions = \
                        [self._resizingObject.boundingBoxDimensions[0] + dx,
                         self._resizingObject.boundingBoxDimensions[1]]
        self.Render()



        self._lastDraggingPosition = [min(pos[0], self.canvasDimensions[0]), min(pos[1], self.canvasDimensions[1])]


    def OnMouseLeftDown(self, evt):
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
                    self._draggingObject = self._objectUnderCursor

        if self._objectUnderResizingGrippers and not self._draggingObject and not self._resizingObject:
            if self._objectUnderResizingGrippers.resizable:
                self._lastDraggingPosition = self.CalcUnscrolledPosition(evt.GetPosition()).Get()
                self._resizingObject = self._objectUnderResizingGrippers
                if self._lastDraggingPosition[0] <= self._objectUnderResizingGrippers.position[0]:
                    self._resizingObject.leftGripper = True
                else:
                    self._resizingObject.leftGripper = False


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

    def OnKeyPress(self, evt):
        if evt.GetKeyCode() == wx.WXK_DELETE:
            if self._selectedObject and self._selectedObject.deletable:
                self._selectedObject.Delete()
                if self._selectedObject in self._canvasObjects:
                    self._canvasObjects.remove(self._selectedObject)
                self._selectedObject = None
        else:
            evt.Skip()

        # Update object under cursor
        pos = self.CalcUnscrolledPosition(evt.GetPosition()).Get()
        self._objectUnderCursor = self.FindObjectUnderPoint(pos)

        self.Render()

def roundup(x, y):
    return int(math.ceil(x / y)) * y

class Frame(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1)

        self.display = PygameDisplay(self, -1)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.Kill)

        self.curframe = 0

        self.slider = wx.Slider(self, wx.ID_ANY, 5, 1, 10, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.slider.SetTickFreq(1)

        self.timer = wx.Timer(self)

        self.Bind(wx.EVT_SCROLL, self.OnScroll)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)

        self.timer.Start((1000.0 / self.display.fps))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.slider, 0, flag=wx.EXPAND)
        sizer.Add(self.display, 1, flag=wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()

    def Kill(self, event):
        self.display.Kill(event)
        pygame.quit()
        self.Destroy()

    def OnSize(self, event):
        self.Layout()

    def Update(self, event):
        self.curframe += 1
        #self.statusbar.SetStatusText("Frame %i" % self.curframe, 2)

    def OnScroll(self, event):
        self.display.linespacing = self.slider.GetValue()


class PygameDisplay(wx.Window):
    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent, ID)
        self.parent = parent
        self.hwnd = self.GetHandle()
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        os.environ['SDL_WINDOWID'] = str(self.hwnd)

        pygame.display.init()
        self.screen = pygame.display.set_mode([10000,1000])
        self.size = self.GetSize()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.Update, self.timer)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.fps = 60.0
        self.timespacing = 1000.0 / self.fps
        self.timer.Start(self.timespacing, False)

        self.linespacing = 5

    def Update(self, event):
        # Any update tasks would go here (moving sprites, advancing animation frames etc.)
        self.Redraw()

    def Redraw(self):
        self.screen.fill((0, 0, 0))

        cur = 0

        while cur <= self.size[1]:
            pygame.draw.aaline(self.screen, (255, 255, 255), (0, self.size[1] - cur), (cur, 0))

            cur += self.linespacing

        pygame.display.update()

    def OnPaint(self, event):
        self.Redraw()

    def OnSize(self, event):
        self.size = self.GetSize()

    def Kill(self, event):
        # Make sure Pygame can't be asked to redraw /before/ quitting by unbinding all methods which
        # call the Redraw() method
        # (Otherwise wx seems to call Draw between quitting Pygame and destroying the frame)
        self.Unbind(event=wx.EVT_PAINT, handler=self.OnPaint)
        self.Unbind(event=wx.EVT_TIMER, handler=self.Update, source=self.timer)