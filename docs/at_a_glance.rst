Peachy
------

Peachy is a 2D game framework. It's free, open-source, and works on Windows and Linux (and probably OSX).


Features
________

* Entity, World structure
* Simple architecture
* CLI utility
    * Project scaffolding
    * Profiling
    * Building Executable
* Tiled support
* Filesystem operations
    * bmp, png, jpg


Modules
________

* peachy - The core modules that contains the Engine, World, and Entity classes among others
* peachy.audio - Contains sound classes (still under heavy maintenance)
* peachy.fs - Short for 'filesystem', this module is used for loading and storing resources
* peachy.geo - Geometric shapes and collision detection between them
* peachy.graphics - Drawing and animation
* peachy.stage - Used to load popular level editor templates
    * Only supports tiled, but planning to add OGMO and more generic methods
* peachy.ui - Generic user interface template
* peachy.utils - Utility functions for camera, input, etc


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
