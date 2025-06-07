use std::io;

/// Compress a slice of u64 integers using a simple variable-length encoding.
/// Each integer is encoded in little-endian 7-bit groups with the MSB as a
/// continuation flag.
pub fn compress(nums: &[u64]) -> Vec<u8> {
    let mut buf = Vec::new();
    for &n in nums {
        let mut n = n;
        loop {
            let mut byte = (n & 0x7F) as u8;
            n >>= 7;
            if n != 0 {
                byte |= 0x80;
                buf.push(byte);
            } else {
                buf.push(byte);
                break;
            }
        }
    }
    buf
}

/// Decompress a slice of bytes into u64 integers using the same variable-length
/// encoding used in `compress`.
pub fn decompress(data: &[u8]) -> io::Result<Vec<u64>> {
    let mut result = Vec::new();
    let mut value = 0u64;
    let mut shift = 0;
    for &byte in data {
        let part = (byte & 0x7F) as u64;
        value |= part << shift;
        if (byte & 0x80) == 0 {
            result.push(value);
            value = 0;
            shift = 0;
        } else {
            shift += 7;
            if shift >= 64 {
                return Err(io::Error::new(io::ErrorKind::InvalidData, "overflow"));
            }
        }
    }
    if shift != 0 {
        return Err(io::Error::new(io::ErrorKind::UnexpectedEof, "truncated data"));
    }
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roundtrip() {
        let nums = vec![0, 1, 127, 128, 255, 256, u64::MAX];
        let encoded = compress(&nums);
        let decoded = decompress(&encoded).unwrap();
        assert_eq!(nums, decoded);
    }
}
