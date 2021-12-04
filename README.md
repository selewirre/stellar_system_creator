[comment]: https://www.jetbrains.com/help/pycharm/markdown.html#code-blocks
[comment]: https://www.markdownguide.org/basic-syntax/
# Description
This is a package to create custom, scientifically plausible stellar systems.

# Installation
To install this package, run:

```
python3 setup.py sdist bdist_wheel
pip3 install dist/stellar_system_creator-0.0.1.2.tar.gz
```

If you want to check out the example code, look in the folder `examples/...`

To run the gui (which is still under construction) use the following code:

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

When rendering, allow the program to work through it (takes 20-60 seconds),
since it is adding 500 images on a single plt.figure.

Most buttons do not work. What works is the star right-click menu.

# License 
GNU GPL v3 license.

# Copyright
Copyright (C) 2021 Selewirre Iskvary

# Contact
Please report any questions, issues, concerns, suggestions at <selewirre@gmail.com>
