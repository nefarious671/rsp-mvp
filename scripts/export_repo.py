#!/usr/bin/env python3
"""Export repository root as a zip file excluding anything matched by .gitignore.

This script uses `git` to determine the repository root and to assemble a list of
files to include (tracked files + untracked but not ignored files). It then
writes those files into a zip archive preserving relative paths.

Usage examples:
  python scripts/export_repo.py                 # creates YYYYMMDD-HHMMSS.zip in repo root
  python scripts/export_repo.py -o /tmp/repo.zip
  python scripts/export_repo.py --dry-run

Requirements: git must be installed and this must be run inside a git repository.
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def run_git(args, cwd: Path) -> bytes:
    return subprocess.check_output(["git", *args], cwd=str(cwd))


def repo_root_from_git(cwd: Path) -> Path:
    try:
        out = run_git(["rev-parse", "--show-toplevel"], cwd)
        return Path(out.decode().strip())
    except subprocess.CalledProcessError:
        raise RuntimeError("Not inside a git repository or git is not available")


def gather_files(repo_root: Path, include_untracked: bool = True) -> list[Path]:
    files: list[Path] = []

    # tracked files
    try:
        tracked = run_git(["ls-files", "-z"], repo_root)
        if tracked:
            for p in tracked.split(b"\x00"):
                if not p:
                    continue
                files.append(repo_root / Path(p.decode()))
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Failed to list tracked files from git: %s" % e)

    # untracked but not ignored
    if include_untracked:
        try:
            untracked = run_git(["ls-files", "--others", "--exclude-standard", "-z"], repo_root)
            if untracked:
                for p in untracked.split(b"\x00"):
                    if not p:
                        continue
                    files.append(repo_root / Path(p.decode()))
        except subprocess.CalledProcessError as e:
            # non-fatal; continue with tracked
            print("Warning: failed to list untracked files: %s" % e, file=sys.stderr)

    # filter out directories (keep only files)
    real_files = [p for p in files if p.is_file()]
    # deduplicate while preserving order
    seen = set()
    unique_files: list[Path] = []
    for p in real_files:
        key = p.resolve()
        if key not in seen:
            seen.add(key)
            unique_files.append(p)
    return unique_files


def make_zip(repo_root: Path, files: list[Path], output: Path, dry_run: bool = False) -> None:
    if dry_run:
        print(f"Dry run: would archive {len(files)} files. Sample:")
        for p in files[:30]:
            print("  ", p.relative_to(repo_root))
        return

    # Ensure output parent exists
    output.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(output, "w", compression=ZIP_DEFLATED) as zf:
        for p in files:
            arcname = p.relative_to(repo_root).as_posix()
            zf.write(p, arcname)

    print(f"Wrote {output} ({shutil.os.path.getsize(output)} bytes)")


def default_output_name(repo_root: Path) -> Path:
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{repo_root.name}-{stamp}.zip"
    return repo_root / name


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export repo root as zip excluding files in .gitignore.")
    p.add_argument("-o", "--output", help="Output zip path (default: repo-root-YYYYMMDD-HHMMSS.zip)")
    p.add_argument("--repo-root", "-r", help="Repository root (auto-detected by git)")
    p.add_argument("--no-untracked", dest="include_untracked", action="store_false", help="Do not include untracked files")
    p.add_argument("--dry-run", action="store_true", help="Show what would be archived, do not create zip")
    p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    cwd = Path.cwd()

    # determine repo root
    repo_root = Path(args.repo_root) if args.repo_root else None
    try:
        if repo_root:
            repo_root = repo_root.resolve()
        else:
            repo_root = repo_root_from_git(cwd)
    except RuntimeError as e:
        print("Error:", e, file=sys.stderr)
        return 2

    files = gather_files(repo_root, include_untracked=args.include_untracked)

    if args.verbose:
        print(f"Found {len(files)} files to include")

    output = Path(args.output) if args.output else default_output_name(repo_root)

    make_zip(repo_root, files, output, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
