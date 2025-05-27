import { defineWebSocketHandler } from 'h3';
import { WebSocket } from 'ws'; // WebSocket client for connecting to ElevenLabs
import { v4 as uuidv4 } from 'uuid'; // For generating unique context IDs

// Define message types for client-server and server-client communication
interface ClientToServerMessage {
    action: 'START_TTS' | 'ADD_TEXT' | 'END_TTS_INPUT' | 'INTERRUPT_TTS';
    text?: string;
    voiceId?: string; // e.g., '21m00Tcm4TlvDq8ikWAM' (Bella)
    modelId?: string; // e.g., 'eleven_multilingual_v2' (recommended for multi-context)
    // Future: voiceSettings, generationConfig could be passed from client
}

interface ServerToClientMessage {
    type: 'AUDIO_CHUNK' | 'TTS_STARTED' | 'TTS_ENDED' | 'ERROR' | 'INFO';
    audio?: string; // base64 encoded audio data
    isFinal?: boolean;
    message?: string;
    contextId?: string; // To inform client which context is active for this TTS stream
}

const runtimeConfig = useRuntimeConfig();
// Ensure your .env and nuxt.config.ts are set up for this
const ELEVENLABS_API_KEY = runtimeConfig.ELEVENLABS_API_KEY;

// Store active ElevenLabs WebSocket connections and their associated context IDs, mapped by Nuxt client peer.id
const clientSessions = new Map<string, { elabWs?: WebSocket; contextId?: string }>();

// --- ElevenLabs HTTP Helper Functions ---
async function createContext(contextId: string, voiceId: string, initialText: string = " "): Promise<boolean> {
    if (!ELEVENLABS_API_KEY) {
        console.error('[ElevenLabs HTTP] API Key is not configured.');
        return false;
    }
    // The multi-context API uses model_id in the WebSocket URL, not in this POST.
    // Voice settings are sent in the body of this POST.
    try {
        console.log(`[ElevenLabs HTTP] Creating context: ${contextId} with voice: ${voiceId}`);
        await $fetch(`https://api.elevenlabs.io/v1/multi-context/${contextId}`, {
            method: 'POST',
            headers: {
                'xi-api-key': ELEVENLABS_API_KEY,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: initialText, // Initial text, can be a space or first chunk.
                voice_settings: { stability: 0.5, similarity_boost: 0.75, style: 0.0, use_speaker_boost: true }, // Example settings
            }),
        });
        console.log(`[ElevenLabs HTTP] Context ${contextId} created successfully.`);
        return true;
    } catch (error: any) {
        console.error(`[ElevenLabs HTTP] Failed to create context ${contextId}:`, error.data || error.message || error);
        return false;
    }
}

async function deleteContext(contextId: string): Promise<void> {
    if (!contextId || !ELEVENLABS_API_KEY) return;
    try {
        console.log(`[ElevenLabs HTTP] Deleting context: ${contextId}`);
        await $fetch(`https://api.elevenlabs.io/v1/multi-context/${contextId}`, {
            method: 'DELETE',
            headers: { 'xi-api-key': ELEVENLABS_API_KEY },
        });
        console.log(`[ElevenLabs HTTP] Context ${contextId} deleted successfully.`);
    } catch (error: any) {
        console.error(`[ElevenLabs HTTP] Failed to delete context ${contextId}:`, error.data || error.message || error);
    }
}

