import os
import platform
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from threading import BoundedSemaphore


RUNNER_LANGUAGE = "cpp17"
MAX_CODE_BYTES = 64 * 1024
MAX_STDIN_BYTES = 16 * 1024
MAX_OUTPUT_BYTES = 16 * 1024
MAX_COMPILE_FILE_BYTES = 16 * 1024 * 1024
COMPILE_TIMEOUT_SECONDS = 8
RUN_TIMEOUT_SECONDS = 2
CPU_TIMEOUT_SECONDS = 3
MEMORY_LIMIT_MB = 256
COMPILE_NPROC_LIMIT = 64
RUN_NPROC_LIMIT = 16
MAX_CONCURRENCY = int(os.environ.get("NOI_CODE_RUNNER_MAX_CONCURRENCY", "4"))
ACQUIRE_TIMEOUT_SECONDS = 2

_runner_semaphore = BoundedSemaphore(MAX_CONCURRENCY)


@dataclass
class RunnerHealth:
    available: bool
    message: str
    language: str = RUNNER_LANGUAGE
    sandbox: str = ""

    def to_dict(self) -> dict:
        payload = {
            "available": self.available,
            "language": self.language,
            "message": self.message,
            "limits": runner_limits(),
        }
        if self.sandbox:
            payload["sandbox"] = self.sandbox
        return payload


def runner_limits() -> dict:
    return {
        "memory_mb": MEMORY_LIMIT_MB,
        "compile_timeout_seconds": COMPILE_TIMEOUT_SECONDS,
        "run_timeout_seconds": RUN_TIMEOUT_SECONDS,
        "max_concurrency": MAX_CONCURRENCY,
    }


def get_runner_health() -> RunnerHealth:
    if platform.system() != "Linux":
        return RunnerHealth(
            available=False,
            message="当前服务器暂不支持代码运行，仍然可以把代码发给 AIChat 讨论。",
        )
    if not shutil.which("g++"):
        return RunnerHealth(
            available=False,
            message="当前服务器缺少 C++ 编译器，暂不支持代码运行。",
        )
    if not shutil.which("firejail"):
        return RunnerHealth(
            available=False,
            message="当前服务器暂不支持代码运行，仍然可以把代码发给 AIChat 讨论。",
        )
    return RunnerHealth(
        available=True,
        message="代码运行环境可用",
        sandbox="firejail",
    )


def _bytes_len(text: str) -> int:
    return len((text or "").encode("utf-8"))


def _normalize_output(text: str) -> str:
    return (text or "").replace("\r\n", "\n").replace("\r", "\n")


def compare_expected_output(stdout: str, expected_output: str) -> tuple[bool | None, str]:
    if expected_output is None or expected_output == "":
        return None, ""
    normalized_stdout = _normalize_output(stdout)
    normalized_expected = _normalize_output(expected_output)
    if normalized_stdout == normalized_expected:
        return True, "输出一致"
    if normalized_stdout.rstrip() == normalized_expected.rstrip():
        return True, "主要内容一致，但末尾空白不同"
    return False, "输出不一致"


def _truncate_output(text: str) -> tuple[str, bool]:
    encoded = (text or "").encode("utf-8")
    if len(encoded) <= MAX_OUTPUT_BYTES:
        return text or "", False
    truncated = encoded[:MAX_OUTPUT_BYTES].decode("utf-8", errors="ignore")
    return truncated + "\n... 输出过长，已截断", True


def _base_firejail_command(tmpdir: Path, *, nproc_limit: int, fsize_limit: int) -> list[str]:
    firejail = shutil.which("firejail") or "firejail"
    return [
        firejail,
        "--quiet",
        "--noprofile",
        "--net=none",
        f"--private={tmpdir}",
        f"--rlimit-as={MEMORY_LIMIT_MB * 1024 * 1024}",
        f"--rlimit-cpu={CPU_TIMEOUT_SECONDS}",
        f"--rlimit-fsize={fsize_limit}",
        f"--rlimit-nproc={nproc_limit}",
        "--rlimit-nofile=32",
    ]


