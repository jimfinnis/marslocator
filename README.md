This is a locator system for Space Engineers - so it's no good for Actual Real Mars, but there's some
useful stuff for decoding Cartesian coordinates into longitude and latitude and vice versa.

It incorporates a Mars map (again, not Real Mars) from Reddit user AhCrapItsYou :

https://www.reddit.com/r/spaceengineers/comments/ixwqt1/topographical_map_of_mars_8706_x_4748/

and a zoomable image viewer by Marcel Goldschen-Ohm <marcel.goldschen@gmail.com>.

It's crude, but it got my massive mobile base around the Valles Marineris and up onto the Tharsis Bulge!

## Required Python packages
* PyQt5


## Mouse Map Controls
* Left button drag: pan
* Right button box drag: zoom
* Right button double click: zoom all the way out (will do a progressive zoom out at some point because this is annoying)
* Mid-button click: locate a position, set the lon/lat, XYZ and GPS strings accordingly. GPS can be cut-and-pasted into SE GPS

# Buttons
* Decode string: turn the GPS string into Cartesian and Lon/Lat, and add a cross to the map (you might have to zoom to see it)
* Decode coords: turn the Cartesian coords into Lon/Lat and add a cross
* Clear: clear all visible crosses