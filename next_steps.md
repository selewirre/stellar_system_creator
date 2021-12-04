
# Main code:
1. Ring, resonances from moons etc. To find ring minima, use atmospheric extend. Ring maxima is the roche limit.
2. Check lagrange L4, L5 point m3 limit. Gascheau's limit?
3. Add saddle orbits?
4. add oblateness option?
5. Add stellar initial rotation period/speed from
    - https://arxiv.org/pdf/1307.2891.pdf, 
    - http://assets.cambridge.org/97805217/72181/sample/9780521772181ws.pdf
    - https://www.aanda.org/articles/aa/abs/2012/01/aa17691-11/aa17691-11.html
    - Seems like I can have the same rotation period for stars < 1.2 Ms after 1by.
    - I can also determine the minimum corotation radius by using the minimum starting period at 10-100 Myr or so,
    and hence, define another rough limit for the inner orbit radius!
    - From corotation and rockline, we get what is the suggested inner limit.
6. Make an atmospheric model class with:
     1. Many potential chemicals, their mass, their absorption and reflection spectra.
     2. Make subclasses of specific atmospheres, calculate if the compounds can actually stay in the atmosphere
     3. allow for creation of user based subclasses
     4. estimate greenhouse effect, albedo(?), color of sky, color of vegetation.
     5. Give description of atmosphere for users.
     6. Start with terran atmosphere. add terran atm mods, carry on with mars atmosphere etc.
7. Modify HZ for A-type stars: https://iopscience.iop.org/article/10.3847/1538-4357/aab8fa/pdf pg. 6, table 2
8. Add other types of stars -> probably not, because they are not long-lasting.
9. Add black holes https://arxiv.org/pdf/1909.06748.pdf (it would only be around AGNs and it is tricky)
10. add dwarfs?

# Plotting:
0. plotting of binaries/trinaries/quaternaries
1. try to plot in processing instead of matplotlib? (supposed to be faster)
    - https://github.com/jdf/processing-py-site
    - https://py.processing.org/
    - https://py.processing.org/tutorials/gettingstarted/
    - https://discourse.processing.org/t/writing-a-python-script-that-runs-a-processing-program/16456/2
2. add an automatic script creator for celestia simulators https://celestia.space/guides.html, https://celestia.space/docs/CELScriptingGuide/Cel_Script_Guide_v1_0g.htm


# GUI:
0. updatable treeview
1. Add to qthread: rendering, opening, saving
2. Add zoom function for svgwidget
3. Add S-type Binaries (multisolar systems) in treeview
4. Add trigger functions to Edit menu
5. Add trigger functions to insert menu
6. Add right-click functionalities for tree view.
    - add details on planet
    - add details on asteroid belt
    - add details on Satellite
    - add details on Trojan
    - add details on binary system
    - add details on solar system
    - add details on planetary system
7. Add tree view header right-click functionalities (and allow name change like rest "system" types)



# Miscellaneous:
1. check out satellites around gasginats heating model https://iopscience.iop.org/article/10.1088/0004-637X/704/2/1341/pdf
2. Add non-water-based HZ:
    - misc: https://www.mdpi.com/2076-3263/8/8/280/htm
    - methane: https://iopscience.iop.org/article/10.3847/1538-4357/aab8fa/pdf
    - ethane and more heating: https://iopscience.iop.org/article/10.3847/2041-8213/ab68e5/pdf
    - ammonia:
    - hydrogen fluoride:
    - hydrogen sulfide:
3. Write down documentation, tutorials and examples


[comment]: <publishing options>
[comment]: <flask and html through google sites>
[comment]: <html and github>

