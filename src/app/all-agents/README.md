# Agent Survey Frontend

This directory contains the frontend implementation for the Agent Survey feature.

## Components

### Page Component
- [page.tsx](file:///d:/Projects/ai-agent/src/app/all-agents/page.tsx): Main page component for the Agent Survey interface

### UI Components
Custom UI components created for this feature:
- [Button](file:///d:/Projects/ai-agent/src/components/ui/button.tsx): Styled button component
- [Card](file:///d:/Projects/ai-agent/src/components/ui/card.tsx): Card container with header, content, and footer
- [Input](file:///d:/Projects/ai-agent/src/components/ui/input.tsx): Styled input field
- [Label](file:///d:/Projects/ai-agent/src/components/ui/label.tsx): Form label component
- [Alert](file:///d:/Projects/ai-agent/src/components/ui/alert.tsx): Alert/notification component

## Features

1. **Survey ID Input**: Form to enter the LimeSurvey ID for processing
2. **Processing Status**: Loading indicator during data processing
3. **Error Handling**: Display of any errors that occur during processing
4. **Results Display**: Formatted display of categorized survey responses
5. **Agent Listing**: Section showing available AI agents

## API Integration

The frontend communicates with the Agent Survey API endpoint at `/api/agent-survey` using POST requests with the survey ID.

## Styling

The components use Tailwind CSS classes for styling and follow the existing design patterns in the application.