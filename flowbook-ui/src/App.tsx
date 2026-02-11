import React, { useCallback, useState } from "react";
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  ReactFlowProvider,
  Node,
  Edge,
  Connection,
  NodeTypes,
} from "reactflow";
import "reactflow/dist/style.css";
import axios from "axios";
import NodeCell from "./NodeCell";
import { nanoid } from "nanoid";

function shortId() {
  return nanoid().slice(0, 6).toUpperCase();
}

const nodeTypes: NodeTypes = { flowNode: NodeCell as any };

export default function App() {
  const [nodes, setNodes] = useState<Node[]>([
    {
      id: "A",
      type: "flowNode",
      position: { x: 50, y: 20 },
      data: {
        code: "x = 1\nprint('A, x =', x)",
        output: "",
        // state removed (no longer used)
      },
    },
  ]);

  const [edges, setEdges] = useState<Edge[]>([]);

  // ---------------------------
  // Helper to update one node
  // ---------------------------
  const updateNodeData = useCallback((id: string, patch: any) => {
    setNodes((prev) =>
      prev.map((n) =>
        n.id === id ? { ...n, data: { ...n.data, ...patch } } : n
      )
    );
  }, []);

  // ---------------------------
  // Get parent ID
  // ---------------------------
  const getParentId = useCallback(
    (nodeId: string): string | null => {
      const parentEdge = edges.find((e) => e.target === nodeId);
      return parentEdge ? parentEdge.source : null;
    },
    [edges]
  );

  // ---------------------------
  // RUN node
  // ---------------------------
  const handleRun = useCallback(
  async (nodeId: string) => {
    updateNodeData(nodeId, { output: "Running..." });

    const node = nodes.find((n) => n.id === nodeId);
    if (!node) return;

    const parentId = getParentId(nodeId);

    try {
      const res = await axios.post("http://127.0.0.1:8000/execute_node", {
        nodeId,       // required by new API
        parentId,     // required by new API
        code: node.data.code,
      });

      updateNodeData(nodeId, {
        output: res.data.error ? res.data.error : res.data.stdout, 
      });
    } catch (err: any) {
      updateNodeData(nodeId, { output: "Error: " + err.message });
    }
  },
  [nodes, getParentId, updateNodeData]
);

  // ---------------------------
  // Edit code
  // ---------------------------
  const handleChangeCode = useCallback(
    (nodeId: string, newCode: string) => {
      updateNodeData(nodeId, { code: newCode });
    },
    [updateNodeData]
  );

  // ---------------------------
  // Add child node
  // ---------------------------
  const handleAddChild = useCallback(
    (parentId: string) => {
      const parent = nodes.find((n) => n.id === parentId);
      if (!parent) return;

      const newId = shortId();
      const parentPos = parent.position as { x: number; y: number };

      const newNode: Node = {
        id: newId,
        type: "flowNode",
        position: {
          x: parentPos.x + 300,
          y: parentPos.y + 140,
        },
        data: {
          code: `print("child ${newId}", x)`,
          output: "",
        },
      };

      const newEdge: Edge = {
        id: `e-${parentId}-${newId}`,
        source: parentId,
        target: newId,
      };

      setNodes((nds) => [...nds, newNode]);
      setEdges((eds) => [...eds, newEdge]);
    },
    [nodes]
  );

  // ---------------------------
  // Flow events
  // ---------------------------
  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  const onNodeDragStop = useCallback((_: any, node: Node) => {
    setNodes((prev) =>
      prev.map((n) =>
        n.id === node.id ? { ...n, position: node.position } : n
      )
    );
  }, []);

  // Attach callbacks
  const nodesWithCallbacks = nodes.map((n) => ({
    ...n,
    data: {
      ...n.data,
      onChange: handleChangeCode,
      onRun: handleRun,
      onAddChild: handleAddChild,
    },
  }));

  return (
    <ReactFlowProvider>
      <div style={{ width: "100vw", height: "100vh" }}>
        <ReactFlow
          nodes={nodesWithCallbacks}
          edges={edges}
          onConnect={onConnect}
          onNodeDragStop={onNodeDragStop}
          nodeTypes={nodeTypes}
          fitView
        >
          <MiniMap />
          <Controls />
          <Background gap={16} color="#071129" />
        </ReactFlow>
      </div>
    </ReactFlowProvider>
  );
}
