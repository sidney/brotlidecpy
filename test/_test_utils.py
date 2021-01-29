# This file copied from the tests for the Python bindings of the brotli RFC 7932 reference implementation
# Copyright 2016 The Brotli Authors. All rights reserved.
#
# Distributed under MIT license.
# See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

from __future__ import print_function
import filecmp
import glob
import itertools
import os
import sys
import tempfile
import unittest


project_dir = os.path.abspath(os.path.join(__file__, '..', '..'))
src_dir = os.path.join(project_dir, '_brotlidecpy')
test_dir = os.path.join(project_dir, 'test')

python_exe = sys.executable or 'python'

TESTDATA_DIR = os.path.join(test_dir, 'testdata')

TESTDATA_FILES = [
    'empty',  # Empty file
    '10x10y',  # Small text
    'alice29.txt',  # Large text
    'random_org_10k.bin',  # Small data
    'mapsdatazrh',  # Large data
]

TESTDATA_PATHS = [os.path.join(TESTDATA_DIR, f) for f in TESTDATA_FILES]

TESTDATA_PATHS_FOR_DECOMPRESSION = glob.glob(
    os.path.join(TESTDATA_DIR, '*.compressed'))

TEMP_DIR = tempfile.mkdtemp()


def get_temp_compressed_name(filename):
    return os.path.join(TEMP_DIR, os.path.basename(filename + '.bro'))


def get_temp_uncompressed_name(filename):
    return os.path.join(TEMP_DIR, os.path.basename(filename + '.unbro'))


def bind_method_args(method, *args, **kwargs):
    return lambda self: method(self, *args, **kwargs)


def generate_test_methods(test_case_class,
                          variants=None):
    # Add test methods for each test data file.  This makes identifying problems
    # with specific compression scenarios easier.
    paths = TESTDATA_PATHS_FOR_DECOMPRESSION
    opts = []
    if variants:
        opts_list = []
        for k, v in variants.items():
            opts_list.append([r for r in itertools.product([k], v)])
        for o in itertools.product(*opts_list):
            opts_name = '_'.join([str(i) for i in itertools.chain(*o)])
            opts_dict = dict(o)
            opts.append([opts_name, opts_dict])
    else:
        opts.append(['', {}])
    for method in [m for m in dir(test_case_class) if m.startswith('_test')]:
        for testdata in paths:
            for (opts_name, opts_dict) in opts:
                f = os.path.splitext(os.path.basename(testdata))[0]
                name = 'test_{method}_{options}_{file}'.format(
                    method=method, options=opts_name, file=f)
                func = bind_method_args(
                    getattr(test_case_class, method), testdata, **opts_dict)
                setattr(test_case_class, name, func)


class TestCase(unittest.TestCase):

    def tearDown(self):
        for f in TESTDATA_PATHS:
            try:
                os.unlink(get_temp_compressed_name(f))
            except OSError:
                pass
            try:
                os.unlink(get_temp_uncompressed_name(f))
            except OSError:
                pass

    def assertFilesMatch(self, first, second):
        self.assertTrue(
            filecmp.cmp(first, second, shallow=False),
            'File {} differs from {}'.format(first, second))
