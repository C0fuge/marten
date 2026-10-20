#!/bin/sh
# Compiler launcher for the BE build: ccache + "-g0" appended last, which overrides the "-g -gdwarf-4"
# that be/CMakeLists.txt forces for Release builds. Result: no debug info in our objects (smaller and
# faster to build and cache); function names still appear in stack traces.
exec ccache "$@" -g0
