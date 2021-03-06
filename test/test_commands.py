# -*- coding: utf-8 -*-
# MD-Tracks is a trajectory analysis toolkit for molecular dynamics
# and monte carlo simulations.
# Copyright (C) 2007 - 2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of MD-Tracks.
#
# MD-Tracks is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# In addition to the regulations of the GNU General Public License,
# publications and communications based in parts on this program or on
# parts of this program are required to cite the following article:
#
# "MD-TRACKS: A productive solution for the advanced analysis of Molecular
# Dynamics and Monte Carlo simulations", Toon Verstraelen, Marc Van Houteghem,
# Veronique Van Speybroeck and Michel Waroquier, Journal of Chemical Information
# and Modeling, 48 (12), 2414-2424, 2008
# DOI:10.1021/ci800233y
#
# MD-Tracks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
#--


from common import *

from tracks.core import load_track, dump_track
from tracks.parse import parse_slice
import tracks.api.vector as vector
import tracks.api.cell as cell

from molmod.io.psf import PSFFile
from molmod.io.xyz import XYZReader, XYZFile
from molmod.units import angstrom, nanometer, femtosecond, picosecond, kcalmol, \
    bar
from molmod.constants import lightspeed, boltzmann
from molmod.periodic import periodic

import numpy, os, glob, shutil


__all__ = ["CommandsTestCase"]


