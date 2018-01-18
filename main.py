import battlecode as bc
import random
import math
import sys
import traceback
import mage_move
# from communication import *
# import factory_production
# from healer_attack import *
# from healer_move import *
# from knight_attack import *
# from knight_move import *
# from mage_attack import *
# from mage_move import *
# from map_type import *
# from ranger_attack import *
# from ranger_move import *
# from research import *
# from rocket_launch import *
import worker_build
# from worker_harvest import *
# from worker_move import *
# from worker_replicate import *

print("pystarting2")


# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)
del directions[8] # removes the direction: center

gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Ranger)

'''mars_x_destinations = []
mars_y_destinations = []
k=0
for x_coord in range(gc.starting_map(bc.Planet.Mars).width):
    for y_coord in range(gc.starting_map(bc.Planet.Mars).height):
        if gc.starting_map(bc.Planet.Mars).is_passable_terrain_at(bc.MapLocation(bc.Planet.Mars,x_coord,y_coord)):
            # bc.MapLocation(bc.Planet.Mars,x_coord,y_coord)):
            mars_x_destinations.append(x_coord)
            mars_y_destinations.append(y_coord)
            k += 1
            if k == 0:
                print("Mars has no open spots")
print("Mars has %d landing spots:" % k)'''

# Find all deposits on earth
'''deposit_locations_earth = []
for x_coord in range(gc.starting_map(bc.Planet.Earth).width):
    for y_coord in range(gc.starting_map(bc.Planet.Earth).height):
        if gc.starting_map(bc.Planet.Earth).initial_karbonite_at(bc.MapLocation(bc.Planet.Earth,x_coord,y_coord)) > 0:
            deposit_locations_earth.append([x_coord,y_coord])

# sum of total resources
total_earth_deposit = 0
for i in deposit_locations_earth:
        total_earth_deposit += gc.starting_map(bc.Planet.Earth).initial_karbonite_at(bc.MapLocation(
            bc.Planet.Earth,i[0],i[1]))
print("total earth deposit is:", total_earth_deposit)
print("pystarted")'''

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

my_team = gc.team()
building = False
num_of_factory_blueprints = 0
num_of_rocket_blueprints = 0
bug_move_dic = {}
# /////////////////////Definitions//////////////////////////////////////////////////////////////////


def factory_count(in_progress):
    ft = in_progress  #factory total
    for units in gc.my_units():
        if units.unit_type == 5:
            ft += 1
    return ft


def rocket_count(in_progress):
    rt = in_progress  #factory total
    for units in gc.my_units():
        if units.unit_type == bc.UnitType.Rocket:
            rt += 1
    return rt


def military_count():  # kt = knight_total, rt = ranger_total, mt = mage_total, ht = healer_total
    kt = 0
    rt = 0
    mt = 0
    ht = 0
    for units in gc.my_units():
        if units.unit_type == bc.UnitType.Factory and units.is_factory_producing() == True:
            # knight = 1, ranger = 2, mage = 3, healer = 4
            if units.factory_unit_type() == bc.UnitType.Knight:
                kt += 1
            elif units.factory_unit_type() == bc.UnitType.Ranger:
                rt += 1
            elif units.factory_unit_type() == bc.UnitType.Mage:
                mt += 1
            elif units.factory_unit_type() == bc.UnitType.Healer:
                ht += 1
        elif units.unit_type == bc.UnitType.Knight:
            kt += 1
        elif units.unit_type == bc.UnitType.Ranger:
            rt += 1
        elif units.unit_type == bc.UnitType.Mage:
            mt += 1
        elif units.unit_type == bc.UnitType.Healer:
            ht += 1
    return [kt, rt, mt, ht]


def ratio():
    military_total_count = sum(military_count()) + 1  # we add 1 because we want to increase military by 1
    # here are the ratios
    ratio_k = .2
    # ratio_r = .6
    ratio_m = .1
    ratio_h = .1
    # using some math we get the number of units planned, kp = knight planned, mp = mage planned, ...
    kp = math.floor(ratio_k * military_total_count)
    mp = math.floor(ratio_m * military_total_count)
    hp = math.floor(ratio_h * military_total_count)
    rp = military_total_count - sum([kp, mp, hp])  # the rest of the planned units should be rangers
    return [kp, rp, mp, hp]


def is_robot(unit):
    if unit.unit_type != bc.UnitType.Factory and unit.unit_type != bc.UnitType.Rocket:
        return True
    else:
        return False


