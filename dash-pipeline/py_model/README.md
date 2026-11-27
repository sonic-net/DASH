# Python model (py_model) for DASH pipeline Developer Guide

This folder contains the Python "py_model" implementation of the DASH pipeline used for local testing, artifact generation, and a lightweight P4Runtime-compatible control plane. It mirrors the P4 pipeline logic in Python for inspection, unit tests and for producing P4 mirrored artifacts.

Contents
- Core model and entrypoints
  - [`py_model/dash_py_v1model.py`](py_model/dash_py_v1model.py) — contains the Python model entrypoint.
  - [`py_model/main_dash.py`](py_model/main_dash.py) — CLI/runner used by `make pymodel` and `run.sh`.
- Control plane (gRPC / P4Runtime helper)
  - [`py_model/control_plane/grpc_server.py`](py_model/control_plane/grpc_server.py) — lightweight P4Runtime server skeleton including [`grpc_server.P4RuntimeServicer`](py_model/control_plane/grpc_server.py), helpers such as [`grpc_server.populate_tables_actions_ids`](py_model/control_plane/grpc_server.py) and [`grpc_server.pretty_print_proto`](py_model/control_plane/grpc_server.py).
  - [`py_model/control_plane/control_plane.py`](py_model/control_plane/control_plane.py) — control plane helpers and mappings used by the server.
- Data plane implementation (pipeline stages & routing)
  - Pipeline orchestration: [`py_model/data_plane/dash_pipeline.py`](py_model/data_plane/dash_pipeline.py).
  - Inbound/outbound flows: [`py_model/data_plane/dash_inbound.py`](py_model/data_plane/dash_inbound.py) (class `inbound`) and [`py_model/data_plane/dash_outbound.py`](py_model/data_plane/dash_outbound.py) (class `outbound`).
  - Routing & mapping stages: e.g. [`py_model/data_plane/stages/outbound_routing.py`](py_model/data_plane/stages/outbound_routing.py) (class `outbound_routing_stage`, method `apply`) and [`py_model/data_plane/stages/outbound_mapping.py`](py_model/data_plane/stages/outbound_mapping.py) (class `outbound_mapping_stage`, table `ca_to_pa`).
  - Per-packet routing actions grouped in [`py_model/data_plane/stages/routing_action_apply.py`](py_model/data_plane/stages/routing_action_apply.py).
  - Headers, metadata and routing types: [`py_model/data_plane/dash_headers.py`](py_model/data_plane/dash_headers.py), [`py_model/data_plane/dash_metadata.py`](py_model/data_plane/dash_metadata.py) and [`py_model/data_plane/dash_routing_types.py`](py_model/data_plane/dash_routing_types.py).
- Libraries (runtime support)
  - Table and table helpers: [`py_model/libs/__table.py`](py_model/libs/__table.py)
  - Common runtime vars and metadata: [`py_model/libs/__vars.py`](py_model/libs/__vars.py)
  - ID / name mapping utilities: [`py_model/libs/__id_map.py`](py_model/libs/__id_map.py)
  - JSON/textproto helpers used by artifact generation: [`py_model/libs/__jsonize.py`](py_model/libs/__jsonize.py)
  - Counters and small utilities: [`py_model/libs/__counters.py`](py_model/libs/__counters.py), [`py_model/libs/__utils.py`](py_model/libs/__utils.py)
  - Object class imports that connect modules: [`py_model/libs/__obj_classes.py`](py_model/libs/__obj_classes.py)
- Scripts and artifact generation
  - Artifact generator: [`py_model/scripts/artifacts_gen.py`](py_model/scripts/artifacts_gen.py) — optimized generator that produces runtime artifacts (`dash_pipeline_p4rt.json`, `dash_pipeline_p4rt.txt`, and `dash_pipeline_ir.json`) by reflecting over the in-memory Python model.
  - Call graph and codegen helpers: [`py_model/scripts/call_graph.py`](py_model/scripts/call_graph.py), [`py_model/scripts/gen_table_chain.py`](py_model/scripts/gen_table_chain.py), etc.