class CommandsTestCase(BaseTestCase):
    def from_xyz(self, case, middle_word, extra_args=[]):
        self.execute("tr-from-xyz", [
            os.path.join(input_dir, case, "md-%s-1.xyz" % middle_word),
            middle_word
        ] + extra_args)

    def from_cp2k_ener(self, case, extra_args=[], verbose=False):
        self.execute("tr-from-cp2k-ener", [
            os.path.join(input_dir, case, "md-1.ener"),
        ] + extra_args, verbose=verbose)

    def from_cpmd_traj(self, filename, extra_args=[], verbose=False):
        self.execute("tr-from-cpmd-traj", [
            os.path.join(input_dir, filename),
        ] + extra_args, verbose=verbose)

    def execute(self, command, args, verbose=False, stdin=None):
        from subprocess import Popen, PIPE, STDOUT
        env = {}
        if lib_dir is not None:
            env = {"PYTHONPATH": "%s:%s" % (lib_dir, os.getenv("PYTHONPATH"))}
        env['DISPLAY'] = os.getenv('DISPLAY')
        p = Popen(
            ["/usr/bin/env", "python", os.path.join(scripts_dir, command)] + args,
            stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env,
        )
        if stdin is not None:
            for line in stdin:
                print >> p.stdin, line
        p.stdin.close()
        output = list(line[:-1] for line in p.stdout)
        error = list(line[:-1] for line in p.stderr)
        retcode = p.wait()
        self.assertEqual(retcode, 0, "Something went wrong with this command:\n%s %s\n. The output is:\n%s The error is:\n%s" % (command, " ".join(args), "\n".join(output), "\n".join(error)))
        if verbose:
            print "\n".join(output)
            print "\n".join(error)
        return output

    def test_from_xyz(self):
        # Load the xyz file
        self.from_xyz("thf01", "pos")
        # Test some values
        tmp = load_track("tracks/atom.pos.0000000.x")
        self.assertAlmostEqual(tmp[0]/angstrom, 1.160855, 5)
        self.assertAlmostEqual(tmp[1]/angstrom, 1.1814236022, 5)
        self.assertAlmostEqual(tmp[-1]/angstrom, -0.9141294178, 5)
        tmp = load_track("tracks/atom.pos.0000012.z")
        self.assertAlmostEqual(tmp[0]/angstrom, 1.0237910000, 5)
        self.assertAlmostEqual(tmp[1]/angstrom, 1.0193867160, 5)
        self.assertAlmostEqual(tmp[-1]/angstrom, -0.5994763399, 5)
        # Load
        self.from_xyz("thf01", "pos", ["-s20:601:5"])
        # Test some values
        tmp = load_track("tracks/atom.pos.0000000.x")
        self.assertAlmostEqual(tmp[0]/angstrom, 1.1643775386, 5)
        self.assertAlmostEqual(tmp[1]/angstrom, 1.1186662255, 5)
        self.assertAlmostEqual(tmp[-1]/angstrom, 0.3461355118, 5)
        tmp = load_track("tracks/atom.pos.0000012.z")
        self.assertAlmostEqual(tmp[0]/angstrom, 1.4974560873, 5)
        self.assertAlmostEqual(tmp[1]/angstrom, 1.7383838088, 5)
        self.assertAlmostEqual(tmp[-1]/angstrom, -0.6220795393, 5)
        # Load the xyz file
        self.from_xyz("thf01", "vel", ["-u1"])
        # Test some values
        tmp = load_track("tracks/atom.vel.0000000.x")
        self.assertAlmostEqual(tmp[0], 0.0002092059, 5)
        self.assertAlmostEqual(tmp[1], 0.0001447176, 5)
        self.assertAlmostEqual(tmp[-1], -0.0001092007, 5)
        tmp = load_track("tracks/atom.vel.0000012.z")
        self.assertAlmostEqual(tmp[0], -0.0003909859, 5)
        self.assertAlmostEqual(tmp[1], 0.0004487963, 5)
        self.assertAlmostEqual(tmp[-1], 0.0000859001, 5)
        # Load the xyz file
        self.from_xyz("thf01", "vel", ["-u1", "-s20:601:5"])
        # Test some values
        tmp = load_track("tracks/atom.vel.0000000.x")
        self.assertAlmostEqual(tmp[0], 0.0000503137, 5)
        self.assertAlmostEqual(tmp[1], -0.0000955072, 5)
        self.assertAlmostEqual(tmp[-1], -0.0000947954, 5)
        tmp = load_track("tracks/atom.vel.0000012.z")
        self.assertAlmostEqual(tmp[0], 0.0001216775, 5)
        self.assertAlmostEqual(tmp[1], -0.0001251857, 5)
        self.assertAlmostEqual(tmp[-1], 0.0007943491, 5)
        # clean up
        shutil.rmtree("tracks")
        # Load the xyz file
        self.from_xyz("thf01", "pos", ["-a2,5"])
        # Test the number of files
        self.assertEqual(len(glob.glob("tracks/atom.pos.*")), 6)
        # Test some values
        tmp = load_track("tracks/atom.pos.0000002.x")
        self.assertAlmostEqual(tmp[0]/angstrom, 0.4226530000, 5)
        self.assertAlmostEqual(tmp[1]/angstrom, 0.3698115354, 5)
        self.assertAlmostEqual(tmp[-1]/angstrom, 0.1250660111, 5)
        tmp = load_track("tracks/atom.pos.0000005.z")
        self.assertAlmostEqual(tmp[0]/angstrom, 0.3813110000, 5)
        self.assertAlmostEqual(tmp[1]/angstrom, 0.4181952123, 5)
        self.assertAlmostEqual(tmp[-1]/angstrom, -1.7859607480, 5)

    def test_from_cp2k_ener(self):
        # Load the energy file
        self.from_cp2k_ener("thf01")
        # Test some values
        tmp = load_track("tracks/step")
        self.assertEqual(tmp[0], 0)
        self.assertEqual(tmp[1], 5)
        self.assertEqual(tmp[-1], 5000)
        tmp = load_track("tracks/time")
        self.assertAlmostEqual(tmp[0]/femtosecond, 0.0, 5)
        self.assertAlmostEqual(tmp[1]/femtosecond, 5.0, 5)
        self.assertAlmostEqual(tmp[-1]/femtosecond, 5000.0, 5)
        tmp = load_track("tracks/kinetic_energy")
        self.assertAlmostEqual(tmp[0], 0.015675735, 5)
        self.assertAlmostEqual(tmp[1], 0.008711175, 5)
        self.assertAlmostEqual(tmp[-1], 0.011256845, 5)
        tmp = load_track("tracks/temperature")
        self.assertAlmostEqual(tmp[0], 300.000000000, 5)
        self.assertAlmostEqual(tmp[1], 166.713237534, 5)
        self.assertAlmostEqual(tmp[-1], 215.431909415, 5)
        tmp = load_track("tracks/potential_energy")
        self.assertAlmostEqual(tmp[0], 0.029894724, 5)
        self.assertAlmostEqual(tmp[1], 0.036975396, 5)
        self.assertAlmostEqual(tmp[-1], 0.034406422, 5)
        tmp = load_track("tracks/conserved_quantity")
        self.assertAlmostEqual(tmp[0], 0.045570459, 5)
        self.assertAlmostEqual(tmp[1], 0.045686571, 5)
        self.assertAlmostEqual(tmp[-1], 0.045663267, 5)
        # Load the energy file
        self.from_cp2k_ener("thf01", ["-s20:601:5"])
        # Test some values
        tmp = load_track("tracks/step")
        self.assertEqual(tmp[0], 100)
        self.assertEqual(tmp[1], 125)
        self.assertEqual(tmp[-1], 3000)
        tmp = load_track("tracks/time")
        self.assertAlmostEqual(tmp[0]/femtosecond, 100.0, 5)
        self.assertAlmostEqual(tmp[1]/femtosecond, 125.0, 5)
        self.assertAlmostEqual(tmp[-1]/femtosecond, 3000.0, 5)
        tmp = load_track("tracks/kinetic_energy")
        self.assertAlmostEqual(tmp[0], 0.007844166, 5)
        self.assertAlmostEqual(tmp[1], 0.008257514, 5)
        self.assertAlmostEqual(tmp[-1], 0.011402720, 5)
        tmp = load_track("tracks/temperature")
        self.assertAlmostEqual(tmp[0], 150.120545659, 5)
        self.assertAlmostEqual(tmp[1], 158.031128585, 5)
        self.assertAlmostEqual(tmp[-1], 218.223631032, 5)
        tmp = load_track("tracks/potential_energy")
        self.assertAlmostEqual(tmp[0], 0.037852247, 5)
        self.assertAlmostEqual(tmp[1], 0.037445922, 5)
        self.assertAlmostEqual(tmp[-1], 0.034186532, 5)
        tmp = load_track("tracks/conserved_quantity")
        self.assertAlmostEqual(tmp[0], 0.045696413, 5)
        self.assertAlmostEqual(tmp[1], 0.045703436, 5)
        self.assertAlmostEqual(tmp[-1], 0.045589252, 5)
        # Load the energy file
        self.from_cp2k_ener("thf01", ["--append"])
        # Test some values
        tmp = load_track("tracks/step")
        self.assertEqual(tmp[117], 0)
        self.assertEqual(tmp[118], 5)
        self.assertEqual(tmp[-1], 5000)
        tmp = load_track("tracks/time")
        self.assertAlmostEqual(tmp[117]/femtosecond, 0.0, 5)
        self.assertAlmostEqual(tmp[118]/femtosecond, 5.0, 5)
        self.assertAlmostEqual(tmp[-1]/femtosecond, 5000.0, 5)
        tmp = load_track("tracks/kinetic_energy")
        self.assertAlmostEqual(tmp[117], 0.015675735, 5)
        self.assertAlmostEqual(tmp[118], 0.008711175, 5)
        self.assertAlmostEqual(tmp[-1], 0.011256845, 5)
        tmp = load_track("tracks/temperature")
        self.assertAlmostEqual(tmp[117], 300.000000000, 5)
        self.assertAlmostEqual(tmp[118], 166.713237534, 5)
        self.assertAlmostEqual(tmp[-1], 215.431909415, 5)
        tmp = load_track("tracks/potential_energy")
        self.assertAlmostEqual(tmp[117], 0.029894724, 5)
        self.assertAlmostEqual(tmp[118], 0.036975396, 5)
        self.assertAlmostEqual(tmp[-1], 0.034406422, 5)
        tmp = load_track("tracks/conserved_quantity")
        self.assertAlmostEqual(tmp[117], 0.045570459, 5)
        self.assertAlmostEqual(tmp[118], 0.045686571, 5)
        self.assertAlmostEqual(tmp[-1], 0.045663267, 5)

    def test_from_cp2k_cell(self):
        # Load the energy file
        self.execute("tr-from-cp2k-cell", [os.path.join(input_dir, "thf64/md-1.cell")])
        tmp = load_track("tracks/cell.a.x")
        self.assertAlmostEqual(tmp[0]/angstrom, 20.5000000000)
        self.assertAlmostEqual(tmp[1]/angstrom, 20.4977671159)
        self.assertAlmostEqual(tmp[-1]/angstrom, 20.4328712109)
        tmp = load_track("tracks/cell.a")
        self.assertAlmostEqual(tmp[0]/angstrom, 20.5000000000)
        self.assertAlmostEqual(tmp[1]/angstrom, 20.4977671159)
        self.assertAlmostEqual(tmp[-1]/angstrom, 20.4328712109)
        tmp = load_track("tracks/time")
        self.assertAlmostEqual(tmp[0]/femtosecond, 0.000)
        self.assertAlmostEqual(tmp[1]/femtosecond, 5.000)
        self.assertAlmostEqual(tmp[-1]/femtosecond, 95.000)
        tmp = load_track("tracks/volume")
        self.assertAlmostEqual(tmp[0]/angstrom**3, 8615.1250000000)
        self.assertAlmostEqual(tmp[1]/angstrom**3, 8612.3101980259)
        self.assertAlmostEqual(tmp[-1]/angstrom**3, 8530.7692124516)

    def test_from_cp2k_stress(self):
        # Load the energy file
        self.execute("tr-from-cp2k-stress", [os.path.join(input_dir, "thf64/md-1.stress")])
        tmp = load_track("tracks/stress.xx")
        self.assertAlmostEqual(tmp[0]/bar, 982.6527136414)
        self.assertAlmostEqual(tmp[1]/bar, 1520.9982884185)
        self.assertAlmostEqual(tmp[-1]/bar, 3352.0001110665)
        tmp = load_track("tracks/stress.zy")
        self.assertAlmostEqual(tmp[0]/bar, -4721.3431812354)
        self.assertAlmostEqual(tmp[1]/bar, -19.6129483571)
        self.assertAlmostEqual(tmp[-1]/bar, 6209.6972369552)
        tmp = load_track("tracks/time")
        self.assertAlmostEqual(tmp[0]/femtosecond, 0.000)
        self.assertAlmostEqual(tmp[1]/femtosecond, 5.000)
        self.assertAlmostEqual(tmp[-1]/femtosecond, 95.000)
        tmp = load_track("tracks/pressure")
        self.assertAlmostEqual(tmp[0]/bar, -0.284470689513E+04)
        self.assertAlmostEqual(tmp[1]/bar, 0.264474996707E+04)
        self.assertAlmostEqual(tmp[-1]/bar, 0.523529867036E+03)

    def test_from_cpmd_traj(self):
        self.execute("tr-from-cpmd-traj", [os.path.join(input_dir, "cpmd_h2/TRAJECTORY")])
        tmp = load_track("tracks/atom.pos.0000000.x")
        self.assertAlmostEqual(tmp[0], 8.28459820349145, 6)
        self.assertAlmostEqual(tmp[1], 8.28359660306853, 6)
        self.assertAlmostEqual(tmp[-1], 8.24604180945518, 6)
        tmp = load_track("tracks/atom.pos.0000001.z")
        self.assertAlmostEqual(tmp[0], 7.55848989965510, 6)
        self.assertAlmostEqual(tmp[1], 7.55807880859648, 6)
        self.assertAlmostEqual(tmp[-1], 7.47953391824190, 6)
        tmp = load_track("tracks/atom.vel.0000000.x")
        self.assertAlmostEqual(tmp[0], -0.00025263238305, 6)
        self.assertAlmostEqual(tmp[1], -0.00024652673917, 6)
        self.assertAlmostEqual(tmp[-1], -0.00000631539158, 6)
        tmp = load_track("tracks/atom.vel.0000001.z")
        self.assertAlmostEqual(tmp[0], -0.00010314321490, 6)
        self.assertAlmostEqual(tmp[1], -0.00010229631610, 6)
        self.assertAlmostEqual(tmp[-1], -0.00010743513101, 6)

    def test_from_cpmd_ener(self):
        self.execute("tr-from-cpmd-ener", [os.path.join(input_dir, "cpmd_h2/ENERGIES")])
        tmp = load_track("tracks/step")
        self.assertEqual(tmp[0], 1)
        self.assertEqual(tmp[1], 2)
        self.assertEqual(tmp[-1], 200)
        tmp = load_track("tracks/fict_kinectic_energy")
        self.assertAlmostEqual(tmp[0], 0.00000034, 6)
        self.assertAlmostEqual(tmp[1], 0.00000289, 6)
        self.assertAlmostEqual(tmp[-1], 0.00000909, 6)
        tmp = load_track("tracks/temperature")
        self.assertAlmostEqual(tmp[0], 49.433, 6)
        self.assertAlmostEqual(tmp[1], 47.850, 6)
        self.assertAlmostEqual(tmp[-1], 27.783, 6)
        tmp = load_track("tracks/potential_energy")
        self.assertAlmostEqual(tmp[0], -1.1328933401, 6)
        self.assertAlmostEqual(tmp[1], -1.1328882582, 6)
        self.assertAlmostEqual(tmp[-1], -1.1327990428, 6)
        tmp = load_track("tracks/classical_energy")
        self.assertAlmostEqual(tmp[0], -1.1326585354, 6)
        self.assertAlmostEqual(tmp[1], -1.1326609757, 6)
        self.assertAlmostEqual(tmp[-1], -1.1326670764, 6)
        tmp = load_track("tracks/hamiltonian_energy")
        self.assertAlmostEqual(tmp[0], -1.1326581984, 6)
        self.assertAlmostEqual(tmp[1], -1.1326580823, 6)
        self.assertAlmostEqual(tmp[-1], -1.1326579867, 6)
        tmp = load_track("tracks/ms_displacement")
        self.assertAlmostEqual(tmp[0], 0.207014E-05, 6)
        self.assertAlmostEqual(tmp[1], 0.817859E-05, 6)
        self.assertAlmostEqual(tmp[-1], 0.397302E-01, 6)

    def test_from_atrj(self):
        # normal test
        self.execute("tr-from-atrj", [os.path.join(input_dir, "bartek.atrj")])
        time = load_track("tracks/time")
        self.assertArraysAlmostEqual(time, numpy.array([1, 2, 3])*picosecond, 1e-5)
        step = load_track("tracks/step")
        self.assertArraysAlmostEqual(step, numpy.array([1000, 2000, 3000]), 1e-5)
        step = load_track("tracks/total_energy")
        self.assertArraysAlmostEqual(step, numpy.array([341.860357, 334.433566, 336.136295])*kcalmol, 1e-5)
        cor = load_track("tracks/atom.pos.0000000.x")
        self.assertArraysAlmostEqual(cor, numpy.array([11.953453, 11.953817, 11.850193])*angstrom, 1e-5)
        cor = load_track("tracks/atom.pos.0000027.y")
        self.assertArraysAlmostEqual(cor, numpy.array([8.354914, 9.718356, 9.159180])*angstrom, 1e-5)
        cor = load_track("tracks/atom.pos.0001292.z")
        self.assertArraysAlmostEqual(cor, numpy.array([0.622863, 0.901589, -0.250132])*angstrom, 1e-5)
        # slicing test
        self.execute("tr-from-atrj", [os.path.join(input_dir, "bartek.atrj"), "--slice=::2"])
        time = load_track("tracks/time")
        self.assertArraysAlmostEqual(time, numpy.array([1, 3])*picosecond, 1e-5)
        step = load_track("tracks/step")
        self.assertArraysAlmostEqual(step, numpy.array([1000, 3000]), 1e-5)
        step = load_track("tracks/total_energy")
        self.assertArraysAlmostEqual(step, numpy.array([341.860357, 336.136295])*kcalmol, 1e-5)
        cor = load_track("tracks/atom.pos.0000000.x")
        self.assertArraysAlmostEqual(cor, numpy.array([11.953453, 11.850193])*angstrom, 1e-5)
        cor = load_track("tracks/atom.pos.0000027.y")
        self.assertArraysAlmostEqual(cor, numpy.array([8.354914, 9.159180])*angstrom, 1e-5)
        cor = load_track("tracks/atom.pos.0001292.z")
        self.assertArraysAlmostEqual(cor, numpy.array([0.622863, -0.250132])*angstrom, 1e-5)

    def test_from_dlpoly_hist(self):
        self.execute("tr-from-dlpoly-hist", [os.path.join(input_dir, "dlpoly_uo", "HISTORY")])
        time = load_track("tracks/time")
        self.assertAlmostEqual(time[0], 4*picosecond)
        self.assertAlmostEqual(time[1], 4.05*picosecond)
        # test will be extended once we know for sure that our assumptions for
        # the units in the dl_poly file are correct.

    def test_from_dlpoly_output(self):
        self.execute("tr-from-dlpoly-output", [os.path.join(input_dir, "dlpoly_uo", "OUTPUT")])
        step = load_track("tracks/step")
        self.assertAlmostEqual(step[0], 4000)
        self.assertAlmostEqual(step[1], 4050)
        time = load_track("tracks/time")
        self.assertAlmostEqual(time[0], 4*picosecond)
        self.assertAlmostEqual(time[1], 4.05*picosecond)
        # test will be extended once we know for sure that our assumptions for
        # the units in the dl_poly file are correct.

    def test_from_lammps_dump(self):
        self.execute("tr-from-lammps-dump", [os.path.join(input_dir, "lammps2", "dump.txt"), "A", "pos3", "A/fs", "vel3"])
        step = load_track("tracks/step")
        self.assertAlmostEqual(step[0], 0)
        self.assertAlmostEqual(step[-1], 45)
        pos0x = load_track("tracks/atom.pos.0000000.x")
        self.assertAlmostEqual(pos0x[0]/angstrom, 0.76561)
        self.assertAlmostEqual(pos0x[-1]/angstrom, 0.897658)
        vel5y = load_track("tracks/atom.vel.0000005.y")
        self.assertAlmostEqual(vel5y[0]/(angstrom/femtosecond), 0.0188858)
        self.assertAlmostEqual(vel5y[5]/(angstrom/femtosecond), 0.00913911)
        self.assertAlmostEqual(vel5y[-1]/(angstrom/femtosecond), 0.00252762)

    def test_from_gro(self):
        self.execute("tr-from-gro", [os.path.join(input_dir, "gromacs", "water2.gro")])
        time = load_track("tracks/time")
        self.assertAlmostEqual(time[0]/picosecond, 0.0)
        self.assertAlmostEqual(time[-1]/picosecond, 1.0)
        pos0x = load_track("tracks/atom.pos.0000000.x")
        self.assertAlmostEqual(pos0x[0]/nanometer, 0.126)
        vel5y = load_track("tracks/atom.vel.0000005.y")
        self.assertAlmostEqual(vel5y[1]/(nanometer/picosecond), -0.8216)
        cellby = load_track("tracks/cell.b.y")
        self.assertAlmostEqual(cellby[1]/nanometer, 1.82060)
        cellbz = load_track("tracks/cell.b.z")
        self.assertAlmostEqual(cellbz[1]/nanometer, 0.0)


    def test_to_xyz(self):
        self.from_xyz("thf01", "pos")
        # all-atoms version
        self.execute("tr-to-xyz", [os.path.join(input_dir, "thf01/init.xyz"), "tracks/atom.pos", "test.pos.xyz"])
        xyz_reader_orig = XYZReader(os.path.join(input_dir, "thf01/md-pos-1.xyz"))
        xyz_reader_copy = XYZReader("test.pos.xyz")
        self.assertEqual(xyz_reader_orig.symbols,xyz_reader_copy.symbols)
        for (title_orig, coordinates_orig), (tile_copy, coordinates_copy) in zip(xyz_reader_orig, xyz_reader_copy):
            self.assertArraysAlmostEqual(coordinates_orig, coordinates_copy, 1e-7)
        # atom-filter version
        self.execute("tr-to-xyz", [os.path.join(input_dir, "thf01/init.xyz"), "tracks/atom.pos", "test.pos.xyz", "-a2,5"])
        xyz_reader_orig = XYZReader(os.path.join(input_dir, "thf01/md-pos-1.xyz"))
        xyz_reader_copy = XYZReader("test.pos.xyz")
        self.assertEqual(xyz_reader_copy.symbols,('C','H'))
        for (title_orig, coordinates_orig), (tile_copy, coordinates_copy) in zip(xyz_reader_orig, xyz_reader_copy):
            self.assertArraysAlmostEqual(coordinates_orig[[2,5]], coordinates_copy, 1e-7)
        self.from_xyz("water32", "pos")
        # unit_cell_version without ref.psf
        self.execute("tr-to-xyz", [
            os.path.join(input_dir, "water32/init.xyz"),
            "9.865*A,", "tracks/atom.pos", os.path.join(output_dir, "water32.noref.pos.xyz"),
        ])
        # unit_cell_version with ref.psf
        self.execute("tr-to-xyz", [
            os.path.join(input_dir, "water32/init.xyz"),
            os.path.join(input_dir, "water32/init.psf"),
            "9.865*A,", "tracks/atom.pos", os.path.join(output_dir, "water32.ref.pos.xyz"),
        ])
        self.from_xyz("ar108", "pos")

    def test_txt_slice_length(self):
        self.from_cp2k_ener("water32")
        # tr-to-txt
        lines = self.execute("tr-to-txt", ["tracks/temperature"])
        tmp1 = numpy.array([float(line) for line in lines], float)
        tmp2 = load_track("tracks/temperature")
        self.assertArraysEqual(tmp1, tmp2)
        self.assertEqual(len(lines), 201)
        # tr-length
        length = int("".join(self.execute("tr-length", ["tracks/temperature"])))
        self.assertEqual(length, 201)
        # tr-slice
        self.execute("tr-slice", ["tracks/temperature", "20:80:5", "tracks/temperature_sliced"])
        length = int("".join(self.execute("tr-length", ["tracks/temperature_sliced"])))
        self.assertEqual(length, 12)
        t = load_track("tracks/temperature")
        ts = load_track("tracks/temperature_sliced")
        self.assertArraysEqual(t[20:80:5], ts)
        # tr-from-txt
        tmp1 = numpy.arange(101, dtype=float)
        lines = [str(val) for val in tmp1]
        self.execute("tr-from-txt", ["tracks/tmp"], stdin=lines)
        tmp2 = load_track("tracks/tmp")
        self.assertArraysEqual(tmp1, tmp2)

    def test_read_write_multiple(self):
        def check(subs):
            sub = parse_slice(subs)
            # slice in read
            self.from_cp2k_ener("thf01")
            t1 = load_track("tracks/time", sub)
            k1 = load_track("tracks/kinetic_energy", sub)
            lines = self.execute("tr-to-txt", ["-s%s" % subs, "ps", "tracks/time", "kjmol", "tracks/kinetic_energy"])
            self.execute("tr-from-txt", ["ps", "tracks/time", "kjmol", "tracks/kinetic_energy"], stdin=lines)
            t2 = load_track("tracks/time")
            k2 = load_track("tracks/kinetic_energy")
            self.assertArraysAlmostEqual(t1, t2, 1e-5)
            self.assertArraysAlmostEqual(k1, k2, 1e-5)
            # slice in write
            self.from_cp2k_ener("thf01")
            t1 = load_track("tracks/time", sub)
            k1 = load_track("tracks/kinetic_energy", sub)
            lines = self.execute("tr-to-txt", ["ps", "tracks/time", "kjmol", "tracks/kinetic_energy"])
            self.execute("tr-from-txt", ["-s%s" % subs, "ps", "tracks/time", "kjmol", "tracks/kinetic_energy"], stdin=lines)
            t2 = load_track("tracks/time")
            k2 = load_track("tracks/kinetic_energy")
            self.assertArraysAlmostEqual(t1, t2, 1e-5)
            self.assertArraysAlmostEqual(k1, k2, 1e-5)
            # - in write, no slice
            self.from_cp2k_ener("thf01")
            k1 = load_track("tracks/kinetic_energy")
            lines = self.execute("tr-to-txt", ["ps", "tracks/time", "kjmol", "tracks/kinetic_energy"])
            self.execute("tr-from-txt", ["ps", "-", "kjmol", "tracks/test"], stdin=lines)
            k2 = load_track("tracks/test")
            self.assertArraysAlmostEqual(k1, k2, 1e-5)
        check("::")
        check("20:601:5")

    def test_ac(self):
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        ndim = len(glob.glob("tracks/atom.vel.*"))
        self.execute("tr-ac", glob.glob("tracks/atom.vel.*") + ["5.0*fs", "tracks/vac_a1"])
        self.execute("tr-ac-error", ["tracks/vac_a1", str(ndim), "5.0*fs", "5000*fs", "200*fs"])
        self.execute("tr-ac", glob.glob("tracks/atom.vel.*") + ["tracks/time", "tracks/vac_a2"])
        self.execute("tr-ac-error", ["tracks/vac_a2", str(ndim), "tracks/time", "200*fs"])
        length = int("".join(self.execute("tr-length", ["tracks/vac_a2"])))
        self.assertEqual(length, 501)
        self.execute("tr-slice", ["tracks/time", ":%i:" % length, "tracks/time_sliced"])
        self.execute("tr-plot", [
            "-x", "delta t", "-y", "VAC", "-t", "Velocity autocorrelation function (thf01)", "--xunit=ps",
            ":line", "tracks/time_sliced", "tracks/vac_a1", "tracks/vac_a1.error",
            os.path.join(output_dir, "ac_vac_a1.png")
        ])
        self.execute("tr-plot", [
            "--ylim=-1,1", "-x", "delta t", "-y", "VAC", "-t", "Normalized velocity autocorrelation function (thf01)", "--xunit=ps",
            ":line", "tracks/time_sliced", "tracks/vac_a1.normalized", "tracks/vac_a1.normalized.error",
            os.path.join(output_dir, "ac_vac_a1.normalized.png")
        ])
        tmp1 = load_track("tracks/vac_a1")
        tmp2 = load_track("tracks/vac_a2")
        self.assertArraysEqual(tmp1, tmp2)
        tmp1 = load_track("tracks/vac_a1.normalized")
        tmp2 = load_track("tracks/vac_a2.normalized")
        self.assertArraysEqual(tmp1, tmp2)
        self.assertEqual(tmp1[0], 1.0)
        tmp1 = load_track("tracks/vac_a1.error")
        tmp2 = load_track("tracks/vac_a2.error")
        self.assertArraysEqual(tmp1, tmp2)
        self.assertArrayConstant(tmp1, tmp1[0])
        tmp1 = load_track("tracks/vac_a1.normalized.error")
        tmp2 = load_track("tracks/vac_a2.normalized.error")
        self.assertArraysEqual(tmp1, tmp2)
        self.assertArrayConstant(tmp1, tmp1[0])

        self.execute("tr-ac", glob.glob("tracks/atom.vel.*") + ["-m 4000*fs", "5.0*fs", "tracks/vac_b1"])
        self.execute("tr-ac-error", ["tracks/vac_b1", str(ndim), "5.0*fs", "5000*fs", "200*fs"])
        self.execute("tr-ac", glob.glob("tracks/atom.vel.*") + ["-m 4000*fs", "tracks/time", "tracks/vac_b2"])
        self.execute("tr-ac-error", ["tracks/vac_b2", str(ndim), "tracks/time", "200*fs"])
        length = int("".join(self.execute("tr-length", ["tracks/vac_b2"])))
        self.assertEqual(length, 801)
        self.execute("tr-slice", ["tracks/time", ":%i:" % length, "tracks/time_sliced"])
        self.execute("tr-plot", [
            "-x", "delta t", "-y", "VAC", "-t", "Velocity autocorrelation function (thf01)", "--xunit=ps",
            ":line", "tracks/time_sliced", "tracks/vac_b1", "tracks/vac_b1.error",
            os.path.join(output_dir, "ac_vac_b1.png")
        ])
        self.execute("tr-plot", [
            "--ylim=-1,1", "-x", "delta t", "-y", "VAC", "-t", "Normalized velocity autocorrelation function (thf01)", "--xunit=ps",
            ":line", "tracks/time_sliced", "tracks/vac_b1.normalized", "tracks/vac_b1.normalized.error",
            os.path.join(output_dir, "ac_vac_b1.normalized.png")
        ])
        tmp1 = load_track("tracks/vac_b1")
        tmp2 = load_track("tracks/vac_b2")
        self.assertArraysEqual(tmp1, tmp2)
        tmp1 = load_track("tracks/vac_b1.normalized")
        tmp2 = load_track("tracks/vac_b2.normalized")
        self.assertArraysEqual(tmp1, tmp2)
        self.assertEqual(tmp1[0], 1.0)
        tmp1 = load_track("tracks/vac_b1.error")
        tmp2 = load_track("tracks/vac_b2.error")
        self.assertArraysEqual(tmp1, tmp2)
        self.assertArrayConstant(tmp1, tmp1[0])
        tmp1 = load_track("tracks/vac_b1.normalized.error")
        tmp2 = load_track("tracks/vac_b2.normalized.error")
        self.assertArraysEqual(tmp1, tmp2)
        self.assertArrayConstant(tmp1, tmp1[0])

    def test_ac_fft(self):
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        ndim = len(glob.glob("tracks/atom.vel.*"))
        self.execute("tr-ac-fft", glob.glob("tracks/atom.vel.*") + ["5.0*fs", "tracks/vac", "-t", "fs"])

    def test_integrate(self):
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        ndim = len(glob.glob("tracks/atom.vel.*"))
        self.execute("tr-ac", glob.glob("tracks/atom.vel.*") + ["-m3000*fs", "tracks/time", "tracks/vac"])
        self.execute("tr-ac-error", ["tracks/vac", str(ndim), "tracks/time", "200*fs"])
        self.execute("tr-integrate", ["tracks/vac.normalized", "tracks/time"])
        length = int("".join(self.execute("tr-length", ["tracks/vac.normalized"])))
        self.assertEqual(length, 601)
        length = int("".join(self.execute("tr-length", ["tracks/vac.normalized.error"])))
        self.assertEqual(length, 601)
        length = int("".join(self.execute("tr-length", ["tracks/vac.normalized.int"])))
        self.assertEqual(length, 601)
        length = int("".join(self.execute("tr-length", ["tracks/vac.normalized.int.error"])))
        self.assertEqual(length, 601)
        self.execute("tr-slice", ["tracks/time", ":%i:" % length, "tracks/time_sliced"])
        self.execute("tr-plot", [
            "--ylim=-1,1", "-x", "delta t", "-y", "VAC", "-t", "Normalized velocity autocorrelation function (thf01)", "--xunit=ps",
            ":line", "tracks/time_sliced", "tracks/vac.normalized", "tracks/vac.normalized.error",
            os.path.join(output_dir, "integrate_vac.normalized.png")
        ])
        self.execute("tr-plot", [
            "-x", "delta t", "-y", "Int(VAC)", "-t", "Integral of the normalized velocity autocorrelation function (thf01)", "--xunit=ps", "--yunit=fs",
            ":line", "tracks/time_sliced", "tracks/vac.normalized.int", "tracks/vac.normalized.int.error",
            os.path.join(output_dir, "integrate_vac.normalized.int.png")
        ])

    def test_derive(self):
        self.from_cp2k_ener("thf01")
        self.execute("tr-integrate", ["tracks/temperature", "tracks/time"])
        self.execute("tr-derive", ["tracks/temperature.int", "tracks/time"])
        tmp1 = load_track("tracks/temperature")
        tmp2 = load_track("tracks/temperature.int.deriv")
        self.assertArraysAlmostEqual(tmp1[1:], tmp2, 1e-5)

    def test_rfft_irfft(self):
        # test on the whole thing
        self.from_xyz("thf01", "vel", ["-s:1000:", "-u1"]) # irrft always results in an even number of datapoints
        self.from_cp2k_ener("thf01")
        self.execute("tr-rfft", glob.glob("tracks/atom.vel.???????.?") + ["tracks/time", "tracks/spectrum"])
        self.execute("tr-irfft", glob.glob("tracks/atom.vel.???????.?.rfft"))
        self.assertEqual(len(glob.glob("tracks/atom.vel.???????.?")), len(glob.glob("tracks/*.rfft")))
        self.assertEqual(len(glob.glob("tracks/atom.vel.???????.?")), len(glob.glob("tracks/*.rfft.irfft")))
        for filename in glob.glob("tracks/atom.vel.???????.?"):
            other_filename = "%s.rfft.irfft" % filename
            tmp1 = load_track(filename)
            tmp2 = load_track(other_filename)
            self.assertEqual(tmp1.shape, tmp2.shape)
            self.assertArraysAlmostEqual(tmp1, tmp2, 1e-7)
        # A test plot
        tmp = 0
        for filename in glob.glob("tracks/atom.vel.???????.?.rfft"):
            tmp += abs(load_track(filename))**2
        dump_track("tracks/y", tmp)
        self.execute("tr-plot", [
            "--xunit=1/cm", "--xlim=0,3500/cm",
            ":line", "tracks/spectrum.wavenumbers", "tracks/y",
            os.path.join(output_dir, "rfft_irfft_test.png")
        ])
        # test with a slice
        self.execute("tr-rfft", ["--slice=100:203:2",] + glob.glob("tracks/atom.vel.???????.?") + ["tracks/time", "tracks/spectrum"])
        self.execute("tr-irfft", glob.glob("tracks/atom.vel.*.rfft"))
        self.assertEqual(len(glob.glob("tracks/atom.vel.???????.?")), len(glob.glob("tracks/*.rfft")))
        self.assertEqual(len(glob.glob("tracks/atom.vel.???????.?")), len(glob.glob("tracks/*.rfft.irfft")))
        for filename in glob.glob("tracks/atom.vel.*.?"):
            other_filename = "%s.rfft.irfft" % filename
            tmp1 = load_track(filename, slice(100,203,2))
            tmp2 = load_track(other_filename)
            self.assertEqual(tmp1.shape, tmp2.shape)
            self.assertArraysAlmostEqual(tmp1, tmp2, 1e-7)
        # A test plot
        tmp = 0
        for filename in glob.glob("tracks/atom.vel.???????.?.rfft"):
            tmp += abs(load_track(filename))**2
        dump_track("tracks/y", tmp)
        self.execute("tr-plot", [
            "--xunit=1/cm", "--xlim=0,3500/cm",
            ":line", "tracks/spectrum.wavenumbers", "tracks/y",
            os.path.join(output_dir, "rfft_irfft_test_slice.png")
        ])

    def test_fit_peaks(self):
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        self.execute("tr-spectrum", glob.glob("tracks/atom.vel.*") + ["tracks/time", "tracks/spectrum"])
        output = self.execute("tr-fit-peaks", [
            "tracks/spectrum.wavenumbers", "tracks/spectrum.amplitudes", "1900", "2200",
            "0.0001:2050.0:50.0:0.01", "--dump-model=tracks/spectrum.model", #"--no-fit",
        ])
        f = file(os.path.join(output_dir, "fit_peaks.out"), "w")
        f.writelines(output)
        f.close()
        self.execute("tr-plot", [
            "--xlabel=Wavenumber", "--ylabel=Amplitude", "--xunit=1/cm",
            ":line", "-s3::", "tracks/spectrum.wavenumbers", "tracks/spectrum.amplitudes",
            ":line", "-s3::", "tracks/spectrum.wavenumbers", "tracks/spectrum.model",
            ":vline", "1900/cm",
            ":vline", "2200/cm",
            os.path.join(output_dir, "fit_peaks_spectrum.png"),
        ])

    def check_deriv(self, pos, vel, time, relerr):
        self.execute("tr-derive", [pos, time])
        v = load_track(vel)
        v_check = load_track("%s.deriv" % pos)
        v_half = 0.5*(v[1:]+v[:-1])
        self.assertArraysAlmostEqual(v_check, v_half, relerr, do_mean=True)

    def test_ic_dist(self):
        self.from_xyz("thf01", "pos")
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        # just pos
        self.execute("tr-ic-dist", ["tracks/atom.pos.0000001", "tracks/atom.pos.0000002", "tracks/test"])
        dists = load_track("tracks/test")
        self.assertAlmostEqual(dists[0], 4.25631, 4)
        self.assertAlmostEqual(dists[1], 4.28458, 4)
        self.assertAlmostEqual(dists[-1], 4.26709, 4)
        # slice
        self.execute("tr-ic-dist", ["-s20:601:5", "tracks/atom.pos.0000001", "tracks/atom.pos.0000002", "tracks/test"])
        dists = load_track("tracks/test")
        self.assertAlmostEqual(dists[0], 4.32567, 4)
        self.assertAlmostEqual(dists[1], 4.41805, 4)
        self.assertAlmostEqual(dists[-1], 4.35014, 4)
        # pos and vel
        self.execute("tr-ic-dist", ["--project",
            "tracks/atom.pos.0000001", "tracks/atom.pos.0000002",
            "tracks/atom.vel.0000001", "tracks/atom.vel.0000002",
            "tracks/test_pos", "tracks/test_vel",
        ])
        dists = load_track("tracks/test_pos")
        self.assertAlmostEqual(dists[0], 4.25631, 4)
        self.assertAlmostEqual(dists[1], 4.28458, 4)
        self.assertAlmostEqual(dists[-1], 4.26709, 4)
        self.check_deriv("tracks/test_pos", "tracks/test_vel", "tracks/time", 1e-1)
        proj_norm_sq = 0.0
        orig_norm_sq = 0.0

    def test_ic_bend(self):
        self.from_xyz("thf01", "pos")
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        # just pos
        self.execute("tr-ic-bend", ["tracks/atom.pos.0000001", "tracks/atom.pos.0000000", "tracks/atom.pos.0000002", "tracks/test"])
        bends = load_track("tracks/test")
        self.assertAlmostEqual(bends[0]*180/numpy.pi, 105.426, 3)
        self.assertAlmostEqual(bends[1]*180/numpy.pi, 102.286, 3)
        self.assertAlmostEqual(bends[-1]*180/numpy.pi, 107.284, 3)
        # slice
        self.execute("tr-ic-bend", ["-s20:601:5", "tracks/atom.pos.0000001", "tracks/atom.pos.0000000", "tracks/atom.pos.0000002", "tracks/test"])
        bends = load_track("tracks/test")
        self.assertAlmostEqual(bends[0]*180/numpy.pi, 104.739, 3)
        self.assertAlmostEqual(bends[1]*180/numpy.pi, 108.972, 3)
        self.assertAlmostEqual(bends[-1]*180/numpy.pi, 107.277, 3)
        # pos and vel
        self.execute("tr-ic-bend", [
            "tracks/atom.pos.0000001", "tracks/atom.pos.0000000", "tracks/atom.pos.0000002",
            "tracks/atom.vel.0000001", "tracks/atom.vel.0000000", "tracks/atom.vel.0000002",
            "tracks/test_pos", "tracks/test_vel",
        ])
        bends = load_track("tracks/test_pos")
        self.assertAlmostEqual(bends[0]*180/numpy.pi, 105.426, 3)
        self.assertAlmostEqual(bends[1]*180/numpy.pi, 102.286, 3)
        self.assertAlmostEqual(bends[-1]*180/numpy.pi, 107.284, 3)
        self.check_deriv("tracks/test_pos", "tracks/test_vel", "tracks/time", 1e-1)

    def test_ic_dihed(self):
        self.from_xyz("thf01", "pos")
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        # just pos
        self.execute("tr-ic-dihed", ["tracks/atom.pos.0000002", "tracks/atom.pos.0000003", "tracks/atom.pos.0000004", "tracks/atom.pos.0000001", "tracks/test"])
        diheds = load_track("tracks/test")
        self.assertAlmostEqual(diheds[0]*180/numpy.pi, 0.000, 3)
        self.assertAlmostEqual(diheds[1]*180/numpy.pi, -1.919, 3)
        self.assert_(diheds[99] < 0)
        self.assert_(diheds[199] > 0)
        self.assertAlmostEqual(diheds[-1]*180/numpy.pi, 21.320, 3)
        # just pos, different atom order
        self.execute("tr-ic-dihed", ["tracks/atom.pos.0000001", "tracks/atom.pos.0000004", "tracks/atom.pos.0000003", "tracks/atom.pos.0000002", "tracks/test"])
        diheds = load_track("tracks/test")
        self.assertAlmostEqual(diheds[0]*180/numpy.pi, 0.000, 3)
        self.assertAlmostEqual(diheds[1]*180/numpy.pi, -1.919, 3)
        self.assert_(diheds[99] < 0)
        self.assert_(diheds[199] > 0)
        self.assertAlmostEqual(diheds[-1]*180/numpy.pi, 21.320, 3)
        # slice
        self.execute("tr-ic-dihed", ["-s20:601:5", "tracks/atom.pos.0000002", "tracks/atom.pos.0000003", "tracks/atom.pos.0000004", "tracks/atom.pos.0000001", "tracks/test"])
        diheds = load_track("tracks/test")
        self.assertAlmostEqual(diheds[0]*180/numpy.pi, -15.209, 3)
        self.assertAlmostEqual(diheds[1]*180/numpy.pi, -16.602, 3)
        self.assertAlmostEqual(diheds[-1]*180/numpy.pi, -31.306, 3)
        # just pos and vel
        self.execute("tr-ic-dihed", [
            "tracks/atom.pos.0000002", "tracks/atom.pos.0000003", "tracks/atom.pos.0000004", "tracks/atom.pos.0000001",
            "tracks/atom.vel.0000002", "tracks/atom.vel.0000003", "tracks/atom.vel.0000004", "tracks/atom.vel.0000001",
            "tracks/test_pos", "tracks/test_vel"
        ])
        diheds = load_track("tracks/test_pos")
        self.assertAlmostEqual(diheds[0]*180/numpy.pi, 0.000, 3)
        self.assertAlmostEqual(diheds[1]*180/numpy.pi, -1.919, 3)
        self.assertAlmostEqual(diheds[-1]*180/numpy.pi, 21.320, 3)
        self.check_deriv("tracks/test_pos", "tracks/test_vel", "tracks/time", 1e-1)

    def test_ic_dtl(self):
        self.from_xyz("thf01", "pos")
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        # pos
        self.execute("tr-ic-dtl", ["tracks/atom.pos.0000001", "tracks/atom.pos.0000000", "tracks/atom.pos.0000002", "tracks/test"])
        dtls = load_track("tracks/test")
        self.assertAlmostEqual(dtls[0]/angstrom, 1.364, 3)
        self.assertAlmostEqual(dtls[1]/angstrom, 1.422, 3)
        self.assertAlmostEqual(dtls[-1]/angstrom, 1.337, 3)
        # slice
        self.execute("tr-ic-dtl", ["-s20:601:5", "tracks/atom.pos.0000001", "tracks/atom.pos.0000000", "tracks/atom.pos.0000002", "tracks/test"])
        dtls = load_track("tracks/test")
        self.assertAlmostEqual(dtls[0]/angstrom, 1.394, 3)
        self.assertAlmostEqual(dtls[1]/angstrom, 1.358, 3)
        self.assertAlmostEqual(dtls[-1]/angstrom, 1.367, 3)
        # pos and vel
        self.execute("tr-ic-dtl", [
            "tracks/atom.pos.0000001", "tracks/atom.pos.0000000", "tracks/atom.pos.0000002",
            "tracks/atom.vel.0000001", "tracks/atom.vel.0000000", "tracks/atom.vel.0000002",
            "tracks/test_pos", "tracks/test_vel",
        ])
        dtls = load_track("tracks/test_pos")
        self.assertAlmostEqual(dtls[0]/angstrom, 1.364, 3)
        self.assertAlmostEqual(dtls[1]/angstrom, 1.422, 3)
        self.assertAlmostEqual(dtls[-1]/angstrom, 1.337, 3)
        self.check_deriv("tracks/test_pos", "tracks/test_vel", "tracks/time", 1e-1)

    def test_ic_oop(self):
        self.from_xyz("thf01", "pos")
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        # pos
        self.execute("tr-ic-oop", ["tracks/atom.pos.0000002", "tracks/atom.pos.0000003", "tracks/atom.pos.0000004", "tracks/atom.pos.0000001", "tracks/test"])
        oops = load_track("tracks/test")
        self.assertAlmostEqual(oops[0]/angstrom, 0.000, 2)
        self.assertAlmostEqual(oops[1]/angstrom, 0.049, 2)
        self.assertAlmostEqual(oops[-1]/angstrom, -0.5515, 2)
        # slice
        self.execute("tr-ic-oop", ["-s20:601:5", "tracks/atom.pos.0000002", "tracks/atom.pos.0000003", "tracks/atom.pos.0000004", "tracks/atom.pos.0000001", "tracks/test"])
        oops = load_track("tracks/test")
        self.assertAlmostEqual(oops[0]/angstrom, 0.380, 2)
        self.assertAlmostEqual(oops[1]/angstrom, 0.419, 2)
        self.assertAlmostEqual(oops[-1]/angstrom, 0.755, 2)
        # pos and vel
        self.execute("tr-ic-oop", [
            "tracks/atom.pos.0000002", "tracks/atom.pos.0000003", "tracks/atom.pos.0000004", "tracks/atom.pos.0000001",
            "tracks/atom.vel.0000002", "tracks/atom.vel.0000003", "tracks/atom.vel.0000004", "tracks/atom.vel.0000001",
            "tracks/test_pos", "tracks/test_vel"
        ])
        oops = load_track("tracks/test_pos")
        self.assertAlmostEqual(oops[0]/angstrom, 0.000, 2)
        self.assertAlmostEqual(oops[1]/angstrom, 0.049, 2)
        self.assertAlmostEqual(oops[-1]/angstrom, -0.5515, 2)
        self.check_deriv("tracks/test_pos", "tracks/test_vel", "tracks/time", 1e-1)

    def test_ic_psf(self):
        def check_ic_psf(nbonds, nbends, ndiheds, ndtls, noops):
            # bond
            bond_filenames = glob.glob("tracks/atom.bond.pos*")
            self.assertEqual(len(bond_filenames), nbonds)
            for pos_filename in bond_filenames:
                bond_pos = load_track(pos_filename)
                index1, index2 = [int(word) for word in pos_filename.split(".")[-2:]]
                vel_filename = pos_filename.replace('pos', 'vel')
                if os.path.isfile(vel_filename):
                    bond_pos_check, bond_vel_check = vector.dist(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index2),
                    )
                    bond_vel = load_track(vel_filename)
                    self.assertArraysEqual(bond_vel, bond_vel_check)
                else:
                    bond_pos_check = vector.dist(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                    )
                self.assertArraysEqual(bond_pos, bond_pos_check)
            # bend
            bend_filenames = glob.glob("tracks/atom.bend.pos*")
            self.assertEqual(len(bend_filenames), nbends)
            for pos_filename in bend_filenames:
                bend_pos = load_track(pos_filename)
                index1, index2, index3 = [int(word) for word in pos_filename.split(".")[-3:]]
                vel_filename = pos_filename.replace('pos', 'vel')
                if os.path.isfile(vel_filename):
                    bend_pos_check, bend_vel_check = vector.bend(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index3),
                    )
                    bend_vel = load_track(vel_filename)
                    self.assertArraysEqual(bend_vel, bend_vel_check)
                else:
                    bend_pos_check = vector.bend(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                    )
                self.assertArraysEqual(bend_pos, bend_pos_check)
            # span
            span_filenames = glob.glob("tracks/atom.span.pos*")
            self.assertEqual(len(span_filenames), nbends)
            for pos_filename in span_filenames:
                span_pos = load_track(pos_filename)
                index1, index2, index3 = [int(word) for word in pos_filename.split(".")[-3:]]
                vel_filename = pos_filename.replace('pos', 'vel')
                if os.path.isfile(vel_filename):
                    span_pos_check, span_vel_check = vector.dist(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index3),
                    )
                    span_vel = load_track(vel_filename)
                    self.assertArraysEqual(span_vel, span_vel_check)
                else:
                    span_pos_check = vector.dist(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                    )
                self.assertArraysEqual(span_pos, span_pos_check)
            # dihed
            dihed_filenames = glob.glob("tracks/atom.dihed.pos*")
            self.assertEqual(len(dihed_filenames), ndiheds)
            for pos_filename in dihed_filenames:
                dihed_pos = load_track(pos_filename)
                index1, index2, index3, index4 = [int(word) for word in pos_filename.split(".")[-4:]]
                vel_filename = pos_filename.replace('pos', 'vel')
                if os.path.isfile(vel_filename):
                    dihed_pos_check, dihed_vel_check = vector.dihed(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index4),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index3),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index4),
                    )
                    dihed_vel = load_track(vel_filename)
                    self.assertArraysEqual(dihed_vel, dihed_vel_check)
                else:
                    dihed_pos_check = vector.dihed(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index4),
                    )
                self.assertArraysEqual(dihed_pos, dihed_pos_check)
            # dtl
            dtl_filenames = glob.glob("tracks/atom.dtl.pos*")
            self.assertEqual(len(dtl_filenames), ndtls)
            for pos_filename in dtl_filenames:
                dtl_pos = load_track(pos_filename)
                index1, index2, index3 = [int(word) for word in pos_filename.split(".")[-3:]]
                vel_filename = pos_filename.replace('pos', 'vel')
                if os.path.isfile(vel_filename):
                    dtl_pos_check, dtl_vel_check = vector.dtl(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index3),
                    )
                    dtl_vel = load_track(vel_filename)
                    self.assertArraysEqual(dtl_vel, dtl_vel_check)
                else:
                    dtl_pos_check = vector.dtl(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                    )
                self.assertArraysEqual(dtl_pos, dtl_pos_check)
            # oop
            oop_filenames = glob.glob("tracks/atom.oop.pos*")
            self.assertEqual(len(oop_filenames), noops)
            for pos_filename in oop_filenames:
                oop_pos = load_track(pos_filename)
                index1, index2, index3, index4 = [int(word) for word in pos_filename.split(".")[-4:]]
                vel_filename = pos_filename.replace('pos', 'vel')
                if os.path.isfile(vel_filename):
                    oop_pos_check, oop_vel_check = vector.oop(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index4),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index3),
                        vector.TrackVector.from_prefix("tracks/atom.vel.%07i" % index4),
                    )
                    oop_vel = load_track(vel_filename)
                    self.assertArraysEqual(oop_vel, oop_vel_check)
                else:
                    oop_pos_check = vector.oop(
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index1),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index2),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index3),
                        vector.TrackVector.from_prefix("tracks/atom.pos.%07i" % index4),
                    )
                self.assertArraysEqual(oop_pos, oop_pos_check)
        self.from_xyz("thf01", "pos")
        self.execute("tr-ic-psf", ["bond", "tracks/atom.pos", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["bend", "tracks/atom.pos", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["span", "tracks/atom.pos", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["dihed", "tracks/atom.pos", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["dtl", "tracks/atom.pos", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["oop", "tracks/atom.pos", os.path.join(input_dir, "thf01/init.psf")])
        check_ic_psf(13,25,33,50,16)
        # clean up and start again with --filter-atoms
        shutil.rmtree("tracks")
        self.from_xyz("thf01", "pos")
        self.execute("tr-ic-psf", ["bond", "tracks/atom.pos", "1,2,3,4", "5,6,7,8,9,10,11,12", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["bend", "tracks/atom.pos", "0,1,2,3,4", "0,1,2,3,4", "0,1,2,3,4", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["span", "tracks/atom.pos", "0,1,2,3,4", "0,1,2,3,4", "0,1,2,3,4", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["dihed", "tracks/atom.pos", "5,6,7,8,9,10,11,12", "1,2,3,4", "1,2,3,4", "5,6,7,8,9,10,11,12", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["dtl", "tracks/atom.pos", "0,1,2,3,4", "0,1,2,3,4", "0,1,2,3,4", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["oop", "tracks/atom.pos", "1,2,3,4,9,10,11,12", "1,2,3,4,9,10,11,12", "1,2,3,4,9,10,11,12", "3,4", os.path.join(input_dir, "thf01/init.psf")])
        check_ic_psf(8,5,12,10,8)
        # clean up and start again with velocites
        shutil.rmtree("tracks")
        self.from_xyz("thf01", "pos")
        self.from_xyz("thf01", "vel", ["-u1"])
        self.execute("tr-ic-psf", ["bond", "tracks/atom.pos", "tracks/atom.vel", "1,2,3,4", "5,6,7,8,9,10,11,12", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["bend", "tracks/atom.pos", "tracks/atom.vel", "0,1,2,3,4", "0,1,2,3,4", "0,1,2,3,4", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["span", "tracks/atom.pos", "tracks/atom.vel", "0,1,2,3,4", "0,1,2,3,4", "0,1,2,3,4", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["dihed", "tracks/atom.pos", "tracks/atom.vel", "5,6,7,8,9,10,11,12", "1,2,3,4", "1,2,3,4", "5,6,7,8,9,10,11,12", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["dtl", "tracks/atom.pos", "tracks/atom.vel", "0,1,2,3,4", "0,1,2,3,4", "0,1,2,3,4", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-ic-psf", ["oop", "tracks/atom.pos", "tracks/atom.vel", "1,2,3,4,9,10,11,12", "1,2,3,4,9,10,11,12", "1,2,3,4,9,10,11,12", "3,4", os.path.join(input_dir, "thf01/init.psf")])
        check_ic_psf(8,5,12,10,8)

    def test_mean_std(self):
        self.from_xyz("thf01", "vel", ["-u1"])
        self.from_cp2k_ener("thf01")
        molecule = XYZFile(os.path.join(input_dir, "thf01/init.xyz")).get_molecule()
        # A1) compute the kinetic energy per atom:
        for index, number in enumerate(molecule.numbers):
            vx = load_track("tracks/atom.vel.%07i.x" % index)
            vy = load_track("tracks/atom.vel.%07i.y" % index)
            vz = load_track("tracks/atom.vel.%07i.z" % index)
            ekin = 0.5*periodic[number].mass*(vx*vx+vy*vy+vz*vz)
            dump_track("tracks/atom.ekin.%07i" % index, ekin)
        # A2) average and compare to the kinetic energy from the energy file
        self.execute("tr-mean-std", glob.glob("tracks/atom.ekin.*") + ["tracks/atom.ekin"])
        ekin_mean = load_track("tracks/atom.ekin.mean")
        ekin = load_track("tracks/kinetic_energy")
        self.assertArraysAlmostEqual(ekin/13, ekin_mean, 1e-6)
        # B) Verify the relation between std and error
        self.execute("tr-mean-std", glob.glob("tracks/atom.vel.*") + ["tracks/atom.vel"])
        vel_error = load_track("tracks/atom.vel.error")
        vel_std = load_track("tracks/atom.vel.std")
        self.assertArraysAlmostEqual(vel_std, vel_error*numpy.sqrt(3*13), 1e-5)

    def test_blav(self):
        self.from_cp2k_ener("thf01")
        self.execute("tr-blav", ["tracks/temperature", "tracks/time", "-b50", "-tfs"])
        self.execute("tr-blav", [
            "tracks/temperature", "tracks/time", "-b10", "-tfs",
            "--plot-error=%s" % os.path.join(output_dir, "blav_error.png"),
            "--plot-ctime=%s" % os.path.join(output_dir, "blav_ctime.png"),
        ])
        self.execute("tr-blav", [
            "tracks/temperature", "tracks/time", "-b10", "-tfs", "--slice=10::4",
            "--plot-error=%s" % os.path.join(output_dir, "blav_error_sliced.png"),
            "--plot-ctime=%s" % os.path.join(output_dir, "blav_ctime_sliced.png"),
        ])

    def test_split_com(self):
        self.from_xyz("water32", "vel", ["-u1"])
        self.from_cp2k_ener("water32")
        # first test the --filter-molecules
        self.execute("tr-split-com", ["-m2,5", "tracks/atom.vel", "vel", os.path.join(input_dir, "water32/init.psf")])
        self.assertEqual(len(glob.glob("tracks/com.vel.*")),6)
        self.assertEqual(len(glob.glob("tracks/rel.vel.*")),0)
        self.execute("tr-split-com", ["-m2,5", "--rel", "tracks/atom.vel", "vel", os.path.join(input_dir, "water32/init.psf")])
        self.assertEqual(len(glob.glob("tracks/com.vel.*")),6)
        self.assertEqual(len(glob.glob("tracks/rel.vel.*")),18)
        # then do the remaining tests
        self.execute("tr-split-com", ["tracks/atom.vel", "--rel", "vel", os.path.join(input_dir, "water32/init.psf")])
        psf = PSFFile(os.path.join(input_dir, "water32/init.psf"))
        # check that the coms have in total no translational kinetic energy
        for c in 'xyz':
            self.execute("tr-mean-std", glob.glob("tracks/com.vel.*.%s" % c) + ["tracks/com.vel.%s" % c])
            vmean = load_track("tracks/com.vel.%s.mean" % c)
            self.assertArrayAlmostZero(vmean, 1e-10)
        # check that the weighted sum of the relative velocities is always zero, per molecule
        for m_index in xrange(32):
            for c in 'xyz':
                tmp = 0
                for a_index in (psf.molecules==m_index).nonzero()[0]:
                    mass = periodic[psf.numbers[a_index]].mass
                    tmp += mass*load_track("tracks/rel.vel.%07i.%s" % (a_index, c))
                self.assertArrayAlmostZero(tmp, 1e-14)
        # compute the total kinetic energy from the com and the rel contributions
        # and compare it to tracks/kinetic_energy
        ekin = 0
        mass_water = periodic[1].mass*2+periodic[8].mass
        for m_index in xrange(32):
            for c in 'xyz':
                v = load_track("tracks/com.vel.%07i.%s" % (m_index, c))
                ekin += 0.5*mass_water*v*v
                for a_index in (psf.molecules==m_index).nonzero()[0]:
                    mass = periodic[psf.numbers[a_index]].mass
                    v = load_track("tracks/rel.vel.%07i.%s" % (a_index, c))
                    ekin += 0.5*mass*v*v
        ekin_check = load_track("tracks/kinetic_energy")
        self.assertArraysAlmostEqual(ekin, ekin_check, 1e-6)

    def test_filter(self):
        verbose = False
        if verbose: print
        def check_filter(case, kind, expression, expected):
            arguments = [os.path.join(input_dir, "%s/init.psf" % case), kind, expression]
            result = self.execute("tr-select", arguments, verbose=verbose)[0].strip()
            self.assertEqual(result, expected)
            if verbose: print "%s  |  %s  |  %s   =>   %s" % (case, kind, expression, result)

        check_filter('thf01', 'at', 'a.label=="ca" or a.label=="CB"', '1,2,3,4')
        check_filter('thf01', 'at', 'a.symbol=="c"', '1,2,3,4')
        check_filter('thf01', 'at', 'a.symbol=="C"', '1,2,3,4')
        check_filter('thf01', 'at', 'a.nlabels=="ca,cb,hb,hb"', '3,4')
        check_filter('thf01', 'at', 'a.nsymbols=="c,c,h,h"', '3,4')
        check_filter('thf01', 'at', 'a.nlabels=="o,cb,ha,ha"', '1,2')
        check_filter('thf01', 'at', 'a.nsymbols=="o,c,h_2"', '1,2')
        check_filter('thf01', 'at', 'a.nlabels=="ca,cb,hb_2"', '3,4')
        check_filter('thf01', 'at', 'a.nsymbols=="c_2,h_2"', '3,4')
        check_filter('thf01', 'at', 'a.nnumbers=="6_2,1_2"', '3,4')
        check_filter('thf01', 'at', 'a.nnumbers=="6,8,1,1"', '1,2')
        check_filter('thf01', 'at', 'a.nnumbers=="6,6"', '0')
        check_filter('thf01', 'at', 'a.number=="6"', '')
        check_filter('thf01', 'at', 'a.number==6', '1,2,3,4')
        check_filter('thf01', 'at', 'a.index==6', '6')
        check_filter('thf01', 'at', '0 in a.nindexes', '1,2')
        check_filter('thf01', 'at', 'a.m.index==0', '0,1,2,3,4,5,6,7,8,9,10,11,12')
        check_filter('thf01', 'mol', 'a.index==6', '0')
        check_filter('thf01', 'mol', 'a.index=="6"', '')
        check_filter('thf01', 'mol', 'm.index==0', '0')
        check_filter('thf01', 'mol', 'm.cf=="C_4,O,H_8"', '0')
        check_filter('thf01', 'mol', 'm.cf=="C_3,O,H_8"', '')
        check_filter('thf01', 'mol', 'm.cfl=="Ca_2,Cb_2,O,Ha_4,Hb_4"', '0')
        check_filter('thf01', 'mol', 'm.cfl=="Ca_3,O,Ha_4,Ha_4"', '')
        check_filter('water32', 'mol', 'm.cf=="H_2,O"', '0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31')
        check_filter('water32', 'mol', 'm.index==5', '5')
        check_filter('water32', 'mol', 'a.index==6', '2')

    def test_filter_rings(self):
        output = self.execute("tr-select-rings", [os.path.join(input_dir, "thf01/init.psf"), "5"])
        self.assert_(len(output)==1)
        self.assertEqual(set([0,1,2,3,4]), set(int(word) for word in output[0].split(",")))

    def test_fluct(self):
        self.from_cp2k_ener("thf01")
        self.execute("tr-fluct", ["tracks/temperature", "tracks/temperature", "tracks/test"])

    def test_hist(self):
        self.from_xyz("thf01", "pos")
        self.from_cp2k_ener("thf01")
        self.execute("tr-ic-psf", ['bond', 'tracks/atom.pos', '1,2,3,4', '5,6,7,8,9,10,11,12', os.path.join(input_dir, "thf01/init.psf")])
        # ordinary hist, no error bars
        self.execute("tr-hist", glob.glob("tracks/atom.bond.pos.???????.???????") + ["1.0*A", "1.2*A", "20", "tracks/atom.bond.pos.df"])
        df_hist = load_track("tracks/atom.bond.pos.df.hist")
        self.assertAlmostEqual(df_hist.sum(), 1.0, 2)
        self.execute("tr-plot", [
            "--title=C-H bond length distribution", "--xlabel=C-H Distance", "--xunit=A", "--yunit=1", "--ylabel=Frequency",
            ":bar", "tracks/atom.bond.pos.df.bins", "tracks/atom.bond.pos.df.hist",
            os.path.join(output_dir, "df_noerror.png"),
        ])
        # cumulative hist, no error bars
        cdf_hist = load_track("tracks/atom.bond.pos.df.cumul.hist")
        self.assertAlmostEqual(cdf_hist[-1], 1.0, 2)
        self.execute("tr-plot", [
            "--title=Cumulative C-H bond length distribution", "--xlabel=C-H Distance", "--xunit=A", "--yunit=1", "--ylabel=Frequency",
            ":bar", "tracks/atom.bond.pos.df.bins", "tracks/atom.bond.pos.df.cumul.hist",
            os.path.join(output_dir, "df_cumul_noerror.png"),
        ])
        # ordinary hist, with error bars
        self.execute("tr-hist", glob.glob("tracks/atom.bond.pos.???????.???????") + ["--bin-tracks", "1.0*A", "1.2*A", "20", "tracks/atom.bond.pos.df"])
        lines = []
        for bin_filename in sorted(glob.glob("tracks/atom.bond.pos.df.bin.???????"))[:19]:
            output = self.execute("tr-blav", [bin_filename, "tracks/time", "-b10"])
            lines.append(output[0])
        self.execute("tr-from-txt", ["tracks/atom.bond.pos.df.hist", "tracks/atom.bond.pos.df.hist.error"], stdin=lines)
        df_hist_bis = load_track("tracks/atom.bond.pos.df.hist")
        self.assertAlmostEqual(df_hist_bis.sum(), 1.0, 2)
        self.assertArraysAlmostEqual(df_hist[:19], df_hist_bis, 1e-5)
        self.execute("tr-plot", [
            "--title=C-H bond length distribution", "--xlabel=C-H Distance", "--xunit=A", "--yunit=1", "--ylabel=Frequency",
            ":bar", "tracks/atom.bond.pos.df.bins", "tracks/atom.bond.pos.df.hist", "tracks/atom.bond.pos.df.hist.error",
            os.path.join(output_dir, "df_error.png"),
        ])
        # cumulative hist, with error bars
        lines = []
        for bin_filename in sorted(glob.glob("tracks/atom.bond.pos.df.cumul.bin.???????"))[:19]:
            output = self.execute("tr-blav", [bin_filename, "tracks/time", "-b10"])
            lines.append(output[0])
        self.execute("tr-from-txt", ["tracks/atom.bond.pos.df.cumul.hist", "tracks/atom.bond.pos.df.cumul.hist.error"], stdin=lines)
        cdf_hist_bis = load_track("tracks/atom.bond.pos.df.cumul.hist")
        self.assertAlmostEqual(cdf_hist_bis[-1], 1.0, 2)
        self.assertArraysAlmostEqual(cdf_hist[:19], cdf_hist_bis, 1e-5)
        self.execute("tr-plot", [
            "--title=C-H bond length distribution", "--xlabel=C-H Distance", "--xunit=A", "--yunit=1", "--ylabel=Frequency",
            ":bar", "tracks/atom.bond.pos.df.bins", "tracks/atom.bond.pos.df.cumul.hist", "tracks/atom.bond.pos.df.cumul.hist.error",
            os.path.join(output_dir, "df_cumul_error.png"),
        ])

    def test_calc(self):
        # normal usage
        self.from_cp2k_ener("thf01")
        self.execute("tr-calc", ["k=tracks/kinetic_energy", "k/(3*13)*2/boltzmann", "tracks/tcheck"])
        k = load_track("tracks/kinetic_energy")
        t = k/(3*13)*2/boltzmann
        tcheck = load_track("tracks/tcheck")
        # evaluate a constant expression
        self.assertArraysEqual(t, tcheck)
        result = float(self.execute("tr-calc", ["cos(atAr.mass)"])[0])
        self.assertAlmostEqual(result, numpy.cos(periodic["Ar"].mass), 5)

    def test_shortest_distance1(self):
        self.from_xyz("thf01", "pos")
        group_a = ["tracks/atom.pos.0000005", "tracks/atom.pos.0000003", "tracks/atom.pos.0000007", "tracks/atom.pos.0000008"]
        group_b = ["tracks/atom.pos.0000009", "tracks/atom.pos.0000010", "tracks/atom.pos.0000011", "tracks/atom.pos.0000012"]
        self.execute("tr-shortest-distance", group_a + ["-"] + group_b + ["tracks/atom.pos.sd"])
        shortest_distances = load_track("tracks/atom.pos.sd")
        equal = numpy.zeros(len(shortest_distances), int)
        for atom_a in group_a:
            for atom_b in group_b:
                distances = vector.dist(
                    vector.TrackVector.from_prefix(atom_a),
                    vector.TrackVector.from_prefix(atom_b),
                )
                self.assert_((distances >= shortest_distances).all())
                equal += (shortest_distances == distances)
        self.assert_((equal > 0).all())

    def test_shortest_distance2(self):
        self.from_xyz("water32", "pos")
        group_a = ["tracks/atom.pos.0000000", "tracks/atom.pos.0000001", "tracks/atom.pos.0000002", "tracks/atom.pos.0000003"]
        group_b = ["tracks/atom.pos.0000015", "tracks/atom.pos.0000016", "tracks/atom.pos.0000017", "tracks/atom.pos.0000018"]
        self.execute("tr-shortest-distance", group_a + ["-"] + group_b + ["tracks/atom.pos.sd", "--cell=9.865*A,"])
        shortest_distances = load_track("tracks/atom.pos.sd")
        equal = numpy.zeros(len(shortest_distances), int)
        for atom_a in group_a:
            for atom_b in group_b:
                distances = vector.dist(
                    vector.TrackVector.from_prefix(atom_a),
                    vector.TrackVector.from_prefix(atom_b),
                    track_cell=cell.TrackCell.from_cell_str("9.865*A,")
                )
                self.assert_((distances >= shortest_distances).all())
                equal += (shortest_distances == distances)
        self.assert_((equal > 0).all())

    def test_pca(self):
        self.from_xyz("thf01", "pos")
        self.from_cp2k_ener("thf01")
        self.execute("tr-ic-psf", ["bond", "tracks/atom.pos", os.path.join(input_dir, "thf01/init.psf")])
        self.execute("tr-pca", glob.glob("tracks/atom.bond.pos.*") + ["tracks/pca", "-p"])
        self.execute("tr-plot", [
            "--xunit=ps", "--yunit=A", "--xlabel=Time", "--ylabel=Amplitude", "--title=First principal bond stretch mode",
            ":line", "tracks/time", "tracks/pca.pc.0000000",
            os.path.join(output_dir, "pc_first_time"),
        ])
        self.execute("tr-plot", [
            ":line", "tracks/pca.ccs", os.path.join(output_dir, "pca_ccs"),
        ])
        self.execute("tr-plot", [
            "--yunit=A", ":line", "tracks/pca.sigmas", os.path.join(output_dir, "pca_evals"),
        ])

    def test_pca_cosine_content(self):
        num = 10
        paths_in = []
        for i in xrange(10):
            delta = numpy.random.normal(0,0.01,5000)
            y = numpy.cumsum(delta)
            path = "y%i" % i
            dump_track(path, y)
            paths_in.append(path)
        self.execute("tr-pca", paths_in + ["pca", "-p", "-n", "4"])
        self.execute("tr-plot", [":line", "pca.ccs",
            os.path.join(output_dir, "pca_cosine_content_ccs.png")
        ])
        self.execute("tr-plot", [":line", "pca.sigmas",
            os.path.join(output_dir, "pca_cosine_content_sigmas.png")
        ])

        pc0 = load_track("pca.pc.0000000")
        cosamp = load_track("pca.cosamp")
        t = numpy.arange(len(pc0),dtype=float)*(numpy.pi/len(pc0))

        for i in xrange(num):
            cos = cosamp[i]*numpy.cos((i+1)*t)
            dump_track("pca.cos.%07i" % i, cos)
            self.execute("tr-plot", [
                ":line", "pca.pc.%07i" % i,
                ":line", "pca.cos.%07i" % i,
                os.path.join(output_dir, "pca_cosine_content_pc_%07i.png" % i)
            ])

    def test_pca_geom1(self):
        self.from_xyz("thf01", "pos")
        self.from_cp2k_ener("thf01")
        fn_average = os.path.join(output_dir, "average.xyz")
        self.execute("tr-pca-geom", ["tracks/atom.pos", os.path.join(input_dir, "thf01", "init.xyz"), "tracks/pca", fn_average, "-p"])
        self.execute("tr-plot", [
            "--xunit=ps", "--yunit=A", "--xlabel=Time", "--ylabel=Amplitude", "--title=First Cartesian principal component",
            ":line", "tracks/time", "tracks/pca.pc.0000000",
            os.path.join(output_dir, "pca_geom_first_time"),
        ])
        self.execute("tr-plot", [
            ":line", "tracks/pca.ccs", os.path.join(output_dir, "pca_geom_ccs"),
        ])
        self.execute("tr-plot", [
            "--yunit=A", ":line", "tracks/pca.sigmas", os.path.join(output_dir, "pca_geom_evals"),
        ])
        self.execute("tr-to-xyz-mode", [
            "tracks/pca.mode.0000000",
            os.path.join(input_dir, "thf01", "init.xyz"),
            os.path.join(output_dir, "pca_geom_thf01_mode0.xyz"),
        ])
        self.assert_(os.path.isfile(fn_average))

    def test_pca_geom2(self):
        self.from_xyz("solvated", "pos")
        fn_average = os.path.join(output_dir, "average.xyz")
        output = self.execute("tr-pca-geom", [
            "tracks/atom.pos", os.path.join(input_dir, "solvated", "init.xyz"),
            "tracks/pca", fn_average, "-a", "144,145,146,147,148,149,150,151,152"
        ])
        self.assertEqual(XYZFile(fn_average).symbols[1], "Si")

    def test_rdf_water32(self):
        self.from_xyz("water32", "pos")
        self.from_cp2k_ener("water32")

        prefixes_O = self.execute("tr-select", [os.path.join(input_dir, "water32/init.psf"), "at", "a.number==8", "--prefix=tracks/atom.pos"])[0]
        self.execute("tr-rdf", prefixes_O.split() + ["-s::20", "9.865*A,9.865*A,9.865*A", "10*A", "80", "tracks/rdf_O_O"])

        prefixes_H = self.execute("tr-select", [os.path.join(input_dir, "water32/init.psf"), "at", "a.number==1", "--prefix=tracks/atom.pos"])[0]
        self.execute("tr-rdf", prefixes_H.split() + ["-s::20", "9.865*A,9.865*A,9.865*A", "10*A", "80", "tracks/rdf_H_H"])

        self.execute("tr-rdf", prefixes_H.split() + ['-'] + prefixes_O.split() + ["-s::20", "9.865*A,9.865*A,9.865*A", "10*A", "80", "tracks/rdf_O_H"])

        self.execute("tr-plot", [
            "--xunit=A", "--yunit=1", "--xlabel=Iteratomic distance", "--ylabel=g(r)", "--title=Radial distribution functions",
            ":bar", "tracks/rdf_O_O.bins", "tracks/rdf_O_O.hist",
            ":bar", "tracks/rdf_H_H.bins", "tracks/rdf_H_H.hist",
            ":bar", "tracks/rdf_O_H.bins", "tracks/rdf_O_H.hist",
            ":hline", "1",
            os.path.join(output_dir, "rdf_water32_noerror")
        ])
        self.execute("tr-plot", [
            "--ylim=0,10", "--xunit=A", "--yunit=1", "--xlabel=Iteratomic distance", "--ylabel=f(r)", "--title=Cumulative radial distribution functions",
            ":bar", "tracks/rdf_O_O.bins", "tracks/rdf_O_O.cumul.hist",
            ":bar", "tracks/rdf_H_H.bins", "tracks/rdf_H_H.cumul.hist",
            ":bar", "tracks/rdf_O_H.bins", "tracks/rdf_O_H.cumul.hist",
            ":hline", "1",
            os.path.join(output_dir, "rdf_cumul_water32_noerror")
        ])

    def test_angular_momentum(self):
        self.from_xyz("water32", "pos")
        self.from_xyz("water32", "vel", ["-u1"])
        self.from_cp2k_ener("water32")
        # split positions and velocities in com and rel
        self.execute("tr-split-com", ["tracks/atom.pos", "pos", os.path.join(input_dir, "water32/init.psf"), "--rel"])
        self.execute("tr-split-com", ["tracks/atom.vel", "vel", os.path.join(input_dir, "water32/init.psf"), "--rel"])
        # compute the angular momenta
        self.execute("tr-angular-momentum", ["tracks/rel", os.path.join(input_dir, "water32/init.psf")])
        # check the number of generated files:
        self.assertEqual(len(glob.glob("tracks/ang.mom*")), 32*3)

    def test_norm(self):
        v1 = numpy.random.normal(0, 1, 100)
        v2 = numpy.random.normal(0, 1, 100)
        dump_track("v1", v1)
        dump_track("v2", v2)
        result = numpy.sqrt(v1*v1+v2*v2)
        self.execute("tr-norm", ["v1", "v2", "result"])
        self.assertArraysEqual(load_track("result"), result)

    def test_cc(self):
        t = numpy.arange(0,1001,dtype=float)/1000*numpy.pi*2
        dump_track("test0", numpy.sin(t))
        dump_track("test1", numpy.cos(t))
        dump_track("test2", -numpy.sin(t))
        dump_track("test3", numpy.sin(t)+1)
        lines = self.execute("tr-corr", ["test0", "test0", "test1", "test2", "test3"])
        values = [int(line.split()[-2]) for line in lines]
        self.assertEqual(values, [100, 0, -100, 100])

    def test_cwt(self):
        signal = numpy.zeros(1000, float)
        time = numpy.arange(1000)*femtosecond
        #signal[:500] = numpy.sin(time[:500]*2*numpy.pi/(50*femtosecond))
        #signal[500:1000] = numpy.sin(time[500:1000]*2*numpy.pi/(25*femtosecond))
        freq_mod = (numpy.cos(2*time/time[-1]*2*numpy.pi)+5)/6/(17*femtosecond)
        time_step = time[1]-time[0]
        signal = numpy.sin((freq_mod*2*numpy.pi*time_step).cumsum())
        dump_track("time", time)
        dump_track("signal", signal)
        dump_track("wavenum_mod", freq_mod/lightspeed)
        self.execute("tr-cwt", ["--kmax=2500/cm", "--kstep=20/cm", "20", "signal", "time", "cwt"])
        self.execute("tr-plot", ["--xunit=fs",
            ":line", "time", "cwt.mother.real",
            ":line", "time", "cwt.mother.imag",
        os.path.join(output_dir, "cwt_wavelets.png")])
        self.execute("tr-plot", ["--xunit=fs",
            ":line", "time", "signal",
        os.path.join(output_dir, "cwt_signal.png")])
        paths_z = glob.glob("cwt.scale.*")
        paths_z.sort()
        self.execute("tr-plot", ["--xunit=fs", "--yunit=1/cm", "--no-legend",
            ":contour", "time", "cwt.wavenumbers"] + paths_z + ["--slice=::20",
            ":line", "time", "wavenum_mod", "--color=k",
            ":line", "cwt.left_margin", "cwt.wavenumbers", "--color=k", "-d", "--",
            ":line", "cwt.right_margin", "cwt.wavenumbers", "--color=k", "-d", "--",
            ":hline", "1000/cm", "2000/cm", "--min=0.2", "--max=0.4",
            os.path.join(output_dir, "cwt_spectrogram.png")
        ])

    def test_scatter_plot(self):
        dump_track("x", numpy.random.normal(0,1,200))
        dump_track("y", numpy.random.normal(0,1,200))
        self.execute("tr-plot", [
            ":scatter", "x", "y", "-c", "#44FFAA", "-e", "#2266FF", "-m", "d",
            os.path.join(output_dir, "scatter_plot.png")
        ])

    def test_reduce(self):
        time = numpy.arange(100000)
        signal = numpy.random.normal(0,1,len(time))
        signal *= (1+numpy.cos(0.0001*time))
        signal += numpy.sin(0.00015*time)
        dump_track("time", time)
        dump_track("signal", signal)
        self.execute("tr-reduce", ["time", "signal", "1003"])
        self.execute("tr-plot", [
            ":line", "time", "signal", "-c", "#DDDDDD",
            ":line", "time.red", "signal.red", "signal.red.std", "-c", "#00AA00",
            ":line", "time.red", "signal.red.min", "-c", "#00AA00", "-a", "0.5", "-w", "0.5", "-d", "--",
            ":line", "time.red", "signal.red.max", "-c", "#00AA00", "-a", "0.5", "-w", "0.5", "-d", "--",
            os.path.join(output_dir, "reduce.png")
        ])

    def test_msd(self):
        self.from_xyz("water32", "pos")
        self.from_cp2k_ener("water32")
        self.execute("tr-msd", glob.glob("tracks/atom.pos.???????.?") + [
            "tracks/atom.pos.msd", "--delta-origin=2"
        ])
        self.execute("tr-plot", [
            "--xunit=ps", "--yunit=A**2", "--xlabel=Time", "--ylabel='Mean square displacement'",
            ":line", "tracks/time", "tracks/atom.pos.msd",
            os.path.join(output_dir, "diff_msd.png")
        ])
        lines = self.execute("tr-msd-fit", ["tracks/atom.pos.msd", "tracks/time", "--slice=10:100:", "--unit=cm**2/s"])
        self.assertAlmostEqual(float(lines[0].split()[-1]), 2.2861e-05)

    def test_qh_entropy(self):
        self.from_xyz("ar108", "pos")
        self.execute("tr-qh-entropy", [os.path.join(input_dir, "thf01", "init.xyz"), "300*K", "--unit=J/K/mol"])

    def test_spectrum(self):
        self.from_cp2k_ener("water32")
        self.from_xyz("water32", "vel")
        self.execute("tr-spectrum", glob.glob("tracks/atom.vel.???????.?") + ["tracks/time", "--blocks=3", "tracks/spectrum"])
        self.execute("tr-plot", ["--xunit=1/cm", "--xlabel=Wavenumber", "--ylabel=Amplitude",
            ":line", "tracks/spectrum.wavenumbers", "tracks/spectrum.amplitudes",
            os.path.join(output_dir, "spectrum.png"),
        ])

    def test_slice(self):
        self.from_cp2k_ener("water32")
        os.mkdir("sliced")
        self.execute("tr-slice", glob.glob("tracks/*") + ["10::10", "sliced"])
        for filename in glob.glob("tracks/*"):
            self.assertArraysEqual(
                load_track(filename, slice(10,None,10)),
                load_track(filename.replace("tracks", "sliced"))
            )
        os.mkdir("sliced_bis")
        self.execute("tr-slice", ["tracks/time", "10::10", "sliced_bis/time"])
        self.assertArraysEqual(
            load_track("tracks/time", slice(10,None,10)),
            load_track("sliced_bis/time")
        )

    def test_ic_puckering1(self):
        self.from_cp2k_ener("thf01")
        self.from_xyz("thf01", "pos")
        self.from_xyz("thf01", "vel")
        self.execute("tr-ic-puckering", ["5",
            "tracks/atom.pos.0000000",
            "tracks/atom.pos.0000001", "tracks/atom.pos.0000004",
            "tracks/atom.pos.0000003", "tracks/atom.pos.0000002",
            "tracks/atom.vel.0000000",
            "tracks/atom.vel.0000001", "tracks/atom.vel.0000004",
            "tracks/atom.vel.0000003", "tracks/atom.vel.0000002",
            "tracks/puck.pos", "tracks/puck.vel", "--project"
        ])
        self.execute("tr-plot", ["--xunit=ps", "--xlabel=Time", "--yunit=A", "--ylabel=Puckering amplitude", "--no-legend",
            ":line", "tracks/time", "tracks/puck.pos.amplitude.0000002",
            os.path.join(output_dir, "ic_puckering1_thf_pos_amp.png"),
        ])
        self.execute("tr-plot", ["--xunit=ps", "--xlabel=Time", "--yunit=deg", "--ylabel=Puckering phase", "--no-legend",
            ":line", "tracks/time", "tracks/puck.pos.phase.0000002",
            os.path.join(output_dir, "ic_puckering1_thf_pos_phase.png"),
        ])
        self.execute("tr-plot", ["--xunit=ps", "--xlabel=Time", "--yunit=A/fs", "--ylabel=Puckering amplitude (dt)", "--no-legend",
            ":line", "tracks/time", "tracks/puck.vel.amplitude.0000002",
            os.path.join(output_dir, "ic_puckering1_thf_vel_amp.png"),
        ])
        self.execute("tr-plot", ["--xunit=ps", "--xlabel=Time", "--yunit=deg/fs", "--ylabel=Puckering phase (dt)", "--no-legend",
            ":line", "tracks/time", "tracks/puck.vel.phase.0000002",
            os.path.join(output_dir, "ic_puckering1_vel_pos_phase.png"),
        ])
        self.execute("tr-plot", ["--xunit=A", "--xlabel=puck_x", "--yunit=A", "--ylabel=puck_y", "--no-legend",
            ":line", "tracks/puck.pos.x.0000002", "tracks/puck.pos.y.0000002",
            os.path.join(output_dir, "ic_puckering1_thf_xy.png"),
        ])
        # Test the derivatives
        self.check_deriv("tracks/puck.pos.x.0000002", "tracks/puck.vel.x.0000002", "tracks/time", 1)
        self.check_deriv("tracks/puck.pos.y.0000002", "tracks/puck.vel.y.0000002", "tracks/time", 1)
        self.check_deriv("tracks/puck.pos.amplitude.0000002", "tracks/puck.vel.amplitude.0000002", "tracks/time", 1)
        self.check_deriv("tracks/puck.pos.phase.0000002", "tracks/puck.vel.phase.0000002", "tracks/time", 1)
        # Test the project stuff
        for label in ["puck.vel.x.0000002", "puck.vel.y.0000002", "puck.vel.amplitude.0000002", "puck.vel.phase.0000002"]:
            proj_norm_sq = 0.0
            orig_norm_sq = 0.0
            for c in 'xyz':
                for i in 0,1,2,3,4:
                    proj = load_track("tracks/atom.vel.%07i.%s.proj.%s" % (i, c, label))
                    orig = load_track("tracks/atom.vel.%07i.%s" % (i, c))
                    proj_norm_sq += abs(proj)**2
                    orig_norm_sq += abs(orig)**2
            self.assert_((proj_norm_sq <= orig_norm_sq).all())

    def test_ic_puckering2(self):
        self.from_xyz("org01", "pos")
        self.execute("tr-ic-puckering", ["6",
            "tracks/atom.pos.0000000", "tracks/atom.pos.0000016",
            "tracks/atom.pos.0000003", "tracks/atom.pos.0000002",
            "tracks/atom.pos.0000017", "tracks/atom.pos.0000001", "tracks/puck"
        ])
        self.execute("tr-plot", ["--xunit=1", "--xlabel=Step", "--yunit=A", "--ylabel=Puckering amplitude", "--no-legend",
            ":line", "tracks/puck.amplitude.0000002",
            ":line", "tracks/puck.amplitude.0000003",
            os.path.join(output_dir, "ic_puckering2_thf_amp.png"),
        ])
        self.execute("tr-plot", ["--xunit=1", "--xlabel=Step", "--yunit=deg", "--ylabel=Puckering phase", "--no-legend",
            ":line", "tracks/puck.phase.0000002",
            os.path.join(output_dir, "ic_puckering2_thf_phase.png"),
        ])
        self.execute("tr-plot", ["--xunit=A", "--xlabel=puck_x", "--yunit=A", "--ylabel=puck_y", "--no-legend",
            ":line", "tracks/puck.x.0000002", "tracks/puck.y.0000002",
            os.path.join(output_dir, "ic_puckering2_thf_xy.png"),
        ])

    def test_ic_puckering3(self):
        # a few artificial tricks to test the derivatives and projections
        # generated with tr-ic-puckering, using finite differences.
        os.system("tail -n 15 %s > single-pos.xyz" % os.path.join(input_dir, "thf01", "md-pos-1.xyz"))
        os.system("tail -n 15 %s > single-vel.xyz" % os.path.join(input_dir, "thf01", "md-vel-1.xyz"))
        single_pos = XYZFile("single-pos.xyz").get_molecule()
        single_vel = XYZFile("single-pos.xyz", file_unit=1).get_molecule()
        os.mkdir("tracks")

        epsilon = 1e-7
        counter = 0
        counter_max = len(single_pos.numbers)*3
        for i in xrange(len(single_pos.numbers)):
            for j, c in enumerate('xyz'):
                tmp = numpy.zeros(counter_max+1, float)
                tmp[:] = single_pos.coordinates[i,j]
                tmp[counter+1] += epsilon
                dump_track("tracks/atom.pos.%07i.%s" % (i, c), tmp)
                tmp[:] = single_vel.coordinates[i,j]
                dump_track("tracks/atom.vel.%07i.%s" % (i, c), tmp)
                counter += 1

        # run the command
        self.execute("tr-ic-puckering", ["5",
            "tracks/atom.pos.0000000",
            "tracks/atom.pos.0000001", "tracks/atom.pos.0000004",
            "tracks/atom.pos.0000003", "tracks/atom.pos.0000002",
            "tracks/atom.vel.0000000",
            "tracks/atom.vel.0000001", "tracks/atom.vel.0000004",
            "tracks/atom.vel.0000003", "tracks/atom.vel.0000002",
            "tracks/puck.pos", "tracks/puck.vel", "--project"
        ])

        # do the tests
        for label in ["x.0000002", "y.0000002", "amplitude.0000002", "phase.0000002"]:
            # load the values
            values = load_track("tracks/puck.pos.%s" % label)
            # construct the numerical gradient
            grad = numpy.array([(values[i+1]-values[0])/epsilon for i in xrange(counter_max)])
            # normalize the gradient
            egrad = grad/numpy.linalg.norm(grad)
            # test that the sum of the gradient components is zero
            self.assertAlmostEqual(egrad[0::3].sum(), 0.0)
            self.assertAlmostEqual(egrad[1::3].sum(), 0.0)
            self.assertAlmostEqual(egrad[2::3].sum(), 0.0)
            # compute the time derivative
            cart_vel = single_vel.coordinates.ravel()
            q_vel = numpy.dot(cart_vel, grad)
            # test the time derivative
            self.assertAlmostEqual(q_vel, load_track("tracks/puck.vel.%s" % label)[0])
            # compute the projected velocity
            cart_proj = (numpy.dot(cart_vel, egrad)*egrad)[0:3*5]
            # load the projected velocity
            cart_proj_file = numpy.array([load_track(filename)[0] for filename in sorted(glob.glob("tracks/atom.vel.???????.?.proj.puck.vel.%s" % label))])
            # test that the components sum to zero
            self.assertAlmostEqual(cart_proj_file[0::3].sum(), 0.0)
            self.assertAlmostEqual(cart_proj_file[1::3].sum(), 0.0)
            self.assertAlmostEqual(cart_proj_file[2::3].sum(), 0.0)
            # compare both projections
            self.assertArraysAlmostEqual(cart_proj, cart_proj_file, 1e-5, do_abs=True)

    def test_fit_geom1(self):
        # TODO: this is a blind test
        self.from_xyz("org01", "pos")
        self.execute("tr-fit-geom", ["-w", "-g", "-t",
            "tracks/atom.pos",
            os.path.join(input_dir, "org01", "init.xyz"),
            "tracks/fit",
        ])
        self.assert_(os.path.isfile("tracks/fit.rmsd"))
        self.assert_(os.path.isfile("tracks/fit.pos.0000000.x"))
        self.assert_(os.path.isfile("tracks/fit.pos.0000033.z"))
        self.assert_(os.path.isfile("tracks/fit.rot.a.x"))
        self.assert_(os.path.isfile("tracks/fit.rot.c.z"))
        self.assert_(os.path.isfile("tracks/fit.trans.x"))
        self.assert_(os.path.isfile("tracks/fit.trans.z"))


    def test_fit_geom2(self):
        # TODO: this is a blind test
        self.from_xyz("solvated", "pos")
        self.execute("tr-fit-geom", ["-w", "-g", "-t",
            "-a", "144,145,146,147,148,149,150,151,152",
            "tracks/atom.pos",
            os.path.join(input_dir, "solvated", "init.xyz"),
            "tracks/fit",
        ])
        self.assert_(os.path.isfile("tracks/fit.rmsd"))
        self.assert_(not os.path.isfile("tracks/fit.pos.0000000.x"))
        self.assert_(not os.path.isfile("tracks/fit.pos.0000139.z"))
        self.assert_(os.path.isfile("tracks/fit.pos.0000144.x"))
        self.assert_(os.path.isfile("tracks/fit.pos.0000152.z"))
        self.assert_(os.path.isfile("tracks/fit.rot.a.x"))
        self.assert_(os.path.isfile("tracks/fit.rot.c.z"))
        self.assert_(os.path.isfile("tracks/fit.trans.x"))
        self.assert_(os.path.isfile("tracks/fit.trans.z"))


