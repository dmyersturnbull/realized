# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

"""
Realized.
"""

from realized._meta import Metadata
from realized.misc.coordinates import Rectangle
from realized.dt import Resolution
from realized.dt.durations import Duration
from realized.dt.instants import Instant, InstantUtc, InstantWithOffset, InstantWithCity
from realized.dt.intervals import Interval
from realized.dt.repeats import RepeatEvent, RepeatDuration
from realized.biochem.wells import Well
from realized.biochem.well_sets import WellSet
from realized.biochem.registries import WELL_TYPES as PlateTypes


__version__ = Metadata.version


Well2x3 = PlateTypes.well_type(2, 3)
Well3x4 = PlateTypes.well_type(3, 4)
Well4x6 = PlateTypes.well_type(4, 6)
Well6x8 = PlateTypes.well_type(6, 8)
Well8x12 = PlateTypes.well_type(8, 12)
Well16x24 = PlateTypes.well_type(16, 24)
Well32x48 = PlateTypes.well_type(32, 48)
Well48x72 = PlateTypes.well_type(48, 72)

WellSet2x3 = PlateTypes.well_set_type(2, 3)
WellSet3x4 = PlateTypes.well_set_type(3, 4)
WellSet4x6 = PlateTypes.well_set_type(4, 6)
WellSet6x8 = PlateTypes.well_set_type(6, 8)
WellSet8x12 = PlateTypes.well_set_type(8, 12)
WellSet16x24 = PlateTypes.well_set_type(16, 24)
WellSet32x48 = PlateTypes.well_set_type(32, 48)
WellSet48x72 = PlateTypes.well_set_type(48, 72)
