use clap::{Parser, Subcommand};
use rsp_core::Envelope;
use hex::{FromHex, ToHex};

#[derive(Parser)]
struct Cli {
    #[command(subcommand)]
    command: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Encode a token to hex bytes
    Encode { token: String },
    /// Decode hex bytes back to a token
    Decode { hex: String },
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Cmd::Encode { token } => {
            let env = Envelope { token };
            println!("{}", env.encode().encode_hex::<String>());
        }
        Cmd::Decode { hex } => {
            let bytes = Vec::<u8>::from_hex(hex)?;
            let env = Envelope::decode(&bytes)?;
            println!("{}", env.token);
        }
    }
    Ok(())
}
