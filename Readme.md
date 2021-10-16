Garapa
======================
GABATE - Genetic Algorithm Based Agent for TEtris
-------

GABATE is an AI built on top of [Garapa](https://github.com/h3nnn4n/garapa),
that can learn and play Tetris by itself, fully automated. It also outperforms
all humans.

Records
=======

So far the current record is: 3118 pieces, using the commit f263b80e735faa641cfa03732572aa6012c0f4d6

Features
========

 - Reading the placed blocks from OAM
 - Reading the falling piece from OAM
 - Identifying the falling piece directly from the game memory
 - Identifying the current game screen directly from the game memory
 - 8 different metrics to evaluate where the piece will go
 - Genetic algorithm to weight the different placement criteria
 - Fitness based on the number of cleared lines
 - Autonomous training system
 - For each individual, the game is played a fixed number of times and the
   worst run is used as fitness, to ensure consistency.

License
=======
See `LICENSE` for more info.
