# Created by Dmytro Konobrytskyi, 2013 (github.com/Akson/MoveMe)
from Frames.MoveMe.Canvas.Objects.SimpleBoxNode import SimpleBoxNode, ObjectState


class SimpleTextBoxNode(SimpleBoxNode):
    def __init__(self, **kwargs):
        super(SimpleTextBoxNode, self).__init__(**kwargs)
        self.text = kwargs.get("text", "No text")
        self.state = ObjectState.IDLE
        self._leftGripper = False

    def render(self, gc):
        textDimensions = gc.GetTextExtent(self.text)
        self.boundingBoxDimensions = [self.boundingBoxDimensions[0], self.boundingBoxDimensions[1]]
        super(SimpleTextBoxNode, self).render(gc)

        gc.DrawText(self.text, self.position[0] + self.boundingBoxDimensions[0] / 2 - textDimensions[0] / 2,
                    self.position[1] + self.boundingBoxDimensions[1] / 2 - textDimensions[1] / 2)

    def GetCloningNodeDescription(self):
        return self.text

    def get_serialization_data(self):
        d = {'text': self.text,
             'boundingBoxDimensions': self.boundingBoxDimensions,
             'color': self.color.GetRGBA(),
             'position': self.position}

        return 'SimpleTextBoxNode', d
