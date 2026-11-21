export interface ProjectItem {
  title: string;
  description: string;
  technologies: string[];
  githubUrl?: string;
  liveUrl?: string;
}

export interface ProfilePreferences {
  targetRoles: string[];
  preferredLocations: string[];
  preferredCompanyTypes: string[];
  outreachObjective?: string;
}

export interface StudentProfile {
  _id?: string;
  userId: string;
  fullName: string;
  email: string;
  college: string;
  degree: string;
  branch: string;
  currentYear: string;
  skills: string[];
  programmingLanguages: string[];
  frameworks: string[];
  projects: ProjectItem[];
  githubProfile?: string;
  linkedinProfile?: string;
  portfolioUrl?: string;
  resumeText?: string;
  preferences: ProfilePreferences;
  updatedAt?: string;
}

export interface Campaign {
  _id: string;
  userId: string;
  name: string;
  objective: string;
  targetIndustry: string;
  targetLocation: string;
  targetRoles: string[];
  targetProspectCount: number;
  preferredTechnologies: string[];
  status: "draft" | "planning" | "running" | "completed" | "paused" | "failed";
  companiesCount: number;
  contactsCount: number;
  draftsCount: number;
  emailsSentCount: number;
  lastExecutionId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Company {
  _id: string;
  campaignId: string;
  name: string;
  website: string;
  description: string;
  industry: string;
  location: string;
  technologies: string[];
  sources: { url: string; title?: string; discoveredAt: string }[];
  createdAt: string;
}

export interface Contact {
  _id: string;
  campaignId: string;
  companyId: string;
  companyName: string;
  name: string;
  role: string;
  professionalEmail?: string;
  profileUrl?: string;
  sourceUrl: string;
  confidence: number;
  verificationStatus: "unverified" | "publicly_disclosed" | "domain_matched" | "demo_sample";
  relevanceScore?: number;
  relevanceReasons?: string;
  suggestedAngle?: string;
  createdAt: string;
}

export interface EmailDraft {
  _id: string;
  userId: string;
  campaignId: string;
  contactId: string;
  companyId: string;
  recipientName: string;
  recipientEmail: string;
  recipientRole: string;
  companyName: string;
  subject: string;
  body: string;
  personalizationEvidence: string[];
  researchReferences: string[];
  warnings: string[];
  approvalStatus: "generated" | "pending_review" | "approved" | "rejected" | "sending" | "sent" | "failed";
  approvedContentHash?: string;
  approvedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AgentStep {
  stepNumber: number;
  task: string;
  thought: string;
  action?: string;
  observation?: string;
  status: string;
  timestamp: string;
}

export interface ToolCall {
  toolName: string;
  inputArgs: Record<string, any>;
  outputSummary?: string;
  isSuccess: boolean;
  error?: string;
  timestamp: string;
}

export interface AgentExecution {
  _id: string;
  campaignId: string;
  userId: string;
  currentStep: number;
  totalSteps: number;
  executionStatus: "pending" | "running" | "completed" | "failed" | "stopped";
  planTasks: string[];
  toolCalls: ToolCall[];
  steps: AgentStep[];
  errors: string[];
  startedAt: string;
  completedAt?: string;
}
