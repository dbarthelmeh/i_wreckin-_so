"""
class FactoryProduction:
    def __init__(self,who,where,health):
        self.who = who
        self.where = where
        self.health = health

    def status_check(self):
        return "FactoryProduction successfully imported"
    m = main.bc

    def military_count(self,everyone,type):  #kt = knight_total, rt = ranger_total, mt = mage_total, ht = healer_total
            kt = 0
            rt = 0
            mt = 0
            ht = 0
            for units in everyone:
                if m.units.unit_type == m.UnitType.Factory:  #knight = 1, ranger = 2, mage = 3, healer = 4
                    if m.units.factory_unit_type() == m.UnitType.Knight:
                        kt += 1
                    elif m.units.factory_unit_type() == m.UnitType.Ranger:
                        rt += 1
                    elif m.units.factory_unit_type() == m.UnitType.Mage:
                        mt += 1
                    elif m.units.factory_unit_type() == m.UnitType.Healer:
                        ht += 1
                elif m.units.unit_type == m.UnitType.Knight:
                    kt += 1
                elif m.units.unit_type == m.UnitType.Ranger:
                    rt += 1
                elif m.units.unit_type == m.UnitType.Mage:
                    mt += 1
                elif m.units.unit_type == m.UnitType.Healer:
                    ht += 1
            return [kt,rt,mt,ht]

    def ratio(self):
        military_total_count = sum(military_count()) + 1  #we add 1 because we want to increase military by 1
        #here are the ratios
        ratio_k = .2
        #ratio_r = .6
        ratio_m = .1
        ratio_h = .1
        #using some math we get the number of units planned, kp = knight planned, mp = mage planned, ...
        kp = floor(ratio_k * military_total_count)
        mp = floor(ratio_m * military__total_count)
        hp = floor(ratio_h * military_total_count)
        rp = military_count - sum([kp,mp,hp])  #the rest of the planned units should be rangers
        return [kp,rp,mp,hp]

    garrison = unit.structure_garrison()
    if len(garrison) > 0:
        d = random.choice(directions)
        if gc.can_unload(unit.id, d):
            print('unloaded a unit!')
            gc.unload(unit.id, d)
    elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger) and military_count()[1] < ratio()[1]:  #ranger = 1, ...
        gc.produce_robot(unit.id, bc.UnitType.Ranger)
        print('produced a ranger!')

    elif gc.can_produce_robot(unit.id, bc.UnitType.Knight) and military_count()[0] < ratio()[0]:  #knight = 0, ...
        gc.produce_robot(unit.id, bc.UnitType.Knight)
        print('produced a knight!')

    elif gc.can_produce_robot(unit.id, bc.UnitType.Mage) and military_count()[2] < ratio()[2]:  #mage = 2, ...
        gc.produce_robot(unit.id, bc.UnitType.Mage)
        print('produced a mage!')

    elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger) and military_count()[3] < ratio()[3]:  #healer = 3
        gc.produce_robot(unit.id, bc.UnitType.Ranger)
        print('produced a healer!')"""
