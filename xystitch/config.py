'''
pr0ntools
Copyright 2012 John McMaster <JohnDMcMaster@gmail.com>
Licensed under a 2 clause BSD license, see COPYING for details
'''

import json
import os


class Config:
    def __init__(self, fn=None):
        if fn is None:
            fn = Config.get_default_fn()
        if os.path.exists(fn):
            js = open(fn).read()
        else:
            js = "{}"
        self.json = json.loads(js)

        self.imgw = int(os.getenv('XY_IMW', "1632"))
        self.imgh = int(os.getenv('XY_IMH', "1224"))

    @staticmethod
    def get_default_fn():
        return os.getenv('HOME') + '/' + '.pr0nrc'

    def getx(self, ks, default=None):
        root = self.json
        for k in ks.split('.'):
            if k in root:
                root = root[k]
            else:
                return default
        return root

    def get(self, k, default=None):
        if k in self.json:
            return self.json[k]
        else:
            return default

    def keep_temp_files(self):
        return self.get('keep_temp', 0)

    def temp_base(self):
        return self.get('temp_base', "/tmp/pr0ntools_")

    def enblend_opts(self):
        return self.get('enblend', {'opts': ''})['opts']

    def super_tile_memory(self):
        return self.getx('pr0nts.mem', None)

    def poor_opt_thresh(self):
        # FIXME:
        # 1) should be derived from image size
        # 2) should be configurable
        return int(os.getenv('XY_OPT_THRESH', "175"))

    def default_overlapi(self):
        """
        Fraction of image not overlapping ("overlap inverse")
        """
        return float(os.getenv('XY_OVERLAPI', "0.7"))

    def overlap_outlier_thresh(self):
        """
        Throw out images that differ by more than given fraction vs expected overlap
        """
        return float(os.getenv('XY_OVERLAP_OUTLIER_THRESH', "0.10"))


config = Config()
