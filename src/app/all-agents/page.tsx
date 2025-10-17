'use client';

import React, { useRef, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Label } from '@/components/ui';
import { Alert, AlertDescription } from '@/components/ui';
import { Loader2, Users, BarChart } from 'lucide-react';

type StreamEvent =
  | { type: 'message'; data: string; messageId?: string }
  | { type: 'messageEnd' }
  | { type: string; [k: string]: any };

async function readJSONLineSSE(
  url: string,
  init: RequestInit,
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (errMsg: string) => void
) {
  try {
    const res = await fetch(url, init);
    if (!res.ok) {
      const detail = await res.text().catch(() => '');
      throw new Error(detail || `Request failed with ${res.status}`);
    }

    const reader = res.body?.getReader();
    if (!reader) throw new Error('No readable body');

    const decoder = new TextDecoder();
    let carry = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      carry += decoder.decode(value, { stream: true });

      const lines = carry.split('\n');
      carry = lines.pop() ?? '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        let evt: StreamEvent | null = null;
        try {
          evt = JSON.parse(trimmed);
        } catch {
          continue;
        }

        if (!evt) continue;

        if (evt.type === 'messageEnd') {
          try {
            await reader.cancel();
          } catch {}
          onDone();
          return;
        }

        if (evt.type === 'message') {
          const text = typeof evt.data === 'string' ? evt.data : '';
          if (text) onChunk(text);
        }
      }
    }

    const last = carry.trim();
    if (last) {
      try {
        const evt = JSON.parse(last) as StreamEvent;
        if (evt.type === 'message') {
          const text = typeof evt.data === 'string' ? evt.data : '';
          if (text) onChunk(text);
        }
      } catch {}
    }

    onDone();
  } catch (err: any) {
    if (err?.name === 'AbortError') return;
    onError(err?.message || 'Stream error');
  }
}

const AgentSurveyPage = () => {
  const [surveyId, setSurveyId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const handleProcessSurvey = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!surveyId.trim()) {
      setError('Please enter a Survey ID');
      return;
    }

    if (abortRef.current) abortRef.current.abort();
    const aborter = new AbortController();
    abortRef.current = aborter;

    setIsLoading(true);
    setError(null);
    setResult('');

    await readJSONLineSSE(
      '/api/agent-survey',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({ sid: surveyId.trim() }),
        signal: aborter.signal,
      },
      (text) => setResult((prev) => prev + text),
      () => setIsLoading(false),
      (msg) => {
        setError(msg);
        setIsLoading(false);
      }
    );
  };

  const formatResult = (text: string) => {
    const sections = text.split('\n\n');
    return (
      <div className="space-y-6">
        {sections.map((section, idx) => {
          if (!section.trim()) return null;
          const lines = section.split('\n');
          const title = lines[0];
          const items = lines.slice(1);
          return (
            <div key={idx}>
              <h3 className="text-xl font-semibold mb-2">{title}</h3>
              <ul className="list-none space-y-1">
                {items.map((item, i) => (
                  <li key={i} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span
                      dangerouslySetInnerHTML={{
                        __html: item.replace('• ', ''),
                      }}
                    />
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center mb-8">
        <Users className="mr-3 h-8 w-8" />
        <h1 className="text-3xl font-bold">Agent Survey Processor</h1>
      </div>

      {/* Single full-width column so Results spans same width as Available Agents */}
      <div className="grid grid-cols-1 gap-8">
        {/* Results Section (full width) with inline Survey controls */}
        <Card>
          <CardHeader>
            <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <CardTitle>
                  <div className="flex items-center">
                    <BarChart className="mr-2 h-5 w-5" />
                    Results
                  </div>
                </CardTitle>
                <CardDescription>Categorized survey responses</CardDescription>
              </div>

              {/* Moved Survey ID + Process button here */}
              <form onSubmit={handleProcessSurvey} className="w-full md:w-auto">
                <div className="flex w-full gap-3 md:items-end">
                  <div className="flex-1">
                    <Label htmlFor="surveyId" className="mb-1 block">Survey ID</Label>
                    <Input
                      id="surveyId"
                      value={surveyId}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSurveyId(e.target.value)}
                      placeholder="Enter survey ID (e.g., 12345)"
                      disabled={isLoading}
                    />
                  </div>
                  <Button type="submit" disabled={isLoading} className="whitespace-nowrap">
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      'Process Survey'
                    )}
                  </Button>
                </div>
              </form>
            </div>
          </CardHeader>

          {error && (
            <div className="px-6">
              <Alert variant="destructive" className="mt-2">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            </div>
          )}

          {/* Scrollable results viewport */}
          <div
            className="
              max-h-[50vh]
              overflow-y-auto
              overscroll-contain
              scroll-smooth
              pr-2
              [scrollbar-width:thin]
              [scrollbar-color:theme(colors.gray.400)_transparent]
            "
            style={{ scrollbarGutter: 'stable' }}
          >
            <CardContent className="pt-0">
              {result ? (
                <div className="prose max-w-none dark:prose-invert">
                  {formatResult(result)}
                </div>
              ) : isLoading ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                  <p className="mt-4 text-center text-gray-500 dark:text-gray-400">
                    Processing survey data...
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <BarChart className="h-12 w-12 text-gray-400" />
                  <h3 className="mt-4 font-medium">No results yet</h3>
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    Enter a survey ID and click "Process Survey" to see categorized feedback
                  </p>
                </div>
              )}
            </CardContent>
          </div>
        </Card>
      </div>

      {/* Available Agents (full width) */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Available Agents</CardTitle>
          <CardDescription>Other AI agents available for data processing</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
              <h3 className="font-medium flex items-center">
                <Users className="mr-2 h-4 w-4" />
                Agent Survey
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Process and analyze survey data with AI-powered categorization
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AgentSurveyPage;
