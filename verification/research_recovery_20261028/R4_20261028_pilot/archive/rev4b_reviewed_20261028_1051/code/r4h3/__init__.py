"""R4 H3 pilot implementation (protocol ../R4_20261028_preflight/03_R4_protocol_v1.md, H3 only).

Importing this package disables bytecode writing so that importing the frozen R3 library never
creates __pycache__ inside the R3 tree.
"""

import sys

sys.dont_write_bytecode = True

SCHEMA_VERSION = "r4h3-trace-v2"          # v2 adds the closure integrators (change VC-08); v1 stays readable
READABLE_SCHEMAS = ("r4h3-trace-v1", "r4h3-trace-v2")
