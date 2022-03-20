import cffi
import pathlib
import os
ffi = cffi.FFI()

this_dir = os.path.dirname(os.path.realpath(__file__))
h_file_name = os.path.join(this_dir, "playground.h")
with open(h_file_name) as h_file:
    ffi.cdef(h_file.read())

ffi.set_source(
    "race_env",
    # Since you're calling a fully-built library directly, no custom source
    # is necessary. You need to include the .h files, though, because behind
    # the scenes cffi generates a .c file that contains a Python-friendly
    # wrapper around each of the functions.
    '#include "playground.h"',
    # The important thing is to include the pre-built lib in the list of
    # libraries you're linking against:
    sources=["playground.c"],
    #libraries=["math"],
    #library_dirs=[this_dir.as_posix()],
    extra_compile_args=["-w"],
    #extra_link_args=["-Wl,-rpath,."],
)
ffi.compile()