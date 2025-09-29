import os
import msvcrt


#map
dungeonMap = [["0","0","0","0","0","0","0","0","0"],
              ["0",".",".","0",".",".",".",".","0"],
              ["0",".",".",".",".",".",".","0","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0",".",".",".","0",".",".",".","0"],
              ["0",".","0","0",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0","0","0","0","0","0","0","0","0"]]

playerMap  = [["0","0","0","0","0","0","0","0","0"],
              ["0",".",".","0",".",".",".",".","0"],
              ["0",".",".",".",".",".",".","0","0"],
              ["0","S",".",".",".",".",".",".","0"],
              ["0",".",".",".","0",".",".",".","0"],
              ["0",".","0","0",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0",".",".",".",".",".",".",".","0"],
              ["0","0","0","0","0","0","0","0","0"]]


x = 1
y = 3

def displayMapAround(maps, x, y):
    max_y = len(maps) - 1
    max_x = len(maps[0]) - 1

    y0 = max(0, y - 7)
    y1 = min(max_y, y + 7)

    x0 = max(0, x - 4)
    x1 = min(max_x + 1, x + 5)

    for yy in range(y0, y1 + 1):
        print(maps[yy][x0:x1])



def displayMap(maps):
    for row in maps:
        print(row)

mapChoice = dungeonMap

position = mapChoice[y][x]



while position != "E":
    os.system('cls' if os.name == 'nt' else 'clear')
    displayMap(playerMap)
    max_y = len(mapChoice) - 1
    max_x = len(mapChoice[0]) - 1
    playerMap[y][x] = "."
    print("W,S,D,A,M")
    movement = msvcrt.getch()

    nx, ny = x, y

    if movement in {b'w', b'W'}:
        ny -= 1
        
    elif movement in {b's', b'S'}:
        ny += 1
        
    elif movement in {b'd', b'D'}:
        nx += 1
        
    elif movement in {b'a', b'A'}:
        nx -= 1

    elif movement in {b'm', b'M'}:
        displayMapAround(playerMap, x, y)
        print("[M] Press any key to return...")
        msvcrt.getch()
        playerMap[y][x] = "S"
        continue

    nx = max(0, min(max_x, nx))
    ny = max(0, min(max_y, ny))

    tile = mapChoice[ny][nx]
    
    if tile in {"0", "1"}:
        print("You hit a wall, you stumble in the darkness back to your previous position...")
    else:
        x, y = nx, ny
    
    position = mapChoice[y][x]
    playerMap[y][x] = "S"
        



