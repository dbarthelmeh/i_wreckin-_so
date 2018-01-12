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
from map_type import *
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

gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Rocket)

mars_x_destinations = []
mars_y_destinations = []
k=0
for x_coord in range(gc.starting_map(bc.Planet.Mars).width):
    for y_coord in range(gc.starting_map(bc.Planet.Mars).height):
        if gc.starting_map(bc.Planet.Mars).is_passable_terrain_at(bc.MapLocation(bc.Planet.Mars,x_coord,y_coord)):  # bc.MapLocation(bc.Planet.Mars,x_coord,y_coord)):
            mars_x_destinations.append(x_coord)
            mars_y_destinations.append(y_coord)
            k += 1
            if k == 0:
                print("Mars has no open spots")
print(mars_x_destinations)
print(mars_y_destinations)
print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

my_team = gc.team()
building = False
num_of_factory_blueprints = 0
num_of_rocket_blueprints = 0
#/////////////////////Definitions//////////////////////////////////////////////////////////////////


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
        if units.unit_type == bc.UnitType.Factory and units.is_factory_producing() == True:  # knight = 1, ranger = 2, mage = 3, healer = 4
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





while True:
    # We only support Python 3, which means brackets around print()

    if gc.round() % 50 == 0:
        print('pyround:', gc.round())
        print(gc.karbonite())
        # print('factories being built:', num_of_factory_blueprints)
        # print('factory count:', factory_count(num_of_factory_blueprints))
    num_of_factory_blueprints = 0
    num_of_rocket_blueprints = 0
    # frequent try/catches are a good idea
    try:
        # walk through our units:
        for unit in gc.my_units():
            # test if import works
            try:
                if unit.unit_type == bc.UnitType.Worker:
                    # wm = WorkerMove(unit,unit.location,unit.health)
                    wb = worker_build.WorkerBuild(unit,unit.location,unit.health)
                    # wh = WorkerHarvest(unit)
                    # print(wb.status_check())
            except Exception as e:
                print('Error:', e)
                # use this to show where the error was
                traceback.print_exc()

            try: # produce units from a factory
                if unit.unit_type == bc.UnitType.Factory:
                    # fp = factory_production.FactoryProduction(unit,unit.location, unit.health)
                    # print(fp.military_count())
                    # print(fp.status_check())
                    # print(military_count())
                    # print(ratio())
                    garrison = unit.structure_garrison()
                    if len(garrison) > 0:
                        d = random.choice(directions)
                        if gc.can_unload(unit.id, d):
                            # print('unloaded a unit!')
                            gc.unload(unit.id, d)
                    elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger) and military_count()[1] < ratio()[1]:  #ranger = 1, ...
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        # print('produced a ranger!')

                    elif gc.can_produce_robot(unit.id, bc.UnitType.Knight) and military_count()[0] < ratio()[0]:  #knight = 0, ...
                        gc.produce_robot(unit.id, bc.UnitType.Knight)
                        # print('produced a knight!')

                    elif gc.can_produce_robot(unit.id, bc.UnitType.Mage) and military_count()[2] < ratio()[2]:  #mage = 2, ...
                        gc.produce_robot(unit.id, bc.UnitType.Mage)
                        # print('produced a mage!')

                    elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger) and military_count()[3] < ratio()[3]:  #healer = 3
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        # print('produced a healer!')
                # let's launch a rocket
                if unit.unit_type == bc.UnitType.Rocket:
                    garrison = unit.structure_garrison()
                    x_roll = random.choice(mars_x_destinations)
                    y_roll = random.choice(mars_y_destinations)
                    if len(garrison) > 7 and gc.can_launch_rocket(unit.id,bc.MapLocation(bc.Planet.Mars,x_roll,y_roll)):
                        gc.launch_rocket(bc.Planet.Mars,x_roll,y_roll)
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
                    if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                        # print('attacked a thing!')
                        gc.attack(unit.id, other.id)
                        continue

            # okay, there weren't any dudes around
            # pick a random direction:
            d = random.choice(directions)

            # or, try to build a factory:
            if gc.karbonite() >= bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d) and factory_count(num_of_factory_blueprints) < 5:
                gc.blueprint(unit.id, bc.UnitType.Factory, d)
                # print("building a new factory")
                num_of_factory_blueprints += 1
                # print("%d" % num_of_factory_blueprints)
            # let's build a rocket
            elif gc.karbonite() >= bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Rocket,d) and rocket_count(num_of_rocket_blueprints) < 5:
                gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                num_of_rocket_blueprints += 1
            # and if that fails, try to move

            elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d) and building == False:
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