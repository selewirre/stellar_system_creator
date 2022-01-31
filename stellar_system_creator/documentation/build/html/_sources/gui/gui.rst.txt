GUI
===

.. _gui:

The gui is (a hopefully) easy to navigate tool, once you get the basics. We will start
with an example, and move forward to talking about the individual buttons an functionalities
that are available. For visual learners, there is a series of video tutorials on this
`YouTube Channel <https://www.youtube.com/channel/UCWAz_u7tOu2IIIBqjZzY9gA>`_.

Simple example
--------------

You can design a new system, by going to Files -> New Project
and choose between a :ref:`planetary <planetary_system>`, a
:ref:`stellar <stellar_system>` or a :ref:`multi-stellar <multi_stellar_system>` system.
In the his example, we will choose a :ref:`multi-stellar system <multi_stellar_system>`,
which includes one or more of the other systems.

When you create a :ref:`multi-stellar system <multi_stellar_system>`,
you create an :ref:`S-type stellar binary system <binary_system>`
(two :ref:`stars <star>` orbiting around each other with a distance big enough that other objects
can orbit around each :ref:`star <star>` individually). By default, a :ref:`binary system <binary_system>`
with two :ref:`stars <star>` of the same :ref:`mass <mass>` as our sun are generated,
with :ref:`mean distance <semi_major_axis>` of 500 AU
and an eccentric orbit of 0.6 :ref:`eccentricity <eccentricity>`.
You can find information about the  :ref:`binary system <binary_system>` if you right-click on the binary,
and select Details from the context menu. Similarly, information on the :ref:`stars <star>` can be
found in the Details context menu item.
To create a :ref:`P-type stellar binary system <binary_system>`
(two :ref:`stars <star>` orbiting around each other with a distance small enough that other objects rotate around
both at the same time), you may "Replace" (see below) the parent of a stellar system, and choose "Stellar Binary"
on the prompt. To convert a :ref:`star <star>` into a :ref:`black hole <black_hole>` and vice versa,
simply right-click on the object you want to convert and choose "Convert to ..".

To add elements in a given system, right-click on the list of the elements you want
to add on, and choose the Add <element of choice> option. For example, to add new
:ref:`planetary system <planetary_system>` on the first :ref:`stellar system <stellar_system>`,
right-click on the Planetary Systems item within the first :ref:`stellar system <stellar_system>`,
and choose add Planetary System. A small prompt
will pop up, where you choose the name of the the :ref:`planetary system <planetary_system>`
and the :ref:`planet <planet>`.
You can then open up the new :ref:`planetary system <planetary_system>` item,
and find out the new :ref:`planet <planet>`, as
well as the empty item lists :ref:`Satellites <satellite>` and :ref:`Trojans <trojan>`.
You can add :ref:`Satellites <satellite>` and :ref:`Trojans <trojan>` in
a similar way. To modify the :ref:`planet <planet>`'s characteristics, open up the details menu of the
:ref:`planet <planet>`. To add an :ref:`asteroid belt <asteroid_belt>` in the
:ref:`stellar system <stellar_system>` of your choice, follow the same
procedure as for a :ref:`planetary system <planetary_system>`,
but now do it through the Asteroid Belts item list.

You can also add a system (Planetary or Stellar) from a file. That is, if you worked on a subsystem you want to
incorporate in a bigger system, you can save it to file and upload it on the bigger one. This can also
be used as a "copy" function, which is not yet available officially. Similarly you can save subsystems as
separate files, for the same purpose.

To delete an element, simply right-click on the undesired element and choose
Delete Permanently.
Some elements (e.g. :ref:`planets <planet>` in :ref:`planetary systems <planetary_system>`
or :ref:`stars <star>` in :ref:`stellar systems <stellar_system>`) are not deletable, only replaceable.

To save your progress, go to Files -> Save project and choose the name under
which you want to save the file. SSC files can get quite big due to saving
images for every single element. The average :ref:`stellar system <stellar_system>`
should be less than 100 MB. **I highly suggest using the SSCL type**, which is 10-1000 times
lighter but they take a little bit more time to load.

To open an existing project in a new tab, go to files -> Open Project and
select the project of your choice.

