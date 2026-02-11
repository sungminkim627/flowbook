import json
from .model import Node, Flowbook

def load_flowbook(path: str) -> Flowbook:
    with open(path, "r") as f:
        data = json.load(f)
    nodes = {k: Node(id=k, **v) for k, v in data["nodes"].items()}
    return Flowbook(metadata=data["metadata"], nodes=nodes, root=data["root"])

def save_flowbook(flowbook: Flowbook, path: str):
    data = {
        "metadata": flowbook.metadata,
        "root": flowbook.root,
        "nodes": {
            node_id: {
                "type": node.type,
                "source": node.source,
                "parents": node.parents,
                "outputs": node.outputs,
            }
            for node_id, node in flowbook.nodes.items()
        },
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
