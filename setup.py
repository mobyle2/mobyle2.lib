#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import sys
import os
from distutils.core import setup
from distutils.command.install_egg_info import install_egg_info
from distutils.dist import Distribution as _Distribution
from distutils.command.build import build
from distutils.command.install import install as _install
from distutils.command.install_scripts import install_scripts as _install_scripts
from distutils.command.install_data import install_data as _install_data
from distutils.versionpredicate import VersionPredicate
from distutils import log, dir_util
from distutils.util import get_platform, change_root, convert_path
from distutils.util import subst_vars as distutils_subst_vars

class check_and_build( build ):
    def run(self):
        chk = True
        for req in require_pyt:
            chk &= self.chkpython(req)
        for req in require_mod:
            chk &= self.chkmodule(req)
        if not chk:
            sys.exit(1)
        build.run( self )

    def chkpython(self, req):
        chk = VersionPredicate(req)
        ver = '.'.join([str(v) for v in sys.version_info[:2]])
        if not chk.satisfied_by(ver):
            print >> sys.stderr, "Invalid python version, expected %s" % req
            return False
        return True

    def chkmodule(self, req):
        chk = VersionPredicate(req)
        try:
            mod = __import__(chk.name)
        except:
            print >> sys.stderr, "Missing mandatory %s python module" % chk.name
            return False
        for v in [ '__version__', 'version' ]:
            ver = getattr(mod, v, None)
            break
        try:
            if ver and not chk.satisfied_by(ver):
                print >> sys.stderr, "Invalid module version, expected %s" % req
                return False
        except:
            pass
        return True


class install(_install):

#     #I use record to store all installed files and reuse this record file for uninstall
#     #so this option is not available anymore for the users 
#     for i, opt in enumerate(_install.user_options):
#         if opt[0] == 'record=':
#             _install.user_options.pop(i)

    def initialize_options(self):
        _install.initialize_options(self)
        self.verbosity = None
        self.build_base = 'build'
        self.build_dir = None
        self.build_lib = None
        self.build_purelib = None
        self.build_platlib = None
        self.plat_name = None
        self.skip_build = 0
        self.warn_dir = 1
        
    def finalize_options(self):
        _install.finalize_options(self)
        if self.verbosity is None:
            self.verbosity = 0
        else:
            self.verbosity = int(self.verbosity)

        if self.plat_name is None:
            self.plat_name = get_platform()
        else:
            # plat-name only supported for windows (other platforms are
            # supported via ./configure flags, if at all).  Avoid misleading
            # other platforms.
            if os.name != 'nt':
                raise DistutilsOptionError(
                            "--plat-name only supported on Windows (try "
                            "using './configure --help' on your platform)")

        plat_specifier = ".%s-%s" % (self.plat_name, sys.version[0:3])

        # Make it so Python 2.x and Python 2.x with --with-pydebug don't
        # share the same build directories. Doing so confuses the build
        # process for C modules
        if hasattr(sys, 'gettotalrefcount'):
            plat_specifier += '-pydebug'

        # 'build_purelib' and 'build_platlib' just default to 'lib' and
        # 'lib.<plat>' under the base build directory.  We only use one of
        # them for a given distribution, though --
        if self.build_purelib is None:
            self.build_purelib = os.path.join(self.build_base, 'lib')
        if self.build_platlib is None:
            self.build_platlib = os.path.join(self.build_base,
                                              'lib' + plat_specifier)

        # 'build_lib' is the actual directory that we will use for this
        # particular module distribution -- if user didn't supply it, pick
        # one of 'build_purelib' or 'build_platlib'.
        if self.build_lib is None:
            if os.path.exists(self.build_purelib):
                self.build_lib = self.build_purelib
            elif os.path.exists(self.build_platlib):
                self.build_lib = self.build_platlib
        self.build_dir = self.build_lib
                
    def run(self):
        inst = self.distribution.command_options.get('install')
        vars_2_subst = {'PREFIX': inst.get('prefix', ''),
                        'PREFIXDATA' : os.path.join(get_install_data_dir(inst), 'mobyle'),
                        }
        for _file in self.distribution.fix_lib:
            input_file = os.path.join(self.build_lib, _file)
            output_file = input_file + '.tmp'
            subst_vars(input_file, output_file, vars_2_subst)
            os.unlink(input_file)
            self.move_file(output_file, input_file)
        _install.run(self)