# some movement things
def general_direction(dir):  # dir is one of the integers: 0, 1, ..., 7
    # this returns a list of directions that will be somewhat closer to the target
    result = directions[:]  #clones our directions
    for i in range(3):
        if dir - 3 > -1:  # either subtracts or adds 3 from dir making sure that the difference or sum is a valid index
            del result[dir - 3]
        else:
            del result[dir + 3]
    return result


def can_move_any(unit, list):
    result = []
    for dir in list:
        if gc.can_move(unit.id, dir):
            result.append(dir)
    if len(result) > 0:
        return True
    else:
        return False


def move_robot_any(unit, list):
    for dir in list:
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, dir):
            gc.move_robot(unit.id, dir)


'''def bug_over_list(location, target_dir):  # a list of Locations() on the other side of obstructions
    result = []
    if target_dir in [0, 1, 7]:  # North, NE, NW
        for i in range(3):
            if gc.starting_map(gc.planet()).on_map(bc.MapLocation(
                    gc.planet(), location.map_location().x - 1 + i, location.map_location().y + 2)):  # if target columns are on the map
                for j in range(5):
                    result.append(bc.MapLocation(gc.planet(), location.map_location().x - 1 + i, location.map_location().y - 2 + j))
    elif target_dir in [3, 4, 5]:  # SE, S, SW
        for i in range(3):
            if gc.starting_map(gc.planet()).on_map(bc.MapLocation(
                    gc.planet(), location.map_location().x - 1 + i, location.map_location().y - 2)):  # if target columns are on the map
                for j in range(5):
                    result.append(bc.MapLocation(gc.planet(), location.map_location().x - 1 + i, location.map_location().y - 2 - j))
    elif target_dir in [2]:  # E
        for i in range(3):
            if gc.starting_map(gc.planet()).on_map(bc.MapLocation(
                    gc.planet(), location.map_location().x + 2, location.map_location().y - 1 + i)):  # if target rows are on the map
                for j in range(5):
                    result.append(bc.MapLocation(gc.planet(), location.map_location().x + 2 + j, location.map_location().y - 1 + i))
    elif target_dir in [6, 8]:  # W, center
        for i in range(3):
            if gc.starting_map(gc.planet()).on_map(bc.MapLocation(
                    gc.planet(), location.map_location().x - 2, location.map_location().y - 1 + i)):  # if target rows are on the map
                for j in range(5):
                    result.append(bc.MapLocation(gc.planet(), location.map_location().x - 2 - j, location.map_location().y - 1 + i))
    return result'''


'''def bug_move(unit):  # makes a move that goes around obstructions
    dirs = list(bc.Direction)
    i = 0
    j = 0
    k = 0
    safe_dir = True  # check that direction is on map
    nearby_factories = gc.sense_nearby_units_by_type(unit.location.map_location(), 2, bc.UnitType.Factory)
    nearby_rockets = gc.sense_nearby_units_by_type(unit.location.map_location(), 2, bc.UnitType.Rocket)
    nearby_buildings = []
    for items in nearby_factories:
        nearby_buildings.append(items)
    for items in nearby_rockets:
        nearby_buildings.append(items)
    if len(nearby_buildings) > 0:
        buildings_in_the_way = True
    else:
        buildings_in_the_way = False
    while safe_dir and i < 7:
        if gc.starting_map(gc.planet()).on_map(unit.location.map_location().add(dirs[i])):
            while not gc.can_move(unit.id, dirs[i]) and not gc.is_occupiable(unit.location.map_location().add(dirs[i]))\
                   or buildings_in_the_way and j < 9:
                j += 1  # if j == 9 then we have checked all directions and we're trapped in a box
                while buildings_in_the_way and k < 9:
                    if gc.starting_map(gc.planet()).on_map(unit.location.map_location().add(dirs[i])):
                        for items in nearby_buildings:  # checks for buildings in the way
                            if unit.location.map_location().add(dirs[i]) == items.location.map_location():
                                if i < 7:
                                    i += 1
                                else:
                                    i = 0
                                k += 1
                                break
                        else:  # if no buildings in the way then run this
                            buildings_in_the_way = False
                            break
                    else:  # if direction is not on map
                        if i < 7:
                            i += 1
                        else:
                            i = 0
                else:  # if k == 9 then we are surrounded by buildings
                    return dirs[8]
                if i < 7:  # check for can move and is occupiable
                    i += 1
                else:
                    i = 0
        else:
            if i < 7:
                i += 1
            else:
                i = 0
    if gc.can_move(unit.id, dirs[i]) and not gc.is_occupiable(unit.location.map_location().add(dirs[i])):
        return dirs[i]
    else:
        return dirs[8]'''


