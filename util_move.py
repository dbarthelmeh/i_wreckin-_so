import battlecode as bc

class UtilMove(object):
    pass


# bug movement. Does move_robot action
#
# unit is the unit to be moved
# x    is the x cord to move to
# y    is the y cord to move to
def util_bug(unit, x, y):
    loc = unit.location.map_location()
    der = loc.direction_to(bc.MapLocation(gc.planet(), x, y)
    for i in (0,8): 
        if (gc.can_move(unit.id, der):
            gc.move_robot(unit.id,der)
            break
        if der == 7:
            der = 0
        der++

# Same as util_bug but takes a MapLocation as input
# instead of x y cord.
#
# unit is the unit to be moved
# to   is the MapLocation to move to
def util_bug_map(unit, to):
    loc = unit.location.map_location()
    der = int(loc.direction_to(to))
    for i in range(0,8):
        if gc.can_move(unit.id, directions[der]):
            gc.move_robot(unit.id,directions[der])
            break
        if der == 7:
            der = 0
        der += 1
    if der == 0:
        return 7
    else:
        return der - 1





