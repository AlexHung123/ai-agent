import MetaSearchAgent from '@/lib/search/metaSearchAgent';
import prompts from '../prompts';

export const searchHandlers: Record<string, MetaSearchAgent> = {
  agentSFC: new MetaSearchAgent({
    activeEngines: [],
    queryGeneratorPrompt: '',
    responsePrompt: prompts.sfcPrompt,
    queryGeneratorFewShots: [],
    rerank: true,
    rerankThreshold: 0.3,
    searchWeb: false,
  }),
  agentGuide: new MetaSearchAgent({
    activeEngines: [],
    queryGeneratorPrompt: '',
    queryGeneratorFewShots: [],
    responsePrompt: prompts.guidePrompt,
    rerank: true,
    rerankThreshold: 0,
    searchWeb: false,
  }),
  agentSurvey: new MetaSearchAgent({
    activeEngines: [],
    queryGeneratorPrompt: '',
    queryGeneratorFewShots: [],
    responsePrompt: prompts.surveyPrompt,
    rerank: true,
    rerankThreshold: 0,
    searchWeb: false,
  }),
};