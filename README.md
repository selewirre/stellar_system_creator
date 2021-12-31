[comment]: https://www.jetbrains.com/help/pycharm/markdown.html#code-blocks
[comment]: https://www.markdownguide.org/basic-syntax/
# Description
This is a package to create custom, scientifically plausible stellar systems.

# Installation
To install this package, run:

```
python3 setup.py sdist bdist_wheel
pip3 install dist/stellar_system_creator-0.1.0.2.tar.gz
```

If you want to check out the example code, look in the folder `examples/...`

To run the GUI (which is still under construction) use the following code:

```python
import sys

import pkg_resources
from PyQt5.QtWidgets import QApplication
from stellar_system_creator.gui.gui_window import Window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # app.setPalette(get_dark_theme_pallet())
    win = Window()
    filename = pkg_resources.resource_filename(
        'stellar_system_creator', 'examples/output_files/TrakunaStellarSystem.ssc')
    win.central_widget.add_new_tab(filename)

    win.show()
    # win.showMaximized()
    sys.exit(app.exec_())
```

What you can do with the GUI:
1. Create new multi-stellar, stellar and planetary systems.
2. Modify existing examples.
3. Use S-type or P-type binaries, planets, satellites, asteroid belts, trojans, trojan satellites.
4. Change each star/planet/satellite's image (not available for trojans or asteroid belts)
5. Render the system as an image.
6. Use Render image options to add/remove lines of interest (e.g. habitability zone, orbit, frostline, etc.).

What you can NOT do with the GUI just yet:
1. Create rings or planetary binaries.
2. Add your own image as system background.
3. Add ssc files as subsystem (in add XX system option).

When rendering, allow the program to work through it (takes 20-60 seconds) if you added asteroid belts and/or trojans.
It is adding 500 images on a single plt.figure.

# License 
GNU GPL v3 license.

# Copyright
Copyright (C) 2021 Selewirre Iskvary

# User Support
I would greatly appreciate it if users clearly state that their illustrations and calculations were made 
(partially or completely) with this project.

# Other Sources
Great worldbuiling sources of this type can be found on:
1. [Artifexian world-building videos](https://www.youtube.com/playlist?list=PLduA6tsl3gygXJbq_iQ_5h2yri4WL6zsS)
2. [Worldbuilding Pasta](https://worldbuildingpasta.blogspot.com/)

# Contact
Please report any questions, issues, concerns, suggestions at <selewirre@gmail.com>.
