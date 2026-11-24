import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProcessResult:
    ok: bool
    stdout: str
    stderr: str
    returncode: int


def _run(cmd: list[str], cwd: Path | None = None) -> ProcessResult:
    try:
        r = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=600,
        )
        return ProcessResult(r.returncode == 0, r.stdout, r.stderr, r.returncode)
    except FileNotFoundError as e:
        return ProcessResult(False, "", f"Executable not found: {e}", -1)
    except subprocess.TimeoutExpired:
        return ProcessResult(False, "", "Timeout (600 s)", -1)
    except Exception as e:
        return ProcessResult(False, "", f"Error: {e}", -1)


def decompile(champollion: str, pex: Path, out_dir: Path) -> ProcessResult:
    """Champollion CLI: champollion <input.pex> -p <output_dir>"""
    return _run([champollion, str(pex), "-p", str(out_dir)])


def compile_psc(
    compiler: str,
    compiler_type: str,
    psc: Path,
    out_dir: Path,
    import_dir: str,
    game: str,
) -> ProcessResult:
    """
    Compile .psc → .pex.

    Caprica:         <compiler> <input.psc> --output=<dir> [--import=<dir>] --game=<game>
    PapyrusCompiler: <compiler> <input.psc> -i=<imports> -o=<output.pex> -f=Starfield
    """
    if compiler_type == "caprica":
        cmd = [compiler, str(psc), f"--output={out_dir}"]
        if import_dir:
            cmd.append(f"--import={import_dir}")
        cmd.append(f"--game={game}")
        return _run(cmd)

    # PapyrusCompiler (Creation Kit, Skyrim/FO4/Starfield)
    # -o je VÝSTUPNÝ SÚBOR (.pex), nie priečinok!
    output_pex = out_dir / (psc.stem + ".pex")
    cmd = [compiler, str(psc)]
    if import_dir:
        cmd.append(f"-i={import_dir}")
    cmd.append(f"-o={output_pex}")
    cmd.append("-f=Starfield")
    return _run(cmd)