To open the documentation through the GUI, go to menu option "Help". There are three ways to open the
documentation. One is within the gui itself (small window opening HTML files),
another is as a PDF file, and the third one is as an HTML file on the default internet browser.

Details Dialog
--------------

Opening a detail dialog, depending on the element opened, there
are multiple tabs and for each one there are many options to modify and explore.
Each :ref:`quantity <quantities>` you find in the tab that has the information
symbol on the side, can be double clicked to display the help menu entry on that
:ref:`quantity <quantities>`.

The main tab is Designations, a tab that contains general information,
such as name and parents (which body they :ref:`orbit <orbital>` or are part of),
and other classification and composition characteristics.

The second tab is the physical characteristics tab, which contains
information about the :ref:`mass <mass>`, :ref:`radius <radius>`, :ref:`rotation <spin_period>`, and :ref:`age <age>`.
For :ref:`stars <star>`, it also includes some :ref:`spectral/surface <emission>` characteristics.

Another tab would be the :ref:`orbit <orbital>` characteristics, which includes
:ref:`eccentricity <eccentricity>`, :ref:`semi-major axis <semi_major_axis>` etc.

The :ref:`children orbit limit <children_orbit_limits>` tab contain different types of orbit
limits for the bodies that orbit around the body for which the detail dialog is open.

The :ref:`surface <surface>` tab contains all potential surface related
characteristics such as :ref:`temperature <temperature>`, :ref:`gravitational acceleration <surface_gravity>`,
:ref:`size of parent in the sky <angular_diameter>`, and :ref:`tectonic activity <tectonic_activity>`.

The :ref:`ring <ring>` tab allows the modification of the color of the potential ring of
a given :ref:`planet <planet>`. The addition of ring gaps happens automatically
with the addition of ref:`satellites <satellite>`, or one can manually change the color gradient
in such a way so as to imitate the ring-gap feeling.

The :ref:`insolation <insolation_models>` tab contains the two different :ref:`insolation models <insolation_models>`
that can be used to calculate the :ref:`habitable zone <habitable_zones>` around
:ref:`stars <star>` and :ref:`stellar binaries <binary_system>`.

The :ref:`habitability <habitability>` tab contains all the information relevant
to the :ref:`habitability <habitability>` of the body. For :ref:`stars <star>` that includes
the :ref:`habitable zone <habitable_zones>`.
For :ref:`planets <planet>` and :ref:`satellites <satellite>`,
the :ref:`habitability <habitability>` is dependent on multiple factors.
Each one that is violated is portrayed on the habitability violations box.

Finally, the image tab contains the default image, or a option for the user to add their own.

Rendering
---------

One of the biggest advantages of this package is the ability to render images of the
created systems. With a simple click of a button (same as the logo) and a few seconds
of patience, the system is rendered.

The user has a multitude of options to choose from, by clicking the "Rendering Settings"
button. From the pop-up dialog, the user can choose which sub-system to render (via the
top-most drop-down menu).
The user can chose the resolution scale of the rendered system. The resolution with
scale "s" corresponds to a png image of :math:`1100 \cdot s` x :math:`300 \cdot s`
pixels. The lower the resolution, the faster the rendition process.
Next there are three groups of options. The first one, called "Line/Area Options",
allows the user to choose which of the vector-lines/areas will be rendered, as
well as their line-width.
The second one, called "Label Options" allows the user to choose which of the labels
of the distances and celestial objects' names will be displayed as well as their font size.
Lastly, there "Celestial Object Options" allows the user to choose which specific type of
:ref:`celestial object <celestial_bodies>` they want to render. The option
"Satellite display vertical distance" refers to the distance between rendered :ref:`satellites <satellite>`
in :ref:`stellar systems <stellar_system>` (they are depicted on the
left side of their parent :ref:`planet <planet>`. This value is normalized to the total height of the displayed image,
meaning that with the default value of 0.1, up to 9 satellites will be depicted on the rendered image.
The user may choose to make this value smaller, to allow for more satellites to be displayed.
However, I do find more than 15 satellites to make the rendered image a tad too crowded.

Finally, the user can save the rendered image as a PNG file. I suggest working with a lower scale (resolution)
until the rendered image is satisfying for speed purposes, and then re-rendering with a higher scale before
saving the image.
