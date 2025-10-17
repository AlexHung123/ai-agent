import crypto from 'crypto';
import { EventEmitter } from 'stream';
// import db from '@/lib/db';
// import { messages as messagesSchema } from '@/lib/db/schema';

export const handleEmitterEvents = async (
  stream: EventEmitter,
  writer: WritableStreamDefaultWriter,
  encoder: TextEncoder,
//   chatId: string,
) => {
  let recievedMessage = '';
  const aiMessageId = crypto.randomBytes(7).toString('hex');

  stream.on('data', (data) => {
    const parsedData = JSON.parse(data);
    if (parsedData.type === 'response') {
      writer.write(
        encoder.encode(
          JSON.stringify({
            type: 'message',
            data: parsedData.data,
            messageId: aiMessageId,
          }) + '\n',
        ),
      );

      recievedMessage += parsedData.data;
    } else if (parsedData.type === 'sources') {
      writer.write(
        encoder.encode(
          JSON.stringify({
            type: 'sources',
            data: parsedData.data,
            messageId: aiMessageId,
          }) + '\n',
        ),
      );

    //   const sourceMessageId = crypto.randomBytes(7).toString('hex');

    //   db.insert(messagesSchema)
    //     .values({
    //       chatId: chatId,
    //       messageId: sourceMessageId,
    //       role: 'source',
    //       sources: parsedData.data,
    //       createdAt: new Date().toString(),
    //     })
    //     .execute();
    }
  });
  stream.on('end', () => {
    writer.write(
      encoder.encode(
        JSON.stringify({
          type: 'messageEnd',
        }) + '\n',
      ),
    );
    writer.close();

    // db.insert(messagesSchema)
    //   .values({
    //     content: recievedMessage,
    //     chatId: chatId,
    //     messageId: aiMessageId,
    //     role: 'assistant',
    //     createdAt: new Date().toString(),
    //   })
    //   .execute();
  });
  stream.on('error', (data) => {
    const parsedData = JSON.parse(data);
    writer.write(
      encoder.encode(
        JSON.stringify({
          type: 'error',
          data: parsedData.data,
        }),
      ),
    );
    writer.close();
  });
};