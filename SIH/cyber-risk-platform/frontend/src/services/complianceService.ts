import api from './api';
import { 
  ComplianceFramework, 
  FrameworkAssessmentSummary, 
  ComplianceGap, 
  CrosswalkResponse 
} from '../types/compliance';

export const getFrameworks = async (): Promise<ComplianceFramework[]> => {
  const response = await api.get('/compliance/frameworks');
  return response.data;
};

export const getFrameworkSummary = async (frameworkId: string): Promise<FrameworkAssessmentSummary> => {
  const response = await api.get(`/compliance/frameworks/${frameworkId}/summary`);
  return response.data;
};

export const assessFramework = async (frameworkId: string): Promise<FrameworkAssessmentSummary> => {
  const response = await api.post(`/compliance/frameworks/${frameworkId}/assess`);
  return response.data;
};

export const getGaps = async (): Promise<ComplianceGap[]> => {
  const response = await api.get('/compliance/gaps');
  return response.data;
};

export const getControlCrosswalk = async (controlId: string): Promise<CrosswalkResponse> => {
  const response = await api.get(`/compliance/crosswalk/control/${controlId}`);
  return response.data;
};
