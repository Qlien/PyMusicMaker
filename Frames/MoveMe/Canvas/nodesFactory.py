# Created by Dmytro Konobrytskyi, 2013 (github.com/Akson/MoveMe)
from Frames.MoveMe.Canvas.Objects.simpleTextNote import SimpleTextNote


class NodesFactory(object):
    def __init__(self):
        pass

    def CreateNodeFromDescription(self, **kwargs):
        return SimpleTextNote(**kwargs)
