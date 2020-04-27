# MiniLode

MiniLode is a mining game which you, the MiniLode is on the task to mine for precious gems in the earth's mantle. Faced with difficult situations and tough twist and turns along the way, you need to decide which steps to take, and dig out your own path to success.

[(Please click here for video)](https://github.com/LoJunKai/DW-Game/raw/master/DW%20Game%20Video.mp4)

![Please go to https://github.com/LoJunKai/DW-Game.git if you cannot see this image](https://github.com/LoJunKai/DW-Game/raw/master/Demo.png)


# State Machines
  - Start page, tutorial, and play mode

![Please go to https://github.com/LoJunKai/DW-Game.git if you cannot see this image](https://github.com/LoJunKai/DW-Game/raw/master/State_Diagrams.png)
  
 
# Tutorial

  - Short story and instructions on how to play
  - Gets unlimited coins
  - All blocks will be shown
  
  
# Mechanics

### Types of blocks:
| Block | Coins | Description |
| --- | --- | --- |
| Ruby | 75 | Hehehe |
| Gold | 25 | $$$ |
| Dirt | -1 | Normal ground |
| Junk | -5 | This sticky mess clogs up your drill bits |
| Lava | -1000 | This corrodes away your armour in seconds |

### Parameters
|  | Easy | Medium | Difficult |
|--| :---: | :---: | :---: |
| Starting Coins | 30 | 50 | 70 |
| Playing Area | 15\*15 | 25\*25 | 35\*35 | 
| Checkpoints Price | 5 | 10 | 15 |
| Sonar Max Level | 2 ($75) | 3 ($225) | 4 ($675) |
| No. of Ruby | 0 | 4-6 | 8-12 |
| No. of Gold | 10 | 15 | 20 |
| No. of Junk (per Gold) | 1-5 | 2-7 | 3-9 |
| No. of Lava (per Ruby) | - | 0-1 | 0-1 |
| Position of Junk (rel to Gold) | ±2 | ±2 | ±3 |
| Position of Lava (rel to Ruby) | - | ±2 | ±2 |


# Notes

## Stage 1 of development
  - Randomised world
  - Gold blocks
  - [Use cmd to parse command line inputs](https://wiki.python.org/moin/CmdModule)
  - Use readline to enable input history
  - Implement state machines
  - Walking
  - Digging and collecting coins

## Stage 2 of development
  - The blocks will be covered with #, until digged (or undigged ' ', digged '.'(dot))
  - Setting of checkpoints available (bought from the store) (can teleport between checkpoints)
  - Difficulty levels implemented (easy, medium, hard)
    - easy --> same as stage 1
    - medium --> Have junk blocks that saps 1 energy to clean
    - hard (stage 3) --> Lava blocks that instantly kill the player
  - Blocks generator function is tied to the gold blocks - higher distribution of junk near gold blocks

## Stage 3 of development
  - Only closer blocks will be revealed, but this comes as an upgrade
  - Implement tutorial
