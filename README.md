# DW-Game



# MiniLode


# Notes


## Stage 1 of development
  - Randomised world
  - Gold blocks
  - [Use cmd to parse command line inputs](https://wiki.python.org/moin/CmdModule)
  - Use readline to enable input history

## Stage 2 of development
  - The blocks will be covered with #, until digged (or undigged ' ', digged '.'(dot))
  - Setting of checkpoints available (bought from the store) (can teleport between checkpoints)
  - Difficulty levels implemented (easy, medium, hard)
    - easy --> same as stage 1
    - medium --> Have gunk blocks that saps 1 energy to clean
    - hard (stage 3) --> Lava blocks that instantly kill the player
  - Blocks generator function is tied to the gold blocks - higher distribution of gunk near gold blocks

## Stage 3 of development
  - Only closer blocks will be revealed, but this comes as an upgrade

# Tutorial
  - Short story and guided game

# State Machines

  - Start page, tutorial, and play mode
  
  
# Mechanics

### Types of blocks:
| Block | Points | Description |
| --- | --- | --- |
| Ruby | 15 | Hehehe |
| Gold | 5 | $$$ |
| Gunk | -1 | This sticky mess clogs up your drill bits |
| Lava | -100 | This corrodes away your armour in seconds |
