import battlecode as bc
import random
import math
import sys
import traceback

gc = bc.GameController()
directions = list(bc.Direction)
del directions[8]  # removes the direction: center

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

mars_x_destinations = []
mars_y_destinations = []
k = 0
for x_coord in range(gc.starting_map(bc.Planet.Mars).width):
    for y_coord in range(gc.starting_map(bc.Planet.Mars).height):
        if gc.starting_map(bc.Planet.Mars).is_passable_terrain_at(bc.MapLocation(bc.Planet.Mars, x_coord, y_coord)):
            mars_x_destinations.append(x_coord)
            mars_y_destinations.append(y_coord)
            k += 1
            if k == 0:
                print("Mars has no open spots")
print("Mars has %d landing spots:" % k)

# Find all deposits on earth
deposit_locations_earth = []
for x_coord in range(gc.starting_map(bc.Planet.Earth).width):
    for y_coord in range(gc.starting_map(bc.Planet.Earth).height):
        if gc.starting_map(bc.Planet.Earth).initial_karbonite_at(bc.MapLocation(bc.Planet.Earth, x_coord, y_coord)) > 0:
            deposit_locations_earth.append(bc.MapLocation(bc.Planet.Earth, x_coord, y_coord))

# sum of total resources
total_earth_deposit = 0
for i in deposit_locations_earth:
        total_earth_deposit += gc.starting_map(bc.Planet.Earth).initial_karbonite_at(i)
print("total earth deposit is:", total_earth_deposit)

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

my_team = gc.team()
building = False
attacking = False
one_worker_loaded = False
first_rocket = True
rocket_locations = []
known_asteroid_locations = []
num_of_factory_blueprints = 0
num_of_rocket_blueprints = 0
bug_init = {}
cu = bc.MapLocation(
    gc.planet(), int(gc.starting_map(gc.planet()).width / 2), int(gc.starting_map(gc.planet()).height / 2))
# /////////////////////Definitions//////////////////////////////////////////////////////////////////


def factory_count(in_progress):
    ft = in_progress  # factory total
    for units in gc.my_units():
        if units.unit_type == 5:
            ft += 1
    return ft


def adjacent_impassable_terrain(loc):
    result = 0
    for m in directions:
        if not gc.starting_map(gc.planet()).on_map(loc.add(m)):
            result += 1
        elif not gc.starting_map(gc.planet()).is_passable_terrain_at(loc.add(m)):
            result += 1
    return result


def rocket_count(in_progress):
    rt = in_progress  # rocket total
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
        if units.unit_type == bc.UnitType.Factory and units.is_factory_producing():
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


def is_robot(unt):
    if unt.unit_type != bc.UnitType.Factory and unt.unit_type != bc.UnitType.Rocket:
        return True
    else:
        return False


# some movement things
def general_direction(dir):  # dir is one of the integers: 0, 1, ..., 7
    # this returns a list of directions that will be somewhat closer to the target
    result = directions[:]
    der = dir.value
    for i1 in range(3):
        if der - 3 > -1:  # either subtracts or adds 3 from dir making sure that the difference or sum is a valid index
            del result[der - 3]
        else:
            del result[der + 3]
    return result


def can_move_any(un, list):
    result = []
    for dir in list:
        if gc.can_move(un.id, dir):
            result.append(dir)
    if len(result) > 0:
        return True
    else:
        return False


def move_robot_any(unit4, list):
    for dir in list:
        if gc.is_move_ready(unit4.id) and gc.can_move(unit4.id, dir):
            gc.move_robot(unit4.id, dir)


def nearest_karbonite_to_friendlies(list):
    loc = cf
    shortest = 5000
    nearest_loc = cf
    for item in list:
        test_distance = loc.distance_squared_to(item)
        if test_distance < shortest:
            shortest = test_distance
            nearest_loc = item
    return nearest_loc