class install_data(_install_data):

    user_options = [
        ('install-dir=', 'd',
         "base directory for installing data files "
         "(default: installation base dir)"),
        ('root=', None,
         "install everything relative to this alternate root directory"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ]

    boolean_options = ['force']

    def finalize_options(self):
        inst = self.distribution.command_options.get('install')
        self.install_dir = get_install_data_dir(inst)
        self.set_undefined_options('install',
                                   ('root', 'root'),
                                   ('force', 'force'),
                                  )
        self.prefix_data = self.install_dir
        self.files_2_install = self.distribution.data_files 


    def run(self):
        self.mkpath(self.install_dir)
        for f in self.files_2_install:
            if isinstance(f, str):
                if not os.path.exists(f):
                    log.warn("WARNING the document {} cannot be found, installation skipped".format(f))
                # it's a simple file, so copy it
                f = convert_path(f)
                if self.warn_dir:
                    self.warn("setup script did not provide a directory for "
                              "'%s' -- installing right in '%s'" %
                              (f, self.install_dir))
                (out, _) = self.copy_file(f, self.install_dir)
                self.outfiles.append(out)
            else:
                # it's a tuple with path to install to and a list of path
                dir = convert_path(f[0])
                if not os.path.isabs(dir):
                    dir = os.path.join(self.install_dir, dir)
                elif self.root:
                    dir = change_root(self.root, dir)
                self.mkpath(dir)
                if f[1] == []:
                    # If there are no files listed, the user must be
                    # trying to create an empty directory, so add the
                    # directory to the list of output files.
                    self.outfiles.append(dir)
                else:
                    # Copy files, adding them to the list of output files.
                    for data in f[1]:
                        data = convert_path(data)#return name that will work on the native filesystem
                        if not os.path.exists(data):
                            log.warn("WARNING the document {} cannot be found, installation skipped".format(data))
                            continue
                        if os.path.isdir(data):
                            out = self.copy_tree(data, dir)
                            self.outfiles.extend(out)
                        else:
                            (out, _) = self.copy_file(data, dir)
                            self.outfiles.append(out)


class install_scripts(_install_scripts):
    
    
    def initialize_options(self):
        _install_scripts.initialize_options(self)
        
    def finalize_options(self):
        _install_scripts.finalize_options(self)

    def run(self):
        inst = self.distribution.command_options.get('install')
        vars_2_subst = {'PREFIX': inst.get('prefix', ''),
                        'PREFIXDATA' : os.path.join(get_install_data_dir(inst), 'mobyle'),
                        }
        for _file in self.distribution.fix_scripts:
            input_file = os.path.join(self.build_dir, _file)
            output_file = input_file + '.tmp'
            subst_vars(input_file, output_file, vars_2_subst)
            os.unlink(input_file)
            self.move_file(output_file, input_file)
        _install_scripts.run(self)



class Distribution(_Distribution):

    def __init__(self, attrs = None):
        #It's important to define options before to call __init__
        #otherwise AttributeError: UsageDistribution instance has no attribute 'conf_files'
        self.fix_lib = None
        self.fix_scripts = None
        _Distribution.__init__(self, attrs = attrs)


def subst_vars(src, dst, vars):
    try:
        src_file = open(src, "r")
    except os.error, err:
        raise DistutilsFileError, "could not open '%s': %s" % (src, err)
    try:
        dest_file = open(dst, "w")
    except os.error, err:
        raise DistutilsFileError, "could not create '%s': %s" % (dst, err)
    with src_file:
        with dest_file:
            for line in src_file:
                new_line = distutils_subst_vars(line, vars)
                dest_file.write(new_line)

def get_install_data_dir(inst):

    if 'VIRTUAL_ENV' in os.environ:
        inst['prefix'] = ('environment', os.environ['VIRTUAL_ENV'])

    if 'install_data' in inst:
        install_dir = inst['install_data'][1]
    elif 'prefix' in inst:
        install_dir = os.path.join(inst['prefix'][1], 'share')
    else:
        install_dir = os.path.join('/', 'usr', 'share')
    return install_dir


require_pyt = [ 'python (>=2.7, <3.0)' ]
require_mod = []

setup(name        = 'mobyle.lib',
      version     =  time.strftime("%Y-%m-%d"),
      author      = "Émeline Legros, Hervé Ménager, Olivier Sallou, Adrien Saladin, Bertrand Néron",
      author_email = "bneron@pasteur.fr",
      license      = "GPLv3" ,
      url = "https://github.com/mobyle2/mobyle2.lib",
      download_url = "https://github.com/mobyle2/mobyle2.lib",
      description  = "common libraries to Mobyle2 project",
      classifiers = [
                     'License :: GPLv3' ,
                     'Operating System :: POSIX' ,
                     'Programming Language :: Python' ,
                     'Topic :: Bioinformatics' ,
                    ] ,
      packages    = ['mobyle' , 'mobyle.common', 'mobyle.common.stats'],
      package_dir = {'' : '.'},
      package_data = {'mobyle.common.stats': ['GeoIP.dat']},
      scripts = ['scripts/db/mob_classification_update', 
                 'scripts/db/mob_data_format_terms_update',
                 'scripts/db/mob_seed',
                 'scripts/db/mob_services_loader',
                 'scripts/imports/mob_edam_import',
                 'scripts/imports/mob_m1_services_import'
                 ],
      #(dataprefix +'where to put the data in the install, [where to find the data in the tar ball]
      data_files = [('mobyle/imports', ['scripts/imports/formats_mapping.txt',
                                     'scripts/imports/operation_mapping.txt',
                                     'scripts/imports/topic_mapping.txt',
                                     'scripts/imports/types_mapping.txt'
                                     ]) ],
      #scripts files where some variables must be fix by install_scripts
      fix_scripts = ['mob_edam_import', 'mob_m1_services_import'],
      #module lib files where some variables must be fix by install
      fix_lib = [],
      cmdclass= { 'build' : check_and_build,
                  'install_data' : install_data,
                  'install_scripts' : install_scripts,
                  'install' : install
                  },
      distclass = Distribution
      )
