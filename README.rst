Peachy
------
"A python3 framework that makes developing 2d games peachy keen."

.. image:: images/logo.png
   :alt: PEACHY

Peachy is a python game development framework made to make developing games in
python a bit more streamlined.

Features
________

* Entity, World structure
* Simple architecture
* 2d collision detection for basic shapes
* 2d rendering
* Resource management and loading
* Tiled support
* Command line utility (TODO)
    * Project scaffolding
    * Profiling
    * Building Executable

(Some features are still under development)

Modules
________

* peachy - The core modules, contains the Engine, World, and Entity classes among others.
* peachy.audio - Contains sound classes (still under heavy maintenance).
* peachy.collision - Multiple collision detection functions for 2d shapes.
* peachy.fs - Short for 'filesystem', this module is used for loading and storing resources.
* peachy.geo - Geometric shapes and collision detection between them.
* peachy.graphics - Drawing and animation.
* peachy.stage - Used to load popular level editor templates (only Tiled at the moment).
* peachy.resources - Resource handling. Loading & management.
* peachy.utils - Utility functions for camera, input, etc.
* peachy.etc - Everything else.


Building Docs
-------------
Peachy is documented using Google Style Python Docstrings. Docs are held
within /docs.

You can build the docs using Sphinx.


Running Tests
-------------
Just use pytest


Installation
____________
Requirements
 * Python 3
 * Pygame (check out resources for compatible versions)
 * PyTMX (If you intend to use peachy to load tiled stages)
 * PyInstaller (If you intend to use Peachy for building your executables)
 * Click (Used for the Peachy CLI tool)

Install via PyPi
    pip install peachy

Install manually
    git clone https://github.com/shellbotx/peachy
    python setup.py install


Resources
_________
Repository ~ https://github.com/shellbotx/peachy

Tutorial ~ coming soon

Peachy is licensed under the MIT license.
