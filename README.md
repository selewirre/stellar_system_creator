[comment]: https://www.jetbrains.com/help/pycharm/markdown.html#code-blocks
[comment]: https://www.markdownguide.org/basic-syntax/
# Description
This is a package to create custom, scientifically plausible stellar systems.

# Installation
To install this package, run:

```
python3 setup.py sdist bdist_wheel
pip3 install dist/stellar_system_creator-0.0.5.1.tar.gz
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

Most buttons do not work. What does work are all the details buttons in the treeview and the Render button.
You can modify any of the existing examples, but not create new ones yet.

When rendering, allow the program to work through it (takes 20-60 seconds),
since it is adding 500 images on a single plt.figure (due to solar system rendering ~460 images for a single asteroid belt).

# License 
GNU GPL v3 license.

# Copyright
Copyright (C) 2021 Selewirre Iskvary

# User Support
I would greatly appreciate it if users clearly state that their illustrations and calculations were made 
(partially or completely) with this project. 

# Contact
Please report any questions, issues, concerns, suggestions at <selewirre@gmail.com>
