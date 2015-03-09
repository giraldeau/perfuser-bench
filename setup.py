from setuptools import setup, Extension
import glob
import sys

v = sys.version_info
if v.major < 3:
    sys.stderr.write('Python 3 is required\n')
    sys.exit(1)

ext = [
    Extension(
            'perfuserBench.ext',
            sources = glob.glob('ext/*.c'),
            include_dirs=['ext/'],
            libraries=['dl'],
            #extra_compile_args = ['-O0', '-g'], # FIXME: add --enable-debug option
            extra_compile_args = ['-O2'],
    ),
]

entry_points = {
    'console_scripts': [
        'perfuserBench = perfuserBench.cli:main'
    ],
}
 
setup (name = 'perfuserBench',
        version = '1.0',
        description = 'python-profile-ust benchmarks',
        ext_modules = ext,
        packages = ['perfuserBench'],
        entry_points = entry_points,
)

