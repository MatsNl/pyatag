from distutils.core import setup
setup(
  name = 'pyatag',         # How you named your package folder (MyLib)
  packages = ['pyatag'],   # Chose the same as "name"
  version = '0.1.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Python API to connect ATAG One Thermostat',
  author = 'Mats',                   # Type in your name
  author_email = 'mats.nelissen@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/MatsNl/pyatag',
#  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
#  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
  install_requires=[
        'asyncio',
        'aiohttp',
        'netifaces'
    ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
#    'Intended Audience :: Developers',      # Define that your audience are developers
#    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)

