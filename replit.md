# Banking Chatbot Application

## Overview

This is a Flask-based banking chatbot application that provides general banking information and assistance to users through a conversational interface. The application uses Google's Gemini AI service to generate intelligent responses and maintains conversation history through a database.

## System Architecture

### Frontend Architecture
- **Technology**: HTML5, CSS3, Bootstrap 5 (Dark Theme), JavaScript
- **UI Framework**: Bootstrap with custom CSS styling
- **Theme**: Dark theme optimized for chat interface
- **Responsive Design**: Mobile-first approach with container-fluid layout

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Session Management**: Flask sessions with UUID-based session IDs
- **AI Integration**: Google Gemini API for natural language processing
- **WSGI Middleware**: ProxyFix for handling reverse proxy headers

### Database Schema
- **Users Table**: Stores session-based user information
  - `id` (Primary Key)
  - `session_id` (Unique identifier)
  - `created_at` (Timestamp)
- **ChatMessages Table**: Stores conversation history
  - `id` (Primary Key)
  - `user_id` (Foreign Key to Users)
  - `message` (User input)
  - `response` (AI response)
  - `timestamp` (Message timestamp)

## Key Components

### 1. Application Core (`app.py`)
- Flask application initialization
- Database configuration with SQLAlchemy
- Environment-based configuration (DATABASE_URL, SESSION_SECRET)
- Database table creation and model imports

### 2. AI Service (`gemini_service.py`)
- Google Gemini client initialization
- Banking-specific chatbot class with system prompts
- Conversation context management
- Response generation with banking guidelines

### 3. Database Models (`models.py`)
- User model with session-based identification
- ChatMessage model for conversation persistence
- Relationship mapping between users and messages

### 4. API Routes (`routes.py`)
- Main chat interface endpoint (`/`)
- Chat API endpoint (`/api/chat`) for message processing
- Session management and user creation
- Conversation history retrieval

### 5. Frontend Interface
- **HTML Template**: Single-page chat interface
- **CSS Styling**: Custom styles for chat bubbles and layout
- **JavaScript**: Chat functionality, message handling, and UI interactions

## Data Flow

1. **User Session Creation**: New users get a UUID-based session ID
2. **Message Processing**: 
   - User sends message via frontend
   - Backend validates session and retrieves user
   - Recent conversation history is fetched for context
   - Message is processed through Gemini AI
   - Response is stored in database and returned to frontend
3. **Context Management**: Last 5 messages are used for conversation context
4. **Real-time Updates**: Frontend updates chat interface with new messages

## External Dependencies

### Required Services
- **Google Gemini API**: For AI-powered responses
  - Environment variable: `GEMINI_API_KEY`
  - Used for natural language processing and response generation

### Python Packages
- Flask and Flask-SQLAlchemy for web framework and ORM
- Google Generative AI library for Gemini integration
- Werkzeug for WSGI utilities
- Flask-Login for user session management

### Frontend Dependencies
- Bootstrap 5 (CDN) for UI components and styling
- Font Awesome 6 (CDN) for icons
- Custom CSS for chat-specific styling

## Deployment Strategy

### Environment Configuration
- **Development**: SQLite database with debug mode enabled
- **Production**: Configurable database URL via environment variables
- **Session Security**: Environment-based secret key configuration

### Database Strategy
- SQLite for development (default)
- Configurable for production databases via `DATABASE_URL`
- Connection pooling with pre-ping for reliability

### Security Considerations
- Session-based user identification (no authentication required)
- Input validation and sanitization
- Environment variable configuration for sensitive data
- AI safety guidelines implemented in system prompts

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Updates

### July 07, 2025 - Production-Level Session Management
- **Refactored Session Architecture**: Implemented production-ready session management
  - Added dedicated `/api/init` endpoint for session initialization
  - Created `@require_user` decorator for protected routes
  - Removed automatic user creation from individual endpoints
  - Added proper error handling for missing sessions (401 responses)
  - Frontend now initializes session on page load with `credentials: 'include'`
- **Enhanced Security**: 
  - Session validation at route level
  - Consistent error responses for unauthorized access
  - Proper cookie handling for session persistence
- **Improved User Experience**:
  - Interface disabled until session initializes
  - Automatic session recovery on 401 errors
  - Clear feedback for session-related issues
  - Welcome message for new sessions

### July 07, 2025 - Enhanced Features Added
- **User Feedback System**: Added 5-star rating and thumbs up/down feedback for bot responses
- **Question Categorization**: Automatic categorization of questions into 7 banking categories:
  - Account Services (checking, savings, account management)
  - Loans & Credit (mortgages, credit cards, personal loans)
  - Online Banking (digital services, mobile app)
  - Fees & Charges (banking fees and costs)
  - Investment Services (portfolio, retirement planning)
  - Customer Service (general support, locations)
  - Security & Fraud (account protection, fraud prevention)
- **Analytics Dashboard**: Real-time statistics showing:
  - Average feedback rating
  - Total feedback received
  - Percentage of helpful responses
  - Question distribution by category
- **Enhanced Database**: New tables for categories and message feedback
- **Improved UI**: Category badges, feedback controls, and analytics modal

### July 07, 2025 - Complete Kyrgyz Language Localization
- **Full UI Translation**: Converted entire interface to Kyrgyz language
  - Welcome message and greeting text
  - Button labels and navigation elements
  - Modal dialogs and help information
  - Form placeholders and error messages
  - Timestamp formatting (e.g., "мүнөт мурун", "саат мурун")
- **AI System Translation**: Complete Kyrgyz localization of chatbot responses
  - System prompt translated to Kyrgyz for native language processing
  - Banking terminology and explanations in Kyrgyz
  - Contextual responses that maintain cultural relevance
- **Category Names**: Updated question categories to Kyrgyz
  - Эсеп Кызматтары (Account Services)
  - Кредиттер жана Насыя (Loans & Credit)
  - Онлайн Банкинг (Online Banking)
  - Комиссиялар жана Алымдар (Fees & Charges)
  - Инвестиция Кызматтары (Investment Services)
  - Кардар Кызматы (Customer Service)
  - Коопсуздук жана Алдамчылык (Security & Fraud)
- **Analytics Interface**: Translated dashboard and statistics labels
- **Database Updates**: Updated category names in PostgreSQL database

### Database Schema Updates
- **QuestionCategory Table**: Stores banking question categories with keywords
- **MessageFeedback Table**: Stores user ratings and helpful/unhelpful feedback
- **Enhanced ChatMessage**: Now includes category relationships

### Architecture Changes
- **Authentication Layer**: Added `auth_utils.py` with session management utilities
- **Route Protection**: All chat-related routes now use `@require_user` decorator
- **Frontend Session Management**: Proper initialization flow with `/api/init`

## Changelog

Changelog:
- July 07, 2025. Initial setup and core banking chatbot
- July 07, 2025. Added feedback system and question categorization
- July 07, 2025. Implemented production-level session management architecture
- July 07, 2025. Complete Kyrgyz language localization (UI, AI responses, database)