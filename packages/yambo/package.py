# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import os
from pathlib import Path

from spack import *


class Yambo(AutotoolsPackage):
    """YAMBO is an open-source code released within the GPL licence.

    YAMBO implements Many-Body Perturbation Theory (MBPT) methods
    (such as GW and BSE) and Time-Dependent Density Functional Theory
    (TDDFT), which allows for accurate prediction of fundamental
    properties as band gaps of semiconductors, band alignments, defect
    quasi-particle energies, optics and out-of-equilibrium properties
    of materials.

    The code resorts to previously computed electronic structure,
    usually at the Density Functional Theory (DFT) level and for this
    reason it is interfaced with two of the most used planewave DFT
    codes used in scientific community, Quantum ESPRESSO and Abinit.
    """

    homepage = "http://www.yambo-code.eu"
    url = "https://github.com/yambo-code/yambo/archive/5.2.0.tar.gz"
    git = "https://github.com/yambo-code/yambo.git"

    maintainers = ['nicspalla']

    version('develop', branch='develop', git="https://github.com/yambo-code/yambo-devel")
    version('develop-bugfixes', branch='bug-fixes', git="https://github.com/yambo-code/yambo-devel")
    version('5.2.0', sha256='eb41e83df716eb87261cf130ffe7f930e7dc2e123343d47b73d5a3c69fea7316')
    version('5.1.2', sha256='9625d8a96bd9a3ff3713ebe53228d5ac9be0a98adecbe2a2bad67234c0e26a2e')
    version('5.1.1', sha256='c85036ca60507e627c47b6c6aee8241830349e88110e1ce9132ef03ab2c4e9f6')
    version('5.0.4', sha256='1841ded51cc31a4293fa79252d7ce893d998acea7ccc836e321c3edba19eae8a')
    version('5.0.3', sha256='7a5a5f3939bdb6438a3f41a3d26fff0ea6f77339e4daf6a5d850cf2a51da4414')
    version('5.0.2', sha256='a2cc0f880dd915b47efa0d5dd88cb94edffbebaff37a252183efb9e23dbd3fab')
    version('5.0.1', sha256='bbdbd08f7219d575a0f479ff05dac1f1a7b25f7e20f2165abf1b2cf28aedae92')
    version('5.0.0', sha256='b1cbc0b3805538f892b2b8691901c4cc794e75e056a4bd9ad9cf585899cf0aa9')
    version('4.5.3', sha256='04f89b5445d35443325c071784376c7b5c25cc900d1fdcc92971a441f8c05985')
    version('4.5.2', sha256='0b4f8b82c1d37fce472228bdffb6f6f44b86104d170677a5d55e77a2db832cf0')
    version('4.5.1', sha256='6ef202535e38f334a69bd75bd24ff8403b0a4c6b8c60a28b69d4b1c5808aeff5')
    version('4.5.0', sha256='c68b2c79acc31b3d48e7edb46e4049c1108d60feee80bf4fcdc4afe4b12b6928')
    version('4.4.1', sha256='2daf80f394a861301a9bbad559aaf58de283ce60395c9875e9f7d7fa57fcf16d')
    version('4.3.3', sha256='790fa1147044c7f33f0e8d336ccb48089b48d5b894c956779f543e0c7e77de19')

    patch('hdf5.patch', sha256='b9362020b0a29abec535afd7d782b8bb643678fe9215815ca8dc9e4941cb169f', when='@4.3:5.0.99')
    patch('s_psi.patch', sha256='981a0783a9a2c21a89faa358eaf277213837ed712c936152842f8cf7620f52cd', when='%gcc@12.0.0:')

    # MPI + OpenMP parallelism
    variant('mpi', default=True, description='Enable MPI support')
    variant('openmp', default=False, description='Enable OpenMP support')
    depends_on('mpi', when='+mpi')

    conflicts('+scalapack', when='~mpi',
              msg="Parallel linear algebra available only with +mpi")
    depends_on('blas')
    depends_on('lapack')
    variant('scalapack', default=False, description='Activate support for parallel linear algebra with SCALAPACK')
    depends_on('scalapack', when='+scalapack')
    variant('slepc', default=False, description='Activate support for linear algebra with SLEPc and PETSc')
    depends_on('petsc~cuda+mpi+double+complex~superlu-dist~hypre~metis', when='+slepc+mpi+dp')
    depends_on('petsc~cuda~mpi~double+complex~superlu-dist~hypre~metis', when='+slepc~mpi~dp')
    depends_on('petsc~cuda~mpi+double+complex~superlu-dist~hypre~metis', when='+slepc~mpi+dp')
    depends_on('petsc~cuda+mpi~double+complex~superlu-dist~hypre~metis', when='+slepc+mpi~dp')
    depends_on('slepc~cuda~arpack', when='+slepc')
    depends_on('slepc~cuda~arpack@:3.7.4', when='@:4.5.3 +slepc')

    # GPU acceleration
    variant('cuda-fortran', default=False, description='Build with CUDA-Fortran')
    variant('cuda_arch', default='none', values=['none', '86', '50', '72', '90', 
                    '53', '21', '11', '62', '13', '52', '35', '12', '75', '89', 
                    '70', '32', '10', '30', '87', '60', '37', '61', '80', '20'], 
            multi=False, when='+cuda-fortran', description='CUDA architecture')
    with when('+cuda-fortran'):
        conflicts('cuda_arch=none',
                  msg="CUDA architecture is required when +cuda-fortran")
        conflicts('@:4.5.3',
                  msg="CUDA-Fortran available only from version 5.0.0")
        conflicts('%gcc',
                  msg="CUDA-Fortran available only with NV or PGI compilers")
        conflicts('%intel',
                  msg="CUDA-Fortran available only with NV or PGI compilers")
        conflicts('%oneapi',
                  msg="CUDA-Fortran available only with NV or PGI compilers")
    # variant('nvtx', default=False, description='Enable NVTX support', when='+cuda-fortran %nvhpc')
    variant('magma', default=False, description='Enable Magma support', when='+cuda-fortran %nvhpc')
    depends_on('magma+cuda', when='+magma')
    
    # Other variants
    variant('dp', default=False, description='Enable double precision')
    variant('time', default=False, description='Activate time profiling of specific sections')
    variant('memory', default=False, description='Activate memory profiling of specific sections')
    variant('ph', default=False, description='Compile Electron-phonon coupling project executables: yambo_ph ypp_ph')
    variant('rt', default=False, description='Compile Real-time dynamics project executables: yambo_rt ypp_rt')
    variant('sc', default=False, description='Compile Self-consistent (COHSEX, HF, DFT) project executables: yambo_sc ypp_sc')
    variant('nl', default=False, description='Compile Non-linear optics project executables: yambo_nl ypp_nl')

    # Yambopy
    # variant('yambopy', default=False, description='Install Yambopy package')
    # depends_on('py-yambopy', when='+yambopy')

    # FFTW
    depends_on('fftw-api@3~mpi', when='~mpi')
    depends_on('fftw-api@3+mpi', when='+mpi')

    # HDF5
    variant('parallel_io', default=False, when='@4.4.0: +mpi', description='Activate the HDF5 parallel I/O')
    depends_on('hdf5+fortran+hl~mpi', when='@:4.4.0')
    depends_on('hdf5+fortran+hl~mpi', when='~parallel_io')
    depends_on('hdf5+fortran+hl+mpi', when='+parallel_io')
    depends_on('hdf5+fortran+hl~mpi', when='~mpi')

    # NETCDF
    depends_on('netcdf-c~mpi', when='~parallel_io')
    depends_on('netcdf-c+mpi', when='+parallel_io')
    depends_on('netcdf-c~mpi', when='~mpi')
    depends_on('netcdf-fortran')

    # LIBXC
    depends_on('libxc@2.0.3:3.0.0~cuda', when='@:5.0.99')
    depends_on('libxc@5.0:~cuda', when='@5.1.0:')

    # IOTK
    resource(
       name='iotk',
       url='https://github.com/yambo-code/yambo-libraries/raw/master/external/iotk-y1.2.2.tar.gz',
       sha256='64af6a4b98f3b62fcec603e4e1b00ef994f95a0efa53ab6593ebcfe6de1739ef',
       destination='lib/iotk'
    )

    # Yambo driver
    resource(
       name='Ydriver',
       url='https://github.com/yambo-code/yambo-libraries/raw/master/external/Ydriver-0.0.2.tar.gz',
       sha256='63984c3eb2d28320b320f1d9b3a2c1efcd3c9505a10d887c8bbd54513442202c',
       destination='',
       placement={'driver': 'lib/yambo/driver'},
       when='@5.0.0:5.0.99'
    )
    resource(
       name='Ydriver',
       url='https://github.com/yambo-code/yambo-libraries/raw/master/external/Ydriver-1.1.0.tar.gz',
       sha256='6c316d613f5a41ddd15efad7ba97e4712f87d7e56c073ba5458caf424afcb97a',
       destination='',
       placement={'driver': 'lib/yambo/driver'},
       when='@5.1.0:5.1.99'
    )
    resource(
       name='Ydriver',
       url='https://github.com/yambo-code/Ydriver/archive/refs/tags/1.2.0.tar.gz',
       sha256='0f29a44e9c4b49d3f6be3f159a7ef415932b2ae2f2fdba163af60a0673befe6e',
       destination='lib/yambo/Ydriver',
       placement={'config': 'config',
                  'configure': 'configure',
                  'example': 'example',
                  'include': 'include',
                  'lib': 'lib',
                  'bin': 'bin',
                  'Makefile': 'Makefile',
                  'src': 'src',
              },
       when='@5.2.0:'
    )

    # Sanity check
    sanity_check_is_file = ["bin/yambo", "bin/ypp", "bin/a2y", "bin/c2y", "bin/p2y"]

    @property
    def build_targets(self):
        spec = self.spec
        if '+ph' in spec and '+rt' in spec and '+sc' in spec and '+nl' in spec:
            return ['all']
        bt = ['core']
        if '+ph' in spec:
            bt.append('ph-project')
        if '+rt' in spec:
            bt.append('rt-project')
        if '+sc' in spec:
            bt.append('sc-project')
        if '+nl' in spec:
            bt.append('nl-project')
        return bt

    @run_before('configure')
    def filter_iotk(self):
        # block iotk download
        filter_file('; \$\(getsrc\)', ' ', 'lib/archive/Makefile.loc')
        # filter_file('783147', '962173', 'lib/archive/Makefile.loc', when='@:4.5.0')
        with when('@:5.0.99'):
            filter_file('\( cd \.\./archive ;', r'#( cd ../archive ;', 'lib/iotk/Makefile.loc')
            filter_file('; \$\(make\) \$\(TARBALL\) ; fi \)', r'; #$(make) $(TARBALL) ; fi )', 'lib/iotk/Makefile.loc')
            filter_file('gunzip', r'#gunzip', 'lib/iotk/Makefile.loc')
        with when('@5.1.1:'):
            # set link for iotk lib dir and block tarball uncompress
            filter_file('! test -d iotk;', ' test -d iotk;', 'lib/iotk/Makefile.loc')
            filter_file('@\$\(uncompress\)', 'touch uncompress.stamp', 'lib/iotk/Makefile.loc')

    @run_before('configure')
    def filter_ydriver(self):
        spec = self.spec
        if '@5.1.0:5.1.99' in spec or '@develop-pcm' in spec:
            # solve issue for parallel compilation
            filter_file('\$\(MAKE\) \$\(MAKEFLAGS\) -f Makefile.loc', 
                        r'$(MAKE) -f Makefile.loc $(MAKEFLAGS)', 
                        'config/mk/global/functions/get_libraries.mk')
            # block Ydriver download
            filter_file('; \$\(getsrc_git\); \$\(call link_it,"yambo"\)', ' ', 'lib/archive/Makefile.loc')
        if '@5.2.0:' in spec:
            # block Ydriver download
            filter_file('; \$\(call getsrc_git,"Ydriver"\); \$\(call copy_driver,"Ydriver"\)', ' ', 'lib/archive/Makefile.loc')

    @run_before('configure')
    def filter_configure(self):
        spec = self.spec
        # The configure in the package has the string 'cat config/report'
        # hard-coded, which causes a failure at configure time due to the
        # current working directory in Spack. Fix this by using the absolute
        # path to the file.
        report_abspath = join_path(self.build_directory, 'config', 'report')
        filter_file('cat config/report', 'cat '+report_abspath, 'configure')
        # fix petsc bad recognition
        filter_file('#include <petsc/finclude/petscvec.h90>', '#include <petsc/finclude/petscvec.h>', 'configure')
        # fix hdf5 bad linking and include flags
        filter_file('.+try_HDF5_LIBS=..h5pfc -show .+', '#', 'configure')
        filter_file('.+try_hdf5_incdir=..h5pfc -show .+', '#', 'configure')
        filter_file('.+try_HDF5_LIBS=..h5fc -show .+', '#', 'configure')
        filter_file('.+try_hdf5_incdir=..h5fc -show .+', '#', 'configure')
        if '@5.1.2:' in spec:
            # fix petsc linking issue
            filter_file('libs="-lint_modules \$libs \$llocal \$lPLA \$lIO \$lextlibs -lm"', 
                        r'libs="-lint_modules $libs $llocal $lSL $lPLA $lIO $lextlibs -lm"', 
                        'sbin/compilation/libraries.sh')
            filter_file('libs="\$libs \$llocal \$lPLA \$lIO \$lextlibs -lm"', 
                        r'libs="$libs $llocal $lSL $lPLA $lIO $lextlibs -lm"', 
                        'sbin/compilation/libraries.sh')

    def enable_or_disable_time(self, activated):
        return '--enable-time-profile' if activated else '--disable-time-profile'

    def enable_or_disable_memory(self, activated):
        return '--enable-memory-profile' if activated else '--disable-memory-profile'

    def enable_or_disable_openmp(self, activated):
        return '--enable-open-mp' if activated else '--disable-open-mp'

    def enable_or_disable_parallel_io(self, activated):
        return '--enable-hdf5-par-io' if activated else '--disable-hdf5-par-io'

    def setup_build_environment(self, env):
        spec = self.spec
        if spec['mpi'].name == 'openmpi':
            # env.set('MPICC', spec['mpi'].mpicc)
            # env.set('MPICXX', spec['mpi'].mpicxx)
            # env.set('MPIF77', spec['mpi'].mpif77)
            # env.set('MPIFC', spec['mpi'].mpifc)
            env.set('MPICC', 'mpicc')
            env.set('MPICXX', 'mpicxx')
            env.set('MPIF77', 'mpif77')
            env.set('MPIFC', 'mpif90')
        if 'intel' in spec['mpi'].name:
            env.set('MPICC', '{0}/mpiicc'.format(spec['mpi'].prefix.mpi.latest.bin))
            env.set('MPICXX', '{0}/mpiicpc'.format(spec['mpi'].prefix.mpi.latest.bin))
            env.set('MPIF77', '{0}/mpiifort'.format(spec['mpi'].prefix.mpi.latest.bin))
            env.set('MPIFC', '{0}/mpiifort'.format(spec['mpi'].prefix.mpi.latest.bin))
        if '%nvhpc' in spec:
            env.set('FC', "nvfortran")
            env.set('CPP', "cpp -E")
            env.set('FPP', "nvfortran -Mpreprocess -E")
            env.set('F90SUFFIX', ".f90")
            env.unset('CUDA_HOME')
        if '%intel' in spec:
            env.set('FPP', "ifort -E -free -P")
            env.set('FC', "ifort")
            env.set('CC', "icc")
            env.set('CXX', "icpc")
            env.set('CPP', "icc -E -ansi")
        if '%oneapi' in spec:
            env.set('FPP', "ifx -E -free -P")
        if 'mkl' in spec:
            if 'MKLROOT' not in os.environ:
                env.set('MKLROOT', '{}/mkl/latest'.format(spec['blas'].prefix))

    def configure_args(self):
        spec = self.spec

        args = [
            '--enable-msgs-comps',
            '--disable-keep-objects',
            '--with-editor=none'
        ]

        # There are hard-coded paths that make the build process fail if the
        # target prefix is not the configure directory
        args.append('--prefix={0}'.format(self.stage.source_path))
        if '@:4.5.3' in spec:
            if '%gcc@9.0.0:' in spec:
                args.append('FCFLAGS=-fallow-argument-mismatch')

        # Double precision
        args.extend(self.enable_or_disable('dp'))

        # Application profiling
        args.extend(self.enable_or_disable('time'))
        args.extend(self.enable_or_disable('memory'))

        # MPI + threading
        args.extend(self.enable_or_disable('mpi'))
        args.extend(self.enable_or_disable('openmp'))

        # Linear Algebra
        if 'mkl' in spec and ('%intel' in spec or '%oneapi' in spec):
            if '+openmp' in spec:
                args.extend([
                    '--with-blas-libs=-L{0}/lib/intel64 -lmkl_intel_lp64 '
                    '-lmkl_intel_thread -lmkl_core -liomp5'.format(env['MKLROOT']),
                    '--with-lapack-libs=-L{0}/lib/intel64 -lmkl_intel_lp64 '
                    '-lmkl_intel_thread -lmkl_core -liomp5'.format(env['MKLROOT']),
                ])
            else:
                args.extend([
                    '--with-blas-libs=-L{0}/lib/intel64 -lmkl_intel_lp64 '
                    '-lmkl_sequential -lmkl_core'.format(env['MKLROOT']),
                    '--with-lapack-libs=-L{0}/lib/intel64 -lmkl_intel_lp64 '
                    '-lmkl_sequential -lmkl_core'.format(env['MKLROOT']),
                ])
        elif 'mkl' in spec and '%gcc' in spec:
            if '+openmp' in spec:
                args.extend([
                    '--with-blas-libs=-L{0}/lib/intel64 -lmkl_gf_lp64 '
                    '-lmkl_gnu_thread -lmkl_core -lgomp'.format(env['MKLROOT']),
                    '--with-lapack-libs=-L{0}/lib/intel64 -lmkl_gf_lp64 '
                    '-lmkl_gnu_thread -lmkl_core -lgomp'.format(env['MKLROOT']),
                ])
            else:
                args.extend([
                    '--with-blas-libs=-L{0}/lib/intel64 -lmkl_gf_lp64 '
                    '-lmkl_sequential -lmkl_core'.format(env['MKLROOT']),
                    '--with-lapack-libs=-L{0}/lib/intel64 -lmkl_gf_lp64 '
                    '-lmkl_sequential -lmkl_core'.format(env['MKLROOT']),
                ])
        elif 'mkl' in spec and '%nvhpc' in spec:
            if '+openmp' in spec:
                args.extend([
                    '--with-blas-libs=-L{0}/lib/intel64 -lmkl_intel_lp64 '
                    '-lmkl_pgi_thread -lmkl_core -pgf90libs -mp'.format(env['MKLROOT']),
                    '--with-lapack-libs=-L{0}/lib/intel64 -lmkl_intel_lp64 '
                    '-lmkl_pgi_thread -lmkl_core -pgf90libs -mp'.format(env['MKLROOT']),
                ])
            else:
                args.extend([
                    '--with-blas-libs=-L{0}/lib/intel64 -lmkl_intel_lp64 '
                    '-lmkl_sequential -lmkl_core'.format(env['MKLROOT']),
                    '--with-lapack-libs=-L{0}/lib/intel64 -lmkl_intel_lp64 '
                    '-lmkl_sequential -lmkl_core'.format(env['MKLROOT']),
                ])
        else:
            args.extend([
                '--with-blas-libs={0}'.format(spec['blas'].libs),
                '--with-lapack-libs={0}'.format(spec['lapack'].libs),
                # '--with-blas-libs="{0} {1}"'.format(spec['blas'].libs.search_flags, spec['blas'].libs.link_flags),
                # '--with-lapack-libs="{0} {1}"'.format(spec['lapack'].libs.search_flags, spec['lapack'].libs.link_flags),
            ])
        if '+scalapack' in spec:
            args.append('--enable-par-linalg')
            if 'mkl' in spec and 'intel' in spec['mpi'].name:
                args.extend([
                    '--with-blacs-libs=-L{0}/lib/intel64 '
                    '-lmkl_blacs_intelmpi_lp64'.format(env['MKLROOT']),
                    '--with-scalapack-libs=-L{0}/lib/intel64 '
                    '-lmkl_scalapack_lp64'.format(env['MKLROOT']),
                ])
            else:
                args.extend([
                    '--with-blacs-libs={0}'.format(spec['scalapack'].libs),
                    '--with-scalapack-libs={0}'.format(spec['scalapack'].libs),
                ])
        if '+slepc' in spec:
            args.extend([
                '--enable-slepc-linalg',
                '--with-petsc-path={0}'.format(spec['petsc'].prefix),
                '--with-slepc-path={0}'.format(spec['slepc'].prefix),
            ])

        # I/O
        args.extend([
            '--with-netcdf-path={0}'.format(spec['netcdf-c'].prefix),
            '--with-netcdff-path={0}'.format(spec['netcdf-fortran'].prefix),
            '--with-hdf5-path={0}'.format(spec['hdf5'].prefix)
        ])

        # Parallel I/O
        if '@4.4.0:' in spec:
            args.extend(self.enable_or_disable('parallel_io'))

        # FFT
        if 'mkl' in spec and ('%intel' in spec or '%oneapi' in spec):
            if '+openmp' in spec:
                args.append('--with-fft-libs=-qmkl=parallel')
            else:
                args.append('--with-fft-libs=-qmkl=sequential')
        else:
            args.append('--with-fft-path={0}'.format(spec['fftw-api'].prefix))

        # Other dependencies
        args.append('--with-libxc-path={0}'.format(spec['libxc'].prefix))

        # CUDA
        if '+cuda-fortran' in spec:
            # enable_cuda = '--enable-cuda=cuda{0}.{1}'.format(*spec['cuda'].version)
            enable_cuda = '--enable-cuda=cuda{0}.{1}'.format(11, 0)
            enable_cuda += ',cc{0}'.format(spec.variants['cuda_arch'].value)
            args.append(enable_cuda)
            # if '+nvtx' in spec:
            #     p = Path(spec['%nvhpc'].prefix)
            #     nvptx_path = list(p.glob('Linux*/202*/cuda/11.0'))[0]
            #     if (nvptx_path.is_dir()):
            #         args.append('--enable-nvtx={0}'.format(nvptx_path))
            if '+magma' in spec:
                args.append('--enable-magma-linalg')
                args.append('--with-magma-path={0}'.format(spec['magma'].prefix))

        return args

    def install(self, spec, prefix):
        # 'install' target is not present
        install_tree('bin', prefix.bin)
