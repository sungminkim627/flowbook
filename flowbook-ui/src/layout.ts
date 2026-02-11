// src/layout.ts
import dagre from "dagre";
import { Node, Edge } from "reactflow";

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

export function applyDagreLayout(nodes: Node[], edges: Edge[], direction = "TB") {
  const nodeWidth = 420;
  const nodeHeight = 340; // editor + output -> keep generous

  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((n) => {
    dagreGraph.setNode(n.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((e) => {
    dagreGraph.setEdge(e.source, e.target);
  });

  dagre.layout(dagreGraph);

  const layouted = nodes.map((n) => {
    const pos = dagreGraph.node(n.id);
    return {
      ...n,
      position: { x: pos.x - nodeWidth / 2, y: pos.y - nodeHeight / 2 },
    };
  });

  return { nodes: layouted, edges };
}
