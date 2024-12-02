from enum import Enum


class WrangleNodes(Enum):
    ATTRIB_WRANGLE = ('Attrib Wrangle', 'attribwrangle')
    DEFORMATION_WRANGLE = ('Deformation Wrangle', 'deformationwrangle')
    RIG_ATTRIB_WRANGLE = ('Rig Attrib Wrangle', 'rigattribwrangle')
    VOLUME_WRANGLE = ('Volume Wrangle', 'volumewrangle')

    GEOMETRY_WRANGLE = ('Geometry Wrangle', 'geometrywrangle')
    POP_WRANGLE = ('POP Wrangle', 'popwrangle')

    WRANGLE = ('Wrangle', 'wrangle')

    CHANNEL_WRANGLE = ('Channel Wrangle', 'channelwrangle')