def _safe_completed_process(
    command: list[str],
    *,
    cwd: Path,
    stdin: str = "",
    timeout: int,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(cwd),
        shell=False,
    )


def run_cpp17_sample(code: str, stdin: str = "", expected_output: str = "") -> dict:
    if _bytes_len(code) > MAX_CODE_BYTES:
        return _result("invalid_request", "代码太长了，请先保留关键部分再运行。")
    if _bytes_len(stdin) > MAX_STDIN_BYTES:
        return _result("invalid_request", "样例输入太长了，请缩短后再运行。")

    health = get_runner_health()
    if not health.available:
        return _result("runner_unavailable", health.message)

    if not _runner_semaphore.acquire(timeout=ACQUIRE_TIMEOUT_SECONDS):
        return _result("busy", "当前运行人数较多，请稍后再试。")

    started = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory(prefix="noi-code-runner-") as tmp:
            tmpdir = Path(tmp)
            source_path = tmpdir / "main.cpp"
            binary_path = tmpdir / "main"
            source_path.write_text(code, encoding="utf-8")

            compile_command = [
                *_base_firejail_command(tmpdir, nproc_limit=COMPILE_NPROC_LIMIT, fsize_limit=MAX_COMPILE_FILE_BYTES),
                "g++",
                "main.cpp",
                "-std=c++17",
                "-O2",
                "-pipe",
                "-o",
                "main",
            ]
            try:
                compiled = _safe_completed_process(
                    compile_command,
                    cwd=tmpdir,
                    timeout=COMPILE_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                return _result("timeout", "编译超时，请检查代码是否包含异常复杂的模板或宏。", elapsed_ms=started)

            compile_output, compile_truncated = _truncate_output(
                "\n".join(part for part in (compiled.stdout, compiled.stderr) if part)
            )
            if compiled.returncode != 0:
                return _result(
                    "compile_error",
                    "编译失败，请检查语法错误（原始错误信息如下）。",
                    compile_output=compile_output,
                    elapsed_ms=started,
                    output_limited=compile_truncated,
                )

            if not binary_path.exists():
                return _result(
                    "runtime_error",
                    "编译没有生成可运行文件，请检查代码。",
                    compile_output=compile_output,
                    elapsed_ms=started,
                )

            run_command = [*_base_firejail_command(tmpdir, nproc_limit=RUN_NPROC_LIMIT, fsize_limit=MAX_OUTPUT_BYTES), "./main"]
            try:
                executed = _safe_completed_process(
                    run_command,
                    cwd=tmpdir,
                    stdin=stdin or "",
                    timeout=RUN_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                return _result("timeout", "运行超时，请检查是否有死循环或复杂度过高。", elapsed_ms=started)

            stdout, stdout_limited = _truncate_output(executed.stdout or "")
            stderr, stderr_limited = _truncate_output(executed.stderr or "")
            output_limited = stdout_limited or stderr_limited
            matched_expected, compare_message = compare_expected_output(stdout, expected_output or "")
            status = "ok" if executed.returncode == 0 and not output_limited else "output_limit" if output_limited else "runtime_error"
            message = compare_message or ("运行完成" if status == "ok" else "运行时出错，请查看错误信息。")
            return _result(
                status,
                message,
                stdout=stdout,
                stderr=stderr,
                compile_output=compile_output,
                elapsed_ms=started,
                exit_code=executed.returncode,
                matched_expected=matched_expected,
                output_limited=output_limited,
            )
    finally:
        _runner_semaphore.release()


def _result(
    status: str,
    message: str,
    *,
    stdout: str = "",
    stderr: str = "",
    compile_output: str = "",
    elapsed_ms: float | None = None,
    exit_code: int | None = None,
    matched_expected: bool | None = None,
    output_limited: bool = False,
) -> dict:
    elapsed = 0
    if elapsed_ms is not None:
        elapsed = int((time.perf_counter() - elapsed_ms) * 1000)
    return {
        "status": status,
        "message": message,
        "stdout": stdout,
        "stderr": stderr,
        "compile_output": compile_output,
        "elapsed_ms": elapsed,
        "exit_code": exit_code,
        "matched_expected": matched_expected,
        "output_limited": output_limited,
    }
