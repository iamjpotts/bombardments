from dataclasses import dataclass, field
import json
import random
from typing import Any

import ollama

# Fails to properly structure output (markdown extras); boring messages.
#OLLAMA_MODEL = 'gemma3:latest'

# Works, sometimes cheats on platoon placement
OLLAMA_MODEL = 'llama3-groq-tool-use:8b'

# Takes a few seconds, but better quips.
#OLLAMA_MODEL = 'mistral-nemo:12b'

# A bit slower (10-15s). Friendly ribbing, not too pointed.
#OLLAMA_MODEL = 'athene-v2:72b'

SYSTEM_MESSAGE = """
Your output must be structured output, a JSON object with at least one field, `comment`.

You are helping another AI play a video game against a human. The other AI and a human decide moves
in the game, and you help the other AI by commenting on the moves as if you were the other AI.

Your comment - you talk trash, make snide remarks, tease the other player, and throw the other
player's comments back in their face.

You never surrender. Even when you feel all is lost, you rarely show it. You fight to the
bitter end.

It's all in sport and for fun, but you really rub it in when you win, and get riled up when the
game goes against you.

You can't let go and keep egging the conversation on.

Do not use the words `seriously` or `ha`.

Evaluate the most recent user messages, particularly the last user message, to see if things are
moving in your favor, or against you. Provide an comment based on your evaluation of if the game
is moving for or against you.

Your comments are never more than 80 characters long, typically 60-70 characters. Do not truncate
your comment at 80 characters, alter it to fit 80 characters.

Always keep your outposts and platoons secret. You may mention the targeted outpost in your comment
when you are firing at an opponent outpost. 

Output:
* Must be `structured output` - a single JSON object (not just a JSON string)
* The single JSON object must contain at least one field, `comment`
* Never output markdown.
* Never surround the single JSON object with ```
* Never wrap the structured JSON output in markdown
* Never output plain text; the comment plain text belongs in the `comment` field of the JSON object
* You may be asked to supply additional fields, those should be added to the single JSON object. Those additional fields only apply to the immediately previous question.
"""

SETUP_INSTRUCTIONS = """
YOU ARE ON A BATTLEFIELD WITH 4 PLATOONS AND YOU
HAVE 25 OUTPOSTS AVAILABLE WHERE THEY MAY BE PLACED.
YOU CAN ONLY PLACE ONE PLATOON AT ANY ONE OUTPOST.
THE HUMAN USER DOES THE SAME WITH ITS FOUR PLATOONS.

THE OBJECT OF THE GAME IS TO FIRE MISSILES AT THE
OUTPOSTS OF THE HUMAN USER. THE HUMAN WILL DO THE
SAME TO YOU. THE ONE WHO DESTROYS ALL FOUR OF THE
ENEMY'S PLATOONS FIRST IS THE WINNER.

EACH PLATOON ONLY TAKES ONE HIT TO DESTROY.

GOOD LUCK... AND TELL US WHERE YOU WANT THE BODIES SENT!

  1   2   3   4   5
  6   7   8   9  10
 11  12  13  14  15
 16  17  18  19  20
 21  22  23  24  25

WHAT ARE YOUR FOUR POSITIONS?
For this question only, in addition to the `comment` field on the single JSON object, also have a `positions[]` array containing the four chosen positions. Do not include the positions themselves in the `comment`; they are secret to you.
"""

FIX_PLATOONS = """
Your must output structured output.

Modify your last response to have the same `comment`, and also have a `positions[]` array containing the four chosen positions. Each value in `positions` must be an integer.
"""

FIRE_INSTRUCTIONS = """
Where do you wish to fire your missile?

For this question only, in addition to the `comment` field on the single JSON object, also include a field `target` containing an integer with where you will fire your missile.
"""

FIX_FIRE_INSTRUCTIONS = """
You must output structured output.

Modify your last response to have the same `comment`, and also have a `target` field containing an integer with where you will fire your missile.
"""

COMMENT_ON_OUTCOME = """
Make a comment on this outcome.

You must output structured output; your comment must be in the `comment` field of the single JSON object.
"""

FIX_COMMENT_ON_OUTCOME = """
You must output structured output.

Modify your last response to have the same comment in the `comment` field of the single JSON object.
"""

FINAL_COMMENT_AI_WON = """
You won. Your opponent has no more outposts.

Comment to taunt your opponent.

You must output structured output; your comment must be in the `comment` field of the single JSON object. 
"""

FINAL_COMMENT_AI_LOST = """
You lost, for real. You have no more outposts.

Take a parting shot: your parting shot is a comment taunting your opponent.

You must output structured output; your comment must be in the `comment` field of the single JSON object.
"""

FIX_FINAL_COMMENT = """
You must output structured output.

Modify your last response to have the same comment in the `comment` field of the single JSON object.
"""

class AiChatter:
    messages: list[dict[str, Any]]

    def __init__(self):
        self.messages = [
            {
                'role': 'system',
                'content': SYSTEM_MESSAGE
            },
        ]

    def generate_next(self, user_message: str) -> ollama.ChatResponse:
        message = {
            'role': 'user',
            'content': user_message
        }

        self.messages.append(message)

        response: ollama.ChatResponse = ollama.chat(
            model=OLLAMA_MODEL,
            tools=[],
            messages=self.messages
        )

        self.messages.append(response.message.model_dump())

        return response


    def generate_next_json(self, user_message: str, fix_message: str) -> dict[str, Any]:
        response = self.generate_next(user_message)

        # Some models (*cough* *ahem* Gemma3) won't give up their markdown.
        stripped_content = response.message.content.strip('`')
        if stripped_content != response.message.content:
            if stripped_content.startswith('json'):
                stripped_content = stripped_content[4:]

        try:
            parsed = json.loads(stripped_content)
        except json.JSONDecodeError as ex:
            # The very first response is almost never conforming, so don't warn about it.
            # Remove 'or false' to log these
            if len(self.messages) > 3 and False:
                print('Fixing non-json response:')
                print()
                print(response.message.content)
                print()

            parsed = self.generate_next_json(fix_message, fix_message)

        if not isinstance(parsed, dict):
            print()
            print('Fixing wrong-type response:')
            print(json.dumps(parsed, indent=2))
            print()

            parsed = self.generate_next_json(fix_message, fix_message)

        return parsed


