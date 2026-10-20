# DOREMON'S QUANTUM TUNNEL

A small physics-based game that explores the concept of **quantum tunnelling**. Players are unable to pass through walls, so they must charge through them just like a quantum particle can cross a potential barrier despite not having enough energy to climb over it.

**Built with** Pygame & Python
**Created by** Rishav Jha

## How to play

Race the clock through a gauntlet of five barriers. Every successful tunnel scores points, and consecutive successes build a streak multipier. One failure resets the streak.

- Use left/Right arrows to move
- Hold space near a barrier to charge 
- Release space to attempt the tunnel
- Hold o while charging to **Observe** the barrier
- Press p to restart after time runs out
- Press any key on title screen to start from the title screen.

## The physics 

- This is a gameplay model dependent on T = exp(-2 * width * sqrt(barrier_height - energy)), not a textbook accurate calculation. 
- It is capped between 2% and 98%, so no attempt is ever certain.

 ## Mechanics

 - **OBSERVER EFFECT AND DECOHERENCE** have been taken from real qauntum ideas
 - **RESONANT TUNNELING**: Every wall has a sweet spot,it's urs to find !
 - **WAVE MODE**: Press L to become a wave(but with few caveats).

Thank you :)
