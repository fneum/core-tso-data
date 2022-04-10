# Matching Core TSO Grid Data with OSM Data #

1. Download PBF files with OSM data (all NUTS 1 files for one country for better performance)
2. Get the information about the EHV substations in OSM
3. Compare the names the the OSM data and Core TSO with fuzzywuzzy (it gives a list of the 5 best matches)
4. Check manually if the choices are correct:
  - If is not the first match, see if it is one of the others (almost always is the second)
  - If there is data missing in OSM: Add it in OSM and return to step 1
  - Some data is missing because it is actually in a different country, that was added manually, but could be handled later

## Notes: ##
- Over 95% are already well allocated and the rest is easy to correct
- Updating the OSM is the most time consuming step, but is easy to do and worth it for the community
- In OSM sometimes there is more than one substation with the same name: Just take the first one (for now)
- A 100 % match of the names is impossible (more fancy fuzzywuzzy functions were tested), but the manual adjustments is minimal 
- The missing data from other countries and Tie Lines and Trafos, could be allocated later