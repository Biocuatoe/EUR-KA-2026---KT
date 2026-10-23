"""Start the registered 'eureka-2026' Jupyter kernel and run code inside it.

Confirms that the kernelspec is discoverable, that it launches the project .venv
interpreter, and that the kernel sees the D: runtime paths. Prints JSON; exit 1 on failure.
"""

import json
import os
import sys

from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client.manager import start_new_kernel

KERNEL = "eureka-2026"
ROOT = os.path.normcase(os.environ.get("EUREKA_ROOT", r"D:\EUREKA-2026"))
PROBE = (
    "import json, os, sys, tempfile, matplotlib, numpy\n"
    "print(json.dumps({'executable': sys.executable, 'prefix': sys.prefix,"
    " 'numpy': numpy.__version__, 'mplconfigdir': matplotlib.get_configdir(),"
    " 'tempdir': tempfile.gettempdir(), 'ipythondir': os.environ.get('IPYTHONDIR')}))"
)


def main() -> int:
    spec = KernelSpecManager().get_kernel_spec(KERNEL)
    km, kc = start_new_kernel(kernel_name=KERNEL, startup_timeout=120)
    chunks = []
    try:
        reply = kc.execute_interactive(
            PROBE,
            timeout=120,
            output_hook=lambda msg: (
                chunks.append(msg["content"].get("text", ""))
                if msg["msg_type"] == "stream"
                else None
            ),
        )
        status = reply["content"]["status"]
    finally:
        kc.stop_channels()
        km.shutdown_kernel(now=True)

    probe = json.loads("".join(chunks)) if status == "ok" else {}
    paths = [spec.resource_dir, spec.argv[0]] + [
        probe.get(k) or "" for k in ("executable", "mplconfigdir", "tempdir", "ipythondir")
    ]
    outside = [p for p in paths if not os.path.normcase(p).startswith(ROOT)]
    ok = status == "ok" and not outside
    print(
        json.dumps(
            {
                "ok": ok,
                "kernel": KERNEL,
                "resource_dir": spec.resource_dir,
                "argv0": spec.argv[0],
                "execute_status": status,
                "probe": probe,
                "paths_outside_root": outside,
            },
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
