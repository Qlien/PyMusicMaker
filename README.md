# PyMusicMaker
Simple tracker like music maker made in Python.

PyMusicMaker allows to make melodies by combining sounds made in various plugins, and then save them as real sounds.

![app screen](https://i.imgur.com/ZWSon65.png)

Main window consists of three key subwindows:

Plugins window is list of included sound generators which depending on various parameters can make sounds. Each plugin to be recognized by PyMusicMaker has to be placed in plugins window and inherit from PluginBase class. Parent class make sure basic parameters and functions are delivered by the plugin. Parameters are name, color. Plugin has to provide generate_sound method which makes sounds based on given parameters. By clicking generate sound on plugins window, new "instrument is placed in instruments window. (by pressing spacebar in currently opened plugin sample sound is generated)

Instruments window allows to pick generated sounds, now called instruments and place them on Sounds window

Sounds window allows user to draw sounds and make more complex melodies. Sound parts san be dragged from instruments window by drag and drop functionality or just by pressing spacebar after selecting particular instrument and having active sounds window. Sounds can be moved and resized. By clicking left mouse button sound is placed on the grid. To erase sounds sound has to be clicked by right mouse button. Each column of sounds window represents sound note whoch is described by frequency which is then applied to sound generation function provided by plugin represented by instrument. Notes are visible on the left side of window.

Sounds made in PyMusicMaker can be saved and loaded by selecting specified option in File menu button. Sounds can be saved as wav files.

bits per minute (field present by the play and pause buttons) can be modified changing tempo of the sound.

Libraries used in project, and necessary to run app:
-	wxPython
-	PyAudio
-	NumPy
-	scipy.io