- Generated artifacts
  - Pre-generated outputs are under [`py_model/dash_pipeline.py_model/`](py_model/dash_pipeline.py_model) (e.g. `dash_pipeline_p4rt.json`, `dash_pipeline_p4rt.txt`) used by saithrift-server and dpapp.

How it fits together (brief)
- The `dash_py_v1model.dash_py_model` function is the high-level packet processing entry that builds headers/metadata and calls the pipeline (`dash_pipeline` modules).
- The pipeline is organized into stages (seen in `py_model/data_plane/stages/*`) which model table lookups and actions. A stage exposes an `apply()` method (for example [`outbound_routing_stage.apply`](py_model/data_plane/stages/outbound_routing.py)) that performs the table lookup logic, counters and potential packet drop or forwarding decisions.
- Routing transformations and NAT/encap actions are implemented in `py_model/data_plane/routing_actions/*`.
- The control-plane helper (`grpc_server.py`) can load P4Info-like JSON and populate maps of table/action/counter IDs (`grpc_server.populate_tables_actions_ids`) so the test server can simulate control operations.

Quick start
- Generate py-model artifacts:
  - Run the artifact generator: `python3 -m py_model.scripts.artifacts_gen` (same as `make py-artifacts`). See [`py_model/scripts/artifacts_gen.py`](py_model/scripts/artifacts_gen.py).
- Run the python model interactively:
  - Use the runner: `make pymodel` (see [`py_model/main_dash.py`](py_model/main_dash.py)).
- Launch the P4Runtime test server/sniffer (if used):
  - Start the server: call [`grpc_server.serve`](py_model/control_plane/grpc_server.py) or run the server module.

Development pointers
- Code generation and reflections: study [`py_model/scripts/artifacts_gen.py`](py_model/scripts/artifacts_gen.py) to understand how the Python model is introspected to generate P4RT artifacts.
- Tables and runtime model objects live in [`py_model/libs/__table.py`](py_model/libs/__table.py) and are referenced by stage modules under `py_model/data_plane/stages/`.
- To trace a packet path, follow `dash_py_v1model.dash_py_model` -> `dash_pipeline` -> stage `apply()` methods (e.g. [`outbound_routing_stage.apply`](py_model/data_plane/stages/outbound_routing.py), [`outbound_mapping_stage.ca_to_pa`](py_model/data_plane/stages/outbound_mapping.py)).

Useful files (quick links)
- Model entry: [`py_model/dash_py_v1model.py`](py_model/dash_py_v1model.py) — [`dash_py_v1model.dash_py_model`](py_model/dash_py_v1model.py)
- Runner: [`py_model/main_dash.py`](py_model/main_dash.py)
- Artifact generator: [`py_model/scripts/artifacts_gen.py`](py_model/scripts/artifacts_gen.py)
- Pipeline orchestration: [`py_model/data_plane/dash_pipeline.py`](py_model/data_plane/dash_pipeline.py)
- Inbound/outbound: [`py_model/data_plane/dash_inbound.py`](py_model/data_plane/dash_inbound.py) (class `inbound`), [`py_model/data_plane/dash_outbound.py`](py_model/data_plane/dash_outbound.py) (class `outbound`)
- Example stage: [`py_model/data_plane/stages/outbound_routing.py`](py_model/data_plane/stages/outbound_routing.py) (class `outbound_routing_stage`)
- Table runtime: [`py_model/libs/__table.py`](py_model/libs/__table.py)
- Control plane server: [`py_model/control_plane/grpc_server.py`](py_model/control_plane/grpc_server.py)

Where to look next
- If you want to extend tables or behavioral logic, add/modify tables in `py_model/data_plane/stages/*` and adjust artifact generation logic in `py_model/scripts/artifacts_gen.py`.
- If you need to adapt the control-plane mapping, modify [`py_model/control_plane/grpc_server.py`](py_model/control_plane/grpc_server.py) and [`py_model/libs/__id_map.py`](py_model/libs/__id_map.py).
