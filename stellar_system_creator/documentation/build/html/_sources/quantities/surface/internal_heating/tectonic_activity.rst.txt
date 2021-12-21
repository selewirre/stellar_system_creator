Tectonic Activity
=================

.. _tectonic_activity:

The tectonic activity label is determined by amount of total internal heating :math:`Q_{\rm tot}`.
Since each internal heating process is not estimated very accurately, take the
label as a suggestion, rather than an absolute truth, and optimize however you see fit.
Plate tectonics are only present on sold planets, so any planets with substantial gaseous
components will not have any plate tectonics.

The labels we use are:

1. 'Not applicable', if the composition is Icegiant or Gasgiant.
2. 'Unknown', if :math:`Q_{\rm tot} = {\rm nan}`.
3. 'Stagnant', if :math:`Q_{\rm tot} < 0.01 \, {\rm W/m^2}`.
4. 'Low', if :math:`Q_{\rm tot} < 0.04 \, {\rm W/m^2}`.
5. 'Medium Low', if :math:`Q_{\rm tot} < 0.07 \, {\rm W/m^2}`.
6. 'Medium', if :math:`Q_{\rm tot} < 0.15 \, {\rm W/m^2}`.
7. 'Medium High', if :math:`Q_{\rm tot} < 0.2 \, {\rm W/m^2}`.
8. 'High', if :math:`Q_{\rm tot} < 0.35 \, {\rm W/m^2}`.
9. 'Extreme', if :math:`Q_{\rm tot} \ge 0.35 \, {\rm W/m^2}`.
