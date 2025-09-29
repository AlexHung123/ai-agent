import { Message } from '@/components/ChatWindow';
import { apiClient } from './api';

export const getSuggestions = async (chatHistory: Message[]) => {
  const chatModel = localStorage.getItem('chatModel');
  const chatModelProvider = localStorage.getItem('chatModelProvider');

  const customOpenAIKey = localStorage.getItem('openAIApiKey');
  const customOpenAIBaseURL = localStorage.getItem('openAIBaseURL');

  const data = await apiClient.post('/api/suggestions', {
    chatHistory: chatHistory,
    chatModel: {
      provider: chatModelProvider,
      model: chatModel,
      ...(chatModelProvider === 'custom_openai' && {
        customOpenAIKey,
        customOpenAIBaseURL,
      }),
    },
  });

  return data.suggestions;
};
