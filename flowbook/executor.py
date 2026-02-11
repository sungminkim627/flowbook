from jupyter_client import KernelManager
import networkx as nx

def execute_flowbook(flowbook, start_node):
    km = KernelManager(kernel_name=flowbook.metadata.get("kernel", "python3"))
    km.start_kernel()
    kc = km.client()
    kc.start_channels()

    # Build DAG
    G = nx.DiGraph()
    for node_id, node in flowbook.nodes.items():
        for p in node.parents:
            G.add_edge(p, node_id)
    run_order = list(nx.topological_sort(G.subgraph(nx.ancestors(G, start_node) | {start_node})))

    print(f"Executing: {run_order}")

    for node_id in run_order:
        node = flowbook.nodes[node_id]
        print(f"\n>>> Running Node {node_id} <<<")
        kc.execute(node.source)
        while True:
            msg = kc.get_iopub_msg()
            if msg["msg_type"] == "execute_result":
                print(msg["content"]["data"].get("text/plain", ""))
                node.outputs.append({
                    "mime_type": "text/plain",
                    "data": msg["content"]["data"]
                })
            elif msg["msg_type"] == "status" and msg["content"]["execution_state"] == "idle":
                break

    kc.stop_channels()
    km.shutdown_kernel()
