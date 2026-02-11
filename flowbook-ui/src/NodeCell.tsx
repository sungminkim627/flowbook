import React, { memo } from "react";
import { Handle, Position, NodeProps } from "reactflow";
import Editor from "@monaco-editor/react";

export type FlowNodeData = {
  code: string;
  output: string;
  state?: string | null;   // now included
  onChange: (nodeId: string, newCode: string) => void;
  onRun: (nodeId: string) => void;
  onAddChild: (nodeId: string) => void;
};

export default memo(function NodeCell({ id, data }: NodeProps<FlowNodeData>) {
  return (
    <div
      style={{
        width: 380,
        background: "#0e1628",
        border: "1px solid #203050",
        borderRadius: "12px",
        padding: "12px",
        color: "white",
      }}
    >
      <Handle type="target" position={Position.Top} />

      <Editor
        height="160px"
        defaultLanguage="python"
        value={data.code}
        onChange={(val) => data.onChange(id, val || "")}
        theme="vs-dark"
      />

      <div style={{ display: "flex", gap: "8px", marginTop: 8 }}>
        <button
          onClick={() => data.onRun(id)}
          style={{
            background: "#234bda",
            padding: "6px 12px",
            borderRadius: 6,
            border: "none",
            color: "white",
            cursor: "pointer",
          }}
        >
          Run
        </button>

        <button
          onClick={() => data.onAddChild(id)}
          style={{
            background: "#2d7d46",
            padding: "6px 12px",
            borderRadius: 6,
            border: "none",
            color: "white",
            cursor: "pointer",
          }}
        >
          +
        </button>
      </div>

      <pre
        style={{
          background: "#0a1020",
          borderRadius: 6,
          padding: "8px",
          marginTop: "10px",
          minHeight: "40px",
          whiteSpace: "pre-wrap",
        }}
      >
        {data.output}
      </pre>

      <Handle type="source" position={Position.Bottom} />
    </div>
  );
});
