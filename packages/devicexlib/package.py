# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import spack.build_systems.autotools
from spack.package import *


class Devicexlib(AutotoolsPackage,CudaPackage,ROCmPackage):
    """deviceXlib is a library that wraps device-oriented routines and utilities, 
    such as device data allocation, host-device data transfers. deviceXlib supports CUDA language, 
    together with OpenACC and OpenMP programming paradigms. deviceXlib wraps a subset of functions 
    from Nvidia cuBLAS, Intel oneMKL BLAS and AMD rocBLAS libraries.
    """

    homepage = "https://gitlab.com/max-centre/components/devicexlib"
    url = "https://gitlab.com/max-centre/components/devicexlib/-/archive/0.8.3/devicexlib-0.8.3.tar.gz"
    git = "https://gitlab.com/max-centre/components/devicexlib"

    maintainers = ['nicspalla']

    version('develop', branch='develop')
    version("0.8.3", sha256="3d2d4264df8c57da2791b0f94def52d789d67c6fe7ad5960f96c96dfc6c25cb2")
    version("0.8.2", sha256="c184de73f424e9437e352eb0e35716514348a7cd88ebac3ad7a52c66c4e4ba9c")

    variant('openmp', default=False, description='Enable OpenMP support')
    variant('openmp5', default=False, description='Build with OpenMP-GPU support')
    variant('openacc', default=False, description='Build with OpenACC')
    variant('cuda-fortran', default=False, description='Build with CUDA-Fortran')

    # with when('+cuda-fortran'):
        # requires('%nvhpc', msg="CUDA-Fortran available only with Nvidia compilers")
    # with when('+openacc'):
        # requires('%nvhpc', '%gcc@10:+nvptx', policy="one_of",
        #          msg="OpenACC available only with Nvidia or GCC compilers")
    # with when('+openmp5'):
        # requires('%oneapi', '%cce', '%gcc@10:+nvptx',  policy="one_of",
        #          msg="OpenMP offloading available only with GCC or oneAPI or Cray compilers")

    variant('nvtx', default=False, description='Enable NVTX support', when='+cuda')
    variant('roctx', default=False, description='Enable ROCTX support', when='+rocm')
    variant('mkl', default=False, description='Enable MKL-GPU support')

    depends_on("blas")
    # depends_on("lapack")
    depends_on('cuda', when='+nvtx')
    depends_on('intel-oneapi-mkl', when='+mkl')
    conflicts('cuda_arch=none', when='+cuda', msg='CUDA architecture is required')
    conflicts('cuda_arch=none', when='+cuda-fortran', msg='CUDA architecture is required')

    with when("+openmp"):
         depends_on("openblas threads=openmp", when="^openblas")

    def enable_or_disable_openmp(self, activated):
        return '--enable-openmp' if activated else '--disable-openmp'

    def enable_or_disable_cuda(self, activated):
        return '--enable-cublas=yes' if activated else '--enable-cublas=no'

    def enable_or_disable_rocm(self, activated):
        return '--enable-rocblas=yes' if activated else '--enable-rocblas=no'

    def enable_or_disable_mkl(self, activated):
        return '--enable-mkl-gpu=yes' if activated else '--enable-mkl-gpu=no'

    def setup_build_environment(self, env):
        spec = self.spec
        if '%nvhpc' in spec:
            env.set('CC', "nvc")
            env.set('FC', "nvfortran")
            env.set('F90', "nvfortran")
            env.set('CPP', "cpp -E")
            env.set('FPP', "nvfortran -Mpreprocess -E")
            env.set('F90SUFFIX', ".f90")
    
    def configure_args(self):
        spec = self.spec
        args = ['--disable-parallel --enable-cuda-env-check=no']

        # OpenMP
        args.extend(self.enable_or_disable('openmp'))

        # GPU offloading
        if '+cuda-fortran' in spec:
            args.append('--enable-cuda-fortran')
        if '+openacc' in spec:
            args.append('--enable-openacc')
        if '+openmp5' in spec:
            args.append('--enable-openmp5')

        # BLAS
        args.append('--with-blas-libs={0}'.format(spec['blas'].libs))

        # CUDA
        args.extend(self.enable_or_disable('cuda'))
        if '+cuda' in spec:
            args.append('--with-cuda-cc={0}'.format(*spec.variants['cuda_arch'].value))
            args.append('--with-cuda-runtime={0}.{1}'.format(*spec['cuda'].version))
            args.append('--with-cuda-path={0}'.format(spec['cuda'].home))
            
        # ROCm
        args.extend(self.enable_or_disable('rocm'))
        if '+rocm' in spec:
            args.append('--with-rocm-path={0}'.format(spec['hip'].home))

        # MKL
        args.extend(self.enable_or_disable('mkl'))

        return args

    @property
    def build_targets(self):
        return ['all']
