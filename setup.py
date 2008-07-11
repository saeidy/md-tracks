#!/usr/bin/python
# MD-Tracks is a statistical analysis toolkit for molecular dynamics
# and monte carlo simulations.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of MD-Tracks.
#
# MD-Tracks is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# MD-Tracks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --

if __name__ == "__main__":
    from distutils.core import setup
    from glob import glob

    setup(name='MD-Tracks',
        version='0.003',
        description='MD-Tracks is a statistical analysis toolkit for molecular '
        'dynamics and monte carlo simulations.',
        author='Toon Verstraelen',
        author_email='Toon.Verstraelen@UGent.be',
        url='http://molmod.ugent.be/code/',
        package_dir = {'tracks': 'lib/tracks'},
        packages = ['tracks'],
        scripts=glob("scripts/*"),
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
        ],
    )








