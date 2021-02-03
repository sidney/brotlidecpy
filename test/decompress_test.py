# Copyright 2021 Sidney Markowitz All Rights Reserved.
# Distributed under MIT license.
# See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import unittest
import os
import timeit
import _test_utils
from brotlidecpy import decompress
from brotli import decompress as brotlidecompress


class TestDecompress(_test_utils.TestCase):

    def _test_decompress(self, test_data):
        """This performs the same decompression tests as in the Python bindings of brotli reference implementation"""
        temp_uncompressed = _test_utils.get_temp_uncompressed_name(test_data)
        original = _test_utils.get_uncompressed_name(test_data)
        with open(temp_uncompressed, 'wb') as out_file:
            with open(test_data, 'rb') as in_file:
                out_file.write(decompress(in_file.read()))
        self.assertFilesMatch(temp_uncompressed, original)

    def _test_brotli_decompress_buffer(self, test_data):
        """This tests that in memory buffer to buffer decompression of test data gets expected results"""
        with open(test_data, 'rb') as f:
            compressed_buffer = f.read()
        with open(_test_utils.get_uncompressed_name(test_data), 'rb') as f:
            uncompressed_buffer = f.read()
        result_buffer = decompress(compressed_buffer)
        self.assertSequenceEqual(uncompressed_buffer, result_buffer, "Failed decompress of %s" %
                                 os.path.basename(test_data))

    def _test_against_pylib_brotli(self, test_data):
        """This confirms that this package decompresses same as the C reference implementation that is in PyPI.
        It also prints execution times to serve as a performance test, though unit tests are not usually for that"""
        with open(_test_utils.get_uncompressed_name(test_data), 'rb') as f:
            original_uncompressed_buffer = f.read()
        with open(test_data, 'rb') as f:
            compressed_buffer = f.read()
        ref_time = timeit.default_timer()
        ref_uncompressed_buffer = brotlidecompress(compressed_buffer)  # using fast brotli library
        ref_time = timeit.default_timer() - ref_time
        test_time = timeit.default_timer()
        test_uncompressed_buffer = decompress(compressed_buffer)  # testing this package, should be intermediate time
        test_time = timeit.default_timer() - test_time
        self.assertSequenceEqual(ref_uncompressed_buffer, original_uncompressed_buffer,
                                 msg="Something wrong with test:"
                                     " Reference decompress does not match uncompressed test data file")
        self.assertSequenceEqual(original_uncompressed_buffer, test_uncompressed_buffer,
                                 msg="Test failure in decompress of %s" % os.path.basename(test_data))
        print("File '%s' Times msec   C ref: %.3f, this test: %.3f" %
              (os.path.basename(test_data),
               ref_time * 1000,
               test_time * 1000))


_test_utils.generate_test_methods(TestDecompress)

# when running this from cli set PYTHONPATH to parent directory of brotlidecpy so import will work
# e.g., PYTHONPATH=. python test/decompress_test.py
if __name__ == '__main__':
    unittest.main()
