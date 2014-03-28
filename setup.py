from setuptools import setup, find_packages

# http://stackoverflow.com/a/7071358/735926
import re
VERSIONFILE='coucheventjoiner.py'
verstrline = open(VERSIONFILE, 'rt').read()
VSRE = r'^__version__\s+=\s+[\'"]([^\'"]+)[\'"]'
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)


setup(name='coucheventjoiner',
      version=verstr,
      author='Thomas Burette',
      license='MIT',
      url='https://github.com/tburette/coucheventjoiner',
      description='Join couchsurfing events that are full',
      long_description=open('README.md', 'r').read(),
      packages = find_packages(),
      py_modules=['coucheventjoiner'],
      package_data = {
          'tests': ['*.html']
      },
      install_requires=['enum34>=0.9.23',
                      'lxml>=3.3.3',
                      'requests>=2.2.1',
                    ],
      tests_require=[
          'httmock==1.2.1',
          'mock>=1.0.1',
      ],
      entry_points = {
          'console_scripts': [
              'coucheventjoiner = coucheventjoiner:main'
          ]
      },
)
