import battlecode as bc
#Find all deposits on earth
print("map_type works")
deposit_locations_earth = []
map_width = bc.PlanetMap.width
for x_coordinate in range(map_width):
    for y_coordinate in range(bc.height):
        coord = [x_coordinate,y_coordinate]
        if bc.has_deposit(coord) == True:
            bc.deposit_locations_earth.append(coord)


#sum of total resources
total_earth_deposit = 0
for i in deposit_locations_earth:
        total_earth_deposit += bc.initial_karbonite_at(i[0],i[1])
