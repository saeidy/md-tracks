# Tracks provides tools for analyzing large trajectory files.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
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


import os, sys, glob

orig_dir = os.getcwd()
if '-i' in sys.argv:
    # use the installed library for testing
    sys.argv.remove('-i')
    scripts_dir = "/usr/bin"
    lib_dir = None
else:
    retcode = os.system("(cd ..; python setup.py build)")
    if retcode != 0: sys.exit(retcode)
    scripts_dir = glob.glob(os.path.join(os.path.dirname(orig_dir), "build/scripts*"))[0]
    lib_dir = glob.glob(os.path.join(os.path.dirname(orig_dir), "build/lib*"))[0]
    sys.path.insert(0, lib_dir)

tmp_dir = os.path.join(orig_dir, "tmp")
input_dir = os.path.join(orig_dir, "input")
output_dir = os.path.join(orig_dir, "output")

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)


import unittest, shutil


__all__ = [
    "orig_dir", "scripts_dir", "lib_dir", "tmp_dir", "input_dir", "output_dir",
    "BaseTestCase",
]


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)
        os.chdir(tmp_dir)

    def tearDown(self):
        os.chdir(orig_dir)
        shutil.rmtree(tmp_dir)

    def assertArraysEqual(self, a, b):
        self.assertEqual(a.shape, b.shape, "The array shapes do not match.")
        self.assert_((a==b).all(), "The array values do not match.")

    def assertArrayConstant(self, arr, const):
        self.assert_((arr==const).all(), "Some/All array values do not match the constant.")

    def assertArraysAlmostEqual(self, a, b, relerr_threshold, mean=False):
        self.assertEqual(a.shape, b.shape, "The array shapes do not match.")
        if mean:
            error = abs(a-b).mean()
            oom = 0.5*(abs(a).mean()+abs(b).mean())
        else:
            error = abs(a-b).max()
            oom = 0.5*(abs(a).max()+abs(b).max())
        relerr = error/oom
        self.assert_(relerr <= relerr_threshold, "The relative error is larger than given threshold: %5.3e > %5.3e" % (relerr, relerr_threshold))

    def assertArrayAlmostConstant(self, arr, const, relerr_threshold):
        error = abs(arr-const).max()
        oom = const
        relerr = error/oom
        self.assert_(relerr <= relerr_threshold, "The relative error is larger than given threshold: %5.3e > %5.3e" % (relerr, relerr_threshold))

    def assertArrayAlmostZero(self, arr, abserr_threshold):
        abserr = abs(arr).max()
        self.assert_(abserr <= abserr_threshold, "The absolute error is larger than given threshold: %5.3e > %5.3e" % (abserr, abserr_threshold))




