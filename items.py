class Weapon():
    def __init__(self,name,damage,value):
        self.name=name
        self.damage=damage
        self.value=value
        
    def __str__(self):
        return "{}+{} DAM ".format(self.name, self.damage)

class QuarterStaff  (Weapon):
    def __init__(self,name="Wood Quarter Staff",damage=5,value=20):
        Weapon.__init__(self,name,damage,value)


class ImpToothSpear(Weapon):
    def __init__(self,name="Imp Tooth Spear",damage=10,value=75):
        Weapon.__init__(self,name,damage,value)
 

class DemonBoneShiv(Weapon):
     def __init__(self,name="Demon Bone Shank",damage=14,value=100):
        Weapon.__init__(self,name,damage,value)


class DemonBoneAxe(Weapon):
    def __init__(self,name="Demon Bone Axe",damage=20,value=500):
        Weapon.__init__(self,name,damage,value)

class BrimstoneMace(Weapon):
    def __init__(self,name="Brimstone Mace",damage=24,value=700):
        Weapon.__init__(self,name,damage,value)


class RatlingDeathClaws(Weapon):
    def __init__(self,name="Ratling Death Claws",damage=34,value=1200):
        Weapon.__init__(self,name,damage,value)


class DoomHammer(Weapon):
    def __init__(self,name="Doom Hammer",damage=39,value=1500):
        Weapon.__init__(self,name,damage,value)


class SilverSword(Weapon):
    def __init__(self,name="Silver Sword",damage=50,value=1500):
        Weapon.__init__(self,name,damage,value)


class ShadowBlade(Weapon):
    def __init__(self,name="Shadow Blade",damage=75,value=1500):
        Weapon.__init__(self,name,damage,value)

class DemonBastardSword(Weapon):
    def __init__(self,name="Demon Bastard Sword",damage=45,value=1500):
        Weapon.__init__(self,name,damage,value)

class FacebreakerGauntlet(Weapon):
    def __init__(self,name="FaceBreaker Gauntlet",damage=40,value=1500):
        Weapon.__init__(self,name,damage,value)

class DoomKingSword(Weapon):
    def __init__(self,name="Doom King Sword",damage=75,value=1500):
        Weapon.__init__(self,name,damage,value)


class Armour():  
    def __init__(self,name,protection,value):
        self.name=name
        self.protection=protection
        self.value= value
        
    def __str__(self):
        return "{}+{} PROT ".format(self.name, self.protection)


class Rags(Armour):
    def __init__(self,name="Rags",protection=1,value=20):
        Armour.__init__(self,name,protection,value)


class RatskinTunic(Armour):
    def __init__(self,name="Ratskin Tunic",protection=4,value=75):
        Armour.__init__(self,name,protection,value)

class SilkArmour(Armour):
    def __init__(self,name="Silk Armour",protection=10,value=100):
        Armour.__init__(self,name,protection,value)


class BrimstoneBoneArmour (Armour):
    def __init__(self,name="Brimstone Bone Armour",protection=14,value=100):
        Armour.__init__(self,name,protection,value)


class HereticPlateMail (Armour):
    def __init__(self,name="Heretic Plate Mail",protection=18,value=100):
        Armour.__init__(self,name,protection,value)


class ShadowArmour (Armour):
    def __init__(self,name="Shadow Armour",protection=25,value=100):
        Armour.__init__(self,name,protection,value)


class HolyPlateMail (Armour):
    def __init__(self,name="Holy Plate Mail",protection=35,value=100):
        Armour.__init__(self,name,protection,value)


class DoomKingPlateMail (Armour):
    def __init__(self,name="Doom King Plate Mail",protection=50,value=100):
        Armour.__init__(self,name,protection,value)
