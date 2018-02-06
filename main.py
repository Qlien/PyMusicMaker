import wx
from toolbarHelper import *
from Frames.plugins_panel import *
from Frames.instruments_panel import *
from Frames.soundboard_panel import *
import json


class MDIFrame(wx.MDIParentFrame):
    def __init__(self):
        wx.MDIParentFrame.__init__(self, None, -1, "PyMusicMaker", size=(1400, 800))
        menu = wx.Menu()
        menu.Append(5001, "Exit")
        menu.Append(5002, "Save")
        menu.Append(5003, "Load")
        menu.Append(5004, "Save to wav")
        menubar = wx.MenuBar()
        menubar.Append(menu, "&File")
        self.SetMenuBar(menubar)

        self.contentNotSaved = False

        self.play_menu = PlayMenu(self)
        self.generate_windows()

        self.Bind(wx.EVT_MENU, self.on_exit, id=5001)
        self.Bind(wx.EVT_MENU, self.on_save, id=5002)
        self.Bind(wx.EVT_MENU, self.on_load, id=5003)
        self.Bind(wx.EVT_MENU, self.save_to_wav, id=5004)

    def generate_windows(self):

        self.pluginsPanel = generate_plugins_panel(self)
        self.instrumentsPanel = generate_instruments_panel(self)
        self.pluginsPanel.set_instruments_panel(self.instrumentsPanel)
        self.soundBoardPanel = generate_soundboard_panel(self, self.instrumentsPanel, self.play_menu)

        self.play_menu.bind_play_button(self.soundBoardPanel.on_play)
        self.play_menu.bind_stop_button(self.soundBoardPanel.on_stop)

    def destroy_windows(self):
        self.play_menu.unbind_play_button(self.soundBoardPanel.on_play)
        self.play_menu.unbind_stop_button(self.soundBoardPanel.on_stop)
        self.instrumentsPanel.Destroy()
        self.instrumentsPanel = None
        self.pluginsPanel.Destroy()
        self.pluginsPanel = None
        self.soundBoardPanel.Destroy()
        self.soundBoardPanel = None

    def save_to_wav(self, event):
        with wx.FileDialog(self, "Save wav file", wildcard="wav files (*.wav)|*.wav",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                import pygame, wave
                with wave.open(pathname, 'w') as file:
                    file.setframerate(44000)
                    file.setnchannels(1)
                    file.setsampwidth(2)
                    sound = self.soundBoardPanel.generate_sound()
                    snd = pygame.mixer.Sound(sound)
                    file.writeframesraw(snd.get_raw())
                    file.close()
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def on_exit(self, evt):
        self.Close(True)

    def on_save(self, evt):
        with wx.FileDialog(self, "Save XYZ file", wildcard="pmm files (*.pmm)|*.pmm",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    json.dump(self.get_serialization_data(), file)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def get_serialization_data(self):
        instriments = self.instrumentsPanel.get_serialization_data()
        notes = self.soundBoardPanel.get_serialization_data()
        return {'instruments': instriments, 'notes': notes}

    def on_load(self, evt):
        if self.contentNotSaved:
            if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

            # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open XYZ file", wildcard="pmm files (*.pmm)|*.pmm",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as file:
                    self.load_from_file(file)
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def load_from_file(self, file):
        jsonData = json.load(file)
        self.destroy_windows()
        self.pluginsPanel = generate_plugins_panel(self)
        self.instrumentsPanel = generate_instruments_panel(self)
        for instrument in jsonData['instruments']:
            self.instrumentsPanel.add_instrument(getattr(self.pluginsPanel.plugins['Plugins.' + instrument[0].lower()], instrument[0]), instrument[1])

        self.pluginsPanel.set_instruments_panel(self.instrumentsPanel)
        self.soundBoardPanel = generate_soundboard_panel(self, self.instrumentsPanel, self.play_menu)
        for note in jsonData['notes']:
            self.soundBoardPanel.add_note(note[1])

        self.play_menu.bind_play_button(self.soundBoardPanel.on_play)
        self.play_menu.bind_stop_button(self.soundBoardPanel.on_stop)

        pass

app = wx.App()
frame = MDIFrame()
frame.Show()
app.MainLoop()