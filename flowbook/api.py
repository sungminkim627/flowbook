# api.py
import pickle
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
from jupyter_client import KernelManager
import time
import types
import os

app = FastAPI(title="Flowbook API - Option A (isolated child execs)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

class ExecCodeRequest(BaseModel):
    nodeId: str
    parentId: Optional[str] = None
    code: str

# ---------------------------
# Start a single global kernel
# ---------------------------
km = KernelManager(kernel_name="python3")
km.start_kernel()
kc = km.client()
kc.start_channels()

# Helper: wait until kernel is idle (consumes status messages)
def wait_idle(timeout=5):
    start = time.time()
    while True:
        try:
            msg = kc.get_iopub_msg(timeout=1)
        except:
            if time.time() - start > timeout:
                break
            continue
        if msg.get("msg_type") == "status" and msg["content"].get("execution_state") == "idle":
            break

# ---------------------------
# Main endpoint
# ---------------------------
@app.post("/execute_node")
def execute_node(payload: ExecCodeRequest) -> Dict[str, Any]:
    """
    Execute the node's code in an isolated namespace that is initialized
    from parent snapshot bytes (if parentId provided). After execution, snapshot
    only picklable variables in that namespace and store them as bytes under
    _flowbook_node_states[nodeId].

    Returns: {"stdout": "<combined output>", "error": "<error string or null>"}
    """
    try:
        # prepare code to:
        # - create __fb_ns namespace
        # - if parent snapshot exists in _flowbook_node_states (bytes), load and update __fb_ns
        # - exec user code in __fb_ns
        # - build __node_state containing only picklable, non-private items from __fb_ns
        # - create __pickled bytes of __node_state
        # __pickled will be left in kernel globals so we can store it under _flowbook_node_states[nodeId]
        user_code = payload.code or ""

        # embed user_code safely as repr
        user_code_repr = repr(user_code)

        # build the big execution string that runs inside the kernel (but does NOT write to globals except for __fb_ns / __pickled)
        exec_block = f"""
import pickle, types
# temp namespace for this node execution
__fb_ns = {{}}

# ensure our snapshot store exists
if "_flowbook_node_states" not in globals():
    _flowbook_node_states = {{}}

# if parent exists, try to restore parent's pickled bytes into __fb_ns
_parent_id = {repr(payload.parentId)}
if _parent_id:
    _parent_bytes = _flowbook_node_states.get(_parent_id)
    if _parent_bytes:
        try:
            _parent_state = pickle.loads(_parent_bytes)
            if isinstance(_parent_state, dict):
                __fb_ns.update(_parent_state)
        except Exception:
            # ignore parent restoration errors (non-critical)
            pass

# ensure builtins are available inside the namespace
__fb_ns['__builtins__'] = __builtins__

# execute the user code inside __fb_ns (so kernel globals are not polluted)
_exec_code = {user_code_repr}
exec(compile(_exec_code, "<flowbook>", "exec"), __fb_ns)

# helper to detect picklable objects
def _is_picklable(o):
    try:
        pickle.dumps(o)
        return True
    except Exception:
        return False

# build a picklable snapshot of user variables in __fb_ns
__node_state = {{
    k: v for k, v in __fb_ns.items()
    if not k.startswith("_") and _is_picklable(v)
}}

# pickle it
__pickled = pickle.dumps(__node_state)
"""

        # Execute the block in the kernel
        kc.execute(exec_block)

        # Now collect iopub messages (streams, errors, results) while execution runs
        outputs = []
        start = time.time()
        timeout_seconds = 8

        while True:
            try:
                msg = kc.get_iopub_msg(timeout=1)
            except:
                # no message this second
                if time.time() - start > timeout_seconds:
                    break
                continue

            mtype = msg.get("msg_type")
            content = msg.get("content", {})

            if mtype == "stream":
                outputs.append(content.get("text", ""))
            elif mtype == "error":
                outputs.append("\n".join(content.get("traceback", [])))
            elif mtype in ("execute_result", "display_data"):
                # capture textual representation if present
                data = content.get("data", {})
                text = data.get("text/plain")
                if text:
                    outputs.append(text)
            elif mtype == "status" and content.get("execution_state") == "idle":
                # exec finished
                break

        combined_output = "\n".join([s for s in outputs if s])

        # __pickled should now exist in kernel globals. Store it into _flowbook_node_states[nodeId]
        store_code = f"""
if "_flowbook_node_states" not in globals():
    _flowbook_node_states = {{}}
_flowbook_node_states[{repr(payload.nodeId)}] = __pickled
"""
        kc.execute(store_code)
        wait_idle()

        return {"stdout": combined_output, "error": None}

    except Exception as e:
        # a safe error response
        return {"stdout": "", "error": str(e)}


# Serve React static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
