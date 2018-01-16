import wx
from wx.lib.masked import NumCtrl

iconsBase = 'Icons/typicons/png/'


def generate_play_menu_toolbar(parent, play_evt, pause_evt, repeat_evt, bpm_event, max_icons_size=(25, 25)):
    toolbar = parent.CreateToolBar()
    play_menu = toolbar.AddTool(wx.ID_ANY, 'Play', shortHelp='Play',
                            bitmap=scaleImage(iconsBase + 'play-button-1.png', max_icons_size=max_icons_size))

    pause_menu = toolbar.AddTool(wx.ID_ANY, 'Pause', shortHelp='Pause',
                            bitmap=scaleImage(iconsBase + 'pause-button.png', max_icons_size=max_icons_size))

    repeat_menu = toolbar.AddTool(wx.ID_ANY, 'Repeat', shortHelp='Repeat',
                            bitmap=scaleImage(iconsBase + 'repeat.png', max_icons_size=max_icons_size))
    toolbar.Realize()

    parent.Bind(wx.EVT_MENU, play_evt, play_menu)
    parent.Bind(wx.EVT_MENU, pause_evt, pause_menu)
    parent.Bind(wx.EVT_MENU, repeat_evt, repeat_menu)

    text = NumCtrl(toolbar, value = 128, pos=(100, 3), size=(50, 25), fractionWidth = 1, min = 20, max = 250)


def scaleImage(image_dir, max_icons_size=(25, 25)):
    return wx.Bitmap(
        wx.Bitmap(image_dir).ConvertToImage().Scale(max_icons_size[0], max_icons_size[1], wx.IMAGE_QUALITY_HIGH))
