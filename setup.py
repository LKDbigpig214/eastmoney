from distutils.core import setup
import py2exe

import matplotlib

matplotlibdata_files = matplotlib.get_py2exe_datafiles()

setup(
    console = [{'scrip':'./eastmoney.py',}],
    options = {
	'py2exe':{
		'packages': ['matplotlib','pytz'],
		'includes':['matplotlib.backends',
			'matplotlib.figure',
			'matplotlib.pyplot',
			'pylab',
			'numpy',
			'six',
			'matplotlib.backends.backend_tkagg',
			'scipy.special._ufuncs_cxx',
			'scipy.integrate',
			'scipy.integrate.quadpack',
			'scipy.sparse.csgraph._validation',
			],
		'excludes':['_gtkagg',
			'_tkagg',
			'_agg2',
			'_cairo',
			'_cocoaagg',
			'_fltkagg',
			'_gtk',
			'_gtkcairo'
			],
		'dll_excludes':['MSVCP90.dll',
			'libgdk_pixbuf-2.0-0.dll',
			'libgdk-win32-2.0-0.dll',
			'libgobject-2.0-0.dll'
			]
		}
	      },
    data_files = matplotlibdata_files
)
