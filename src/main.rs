mod commands;
mod constants;
mod game_state;

use std::path::Path;
use std::fs::File;

fn main() {
    let visualizer_output_filepath = Path::new("visualizer.out");
    let mut visualizer_output_file = match File::create(&visualizer_output_filepath) {
        Err(why) => panic!("couldn't create visualizer output file: {}", why),
        Ok(file) => file,
    };
}