def util_bug_map(rob):
    loc = rob.location.map_location()
    der = loc.direction_to(bug_init[str(rob.id)]).value
    if der == 8:
        der = 0
    resulting_der = bc.Direction.Center
    for l in range(0, 8):
        if gc.can_move(rob.id, directions[der]):
            if not gc.has_unit_at_location(rob.location.map_location().add(directions[der])):
                resulting_der = directions[der]
                break
        if der == 7:
            der = 0
        else:
            der += 1
    if der == 0:
        bug_init[str(rob.id)] = loc.add(directions[7])
    else:
        bug_init[str(rob.id)] = loc.add(directions[der - 1])
    return resulting_der


def can_replicate_any(unit5):
    result = []
    for dir in directions:
        if gc.can_replicate(unit5.id, dir):
            result.append(dir)
    if len(result) > 0:
        return True
    else:
        return False


def replicate_any(unit3):
    for dir in directions:
        if gc.can_replicate(unit3.id, dir):
            gc.replicate(unit3.id, dir)


def workers_total():
    total = 0
    for units in gc.my_units():
        if units.unit_type == bc.UnitType.Worker:
            total += 1
    return total


# harvest definitions
def can_harvest_adjacent(unit6):
    for di in bc.Direction:
        if gc.can_harvest(unit6.id, di):
            return True
    else:
        return False


def harvest_adjacent(unit7):
    for d1 in bc.Direction:
        if gc.can_harvest(unit7.id, d1):
            return d1


# friendly military units center
def center_of_friendlies():
    x_coordinates = []
    y_coordinates = []
    for unit2 in gc.my_units():
        if unit2.location.is_on_map() and is_robot(unit2):
            instantiate_loc = unit2.location.map_location()
            x_coordinates.append(instantiate_loc.x)
            y_coordinates.append(instantiate_loc.y)
    if len(x_coordinates) > 0 and len(y_coordinates) > 0:
        x_ave = int(sum(x_coordinates) / len(x_coordinates))
        y_ave = int(sum(y_coordinates) / len(y_coordinates))
        return bc.MapLocation(gc.planet(), x_ave, y_ave)
    else:
        return bc.MapLocation(
            gc.planet(), int(gc.starting_map(gc.planet()).width / 2), int(gc.starting_map(gc.planet()).height / 2))


cf = center_of_friendlies()
nk = cf.clone()
nr = cf.clone()


def center_of_uglies():
    x_coordinates = []
    y_coordinates = []
    enemies_sensed = []
    for unit1 in gc.my_units():
        if unit1.location.is_on_map():
            for sensed_units in gc.sense_nearby_units(unit1.location.map_location(), 100):
                if sensed_units.team != my_team and sensed_units not in enemies_sensed:
                    enemies_sensed.append(sensed_units)
    for unit1 in enemies_sensed:
        if unit1.location.is_on_map():
            instantiate_loc = unit1.location.map_location()
            x_coordinates.append(instantiate_loc.x)
            y_coordinates.append(instantiate_loc.y)
    if len(x_coordinates) > 0 and len(y_coordinates) > 0:
        x_ave = int(sum(x_coordinates) / len(x_coordinates))
        y_ave = int(sum(y_coordinates)/len(y_coordinates))
        return bc.MapLocation(gc.planet(), x_ave, y_ave)
    else:
        return bc.MapLocation(gc.planet(), gc.starting_map(
            gc.planet()).width - cf.x, gc.starting_map(gc.planet()).height - cf.y)


