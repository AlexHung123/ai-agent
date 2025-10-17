import { NextRequest } from 'next/server';
import { z } from 'zod';
import { getLimeSurveySummaryBySid } from '@/lib/postgres/limeSurvey'; 
import { splitSurvey } from '@/lib/utils/splitSurvey';
import { ChatOpenAI } from '@langchain/openai';
import { getCustomOpenaiApiKey, getCustomOpenaiApiUrl, getCustomOpenaiModelName } from '@/lib/config';
import { BaseChatModel } from '@langchain/core/language_models/chat_models';
import { handleEmitterEvents } from '@/lib/utils/chatHelper';
import prompts from '@/lib/prompts';
import { getSurveySummary } from '@/lib/chains/limeSurveyAgent';


export type RatingItem = { count: number; value: string };
export type FreeTextItem = { answer: string };

export type Group = RatingItem[] | FreeTextItem[];

export type Survey = Record<string, Group>;

export type RatingsOnly = Record<string, RatingItem[]>;
export type FreeTextOnly = Record<string, FreeTextItem[]>;


// Schema for validating the request body
const surveySchema = z.object({
  sid: z.string().min(1, 'Survey ID is required'),
});


export async function POST(req: NextRequest) {
  try {
    // Parse and validate the request body
    const body = await req.json();
    const parseResult = surveySchema.safeParse(body);
    
    if (!parseResult.success) {
      return Response.json(
        { 
          error: 'Invalid request body',
          details: parseResult.error.errors 
        },
        { status: 400 }
      );
    }
    
    const { sid } = parseResult.data;
    
    try {
      const surveyData = await getLimeSurveySummaryBySid(sid);

      const data: Survey = (surveyData[0]["result_json"]) as unknown as Survey;
     
      const { freeTextOnly } = splitSurvey(data);    

      //  // 3) Preprocess: call FastAPI with freeTextOnly as raw_json (object)
      // const preprocessRes = await fetch('http://192.168.56.1:8000/api/v1/group/bilingual-groups', {
      //   method: 'POST',
      //   headers: {
      //     'accept': 'application/json',
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     raw_json: freeTextOnly, // send as object, not string
      //   }),
      // });

      // if (!preprocessRes.ok) {
      //   const errText = await preprocessRes.text().catch(() => '');
      //   return Response.json(
      //     { error: 'Preprocess API failed', status: preprocessRes.status, details: errText },
      //     { status: 502 }
      //   );
      // }

      // const grouped = await preprocessRes.json();

      console.log('------');
      console.log(freeTextOnly);
      
      const llm = new ChatOpenAI({
        apiKey: getCustomOpenaiApiKey(),
        modelName: getCustomOpenaiModelName(),
        temperature: 0,
        configuration: {
        baseURL: getCustomOpenaiApiUrl(),
        },
      }) as unknown as BaseChatModel;

      const stream = await getSurveySummary({
        baseModel: llm,
        responsePrompt: prompts.surveyPrompt,
        fastApiBaseUrl: "http://192.168.56.1:8000",
        rawText: JSON.stringify(freeTextOnly),
      });

      // const answeringChain = createSurveyChain({
      //   baseModel: llm,
      //   responsePrompt: prompts.surveyPrompt,      // your existing system response prompt
      //   fastApiBaseUrl: "http://192.168.56.1:8000" // your FastAPI host
      // });

      // const stream = answeringChain.streamEvents(
      //   {
      //     chat_history: history,
      //     raw: freeTextOnly, // pass A here (object)
      //   },
      //   { version: "v1" }
      // );

      
      // const handler = searchHandlers['agentSurvey'];
      // if (!handler) {
      //   return Response.json(
      //       {
      //       message: 'Invalid focus mode',
      //       },
      //       { status: 400 },
      //   );
      // }

    // const history: BaseMessage[] = [];

    // const stream = await handler.searchAndAnswer(
    //   JSON.stringify(grouped),
    //   history,
    //   llm,
    //   prompts.surveyPrompt,
    // //   'Your are a helpful assistant that answers questions about surveys'
    // //   body.systemInstructions as string,
    // );

      const responseStream = new TransformStream();
      const writer = responseStream.writable.getWriter();
      const encoder = new TextEncoder();

      handleEmitterEvents(stream, writer, encoder);

      return new Response(responseStream.readable, {
        headers: {
          'Content-Type': 'text/event-stream',
          Connection: 'keep-alive',
          'Cache-Control': 'no-cache, no-transform',
        },
      });
    } catch (error: any) {
      console.error('Error processing agent survey:', error);
      return Response.json(
        { error: 'Failed to process agent survey', details: error.message || 'Unknown error occurred' },
        { status: 500 }
      );
    }
  } catch (error: any) {
    console.error('Error processing agent survey request:', error);
    return Response.json(
      { error: 'Failed to process agent survey request', details: error.message || 'Unknown error occurred' },
      { status: 500 }
    );
  }
}