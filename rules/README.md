# Rules

## The Basics

ApocaWarlords is a 2-player tile-based turn-based competitive tower defense game. Think of it as a mix between Clash Royale and Bloons TD Battles. Each player has a Base, which looks like a castle. The objective of the game is for your Base to survive longer than your opponent's ( or equivalently, to DESTROY your opponent's Base ).

"How do I survive?" you're probably asking. Well, as this is a tower defense game, you'll be building Towers to defend your Base. "Defend against what?", you ask? Well, that would be the hired *goons* of your enemy, the Mercenaries. ( Don't worry: you can hire *goons* yourself! ) Oh, and you will also be defending against the endless horde of Demons which are constantly spawning and becoming progressively stronger, until they completely outscale your available space to place defenses! Look on the bright side though, Demons will also be outscaling your enemy.

Defenses and Mercenaries don't come cheap, though. You will need to make money by placing a special type of Tower, the House. If you've ever played Plants vs. Zombies, these are kind of like sunflowers in that game. Be careful not to build too many Houses, though. **With each Tower you build, towers of that type will become 25% more expensive**.

## Main Game Loop

ApocaWarlords uses *simultaneous turns*. This means that each turn, both players select their actions at the same time, without communication. After both players select their actions, the game world is updated. This repeats until the game ends.

## Player Action

Every turn, each player can decide to do any combination of the following, assuming the decision is valid (more on validity below):
1. Buy a Mercenary
2. Build *or* Destroy a Tower, but not both!
3. Provoke the Demons

An invalid action will cause the player who made it to lose their turn ( they will do nothing ).

### Buying Mercenaries
When either player buys a Mercenary, they must decide which direction the Mercenary starts out from. Mercenaries cost $20.

Depending on the map, different directions will be available. For all maps, there will be at least 2 Mercenary starting directions available per player, and at most 4. Maps are symmetric as to make them fair, so both players will always have the same amount of directions to choose from.

A purchase is valid if the following two conditions are true:
1. There is a Path Tile 1 unit away from the purchasing player's base in the direction which was selected. ( Mercenaries can only walk on path tiles )
2. The purchasing player has $20.

A valid Mercenary purchase will cause $20 to be subtracted from the purchasing player's total money and cause a Mercenary to immediately spawn in the direction selected. Buying Mercenaries happens before buying Towers and before provoking the Demons, so it is possible for a Mercenary purchase to make a player too poor to finish everything they decided to do in a single turn.

### Building/Destroying Towers

When either player builds a Tower, they must decide what type of tower to build and where to build it. Available spaces 


### Provoking the Demons
