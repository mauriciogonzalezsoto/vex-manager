from enum import Enum


class WrangleNodes(Enum):
    ATTRIB_WRANGLE = 'attribwrangle'
    DEFORMATION_WRANGLE = 'deformationwrangle'
    RIG_ATTRIB_WRANGLE = 'rigattribwrangle'
    VOLUME_WRANGLE = 'volumewrangle'

    GEOMETRY_WRANGLE = 'geometrywrangle'
    POP_WRANGLE = 'popwrangle'

    WRANGLE = 'wrangle'

    CHANNEL_WRANGLE = 'channelwrangle'
