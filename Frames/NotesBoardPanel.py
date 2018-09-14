import math

from Frames.MoveMe.Canvas.soundBoardBG import *


def generate_left_notes_panel(parent, boardType):
    s = wx.BoxSizer(wx.VERTICAL)
    soundBoardPanel = NotesBoard(parent, boardType)
    s.Add(soundBoardPanel)
    return soundBoardPanel


class NotesBoard(wx.ScrolledWindow):
    def __init__(self, parent, windowType, id=-1, size=wx.DefaultSize, **kw):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.neighbouring_horizontal_view = None
        self.SetMinSize((70, 110))

        self.parent = parent

        self.scrollStep = kw.get("scrollStep", 30)
        self._soundBoardBG = SoundBoardBG(parts=0, parent=self, boardType=windowType)
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

        self.SetVirtualSize(*self.canvasDimensions)

        self.buffer = wx.Bitmap(*self.canvasDimensions)
        dc = wx.BufferedDC(None, self.buffer)
        dc.Clear()
        self.do_drawing(dc)

        self.Bind(wx.EVT_SCROLLWIN, self.scroll_evt)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.horizontalInterval = 40
        self.verticalInterval = 20

    def scroll_evt(self, evt):
        virtual_size = self.GetViewStart()
        if self.neighbouring_horizontal_view is not None:
            self.neighbouring_horizontal_view.Scroll(self.neighbouring_horizontal_view.GetViewStart()[0]
                                               , virtual_size[1])
        self.render()
        evt.Skip()

    def Destroy(self):
        try:
            super(wx.ScrolledWindow, self).Destroy()
            self.parent.Destroy()
        except:
            print('already deleted')

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        dc.Clear()
        self.do_drawing(dc)

    def do_drawing(self, dc, printing=False):
        self._soundBoardBG.render(dc)

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

    def render(self):
        cdc = wx.ClientDC(self)
        self.PrepareDC(cdc)
        gc = wx.BufferedDC(cdc, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        gc.Clear()

        gc.SetBrush(wx.Brush('#00aaaa', wx.SOLID))
        gc.SetPen(wx.Pen('#00aaaa', 1, wx.SOLID))
        self._soundBoardBG.render(gc)

def roundup(x, y):
    return int(math.ceil(x / y)) * y
