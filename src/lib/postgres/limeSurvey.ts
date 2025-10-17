import {prisma} from './db'

// Dynamically import Prisma to avoid initialization issues
// let prisma: any;

// async function getPrisma() {
//   if (!prisma) {
//     try {
//       const module = await import('./db');
//       prisma = module.prisma;
//     } catch (error) {
//       console.error('Failed to initialize Prisma client:', error);
//       throw new Error('Database connection is not available');
//     }
//   }
//   return prisma;
// }

// Function to get survey data by survey ID
export async function getLimeSurveyData(sid: string) {
  try {
    // const prismaClient = await getPrisma();
    
    // Construct the table name for LimeSurvey
    const tableName = `lime_survey_${sid}`;
    
    // Query the survey data
    // Note: Prisma doesn't support dynamic table names, so we'll use raw query
    const surveyData: any[] = await prisma.$queryRawUnsafe(
      `SELECT * FROM ${tableName}`
    );
    
    return surveyData;
  } catch (error: any) {
    console.error('Error fetching LimeSurvey data:', error);
    throw new Error(`Failed to fetch data for survey ${sid}: ${error.message}`);
  }
}

// Function to get column information for a survey table
export async function getLimeSurveySummaryBySid(sid: string) {
  try {
    // const prismaClient = await getPrisma();
    
    const tableName = `lime_survey_${sid}`;
    
    // Get column information
    const columns: any[] = await prisma.$queryRawUnsafe(
      `WITH qs AS (
        SELECT 
            q.qid,
            q.sid,
            q.gid,
            q.question_theme_name,
            q.type,
            COALESCE(l10n.question, q.title) AS qtext
        FROM lime_questions q
        LEFT JOIN lime_question_l10ns l10n ON l10n.qid = q.qid
        WHERE q.sid = ${sid}
            AND q.parent_qid = 0
            AND l10n.question NOT LIKE '%填表人資料%'
        ),
        sgqa AS (
        SELECT 
            qs.qid,
            qs.qtext,
            qs.question_theme_name,
            qs.type,
            CASE 
            WHEN qs.type IN ('F','Q') THEN 
                jsonb_agg(jsonb_build_object(
                'colname', format('%sX%sX%s%s', qs.sid, qs.gid, qs.qid, sub.title),
                'subcode', sub.title
                ) ORDER BY sub.question_order)
            WHEN qs.type = 'T' THEN
                jsonb_build_array(jsonb_build_object(
                'colname', format('%sX%sX%s', qs.sid, qs.gid, qs.qid),
                'subcode', NULL
                ))
            ELSE '[]'::jsonb
            END AS colmeta
        FROM qs
        LEFT JOIN lime_questions sub
            ON sub.parent_qid = qs.qid
        GROUP BY qs.qid, qs.qtext, qs.question_theme_name, qs.type, qs.sid, qs.gid, qs.qid
        ),
        flat_cols AS (
        SELECT 
            qid, qtext, question_theme_name, type,
            (e->>'colname') AS colname,
            (e->>'subcode') AS subcode
        FROM sgqa, LATERAL jsonb_array_elements(colmeta) AS e
        ),
        /* Map response cell value -> answer code -> localized text */
        arr_counts AS (
        SELECT 
            fc.qtext,
            COALESCE(l10n_lang.answer, la.code) AS answer_value,
            COUNT(*) AS cnt
        FROM flat_cols fc
        JOIN ${tableName} r ON TRUE
        CROSS JOIN LATERAL row_to_json(r) AS rj(rowjson)
        CROSS JOIN LATERAL (
            VALUES (NULLIF(rj.rowjson ->> fc.colname, ''))
        ) AS v(val)
        /* For type F (array/array text that actually stores codes), join to lime_answers by qid+code */
        JOIN lime_answers la
            ON la.qid = fc.qid
        AND la.code = v.val
        LEFT JOIN lime_answer_l10ns l10n_lang
            ON l10n_lang.aid = la.aid
        WHERE fc.type = 'F'
            AND v.val IS NOT NULL
        GROUP BY fc.qtext, COALESCE(l10n_lang.answer, la.code)
        ),
        arr_json AS (
        SELECT 
            qtext,
            jsonb_agg(
            jsonb_build_object('value', answer_value, 'count', cnt)
            ORDER BY answer_value DESC NULLS LAST
            ) AS jarr
        FROM arr_counts
        GROUP BY qtext
        ),
        text_answers AS (
        SELECT 
            t.qtext,
            jsonb_agg(jsonb_build_object('answer', t.ans) ORDER BY t.seq) AS jarr
        FROM (
            SELECT 
            fc.qtext,
            rj.rowjson ->> fc.colname AS ans,
            r.id AS seq
            FROM flat_cols fc
            JOIN ${tableName} r ON TRUE
            CROSS JOIN LATERAL row_to_json(r) AS rj(rowjson)
            WHERE fc.type IN ('T','Q')
            AND (rj.rowjson ->> fc.colname) IS NOT NULL
            AND LENGTH(rj.rowjson ->> fc.colname) > 0
        ) t
        GROUP BY t.qtext
        ),
        merged AS (
        SELECT qtext, jarr FROM arr_json
        UNION ALL
        SELECT qtext, jarr FROM text_answers
        )
        SELECT jsonb_object_agg(qtext, jarr) AS result_json
        FROM merged;`
    );
    
    return columns;
  } catch (error: any) {
    console.error('Error fetching LimeSurvey columns:', error);
    throw new Error(`Failed to fetch columns for survey ${sid}: ${error.message}`);
  }
}


// Function to process LimeSurvey data for questions 4 and 5
export async function processLimeSurveyQuestions(sid: string) {
  try {
    // Get column information
    const columns = await getLimeSurveySummaryBySid(sid);
    
    // Identify columns that likely contain answers to questions 4 and 5
    // In LimeSurvey, these are typically named like SQ001_SQ004, SQ001_SQ005, etc.
    const question4Columns = columns.filter((column: any) => 
      column.column_name.includes('SQ004') || 
      (column.column_name.includes('4') && !column.column_name.includes('SQ005'))
    );
    
    const question5Columns = columns.filter((column: any) => 
      column.column_name.includes('SQ005') || 
      (column.column_name.includes('5') && !column.column_name.includes('SQ004'))
    );
    
    // Get all survey data
    const surveyData = await getLimeSurveyData(sid);
    
    // Transform the data into the expected JSON structure
    const result: any = {
      "4. 本課程最有價值的部分是：": [],
      "5. 對課程內容及講者的整體意見：": []
    };
    
    // Process each row to extract answers
    for (const row of surveyData) {
      // For question 4, look for non-empty values in relevant columns
      for (const column of question4Columns) {
        const value = row[column.column_name];
        if (value && typeof value === 'string' && value.trim().length > 0) {
          result["4. 本課程最有價值的部分是："].push({ answer: value.trim() });
        }
      }
      
      // For question 5, look for non-empty values in relevant columns
      for (const column of question5Columns) {
        const value = row[column.column_name];
        if (value && typeof value === 'string' && value.trim().length > 0) {
          result["5. 對課程內容及講者的整體意見："].push({ answer: value.trim() });
        }
      }
    }
    
    return result;
  } catch (error: any) {
    console.error('Error processing LimeSurvey questions:', error);
    throw new Error(`Failed to process questions for survey ${sid}: ${error.message}`);
  }
}