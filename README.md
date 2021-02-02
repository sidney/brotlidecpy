### brotlidecpy: Brotli Decompressor in Python

The `brotli` module that is in PyPI provides Python bindings to the fast C reference
implementation of [RFC 7932](https://tools.ietf.org/html/rfc7932), and is the preferred
one to use for most purposes. One limitation to its use is that it requires installation
of a platform-specific shared binary executable.

This library is written all in versions 2 and 3 compatible Python for the special case in
which it is not practical to package or require platform-specific binaries. It includes only
the decompression function, under the assumption that will be the most common use-case that
might have that restriction. It is hundreds of times slower than the reference `brotli`.

This is a hand port of the decompression portion of the Javascript project that is
itself a hand port of the C code of the reference implementation.

* JavaScript port of brotli [brotli.js](https://github.com/devongovett/brotli.js)
* C Reference implementation [brotli](https://github.com/google/brotli)

### Installation and Usage

Copy the top level file `brotlidecpy.py` and the directory `brotlidecpy` to a directory  
that will be in `PYTHONPATH` at runtime.

The following code will take a byte-like object, e.g. a bytearray or byte-string,
that contains brotli compressed data, and return one with the uncompressed data

    from brotlidecpy import decompress

    uncompressed_data = decompress(compressed_data)

### Running the integration tests
With a copy of the entire `test` directory, set PYTHONPATH to the directory containing
`brotlidecpy.py`, which may or may not be the same directory that contains `test`,
and run the command (suitably modified for the current directory you are using)

    python test/decompresstest.py


###### brotlidecpy is open-sourced under the MIT License, see the LICENSE file.
