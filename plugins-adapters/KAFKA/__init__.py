#!/usr/bin/env python
# -*- coding: utf-8 -*-

from consumer import *
from producer import *
from templates import *

__DESCRIPTION__ = """Allow to consum/produce kafka topics.
                     Adapter mainly based on kafka-python library functions mapping (1.4.1 minimal version)
				"""

__HELPER__ =    [

		("ProducerClient", ["__init__", "connect", "send", "flush", "partitions_for", "close", "isConnect", "isSend", "isFlush", "isPartitions_for", "isClose"]),
		("ConsumerClient", ["__init__", "connect", "assign","assignment","consume","beginning_offsets",
																					"close","commit","commit_async","committed","end_offsets","highwater",
																					"offsets_for_times","partitions_for_topic","pause","paused","poll",
																					"position","resume","seek","seek_to_beginning","seek_to_end",
																					"subscribe","subscription","topics","unsubscribe","isConnect", "isAssign","isAssignment","isBeginning_offsets",
																					"isClose","isCommit","isCommit_async","isCommitted","isEnd_offsets","isHighwater",
																					"isOffsets_for_times","isPartitions_for_topic","isPause","isPaused","isPoll",
																					"isPosition","isResume","isSeek","isSeek_to_beginning","isSeek_to_end",
																					"isSubscribe","isSubscription","isTopics","isUnsubscribe"])
		]
