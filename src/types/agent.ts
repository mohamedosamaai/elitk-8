/**
 * Agent type contracts for the ELITK-8 multi-agent orchestration pipeline.
 *
 * These interfaces define the structural boundaries between agents.
 * No business logic lives here — only contracts.
 */

/**
 * Roles within the orchestration pipeline.
 * Matches the values used in src/types.ts AgentRole enum at the application layer.
 */
export type AgentPipelineRole =
  | 'orchestrator'
  | 'ideation'
  | 'knowledge-retrieval'
  | 'synthesis'
  | 'output-formatter';

/** A discrete message passed between agents in a pipeline run. */
export interface AgentMessage {
  role: 'user' | 'agent' | 'system';
  content: string;
  /** ISO 8601 UTC timestamp. */
  timestamp: string;
  /** Which agent produced this message, if applicable. */
  agentId?: string;
}

/** Configuration for a single agent instance. */
export interface AgentConfig {
  id: string;
  role: AgentPipelineRole;
  /** System prompt injected at the start of every context window. */
  systemPrompt: string;
  /** Maximum tokens this agent may consume per invocation. */
  maxTokenBudget: number;
}

/** The result produced by an agent after processing a task. */
export interface AgentResult {
  agentId: string;
  output: string;
  /** Whether the agent escalated to the orchestrator for clarification. */
  escalated: boolean;
  tokensConsumed: number;
}

/** Contract for runnable agent implementations. */
export interface RunnableAgent {
  config: AgentConfig;
  run(messages: AgentMessage[]): Promise<AgentResult>;
}
