import datetime
import pytz


def datefunc(old_time):
    now = datetime.datetime.now()
    d = now.day
    h = now.hour
    m = now.minute
    s = now.second
    now = int(d) * 24 * 3600 + int(h) * 3600 + int(m) * 60 + int(s)
    d = old_time.day
    h = old_time.hour
    m = old_time.minute
    s = old_time.second
    old = int(d) * 24 * 3600 + int(h) * 3600 + int(m) * 60 + int(s)
    delta = now - old  # 单位s
    if delta / (3600 * 24 * 30) > 1:
        return "%d个月前" % (delta / (3600 * 24 * 30))
    elif delta / (3600 * 24 * 7) > 1:
        return "%d周前" % (delta / (3600 * 24 * 7))
    elif delta / (3600 * 24) > 1:
        return "%d小时前" % (delta / (3600 * 24))
    elif delta / 3600 > 1:
        return "%d小时前" % (delta / 3600)
    elif delta / 60 > 1:
        return "%d分钟前" % (delta / 60)
    else:
        return "%d秒前" % delta