while True:
    if gc.get_time_left_ms() > 500:
        if gc.round() % 50 == 0:
            print('pyround:', gc.round())
            print('current karbonite:', gc.karbonite())
            print('time left:', gc.get_time_left_ms())
            cu = center_of_uglies()
            print('center of friendlies:', cu)
            print('center of uglies:', cf)
        if gc.round() % 10 == 0:
            cf = center_of_friendlies()
        if gc.round() % 5 == 0:
            if gc.planet() == bc.Planet.Earth:
                for k_lode in deposit_locations_earth:
                    if gc.can_sense_location(k_lode):
                        if gc.karbonite_at(k_lode) == 0:
                            deposit_locations_earth.remove(k_lode)
                nk = nearest_karbonite_to_friendlies(deposit_locations_earth)
            else:
                for k_lode in known_asteroid_locations:
                    if gc.can_sense_location(k_lode):
                        if gc.karbonite_at(k_lode) == 0:
                            known_asteroid_locations.remove(k_lode)
                nk = nearest_karbonite_to_friendlies(known_asteroid_locations)
            for unit in gc.my_units():
                if unit.unit_type == bc.UnitType.Rocket:
                    if len(unit.structure_garrison()) < 8 and unit.structure_is_built():
                        rocket_locations.append(unit.location.map_location())
            nr = nearest_karbonite_to_friendlies(rocket_locations)
            if gc.planet() == bc.Planet.Mars:
                for unit in gc.my_units():
                    if unit.unit_type == bc.UnitType.Worker:
                        gc.write_team_array(0, 1)
                        break
        if gc.planet() == bc.Planet.Mars:
            if gc.asteroid_pattern().has_asteroid(gc.round()):
                known_asteroid_locations.append(gc.asteroid_pattern().asteroid(gc.round()).location)

        num_of_factory_blueprints = 0
        num_of_rocket_blueprints = 0
        wom = gc.get_team_array(bc.Planet.Mars)[0]
        try:
            # walk through our units:
            for unit in gc.my_units():

                try:  # produce units from a factory
                    if unit.unit_type == bc.UnitType.Factory:
                        garrison = unit.structure_garrison()
                        if len(gc.my_units()) < 65:
                            i = 0
                            while len(garrison) > 0 and i < 2:
                                for d in directions:
                                    if gc.can_unload(unit.id, d):
                                        gc.unload(unit.id, d)
                                i += 1
                        if gc.can_produce_robot(unit.id, bc.UnitType.Worker) and workers_total() < 1:
                            gc.produce_robot(unit.id, bc.UnitType.Worker)
                        elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger) and military_count()[1] < ratio()[1]:
                            # ranger = 1, ...
                            gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        elif gc.can_produce_robot(unit.id, bc.UnitType.Knight) and military_count()[0] < ratio()[0]:
                            # knight = 0, ...
                            gc.produce_robot(unit.id, bc.UnitType.Knight)
                        elif gc.can_produce_robot(unit.id, bc.UnitType.Mage) and military_count()[2] < ratio()[2]:
                            # mage = 2, ...
                            gc.produce_robot(unit.id, bc.UnitType.Mage)
                        elif gc.can_produce_robot(unit.id, bc.UnitType.Healer) and military_count()[3] < ratio()[3]:
                            # healer = 3
                            gc.produce_robot(unit.id, bc.UnitType.Healer)

                    # let's launch a rocket
                    if unit.unit_type == bc.UnitType.Rocket:
                        garrison = unit.structure_garrison()
                        x_roll = random.choice(mars_x_destinations)
                        y_roll = random.choice(mars_y_destinations)
                        if (len(garrison) > 5 or (first_rocket and one_worker_loaded)) and \
                                gc.can_launch_rocket(unit.id, bc.MapLocation(
                                bc.Planet.Mars, x_roll, y_roll)):
                            gc.launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x_roll, y_roll))
                            first_rocket = False
                            num_of_rocket_blueprints -= 1
                            print("launched rocket!")
                            continue
                        if gc.round() > 748:
                            if gc.can_launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x_roll, y_roll)):
                                gc.launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x_roll, y_roll))
                                if unit.location.map_location() in rocket_locations:
                                    rocket_locations.remove(unit.location.map_location())

                    if unit.unit_type == bc.UnitType.Rocket and unit.location.is_on_planet(bc.Planet.Mars):
                        for d in directions:
                            if gc.can_unload(unit.id, d):
                                gc.unload(unit.id, d)
                        continue

                except Exception as e:
                    print('Error:', e)
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
                            building = True
                            continue
                            # These next few lines cause my units to explode
                        # if not one_worker_loaded and other.unit_type == bc.UnitType.Worker:
                        #     if gc.can_load(other.id, unit.id):
                        #         gc.load(other.id, unit.id)
                        #         one_worker_loaded = True
                        #         print('loaded worker')
                        # if one_worker_loaded and other.unit_type != bc.UnitType.Worker:
                        #     if gc.can_load(other.id, unit.id):
                        #         gc.load(other.id, unit.id)
                        #         print('loaded military')
                    if unit.unit_type == bc.UnitType.Rocket:
                        for other in nearby:
                            if wom == 0:  # wom = worker on Mars
                                if gc.can_load(unit.id, other.id) and gc.planet() == bc.Planet.Earth:
                                    gc.load(unit.id, other.id)
                            elif other.unit_type != bc.UnitType.Worker:
                                if gc.can_load(unit.id, other.id) and gc.planet() == bc.Planet.Earth:
                                    gc.load(unit.id, other.id)

                    if unit.unit_type == bc.UnitType.Worker and can_harvest_adjacent(unit):
                        gc.harvest(unit.id, harvest_adjacent(unit))
                        building = True  # so that worker doesn't move away from harvest
                        continue

                    if is_robot(unit):
                        in_attack_range = gc.sense_nearby_units(location.map_location(), unit.attack_range())
                        if unit.unit_type != bc.UnitType.Healer:
                            for other in in_attack_range:
                                if other.team != my_team and gc.is_attack_ready(unit.id) and \
                                        gc.can_attack(unit.id, other.id):
                                    gc.attack(unit.id, other.id)
                                    attacking = True
                        else:
                            for other in in_attack_range:
                                if other.team == my_team and gc.is_heal_ready(unit.id) and \
                                        gc.can_heal(unit.id, other.id):
                                    gc.heal(unit.id, other.id)

                    # okay, there weren't any dudes around
                    # pick a random direction:
                    d = random.choice(directions)
                    if len(rocket_locations) < 1 or location.map_location().distance_squared_to(nr) > 12 or \
                            gc.planet() == bc.Planet.Mars:
                        dir_to = location.map_location().direction_to(cu)
                        dir_away = location.map_location().direction_to(cf)
                    else:
                        dir_to = location.map_location().direction_to(nr)
                        dir_away = location.map_location().direction_to(nr)
                    dir_to_karbonite = location.map_location().direction_to(nk)

                    # or, try to build a factory:
                    if can_replicate_any(unit) and workers_total() < 9:
                        replicate_any(unit)

                    if adjacent_impassable_terrain(location.map_location().add(d)) < 6:
                        if gc.karbonite() >= bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(
                                unit.id, bc.UnitType.Factory, d) and factory_count(num_of_factory_blueprints) < 5:
                            gc.blueprint(unit.id, bc.UnitType.Factory, d)
                            num_of_factory_blueprints += 1
                            building = True
                            print('blueprint factory')
                            continue
                        # let's build a rocket
                        if gc.karbonite() >= bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(
                                unit.id, bc.UnitType.Rocket, d) and rocket_count(num_of_rocket_blueprints) < 5:
                            # if (gc.round() < 400 and rocket_count(num_of_rocket_blueprints) < 1) or gc.round() > 399:
                            gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                            num_of_rocket_blueprints += 1
                            building = True
                            print('blueprint rocket')
                            continue
                    # and if that fails, try to move
    # //////////////////////////////////// military move forward ////////////////////////////////////
                    if gc.is_move_ready(unit.id) and unit.health > 40 and \
                            unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Healer and \
                            not attacking:
                        if gc.can_move(unit.id, dir_to):
                            gc.move_robot(unit.id, dir_to)
                        elif can_move_any(unit, general_direction(dir_to)):
                            move_robot_any(unit, general_direction(dir_to))
                        else:
                            try:
                                bug_init[str(unit.id)] = location.map_location().add(dir_to)
                                go_this_way = util_bug_map(unit)
                                if gc.can_move(unit.id, go_this_way):
                                    gc.move_robot(unit.id, go_this_way)
                            except Exception as e:
                                print('Error2:', e)
                                traceback.print_exc()
    # //////////////////////////////// military retreat /////////////////////////////////////////
                    if gc.is_move_ready(unit.id) and (unit.health < 41 or attacking) and \
                            unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Healer:
                        if gc.can_move(unit.id, dir_away):
                            gc.move_robot(unit.id, dir_away)
                        elif can_move_any(unit, general_direction(dir_away)):
                            move_robot_any(unit, general_direction(dir_away))
                        else:
                            try:
                                bug_init[str(unit.id)] = location.map_location().add(dir_away)
                                go_this_way = util_bug_map(unit)
                                if gc.can_move(unit.id, go_this_way):
                                    gc.move_robot(unit.id, go_this_way)
                            except Exception as e:
                                print('Error2:', e)
                                print('Location of Error', location.map_location().add(util_bug_map(unit)))
                                traceback.print_exc()
    # /////////////////////////////// healer move /////////////////////////////////////////////
                    if gc.is_move_ready(unit.id) and \
                            unit.unit_type != bc.UnitType.Worker and unit.unit_type == bc.UnitType.Healer:
                        if gc.can_move(unit.id, dir_away):
                            gc.move_robot(unit.id, dir_away)
                        elif can_move_any(unit, general_direction(dir_away)):
                            move_robot_any(unit, general_direction(dir_away))
                        else:
                            try:
                                bug_init[str(unit.id)] = location.map_location().add(dir_away)
                                go_this_way = util_bug_map(unit)
                                if gc.can_move(unit.id, go_this_way):
                                    gc.move_robot(unit.id, go_this_way)
                            except Exception as e:
                                print('Error1:', e)
                                print('Location of Error', location.map_location().add(util_bug_map(unit)))
                                traceback.print_exc()
    # //////////////////////////// worker move /////////////////////////////////////////////////////
                    if gc.is_move_ready(unit.id) and unit.unit_type == bc.UnitType.Worker and \
                            not building:
                        if gc.can_move(unit.id, dir_to_karbonite):
                            gc.move_robot(unit.id, dir_to_karbonite)
                        elif can_move_any(unit, general_direction(dir_to_karbonite)):
                            move_robot_any(unit, general_direction(dir_to_karbonite))
                        else:
                            try:
                                bug_init[str(unit.id)] = location.map_location().add(dir_to_karbonite)
                                go_this_way = util_bug_map(unit)
                                if gc.can_move(unit.id, go_this_way):
                                    gc.move_robot(unit.id, go_this_way)
                            except Exception as e:
                                print('Error0:', e)
                                print('Location of Error', location.map_location().add(util_bug_map(unit)))
                                traceback.print_exc()
                    building = False
                    attacking = False
                    if is_robot(unit):
                        in_attack_range = gc.sense_nearby_units(location.map_location(), unit.attack_range())
                        if unit.unit_type != bc.UnitType.Healer:
                            for other in in_attack_range:
                                if other.team != my_team and gc.is_attack_ready(unit.id) and \
                                        gc.can_attack(unit.id, other.id):
                                    gc.attack(unit.id, other.id)
                        else:
                            for other in in_attack_range:
                                if other.team == my_team and gc.is_heal_ready(unit.id) and \
                                        gc.can_heal(unit.id, other.id):
                                    gc.heal(unit.id, other.id)
        except Exception as e:
            print('Error total:', e)
            traceback.print_exc()

# send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()