def can_replicate_any(unit):
    result = []
    for dir in directions:
        if gc.can_replicate(unit.id,dir):
            result.append(dir)
    if len(result) > 0:
        return True
    else:
        return False


def replicate_any(unit):
    for dir in directions:
        if gc.can_replicate(unit.id, dir):
            gc.replicate(unit.id,dir)


def workers_total():
    total = 0
    for units in gc.my_units():
        if units.unit_type == bc.UnitType.Worker:
            total += 1
    return total


# harvest definitions
def can_harvest_adjacent(unit):
    for d in directions:
        if gc.can_harvest(unit.id,d):
            return True
        else:
            return False


def harvest_adjacent(unit):
    for d in directions:
        if gc.can_harvest(unit.id,d):
            gc.harvest(unit.id,d)


# friendly military units center
def center_of_friendlies():
    x_coords = []
    y_coords = []
    for unit in gc.my_units():
        if unit.location.is_on_map() and is_robot(unit):
            instantiate_loc = unit.location.map_location()
            x_coords.append(instantiate_loc.x)
            y_coords.append(instantiate_loc.y)
    if len(x_coords) > 0 and len(y_coords) > 0:
        x_ave = int(sum(x_coords)/len(x_coords))
        y_ave = int(sum(y_coords)/len(y_coords))
        return bc.MapLocation(gc.planet(), x_ave, y_ave)
    else:
        return bc.MapLocation(gc.planet(), int(gc.starting_map(gc.planet()).width / 2), int(gc.starting_map(gc.planet()).height / 2))


def center_of_uglies():
    x_coords = []
    y_coords = []
    enemies_sensed = []
    for unit in gc.my_units():
        if unit.location.is_on_map():
            for sensed_units in gc.sense_nearby_units(unit.location.map_location(), 100):
                if sensed_units.team != my_team and sensed_units not in enemies_sensed:
                    enemies_sensed.append(sensed_units)
    for unit in enemies_sensed:
        if unit.location.is_on_map():
            instantiate_loc = unit.location.map_location()
            x_coords.append(instantiate_loc.x)
            y_coords.append(instantiate_loc.y)
    if len(x_coords) > 0 and len(y_coords) > 0:
        x_ave = int(sum(x_coords)/len(x_coords))
        y_ave = int(sum(y_coords)/len(y_coords))
        return bc.MapLocation(gc.planet(), x_ave, y_ave)
    else:
        return bc.MapLocation(gc.planet(), int(gc.starting_map(gc.planet()).width / 2), int(gc.starting_map(gc.planet()).height / 2))


