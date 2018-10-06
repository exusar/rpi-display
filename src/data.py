import logging

import requests
import schedule

import configuration
from weather_providers import OpenWeatherMap, DarkSky


class Data:
    def __init__(self):
        self.weather: dict = None
        self.exchange_rate: dict = None
        self.ig: dict = None

        self._weather_provider = self._get_provider()

        self._mode_cfg = configuration.ModeCfg()

    def schedule_data_download(self):
        updateable_modes, download_modes = self._get_updateable_modes()
        for mode, enabled in updateable_modes:
            if enabled:
                schedule.every(mode.get_update()).seconds.do(next(download_modes))

    def _get_provider(self):
        providers = {
            'owm': OpenWeatherMap,
            'ds': DarkSky
        }
        config_provider = self._mode_cfg.weather.get_provider()
        provider = providers[config_provider]
        return provider()

    def _get_updateable_modes(self):
        return {
                   self._mode_cfg.weather: self._mode_cfg.weather.get_enable(),
                   self._mode_cfg.exchange_rate: self._mode_cfg.exchange_rate.get_enable(),
                   self._mode_cfg.ig: self._mode_cfg.ig.get_enable()
               }, [self.update_weather(), self.update_exchange_rate(), self.update_ig()]

    def update_weather(self):
        self.weather = self._weather_provider.download_data()

    def update_exchange_rate(self):
        data = {}
        for k, v in self._mode_cfg.exchange_rate.get_types():
            response = requests.get('http://free.currencyconverterapi.com/api/v5/convert?q={}_{}&compact=y'.format(
                k.lower(), v.lower()))

            status_code = response.status_code
            if status_code / 100 != 2:
                logging.error('Cannot download exchange rate type={}/{}, status code={} response body={}',
                              k.upper(), v.upper(), status_code, response.json())
                return

            json = response.json()

            data['{}/{}'.format(k.upper(), v.upper())] = round(json['{}_{}'.format(k.upper(), v.upper())]['val'], 2)
        self.exchange_rate = data

    def update_ig(self):
        response = requests.get(
            "https://api.instagram.com/v1/users/self/?access_token=".format(self._mode_cfg.ig.get_api_key()))

        status_code = response.status_code
        if status_code / 100 != 2:
            logging.error('Cannot download instagram followers, status code={}, response body={}',
                          status_code, response.json())
            return

        json = response.json()
        self.ig = {
            'followers': json['data']['counts']['followed_by']
        }