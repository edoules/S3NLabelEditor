from distutils.core import setup, Extension
from Cython.Distutils import build_ext

setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=[
        Extension(
            "cyptnn",
            [
                "ptnn_weightLayer.c",
                "ptnn_nodeLayer.c",
                "ptnn_newNode1.c",
                "ptnn_train.c",
                "ptnn_algorithms.c",
                "ptnn_utility.c",
                "ptnn_io.c",
                "cyptnn.pyx",
            ],            
            extra_compile_args=[
                '-g0', '-O3',
            ]
        ),
    ],
)
