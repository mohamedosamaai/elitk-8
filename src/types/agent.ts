/**
 * Agent type contracts for the ELITK-8 multi-agent pipeline.
 *
 * All agent implementations must satisfy these interfaces.
 * Business logic is never embedded in type definitions —
 * these are pure structural contracts.
 */

/** Supported agent roles within the orchestration pipeline. */
export type AgentRole =
  | 'orchestrator'
  | 'ideation'
  | 'knowledge-retrieval'
  | 'synthesis'
  | 'output-formatter';

/** A discrete message passed between agents. */
export interface AgentMessage {
  role: 'user' | 'agent' | 'system';
  content: string;
  /** ISO 8601 timestamp. */
  timestamp: string;
  /** Which agent produced this message, if applicable. */
  agentId?: string;
}

/** Configuration for a single agent instance. */
export interface AgentConfig {
  id: string;
  role: AgentRole;
  /** System prompt injected at the start of every context window. */
  systemPrompt: string;
  /** Max tokens this agent is permitted to consume per invocation. */
  maxTokenBudget: number;
}

/** Describes the result produced by an agent after processing a task. */
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
