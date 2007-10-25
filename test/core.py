# Tracks provides tools for analyzing large trajectory files.
# Copyright (C) 2007 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Tracks.
#
# Tracks is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Tracks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --


from common import *

from tracks.core import *
from tracks.log import log

import unittest, os, numpy


log.verbose = False


class TrackTestCase(BaseTestCase):
    def get_arrays(self):
        # return a list of different types of arrays, one-dimensional and len=50
        return [
            numpy.random.normal(0,1,50).astype(numpy.float32),
            numpy.random.normal(0,1,50).astype(numpy.float64),
            numpy.random.normal(0,1,50).astype(numpy.float128),
            numpy.random.randint(0,10,50).astype(numpy.int8),
            numpy.random.randint(0,10,50).astype(numpy.int16),
            numpy.random.randint(0,10,50).astype(numpy.int32),
            numpy.random.randint(0,10,50).astype(numpy.int64),
            numpy.random.randint(0,10,50).astype(numpy.uint8),
            numpy.random.randint(0,10,50).astype(numpy.uint16),
            numpy.random.randint(0,10,50).astype(numpy.uint32),
            numpy.random.randint(0,10,50).astype(numpy.uint64),
            (numpy.random.normal(0,1,50)+numpy.random.normal(0,1,50)*1.0j).astype(numpy.complex64),
            (numpy.random.normal(0,1,50)+numpy.random.normal(0,1,50)*1.0j).astype(numpy.complex128),
            (numpy.random.normal(0,1,50)+numpy.random.normal(0,1,50)*1.0j).astype(numpy.complex256),
        ]

    def test_load_dump(self):
        for rnd1 in self.get_arrays():
            dump_track("test", rnd1)
            rnd2 = load_track("test")
            self.assert_((rnd1==rnd2).all())
            self.assert_(rnd1.dtype==rnd2.dtype)

    def test_append(self):
        for rnd1 in self.get_arrays():
            track = Track("test", clear=True)
            for index in xrange(10):
                track.append(rnd1[index*5:(index+1)*5])
            rnd2 = track.read()
            self.assert_((rnd1==rnd2).all())
            self.assert_(rnd1.dtype==rnd2.dtype)

    def test_read_parts(self):
        for rnd1 in self.get_arrays():
            track = Track("test", clear=True)
            track.append(rnd1)
            rnd2 = []
            for index in xrange(10):
                rnd2.append(track.read(start=index*5, length=5))
            rnd2 = numpy.concatenate(rnd2)
            self.assert_((rnd1==rnd2).all())
            self.assert_(rnd1.dtype==rnd2.dtype)

    def test_read_behind(self):
        for rnd1 in self.get_arrays():
            track = Track("test", clear=True)
            track.append(rnd1)
            rnd2 = track.read(50,10)
            self.assert_(len(rnd2)==0)
            self.assert_(rnd1.dtype==rnd2.dtype)


class MultiTrackTestCase(BaseTestCase):
    def get_buffers(self):
        return [
            numpy.random.normal(0,1,1000),
            numpy.random.normal(0,1,1000),
            numpy.random.randint(0,10,1000).astype(numpy.int32),
        ], ["test1", "test2", "test3"]

    def test_write(self):
        buffers, names = self.get_buffers()

        mtw = MultiTracksWriter(names, [b.dtype for b in buffers], buffer_size=5*1024)
        for row in zip(*buffers):
            mtw.dump_row(row)
        mtw.finalize()
        buffers_check = [load_track(name) for name in names]

        for b, b_check in zip(buffers, buffers_check):
            self.assert_((b==b_check).all())
            self.assert_((b.dtype==b_check.dtype))

    def test_read(self):
        buffers, names = self.get_buffers()

        for b, name in zip(buffers, names):
            dump_track(name, b)
        mtr = MultiTracksReader(names, buffer_size=5*1024)
        buffers_check = list([] for index in xrange(len(buffers)))
        for row in mtr:
            for index, value in enumerate(row):
                buffers_check[index].append(value)
        buffers_check = [numpy.array(b, dtype) for b, dtype in zip(buffers_check, mtr.dtypes)]

        for b, b_check in zip(buffers, buffers_check):
            self.assert_((b==b_check).all())
            self.assert_((b.dtype==b_check.dtype))