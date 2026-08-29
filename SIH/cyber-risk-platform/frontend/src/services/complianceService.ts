import api from './api';
import type {  
  ComplianceFramework, 
  FrameworkAssessmentSummary, 
  ComplianceGap, 
  CrosswalkResponse 
 } from "../types/compliance";

export const getFrameworks = async (): Promise<ComplianceFramework[]> => {
  return api.get<ComplianceFramework[]>('/api/v1/compliance/frameworks');
};

export const getFrameworkSummary = async (frameworkId: string): Promise<FrameworkAssessmentSummary> => {
  return api.get<FrameworkAssessmentSummary>(`/api/v1/compliance/frameworks/${frameworkId}/summary`);
};

export const assessFramework = async (frameworkId: string): Promise<FrameworkAssessmentSummary> => {
  return api.post<FrameworkAssessmentSummary>(`/api/v1/compliance/frameworks/${frameworkId}/assess`);
};

export const getGaps = async (): Promise<ComplianceGap[]> => {
  return api.get<ComplianceGap[]>('/api/v1/compliance/gaps');
};

export const getControlCrosswalk = async (controlId: string): Promise<CrosswalkResponse> => {
  return api.get<CrosswalkResponse>(`/api/v1/compliance/crosswalk/control/${controlId}`);
};