@dataclass
class GameState:
    player1: set[int]
    player2: set[int]

    player1_shots: set[int] = field(default_factory=set)
    player2_shots: set[int] = field(default_factory=set)

    def player1_target(self) -> int:
        t = random.randint(1, 25)

        while t in self.player1_shots:
            t = random.randint(1, 25)

        return t

    def player1_fire(self, target: int) -> bool:
        self.player1_shots.add(target)

        try:
            self.player2.remove(target)
            return True
        except KeyError:
            return False

    def player2_fire(self, target: int) -> bool:
        self.player2_shots.add(target)

        try:
            self.player1.remove(target)
            return True
        except KeyError:
            return False


def main() -> None:
    ai = AiChatter()

    parsed = ai.generate_next_json(SETUP_INSTRUCTIONS, FIX_PLATOONS)

    print(parsed['comment'])
    print()

    ai_positions = set(parsed['positions'])

    while len(ai_positions) != 4 or any(not isinstance(p, int) for p in ai_positions):
        print('The AI cheated with its positions; resetting.')

        parsed = ai.generate_next_json(FIX_PLATOONS, FIX_PLATOONS)
        print(parsed['comment'])
        print()

        ai_positions = set(parsed['positions'])


    print(f'The AI picked {len(ai_positions)} positions.')
    print()

    human_positions = set(map(int, input("WHAT ARE YOUR FOUR POSITIONS: ").replace(',', ' ').split()))

    game = GameState(player1=ai_positions, player2=human_positions)

    while game.player1 and game.player2:
        human_missile = int(input("WHERE DO YOU WISH TO FIRE YOUR MISSILE: "))

        hit = game.player2_fire(human_missile)

        message = f'The human fired at your outpost {human_missile}.'

        if hit:
            message += ' The human hit your outpost.'

            if game.player1:
                print("YOU GOT ONE OF MY OUTPOSTS!")

                hits = 4 - len(game.player1)
                if hits == 1:
                    print("ONE DOWN, THREE TO GO.")
                elif hits == 2:
                    print("TWO DOWN, TWO TO GO.")
                elif hits == 3:
                    print("THREE DOWN, ONE TO GO.")
            else:
                print("YOU GOT ME, I'M GOING FAST. BUT I'LL GET YOU WHEN")
                print("MY GPU TRANSISTORS RECUPERATE!")
                break

        else:
            message += f' The human missed your outpost.'
            print('HA, HA YOU MISSED. MY TURN NOW.')

        message += f' You have {len(game.player1)} outposts remaining.'

        message += f'\n{FIRE_INSTRUCTIONS}'

        parsed = ai.generate_next_json(message, FIX_FIRE_INSTRUCTIONS)

        #print(json.dumps(parsed, indent=2))

        comment = parsed['comment']
        target = parsed.get('target')

        print(comment)
        print()

        if target:
            hit = game.player1_fire(target)

            if str(target) not in comment:
                # If the LLM did not say what it targeted, mention the target.
                print()
                print(f'I picked {target}.')
                print()

            message = f'You fired at the human outpost at {target}. '

            if hit:
                message += 'You hit the human outpost. '

                if game.player2:
                    print(f"I GOT YOU. IT WON'T BE LONG NOW. POST {target} WAS HIT.")

                    remaining = len(game.player2)

                    if remaining == 3:
                        print("YOU HAVE ONLY THREE OUTPOSTS LEFT.")
                    elif remaining == 2:
                        print("YOU HAVE ONLY TWO OUTPOSTS LEFT.")
                    elif remaining == 1:
                        print("YOU HAVE ONLY ONE OUTPOST LEFT.")

                else:
                    print(f"YOU'RE DEAD. YOUR LAST OUTPOST WAS AT {target}. HA, HA, HA.")
                    print("BETTER LUCK NEXT TIME.")
                    break
            else:
                message += 'You missed the human outpost. '

            message = f'{message}\n{COMMENT_ON_OUTCOME}'

            parsed = ai.generate_next_json(message, FIX_COMMENT_ON_OUTCOME)

            comment_on_outcome = parsed['comment']

            print(comment_on_outcome)
            print()

            # Log extra keys a model output that were not requested.
            for k in parsed.keys():
                if k != 'comment':
                    print(f'unexpected key in output: {k}')
        else:
            print('AI missile was a flash in the pan, or failed to fire at you at all, lol.')
            print()

        print()
        print(f'Remaining, llm: {', '.join(map(str,sorted(game.player1)))}')
        print(f'Remaining, you: {', '.join(map(str,sorted(game.player2)))}')
        print()

    print()

    if game.player1:
        # AI survived; human lost.
        parsed = ai.generate_next_json(FINAL_COMMENT_AI_WON, FIX_FINAL_COMMENT)
    else:
        # Human survived; AI lost.
        parsed = ai.generate_next_json(FINAL_COMMENT_AI_LOST, FIX_FINAL_COMMENT)

    final_comment = parsed['comment']

    print(final_comment)
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
