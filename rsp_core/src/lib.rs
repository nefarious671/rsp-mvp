//! Minimal RSP envelope codec v0.1

/// An RSP envelope that holds a single token (string) for now.
#[derive(Debug, PartialEq, Eq)]
pub struct Envelope {
    pub token: String,
}

impl Envelope {
    /// Encode into `[len(u32 LE)] + token bytes`.
    pub fn encode(&self) -> Vec<u8> {
        let mut out = Vec::with_capacity(4 + self.token.len());
        let len = self.token.len() as u32;
        out.extend_from_slice(&len.to_le_bytes());
        out.extend_from_slice(self.token.as_bytes());
        out
    }

    /// Decode from the simple length-prefixed format.
    pub fn decode(bytes: &[u8]) -> anyhow::Result<Self> {
        if bytes.len() < 4 {
            anyhow::bail!("buffer too small");
        }
        let len = u32::from_le_bytes(bytes[0..4].try_into().unwrap()) as usize;
        if bytes.len() < 4 + len {
            anyhow::bail!("truncated payload");
        }
        let token = String::from_utf8(bytes[4..4 + len].to_vec())?;
        Ok(Self { token })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn round_trip() {
        let env = Envelope { token: "fire".into() };
        let enc = env.encode();
        let dec = Envelope::decode(&enc).unwrap();
        assert_eq!(env, dec);
    }
}
