# coding:utf8
__author__ = 'loong'
import sys
import os


output_dir = 'bin'


def freeze():
    from cx_Freeze import Executable, Freezer
    import shutil
    from distutils.dist import DistributionMetadata

    base = "Console"

    if sys.platform == "win32":
        base = "Win32GUI"

    dep_modules = ["atexit"]

    executables = [Executable('qqzhaocha.py')]

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    class MetaData(DistributionMetadata):
        def __init__(self):
            DistributionMetadata.__init__(self)
            self.name = 'diskbook-client'
            self.description = 'dishbook client'
            self.version = "0.0.0.0"

    freezer = Freezer(executables,
                      includeFiles=[],
                      includeMSVCR=True,
                      packages=dep_modules,
                      #includes=dep_modules,
                      excludes=[],
                      replacePaths=[],
                      copyDependentFiles=True,
                      base=base,
                      createLibraryZip=True,
                      appendScriptToExe=False,
                      targetDir=output_dir,
                      zipIncludes=[],
                      #icon=icon
                      metadata=MetaData())
    freezer.Freeze()


freeze()
