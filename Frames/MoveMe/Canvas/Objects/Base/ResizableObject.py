# Created by Dmytro Konobrytskyi, 2013 (github.com/Akson/MoveMe)
from Frames.MoveMe.Canvas.Objects.Base.CanvasObject import CanvasObject


class ResizableObject(CanvasObject):
    def __init__(self, **kwargs):
        super(ResizableObject, self).__init__(**kwargs)

        self.boundingBoxDimensions = kwargs.get("boundingBoxDimensions", [31, 22])
        self.minimumClipSize = kwargs.get("minimumClipSize", [31, 22])
        self.resizable = True