import os
import random
import pickle
from player import*
from functions import*
from dungeons import*
from settlements import*
from maps import*
from intro import Intro 
import time
import winsound
import pathlib
import gzip, hashlib, tempfile
import player as _player_mod

SAVES_DIR = pathlib.Path("saves"); SAVES_DIR.mkdir(exist_ok=True)
SAVE_MAGIC = b"DAGGERFALL\0"
SAVE_VERSION = 1

def _pack(state: dict) -> bytes:
    payload = pickle.dumps(state, protocol=pickle.HIGHEST_PROTOCOL)
    comp = gzip.compress(payload, mtime=0)
    h = hashlib.blake2b(comp, digest_size=16).digest()
    return SAVE_MAGIC + SAVE_VERSION.to_bytes(2, "big") + h + comp

def _unpack(buf: bytes) -> dict:
    if not buf.startswith(SAVE_MAGIC):
        raise ValueError("Not a save file for this game")
    ver = int.from_bytes(buf[len(SAVE_MAGIC):len(SAVE_MAGIC)+2], "big")
    h_expected = buf[len(SAVE_MAGIC)+2:len(SAVE_MAGIC)+2+16]
    comp = buf[len(SAVE_MAGIC)+2+16:]
    if hashlib.blake2b(comp, digest_size=16).digest() != h_expected:
        raise ValueError("Save file is corrupted (checksum mismatch)")
    state = pickle.loads(gzip.decompress(comp))
    state.setdefault("_meta", {})
    state["_meta"]["version"] = ver
    return state

def rebuild_derived():
    """Recompute derived state after loading a save."""
    global position, max_x, max_y

    try:
        max_y = len(mapChoice) - 1
        max_x = len(mapChoice[0]) - 1
    except Exception:
        pass

    try:
        playerMap[y][x] = "@"
        position = mapChoice[y][x]
    except Exception:
        pass

    try:
        hero.recalc_stats()
    except Exception:
        pass

def save_game(slot: str | None = None, silent: bool = False):
    """Autosave only: write to /saves/autosave.sav with atomic replace and .bak backup."""
    slot = "autosave.sav"

    state = {
        "_meta": {"version": SAVE_VERSION, "timestamp": time.time()},
        "hero": hero,
        "x": x, "y": y,
        "playerMap": playerMap,
        "local_name": local_name,
        "music": music,
    }
    blob = _pack(state)
    target = SAVES_DIR / slot

    fd, tmp_name = tempfile.mkstemp(prefix="._tmp_", dir=SAVES_DIR)
    tmp_path = pathlib.Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(blob)
            f.flush(); os.fsync(f.fileno())

        if target.exists():
            backup = target.with_suffix(target.suffix + ".bak")
            try:
                os.replace(target, backup)
            except Exception:
                pass

        os.replace(tmp_path, target)

        if not silent:
            clear_screen_2()
            print(f"Saved successfully as: {target.stem}")
            input("Press [Enter] to continue.")
    except Exception as e:
        try:
            tmp_path.unlink()
        except Exception:
            pass
        print("Could not save game:", e)
        input("Press [Enter] to continue.")


