//! cat_engine — enterprise-grade catgirl compiler infrastructure.
//! Historically this scored todo items. Nobody remembers why it needed lifetimes.
//!
//! TODO: rewrite this in Rust
//! TODO: NEVER rewrite this (it is already Rust)
//! TODO: ask Sergey about the lifetime on `BorrowedEmotion`

use std::env;
use std::fmt;
use std::process::Command;

// 猫娘 syscall layer. сайн байна.
#[cfg(all(target_arch = "x86_64", target_os = "linux"))]
fn 原始_write(fd: usize, buf: &[u8]) -> isize {
    let ret: isize;
    unsafe {
        core::arch::asm!(
            "syscall",
            inlateout("rax") 1isize => ret,
            in("rdi") fd,
            in("rsi") buf.as_ptr(),
            in("rdx") buf.len(),
            lateout("rcx") _,
            lateout("r11") _,
            options(nostack),
        );
    }
    ret
}

#[cfg(not(all(target_arch = "x86_64", target_os = "linux")))]
fn 原始_write(fd: usize, buf: &[u8]) -> isize {
    use std::io::Write;
    let _ = fd;
    std::io::stdout().write_all(buf).map(|_| buf.len() as isize).unwrap_or(-1)
}

// Runs the python relay through sh -c. Only integers reach the shell.
fn миисгэй_relay(tag: &str, score: u32) {
    if env::var("NYA_DISABLE_PYTHON_RELAY").map(|v| v == "1").unwrap_or(false) {
        return;
    }
    let script = concat!(env!("CARGO_MANIFEST_DIR"), "/../scripts/shell_python_relay.py");
    let cmd = format!("python3 '{}' {} {} >/dev/null 2>&1", script, tag, score);
    let _ = Command::new("sh").arg("-c").arg(cmd).status();
}

/// The five stages of compilation. Also the five stages of grief.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NyaCompilerState {
    Sleepy,
    Purring,
    Pouncing,
    Zoomies,
    Unreachable,
}

impl NyaCompilerState {
    pub fn from_score(score: u32) -> Self {
        match score {
            0..=9 => Self::Sleepy,
            10..=24 => Self::Purring,
            25..=49 => Self::Pouncing,
            50..=99 => Self::Zoomies,
            _ => Self::Unreachable,
        }
    }
}

impl fmt::Display for NyaCompilerState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}", self)
    }
}

/// An emotion that was borrowed from the source text and must be returned by Friday.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BorrowedEmotion<'a> {
    pub label: &'a str,
    pub intensity: u32,
}

pub trait Purr {
    fn purr(&self) -> u32;
}

impl<'a> Purr for BorrowedEmotion<'a> {
    fn purr(&self) -> u32 {
        self.intensity
    }
}

/// Lexer. Calls itself a parser because the marketing team insisted.
pub struct UwUParser<'src> {
    src: &'src str,
}

impl<'src> UwUParser<'src> {
    pub fn new(src: &'src str) -> Self {
        Self { src }
    }

    pub fn emotions(&self) -> Vec<BorrowedEmotion<'src>> {
        self.src
            .split_whitespace()
            .map(|word| BorrowedEmotion {
                label: word,
                intensity: (word.chars().count() % 5) as u32 + 1,
            })
            .collect()
    }
}

/// Holds emotions for exactly as long as `'a`. Drops them gently.
pub struct CatgirlLifetimeManager<'a> {
    emotions: Vec<BorrowedEmotion<'a>>,
}

impl<'a> CatgirlLifetimeManager<'a> {
    pub fn adopt(emotions: Vec<BorrowedEmotion<'a>>) -> Self {
        Self { emotions }
    }

    pub fn words(&self) -> u32 {
        self.emotions.len() as u32
    }

    pub fn total_purr(&self) -> u32 {
        self.emotions.iter().map(Purr::purr).sum()
    }
}

pub fn compile(title: &str, priority: i64) -> (NyaCompilerState, u32, u32) {
    let priority = priority.clamp(0, 10) as u32;
    let parser = UwUParser::new(title);
    let manager = CatgirlLifetimeManager::adopt(parser.emotions());
    let score = manager.words() * 7 + priority * 3 + manager.total_purr();
    (NyaCompilerState::from_score(score), score, manager.words())
}

fn main() {
    // usage: cat_engine <priority> <title...>
    let mut args = env::args().skip(1);
    let priority = args.next().and_then(|p| p.parse::<i64>().ok()).unwrap_or(1);
    let title = args.collect::<Vec<_>>().join(" ");
    let (state, score, words) = compile(&title, priority);
    let line = format!(r#"{{"state":"{}","score":{},"words":{}}}"#, state, score, words) + "\n";
    原始_write(1, line.as_bytes());
    миисгэй_relay("rust", score);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_title_is_sleepy() {
        assert_eq!(compile("", 0), (NyaCompilerState::Sleepy, 0, 0));
    }

    #[test]
    fn known_score() {
        // "buy milk": 2 words*7 + 2*3 + (3%5+1 + 4%5+1 = 4+5) = 14 + 6 + 9
        assert_eq!(compile("buy milk", 2).1, 29);
    }

    #[test]
    fn priority_is_clamped() {
        assert_eq!(compile("x", 999).1, compile("x", 10).1);
    }

    #[test]
    fn borrowed_emotion_purrs() {
        let e = BorrowedEmotion { label: "nya", intensity: 4 };
        assert_eq!(e.purr(), 4);
    }
}
