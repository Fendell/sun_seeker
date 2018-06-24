#!/usr/bin/env python3
#Offset for azimuth in pysolar

def offset(sun_value):
    offset = 180.0
    if abs(sun_value) >= 0 and abs(sun_value) < 180:
        print(abs(sun_value) + offset)
    else:
        print(abs(sun_value + offset))

print('\nOffset test')
offset(0.0)
offset(-23.0)
offset(-90.0)
offset(-180.0)
offset(-270.0)
offset(-359.5)
