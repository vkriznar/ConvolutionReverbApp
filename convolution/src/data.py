
# Str variable for kivy to build IR signal buttons with Builder.fromString()
buttonStr = """
Button:
    size_hint_y: None
    height: 240
    text: "{0}"
    font_size: 32
    image: image
    on_release: app.ir_selected(self)
    Image:
        source: "../media/images/{1}.jpg"
        allow_stretch: True
        y: self.parent.y + self.parent.height - 240
        x: self.parent.x + 60
        size: (240, 240)
        id: image
"""

# IR Data locations
data = [
    "1st Baptist Church",
    "Creswell Crags",
    "Hamilton Mausoleum",
    "Hoffman Lime Kiln",
    "Jack Lyons Concert Hall",
    "Koli National Park - Winter",
    "Slinky",
    "St. Patrick Church Patrington",
    "Troller's Gill",
    "York Minster"
]
