import { BaseChatModel } from "@langchain/core/language_models/chat_models";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { RunnableSequence, RunnableMap, RunnableLambda, RunnablePassthrough } from "@langchain/core/runnables";
import { StreamEvent } from "@langchain/core/tracers/log_stream";
import eventEmitter from "events";
import { z } from "zod";

const AnswerItemSchema = z.object({
  answer: z.string(),
});
const FirstLLMSchema = z.record(z.string(), z.array(AnswerItemSchema));

import type { RunnableConfig } from "@langchain/core/runnables";

function listenersFor(name: string) {
  return {
    onStart: (run: any, _config?: RunnableConfig) => {
      console.log(`[${name}] onStart`, {
        id: run?.id,
        name: run?.name,
        input: run?.inputs ?? run?.input,
        tags: run?.tags,
        metadata: run?.metadata,
        startTime: run?.start_time ?? run?.startTime,
      });
    },
    // onEnd: (run: any, _config?: RunnableConfig) => {
    //   console.log(`[${name}] onEnd`, {
    //     id: run?.id,
    //     name: run?.name,
    //     output: run?.outputs ?? run?.output,
    //     endTime: run?.end_time ?? run?.endTime,
    //   });
    // },
    // onError: (run: any, _config?: RunnableConfig) => {
    //   console.error(`[${name}] onError`, {
    //     id: run?.id,
    //     name: run?.name,
    //     error: run?.error,
    //   });
    // },
  };
}

function buildFirstLLM(baseModel: BaseChatModel) {
  const llmAtoB = baseModel.withStructuredOutput(FirstLLMSchema, {
    name: "split_topic",
    strict: true,
  });
  const firstPrompt = ChatPromptTemplate.fromMessages([
    [
      "system",
      'Please review the following JSON. If the "answer" contains multiple key points, split each key point into a separate "answer" entry in sequence and add them to the current question. Keep the original text unchanged — do not modify or rewrite anything. Output the result as a complete, valid JSON object. Return only the JSON that matches the schema.',
    ],
    ["user", "{raw}"],
  ]);
  return RunnableSequence.from([
    RunnableMap.from({
      raw: (x: any) => JSON.stringify(x),
    }),
    firstPrompt,
    llmAtoB,
  ]);
}

function buildPreprocessRunnable(fastApiUrl: string) {
  return RunnableLambda.from(async (b: Record<string, any>) => {
    const res = await fetch(`${fastApiUrl}/api/v1/group/bilingual-groups`, {
      method: "POST",
      headers: {
        accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ raw_json: b }),
    });
    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      throw new Error(`Preprocess API failed ${res.status}: ${errText}`);
    }
    const grouped = await res.json();
    return grouped;
  });
}

function buildFinalLLMChain(baseModel: BaseChatModel, responsePrompt: string) {
  const finalPrompt = ChatPromptTemplate.fromMessages([
    ["system", responsePrompt],
    new MessagesPlaceholder("chat_history"),
    ["user", "{query}"],
  ]);
  return RunnableSequence.from([finalPrompt, baseModel]);
}

async function handleStream(
  stream: AsyncGenerator<StreamEvent, any, any>,
  emitter: eventEmitter,
) {
  for await (const event of stream) {
    if (event.event === "on_chain_end" && event.name === "FinalSourceRetriever") {
      emitter.emit("data", JSON.stringify({ type: "sources", data: event.data.output }));
    }
    if (event.event === "on_chain_stream" && event.name === "FinalResponseGenerator") {
      emitter.emit("data", JSON.stringify({ type: "response", data: event.data.chunk }));
    }
    if (event.event === "on_chain_end" && event.name === "FinalResponseGenerator") {
      emitter.emit("end");
    }
  }
}

function createSurveyChain({
  baseModel,
  responsePrompt,
  fastApiBaseUrl,
}: {
  baseModel: BaseChatModel;
  responsePrompt: string;
  fastApiBaseUrl: string;
}) {
  const firstLLM = buildFirstLLM(baseModel);
  const preprocess = buildPreprocessRunnable(fastApiBaseUrl);
  const finalLLM = buildFinalLLMChain(baseModel, responsePrompt);

  return RunnableSequence.from([
    // accept { chat_history, raw } at the top
    RunnableMap.from({
      chat_history: (i: any) => i.chat_history,
      raw: (i: any) => i.raw, // passthrough
    }),
    // A -> B
    RunnableLambda.from((i: any) => i.raw).pipe(firstLLM),
    // B -> C
    preprocess,
    // Map C into final prompt variables (use function constants)
    RunnableMap.from({
      chat_history: () => [],
      query: (c: any) => JSON.stringify(c),
    }),
    // C -> Final
    finalLLM,
  ]).withConfig({ runName: "FinalResponseGenerator" });
}

export async function getSurveySummary({
  baseModel,
  responsePrompt,
  fastApiBaseUrl,
  rawText,
  history = [],
}: {
  baseModel: BaseChatModel;
  responsePrompt: string;
  fastApiBaseUrl: string;
  rawText: string;
  history?: any[];
}) {
  const emitter = new eventEmitter();

  const answeringChain = createSurveyChain({
    baseModel,
    responsePrompt,
    fastApiBaseUrl,
  });

  const stream = answeringChain.streamEvents(
    {
      chat_history: history,
      raw: rawText, // matches the chain’s expected top-level input
    },
    { version: "v1" },
  );

  handleStream(stream, emitter);
  return emitter;
}