// --- Nuxt WebSocket Handler ---
export default defineWebSocketHandler({
    open(peer) {
        console.log('[Nuxt WS] Client connected:', peer.id);
        clientSessions.set(peer.id, {}); // Initialize session for this client
    },

    async message(peer, rawMessage) {
        const messageText = rawMessage.text ? rawMessage.text() : rawMessage.toString();
        let clientMsg: ClientToServerMessage;
        try {
            clientMsg = JSON.parse(messageText);
        } catch (e) {
            console.error('[Nuxt WS] Failed to parse message from client:', peer.id, messageText, e);
            peer.send(JSON.stringify({ type: 'ERROR', message: 'Invalid message format' } as ServerToClientMessage));
            return;
        }
        
        console.log('[Nuxt WS] Message from client:', peer.id, clientMsg);

        let session = clientSessions.get(peer.id);
        if (!session) { // Should ideally be set in open
            session = {};
            clientSessions.set(peer.id, session);
        }

        const defaultVoiceId = '21m00Tcm4TlvDq8ikWAM'; // Bella's voice (example)
        const defaultModelId = 'eleven_multilingual_v2'; // Recommended for multi-context

        const voiceId = clientMsg.voiceId || defaultVoiceId;
        const modelId = clientMsg.modelId || defaultModelId;

        switch (clientMsg.action) {
            case 'START_TTS':
                // If an old context/WS exists for this peer, clean it up (interruption or new stream)
                if (session.elabWs) {
                    console.log(`[Nuxt WS] START_TTS: Closing existing EL WS for peer ${peer.id}, context ${session.contextId}`);
                    session.elabWs.close(1000, 'New TTS stream requested by client');
                    // elabWs.onclose will handle cleanup of session.elabWs
                }
                if (session.contextId) {
                    await deleteContext(session.contextId); // Delete old context
                    session.contextId = undefined;
                }
                
                session.contextId = uuidv4(); // Generate a new context ID
                const initialTextForContext = clientMsg.text || " "; // Use provided text or a space for context creation
                const contextCreated = await createContext(session.contextId, voiceId, initialTextForContext);

                if (!contextCreated) {
                    peer.send(JSON.stringify({ type: 'ERROR', message: 'Failed to create ElevenLabs TTS context' } as ServerToClientMessage));
                    session.contextId = undefined; // Clear contextId if creation failed
                    return;
                }

                const elabUri = `wss://api.elevenlabs.io/v1/multi-context/${session.contextId}/tts/stream-input?model_id=${modelId}`;
                session.elabWs = new WebSocket(elabUri);
                // clientSessions.set(peer.id, session); // Session is already by reference

                session.elabWs.onopen = () => {
                    console.log(`[ElevenLabs WS] Connected to context: ${session.contextId}`);
                    peer.send(JSON.stringify({ type: 'TTS_STARTED', contextId: session.contextId } as ServerToClientMessage));
                    // According to EL docs for multi-context, the text in the POST to create context
                    // is the first piece of text. If clientMsg.text was substantial and sent with START_TTS,
                    // it was used. If additional text needs to be sent immediately after WS open,
                    // it would be done via an ADD_TEXT message from client or handled here.
                };

                session.elabWs.onmessage = (event) => {
                    const dataStr = event.data as string;
                    try {
                        const data = JSON.parse(dataStr);
                        if (data.audio) {
                            peer.send(JSON.stringify({ type: 'AUDIO_CHUNK', audio: data.audio, isFinal: data.isFinal } as ServerToClientMessage));
                        } else if (data.isFinal) {
                            peer.send(JSON.stringify({ type: 'TTS_ENDED', isFinal: true, contextId: session.contextId } as ServerToClientMessage));
                            // ElevenLabs will close the WebSocket connection after sending the final audio.
                        } else if (data.alignment || data.normalizedAlignment) {
                            // TODO: Handle alignment data if needed by the client
                        } else {
                            console.log('[ElevenLabs WS] Received unhandled message structure:', data);
                        }
                    } catch (e) {
                        console.error('[ElevenLabs WS] Failed to parse message from ElevenLabs:', dataStr, e);
                    }
                };

                session.elabWs.onerror = (error) => {
                    console.error(`[ElevenLabs WS] Error for context ${session.contextId}:`, error.message);
                    peer.send(JSON.stringify({ type: 'ERROR', message: `ElevenLabs WS Error: ${error.message}`, contextId: session.contextId } as ServerToClientMessage));
                    // No need to call session.elabWs.close() here, as 'close' event will follow.
                };

                session.elabWs.onclose = (event) => {
                    console.log(`[ElevenLabs WS] Connection closed for context ${session.contextId}: Code ${event.code}, Reason: ${event.reason}`);
                    // If the close was not initiated by 'TTS_ENDED' (e.g. an error or unexpected close),
                    // inform the client.
                    if (!event.wasClean && session.elabWs) { // Check session.elabWs to avoid sending error after explicit interrupt
                         peer.send(JSON.stringify({ type: 'ERROR', message: 'ElevenLabs connection closed unexpectedly.', contextId: session.contextId } as ServerToClientMessage));
                    }
                    // The context might linger if EL didn't close it cleanly after TTS.
                    // For multi-context, explicit deletion is good on interrupt or full client disconnect.
                    // If EL manages context lifecycle on stream end, this explicit delete might be redundant but safe.
                    // Let's ensure context is deleted if the WS closes and it wasn't due to a new TTS starting or interrupt.
                    if (session.elabWs && session.contextId) { // If elabWs exists, it means it wasn't closed by an interrupt/new_start
                        // deleteContext(session.contextId); // Decided against aggressive delete here, rely on interrupt/disconnect
                    }
                    session.elabWs = undefined; // Clear the WebSocket instance from the session
                };
                break;

            case 'ADD_TEXT':
                if (session.elabWs && session.elabWs.readyState === WebSocket.OPEN && clientMsg.text) {
                    session.elabWs.send(JSON.stringify({
                        text: clientMsg.text,
                        try_trigger_generation: true, // Helps in streaming scenarios
                    }));
                } else if (!session.elabWs || session.elabWs.readyState !== WebSocket.OPEN) {
                    console.warn(`[Nuxt WS] ADD_TEXT: No active EL WS for peer ${peer.id} or WS not open.`);
                    peer.send(JSON.stringify({ type: 'ERROR', message: 'TTS stream not active. Cannot add text.', contextId: session.contextId } as ServerToClientMessage));
                }
                break;

            case 'END_TTS_INPUT':
                if (session.elabWs && session.elabWs.readyState === WebSocket.OPEN) {
                    session.elabWs.send(JSON.stringify({ text: "" })); // Send End-Of-Stream
                } else {
                    console.warn(`[Nuxt WS] END_TTS_INPUT: No active EL WS for peer ${peer.id}.`);
                }
                // ElevenLabs WS will send 'isFinal' and then close the connection.
                break;

            case 'INTERRUPT_TTS':
                console.log(`[Nuxt WS] INTERRUPT_TTS received for peer ${peer.id}, context ${session.contextId}`);
                if (session.elabWs) {
                    session.elabWs.close(1000, 'Client initiated interruption');
                    // onclose handler for elabWs will set session.elabWs = undefined
                }
                if (session.contextId) {
                    await deleteContext(session.contextId); // Crucial for multi-context interruption handling
                    peer.send(JSON.stringify({ type: 'INFO', message: 'TTS interrupted and context closed.', contextId: session.contextId } as ServerToClientMessage));
                    session.contextId = undefined;
                } else {
                     peer.send(JSON.stringify({ type: 'INFO', message: 'TTS interruption acknowledged (no active context found).'} as ServerToClientMessage));
                }
                break;
        }
    },

    async close(peer, event) {
        console.log(`[Nuxt WS] Client disconnected: ${peer.id}, Code: ${event.code}, Reason: ${event.reason}`);
        const session = clientSessions.get(peer.id);
        if (session) {
            if (session.elabWs) {
                session.elabWs.close(1000, 'Primary client disconnected from Nuxt server');
            }
            if (session.contextId) {
                // Ensure context is cleaned up if the client disconnects abruptly
                await deleteContext(session.contextId);
            }
            clientSessions.delete(peer.id);
        }
    },

    async error(peer, error) {
        console.error(`[Nuxt WS] Error for client ${peer.id}:`, error.message);
        const session = clientSessions.get(peer.id);
        if (session) {
            if (session.elabWs) {
                session.elabWs.close(1006, 'Internal Nuxt server error affecting client');
            }
            if (session.contextId) {
                await deleteContext(session.contextId); // Clean up on error too
            }
            clientSessions.delete(peer.id);
        }
    }
}); 