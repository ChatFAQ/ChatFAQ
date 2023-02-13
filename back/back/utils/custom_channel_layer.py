from channels_postgres.core import PostgresChannelLayer


class CustomPostgresChannelLayer(PostgresChannelLayer):
    """
    This is a modification of the original PostgresChannelLayer to fix the next error:
    When a bunch og nre messages are added quickly one after the other with channel_layer.group_send
    then the order of these messages gets messed up apparently.
    I figure out it was because when "retrieve_queued_messages_sql" returns no message, then the next query the layer
    executes after waiting for the notification was not considering the order of the messages. The solution I
    implemented has been just to repeat the same original query (which does takes in account the order) right after
    receiving the notification.
    What I do not understand is why in the first place there can be no new message
    """

    async def _get_message_from_channel(self, channel):
        retrieve_events_sql = f'LISTEN "{channel}";'
        retrieve_queued_messages_sql = """
                DELETE FROM channels_postgres_message
                WHERE id = (
                    SELECT id
                    FROM channels_postgres_message
                    WHERE channel=%s AND expire > NOW()
                    ORDER BY id
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                    )
                RETURNING message;
            """

        pool, _ = await self.get_pool()
        with await pool as conn:
            cur = await conn.cursor()
            await cur.execute(retrieve_queued_messages_sql, (channel,))
            message = await cur.fetchone()

            if not message:
                # Unlisten and clear pending messages (From other connections) from the queue
                await cur.execute("UNLISTEN *;")
                for _ in range(conn.notifies.qsize()):
                    conn.notifies.get_nowait()

                await cur.execute(retrieve_events_sql)
                _ = await conn.notifies.get()

                await cur.execute(retrieve_queued_messages_sql, (channel,))
                message = await cur.fetchone()
                # message_id = event.payload
                # retrieve_message_sql = (
                #     'DELETE FROM channels_postgres_message '
                #     'WHERE id=%s RETURNING message;'
                # )
                # await cur.execute(retrieve_message_sql, (message_id,))
                # message = await cur.fetchone()

            message = self.deserialize(message[0])

            return message
