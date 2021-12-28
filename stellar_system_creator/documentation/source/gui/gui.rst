GUI
===

.. _gui:

The gui is (a hopefully) easy to navigate tool, once you get the basics. We will start
with an example, and move forward to talking about the individual buttons an functionalities
that are available.

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
can orbit around each :ref:`stars <star>` individually). By default, a :ref:`binary system <binary_system>`
with two :ref:`stars <star>` of the same :ref:`mass <mass>` as our sun are generated,
with :ref:`mean distance <semi_major_axis>` of 500 AU
and an eccentric orbit of 0.6 :ref:`eccentricity <eccentricity>`.
You can find information about the  :ref:`binary system <binary_system>` if you right-click on the binary,
and select Details from the context menu. Similarly, information on the :ref:`stars <star>` can be
found in the Details context menu item.

To add elements in a given system, right-click on the list of the elements you want
to add on, and choose the Add <element of choice> option. For example, to add new
:ref:`planetary system <planetary_system>` on the first :ref:`stellar system <stellar_system>`,
right-click on the Planetary Systems item within the first :ref:`stellar system <stellar_system>`,
and choose add Planetary System. A small prompt
will pop up, where you choose the name of the the :ref:`planetary system <planetary_system>`
and the :ref:`planet <planet>`.
You can then open up the new :ref:`planetary system <planetary_system>` item,
and find out the new :ref:`planet <planet>`, as
well as the empty items :ref:`satellites <satellite>` and :ref:`Trojans <trojan>`.
You can add :ref:`satellites <satellite>` and :ref:`Trojans <trojan>` in
a similar way. To modify the :ref:`planet <planet>`'s characteristics, open up the details menu of the
:ref:`planet <planet>`. To add an :ref:`asteroid belt <asteroid_belt>` in the
:ref:`stellar system <stellar_system>` of your choice, follow the same
procedure as for a :ref:`planetary system <planetary_system>`,
but now do it through the Asteroid Belts item list.

To delete an element, simply right-click on the undesired element and choose
Delete Permanently.
Some elements (e.g. :ref:`planets <planet>` in :ref:`planetary systems <planetary_system>`
or :ref:`stars <star>` in :ref:`stellar systems <stellar_system>`) are not deletable, only replaceable.

To save your progress, go to Files -> Save project and choose the name under
which you want to save the file. The files can get quite big due to saving
images for every single element. The average :ref:`stellar system <stellar_system>`
should be less than 100 MB.

To open an existing project in a new tab, go to files -> Open Project and
select the project of your choice.

To open the documentation through the GUI, go to Help -> Documentation.

Details Dialog
--------------

Opening a detail dialog, depending on the element opened, there
are multiple tabs and for each one there are many options to modify and explore.
Each :ref:`quantity <quantities>` you find in the tab that has the information
symbol on the side, can be double clicked to displace the help menu entry on that
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

The :ref:`surface <surface>` dialog contains all potential surface related
characteristics such as :ref:`temperature <temperature>`, :ref:`gravitational acceleration <surface_gravity>`,
:ref:`size of parent in the sky <angular_diameter>`, and :ref:`tectonic activity <tectonic_activity>`.

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
