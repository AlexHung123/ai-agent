export const surveyPrompt = `
You will receive a JSON object containing a question number (question_zh) and multiple data entries (data array).
Each data item contains the following fields:

- group_topic.zh: Chinese topic

- answers: an array of text responses

Your task is:

1. Classify each topic into one of the four categories based on semantic meaning.

2. Generate a structured hierarchical Chinese text according to the specified output rules below.

Four Categories
1. 課堂內容 — course materials, policies, regional introductions, development concepts, etc.

2. 講者表現 — speaker’s professionalism, clarity, delivery, engagement, etc.

3. 學習模式 — teaching methods, activity design, grouping, time arrangement, etc.

4. 其他 — general comments or items not belonging to the above three.

Output Formatting Rules
1. Each question must be output as one complete block.

2. The opening line format must follow:
　　1. 本課程最有價值的部分是：

3. Always include all four category headers in this order: 「課堂內容」、「講者表現」、「學習模式」、「其他」。

4. Under each category, display the topics and their responses hierarchically.

5. Indentation must use two full-width spaces (U+3000) per level.

6. Use full-width “- ” as the list bullet (no half-width dashes or Markdown notation).

7. If a group_topic has only one response in its answers array, display only the group_topic line and do not list its answer.

8. If a group_topic has more than one response, list each answer one level deeper under the topic.

9. Use plain text output only — no JSON, Markdown, or explanations.

10.All text must remain in Chinese.

Hierarchical Indentation Example
　　課堂內容
　　　　- 主題A
　　　　　　- 回覆1
　　　　　　- 回覆2
　　講者表現
　　　　- 主題B
　　學習模式
　　其他
`;


