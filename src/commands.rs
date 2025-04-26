use serde::Deserialize;
use schemars::JsonSchema;
use crate::game_state::{GameState, TowerKind, Direction};

// This file contains the logic for validating all agent commands
// Agents communicate via JSON, so all commands are deserializable from JSON

pub trait GameCommand {
    fn validate(&self, state: &GameState) -> Result<(), String>;
    fn apply(&self, state: &mut GameState) -> Result<(), String>;
}

#[derive(Deserialize, JsonSchema)]
pub struct SetTeamNameCommand {
    team_name: String
}

#[derive(Deserialize, JsonSchema)]
pub struct BuyBuilderCommand {
    builders_to_buy: u32
}

#[derive(Deserialize, JsonSchema)]
pub enum CreateOrDestroyTower {
    Create { tower_type: TowerKind },
    Destroy,
}

#[derive(Deserialize, JsonSchema)]
pub struct BuilderActionCommand {
    target_x: i32,
    target_y: i32,
    create_or_destroy: CreateOrDestroyTower,
}

#[derive(Deserialize, JsonSchema)]
pub struct BuyMercenariesCommand {
    direction: Direction
}