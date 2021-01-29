# Copyright 2021 Sidney Markowitz All Rights Reserved.
# Distributed under MIT license.
# See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import unittest
import os
import sys
import timeit
import _test_utils
from brotlidecpy import decompress
from brotli import decompress as brotlidecompress, compress
# This is a brotli python library used for test comparisons that requires Python 3. Skip those tests if running Python 2
if sys.version_info[0] > 2:
    from lib.brotlipython import brotlidec


def _get_original_name(test_data):
    return test_data.split('.compressed')[0]


class TestDecompress(_test_utils.TestCase):

    def _test_decompress(self, test_data):
        """This performs the same decompression tests as in the Python bindings of brotli reference implementation"""
        temp_uncompressed = _test_utils.get_temp_uncompressed_name(test_data)
        original = _get_original_name(test_data)
        with open(temp_uncompressed, 'wb') as out_file:
            with open(test_data, 'rb') as in_file:
                out_file.write(decompress(in_file.read()))
        self.assertFilesMatch(temp_uncompressed, original)

    def _test_brotli_decompress_buffer(self, test_data):
        """This tests that in memory buffer to buffer decompression of test data gets expected results"""
        with open(test_data, 'rb') as f:
            compressed_buffer = f.read()
        with open(os.path.splitext(test_data)[0], 'rb') as f:
            uncompressed_buffer = f.read()
        result_buffer = decompress(compressed_buffer)
        self.assertSequenceEqual(uncompressed_buffer, result_buffer, "Failed decompress of %s" %
                                 os.path.splitext(os.path.basename(test_data))[0])

    def _test_against_pylib_brotli(self, test_data):
        """This confirms that this package decompresses same as two other brotli packages, the C reference
        implementation that is in PyPI and a slow port of the Rust implementation.
        It also prints execution times to serve as a performance test, even though unit tests are usually for that"""
        with open(os.path.splitext(test_data)[0], 'rb') as f:
            original_uncompressed_buffer = f.read()
        compressed_buffer = compress(original_uncompressed_buffer)
        ref_time = timeit.default_timer()
        ref_uncompressed_buffer = brotlidecompress(compressed_buffer)  # using fast brotli library
        ref_time = timeit.default_timer() - ref_time
        brotlipy_time = timeit.default_timer()
        if sys.version_info[0] > 2:  # The brotlipython library only runs in Python 3, don't test against it if in 2
            brotlipy_uncompressed_buffer = brotlidec(compressed_buffer, [])  # using brotlipython slow Python
            brotlipy_time = timeit.default_timer() - brotlipy_time
            self.assertSequenceEqual(ref_uncompressed_buffer, brotlipy_uncompressed_buffer)
        test_time = timeit.default_timer()
        test_uncompressed_buffer = decompress(compressed_buffer)  # testing this package, should be intermediate time
        test_time = timeit.default_timer() - test_time
        self.assertSequenceEqual(ref_uncompressed_buffer, test_uncompressed_buffer)
        self.assertSequenceEqual(original_uncompressed_buffer, test_uncompressed_buffer)
        print("File '%s' Times msec   C ref: %.3f, brotlipy: %.3f, this test: %.3f" %
              (os.path.splitext(os.path.basename(test_data))[0],
               ref_time * 1000,
               brotlipy_time * 1000 if (sys.version_info[0] > 2) else float('nan'),
               test_time * 1000))


_test_utils.generate_test_methods(TestDecompress)

# when running this from cli set PYTHONPATH to parent directory of brotlidecpy so import will work
# e.g., PYTHONPATH=. python test/decompress_test.py
if __name__ == '__main__':
    unittest.main()
