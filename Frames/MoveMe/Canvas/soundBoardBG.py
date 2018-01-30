import wx


basicNotesKeys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
keys = [ 2, 3, 4, 5, 6]
def frequencyFormula(n):
    return (2**((n-49)/12))*440 #hz

firstKeyN = 28

class Note(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "No name")
        self.halfNote = kwargs.get("halfNote", False)
        self.frequency = kwargs.get("frequency", 0)
        self.key = kwargs.get("key", 0)

    def frequencyFormula(self, n):
        return (2 ** ((n - 49) / 12)) * 440  # hz

    def __hash__(self):
        return self.frequency

    def __eq__(self, other):
        return self.frequency == other.frequency \
               and self.halfNote == other.halfNote \
               and self.key == other.key

    def __lt__(self, other):
        return self.frequency < other.frequency

class SoundBoardBG(object):
    def __init__(self, **kwargs):
        self.zoom = kwargs.get("zoom", 1)
        self.parts = kwargs.get("parts", 20)
        self.subParts = kwargs.get("subParts", 4)
        self.columnsInSubPart = kwargs.get("columnsInSubPart", 4)
        self.columnWidth = kwargs.get("columnWidth", 30)
        self.noteHeight = kwargs.get("noteHeight", 20)
        self.rowHeight = kwargs.get("rowHeight", 20)
        self.rowSpacing = kwargs.get("rowSpacing", 2)
        self.columnSpacing = kwargs.get("columnSpacing", 1)
        self.minimumNoteWidth = kwargs.get("minimumNoteWidth", 20)
        self.xBegin = kwargs.get("xBegin", 40)
        self.yBegin = kwargs.get("yBegin", 20)
        self.notes = []

        for k_1, key in enumerate(keys):
            for k_2, note in enumerate(basicNotesKeys):
                self.notes.append(
                    Note(name = note,
                         halfNote = True if '#' in note else False,
                         frequency = frequencyFormula(firstKeyN + (k_2 + 1) * k_2),
                         key = key))


    def Render(self, gc):

        self.RenderGrid(gc)
        for k, note in enumerate(self.notes):
            self.RenderNoteInPanel(note, position = (-2, self.yBegin + k * (self.noteHeight + self.rowSpacing)), size = (40,20), gc = gc)

    def RenderGrid(self, gc):

        #columns
        gc.SetPen(wx.Pen('#000000', 1, wx.SOLID))
        for part in range(self.parts):
            for subPart in range(self.subParts):
                for column in range(self.columnsInSubPart):
                    col = (column + (self.columnsInSubPart * subPart) + (part * self.columnsInSubPart * self.subParts))
                    if (col % (self.columnsInSubPart * self.subParts)) == 0:
                        gc.SetPen(wx.Pen('#000000', 1, wx.SOLID))
                    elif (col % (self.columnsInSubPart)) == 0:
                        gc.SetPen(wx.Pen('#9c9c9c', 1, wx.SOLID))
                    else:
                        gc.SetPen(wx.Pen('#c9c9c9', 1, wx.SOLID))

                    gc.DrawLines(points=[(self.xBegin + col * (self.columnWidth + self.columnSpacing),
                                          self.yBegin),
                                         (self.xBegin + col * (self.columnWidth + self.columnSpacing),
                                          self.yBegin + (len(self.notes)) * (self.noteHeight + self.rowSpacing))])


        gc.DrawLines(points=[(self.xBegin + (self.parts * self.columnsInSubPart * self.subParts) * (self.columnWidth + self.columnSpacing),
                              self.yBegin),
                             (self.xBegin + (self.parts * self.columnsInSubPart * self.subParts) * (self.columnWidth + self.columnSpacing),
                              self.yBegin + (len(self.notes)) * (self.noteHeight + self.rowSpacing))])

        #rows
        for note in range(len(self.notes) + 1):
            gc.DrawLines(points=[(self.xBegin
                                  , self.yBegin + note * (self.rowHeight + self.rowSpacing)),
                                 (self.xBegin + (self.parts * self.columnsInSubPart * self.subParts * (self.columnWidth + self.columnSpacing))
                                  , self.yBegin + note * (self.rowHeight + self.rowSpacing))])


    def RenderNoteInPanel(self, note, position, size, gc):
        gc.SetPen(wx.Pen('#00ac00' if note.halfNote else '#acacac', 1, wx.SOLID))
        gc.SetBrush(wx.Brush('#ffffff' if note.halfNote else '#000000', wx.SOLID))
        gc.DrawRoundedRectangle(position[0],
                                position[1],
                                size[0],
                                size[1], 3)


        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        # font.SetForegroundColour((255, 0, 0))
        color = wx.Colour()
        color.Set('#000000') if note.halfNote else color.Set('#ffffff')
        gc.SetFont(font)

        textDimensions = gc.GetTextExtent(note.name)

        gc.DrawTextList([note.name + ' ' + str(note.key)]
                        , [(position[0] + 10, position[1] + size[1] / 2 - textDimensions[1] / 2)]
                        , [color])




