import json

from Frames.instruments_panel import *
from Frames.plugins_panel import *
from Frames.soundboard_wrapper_panel import *
from bin.lookupTables import Lookups
from bin.serialization import SerializationBase
from bin.toolbarHelper import *
from bin.window import WindowBase
import numpy as np


class MainWindowFrame(wx.MDIParentFrame, WindowBase, SerializationBase):
    """represents main window frame and its content"""

    def __init__(self, parent=None, id=None, title=None, size=None):
        wx.MDIParentFrame.__init__(self, parent=parent, id=id, title=title, size=size)

        Lookups.initializeLookups()
        self.pluginsPanel = None
        self.instrumentsPanel = None
        self.sound_board_tuple = None
        self.sound_board_notes_panel = None
        self.sound_board_filters = None
        self.sound_board_panel = None
        self.play_menu = PlayMenu(self)

        self.generate_layout()
        self.generate_windows()
        self.bind_events()
        self.sound_board_panel.bpm_numCtrl = self.play_menu.bpm

    def generate_layout(self):
        """generates main menu aith buttons"""

        menu = wx.Menu()
        menu.Append(5005, "New")
        menu.Append(5001, "Exit")
        menu.Append(5002, "Save")
        menu.Append(5003, "Load")
        menu.Append(5004, "Save to wav")
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.on_new, id=5005)
        self.Bind(wx.EVT_MENU, self.on_exit, id=5001)
        self.Bind(wx.EVT_MENU, self.on_save, id=5002)
        self.Bind(wx.EVT_MENU, self.on_load, id=5003)
        self.Bind(wx.EVT_MENU, self.save_to_wav, id=5004)

    def bind_events(self):
        """binds buttons with actions"""

        self.play_menu.bind_play_button(self.sound_board_panel.on_play)
        self.play_menu.bind_stop_button(self.sound_board_panel.on_stop)

    def unbind_events(self):
        """unbinds buttons with actions"""

        self.play_menu.unbind_play_button(self.sound_board_panel.on_play)
        self.play_menu.unbind_stop_button(self.sound_board_panel.on_stop)

    def get_serialization_data(self):
        """gets serialized notes and instruments data"""

        instruments = self.instrumentsPanel.get_serialization_data()
        notes = self.sound_board_notes_panel.get_serialization_data()
        filters = self.sound_board_filters.get_serialization_data()
        return {'instruments': instruments, 'notes': notes, 'filters': filters}

    def set_serialization_data(self, data):
        """sets serialized notes and instruments"""

        for instrument in data['instruments']:
            self.instrumentsPanel.add_instrument(
                getattr(self.pluginsPanel.plugins['Plugins.' + instrument[0]], instrument[0]), instrument[1])
        for note in data['notes']:
            self.sound_board_notes_panel.add_note(note[1])
        for filterNote in data['filters']:
            self.sound_board_filters.add_note(filterNote[1])

        self.instrumentsPanel.update_instruments()

    def generate_windows(self):
        """creates basic windows inside main window"""

        self.pluginsPanel = generate_plugins_panel(self)
        self.instrumentsPanel = generate_instruments_panel(self)
        self.instrumentsPanel.set_frame_parent(self)
        self.pluginsPanel.set_instruments_panel(self.instrumentsPanel)
        self.pluginsPanel.set_frame_parent(self)

        self.sound_board_tuple = generate_soundboard_wrapper(self)
        self.sound_board_panel = self.sound_board_tuple[0]
        self.sound_board_notes_panel = self.sound_board_tuple[1]
        self.sound_board_notes_panel.set_instruments_panel(self.instrumentsPanel)
        self.sound_board_notes_panel.set_play_menu(self.play_menu)
        self.sound_board_filters = self.sound_board_tuple[2]
        self.sound_board_filters.set_instruments_panel(self.instrumentsPanel)

        self.sound_board_notes_panel.neighbouring_vertical_view = self.sound_board_filters
        self.sound_board_filters.neighbouring_vertical_view = self.sound_board_notes_panel

        self.sound_board_notes_panel.neighbouring_horizontal_view = self.sound_board_tuple[3]
        self.sound_board_tuple[3].neighbouring_horizontal_view = self.sound_board_notes_panel

        self.sound_board_filters.neighbouring_horizontal_view = self.sound_board_tuple[2]
        self.sound_board_tuple[2].neighbouring_horizontal_view = self.sound_board_filters

    def destroy_windows(self):
        """destroys windows inside main frame window"""

        self.play_menu.unbind_play_button(self.sound_board_panel.on_play)
        self.play_menu.unbind_stop_button(self.sound_board_panel.on_stop)
        self.sound_board_panel.Destroy()
        self.sound_board_panel = None
        self.instrumentsPanel.Destroy()
        self.instrumentsPanel = None
        self.pluginsPanel.Destroy()
        self.pluginsPanel = None
        self.sound_board_tuple = None

    def on_exit(self, evt):
        self.unbind_events()
        self.destroy()
        super(MainWindowFrame, self).on_exit()

    def on_new(self, evt):
        """loads saved serialized data back to program"""

        dlg = wx.MessageDialog(None, "Unsaved data will be lost",
                           style=wx.OK | wx.CENTRE | wx.CANCEL | wx.ICON_WARNING)
        dlg.SetOKCancelLabels("OK", "Cancel")
        result = dlg.ShowModal()

        if result == wx.ID_CANCEL:
            return  # the user changed their mind

        # Proceed loading the file chosen by the user
        try:
            self.unbind_events()
            self.destroy_windows()
            self.generate_windows()
            self.bind_events()
            self.sound_board_panel.bpm_numCtrl = self.play_menu.bpm
            self.instrumentsPanel.update_instruments()
        except IOError:
            wx.LogError("Something went wrong")

    def on_save(self, evt):
        """responsible for opening saving window, selecting name and saving serialized data"""

        with wx.FileDialog(self, "Save XYZ file", wildcard="pmm files (*.pmm)|*.pmm",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    json.dump(self.get_serialization_data(), file)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def on_load(self, evt):
        """loads saved serialized data back to program"""

        with wx.FileDialog(self, "Open XYZ file", wildcard="pmm files (*.pmm)|*.pmm",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as file:
                    self.unbind_events()
                    self.destroy_windows()
                    self.generate_windows()
                    self.bind_events()
                    self.sound_board_panel.bpm_numCtrl = self.play_menu.bpm
                    self.set_serialization_data(json.load(file))
                    self.instrumentsPanel.update_instruments()
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def save_to_wav(self, event):
        """transforms soundboard data to playable wav file"""

        with wx.FileDialog(self, "Save wav file", wildcard="wav files (*.wav)|*.wav",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                import scipy.io.wavfile
                scipy.io.wavfile.write(pathname, 44100, np.array(self.sound_board_panel.generate_sound(False)))
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)
