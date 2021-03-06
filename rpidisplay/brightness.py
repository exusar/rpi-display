import datetime
import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from rpidisplay import configuration
from rpidisplay import datetime_provider


class Brightness:
    def __init__(self, device):
        self._device = device
        self._cfg = configuration.BrightnessCfg()
        self._mode = self._get_mode()

    def _get_mode(self):
        modes = {
            'standard': Standard,
            'time_dependent': TimeDependent,
        }
        return modes[self._cfg.get_mode()](self._device)

    def start(self):
        self._mode.start()

    def on_click(self):
        self._mode.on_click()

    def cleanup(self):
        self._mode.cleanup()


class Standard:
    def __init__(self, device):
        self._device = device
        self._cfg = configuration.BrightnessCfg().standard
        self._default = self._cfg.get_default()
        self._increase_on_click = self._cfg.get_increase_on_click()
        self._max = self._cfg.get_max()
        self._level = self._default

    def start(self):
        self._device.brightness(self._level)

    def on_click(self):
        self._change_level()
        self._set_brightness()

    def cleanup(self):
        pass

    def _change_level(self):
        level_after_increase = self._level + self._increase_on_click
        self._level = level_after_increase if level_after_increase <= self._max else 0

    def _set_brightness(self):
        self._device.brightness(self._level)
        logging.info('Changed brightness level to %d', self._level)


class TimeDependent:
    def __init__(self, device):
        self._device = device
        self._cfg = configuration.BrightnessCfg().time_dependent
        self._datetime_provider = datetime_provider
        self._times = self._convert_times()
        self._level = None
        self._scheduler = None

    def start(self):
        self._watch_times()
        self._scheduler = self._setup_scheduler()

    def on_click(self):
        pass

    def cleanup(self):
        self._scheduler.shutdown(wait=False)
        logging.info('Time dependent mode scheduler has been shutdown')

    def _setup_scheduler(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self._watch_times, trigger='cron', minute='*/1')
        scheduler.start()
        return scheduler

    def _convert_times(self):
        time_format = '%H:%M'
        times = sorted(self._cfg.get_times(), key=lambda x: time.strptime(x['from'], time_format), reverse=True)
        for t in times:
            t['from'] = datetime.datetime.strptime(t['from'], time_format).time()
        return times

    def _watch_times(self):
        now = self._datetime_provider.get_current_time()
        for t in self._times:
            if now >= t['from']:
                value = t['value']
                if self._level != value:
                    self._set_brightness(value)
                return
        latest_value = self._times[0]['value']
        self._set_brightness(latest_value)

    def _set_brightness(self, value):
        self._level = value
        self._device.brightness(self._level)
        logging.info('Changed brightness level to %d', self._level)
