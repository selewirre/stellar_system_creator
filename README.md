[comment]: https://www.jetbrains.com/help/pycharm/markdown.html#code-blocks
[comment]: https://www.markdownguide.org/basic-syntax/
# Description
This is a package to create custom, scientifically plausible stellar systems.
Check out the [website](https://sites.google.com/view/caelian-assistants/stellar-system-creator),
the [YouTube Channel](https://www.youtube.com/channel/UCWAz_u7tOu2IIIBqjZzY9gA), and the 
[documentation](https://raw.githubusercontent.com/selewirre/stellar_system_creator/master/stellar_system_creator/documentation/build/latex/stellarsystemcreator.pdf)

# Installation
To install this package, run:

```
python3 setup.py sdist bdist_wheel
pip3 install dist/stellar_system_creator-0.4.2.0.tar.gz
```

If you want to check out the example code, look in the folder `examples/...`

To run the GUI use the following code:

```python
import sys
import os

from stellar_system_creator.gui.gui_window import main

if __name__ == "__main__":
    if len(sys.argv) == 1:
        filename = None
    else:
        filename = sys.argv[1]
        filename = os.path.abspath(filename)

    # filename = '../examples/output_files/QuezuliferhWideBinarySystem.sscl'
    main(filename)

```

What you can do with the GUI:
1. Create new multi-stellar, stellar and planetary systems.
2. Modify existing examples.
3. Use S-type or P-type binaries, planets, satellites, asteroid belts, trojans, trojan satellites.
4. Add planetary rings.
5. Convert Stars to Black Holes and vice versa.
6. Change each star/planet/satellite's image (not available for trojans or asteroid belts).
7. Render the system as an image.
8. Use Render image options to add/remove lines of interest (e.g. habitability zone, orbit, frostline, etc.), labels etc.
9. Add celestial objects or systems from file.
10. Make Rendering Settings permanent.

What you can NOT do with the GUI just yet:
1. Create planetary binaries.
2. Add your own image as system background.
3. Copy/Paste celestial objects or systems.
5. Change font or color of Rendered text.

When loading a new system, allow the program to work through it (takes 5-10 seconds). 
Rendering might also take some time.

# License 
GNU GPL v3 license.

# Copyright
Copyright (C) 2022 Selewirre Iskvary

# User Support
I would greatly appreciate it if users clearly state that their illustrations and calculations were made 
(partially or completely) with this project.

# Other Sources
Check my [website](https://sites.google.com/view/caelian-assistants/resources) 
for more great world-builing sources of this type.

# Contact
Please report any questions, issues, concerns, suggestions at <selewirre@gmail.com>.
