# Factory Tycoon

A python game where you need to manage a hole factory as a tycoon manager.

## Dependencies

- Pygame

## Notes about the code

### Coordonates

When passing coordonates in functions, it coorsponds of the coordonates relatively from the map's center
The only exeption is inside the Map object: the map's matrice requires the coordonates to be absolute.

#### **ABSOLUTE COORDONATES** (*Used inside the Map class only*)

(0, 0)|(0, 1)|(0, 2)
---|---|---
(1, 0)|(1, 1)|(1, 2)
(2, 0)|(2, 1)|(2, 2)

#### **RELATIVE COORDONATES (*Used by all functions*)**

(-1, 1)|(0, 1)|(1, 1)
---|---|---
(-1, 0)|(0, 0)|(1, 0)
(-1, -1)|(0, -1)|(1, -1)