while True:

    if gc.round() % 50 == 0:
        print('pyround:', gc.round())
        print('current karbonite:', gc.karbonite())
        print('center of friendlies:', center_of_friendlies())
        print('center of uglies:', center_of_uglies())
        print('time left:', gc.get_time_left_ms())

    # if gc.round() == 125:
        # current1 = bc.ResearchInfo().get_level(bc.UnitType.Rocket)
        # current2 = bc.ResearchInfo().get_level(bc.UnitType.Ranger)
        # current3 = bc.ResearchInfo().get_level(bc.UnitType.Healer)
        # current4 = bc.ResearchInfo().get_level(bc.UnitType.Mage)
        # current5 = bc.ResearchInfo().get_level(bc.UnitType.Worker)
        # current6 = bc.ResearchInfo().get_level(bc.UnitType.Knight)
        # print('Current rocket research level is:', current1)
        # print('Current ranger research level is:', current2)
        # print('Current healer research level is:', current3)
        # print('Current mage research level is:', current4)
        # print('Current worker research level is:', current5)
        # print('Current knight research level is:', current6)
        # print('factories being built:', num_of_factory_blueprints)
        # print('factory count:', factory_count(num_of_factory_blueprints))
    num_of_factory_blueprints = 0
    num_of_rocket_blueprints = 0
    try:
        # walk through our units:
        for unit in gc.my_units():
            # test if import works
            # try:
                # if unit.unit_type == bc.UnitType.Worker:
                    # wm = WorkerMove(unit,unit.location,unit.health)
                    # wb = worker_build.WorkerBuild(unit,unit.location,unit.health)
                    # wh = WorkerHarvest(unit)
                    # print(wb.status_check())
            # except Exception as e:
                # print('Error:', e)
                # use this to show where the error was
                # traceback.print_exc()

            try:  # produce units from a factory
                if unit.unit_type == bc.UnitType.Factory:
                    # fp = factory_production.FactoryProduction(unit,unit.location, unit.health)
                    # print(fp.military_count())
                    # print(fp.status_check())
                    # print(military_count())
                    # print(ratio())
                    garrison = unit.structure_garrison()
                    # if
                    if len(garrison) > 0:
                        d = random.choice(directions)
                        if gc.can_unload(unit.id, d):
                            # print('unloaded a unit!')
                            gc.unload(unit.id, d)
                    elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger) and military_count()[1] < ratio()[1]:
                        # ranger = 1, ...
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        # print('produced a ranger!')

                    elif gc.can_produce_robot(unit.id, bc.UnitType.Knight) and military_count()[0] < ratio()[0]:
                        # knight = 0, ...
                        gc.produce_robot(unit.id, bc.UnitType.Knight)
                        # print('produced a knight!')

                    elif gc.can_produce_robot(unit.id, bc.UnitType.Mage) and military_count()[2] < ratio()[2]:
                        # mage = 2, ...
                        gc.produce_robot(unit.id, bc.UnitType.Mage)
                        # print('produced a mage!')

                    elif gc.can_produce_robot(unit.id, bc.UnitType.Healer) and military_count()[3] < ratio()[3]:
                        # healer = 3
                        gc.produce_robot(unit.id, bc.UnitType.Healer)
                        # print('produced a healer!')
                # let's launch a rocket
                if unit.unit_type == bc.UnitType.Rocket:
                    garrison = unit.structure_garrison()
                    x_roll = random.choice(mars_x_destinations)
                    y_roll = random.choice(mars_y_destinations)
                    if len(garrison) > 0 and gc.can_launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x_roll, y_roll)):
                        gc.launch_rocket(bc.Planet.Mars, x_roll, y_roll)
                        print("launched rocket!")
                        continue

                # if unit.unit_type == bc.UnitType.Rocket and unit.GameMap.map_mars
                #     d =random.choice(directions)
                #    if gc.can_unload(unit.id,d):
                #       gc.unload(unit.id,d)
                #        continue

            except Exception as e:
                print('Error:', e)
                traceback.print_exc()

            try:
                if unit.unit_type == bc.UnitType.Rocket:
                    pass
                    # rl = RocketLaunch(unit, unit.location, unit.health)
            except Exception as e:
                print('Error:', e)
                traceback.print_exc()

            try:
                if unit.unit_type == bc.UnitType.Ranger:
                    pass
                    # rr = RangerRetreat(unit, unit.location, unit.health)
                    # ra = RangerAttack(unit)
            except Exception as e:
                print('Error:', e)
                traceback.print_exc()

            try:
                if unit.unit_type == bc.UnitType.Knight:
                    pass
                    # kr = KnightRetreat(unit, unit.location, unit.health)
                    # ka = KnightAttack(unit)
            except Exception as e:
                print('Error:', e)
                traceback.print_exc()

            try:
                if unit.unit_type == bc.UnitType.Mage:
                    pass
                    # mr = MageRetreat(unit, unit.location, unit.health)
                    # ma = MageAttack(unit)
            except Exception as e:
                print('Error:', e)
                traceback.print_exc()

            try:
                if unit.unit_type == bc.UnitType.Healer:
                    pass
                    # hr= HealerRetreat(unit, unit.location, unit.health)
                    # hf = HealerForward(unit)
            except Exception as e:
                print('Error:', e)
                # use this to show where the error was
                traceback.print_exc()

            # first, let's look for nearby blueprints to work on
            location = unit.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                        builder = unit.id
                        build_location = other.location
                        # print('building a factory!')
                        building = True
                        # move onto the next unit
                        continue
                if unit.unit_type == bc.UnitType.Worker and can_harvest_adjacent(unit):
                    harvest_adjacent(unit)
                    building = True  # so that worker doesn't move away from harvest
                    # print("harvested karbonite!")
                    continue

                if is_robot(unit):
                    in_attack_range = gc.sense_nearby_units(location.map_location(),unit.attack_range())
                    if unit.unit_type != bc.UnitType.Healer:
                        for other in in_attack_range:
                            if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                                # print('attacked a thing!')
                                gc.attack(unit.id, other.id)
                                continue
                    else:
                        for other in in_attack_range:
                            if other.team == my_team and gc.is_heal_ready(unit.id) and gc.can_heal(unit.id, other.id):
                                gc.heal(unit.id, other.id)
                                # print('Healed unit: %s' % other.unit_type)
                                continue

                # okay, there weren't any dudes around
                # pick a random direction:
                d = random.choice(directions)
                dir_to = location.map_location().direction_to(center_of_uglies())
                dir_away = location.map_location().direction_to(center_of_friendlies())

                # or, try to build a factory:
                if can_replicate_any(unit) and workers_total() < 9:
                    replicate_any(unit)

                if gc.karbonite() >= bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(
                        unit.id, bc.UnitType.Factory, d) and factory_count(num_of_factory_blueprints) < 5:
                    gc.blueprint(unit.id, bc.UnitType.Factory, d)
                    # print("building a new factory")
                    num_of_factory_blueprints += 1
                    # print("%d" % num_of_factory_blueprints)
                # let's build a rocket
                elif gc.karbonite() >= bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(
                        unit.id, bc.UnitType.Rocket,d) and rocket_count(num_of_rocket_blueprints) < 5:
                    gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                    num_of_rocket_blueprints += 1
                # and if that fails, try to move

                # if unit is bug moving then bug move
                '''elif gc.is_move_ready(unit.id) and str(unit.id) in bug_move_dic:
                    gc.move_robot(unit.id, bug_move(unit))
                    if location.map_location() in bug_move_dic[str(unit.id)]:  # is unit clear of obstruction
                        del bug_move_dic[str(unit.id)]

                # impassable terrain ahead, bug move is needed
                elif gc.is_move_ready(unit.id) and not gc.starting_map(gc.planet()).is_passable_terrain_at(
                        location.map_location().add(dir_to)) and \
                        unit.health > 40 and unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Healer:
                    bug_move_dic[str(unit.id)] = bug_over_list(location,dir_to)
                    gc.move_robot(unit.id, bug_move(unit))'''

                # military move towards enemies
                if gc.is_move_ready(unit.id) and gc.can_move(unit.id, dir_to) and unit.health > 40 and \
                        unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Healer:
                    gc.move_robot(unit.id, dir_to)
                '''elif gc.is_move_ready(unit.id) and can_move_any(unit, general_direction(dir_to)) and unit.health > 40\
                        and unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Healer:
                    move_robot_any(unit, general_direction(dir_to))'''

                # military move away from enemies
                '''elif gc.is_move_ready(unit.id) and not gc.starting_map(gc.planet()).is_passable_terrain_at(
                        location.map_location().add(dir_away)) and \
                        unit.health < 41 and unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Healer:
                    bug_move_dic[str(unit.id)] = bug_over_list(location, dir_away)'''
                if gc.is_move_ready(unit.id) and gc.can_move(unit.id, dir_away) and unit.health < 41 and \
                        unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Healer:
                    gc.move_robot(unit.id, dir_away)
                '''elif gc.is_move_ready(unit.id) and can_move_any(unit, general_direction(dir_away)) and \
                        unit.health < 41 and unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Healer:
                    move_robot_any(unit, general_direction(dir_away))'''

                # healer's move
                '''elif gc.is_move_ready(unit.id) and not gc.starting_map(gc.planet()).is_passable_terrain_at(
                        location.map_location().add(dir_away)) and \
                        unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Healer:
                    bug_move_dic[str(unit.id)] = bug_over_list(location,dir_away)'''
                if gc.is_move_ready(unit.id) and gc.can_move(unit.id, dir_away) and \
                        unit.unit_type != bc.UnitType.Worker and unit.unit_type == bc.UnitType.Healer:
                    gc.move_robot(unit.id, dir_away)
                '''elif gc.is_move_ready(unit.id) and can_move_any(unit, general_direction(dir_away)) and \
                        unit.unit_type != bc.UnitType.Worker and unit.unit_type == bc.UnitType.Healer:
                    move_robot_any(unit, general_direction(dir_away))'''

                # worker's move (and anyone else's)
                if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d) and not building:
                    gc.move_robot(unit.id, d)

                building = False
    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()