use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use std::{
    collections::{HashMap, VecDeque},
    fmt,
};
use strum_macros::EnumString;

// This file contains all definitions for game state data structures
// Game state is packaged into one big struct, serialized, then sent to agents via JSON
// Serialization is done via the serde library

#[derive(PartialEq, Eq, Hash, Clone, Copy, Serialize, Deserialize, EnumString, JsonSchema)]
pub enum Direction {
    N,
    NE,
    E,
    SE,
    S,
    SW,
    W,
    NW,
}

#[derive(PartialEq, Eq, Hash, Clone, Copy, Serialize, EnumString)]
pub enum TeamColor {
    Red,
    Blue,
}

// Some polymorphism.
#[derive(PartialEq, Eq, Hash, Serialize, Clone)]
pub enum Entity {
    PlayerBase(PlayerBase),
    Enemy(Enemy),
    Mercenary(Mercenary),
    EnemySpawner(EnemySpawner),
    Tower(Tower),
}

#[derive(PartialEq, Eq, Hash, Clone, Copy, Serialize, EnumString)]
pub enum FloorTile {
    RedTerritory,
    BlueTerritory,
    Path,
}

#[derive(PartialEq, Eq, Hash, Clone, Copy, Serialize, Deserialize)]
pub struct Position {
    x: i32,
    y: i32,
}

// Position should be serialized like (2,2)
impl fmt::Display for Position {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({},{})", self.x, self.y)
    }
}

#[derive(Serialize, Deserialize, Clone, PartialEq, Eq, Hash, JsonSchema, EnumString)]
pub enum TowerKind {
    Crossbow,
    Cannon,
    Minigun,
    House,
}

#[derive(Serialize, Clone, PartialEq, Eq, Hash)]
pub struct TowerStats {
    tower_kind: TowerKind,
    damage: u32,
    cost: u32,
    range: u32,
    reload_turns: u32,
    initial_hp: u32,
}

#[derive(Serialize, Clone, PartialEq, Eq, Hash)]
pub struct Tower {
    uid: u64,
    position: Position,
    tower_stats: TowerStats,
    reload_turns_left: u32,
    team_color: TeamColor,
}

#[derive(Serialize, Clone, PartialEq, Eq, Hash)]
pub struct PlayerBase {
    uid: u64,
    position: Position,
    hp: u32,
    mercenaries_queued: VecDeque<Position>,
    team_color: TeamColor,
}

#[derive(Serialize, Clone, PartialEq, Eq, Hash)]
pub struct Mercenary {
    uid: u64,
    position: Position,
    hp: u32,
    team_color: TeamColor,
    path_to_enemy: VecDeque<Position>,
    // If two mercenaries on the same team are next to each other, one is in front and one is behind
    // We want them both to move in the same turn, but the front mercenary must move first, even if
    // the back mercenary gets updated first. We use can_move_this_turn to handle this logic.
    can_move_this_turn: bool,
}

#[derive(Serialize, Clone, PartialEq, Eq, Hash)]
pub struct Enemy {
    uid: u64,
    position: Position,
    hp: u32,
    path_to_target: VecDeque<Position>,
}

#[derive(Serialize, Clone, PartialEq, Eq, Hash)]
pub struct EnemySpawner {
    uid: u64,
    position: Position,
    reload_time_left: u32,
    enemies_queued: u32,
    target: TeamColor,
    switch_target: bool,
}

#[derive(Serialize)]
pub struct PlayerState {
    team_name: String,
    builder_count: u32,
    money: u32,
}

#[derive(Serialize)]
pub struct GameState {
    turns_progressed: u32,
    victory: Option<TeamColor>,
    player_state_red: PlayerState,
    player_state_blue: PlayerState,
    floor_tiles: HashMap<Position, FloorTile>,
    position_to_entity: HashMap<Position, u128>,
    entities: HashMap<u128, Entity>,
}
