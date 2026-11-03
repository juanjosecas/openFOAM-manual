"""Ejecución local de OpenFOAM con Docker SDK; logs persistentes en el caso."""
from dataclasses import dataclass
from pathlib import Path
import codecs
import math
import os
import shlex
import time
import uuid
import warnings

import docker


@dataclass(frozen=True)
class FoamResult:
    command: tuple[str, ...]
    case_dir: Path
    log_path: Path
    elapsed_seconds: float
    returncode: int
    oom_killed: bool = False


class FoamRunError(RuntimeError):
    def __init__(self, message, result):
        super().__init__(message)
        self.result = result


def foam_run(command, timeout=600, *, case_dir, repo_dir,
             image="opencfd/openfoam-run:2406",
             bashrc="/usr/lib/openfoam/openfoam2406/etc/bashrc",
             verbose=True, require_case=True, client=None):
    """Ejecutar un comando sin interpretar operadores de shell.

    Monta únicamente case_dir. El límite se comprueba por sondeo, incluso sin
    salida; las peticiones al daemon tienen su propio timeout de 10 segundos.
    La limpieza puede prolongar el retorno después del límite de ejecución.
    Requiere un daemon local con acceso a las mismas rutas del notebook.
    """
    args = shlex.split(command) if isinstance(command, str) else list(command)
    if not args or any(not isinstance(a, str) or '\0' in a for a in args) or not args[0].strip():
        raise ValueError("command debe contener un ejecutable válido")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout debe ser positivo y finito")
    repo = Path(repo_dir).expanduser().resolve(strict=True)
    case = Path(case_dir).expanduser().resolve(strict=True)
    if not repo.is_dir() or not case.is_dir():
        raise NotADirectoryError("repo_dir y case_dir deben ser directorios")
    if not case.is_relative_to(repo):
        raise ValueError("case_dir debe estar dentro de repo_dir")
    if require_case and not (case / "system/controlDict").is_file():
        raise FileNotFoundError(case / "system/controlDict")

    name = f"foam-notebook-{uuid.uuid4().hex}"
    log_path = case / f"log.{name}"
    # El archivo es exclusivo y pertenece al usuario del notebook.
    with log_path.open("xb"):
        pass
    script = (
        'foam_rc="$1"; foam_log="$2"; shift 2; '
        'exec >"$foam_log" 2>&1; '
        'source "$foam_rc" "" >/dev/null && '
        'cd /case && exec "$@"'
    )
    owned_client = client is None
    engine = None
    container = None
    started = time.monotonic()
    print(f"[OpenFOAM] {shlex.join(args)}\nCaso: {case}\nLog: {log_path}", flush=True)
    try:
        engine = client if client is not None else docker.from_env(timeout=10)
        local_image = engine.images.get(image)  # No descarga imágenes.
        container = engine.containers.create(
            local_image.id,
            command=["-c", script, "foam-run", bashrc,
                     f"/case/{log_path.name}", *args],
            name=name,
            user=f"{os.getuid()}:{os.getgid()}",
            volumes={str(case): {"bind": "/case", "mode": "rw,z"}},
            network_mode="none", cap_drop=["ALL"],
            security_opt=["no-new-privileges"], init=True,
            auto_remove=False,
        )
        container.start()
        with log_path.open("rb") as reader:
            decoder = codecs.getincrementaldecoder("utf-8")("replace")

            def show_output():
                # Límite por pasada para no retrasar el control del timeout.
                chunk = reader.read(256 * 1024)
                if verbose and chunk:
                    print(decoder.decode(chunk), end="", flush=True)
                return bool(chunk)

            while True:
                show_output()
                container.reload()
                state = container.attrs["State"]
                if state["Status"] in {"exited", "dead"}:
                    break
                if time.monotonic() - started >= timeout:
                    raise TimeoutError(f"Límite de {timeout:g} s superado. Log: {log_path}")
                time.sleep(0.1)
            while show_output():
                pass
            if verbose:
                print(decoder.decode(b"", final=True), end="", flush=True)

        result = FoamResult(tuple(args), case, log_path,
                            time.monotonic() - started,
                            state["ExitCode"], state.get("OOMKilled", False))
        if result.returncode != 0 or state.get("Error"):
            raise FoamRunError(
                f"Código {result.returncode}; OOMKilled={result.oom_killed}; "
                f"error={state.get('Error', '')!r}. Log: {log_path}", result)
        print(f"\n[OK] {result.elapsed_seconds:.2f} s", flush=True)
        return result
    except KeyboardInterrupt:
        print(f"\n[Interrumpido] Log conservado: {log_path}", flush=True)
        raise
    finally:
        try:
            if container is not None:
                container.remove(force=True)
        except docker.errors.NotFound:
            pass
        except Exception as exc:
            # No ocultar el error original si el daemon deja de responder.
            warnings.warn(f"No se pudo eliminar {name}: {exc}", RuntimeWarning)
        finally:
            if owned_client and engine is not None:
                engine.close()
