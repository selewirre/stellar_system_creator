Binary System
=============

.. _binary_system:

A binary system is a system of two :ref:`celestial objects <celestial_bodies>` that orbit around a common center.

In this package, we only implement stellar binary systems.
Planetary binary systems are coming soon though!

There are two main types of binary systems:

1. P-type or close binaries. Their distance is small enough so that other bodies can orbit around both of them
2. S-type or wide binaries. Their distance is big enough so that other bodies can orbit each object individually.

In some cases a P-type system can also be an S-type system, meaning that objects orbit
a) around both hosts, b) around one host.

Binary systems can also also be part of other binary systems. It is wise
to not put too many binaries within binaries, since the orbits become highly unstable.
