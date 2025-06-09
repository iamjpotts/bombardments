"""
The output of asking gpt-o4 to convert the basic code to python 3.12.

Contains three manual edits:
* Allow either commas or whitespace separating the starting positions
* Print matrix numbers evenly spaced
* Only run game once, then exit
"""

import random


def main() -> None:
    print("BOMBARDMENT".center(33))
    print("CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY".center(50))
    print("\n" * 3)

    print("YOU ARE ON A BATTLEFIELD WITH 4 PLATOONS AND YOU")
    print("HAVE 25 OUTPOSTS AVAILABLE WHERE THEY MAY BE PLACED.")
    print("YOU CAN ONLY PLACE ONE PLATOON AT ANY ONE OUTPOST.")
    print("THE COMPUTER DOES THE SAME WITH ITS FOUR PLATOONS.")
    print("")
    print("THE OBJECT OF THE GAME IS TO FIRE MISSILES AT THE")
    print("OUTPOSTS OF THE COMPUTER.  IT WILL DO THE SAME TO YOU.")
    print("THE ONE WHO DESTROYS ALL FOUR OF THE ENEMY'S PLATOONS")
    print("FIRST IS THE WINNER.")
    print("")
    print("GOOD LUCK... AND TELL US WHERE YOU WANT THE BODIES SENT!")
    print("")
    print("TEAR OFF MATRIX AND USE IT TO CHECK OFF THE NUMBERS.")

    for _ in range(5):
        print()

    for r in range(1, 6):
        i = (r - 1) * 5 + 1
        print(f"{i:>3} {i+1:>3} {i+2:>3} {i+3:>3} {i+4:>3}")

    for _ in range(10):
        print()

    positions = random.sample(range(1, 26), 4)
    c, d, e, f = positions

    player_positions = list(map(int, input("WHAT ARE YOUR FOUR POSITIONS: ").replace(',', ' ').split()))
    q, z = 0, 0
    m_positions, used_m_positions = [], set()

    while True:
        y = int(input("WHERE DO YOU WISH TO FIRE YOUR MISSILE: "))

        if y in (c, d, e, f):
            q += 1
            if q == 4:
                print("YOU GOT ME, I'M GOING FAST. BUT I'LL GET YOU WHEN")
                print("MY TRANSISTORS RECUPERATE!")
                break

            print("YOU GOT ONE OF MY OUTPOSTS!")
            if q == 1:
                print("ONE DOWN, THREE TO GO.")
            elif q == 2:
                print("TWO DOWN, TWO TO GO.")
            elif q == 3:
                print("THREE DOWN, ONE TO GO.")

        else:
            print("HA, HA YOU MISSED. MY TURN NOW:")
            while True:
                m = random.randint(1, 25)
                if m not in used_m_positions:
                    used_m_positions.add(m)
                    m_positions.append(m)
                    break

            if m in player_positions:
                z += 1
                if z == 4:
                    print(f"YOU'RE DEAD. YOUR LAST OUTPOST WAS AT {m}. HA, HA, HA.")
                    print("BETTER LUCK NEXT TIME.")
                    return

                print(f"I GOT YOU. IT WON'T BE LONG NOW. POST {m} WAS HIT.")
                if z == 1:
                    print("YOU HAVE ONLY THREE OUTPOSTS LEFT.")
                elif z == 2:
                    print("YOU HAVE ONLY TWO OUTPOSTS LEFT.")
                elif z == 3:
                    print("YOU HAVE ONLY ONE OUTPOST LEFT.")
            else:
                print(f"I MISSED YOU, YOU DIRTY RAT. I PICKED {m}. YOUR TURN:")
        print()


if __name__ == '__main__':
    main()
