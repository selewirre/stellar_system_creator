
# Main code:
1. Add planetary binaries.
2. Semi-major axis minimum limit should take into account the gas giant radius expansion with the roche limit.
3. Make the habitable zone calculation of planets include the eccentricity by copying the parent insolation model.
4. Add saddle/horseshoe orbits as planetary binaries? 
    - https://www.sciencedirect.com/science/article/abs/pii/0019103581901470
    - https://pdfs.semanticscholar.org/0821/7be72965593b0db36dbba501ed12e842b852.pdf
    - https://academic.oup.com/mnras/article-pdf/426/4/3051/3315870/426-4-3051.pdf
5. add oblateness option?
6. Add stellar initial rotation period/speed from
    - https://arxiv.org/pdf/1307.2891.pdf, 
    - http://assets.cambridge.org/97805217/72181/sample/9780521772181ws.pdf
    - https://www.aanda.org/articles/aa/abs/2012/01/aa17691-11/aa17691-11.html
    - Seems like I can have the same rotation period for stars < 1.2 Ms after 1by.
    - I can also determine the minimum corotation radius by using the minimum starting period at 10-100 Myr or so,
    and hence, define another rough limit for the inner orbit radius!
    - From corotation and rockline, we get what is the suggested inner limit.
7. Make an atmospheric model class with:
     1. Many potential chemicals, their mass, their absorption and reflection spectra.
     2. Make subclasses of specific atmospheres, calculate if the compounds can actually stay in the atmosphere
     3. allow for creation of user based subclasses
     4. estimate greenhouse effect, albedo(?), color of sky, color of vegetation.
     5. Give description of atmosphere for users.
     6. Start with terran atmosphere. add terran atm mods, carry on with mars atmosphere etc.
8. Modify HZ for A-type stars: https://iopscience.iop.org/article/10.3847/1538-4357/aab8fa/pdf pg. 6, table 2
9. Add other types of stars -> probably not, because they are not long-lasting.
10. Add AGN black holes https://arxiv.org/pdf/1909.06748.pdf (it is tricky)
11. add dwarfs?

# Plotting:
1. add an automatic script creator for celestia simulators https://celestia.space/guides.html, https://celestia.space/docs/CELScriptingGuide/Cel_Script_Guide_v1_0g.htm


# GUI:
1. For rendering widget:
   2. make rendering button bigger
   3. make loading image rotate.
2. Add right-click functionalities for tree view
    - make "details" process run if you double-click?
3. fix p-type binary so that it will include both S-type and P-type in one (maybe not?)

# Miscellaneous:
1. check out satellites around gasginats heating model https://iopscience.iop.org/article/10.1088/0004-637X/704/2/1341/pdf
2. Add non-water-based HZ:
    - misc: https://www.mdpi.com/2076-3263/8/8/280/htm
    - methane: https://iopscience.iop.org/article/10.3847/1538-4357/aab8fa/pdf
    - ethane and more heating: https://iopscience.iop.org/article/10.3847/2041-8213/ab68e5/pdf
    - ammonia:
    - hydrogen fluoride:
    - hydrogen sulfide:
3. Make tutorials and examples


[comment]: <publishing options>
[comment]: <flask and html through google sites https://realpython.com/python-web-applications/>
[comment]: <html and github>

