---
name: Terminal Chat Interface with Clerk Auth
overview: Create a simple terminal-style chat interface with Clerk Google authentication that connects to a new backend chat endpoint using LangChain + OpenRouter. No session persistence - conversations reset on page reload.
todos:
  - id: backend-chat-endpoint
    content: Create backend chat endpoint at backend/app/api/v1/chat.py with LangChain + OpenRouter integration
    status: pending
  - id: register-chat-router
    content: Register chat router in backend/app/api/v1/router.py
    status: pending
  - id: frontend-clerk-setup
    content: Set up ClerkProvider in frontend/src/app/layout.tsx with Google OAuth
    status: pending
  - id: terminal-ui-component
    content: Create terminal-style chat interface in frontend/src/app/page.tsx
    status: pending
  - id: api-client-chat
    content: Add chat method to frontend/src/lib/api.ts with authentication
    status: pending
  - id: env-config
    content: Update frontend environment template with Clerk publishable key
    status: pending
---

# Terminal Chat Interface with Clerk Authentication

## Overview

Build a terminal-style Q&A interface with Clerk Google authentication. Users authenticate via Clerk, then interact with an LLM through a simple terminal UI. No database session storage - conversations reset on page reload.

## Backend Changes

### 1. Create Chat Endpoint (`backend/app/api/v1/chat.py`)

- New file: `backend/app/api/v1/chat.py`
- Endpoint: `POST /api/v1/chat`
- Request model:
  ```python
  class ChatRequest(BaseModel):
      message: str
      model: Optional[str] = "openai/gpt-4o-mini"
      temperature: Optional[float] = 0.7
  ```

- Response model:
  ```python
  class ChatResponse(BaseModel):
      response: str
      model_used: str
  ```

- Implementation:
  - Use `require_current_user` dependency for Clerk auth
  - Initialize `OpenRouterProvider`
  - Create LangChain chain: `ChatPromptTemplate | LLM | StrOutputParser`
  - Process user message and return response
  - No session storage - stateless

### 2. Register Chat Router (`backend/app/api/v1/router.py`)

- Add: `from app.api.v1 import chat`
- Add: `api_router.include_router(chat.router, prefix="/chat", tags=["chat"])`

## Frontend Changes

### 3. Set Up Clerk Authentication

- Update `frontend/src/app/layout.tsx`:
  - Uncomment `ClerkProvider`
  - Add Clerk publishable key from env: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
  - Configure Google as OAuth provider

### 4. Create Terminal Chat Component (`frontend/src/app/page.tsx`)

- Replace current homepage with terminal interface
- Design:
  - Dark background (`bg-gray-950`)
  - Monospace font for terminal feel
  - Command-line style input at bottom
  - Scrollable message history above
  - Keep gradient accents (purple/blue/pink) for branding
- Features:
  - Clerk sign-in button (Google) if not authenticated
  - User profile display when authenticated
  - Terminal-style prompt (`> `) for input
  - Messages displayed with user/AI prefixes
  - Loading indicator while processing
  - Auto-scroll to bottom

### 5. Update API Client (`frontend/src/lib/api.ts`)

- Add `chat()` method:
  ```typescript
  async chat(message: string, model?: string): Promise<{ response: string; model_used: string }>
  ```

- Use authenticated client with Clerk token

### 6. Create Chat Hook (Optional) (`frontend/src/hooks/use-terminal-chat.ts`)

- Manage chat state (messages array)
- Handle sending messages
- Reset on component unmount (no persistence)

### 7. Environment Configuration

- Update `frontend/.env.template`:
  - Add `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
  - Ensure `NEXT_PUBLIC_API_URL` is set

## File Structure

```
backend/app/api/v1/
  └── chat.py (NEW)

frontend/src/
  ├── app/
  │   ├── layout.tsx (UPDATE - uncomment ClerkProvider)
  │   └── page.tsx (REPLACE - terminal interface)
  ├── lib/
  │   └── api.ts (UPDATE - add chat method)
  └── hooks/
      └── use-terminal-chat.ts (NEW - optional)
```

## Implementation Details

### Backend Chat Endpoint Flow

1. User sends POST request with message
2. Clerk JWT validated via `require_current_user`
3. Extract user info (optional - for logging)
4. Initialize OpenRouterProvider
5. Create LangChain chain with simple system prompt
6. Invoke chain with user message
7. Return response

### Frontend Terminal UI Flow

1. Check Clerk authentication status
2. If not authenticated: Show sign-in button
3. If authenticated: Show terminal interface
4. User types message and presses Enter
5. Send to `/api/v1/chat` with Clerk token
6. Display response in terminal format
7. Clear messages on page reload (useState only)

## Design Notes

- Terminal aesthetic: Monospace font, minimal UI
- Keep existing color scheme: Dark background with purple/blue gradients
- Simple prompt indicator: `> ` or `$ `
- Messages: `[You]` and `[AI]` prefixes
- No fancy animations - keep it terminal-like
- Responsive but focused on desktop experience

## Testing Checklist

- [ ] Clerk Google authentication works
- [ ] Chat endpoint requires authentication
- [ ] Messages send and receive correctly
- [ ] Page reload clears conversation
- [ ] Error handling for API failures
- [ ] Loading states display correctly