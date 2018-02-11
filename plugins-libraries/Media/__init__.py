#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# This file is part of the extensive testing project
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
# -------------------------------------------------------------------

from tones import DialTones
from wav import WavContainer
from noise import Noise
from waves import Waves
from sdp import SDP


from sample import UNSIGNED_8BITS
from sample import UNSIGNED_16BITS
from sample import SIGNED_8BITS
from sample import SIGNED_16BITS

from tones import UE
from tones import US
from tones import UK
from tones import SIT_RO
from tones import SIT_RO2
from tones import SIT_VC
from tones import SIT_NC
from tones import SIT_NC2
from tones import SIT_IC
from tones import SIT_IO
from tones import SIT_FU

from wav import WAVE_FORMAT_PCM
from wav import WAVE_FORMAT_PCMA
from wav import WAVE_FORMAT_PCMU
from wav import CHANNELS_MONO
from wav import CHANNELS_STEREO
from wav import WAV_UNSIGNED_8BITS
from wav import WAV_SIGNED_16BITS

from image import Image

from chartjs import ChartJS

__DESCRIPTION__ = "Some tools for audio, image and video media. Dialtones, waves and noise generators"