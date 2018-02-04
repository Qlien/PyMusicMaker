# Created by Dmytro Konobrytskyi, 2013 (github.com/Akson/MoveMe)
from Frames.MoveMe.Canvas.Objects.SimpleTextBoxNode import SimpleTextBoxNode


class NodesFactory(object):
    def __init__(self):
        pass

    def CreateNodeFromDescription(self, **kwargs):
        return SimpleTextBoxNode(**kwargs)