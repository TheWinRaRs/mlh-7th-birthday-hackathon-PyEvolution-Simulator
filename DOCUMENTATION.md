# PyEvolution Simulator Documentation
When you run the main.py file using
`python3 main.py`

You will be dropped into a title screen inside of the terminal. Press any button to continue, and q to quit at any time(including during the simulation). Hold space to increase the speed of the simulation.

Once inside of the simulation, you will see a simualted ecosystem/environment.

Green areas represent onoccupied areas, with "grass". A yellow [] signifies a food spot, these are generated and change every turn based on MAX_FOOD.

A blueish {} is a live creature, whilst a red <> with a black background signifies a dead creature. These decompose after 10 turns after death.

Creatures of opposite gender can reproduce if they are in a close enough range. The cooldown for this to happen to the same creature is 10 turns.

Reproduction causes genes(currently only size) to be transferred to the child via our binary-bit genome system. Creatures can traverse the environment by moving and collect food for their own health. A food threshold is required to reproduce, and a lack of food will result in death. Food level decrements each turn.

Have fun watching a mini-environment play before your eyes!
