# Genius Square

[Jo](https://github.com/jd12006) and I were playing genius square (see an explanation of the game below) and were intrigued by the claim that, among all 62208 possible configurations of the board, all of them have <b>at least one solution</b>.
Since we were actually quite quick at cracking each of the configurations, we wondered about the general difficulty of the game. We decided to take a data-driven approach to answer that. In particular we wanted to know:

- Q.1. Is there any configuration with <i>exactly</i> one solution? 
- Q.2. If not, what is the hardest configuation (i.e. with the minimum number of solutions)?
- Q.3. How hard is a "typical" game (i.e. what is the median number of solutions)?
- Q.4. What is the easiest configuration?

## Explanation

The game is pretty simple. Each player owns a 6x6 board and 9 pieces with different shapes. At the beginning of each round, 7 dice are rolled and, based on the result, 7 squares of the board are "blocked" by circular pieces. The winner of the round is the player who is able to place the 9 pieces correctly into the board. Below are some pictures:

Original configuration:


<img src="https://github.com/aCampello/genius-square/blob/main/empty-board.png" width="500" />


Picture of the pieces:

<img src="https://github.com/aCampello/genius-square/blob/main/pieces.png" width="500" />

Solved board:

<img src="https://github.com/aCampello/genius-square/blob/main/solved-board.png" width="500" />

The dice are a bit "funny", and some of the faces have repeated numbers, which leads to the magical 62208 numbers.
In particular, those are the "faces" of each of the 7 dice:

```python
[
    ('C3', 'E3', 'D3', 'D4', 'B4', 'C4'),
    ('E6', 'F5', 'E4', 'F4', 'E5', 'D5'),
    ('C5', 'F6', 'A4', 'D6', 'B5', 'C6'),
    ('B1', 'C2', 'A2', 'B3', 'A3', 'B2'),
    ('E1', 'F2', 'B6', 'A5'),
    ('F3', 'D2', 'E2', 'C1', 'A1', 'D1'),
    ('A6', 'F1')
]
```

The pieces are uniquely identified by their colour and have their own class in `base_classes.py`.
Each of them can be flipped or rotated (but some of the isometric transformetions will yield the same "shape"). We decided to hard-code those as opposed to doing some maths to figure out automatically, as it was Friday night, too late for maths.
```python
grey = Piece('grey')
green = Piece('green')
blue = Piece('deepskyblue')
orange = Piece('darkorange')
yellow = Piece('yellow')
red = Piece('red')
brown = Piece('sienna') # Had no idea this is a colour
purple = Piece('purple')
navy = Piece('navy')
```

## Approach

Given a configuration, it is clear that there are quite a lot of possible solutions in general. 
We noticed that due to the fact that it was very rare that both of us came up with exactly the same solution.
 
We thus decided to break down the problem of "solving" the game into two steps:

1. Find an algorithm that, given a configuration, finds `one` solution. Extend that algorithm to find `all` solutions.
2. Iterate over all possible 62208 configurations and find the distribution of number of solutions.

### 1. Finding possible solutions

There is a huge discrepancy between finding <i>one</i> solution (easy problem) and finding all solutions (combinatorially hard).
After modelling the problem in a classic Object-Oriented way (see `genius_square/base_classes.py` to appreciate the objects `Pieces` and `Board`),
we decided for a recursive approach to solve the game. In particular, the general approach is:

```bash
For all possible positions for the j-th piece:
Place the j-th piece on the board and "block" its squares
Call the solver with (9-j) pieces recursively
```

In python this looks like this (see `solver.py:solve`):

```python
def (board: Board, pieces=[grey, green, blue, orange, yellow, red, brown, purple, navy])
    ... 
    for rotation, position in positions:
            board.place_piece(pieces[0], position=position, rotation=rotation)
            
            # Recursive step
            solution_remaining_pieces = solve(board, pieces[1:], all_solutions=all_solutions)
    ...
```

Finding one solution for each configuration is really just a question of milliseconds. Finding <i>all</i> solutions was another story.
Sometimes it took as much as 10 seconds for one configuration alone. We estimated it would take us a week to have our sought-after answer to the original question on how hard the game was. 

### 2. Iterating over all configuration

Probably some smart mathematics to do with the symmetries of the board could have cut our work in half or more. 
But, again, Friday night and the fact that we were a bit tired of this experiment led us to use brute force. But we needed used it smartly because we didn't want to wait a week for an answer.

This search could be easily parallelized with pythons `joblib` library. See the beautiful line 123 of `solver.py` (nothing else is beautiful in that file).

```python
results = \
    Parallel(n_jobs=8)(
        delayed(one_iteration_solve)(dice) for dice in all_dice_combinations[:1000]
    )
```

With this, and with the help of some mammoth AWS EC2 instance, we could have our response (and find all possible solutions for all possible configurations) in about an hour.

And below are the awaited final results.

## Results

- Q.1. Is there any configuration with <i>exactly</i> one solution?

No.

 
- Q.2. If not, what is the hardest configuration (i.e. with the minimum number of solutions)?

The hardest configuration is the one shown above in the [explanation](#explanation). It has 11 possible solutions.

- Q.3. How hard is a "typical" game (i.e. what is the median number of solutions)?

The median number of solutions is 1340, with inter-quartile range between 715 and 2414. Based on that, I'd say the game is actually pretty easy. (0.95-quantile around 5600).

- Q.4. What is the easiest configuration?

The easiest configuration has 22317. That's a ridiculous number. Below is that configuration (I'm sure you can find a solution given the pieces):

 <img src="https://github.com/aCampello/genius-square/blob/main/easy.png" width="500" />

Below is the actual distribution of the number of solutions:

<img src="https://github.com/aCampello/genius-square/blob/main/histogram.png" width="500" />

## Why did we do this?

I have no idea. It seemed like a good idea to crack the game computationally instead of actually playing it. Maybe we'll suggest improvements or different modes to the game in the future.