def load_game():
    """Load the latest autosave (saves/autosave.sav) with a simple confirmation."""
    global hero, x, y, playerMap, local_name, music, position

    path = SAVES_DIR / "autosave.sav"
    if not path.exists():
        print("No autosave found (saves/autosave.sav).")
        input("Press [Enter] to continue.")
        return

    print(f"Found autosave: {path.name}")
    ans = input("Load the latest autosave? Type YES to confirm: ").strip().upper()
    if ans != "YES":
        print("Load cancelled.")
        input("Press [Enter] to continue.")
        return

    try:
        with open(path, "rb") as f:
            buf = f.read()
        state = _unpack(buf)
    except Exception:
        bak = path.with_suffix(path.suffix + ".bak")
        if bak.exists():
            print("Autosave appears corrupted. Trying backup (.bak)...")
            try:
                with open(bak, "rb") as f:
                    buf = f.read()
                state = _unpack(buf)
                print("Loaded from backup.")
                try:
                    with open(path, "wb") as f:
                        f.write(buf)
                except Exception:
                    pass
            except Exception:
                print("Backup is also unreadable.")
                input("Press [Enter] to continue.")
                return
        else:
            print("Autosave unreadable and no backup found.")
            input("Press [Enter] to continue.")
            return

    hero       = state["hero"]
    x, y       = state["x"], state["y"]
    playerMap  = state["playerMap"]
    local_name = state.get("local_name", "Nameless")
    music      = state.get("music", 0)

    playerMap[y][x] = "@"
    try:
        rebuild_derived()
    except Exception:
        pass

    try:
        winsound.PlaySound(".\\music\\background.wav",
                           winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
    except Exception:
        pass

    print("Autosave loaded successfully.")
    input("Press [Enter] to continue.")


gameloop=True

x=8
y=4



def order(bag):
    for x in range(len(bag)): 
        print (x+1, str(bag[x]))

def displayMapAround(maps, x, y):
    max_y = len(maps) - 1
    max_x = len(maps[0]) - 1

    y0 = max(0, y - 7)
    y1 = min(max_y, y + 7)

    x0 = max(0, x - 4)
    x1 = min(max_x + 1, x + 5)

    for yy in range(y0, y1 + 1):
        print(maps[yy][x0:x1])

def clear_screen_2():
    print("\033c", end="")     
    displayMapAround(playerMap,x,y)


mapChoice = WorldMap


position = mapChoice[y][x]

hero = Player(100,0,10,5,0,0,0)

max_y = len(mapChoice) - 1
max_x = len(mapChoice[0]) - 1


os.system("mode con cols=120 lines=48")

local_name=Intro()

clear_screen_2()
print("                                                          ")
print("PRESS N + ENTER TO TURN MUSIC ON/OFF.")
print("                                                          ")


music=0
sound=0
cave=0
trigger=0



winsound.PlaySound(".\\music\\background.wav",  winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)



while gameloop == True:
    if getattr(_player_mod, "REQUEST_AUTOSAVE", False):
        save_game("autosave", silent=True)
        _player_mod.REQUEST_AUTOSAVE = False
    while True:
        previousX = x
        previousY = y
        playerMap[y][x] = (".")
        if position == ("~") and hero.ship==True:
            playerMap[y][x] = ("~")
        elif position ==("#") and hero.amulet==True:
            playerMap[y][x] = ("#")

        else:
            pass
            
        print("Name:",local_name,"| Health:",hero.health,"| STR:",(hero.strength+hero.weapon.damage),"| Mana:",hero.mana,"| Gold:",hero.gold,)
        print("Class:",hero.player_class,"| XP:",hero.exp, "| Level:",hero.level,"| Reputation:",hero.reputation,"| Turn:",hero.turn_counter)
        print("Armour:",hero.armour.name,hero.armour.protection,"PROT+","| Weapon:",hero.weapon.name,hero.weapon.damage,"DAM+")
        hero.turn_counter+=1
        hero.mana=min(hero.max_mana,hero.mana+1)
        movement = input("USE [W, A, S, D] TO MOVE; ITEMS[I]; USE[U]; LOAD AUTOSAVE[L]; QUIT[Q]\nChoice: ").upper()

        if movement == "L":
            playerMap[y][x] = "@"
            clear_screen_2()
            load_game()
            break

        elif movement == "Q":
            print("Goodbye!")
            raise SystemExit
      
        if movement == "M":

            if music==0:
                y = y
                playerMap[y][x] = "@"
                clear_screen_2()
                print("Music change")
                winsound.PlaySound(".\\music\\bloodpit.wav",  winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
                music=1
                break

            elif music==1:
                y = y
                playerMap[y][x] = "@"
                clear_screen_2()
                print("Music change")
                winsound.PlaySound(".\\music\\intro.wav",  winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
                music=2
                break

            elif music==2:
                y = y
                playerMap[y][x] = "@"
                clear_screen_2()
                print("Music change")
                winsound.PlaySound(".\\music\\boss.wav",  winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
                music=3
                break

            elif music==3:
                y = y
                playerMap[y][x] = "@"
                clear_screen_2()
                print("Music change")
                winsound.PlaySound(".\\music\\rave.wav",  winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
                music=4
                break

            elif music==4:
                y = y
                playerMap[y][x] = "@"
                clear_screen_2()
                print("Music on")
                winsound.PlaySound(None,  winsound.SND_ALIAS)    
                winsound.PlaySound(".\\music\\background.wav",  winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
                music=0
                break

        if movement == "N":

            if sound==0:
                y = y
                playerMap[y][x] = "@"
                clear_screen_2()
                print("Music off")
                winsound.PlaySound(None,  winsound.SND_ALIAS)
                sound=1
                break
            
            else:
                y = y
                playerMap[y][x] = "@"
                clear_screen_2()
                print("Music on")
                winsound.PlaySound(None,  winsound.SND_ALIAS)    
                winsound.PlaySound(".\\music\\background.wav",  winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
                sound=0
                break
                


            
    
  
        if movement == "W":
            y = y-1
            y = max(0, min(max_y, y))
            position = mapChoice[y][x]
            playerMap[y][x] = "@"
            break

        elif movement == "S":
            y = y+1
            y = max(0, min(max_y, y))
            position = mapChoice[y][x]
            playerMap[y][x] = "@"
            break

        elif movement == "D":
            x = x+1
            x = max(0, min(max_x, x))
            position = mapChoice[y][x]
            playerMap[y][x] = "@"
            break

        elif movement == "A":
            x = x-1
            x = max(0, min(max_x, x))
            position = mapChoice[y][x]
            playerMap[y][x] = "@"
            break

        elif movement==("I"):
            playerMap[y][x] = "@"
            clear_screen_2()
            while True:
                print("Bag[B]; Change[C]; Spellbook[S]; Exit[E]")
                choice=input("Choice: ").upper()
                clear_screen_2()


                if choice==("B"):
                    playerMap[y][x] = "@"
                    clear_screen_2()
                    print("Armour:",hero.armour.name,"| Weapon:",hero.weapon.name,"| Gold:", hero.gold,"| Diamond:",hero.diamond)
                    print("Healing potion:",hero.healing_potion,"| Mana potion:",hero.mana_potion)
                    print("Demon Bone:", hero.demon_bone, "| Ratling Fur:", hero.ratling_fur, "| Imp Tooth:",hero.imp_tooth)
                    print("Demon Silk:",hero.demon_silk,"| Iron Shard:",hero.iron_shard,"| Brimstone:",hero.brimstone)
                    print ("")
                    order(hero.inventory)

                elif choice==("C"):
                    
                    while True:
                        playerMap[y][x] = "@"
                        clear_screen_2()
                        print("Weapon[W], Armour[A],Exit[E]")
                        choice=input("Choice: ").upper()
                         
                        if choice ==("W"):
                            playerMap[y][x] = "@"
                            clear_screen_2()
               
                            Weapons=[item for item in hero.inventory if isinstance (item,Weapon)]

                            if not Weapons:
                                print("You do not have any Weapon to equip")
                                break
                                
                            print ("Choose a Weapon to equip :")

                            for i,item in enumerate(Weapons,1):

                                print ("{}. {}".format(i,item))

                            valid=False
                            while not valid:
                                choice=input("")
                                try:
                                    bob=hero.weapon
                                    hero.inventory.remove(Weapons[int(choice)-1])
                                    hero.weapon=Weapons[int(choice)-1]
                                    hero.inventory.append(bob)
                                    print("You arm yourself with :",Weapons[int(choice)-1])
                                    valid=True 

                                except (ValueError,IndexError):
                                    print("Invalid choice, try again ")
                            break 
                    

                        elif choice ==("A"):
                            playerMap[y][x] = "@"
                            clear_screen_2()
                        
               
                            Armours=[item for item in hero.inventory if isinstance (item,Armour)]

                            if not Armours:
                                print("You do not have any Armour to equip")
                                break
                                
                            print ("Choose an Armour to equip :")

                            for i,item in enumerate(Armours,1):

                                print ("{}. {}".format(i,item))

                            valid=False
                            while not valid:
                                choice=input("")
                                try:
                                    bob=hero.armour
                                    hero.inventory.remove(Armours[int(choice)-1])
                                    hero.armour=Armours[int(choice)-1]
                                    hero.inventory.append(bob)
                                    print("You equip yourself with:", Armours[int(choice)-1])
                                    valid=True 

                                except (ValueError,IndexError):
                                    print("Invalid choice, try again ")
                            break

                        elif choice ==("E"):
                            break


                        else:
                            print ("invalid choice")
                            


                elif choice==("S"):
                    playerMap[y][x] = "@"
                    clear_screen_2()
                    if hero.fire_bolt==True:
                        print("Fire Bolt: Dam: 70 to 120; Mana: 4; INFO: Stun enemy for the round")
                    else:
                        print ("Fire Bolt: ??????????????")

                    if hero.shadow_flee==True:
                        print("Shadow Flee: Dam: None; Mana: 2; INFO: 100% escape non-dungeon combat")
                    else:
                        print("Shadow Flee: ??????????????")

                    if hero.divine_heal==True:
                        print("Divine Heal: Dam: None; Mana: 7/4(Holy Knight); INFO: Heal all damage")
                    else:
                        print("Divine Heal: ??????????????")

                    if hero.ice_blast==True:
                        print("Ice Blast: Dam: 60 to 100; Mana: 5; INFO: Stun enemy, allowing 2 extra melee attacks")
                    else:
                        print("Ice Blast: ??????????????")

                    if hero.chaos_vortex==True:
                        print("Chaos Vortex: Dam: 200 to 500; Mana: 6; INFO: Stun enemy but inflicts between 5 to 40 damage, self damage")
                    else:
                        print("Chaos Vortex: ??????????????")


                elif choice==("E"):
                    break
                    

                else:
                    print("invalid choice")
                    clear_screen_2()
  

        elif movement==("U"):
            
            while True:
                print("What would you like to use? Healing Potion +250 HP[H], Mana Potion +25 Mana[M], Exit[E]")
                choice = input("Use: ").upper()
                playerMap[y][x] = "@"
                clear_screen_2()

                
                
                if choice==("H"):
                
                    if hero.healing_potion>0:
                        hero.healing_potion-=1
                        heal=250
                        hero.health=min(hero.max_health,hero.health+heal)
                        print("You drink a healing potion")
                        print("Your health is", str(hero.health))
                        input("Press [Enter] to continue...")
                        playerMap[y][x] = "@"
                        clear_screen_2()

                        break
                    else:
                        print("You don't have any healing potions")
                        input("Press [Enter] to continue...")
                        playerMap[y][x] = "@"
                        clear_screen_2()
                        break


                elif choice==("M"):
                
                    if hero.mana_potion>0:
                        hero.mana_potion-=1
                        recharge=25
                        hero.mana=min(hero.max_mana,hero.mana+recharge)
                        print("You drink a mana potion")
                        print("Your mana is", str(hero.mana))
                        input("Press [Enter] to continue...")
                        playerMap[y][x] = "@"
                        clear_screen_2()          
                        break
                    
                    else:
                        print("You don't have any mana potions")
                        input("Press [Enter] to continue...")
                        playerMap[y][x] = "@"
                        clear_screen_2()
                        break

                elif choice==("E"):
                    
                    input("Press [Enter] to continue...")
                    playerMap[y][x] = "@"
                    clear_screen_2()    
                    break

                else:
                    print("invalid option")
                    input("Press [Enter] to continue...")
                    playerMap[y][x] = "@"
                    clear_screen_2()    


        else:
            position = mapChoice[y][x]
            playerMap[y][x] = "@"
            clear_screen_2()
            print("Invalid choice")
            print("              ")

        

    if position == ".":
        playerMap[y][x] = "@"
        clear_screen_2()

        if hero.map==True:
        
            r=random.random()
            if r < 0.80 :
                battle_2(hero)
                clear_screen_2()

            elif r < 0.95:
                nothing()
                print("                 ")
                             
            else:
                hero.gold+=treasure()   
                print("                 ")

        else:

            r=random.random()
            if r < 0.85 :
                nothing()
                print("                 ")
                

            elif r < 0.95:
                battle_1(hero)
                clear_screen_2()
                             
            else:
                hero.gold+=treasure()
                print("                 ")
            

    elif position == "/":
        playerMap[y][x] = "@"
        clear_screen_2()

        r=random.random()

                
        if r < 0.80 :
            nothing()
            print("                 ")
            

        elif r < 0.95:
            battle_3(hero)
            clear_screen_2()
                         
        else:
            hero.gold+=treasure()
            print("                 ")

    elif position =="y":
        playerMap[y][x] = "@"
        clear_screen_2()
        if cave==1:
            winsound.PlaySound(".\\music\\rave.wav",  winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
            cave=0
            trigger=1
        print("You feel something different...")
        print("                                          ")   
             


    elif position =="Y":
        playerMap[y][x] = "@"
        clear_screen_2()
        if trigger==1:
            winsound.PlaySound(".\\music\\background.wav",  winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_LOOP)
            trigger=0
        cave=1
        print("You see a wooden sign, it says")
        print("WARNING: you are about to enter the Caves of Profound Misery")
        print("Monsters are incredibly dangerous in here")
        print("                                          ")   

    elif position == "0": 
        playerMap[y][x] = "0"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        print("You are at a wall and you cannot pass.")
        print("                                      ")

    elif position == "~":
        if hero.ship==False:
            playerMap[y][x] = "~"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            print("You cannot walk on water")
            print("                                      ")
        else:
            playerMap[y][x] = "@"
            clear_screen_2()
            print("You sail pass in your ship")
            print("                                      ")

    elif position == "#":
        if hero.amulet==False:
            playerMap[y][x] = "#"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            print("You cannot pass the bed of souls... The darkness is too great")
            print("                                      ")
        else:
            playerMap[y][x] = "@"
            clear_screen_2()
            print("You walk through the bed of souls, with amulet in hand")
            print("                                      ")


    elif position=="?":
        playerMap[y][x] = "@"
        clear_screen_2()
        print("You stumble upon a secret door")
        print("                                      ")
        

    
    elif position == "!":
        if hero.marks==False:
            playerMap[y][x] = "0"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            print("You cannot pass though here these rocky terrains.")
            print("                                      ")
        else:
            playerMap[y][x] = "@"
            clear_screen_2()
            print("You found a secret passageway, you journey ahead")
            print("                                      ")

    elif position == "R":
            playerMap[y][x] = "R"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            rag_man_1(hero)
            print("                                                        ")
            clear_screen_2()

    elif position == "r":
            playerMap[y][x] = "r"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            rag_man_2(hero)
            print("                                                        ")
            clear_screen_2()

    elif position == "J":
            playerMap[y][x] = "O"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            abandoned_outpost(hero)
            print("                                                        ")
            clear_screen_2()



    elif position=="9":
        playerMap[y][x] = "@"
        clear_screen_2()
        if hero.diamond_1==False:
            diamond(hero)
            hero.diamond_1=True
        else:
            nothing()

    elif position=="8":
        playerMap[y][x] = "@"
        clear_screen_2()
        if hero.diamond_2==False:
            diamond(hero)
            hero.diamond_2=True
        else:
            nothing()

    elif position=="Q":
        playerMap[y][x] = "@"
        clear_screen_2()
        if hero.diamond_3==False:
            diamond(hero)
            hero.diamond_3=True
        else:
            nothing()

    elif position=="D":
        playerMap[y][x] = "@"
        clear_screen_2()
        if hero.diamond_4==False:
            diamond(hero)
            hero.diamond_4=True
        else:
            nothing()

    elif position=="E":
        playerMap[y][x] = "@"
        clear_screen_2()
        if hero.diamond_5==False:
            diamond(hero)
            hero.diamond_5=True
        else:
            nothing()


    elif position == "C":
        if hero.sidequest_2==True and hero.sideboss_2_alive==True:
            playerMap[y][x] = "C"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            outside_sideboss_2(hero)
            print("                                                        ")
            clear_screen_2()

        elif hero.sidequest_2==False and hero.sideboss_2_alive==True :
            playerMap[y][x] = "C"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            print("You see some strange caves, you have a bad feeling")
            print("There are bones scattered across the floor ")
            print("The caves are not easy to navigate through without a map")
            print("                                                        ")
        elif hero.map==False:
            playerMap[y][x] = "C"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            print("Even though you have killed the Sea Beast")
            print("You cannot navigate through these caves without a map")
            print("                                                        ")

        elif hero.map==True:
            playerMap[y][x] = "@"
            clear_screen_2()
            print("The caves are no longer an issue for you with your map, you journey ahead")
            print("                                                        ")

    elif position == "K":
        if hero.doom_king_alive==True:
            playerMap[y][x] = "K"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            doom_king(hero)
            print("                                                        ")
            clear_screen_2()

        else:
            playerMap[y][x] = "K"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            print("The doom king bodies lay dead slaughtered by your violent hands")
            print("Nothing has changed much since his demise, maybe his death was not necessary")
            input("Press [Enter] to continue...")
            clear_screen_2()
            
    elif position == "H":
        if hero.sidequest_3==True and hero.sideboss_3_alive==True and hero.sidequest_3_escape==False:
            playerMap[y][x] = "H"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            outside_sideboss_3(hero)
            clear_screen_2()
            
        else:
            playerMap[y][x] = "H"
            x = previousX
            y = previousY
            playerMap[y][x] = "@"
            clear_screen_2()
            print("You see an empty bunk but nothing of value here")
            print("                                      ")


    elif position == "B":
        playerMap[y][x] = "B"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        blood_pit(hero)
        clear_screen_2()          

    elif position == "W":
        playerMap[y][x] = "W"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        outside_doom_wizard(hero)
        clear_screen_2()

    elif position == "G":
        playerMap[y][x] = "G"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        goblin_shaman(hero)
        clear_screen_2()


    elif position == "N":
        playerMap[y][x] = "N"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        outside_nine_dead_eyes(hero)
        clear_screen_2()    


    elif position==("S"):
        playerMap[y][x] = "S"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        settlement_1(hero)
        playerMap[y][x] = "@"
        clear_screen_2()

    elif position==("A"):
        playerMap[y][x] = "S"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        settlement_2(hero)
        playerMap[y][x] = "@"
        clear_screen_2()

    elif position==("Z"):
        playerMap[y][x] = "S"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        settlement_3(hero)
        playerMap[y][x] = "@"
        clear_screen_2()

    elif position==("P"):
        playerMap[y][x] = "P"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        settlement_4(hero)
        playerMap[y][x] = "@"
        clear_screen_2()


    elif position==("X"):
        playerMap[y][x] = "S"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        settlement_5(hero)
        playerMap[y][x] = "@"
        clear_screen_2()  
         


    elif position==("1"):
        playerMap[y][x] = "T"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        while True:
            print("Do you want to enter the Temple of Apshai?")
            print("You heard that the Temple is not that dangerous")
            print("Yes[Y]; No[N]")
            choice=input("Choice: ").upper()
            if choice==("Y"):
                dungeon_1(hero)
                clear_screen_2()
                break

            elif choice==("N"):
                print("You decide not to enter the Temple")
                clear_screen_2()
                break

            else:
                clear_screen_2()
                pass       
        

    elif position==("2"):
        playerMap[y][x] = "D"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        while True:
            print("Do you want to enter the Dungeon of Doom?")
            print("You heard that the dungeon is quite dangerous")
            print("Yes[Y]; No[N]")
            choice=input("Choice: ").upper()
            if choice==("Y"):
                dungeon_2(hero)
                clear_screen_2()
                break

            elif choice==("N"):
                print("You decide not to enter the dungeon")
                clear_screen_2()
                break

            else:
                clear_screen_2()
                pass



    elif position==("3"):
        playerMap[y][x] = "D"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        while True:
            print("Do you want to enter the Dungeon of Akalabeth?")
            print("You heard that the dungeon is dangerous")
            print("Yes[Y]; No[N]")
            choice=input("Choice: ").upper()
            if choice==("Y"):
                dungeon_3(hero)
                clear_screen_2()
                break

            elif choice==("N"):
                print("You decide not to enter the dungeon")
                clear_screen_2()
                break

            else:
                clear_screen_2()
                pass

    elif position==("4"):
        playerMap[y][x] = "D"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        while True:
            print("Do you want to enter the Dungeon of Daggerfall?")
            print("You heard that the dungeon is dangerous")
            print("Yes[Y]; No[N]")
            choice=input("Choice: ").upper()
            if choice==("Y"):
                dungeon_4(hero)
                clear_screen_2()
                break

            elif choice==("N"):
                print("You decide not to enter the dungeon")
                clear_screen_2()
                break

            else:
                clear_screen_2()
                pass

    elif position==("5"):
        playerMap[y][x] = "T"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        while True:
            print("Do you want to enter the Cultist Temple of lost souls?")
            print("You heard that the Temple is quite dangerous")
            print("Yes[Y]; No[N]")
            choice=input("Choice: ").upper()
            if choice==("Y"):
                dungeon_5(hero)
                clear_screen_2()
                break

            elif choice==("N"):
                print("You decide not to enter the dungeon")
                clear_screen_2()
                break

            else:
                clear_screen_2()
                pass           

  
    elif position==("6"):
        playerMap[y][x] = "D"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        while True:
            print ("Do you want to enter the Demonic Stronghold of Gahlak?")
            print("You heard that the Dungeon is very dangerous")
            print("Yes[Y]; No[N]")
            choice=input("Choice: ").upper()
            if choice==("Y"):
                dungeon_6(hero)
                clear_screen_2()
                break

            elif choice==("N"):
                print("You decide not to enter the dungeon")
                clear_screen_2()
                break

            else:
                clear_screen_2()
                pass           

    elif position==("7"):
        playerMap[y][x] = "T"
        x = previousX
        y = previousY
        playerMap[y][x] = "@"
        clear_screen_2()
        while True:
            print ("Do you want to enter the Temple of the Clockwork Fiend?")
            print("You heard that the Temple is very dangerous")
            print("Yes[Y]; No[N]")
            choice=input("Choice:").upper()
            if choice==("Y"):
                dungeon_7(hero)
                clear_screen_2()
                break

            elif choice==("N"):
                print("You decide not to enter the Temple")
                clear_screen_2()
                break

            else:
                clear_screen_2()
                pass           
